"""
Master Writer — 单次 Codex CLI 调用生成完整简历。

替代原赛马三组（conservative/aggressive/narrative），
使用 PLAN→WRITE 两阶段方法，在规划阶段强制 SKILLS ↔ 正文一致性。

核心流程：
1. 调用 Codex CLI 生成 <PLAN> + <RESUME>
2. 从响应中提取 <RESUME> 段
3. 解析 Markdown → Resume dataclass
"""
import logging
import math
import re
from typing import Optional, Tuple

from models.resume import Resume
from models.jd import JDProfile
from core.anthropic_client import get_llm_client, LLMUnavailableError
from automation.resume_repair import audit_resume_markdown, normalize_resume_markdown
from config.candidate_framework import (
    CANDIDATE_FRAMEWORK,
    experience_framework_for_company,
    is_bytedance_target_company,
)
from config.education_decision_tree import decide_education
from config.natural_tech import BASE_NATURAL_TECH, get_all_tiers
from core.prompt_builder import (
    CLUSTER_WRITER_SYSTEM,
    MASTER_WRITER_SYSTEM,
    build_master_writer_prompt,
    build_upgrade_revision_prompt,
    build_seed_retarget_prompt,
)

logger = logging.getLogger(__name__)


NON_TECH_SKILL_TERMS = {
    "agile",
    "code review",
    "cross-functional collaboration",
    "design review",
    "sprint planning",
    "stakeholder management",
}


class MasterWriter:
    """单组 Master Writer，一次调用产出高质量简历。"""

    def __init__(self):
        self.writer_id = "master"
        self.writer_name = "Master Writer"

    def write(self, jd: JDProfile) -> Tuple[str, str]:
        """
        生成简历。

        Returns:
            (resume_markdown: str, plan_text: str)
            - resume_markdown: 完整的简历 Markdown 文本
            - plan_text: 规划阶段内容（供调试/审计用）
        """
        prompt = build_master_writer_prompt(jd)
        cache_key_parts = (
            jd.jd_id or "unknown",
            jd.company or "",
            jd.role_type or "",
            "master_write_v2",
        )
        return self.write_from_prompt(
            prompt,
            jd=jd,
            system_prompt=MASTER_WRITER_SYSTEM,
            cache_key_parts=cache_key_parts,
        )

    def write_from_prompt(
        self,
        prompt: str,
        *,
        jd: JDProfile | None = None,
        system_prompt: str = MASTER_WRITER_SYSTEM,
        cache_key_parts: tuple[str, ...] | None = None,
    ) -> Tuple[str, str]:
        client = get_llm_client()
        cache_key = None
        if cache_key_parts:
            cache_key = client.make_cache_key(*cache_key_parts)

        logger.info("Master Writer 开始按外部 prompt 生成，cache_key=%s", bool(cache_key))
        raw_response = client.call(
            prompt,
            system=system_prompt,
            cache_key=cache_key,
        )
        logger.info("Master Writer 生成完成，响应长度: %d 字符", len(raw_response))

        plan_text, resume_md = _extract_plan_and_resume(raw_response)

        if not resume_md:
            logger.warning("未找到 <RESUME> 标签，尝试直接解析整个响应")
            resume_md = _clean_markdown(raw_response)
        if resume_md and jd is not None:
            resume_md = _stabilize_resume_markdown(resume_md, jd)

        return resume_md, plan_text

    def write_and_parse(self, jd: JDProfile) -> Tuple[Resume, str, str]:
        """
        生成并解析简历。

        Returns:
            (resume: Resume, resume_markdown: str, plan_text: str)
        """
        resume_md, plan_text = self.write(jd)
        resume = Resume.from_markdown(
            resume_md,
            target_jd_id=jd.jd_id,
            target_company=jd.company,
            target_role=jd.title,
            target_seniority=jd.seniority,
        )
        return resume, resume_md, plan_text

    def revise(
        self,
        resume_md: str,
        revision_prompt: str,
        jd: Optional[JDProfile] = None,
        *,
        rewrite_mode: str = "strict",
    ) -> str:
        """
        按审查结果修改简历，返回修改后的 Markdown。
        """
        client = get_llm_client()
        logger.info("Master Writer 开始修改简历...")

        if rewrite_mode == "upgrade":
            system_prompt = (
                "你是专业简历升级专家。你可以在保持不可变字段、真实性边界和核心职业叙事不变的前提下，"
                "重写 summary、skills、experience bullets、project baseline 和项目 framing，以显著提升 JD 匹配度、"
                "scope 表达完整度和整体得分。不要被 seed phrasing、旧 summary 或旧 bullet 选择束缚；"
                "如果旧稿的 framing 本身导致失分，应主动替换成更强、更清晰、但仍真实自洽的表达。"
                "直接输出修改后的完整简历 Markdown，不要附带解释。"
            )
        else:
            system_prompt = (
                "你是专业简历修改专家。严格按照修改指令执行，只改指出的问题，不做额外改动。"
                "直接输出修改后的完整简历 Markdown，不要附带解释。"
            )

        # Seed resume 的 revision 仍需要强模型，不再降级到轻量 review model。
        revised = client.call(
            revision_prompt,
            system=system_prompt,
        )

        revised_md = _clean_markdown(revised)
        if jd is not None and revised_md:
            revised_md = _stabilize_resume_markdown(revised_md, jd)
        logger.info("简历修改完成，长度: %d 字符", len(revised_md))
        return revised_md

    def retarget(
        self,
        seed_resume_md: str,
        jd: JDProfile,
        *,
        seed_label: str = "",
        route_mode: str = "retarget",
        top_candidate: Optional[dict] = None,
    ) -> str:
        """
        基于已有 seed resume 做最小改动式 retarget。
        """
        seed_resume_md = _stabilize_resume_markdown(seed_resume_md, jd)
        prompt = build_seed_retarget_prompt(
            seed_resume_md,
            jd,
            seed_label=seed_label,
            route_mode=route_mode,
            top_candidate=top_candidate,
        )
        revised_md = self.revise(seed_resume_md, prompt)
        return _stabilize_resume_markdown(revised_md, jd)


