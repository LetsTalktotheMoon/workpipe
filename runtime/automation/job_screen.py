from __future__ import annotations

import re
from dataclasses import dataclass


# ─────────────────────────── 硬拒 — 职能类型 ───────────────────────────

# 标题中出现即硬拒（精确子串，注意不要误伤 "Salesforce"、"AVP"）
HARD_REJECT_TITLE_MARKERS = {
    # 管理层（"vice president" 由 _is_vp_title() 精确处理，避免误杀 AVP）
    "chief ",
    "head of ",
    "general manager",
    # 销售 / GTM（精确词段，避免 "Salesforce" 误判）
    "account executive",
    "account manager",
    "sales engineer",        # 非 SWE，专门做预售的
    "sales manager",
    "sales director",
    "business development",
    "partner manager",
    "partner success",
    "customer success",
    "customer success manager",
    "revenue operations",
    # 招聘 / HR
    "recruiter",
    "talent acquisition",
    "talent partner",
    "hr business partner",
    # 法务
    "counsel",
    "attorney",
    "paralegal",
    # 医疗
    "nurse",
    "physician",
    "therapist",
    "pharmacist",
    "medical assistant",
    "dentist",
    "surgeon",
    # 硬件 / 嵌入式（纯 HW，无法以 SWE 故事覆盖）
    "mechanical engineer",
    "electrical engineer",
    "embedded engineer",
    "firmware engineer",
    "robotics engineer",
    "hardware engineer",
    "controls engineer",
    "manufacturing engineer",
    "silicon engineer",
    "chip design",
    "asic design",
    "fpga engineer",
    "pcb engineer",
    # 财务 / 会计
    "financial analyst",
    "finance manager",
    "accountant",
    "controller",
    "treasury",
    "procurement",
    "auditor",
    # 供应链 / 运营（非 tech）
    "supply chain manager",
    "operations manager",
    "warehouse manager",
    "logistics manager",
    "field technician",
    "field service engineer",
    # 市场营销（非 tech）
    "growth marketing",
    "product marketing",
    "content marketing",
    "seo specialist",
    "social media manager",
    # 纯运维 / 非 SWE 的 IT 支持
    "helpdesk",
    "it support specialist",
    "desktop support",
}

# 基于 taxonomy 的硬拒
HARD_REJECT_TAXONOMY_MARKERS = {
    "sales",
    "business development",
    "customer success",
    "recruiting",
    "talent acquisition",
    "human resources",
    "legal and compliance",
    "marketing",
    "accounting",
    "finance",
}

# ─────────────────────── 软保留（保留但标记为 soft_review）───────────────────────

SOFT_REVIEW_TITLE_MARKERS = {
    "business analyst",
    "product manager",
    "program manager",
    "project manager",
    "solutions engineer",
    "ai strategist",
    "consultant",
    "implementation",
    "architect",
    "principal",
    "staff ",
    "senior staff",
    "distinguished",
    "fellow",
    # 运营类 SWE 相邻岗（保留但需人工确认）
    "technical account manager",
    "developer advocate",
    "devrel",
}

# ─────────────────────── 非目标 taxonomy（补充硬拒）──────────────────────────────

NON_TARGET_TAXONOMY_MARKERS = {
    "accounting and finance",
    "human resources",
    "legal",
}

# ─────────────────────── PhD 研究岗（需 JD 中明写 PhD）───────────────────────────

PHD_RESEARCH_TITLE_MARKERS = {
    "research scientist",
    "applied scientist",
    "quantitative researcher",
    "quant researcher",
    "economist",
    "postdoctoral",
    "postdoc",
    "research engineer",
}


@dataclass(frozen=True)
class JobScreenDecision:
    accepted: bool
    reason: str
    level: str
    tags: tuple[str, ...] = ()


def _title_text(row: dict) -> str:
    return f"{row.get('job_title', '')} {row.get('job_nlp_title', '')}".strip().lower()


def _taxonomy_text(row: dict) -> str:
    return str(row.get("taxonomy_v3", "") or "").strip().lower()


def _detail_text(row: dict) -> str:
    return " ".join(
        str(row.get(key, "") or "")
        for key in (
            "must_have_quals",
            "preferred_quals",
            "core_responsibilities",
            "job_summary",
        )
    ).strip().lower()


def _flag_truthy(row: dict, key: str) -> bool:
    return str(row.get(key, "") or "").strip().lower() == "true"


def _matched_markers(text: str, markers: set[str]) -> tuple[str, ...]:
    return tuple(sorted(marker for marker in markers if marker in text))


