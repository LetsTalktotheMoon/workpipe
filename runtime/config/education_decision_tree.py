"""
教育经历决策树 - 根据目标JD决定呈现哪些教育经历、如何呈现。
"""
from typing import Dict, List, Any


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
    role_type = jd_profile.get("role_type", "swe")
    tech_required = set(jd_profile.get("tech_required", []))
    business_domain = jd_profile.get("business_domain", "")
    seniority = jd_profile.get("seniority", "entry")

    selected = []
    reasoning_parts = []
    gt_label = "MSCS"
    bisu_track = "Finance"
    add_gt_project = False
    gt_project_reason = None

    # ========================================
    # Step 1: GT MSCS 必选（CS核心学位）
    # ========================================
    selected.append("gt_mscs")
    reasoning_parts.append("GT MSCS: 必选，CS核心学位")

    # ========================================
    # Step 2: 决定是否保留UIUC MSIM
    # ========================================
    uiuc_relevant = _is_uiuc_relevant(role_type, business_domain, tech_required)
    if uiuc_relevant:
        selected.append("uiuc_msim")
        gt_label = "OMSCS"  # 有UIUC就必须标注online
        reasoning_parts.append("UIUC MSIM: 保留（与Data/PM/信息管理相关），GT标注为OMSCS")
    else:
        gt_label = "MSCS"  # 无UIUC可以写MSCS
        reasoning_parts.append("UIUC MSIM: 省略（与目标岗位无直接关联），GT可写MSCS")

    # ========================================
    # Step 3: 决定是否保留BISU MIB
    # ========================================
    bisu_relevant, track = _is_bisu_relevant(role_type, business_domain)
    if bisu_relevant:
        selected.append("bisu_mib")
        bisu_track = track
        reasoning_parts.append(f"BISU MIB: 保留（track={track}，与{business_domain}相关）")
    else:
        reasoning_parts.append("BISU MIB: 省略（与目标岗位无关）")

    # ========================================
    # Step 4: 决定是否保留BNU BA
    # ========================================
    bnu_relevant = _is_bnu_relevant(role_type, business_domain)
    if bnu_relevant:
        selected.append("bnu_ba")
        reasoning_parts.append("BNU BA: 保留（认知科学/语言学与目标岗位有交叉）")
    else:
        reasoning_parts.append("BNU BA: 省略（与目标纯技术岗位无关）")

    # ========================================
    # Step 5: 是否需要GT教育项目
    # ========================================
    hardware_or_system_tech = {
        "FPGA", "Verilog", "VHDL", "SystemVerilog", "CUDA",
        "Embedded", "RTOS", "Assembly", "Computer Architecture",
        "Operating Systems", "Compiler", "Digital Logic",
    }
    uncoverable_by_work = tech_required & hardware_or_system_tech
    if uncoverable_by_work:
        add_gt_project = True
        gt_project_reason = (
            f"JD要求的技术栈 {uncoverable_by_work} 无法从工作经历中cover，"
            "需要通过GT MSCS课堂项目弥补"
        )
        reasoning_parts.append(f"GT项目: 启用（{gt_project_reason}）")
    else:
        # 也检查是否有其他纯CS学术技术栈
        cs_academic_tech = {
            "Distributed Systems", "Database Internals", "Networking",
            "Machine Learning Theory", "Algorithm Design",
        }
        academic_gap = tech_required & cs_academic_tech
        if academic_gap and role_type in ("swe_systems", "swe_infra", "mle"):
            add_gt_project = True
            gt_project_reason = (
                f"JD要求的学术技术方向 {academic_gap} 在工作经历中体现不足，"
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
        "reasoning": " | ".join(reasoning_parts),
    }


def _is_uiuc_relevant(role_type: str, business_domain: str, tech_required: set) -> bool:
    """UIUC MSIM在Data/PM/信息管理方向有价值"""
    if role_type in ("data_analyst", "data_scientist", "data_engineer", "tech_pm"):
        return True
    info_keywords = {"information retrieval", "knowledge management", "data governance"}
    if info_keywords & {t.lower() for t in tech_required}:
        return True
    if business_domain.lower() in ("data_platform", "bi", "analytics"):
        return True
    return False


def _is_bisu_relevant(role_type: str, business_domain: str) -> tuple:
    """BISU MIB在FinTech/国际业务方向有价值，返回(relevant, track)"""
    domain_lower = business_domain.lower()
    if "fintech" in domain_lower or "finance" in domain_lower:
        return True, "Finance"
    if "international" in domain_lower or "global" in domain_lower:
        return True, "Finance"
    if "growth" in domain_lower or "marketing" in domain_lower:
        return True, "Marketing"
    if "analytics" in domain_lower or "bi" in domain_lower:
        return True, "Analytics"
    if role_type == "tech_pm":
        return True, "Finance"
    return False, "Finance"


def _is_bnu_relevant(role_type: str, business_domain: str) -> bool:
    """BNU BA在TechPM/NLP/UX方向有价值"""
    if role_type == "tech_pm":
        return True
    if role_type in ("mle_nlp", "ai_nlp"):
        return True
    if "ux" in business_domain.lower() or "user research" in business_domain.lower():
        return True
    return False
