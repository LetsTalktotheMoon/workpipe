"""
教育经历决策树 - 根据目标JD决定呈现哪些教育经历、如何呈现。
"""
from __future__ import annotations

import re
from typing import Any, Dict


PM_ROLE_TYPES = {
    "pm",
    "product",
    "product_manager",
    "product_owner",
    "program_manager",
    "project_manager",
    "tech_pm",
    "technical_program_manager",
}

UIUC_INFO_KEYWORDS = {
    "information management",
    "information science",
    "information systems",
    "information architecture",
    "knowledge management",
    "data governance",
}

BISU_FINANCE_KEYWORDS = {
    "finance",
    "financial",
    "fintech",
    "bank",
    "banking",
    "payment",
    "payments",
    "lending",
    "credit",
    "risk",
    "treasury",
    "cross-border",
    "international business",
    "global business",
    "overseas",
    "global expansion",
}

BISU_GROWTH_KEYWORDS = {
    "growth",
    "marketing",
}

BISU_ANALYTICS_KEYWORDS = {
    "analytics",
    "business intelligence",
    "bi",
}

BNU_EDUCATION_KEYWORDS = {
    "education",
    "edtech",
    "education technology",
    "k-12",
    "k12",
    "teacher",
    "student",
    "school",
    "classroom",
    "curriculum",
    "instructional design",
    "china education",
    "教育",
    "教培",
    "在线教育",
}

BNU_RESEARCH_KEYWORDS = {
    "ux research",
    "user research",
    "user experience",
    "cognitive science",
    "linguistics",
    "nlp",
}

HARDWARE_OR_SYSTEM_TECH = {
    "FPGA",
    "Verilog",
    "VHDL",
    "SystemVerilog",
    "CUDA",
    "Embedded",
    "RTOS",
    "Assembly",
    "Computer Architecture",
    "Operating Systems",
    "Compiler",
    "Digital Logic",
}

CS_ACADEMIC_TECH = {
    "Distributed Systems",
    "Database Internals",
    "Networking",
    "Machine Learning Theory",
    "Algorithm Design",
}