# ── 辅助函数 ──

def _extract_plan_and_resume(raw: str) -> Tuple[str, str]:
    """从 LLM 响应中提取 <PLAN> 和 <RESUME> 内容"""
    plan_text = ""
    resume_md = ""

    # 提取 <PLAN>...</PLAN>
    plan_match = re.search(r'<PLAN>(.*?)</PLAN>', raw, re.DOTALL | re.IGNORECASE)
    if plan_match:
        plan_text = _sanitize_plan_text(plan_match.group(1).strip())

    # 提取 <RESUME>...</RESUME>
    resume_match = re.search(r'<RESUME>(.*?)</RESUME>', raw, re.DOTALL | re.IGNORECASE)
    if resume_match:
        resume_md = _clean_markdown(resume_match.group(1).strip())

    return plan_text, resume_md


def _sanitize_plan_text(plan_text: str) -> str:
    """
    只保留最终计划，去掉 writer 自言自语式推敲，避免 revision 被噪声带偏。
    """
    if not plan_text:
        return ""

    for marker in ("## 最终 PLAN", "## FINAL PLAN"):
        idx = plan_text.find(marker)
        if idx != -1:
            plan_text = plan_text[idx:]
            break

    noisy_prefixes = (
        "Wait",
        "Actually",
        "Hmm",
        "Let me",
        "I can",
        "I'll",
        "Need to",
        "But ",
    )
    cleaned_lines = [
        line for line in plan_text.splitlines()
        if not line.lstrip().startswith(noisy_prefixes)
    ]

    cleaned = "\n".join(cleaned_lines).strip()
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned


def _clean_markdown(text: str) -> str:
    """清理 Markdown 文本：去掉 code fence 包裹，确保从 ## Professional Summary 开始"""
    cleaned = text.strip()

    # 去掉最外层的 ```markdown ... ``` 或 ``` ... ```
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # 找到第一行和最后一行的 ``` 并去掉
        start_idx = 0
        end_idx = len(lines) - 1
        if lines[0].startswith("```"):
            start_idx = 1
        if lines[-1].strip() == "```":
            end_idx = len(lines) - 1
        cleaned = "\n".join(lines[start_idx:end_idx]).strip()

    # 确保从 ## Professional Summary 开始（去掉前面的解释性文字）
    summary_idx = cleaned.find("## Professional Summary")
    if summary_idx > 0:
        cleaned = cleaned[summary_idx:]
    elif summary_idx == -1:
        # 尝试找 ## Skills 或其他 section
        for header in ["## Skills", "## Experience", "## Education"]:
            idx = cleaned.find(header)
            if idx > 0:
                cleaned = cleaned[idx:]
                break

    return cleaned.strip()


