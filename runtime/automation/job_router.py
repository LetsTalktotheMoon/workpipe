"""
Deterministic router that decides reuse / retarget / new_seed for sheet jobs.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Optional
import re

from automation.seed_registry import SeedEntry
from automation.company_subseed_registry import load_company_subseed_registry
from automation.text_utils import (
    build_skill_vocabulary,
    canonicalize_skill,
    extract_domain_terms,
    extract_known_skills,
    normalize_token,
    prepare_skill_tokens,
    slugify,
    split_delimited_list,
)


@dataclass
class JobFingerprint:
    job_id: str
    company_name: str
    company_key: str
    title: str
    seniority: str
    role_family: str
    taxonomy_v3: str
    publish_time: str
    apply_link: str
    core_skills: set[str] = field(default_factory=set)
    required_skills: set[str] = field(default_factory=set)
    preferred_skills: set[str] = field(default_factory=set)
    domains: set[str] = field(default_factory=set)
    source_row: dict = field(default_factory=dict)

    @property
    def combined_required(self) -> set[str]:
        return self.core_skills | self.required_skills

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "company_name": self.company_name,
            "company_key": self.company_key,
            "title": self.title,
            "seniority": self.seniority,
            "role_family": self.role_family,
            "taxonomy_v3": self.taxonomy_v3,
            "publish_time": self.publish_time,
            "apply_link": self.apply_link,
            "core_skills": sorted(self.core_skills),
            "required_skills": sorted(self.required_skills),
            "preferred_skills": sorted(self.preferred_skills),
            "domains": sorted(self.domains),
        }


@dataclass
class RouteCandidate:
    seed_id: str
    label: str
    route_score: float
    base_route_score: float
    required_coverage: float
    core_coverage: float
    preferred_coverage: float
    role_score: float
    domain_score: float
    seniority_score: float
    title_score: float
    same_company: bool
    seed_company_name: str
    seed_source_job_id: str
    company_anchor: bool
    missing_required: list[str]
    project_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "seed_id": self.seed_id,
            "label": self.label,
            "route_score": round(self.route_score, 3),
            "base_route_score": round(self.base_route_score, 3),
            "required_coverage": round(self.required_coverage, 3),
            "core_coverage": round(self.core_coverage, 3),
            "preferred_coverage": round(self.preferred_coverage, 3),
            "role_score": round(self.role_score, 3),
            "domain_score": round(self.domain_score, 3),
            "seniority_score": round(self.seniority_score, 3),
            "title_score": round(self.title_score, 3),
            "same_company": self.same_company,
            "seed_company_name": self.seed_company_name,
            "seed_source_job_id": self.seed_source_job_id,
            "company_anchor": self.company_anchor,
            "missing_required": self.missing_required,
            "project_ids": list(self.project_ids),
        }


@dataclass
class RouteDecision:
    job: JobFingerprint
    route_mode: str
    top_candidate: RouteCandidate
    top_candidates: list[RouteCandidate]
    decision_reason: str
    should_generate: bool

    def to_dict(self) -> dict:
        return {
            "job": self.job.to_dict(),
            "route_mode": self.route_mode,
            "top_candidate": self.top_candidate.to_dict(),
            "top_candidates": [candidate.to_dict() for candidate in self.top_candidates],
            "decision_reason": self.decision_reason,
            "should_generate": self.should_generate,
        }


ROLE_COMPATIBILITY: dict[str, dict[str, float]] = {
    "ai_ml_swe": {
        "ai_ml_swe": 1.0,
        "solutions": 0.85,
        "data_platform": 0.7,
        "backend_generalist": 0.55,
        "generalist": 0.55,
        "data_science": 0.7,
    },
    "backend_generalist": {
        "backend_generalist": 1.0,
        "generalist": 0.9,
        "fullstack": 0.85,
        "platform": 0.72,
        "data_platform": 0.68,
        "enterprise_apps": 0.7,
    },
    "data_analytics": {
        "data_analytics": 1.0,
        "data_science": 0.82,
        "data_platform": 0.62,
        "ai_ml_swe": 0.55,
    },
    "data_platform": {
        "data_platform": 1.0,
        "platform": 0.78,
        "backend_generalist": 0.72,
        "ai_ml_swe": 0.7,
        "data_science": 0.68,
    },
    "data_science": {
        "data_science": 1.0,
        "ai_ml_swe": 0.78,
        "data_analytics": 0.75,
        "data_platform": 0.68,
    },
    "embedded": {"embedded": 1.0, "systems": 0.72},
    "enterprise_apps": {"enterprise_apps": 1.0, "backend_generalist": 0.68, "generalist": 0.62},
    "frontend": {"frontend": 1.0, "fullstack": 0.85, "generalist": 0.45},
    "fullstack": {"fullstack": 1.0, "backend_generalist": 0.82, "frontend": 0.82, "generalist": 0.72},
    "generalist": {"generalist": 1.0, "backend_generalist": 0.88, "fullstack": 0.7, "platform": 0.6},
    "manager": {"manager": 1.0},
    "mobile": {"mobile": 1.0, "frontend": 0.4, "generalist": 0.35},
    "networking": {"networking": 1.0, "platform": 0.72, "systems": 0.75},
    "platform": {"platform": 1.0, "backend_generalist": 0.72, "networking": 0.72, "security": 0.6, "systems": 0.68},
    "qa": {"qa": 1.0, "generalist": 0.35},
    "security": {"security": 1.0, "platform": 0.65, "backend_generalist": 0.42},
    "solutions": {"solutions": 1.0, "ai_ml_swe": 0.78, "backend_generalist": 0.55},
    "systems": {"systems": 1.0, "platform": 0.68, "networking": 0.72},
}


ROLE_KEYWORDS = (
    ("General Software Engineer Manager", "manager"),
    ("Engineering Manager", "manager"),
    ("Product Management", "pm"),
    ("Backend Software Engineer", "backend_generalist"),
    ("General Software Engineer", "generalist"),
    ("Full Stack Engineer", "fullstack"),
    ("Frontend Software Engineer", "frontend"),
    ("Data Scientist", "data_science"),
    ("Data Analyst", "data_analytics"),
    ("Data Engineer", "data_platform"),
    ("Machine Learning Engineer", "ai_ml_swe"),
    ("Artificial Intelligence Engineer", "ai_ml_swe"),
    ("DevOps Engineer", "platform"),
    ("Cloud Engineer", "platform"),
    ("Infrastructure Engineer", "platform"),
    ("Security Engineer", "security"),
    ("Quality Assurance Engineer", "qa"),
    ("Automation Engineer", "platform"),
    ("Java Developer", "backend_generalist"),
    ("Python Developer", "backend_generalist"),
    ("IT Solutions Architect", "solutions"),
    ("Embedded Software Engineer", "embedded"),
    ("Mobile Engineer", "mobile"),
)

GENERIC_SKILL_TOKENS = {
    "ability",
    "accessibility",
    "agile",
    "agile development",
    "agile scrum",
    "ai",
    "analytics",
    "api",
    "backend",
    "cloud",
    "communication",
    "compliance",
    "continuous integration",
    "customer workflows",
    "data analysis",
    "data analytics",
    "data pipelines",
    "debugging",
    "decision making frameworks",
    "deployment",
    "design review",
    "development methodologies",
    "engineering team management",
    "experience",
    "frontend",
    "infrastructure",
    "leadership",
    "mentorship",
    "platform",
    "problem solving",
    "product sense",
    "programming",
    "scrum",
    "software development processes",
    "troubleshooting",
}

GENERIC_SKILL_SUBSTRINGS = (
    "ability",
    "background",
    "communication",
    "equivalent experience",
    "experience",
    "methodolog",
    "problem solving",
    "team leadership",
)

GENERIC_TITLE_TOKENS = {
    "software",
    "engineer",
    "engineering",
    "developer",
    "development",
    "general",
    "application",
    "applications",
}


def _job_specific_title_tokens(job: JobFingerprint) -> set[str]:
    return {
        token
        for token in job.title.lower().replace("/", " ").replace("-", " ").split()
        if len(token) >= 3 and token not in GENERIC_TITLE_TOKENS
    }


SENIORITY_RANK = {
    "entry": 0,
    "mid": 1,
    "mid_senior": 2,
    "senior": 3,
    "lead": 4,
}


def infer_role_family(row: dict) -> str:
    taxonomy = row.get("taxonomy_v3", "") or ""
    title = f"{row.get('job_title', '')} {row.get('job_nlp_title', '')}".lower()
    if "site reliability" in title or re.search(r"\bsre\b", title):
        return "platform"
    for marker, family in ROLE_KEYWORDS:
        if marker.lower() in taxonomy.lower():
            return family
    if "data scientist" in title:
        return "data_science"
    if "data analyst" in title or "analytics" in title:
        return "data_analytics"
    if any(marker in title for marker in ("product manager", "program manager", "project manager", "scrum master", "tpm")):
        return "pm"
    if "ai engineer" in title or "machine learning" in title or "applied scientist" in title:
        return "ai_ml_swe"
    if "frontend" in title or "ui engineer" in title:
        return "frontend"
    if "full stack" in title or "full-stack" in title:
        return "fullstack"
    if "backend" in title or "java developer" in title or "python developer" in title:
        return "backend_generalist"
    if "devops" in title or "platform" in title or "cloud engineer" in title or "infrastructure" in title or "site reliability" in title or "sre" in title:
        return "platform"
    if "security" in title:
        return "security"
    if "qa" in title or "sdet" in title or "quality" in title:
        return "qa"
    if "mobile" in title or "ios" in title or "android" in title:
        return "mobile"
    if "embedded" in title:
        return "embedded"
    if "architect" in title:
        return "solutions"
    if "manager" in title:
        return "manager"
    return "generalist"


def infer_seniority(row: dict) -> str:
    seniority = (row.get("job_seniority", "") or "").lower()
    title = f"{row.get('job_title', '')} {row.get('job_nlp_title', '')}".lower()
    years = str(row.get("min_years_experience", "") or "").strip()
    try:
        years_num = float(years) if years else None
    except ValueError:
        years_num = None

    if "lead/staff" in seniority or any(token in title for token in ("staff", "principal", "lead", "architect")):
        return "lead"
    if "new grad" in seniority or "entry level" in seniority or (years_num is not None and years_num <= 1):
        return "entry"
    if "senior" in seniority or title.startswith("senior ") or title.startswith("sr.") or (years_num is not None and years_num >= 5):
        return "senior"
    if "mid" in seniority or (years_num is not None and years_num >= 2):
        return "mid_senior"
    return "mid"


def seniority_score(job_seniority: str, seed_seniority: str) -> float:
    job_rank = SENIORITY_RANK.get(job_seniority, 1)
    seed_rank = SENIORITY_RANK.get(seed_seniority, 1)
    if job_rank == seed_rank:
        return 1.0
    if abs(job_rank - seed_rank) == 1:
        return 0.82
    if job_rank > seed_rank:
        return 0.6
    return 0.75


def role_score(job_role: str, seed_role: str) -> float:
    if job_role == seed_role:
        return 1.0
    return ROLE_COMPATIBILITY.get(job_role, {}).get(seed_role, 0.2)


def _build_skill_vocab(seeds: Iterable[SeedEntry]) -> set[str]:
    return build_skill_vocabulary([seed.keywords | seed.core_stack for seed in seeds])


def build_skill_vocab_from_seeds(seeds: Iterable[SeedEntry]) -> set[str]:
    return _build_skill_vocab(seeds)


def _is_specific_skill(token: str, skill_vocab: set[str]) -> bool:
    if not token:
        return False
    if token in GENERIC_SKILL_TOKENS:
        return False
    if any(fragment in token for fragment in GENERIC_SKILL_SUBSTRINGS):
        return False
    if token in skill_vocab:
        return True
    if len(token.split()) > 4:
        return False
    return bool(re.search(r"[+#.]|\d", token))


def build_job_fingerprint(
    row: dict,
    seeds: Iterable[SeedEntry],
    skill_vocab: Optional[set[str]] = None,
    skill_tokens: Optional[tuple[str, ...]] = None,
) -> JobFingerprint:
    seed_list = list(seeds)
    skill_vocab = skill_vocab or _build_skill_vocab(seed_list)
    skill_tokens = skill_tokens or prepare_skill_tokens(skill_vocab)
    combined_text = " ".join(
        str(row.get(column, "") or "")
        for column in (
            "job_title",
            "job_nlp_title",
            "core_skills",
            "must_have_quals",
            "preferred_quals",
            "core_responsibilities",
            "job_summary",
            "recommendation_tags",
            "taxonomy_v3",
        )
    )

    core_skills = {canonicalize_skill(skill) for skill in split_delimited_list(row.get("core_skills", ""))}
    core_skills = {skill for skill in core_skills if skill}
    required_from_text = extract_known_skills(str(row.get("must_have_quals", "")), skill_tokens)
    preferred_from_text = extract_known_skills(str(row.get("preferred_quals", "")), skill_tokens)

    core_skills = {skill for skill in core_skills if _is_specific_skill(skill, skill_vocab)}
    required_skills = {
        skill for skill in required_from_text
        if _is_specific_skill(skill, skill_vocab)
    }
    preferred_skills = {
        skill for skill in preferred_from_text
        if _is_specific_skill(skill, skill_vocab)
    } - core_skills
    domains = extract_domain_terms(combined_text)

    return JobFingerprint(
        job_id=str(row.get("job_id", "") or slugify(row.get("apply_link", "") or row.get("job_title", "job"))),
        company_name=str(row.get("company_name", "") or ""),
        company_key=normalize_token(str(row.get("company_name", "") or "")),
        title=str(row.get("job_title", "") or row.get("job_nlp_title", "") or ""),
        seniority=infer_seniority(row),
        role_family=infer_role_family(row),
        taxonomy_v3=str(row.get("taxonomy_v3", "") or ""),
        publish_time=str(row.get("publish_time", "") or ""),
        apply_link=str(row.get("apply_link", "") or ""),
        core_skills=core_skills,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        domains=domains,
        source_row=row,
    )


def _coverage(required: set[str], seed_skills: set[str]) -> tuple[float, list[str]]:
    if not required:
        return 1.0, []
    missing = sorted(required - seed_skills)
    return (len(required & seed_skills) / len(required)), missing


def _title_hint_score(job: JobFingerprint, seed: SeedEntry) -> float:
    haystack = f"{job.title} {job.taxonomy_v3}".lower()
    if not haystack.strip():
        return 0.0

    best = 0.0
    job_specific_tokens = _job_specific_title_tokens(job)
    for hint in seed.taxonomy_hints:
        hint_lower = hint.lower().strip()
        if not hint_lower:
            continue
        tokens = [
            token
            for token in hint_lower.replace("/", " ").replace("-", " ").split()
            if len(token) >= 3
        ]
        if not tokens:
            continue
        specific_tokens = [token for token in tokens if token not in GENERIC_TITLE_TOKENS]

        if hint_lower in haystack:
            if specific_tokens:
                return 1.0
            if not job_specific_tokens:
                return 1.0
            best = max(best, 0.45)
            continue

        if specific_tokens:
            matched = sum(1 for token in specific_tokens if token in haystack)
            best = max(best, matched / len(specific_tokens))
            continue

        matched = sum(1 for token in tokens if token in haystack)
        if matched == len(tokens):
            best = max(best, 0.45 if job_specific_tokens else 1.0)
        elif matched:
            best = max(best, 0.2)
    return round(best, 3)


def _company_bias(job: JobFingerprint, seed: SeedEntry, *, same_company_viable: bool) -> float:
    if not job.company_key or not seed.company_key:
        return 0.0
    if job.company_key == seed.company_key:
        if same_company_viable:
            return 0.12 + (0.04 if seed.company_anchor else 0.0)
        return 0.02 + (0.02 if seed.company_anchor else 0.0)
    if same_company_viable:
        return -0.10
    return 0.0


def score_seed(job: JobFingerprint, seed: SeedEntry, *, same_company_viable: bool = False) -> RouteCandidate:
    seed_skills = seed.keywords | seed.core_stack
    req_cov, missing_required = _coverage(job.combined_required, seed_skills)
    core_cov, _ = _coverage(job.core_skills, seed_skills)
    preferred_cov, _ = _coverage(job.preferred_skills, seed_skills)
    role_cov = role_score(job.role_family, seed.role_family)
    domain_cov, _ = _coverage(job.domains, seed.domains | {normalize_token(item) for item in seed.taxonomy_hints})
    seniority_cov = seniority_score(job.seniority, seed.seniority)
    title_cov = _title_hint_score(job, seed)

    base_total = (
        0.42 * req_cov
        + 0.14 * core_cov
        + 0.05 * preferred_cov
        + 0.17 * role_cov
        + 0.09 * domain_cov
        + 0.05 * seniority_cov
        + 0.08 * title_cov
    )
    same_company = bool(job.company_key and seed.company_key and job.company_key == seed.company_key)
    total = max(0.0, min(1.0, base_total + _company_bias(job, seed, same_company_viable=same_company_viable)))
    return RouteCandidate(
        seed_id=seed.seed_id,
        label=seed.label,
        route_score=total,
        base_route_score=base_total,
        required_coverage=req_cov,
        core_coverage=core_cov,
        preferred_coverage=preferred_cov,
        role_score=role_cov,
        domain_score=domain_cov,
        seniority_score=seniority_cov,
        title_score=title_cov,
        same_company=same_company,
        seed_company_name=seed.company_name,
        seed_source_job_id=seed.source_job_id,
        company_anchor=seed.company_anchor,
        missing_required=missing_required[:12],
        project_ids=tuple(seed.project_ids),
    )


def _promote_role_aligned_same_company_candidate(scored: list[RouteCandidate]) -> list[RouteCandidate]:
    if not scored:
        return scored
    top = scored[0]
    if not top.same_company or top.role_score >= 0.42:
        return scored
    alternatives = [
        candidate
        for candidate in scored[1:]
        if candidate.same_company
        and candidate.role_score >= 0.55
        and candidate.route_score >= top.route_score - 0.08
        and candidate.required_coverage >= max(0.42, top.required_coverage - 0.25)
    ]
    if not alternatives:
        return scored
    preferred = max(
        alternatives,
        key=lambda candidate: (
            candidate.role_score,
            candidate.required_coverage,
            candidate.title_score,
            candidate.route_score,
        ),
    )
    return [preferred] + [candidate for candidate in scored if candidate.seed_id != preferred.seed_id]


def _is_high_signal_same_company_variant(job: JobFingerprint, top: RouteCandidate, *, explicit_outlier: bool = False) -> bool:
    if explicit_outlier:
        return False
    baseline_variant = (
        top.same_company
        and top.route_score >= 0.9
        and top.required_coverage >= 0.82
        and not top.missing_required
        and (top.role_score >= 0.55 or top.title_score >= 0.45)
    )
    analytics_pm_variant = (
        top.same_company
        and top.company_anchor
        and job.role_family == "pm"
        and top.route_score >= 0.8
        and top.required_coverage >= 0.82
        and top.domain_score >= 0.82
        and not top.missing_required
        and (
            "analytics" in job.title.lower()
            or "insight" in job.title.lower()
            or "analytics" in job.domains
            or "data" in job.domains
        )
    )
    return baseline_variant or analytics_pm_variant


def decide_route(job: JobFingerprint, seeds: Iterable[SeedEntry]) -> RouteDecision:
    seed_list = list(seeds)
    explicit_outlier = load_company_subseed_registry().outlier_for_job(job.job_id) is not None
    provisional = [score_seed(job, seed, same_company_viable=False) for seed in seed_list]
    same_company_exists = any(candidate.same_company for candidate in provisional)
    same_company_viable = (not explicit_outlier) and any(
        candidate.same_company
        and candidate.base_route_score >= 0.62
        and candidate.role_score >= 0.55
        and (candidate.required_coverage >= 0.42 or candidate.title_score >= 0.45)
        for candidate in provisional
    )
    scored = sorted(
        (score_seed(job, seed, same_company_viable=same_company_viable) for seed in seed_list),
        key=lambda candidate: candidate.route_score,
        reverse=True,
    )
    scored = _promote_role_aligned_same_company_candidate(scored)
    top = scored[0]
    company_mode = same_company_viable and top.same_company

    if company_mode:
        reuse_threshold = {
            "route_score": 0.78,
            "required_coverage": 0.68,
            "role_score": 0.55,
            "title_score": 0.2,
        }
        retarget_threshold = {
            "route_score": 0.56,
            "required_coverage": 0.42,
            "role_score": 0.42,
            "title_score": 0.1,
        }
    else:
        reuse_threshold = {
            "route_score": 0.83,
            "required_coverage": 0.82,
            "role_score": 0.82,
            "title_score": 0.5,
        }
        retarget_threshold = {
            "route_score": 0.66,
            "required_coverage": 0.58,
            "role_score": 0.55,
            "title_score": 0.34,
        }

    if job.role_family == "manager":
        route_mode = "new_seed"
        reason = "Management/leadership role is outside the current seed pool; create a dedicated seed if this segment matters."
    elif (
        not (explicit_outlier and top.same_company)
        and
        top.route_score >= reuse_threshold["route_score"]
        and top.required_coverage >= reuse_threshold["required_coverage"]
        and top.role_score >= reuse_threshold["role_score"]
        and top.title_score >= reuse_threshold["title_score"]
    ):
        route_mode = "reuse"
        if company_mode:
            reason = (
                f"同公司一致性优先：沿用 {top.label} 作为 {job.company_name} 的公司内锚点版本，"
                "仅需做轻量岗位侧重点调整。"
            )
        else:
            reason = f"Top seed {top.label} already covers required stack and role framing with only minor or no gaps."
    elif (
        top.route_score >= retarget_threshold["route_score"]
        and top.required_coverage >= retarget_threshold["required_coverage"]
        and top.role_score >= retarget_threshold["role_score"]
        and top.title_score >= retarget_threshold["title_score"]
    ):
        route_mode = "retarget"
        if company_mode:
            reason = (
                f"同公司一致性优先：继续基于 {top.label} 做公司内微调，"
                f"主要补齐 {', '.join(top.missing_required[:5]) or '岗位措辞侧重点'}，避免同公司版本漂移。"
            )
        else:
            reason = (
                f"Top seed {top.label} is directionally compatible but misses some required emphasis: "
                f"{', '.join(top.missing_required[:5]) or 'mostly wording-level changes'}."
            )
    elif _is_high_signal_same_company_variant(job, top, explicit_outlier=explicit_outlier):
        route_mode = "retarget"
        reason = (
            f"同公司一致性优先：{top.label} 已覆盖该岗位的大部分硬信号，"
            "这更像同一项目池内的本职/跨职能变体；保持同一公司经历骨架，只调整 summary、skills 和 bullets 强调点。"
        )
    else:
        route_mode = "new_seed"
        if same_company_exists:
            reason = (
                f"公司内已有 seed，但最接近的 {top.label} 仍不足以稳定覆盖该岗位，"
                f"缺口包括 {', '.join(top.missing_required[:5]) or '多个核心信号'}；需要新增更能代表该公司的锚点 seed。"
            )
        else:
            reason = (
                f"Existing seeds do not cleanly cover this role family/stack combination. "
                f"Closest seed {top.label} still misses {', '.join(top.missing_required[:5]) or 'multiple core signals'}."
            )

    return RouteDecision(
        job=job,
        route_mode=route_mode,
        top_candidate=top,
        top_candidates=scored[:5],
        decision_reason=reason,
        should_generate=route_mode != "reuse",
    )


def sort_rows_by_publish_time(rows: list[dict]) -> list[dict]:
    return sorted(rows, key=lambda row: str(row.get("publish_time", "") or ""), reverse=True)


def summarize_decisions(decisions: Iterable[RouteDecision]) -> dict:
    route_counts = Counter()
    role_route_counts = defaultdict(Counter)
    seed_usage = Counter()
    new_seed_gaps = defaultdict(Counter)
    for decision in decisions:
        route_counts[decision.route_mode] += 1
        role_route_counts[decision.job.role_family][decision.route_mode] += 1
        seed_usage[decision.top_candidate.seed_id] += 1
        if decision.route_mode == "new_seed":
            label = decision.job.role_family
            for skill in decision.top_candidate.missing_required[:5]:
                new_seed_gaps[label][skill] += 1

    return {
        "route_counts": dict(route_counts),
        "role_route_counts": {role: dict(counts) for role, counts in role_route_counts.items()},
        "seed_usage": dict(seed_usage.most_common(25)),
        "new_seed_skill_gaps": {
            role: dict(counter.most_common(10))
            for role, counter in new_seed_gaps.items()
        },
    }
