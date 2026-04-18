from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[2]
_RUNTIME_ROOT = _ROOT / "runtime"
if str(_RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(_RUNTIME_ROOT))

from config.candidate_framework import is_bytedance_target_company
from job_webapp.prompt_library import _immutable_block_for_company


def _base_jd_context(jd) -> dict[str, Any]:
    or_groups = "\n".join(f"- {' / '.join(group)}" for group in (jd.tech_or_groups or [])) or "（无）"
    return {
        "is_bytedance": is_bytedance_target_company(jd.company),
        "company": jd.company,
        "title": jd.title,
        "role_type": jd.role_type,
        "seniority": jd.seniority,
        "team_direction": jd.team_direction or "（未说明）",
        "tech_required": ", ".join(jd.tech_required) if jd.tech_required else "（无明确列出）",
        "tech_preferred": ", ".join(jd.tech_preferred) if jd.tech_preferred else "（无）",
        "or_groups": or_groups,
        "or_group": or_groups,
        "soft_required": "\n".join(f"- {item}" for item in (jd.soft_required or [])[:5]) or "（无）",
    }


def build_writer_context(jd, **extra) -> dict[str, Any]:
    ctx = _base_jd_context(jd)
    ctx.update(extra)
    return ctx


def build_reviewer_context(resume_md: str, jd, review_scope: str = "full", **extra) -> dict[str, Any]:
    ctx = build_writer_context(jd)
    ctx.update({
        "resume_md": resume_md,
        "review_scope": review_scope,
        "immutable_block": _immutable_block_for_company(jd.company),
    })
    ctx.update(extra)
    return ctx


def build_upgrade_context(resume_md: str, review_result: dict, tech_required: list[str] | None = None, target_company: str = "", **extra) -> dict[str, Any]:
    ctx = {
        "is_bytedance": is_bytedance_target_company(target_company),
        "resume_md": resume_md,
        "priority": "\n".join(f"{idx + 1}. {item}" for idx, item in enumerate(review_result.get("revision_priority", []) or [])) or "1. Raise the resume to a stronger pass.",
        "findings_block": "",  # legacy builder computes but does NOT interpolate into final prompt
        "tech_line": ", ".join(tech_required or []) or "（无明确 must-have 技术）",
    }
    ctx.update(extra)
    return ctx


def build_retarget_context(jd, seed_resume_md: str, top_candidate: dict | None = None, **extra) -> dict[str, Any]:
    top_candidate = top_candidate or {}
    ctx = build_writer_context(jd)
    ctx.update({
        "seed_resume_md": seed_resume_md,
        "same_company": bool(top_candidate.get("same_company")),
        "seed_label": top_candidate.get("label", ""),
        "route_mode": "retarget",
        "missing_required": ", ".join(top_candidate.get("missing_required", [])[:8]) or "（无明显缺口）",
    })
    ctx.update(extra)
    return ctx


def build_dual_channel_context(delta_summary: list[str] | None, continuity_anchor: dict[str, Any] | None) -> dict[str, Any]:
    delta_lines = [f"- {item}" for item in (delta_summary or [])]
    continuity_line = ""
    if continuity_anchor:
        continuity_line = (
            f"- Continuity anchor: {continuity_anchor.get('company_name', '')} / {continuity_anchor.get('title', '')} "
            f"(reuse_readiness={float(continuity_anchor.get('reuse_readiness', 0.0) or 0.0):.2f})."
        )
    overlay_lines = ["## Dual-channel continuity note"]
    overlay_lines.extend(delta_lines)
    if continuity_line:
        overlay_lines.append(continuity_line)
    overlay_lines.append("- Use semantic anchor as the main skeleton. Apply company continuity only when it does not reintroduce hard gaps.")
    return {
        "delta_summary": delta_lines,
        "continuity_anchor_line": continuity_line,
        "dual_channel_overlay_text": "\n".join(overlay_lines),
    }


def build_planner_context(jd, mode: str, matcher_packet: dict[str, Any] | None = None, starter_resume_md: str = "", **extra) -> dict[str, Any]:
    ctx = _base_jd_context(jd)
    ctx.update({
        "mode": mode,
        "tech_required": jd.tech_required,
        "tech_preferred": jd.tech_preferred,
        "matcher_block": json.dumps(matcher_packet or {}, indent=2, ensure_ascii=False),
        "starter_block": starter_resume_md if starter_resume_md else "（无 starter resume）",
    })
    ctx.update(extra)
    return ctx


def build_planner_writer_context(jd, planner_payload: dict[str, Any], starter_resume_md: str = "", matcher_packet: dict[str, Any] | None = None, **extra) -> dict[str, Any]:
    ctx = build_writer_context(jd)
    ctx.update({
        "planner_json": json.dumps(planner_payload, indent=2, ensure_ascii=False),
        "matcher_json": json.dumps(matcher_packet or {}, indent=2, ensure_ascii=False),
        "starter_block": starter_resume_md if starter_resume_md else "（无 starter resume）",
    })
    ctx.update(extra)
    return ctx


def build_planner_revision_context(current_resume_md: str, review, planner_payload: dict[str, Any], jd=None, **extra) -> dict[str, Any]:
    planner_notes = "\n".join(f"- {item}" for item in planner_payload.get("writer_plan", [])) or "- 无额外 writer plan"
    risk_notes = "\n".join(f"- {item}" for item in planner_payload.get("risk_flags", [])) or "- 无额外风险"
    priority = "\n".join(f"{idx + 1}. {item}" for idx, item in enumerate(review.revision_priority or [])) or "1. Raise the resume to a stronger pass."
    findings: list[str] = []
    for dim_id, dim in review.dimensions.items():
        for finding in dim.findings:
            if finding.get("severity") in {"critical", "high", "medium"}:
                findings.append(
                    f"[{dim_id}] [{str(finding.get('severity', '')).upper()}] {finding.get('field', '')}: {finding.get('issue', '')} -> {finding.get('fix', '')}"
                )
    findings_block = "\n".join(f"- {item}" for item in findings) or "- 无结构化高优先发现"
    must_have = ", ".join(jd.tech_required) if jd and jd.tech_required else "（无明确 must-have）"
    ctx = build_writer_context(jd) if jd else {}
    ctx.update({
        "weighted_score": f"{review.weighted_score:.1f}",
        "passed": "PASS" if review.passed else "FAIL",
        "needs_revision": "是" if review.needs_revision else "否",
        "planner_notes": planner_notes,
        "risk_notes": risk_notes,
        "priority": priority,
        "findings_block": findings_block,
        "must_have": must_have,
        "current_resume_md": current_resume_md,
    })
    ctx.update(extra)
    return ctx