def _stabilize_resume_markdown(resume_md: str, jd: JDProfile) -> str:
    """
    生成后做一次 deterministic lint，修复最常见的 Skills ↔ 正文失配。
    """
    try:
        resume = Resume.from_markdown(
            resume_md,
            target_jd_id=jd.jd_id,
            target_company=jd.company,
            target_role=jd.title,
            target_seniority=jd.seniority,
        )
    except Exception as exc:
        logger.warning("生成后简历解析失败，跳过稳定化: %s", exc)
        return resume_md

    body_supported = _collect_body_supported_tech(resume, jd)
    required_tech = {_canonical_tech_name(item) for item in (getattr(jd, "tech_required", []) or []) if item}
    removed = _remove_unsupported_skills(resume, body_supported, required_tech) if body_supported else []
    added = _add_missing_body_tech_to_skills(resume, body_supported) if body_supported else []
    _canonicalize_skill_categories(resume)
    immutable_changed = _normalize_immutable_experience_fields(resume)
    education_changed = _normalize_education_entries(resume, jd)
    scope_changed = _normalize_scope_framing(resume, jd)
    _clamp_summary_experience_claim(resume)
    normalized_md = resume.to_markdown()
    normalized_md, repair_changes = normalize_resume_markdown(normalized_md, target_company=jd.company)
    if (
        not removed
        and not added
        and not immutable_changed
        and not education_changed
        and not scope_changed
        and not repair_changes
        and normalized_md == resume_md
    ):
        return resume_md

    residual_issues = audit_resume_markdown(normalized_md, target_company=jd.company)
    logger.info(
        "Master Writer 稳定化修复 Skills/Immutable/Education/Scope/Repair 对齐: +%s -%s | immutable_changed=%s education_changed=%s scope_changed=%s repair_changes=%s residual_issues=%s",
        added or [],
        removed or [],
        immutable_changed,
        education_changed,
        scope_changed,
        repair_changes,
        [issue.code for issue in residual_issues],
    )
    return normalized_md


def _collect_body_supported_tech(resume: Resume, jd: JDProfile) -> set[str]:
    known_tech = set(resume.get_skills_list())
    known_tech.update(getattr(jd, "tech_required", []) or [])
    known_tech.update(getattr(jd, "tech_preferred", []) or [])
    for exp_id in BASE_NATURAL_TECH:
        known_tech.update(get_all_tiers(exp_id))

    known_map = {
        _normalize_tech_name(_canonical_tech_name(item)): _canonical_tech_name(item)
        for item in known_tech
        if item
    }

    body_supported = set()
    for bullet in resume.get_all_bullets() + resume.get_all_project_bullets():
        for item in bullet.tech_stack_used:
            if _is_hedged_tech_reference(bullet.text, item):
                continue
            normalized = _normalize_tech_name(item)
            if normalized in NON_TECH_SKILL_TERMS:
                continue
            if normalized in known_map:
                body_supported.add(known_map[normalized])
                continue
            for known_normalized, canonical in known_map.items():
                if known_normalized in NON_TECH_SKILL_TERMS:
                    continue
                if _tech_fragment_contains(normalized, known_normalized):
                    body_supported.add(canonical)
    return body_supported


def _is_hedged_tech_reference(text: str, tech: str) -> bool:
    if not text or not tech:
        return False

    tech_pattern = re.escape(tech)
    hedged_patterns = (
        rf"\*\*{tech_pattern}\*\*-\s*adjacent",
        rf"{tech_pattern}-\s*adjacent",
        rf"adjacent to \*\*{tech_pattern}\*\*",
        rf"adjacent to {tech_pattern}",
    )
    lowered = text.lower()
    return any(re.search(pattern, lowered, re.IGNORECASE) for pattern in hedged_patterns)


def _tech_fragment_contains(fragment: str, tech: str) -> bool:
    if not fragment or not tech:
        return False
    pattern = r"(?<![a-z0-9])" + re.escape(tech).replace(r"\ ", r"\s+") + r"(?![a-z0-9])"
    return re.search(pattern, fragment, re.IGNORECASE) is not None