def decide_education(jd_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据JD profile决定教育经历的呈现策略。

    Returns:
        {
            "selected_education": [edu_id, ...],
            "gt_label": "MSCS" | "OMSCS",
            "bisu_track": "Finance" | "Analytics" | ...,
            "add_gt_project": bool,
            "gt_project_reason": str | None,
            "reasoning": str,
        }
    """
    signals = _extract_signals(jd_profile)
    role_type = signals["role_type"]
    business_domain = signals["business_domain"]
    seniority = signals["seniority"]
    tech_required = set(signals["tech_required"])
    tech_preferred = set(signals["tech_preferred"])
    responsibilities = signals["responsibilities"]
    qualifications_required = signals["qualifications_required"]
    qualifications_preferred = signals["qualifications_preferred"]
    all_text = signals["all_text"]
    required_text = signals["required_text"]

    selected = []
    reasoning_parts = []
    gt_label = "MSCS"
    bisu_track = "Finance"
    add_gt_project = False
    gt_project_reason = None

    # ========================================
    # Step 1: GT MSCS 默认保留
    # ========================================
    selected.append("gt_mscs")
    reasoning_parts.append("GT MSCS: 默认保留（所有线路共享的核心 CS 学位）")

    # ========================================
    # Step 2: 决定是否保留UIUC MSIM
    # ========================================
    uiuc_relevant, uiuc_reason = _is_uiuc_relevant(signals)
    if uiuc_relevant:
        selected.append("uiuc_msim")
        gt_label = "OMSCS"  # 有UIUC就必须标注online
        reasoning_parts.append(f"UIUC MSIM: 保留（{uiuc_reason}），GT标注为OMSCS")
    else:
        gt_label = "MSCS"  # 无UIUC可以写MSCS
        reasoning_parts.append("UIUC MSIM: 省略（未命中 PM / 信息管理 / Illinois 条件），GT可写MSCS")

    # ========================================
    # Step 3: 决定是否保留BISU MIB
    # ========================================
    bisu_relevant, track, bisu_reason = _is_bisu_relevant(signals)
    if bisu_relevant:
        selected.append("bisu_mib")
        bisu_track = track
        reasoning_parts.append(f"BISU MIB: 保留（track={track}，{bisu_reason}）")
    else:
        reasoning_parts.append("BISU MIB: 省略（与目标岗位无关）")

    # ========================================
    # Step 4: 决定是否保留BNU BA
    # ========================================
    bnu_relevant, bnu_reason = _is_bnu_relevant(signals)
    if bnu_relevant:
        selected.append("bnu_ba")
        reasoning_parts.append(f"BNU BA: 保留（{bnu_reason}）")
    else:
        reasoning_parts.append("BNU BA: 省略（与目标纯技术岗位无关）")

    # ========================================
    # Step 5: 是否需要GT教育项目
    # ========================================
    all_tech = tech_required | tech_preferred
    uncoverable_by_work = all_tech & HARDWARE_OR_SYSTEM_TECH
    if uncoverable_by_work:
        add_gt_project = True
        gt_project_reason = (
            f"JD要求的技术栈 {sorted(uncoverable_by_work)} 无法从工作经历中cover，"
            "需要通过GT MSCS课堂项目弥补"
        )
        reasoning_parts.append(f"GT项目: 启用（{gt_project_reason}）")
    else:
        academic_gap = all_tech & CS_ACADEMIC_TECH
        academic_context = _contains_any(all_text, {"systems", "backend", "infrastructure", "infra"})
        if academic_gap and role_type in ("swe_systems", "swe_infra", "mle"):
            add_gt_project = True
            gt_project_reason = (
                f"JD要求的学术技术方向 {sorted(academic_gap)} 在工作经历中体现不足，"
                "GT MSCS课堂项目可补充深度"
            )
            reasoning_parts.append(f"GT项目: 启用（{gt_project_reason}）")
        elif academic_gap and academic_context:
            add_gt_project = True
            gt_project_reason = (
                f"JD文本中出现 {sorted(academic_gap)} 这类学术/系统技术方向，"
                "GT MSCS课堂项目可补充深度"
            )
            reasoning_parts.append(f"GT项目: 启用（{gt_project_reason}）")
        else:
            reasoning_parts.append("GT项目: 不启用（工作经历可cover JD技术栈）")

    return {
        "selected_education": selected,
        "gt_label": gt_label,
        "bisu_track": bisu_track,
        "add_gt_project": add_gt_project,
        "gt_project_reason": gt_project_reason,
        "decision_inputs": signals,
        "reasoning": " | ".join(reasoning_parts),
    }


def _extract_signals(jd_profile: Dict[str, Any]) -> Dict[str, Any]:
    role_type = _normalize_text(_profile_get(jd_profile, "role_type", "swe")) or "swe"
    title = _normalize_text(_profile_get(jd_profile, "title", ""))
    team_direction = _normalize_text(_profile_get(jd_profile, "team_direction", ""))
    business_domain = _normalize_text(_profile_get(jd_profile, "business_domain", ""))
    company = _normalize_text(_profile_get(jd_profile, "company", ""))
    seniority = _normalize_text(_profile_get(jd_profile, "seniority", "entry")) or "entry"
    raw_text = _profile_get(jd_profile, "raw_text", "") or ""

    tech_required = _flatten_text_items(_profile_get(jd_profile, "tech_required", []))
    tech_preferred = _flatten_text_items(_profile_get(jd_profile, "tech_preferred", []))
    tech_or_groups = _flatten_text_items(_profile_get(jd_profile, "tech_or_groups", []))
    soft_required = _flatten_text_items(_profile_get(jd_profile, "soft_required", []))
    soft_preferred = _flatten_text_items(_profile_get(jd_profile, "soft_preferred", []))
    responsibilities = _flatten_text_items(_profile_get(jd_profile, "responsibilities", []))
    qualifications_required = _flatten_text_items(_profile_get(jd_profile, "qualifications_required", []))
    qualifications_preferred = _flatten_text_items(_profile_get(jd_profile, "qualifications_preferred", []))

    all_text_parts = [
        title,
        team_direction,
        business_domain,
        company,
        raw_text,
        role_type,
        seniority,
        *tech_required,
        *tech_preferred,
        *tech_or_groups,
        *soft_required,
        *soft_preferred,
        *responsibilities,
        *qualifications_required,
        *qualifications_preferred,
    ]
    all_text = " ".join(part for part in all_text_parts if part).lower()
    required_text = " ".join(
        part for part in (
            *responsibilities,
            *qualifications_required,
            *soft_required,
        )
        if part
    ).lower()

    return {
        "role_type": role_type,
        "title": title,
        "team_direction": team_direction,
        "business_domain": business_domain,
        "company": company,
        "seniority": seniority,
        "raw_text": raw_text,
        "tech_required": sorted(item for item in tech_required if item),
        "tech_preferred": sorted(item for item in tech_preferred if item),
        "tech_or_groups": sorted(item for item in tech_or_groups if item),
        "soft_required": soft_required,
        "soft_preferred": soft_preferred,
        "responsibilities": responsibilities,
        "qualifications_required": qualifications_required,
        "qualifications_preferred": qualifications_preferred,
        "all_text": all_text,
        "required_text": required_text,
    }


def _is_uiuc_relevant(signals: Dict[str, Any]) -> tuple[bool, str]:
    """UIUC MSIM 只在 PM / 信息管理 / Illinois 条件下保留。"""
    if _is_pm_direction(signals):
        return True, "PM方向"
    if _contains_any(signals["required_text"], UIUC_INFO_KEYWORDS):
        return True, "信息管理经验为岗位必须要求"
    if _mentions_illinois(signals["all_text"]):
        return True, "岗位仅在 Illinois/IL 开设"
    return False, ""


def _is_bisu_relevant(signals: Dict[str, Any]) -> tuple[bool, str, str]:
    """BISU MIB 在 FinTech / 国际业务 / 增长 / 分析方向保留。"""
    all_text = signals["all_text"]
    if signals["role_type"] == "tech_pm" or _contains_any(all_text, {"tech pm", "product management"}):
        return True, "Finance", "tech / product 方向与金融业务桥接"
    if _contains_any(all_text, BISU_FINANCE_KEYWORDS):
        return True, "Finance", "金融 / 国际业务相关"
    if _contains_any(all_text, BISU_GROWTH_KEYWORDS):
        return True, "Marketing", "增长 / 市场方向相关"
    if _contains_any(all_text, BISU_ANALYTICS_KEYWORDS):
        return True, "Analytics", "数据分析 / BI 方向相关"
    return False, "Finance", ""


def _is_bnu_relevant(signals: Dict[str, Any]) -> tuple[bool, str]:
    """BNU BA 在 TechPM / NLP / UX Research / 教育行业保留。"""
    all_text = signals["all_text"]
    if signals["role_type"] == "tech_pm":
        return True, "TechPM 方向"
    if signals["role_type"] in ("mle_nlp", "ai_nlp"):
        return True, "NLP 方向"
    if _contains_any(all_text, BNU_RESEARCH_KEYWORDS):
        if _contains_any(all_text, {"ux", "ux research", "user experience", "user research"}):
            return True, "UX Research 相关"
        return True, "NLP / 认知科学 / 语言学相关"
    if _contains_any(all_text, BNU_EDUCATION_KEYWORDS):
        return True, "中国教育行业 / 教育背景相关"
    return False, ""


def _is_pm_direction(signals: Dict[str, Any]) -> bool:
    if signals["role_type"] in PM_ROLE_TYPES:
        return True
    text = signals["all_text"]
    return _contains_any(
        text,
        {
            "product manager",
            "product management",
            "technical program manager",
            "program manager",
            "project manager",
            "product owner",
        },
    )


def _mentions_illinois(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    return any(
        pattern.search(lowered)
        for pattern in (
            re.compile(r"\billinois\b"),
            re.compile(r"\bil\b"),
            re.compile(r"chicago,\s*il\b"),
            re.compile(r"\bstate of illinois\b"),
        )
    )


def _contains_any(text: str, keywords: set[str]) -> bool:
    return any(_contains_keyword(text, keyword) for keyword in keywords)


def _contains_keyword(text: str, keyword: str) -> bool:
    if not text or not keyword:
        return False
    text_lower = text.lower()
    keyword_lower = keyword.lower()
    if " " in keyword_lower or "-" in keyword_lower:
        return keyword_lower in text_lower
    return re.search(rf"\b{re.escape(keyword_lower)}\b", text_lower) is not None


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _profile_get(jd_profile: Any, key: str, default: Any = None) -> Any:
    if isinstance(jd_profile, dict):
        return jd_profile.get(key, default)
    return getattr(jd_profile, key, default)


def _flatten_text_items(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, dict):
        items: list[str] = []
        for item in value.values():
            items.extend(_flatten_text_items(item))
        return items
    if isinstance(value, (list, tuple, set)):
        items = []
        for item in value:
            items.extend(_flatten_text_items(item))
        return items
    text = str(value).strip()
    return [text] if text else []