def _is_vp_title(title: str) -> bool:
    """
    判断职级是否为 VP 及以上（真正的高管岗），拒绝进入 pipeline。
    规则：
    - VP/SVP/EVP/CVP 缩写（不被字母前缀，如 AVP/MVP 不触发）
    - "vice president" 完整词组，但不是 "assistant vice president"
      或 "associate vice president"（银行体系中这两者是 IC 级别）
    """
    # standalone VP abbreviations: must not be preceded by a letter (avp, mvp ok)
    if re.search(r"(?<![a-z])\b(svp|evp|cvp)\b", title):
        return True
    # "vp" alone — exclude avp (assistant/associate vp)
    if re.search(r"(?<![a-z])(?<!a)\bvp\b", title):
        return True
    # "vice president" — but NOT "assistant vice president" / "associate vice president"
    if "vice president" in title and not re.search(r"\b(assistant|associate)\b", title):
        return True
    return False


def _is_pure_sales_title(title: str) -> bool:
    """
    判断是否是纯销售岗位（区分 Salesforce SWE 与销售岗）。
    只检测"sales"作为独立功能词，不误伤含 Salesforce 的技术岗。
    """
    # "sales engineer", "sales manager", "sales rep", "sales" 作为独立词
    # 但排除 "salesforce"
    title_no_sf = re.sub(r"salesforce", " ", title)
    return bool(re.search(r"\bsales\b", title_no_sf))


def screen_job_for_pipeline(row: dict) -> JobScreenDecision:
    title = _title_text(row)
    taxonomy = _taxonomy_text(row)
    details = _detail_text(row)

    # ── 资质硬限制 ───────────────────────────────────────────────
    if _flag_truthy(row, "is_citizen_only"):
        return JobScreenDecision(
            accepted=False,
            level="hard_reject",
            reason="Job requires citizenship-only eligibility.",
            tags=("citizen_only",),
        )

    if _flag_truthy(row, "is_clearance_required"):
        return JobScreenDecision(
            accepted=False,
            level="hard_reject",
            reason="Job requires security clearance.",
            tags=("clearance_required",),
        )

    if _flag_truthy(row, "is_work_auth_required") and not _flag_truthy(row, "is_h1b_sponsor"):
        return JobScreenDecision(
            accepted=False,
            level="hard_reject",
            reason="Job requires pre-existing work authorization without sponsorship.",
            tags=("work_auth_required_without_sponsorship",),
        )

    # ── VP/C-suite 检测（精确，避免 AVP 误判）────────────────────
    if _is_vp_title(title):
        return JobScreenDecision(
            accepted=False,
            level="hard_reject",
            reason="VP-level or above leadership role is outside candidate profile.",
            tags=("vp_or_above",),
        )

    # ── 纯销售岗（区分 Salesforce 技术岗）───────────────────────
    if _is_pure_sales_title(title):
        return JobScreenDecision(
            accepted=False,
            level="hard_reject",
            reason="Title indicates a pure sales function.",
            tags=("pure_sales",),
        )

    # ── 职能类型硬拒（其他标记）──────────────────────────────────
    hard_title_matches = _matched_markers(title, HARD_REJECT_TITLE_MARKERS)
    if hard_title_matches:
        return JobScreenDecision(
            accepted=False,
            level="hard_reject",
            reason="Title indicates a non-target or structurally incompatible track.",
            tags=hard_title_matches,
        )

    # ── Taxonomy 硬拒 ────────────────────────────────────────────
    hard_taxonomy_matches = _matched_markers(taxonomy, HARD_REJECT_TAXONOMY_MARKERS)
    if hard_taxonomy_matches:
        return JobScreenDecision(
            accepted=False,
            level="hard_reject",
            reason="Taxonomy indicates a non-target commercial, legal, or HR function.",
            tags=hard_taxonomy_matches,
        )

    # ── PhD 研究岗（JD 中明写 PhD 要求）─────────────────────────
    if any(marker in title for marker in PHD_RESEARCH_TITLE_MARKERS):
        phd_signals = ("phd", "ph.d", "doctorate", "doctoral")
        if any(sig in details for sig in phd_signals):
            return JobScreenDecision(
                accepted=False,
                level="hard_reject",
                reason="Research-oriented role requires a PhD-level profile per JD.",
                tags=("phd_research_required",),
            )

    # ── 非目标 taxonomy（补充）──────────────────────────────────
    non_target_taxonomy_matches = _matched_markers(taxonomy, NON_TARGET_TAXONOMY_MARKERS)
    if non_target_taxonomy_matches:
        return JobScreenDecision(
            accepted=False,
            level="hard_reject",
            reason="Taxonomy indicates a non-target function outside engineering/data scope.",
            tags=non_target_taxonomy_matches,
        )

    # ── Soft review ──────────────────────────────────────────────
    soft_title_matches = _matched_markers(title, SOFT_REVIEW_TITLE_MARKERS)
    if soft_title_matches:
        return JobScreenDecision(
            accepted=True,
            level="soft_review",
            reason="Borderline title kept in-pool for controlled fallback handling.",
            tags=soft_title_matches,
        )

    return JobScreenDecision(
        accepted=True,
        level="accept",
        reason="Target engineering/data-adjacent role remains eligible for routing.",
    )
