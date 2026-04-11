"""
JD-cluster retrieval helpers for the experimental B pipeline.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Iterable

from automation.job_router import (
    JobFingerprint,
    build_job_fingerprint,
    build_skill_vocab_from_seeds,
    infer_role_family,
    infer_seniority,
    role_score,
    seniority_score,
)
from automation.seed_registry import load_seed_registry
from automation.text_utils import normalize_token
from models.resume import Resume


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PORTFOLIO_ROOT = ROOT / "data" / "deliverables" / "resume_portfolio"
_SEEDS = load_seed_registry(include_atomizer=False, include_promoted=True)
_SKILL_VOCAB = build_skill_vocab_from_seeds(_SEEDS)


def _load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _review_verdict(review: dict[str, Any]) -> str:
    return str(review.get("verdict", "") or review.get("overall_verdict", "") or "").strip().lower()


def _review_score(review: dict[str, Any]) -> float:
    try:
        return float(review.get("final_score", review.get("weighted_score", 0.0)) or 0.0)
    except Exception:
        return 0.0


def _cluster_terms_from_fingerprint(fp: JobFingerprint) -> tuple[str, ...]:
    strongest: list[str] = []
    for item in sorted(fp.core_skills):
        if item not in strongest:
            strongest.append(item)
        if len(strongest) >= 2:
            break
    for item in sorted(fp.required_skills):
        if item not in strongest:
            strongest.append(item)
        if len(strongest) >= 4:
            break
    domains = sorted(fp.domains)[:2] or ["general"]
    skills = strongest[:3] or ["generalist"]
    return tuple([fp.role_family or "generalist", fp.seniority or "mid", *domains, *skills])


def build_jd_cluster_key(fp: JobFingerprint) -> str:
    return "jd::" + "::".join(_cluster_terms_from_fingerprint(fp))


@dataclass
class ClusterCandidate:
    job_id: str
    company_name: str
    company_key: str
    title: str
    publish_time: str
    source_kind: str
    artifact_dir: Path
    resume_md_path: Path
    review_path: Path
    review_verdict: str
    review_score: float
    row: dict[str, Any]
    fingerprint: JobFingerprint
    jd_cluster_key: str
    project_titles: tuple[str, ...] = field(default_factory=tuple)

    @property
    def company_cluster_key(self) -> str:
        return f"company::{self.company_key or 'unknown-company'}"


@dataclass
class CandidateMatch:
    candidate: ClusterCandidate
    total_score: float
    required_coverage: float
    core_coverage: float
    preferred_coverage: float
    role_score: float
    domain_score: float
    seniority_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.candidate.job_id,
            "company_name": self.candidate.company_name,
            "title": self.candidate.title,
            "artifact_dir": str(self.candidate.artifact_dir),
            "jd_cluster_key": self.candidate.jd_cluster_key,
            "total_score": round(self.total_score, 3),
            "required_coverage": round(self.required_coverage, 3),
            "core_coverage": round(self.core_coverage, 3),
            "preferred_coverage": round(self.preferred_coverage, 3),
            "role_score": round(self.role_score, 3),
            "domain_score": round(self.domain_score, 3),
            "seniority_score": round(self.seniority_score, 3),
            "review_verdict": self.candidate.review_verdict,
            "review_score": round(self.candidate.review_score, 1),
        }


@dataclass
class ClusterSelection:
    cluster_type: str
    cluster_key: str
    candidate_match: CandidateMatch
    cluster_size: int
    company_candidate_count: int
    mature_company_cluster: bool
    reason: str
    top_matches: list[CandidateMatch]


def _coverage(left: set[str], right: set[str]) -> float:
    if not left:
        return 1.0
    return len(left & right) / len(left)


def score_candidate(target: JobFingerprint, candidate: ClusterCandidate) -> CandidateMatch:
    target_required = target.core_skills | target.required_skills
    candidate_required = candidate.fingerprint.core_skills | candidate.fingerprint.required_skills
    required_cov = _coverage(target_required, candidate_required)
    core_cov = _coverage(target.core_skills, candidate_required)
    preferred_cov = _coverage(target.preferred_skills, candidate_required | candidate.fingerprint.preferred_skills)
    role_cov = role_score(target.role_family, candidate.fingerprint.role_family)
    domain_cov = _coverage(target.domains, candidate.fingerprint.domains)
    senior_cov = seniority_score(target.seniority, candidate.fingerprint.seniority)

    total = (
        0.46 * required_cov
        + 0.18 * core_cov
        + 0.06 * preferred_cov
        + 0.18 * role_cov
        + 0.08 * domain_cov
        + 0.04 * senior_cov
    )
    return CandidateMatch(
        candidate=candidate,
        total_score=total,
        required_coverage=required_cov,
        core_coverage=core_cov,
        preferred_coverage=preferred_cov,
        role_score=role_cov,
        domain_score=domain_cov,
        seniority_score=senior_cov,
    )


def _candidate_sort_key(match: CandidateMatch) -> tuple[Any, ...]:
    verdict_rank = 1 if match.candidate.review_verdict == "pass" else 0
    return (
        round(match.total_score, 6),
        verdict_rank,
        round(match.candidate.review_score, 3),
        match.candidate.publish_time,
    )


def _extract_project_titles(resume_md_path: Path) -> tuple[str, ...]:
    try:
        resume = Resume.from_markdown(resume_md_path.read_text(encoding="utf-8"))
    except Exception:
        return ()
    titles = []
    for project in resume.get_all_projects():
        title = str(project.title or "").strip()
        if title and title not in titles:
            titles.append(title)
    return tuple(titles)


def _build_candidate(manifest_path: Path) -> ClusterCandidate | None:
    manifest = _load_json(manifest_path, default={})
    if not isinstance(manifest, dict):
        return None
    artifact_dir = manifest_path.parent
    resume_md_path = artifact_dir / "resume.md"
    review_path = artifact_dir / "review.json"
    row_path = artifact_dir / "sheet_row.json"
    if not resume_md_path.exists() or not row_path.exists():
        return None
    row = _load_json(row_path, default={})
    if not isinstance(row, dict):
        return None
    fingerprint = build_job_fingerprint(row, _SEEDS, skill_vocab=_SKILL_VOCAB)
    review = _load_json(review_path, default={}) if review_path.exists() else {}
    if not isinstance(review, dict):
        review = {}
    return ClusterCandidate(
        job_id=str(manifest.get("job_id", "") or row.get("job_id", "") or "").strip(),
        company_name=str(manifest.get("company_name", "") or row.get("company_name", "") or "").strip(),
        company_key=normalize_token(str(manifest.get("company_name", "") or row.get("company_name", "") or "")),
        title=str(manifest.get("title", "") or row.get("job_title", "") or row.get("job_nlp_title", "") or "").strip(),
        publish_time=str(manifest.get("publish_time", "") or row.get("publish_time", "") or "").strip(),
        source_kind=str(manifest.get("source_kind", "") or "").strip(),
        artifact_dir=artifact_dir,
        resume_md_path=resume_md_path,
        review_path=review_path,
        review_verdict=_review_verdict(review),
        review_score=_review_score(review),
        row=row,
        fingerprint=fingerprint,
        jd_cluster_key=build_jd_cluster_key(fingerprint),
        project_titles=_extract_project_titles(resume_md_path),
    )


def load_cluster_candidates(portfolio_root: str | Path | None = None) -> list[ClusterCandidate]:
    root = DEFAULT_PORTFOLIO_ROOT if portfolio_root is None else Path(portfolio_root)
    manifests = sorted(root.glob("by_company/*/*/*/manifest.json"))
    candidates: list[ClusterCandidate] = []
    for manifest_path in manifests:
        candidate = _build_candidate(manifest_path)
        if candidate is not None and candidate.job_id:
            candidates.append(candidate)
    return candidates


def select_cluster_candidate(
    *,
    target_row: dict[str, Any],
    candidates: Iterable[ClusterCandidate],
    exclude_job_ids: set[str] | None = None,
) -> ClusterSelection:
    exclude_job_ids = {str(item).strip() for item in (exclude_job_ids or set()) if str(item).strip()}
    target_fp = build_job_fingerprint(target_row, _SEEDS, skill_vocab=_SKILL_VOCAB)
    filtered = [candidate for candidate in candidates if candidate.job_id not in exclude_job_ids]
    if not filtered:
        raise ValueError("No eligible cluster candidates found.")

    company_key = normalize_token(str(target_row.get("company_name", "") or ""))
    company_matches = [
        score_candidate(target_fp, candidate)
        for candidate in filtered
        if candidate.company_key and candidate.company_key == company_key
    ]
    company_matches.sort(key=_candidate_sort_key, reverse=True)
    if company_matches:
        top = company_matches[0]
        return ClusterSelection(
            cluster_type="company",
            cluster_key=top.candidate.company_cluster_key,
            candidate_match=top,
            cluster_size=len(company_matches),
            company_candidate_count=len(company_matches),
            mature_company_cluster=len(company_matches) >= 2,
            reason="Target company already has existing delivered resumes; company consistency takes priority.",
            top_matches=company_matches[:5],
        )

    cluster_matches: dict[str, list[CandidateMatch]] = defaultdict(list)
    for candidate in filtered:
        match = score_candidate(target_fp, candidate)
        cluster_matches[candidate.jd_cluster_key].append(match)

    ranked_clusters = []
    for cluster_key, matches in cluster_matches.items():
        matches.sort(key=_candidate_sort_key, reverse=True)
        top = matches[0]
        ranked_clusters.append((top.total_score, top.candidate.review_verdict == "pass", top.candidate.review_score, cluster_key, matches))
    ranked_clusters.sort(reverse=True)
    _, _, _, cluster_key, matches = ranked_clusters[0]
    top = matches[0]
    return ClusterSelection(
        cluster_type="jd",
        cluster_key=cluster_key,
        candidate_match=top,
        cluster_size=len(matches),
        company_candidate_count=0,
        mature_company_cluster=False,
        reason="No same-company resume exists; choose the closest non-company JD cluster and best member within it.",
        top_matches=matches[:5],
    )


def build_company_consistency_context(
    *,
    target_row: dict[str, Any],
    candidates: Iterable[ClusterCandidate],
    exclude_job_ids: set[str] | None = None,
    max_versions: int = 6,
) -> dict[str, Any]:
    exclude_job_ids = {str(item).strip() for item in (exclude_job_ids or set()) if str(item).strip()}
    company_key = normalize_token(str(target_row.get("company_name", "") or ""))
    same_company = [
        candidate
        for candidate in candidates
        if candidate.job_id not in exclude_job_ids and candidate.company_key and candidate.company_key == company_key
    ]
    same_company.sort(key=lambda item: (1 if item.review_verdict == "pass" else 0, item.review_score, item.publish_time), reverse=True)
    same_company = same_company[:max_versions]

    distinct_projects_by_experience: dict[str, set[str]] = defaultdict(set)
    versions: list[dict[str, Any]] = []
    for candidate in same_company:
        try:
            resume = Resume.from_markdown(candidate.resume_md_path.read_text(encoding="utf-8"))
        except Exception:
            resume = None
        experiences = []
        if resume is not None:
            for exp in resume.experiences:
                project_title = ""
                if exp.project and str(exp.project.title or "").strip():
                    project_title = str(exp.project.title or "").strip()
                    distinct_projects_by_experience[exp.id].add(project_title)
                experiences.append(
                    {
                        "experience_id": exp.id,
                        "title": exp.title,
                        "department": exp.department,
                        "team": exp.team,
                        "project_title": project_title,
                    }
                )
        versions.append(
            {
                "job_id": candidate.job_id,
                "title": candidate.title,
                "publish_time": candidate.publish_time,
                "review_verdict": candidate.review_verdict,
                "review_score": round(candidate.review_score, 1),
                "project_titles": list(candidate.project_titles),
                "experiences": experiences,
            }
        )

    high_risk_flags: list[str] = [
        "同公司全部投递版本会被并排审阅；同一时间段不得出现互斥角色、互斥项目池或无法并存的 workload。",
        "同一段经历下的项目池应保持有限且可复用，不得让 reviewer 读出“每投一个岗就发明一个新项目”。",
        "若需要替换项目主题，必须解释为同一团队/同一项目池内的不同强调，而不是完全不同的另一份工作。",
        "不得在不同版本里把同一时间段写成互斥的 team / product line / ownership 设定。",
        "DE 与 Backend SWE 可作为转岗关系共存，但 SWE 版本需要在 summary / framing 中解释‘仅展示相关技能’，不能写成本职自然就是 SWE。",
    ]
    for exp_id, titles in sorted(distinct_projects_by_experience.items()):
        if len(titles) > 2:
            high_risk_flags.append(
                f"{exp_id} 这段经历在现有同公司版本中已经出现 {len(titles)} 个不同项目标题；新版本必须谨慎复用现有项目池，避免继续扩张。"
            )

    return {
        "company_name": str(target_row.get("company_name", "") or ""),
        "version_count": len(versions),
        "versions": versions,
        "high_risk_flags": high_risk_flags,
    }