def _remove_unsupported_skills(
    resume: Resume,
    body_supported: set[str],
    required_tech: set[str] | None = None,
) -> list[str]:
    supported_norm = {_normalize_tech_name(item) for item in body_supported}
    required_norm = {
        _normalize_tech_name(item)
        for item in (required_tech or set())
    }
    removed: list[str] = []

    for category in resume.skills:
        kept = []
        for skill in category.skills:
            normalized = _normalize_tech_name(skill)
            if normalized in supported_norm or normalized in required_norm:
                kept.append(skill)
            else:
                removed.append(skill)
        category.skills = kept

    resume.skills = [category for category in resume.skills if category.skills]
    return removed


def _add_missing_body_tech_to_skills(resume: Resume, body_supported: set[str]) -> list[str]:
    current_norm = {
        _normalize_tech_name(skill)
        for category in resume.skills
        for skill in category.skills
    }
    added: list[str] = []

    for tech in sorted(body_supported):
        normalized = _normalize_tech_name(tech)
        if normalized in current_norm:
            continue
        category = _pick_skill_category(resume, tech)
        category.skills.append(tech)
        current_norm.add(normalized)
        added.append(tech)

    return added


def _canonicalize_skill_categories(resume: Resume) -> None:
    for category in resume.skills:
        deduped = []
        seen = set()
        for skill in category.skills:
            canonical = _canonical_tech_name(skill)
            normalized = _normalize_tech_name(canonical)
            if normalized in seen:
                continue
            seen.add(normalized)
            deduped.append(canonical)
        category.skills = deduped


def _pick_skill_category(resume: Resume, tech: str):
    family = _tech_family(tech)
    category_keywords = {
        "backend": ("programming", "backend", "platform", "systems", "engineering"),
        "cloud": ("cloud", "ml", "ai", "network", "platform"),
        "data": ("data", "analytics", "experimentation"),
    }
    for category in resume.skills:
        name_lower = category.name.lower()
        if any(keyword in name_lower for keyword in category_keywords[family]):
            return category

    if resume.skills:
        return resume.skills[-1]

    from models.resume import SkillCategory
    fallback_name = {
        "backend": "Programming & Systems",
        "cloud": "Cloud & AI",
        "data": "Data & Analytics",
    }[family]
    category = SkillCategory(name=fallback_name, skills=[])
    resume.skills.append(category)
    return category


def _clamp_summary_experience_claim(resume: Resume) -> None:
    if not resume.summary:
        return
    max_years = _candidate_max_years_claim(resume.target_company)
    if max_years <= 0:
        return

    pattern = re.compile(r"\*\*(\d+)\+\s+years\*\*")
    updated_summary = []
    for sentence in resume.summary:
        def _replace(match: re.Match[str]) -> str:
            claimed = int(match.group(1))
            if claimed <= max_years:
                return match.group(0)
            return f"**{max_years}+ years**"

        updated_summary.append(pattern.sub(_replace, sentence))
    resume.summary = updated_summary


def _normalize_education_entries(resume: Resume, jd: JDProfile) -> bool:
    desired = decide_education(_jd_profile_for_education_tree(jd))
    desired_ids = desired.get("selected_education", [])
    desired_by_id = {item["id"]: item for item in CANDIDATE_FRAMEWORK.get("education", [])}

    existing_by_id = {}
    for edu in resume.education:
        edu_id = _canonical_education_id(edu.id, edu.school)
        if edu_id not in existing_by_id:
            existing_by_id[edu_id] = edu

    normalized = []
    for edu_id in desired_ids:
        framework = desired_by_id.get(edu_id)
        if not framework:
            continue

        existing = existing_by_id.get(edu_id)
        if existing is None:
            from models.resume import Education
            existing = Education(
                id=edu_id,
                degree=framework["degree"],
                school=framework["school"],
                dates=framework["dates"],
            )

        existing.id = edu_id
        existing.school = framework["school"]
        existing.dates = framework["dates"]

        if edu_id == "gt_mscs":
            existing.degree = (
                framework["degree_variant_omscs"]
                if desired.get("gt_label") == "OMSCS"
                else framework["degree"]
            )
            existing.track = ""
        elif edu_id == "bisu_mib":
            existing.degree = framework["degree"]
            existing.track = desired.get("bisu_track", framework.get("track", ""))
        else:
            existing.degree = framework["degree"]
            existing.track = framework.get("track", "")

        normalized.append(existing)

    before = resume.to_markdown() if resume.education else ""
    resume.education = normalized
    after = resume.to_markdown() if resume.education else ""
    return before != after


def _normalize_immutable_experience_fields(resume: Resume) -> bool:
    target_company = getattr(resume, "target_company", "") or ""
    framework_by_id = {
        item["id"]: item for item in experience_framework_for_company(target_company)
    }
    changed = False
    filtered_experiences = []
    for exp in resume.experiences:
        if is_bytedance_target_company(target_company):
            exp_company = str(getattr(exp, "company", "") or "").strip().lower()
            exp_dept = str(getattr(exp, "department", "") or "").strip().lower()
            if exp.id == "tiktok_intern" or "tiktok" in exp_company or "bytedance" in exp_company or exp_dept == "security":
                changed = True
                continue
        expected = framework_by_id.get(exp.id)
        if not expected:
            filtered_experiences.append(exp)
            continue
        for field in ("company", "department", "title", "dates", "location"):
            desired = expected.get(field, "")
            if desired and getattr(exp, field) != desired:
                setattr(exp, field, desired)
                changed = True
        filtered_experiences.append(exp)
    resume.experiences = filtered_experiences
    return changed


def _normalize_scope_framing(resume: Resume, jd: JDProfile) -> bool:
    changed = False
    low_scope_target = (jd.seniority or "").lower() in {"intern", "ng", "entry", "junior"}

    for exp in resume.experiences:
        if exp.id != "didi_senior_da":
            continue

        new_note = _soften_didi_cross_functional_note(
            exp.cross_functional_note,
            low_scope_target=low_scope_target,
        )
        if new_note != exp.cross_functional_note:
            exp.cross_functional_note = new_note
            changed = True

        for bullet in exp.bullets:
            original = bullet.text
            bullet.text = _soften_didi_ownership_bullet(
                bullet.text,
                low_scope_target=low_scope_target,
            )
            if bullet.text != original:
                _refresh_bullet_metadata(bullet)
                changed = True

    return changed


def _soften_didi_cross_functional_note(note: str, *, low_scope_target: bool) -> str:
    stripped = (note or "").strip()
    if not stripped or "cross-functional" not in stripped.lower():
        return stripped
    return (
        "Data lead within a **13-person** cross-functional squad "
        "spanning product, backend, frontend, mobile, and ops."
    )


def _soften_didi_ownership_bullet(text: str, *, low_scope_target: bool) -> str:
    updated = text
    if (
        "global operating review" in updated.lower()
        or "global operating reviews" in updated.lower()
        or ("latam" in updated.lower() and "management" in updated.lower())
    ):
        return (
            "Represented the headquarters data organization in biweekly global operating reviews, "
            "and translated performance signals into two-week recommendations adopted by management "
            "and LATAM frontline teams."
        )
    if low_scope_target:
        updated = re.sub(
            r"^Led a \*\*13-person\*\* cross-functional squad to\s+",
            "Partnered with backend and product teammates to ",
            updated,
        )
        updated = re.sub(
            r"^Led a 13-person cross-functional squad to\s+",
            "Partnered with backend and product teammates to ",
            updated,
        )
        updated = re.sub(
            r"^Led a \*\*13-person cross-functional team\*\* to\s+",
            "Partnered with backend and product teammates to ",
            updated,
        )
        updated = re.sub(
            r"^Led a 13-person cross-functional team to\s+",
            "Partnered with backend and product teammates to ",
            updated,
        )
        updated = re.sub(
            r"^Led \*\*Agile\*\* delivery for\s+",
            "Coordinated Agile delivery for ",
            updated,
        )
        updated = re.sub(
            r"^Led Agile delivery for\s+",
            "Coordinated Agile delivery for ",
            updated,
        )
        updated = re.sub(
            r"^Led a \\*\\*13-person cross-functional\\*\\* squad in an \\*\\*Agile\\*\\* delivery cadence,\s*",
            "Coordinated analytics workstreams within a **13-person** cross-functional squad, ",
            updated,
        )
        updated = re.sub(
            r"^Led a 13-person cross-functional squad in an Agile delivery cadence,\s*",
            "Coordinated analytics workstreams within a 13-person cross-functional squad, ",
            updated,
        )
        updated = re.sub(
            r"^Led a \\*\\*13-person cross-functional\\*\\* team in an \\*\\*Agile\\*\\* delivery cadence,\s*",
            "Coordinated analytics workstreams within a **13-person** cross-functional team, ",
            updated,
        )
        updated = re.sub(
            r"^Led a 13-person cross-functional team in an Agile delivery cadence,\s*",
            "Coordinated analytics workstreams within a 13-person cross-functional team, ",
            updated,
        )
    return updated


def _refresh_bullet_metadata(bullet) -> None:
    refreshed = Resume._parse_bullet(bullet.text)
    bullet.has_data = refreshed.has_data
    bullet.tech_stack_used = refreshed.tech_stack_used
    bullet.verb = refreshed.verb


def _jd_profile_for_education_tree(jd: JDProfile) -> dict:
    role_map = {
        "swe_backend": "swe",
        "swe_frontend": "swe",
        "swe_fullstack": "swe",
        "backend_generalist": "swe",
        "data_science": "data_scientist",
        "data_analytics": "data_analyst",
        "data_platform": "data_engineer",
        "mle": "mle",
        "ai_ml_swe": "mle",
        "tech_pm": "tech_pm",
    }
    return {
        "role_type": role_map.get(jd.role_type, jd.role_type or "swe"),
        "tech_required": list(getattr(jd, "tech_required", []) or []),
        "business_domain": getattr(jd, "business_domain", "") or "",
        "seniority": getattr(jd, "seniority", "") or "",
    }


def _canonical_education_id(edu_id: str, school: str) -> str:
    normalized_id = (edu_id or "").strip().lower()
    school_lower = (school or "").strip().lower()

    if normalized_id == "gt_mscs" or "georgia institute of technology" in school_lower:
        return "gt_mscs"
    if normalized_id == "uiuc_msim" or "university of illinois urbana-champaign" in school_lower:
        return "uiuc_msim"
    if normalized_id == "bisu_mib" or "beijing international studies university" in school_lower:
        return "bisu_mib"
    if normalized_id == "bnu_ba" or "beijing normal university" in school_lower:
        return "bnu_ba"
    return normalized_id


def _candidate_max_years_claim(target_company: str = "") -> int:
    total_months = sum(
        int(exp.get("duration_months", 0))
        for exp in experience_framework_for_company(target_company)
    )
    if total_months <= 0:
        return 0
    return math.ceil(total_months / 12)


def _tech_family(tech: str) -> str:
    normalized = _normalize_tech_name(tech)
    cloud = {
        "aws", "s3", "bedrock", "openai", "rag", "llm", "prometheus",
        "docker", "kubernetes", "ml infrastructure", "model deployment",
        "generative ai",
    }
    data = {
        "sql", "hive", "spark sql", "pandas", "numpy", "jupyter",
        "airflow", "etl", "a/b testing", "scikit-learn",
    }
    if normalized in cloud:
        return "cloud"
    if normalized in data:
        return "data"
    return "backend"


def _canonical_tech_name(tech: str) -> str:
    cleaned = re.sub(r"[*`]+", "", tech or "").strip()
    normalized = " ".join(cleaned.lower().split())
    special_cases = {
        "a/b testing": "A/B Testing",
        "api": "API",
        "aws": "AWS",
        "aws bedrock": "AWS Bedrock",
        "amazon bedrock": "AWS Bedrock",
        "bedrock": "AWS Bedrock",
        "ci/cd": "CI/CD",
        "ecs": "ECS",
        "gcp": "GCP",
        "github actions": "GitHub Actions",
        "grpc": "gRPC",
        "llm": "LLM",
        "ml infrastructure": "ML Infrastructure",
        "model deployment": "Model Deployment",
        "mysql": "MySQL",
        "numpy": "NumPy",
        "openai": "OpenAI",
        "postgresql": "PostgreSQL",
        "rag": "RAG",
        "s3": "S3",
        "spark sql": "Spark SQL",
    }
    if normalized in special_cases:
        return special_cases[normalized]
    return JDProfile._capitalize_tech(" ".join(cleaned.split()))


def _normalize_tech_name(tech: str) -> str:
    cleaned = re.sub(r"[*`]+", "", tech or "").strip().lower()
    normalized = " ".join(cleaned.split())
    aliases = {
        "amazon bedrock": "aws bedrock",
        "aws bedrock": "aws bedrock",
        "bedrock": "aws bedrock",
        "openai api": "openai",
        "aws s3": "s3",
        "github actions": "github actions",
        "rag service": "rag",
    }
    return aliases.get(normalized, normalized)
