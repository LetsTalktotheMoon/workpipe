from __future__ import annotations

import difflib
from typing import Any

from .prompt_review_common import (
    BASELINE_PATH,
    EDITED_PATH,
    REGENERATED_PATH,
    ROUNDTRIP_PATH,
    empty_roundtrip_report,
    normalized_text,
    now_iso,
    read_json,
    write_json,
)
from .prompt_review_store import _write_conflict_state, ensure_prompt_review_state


def _group_lookup(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(group.get("group_id", "")): group
        for group in payload.get("groups", [])
        if str(group.get("group_id", ""))
    }


def run_prompt_review_roundtrip(*, freeze_threshold: float = 0.25) -> dict[str, Any]:
    ensure_prompt_review_state()
    edited = read_json(EDITED_PATH, {})
    regenerated = read_json(REGENERATED_PATH, {})
    baseline = read_json(BASELINE_PATH, {})
    if not edited:
        report = empty_roundtrip_report()
        report["status"] = "missing_edited"
        write_json(ROUNDTRIP_PATH, report)
        return report
    if not regenerated:
        report = empty_roundtrip_report()
        report["status"] = "missing_regenerated"
        write_json(ROUNDTRIP_PATH, report)
        return report

    edited_groups = _group_lookup(edited)
    regenerated_groups = _group_lookup(regenerated)
    baseline_groups = _group_lookup(baseline)
    comparisons: list[dict[str, Any]] = []
    landed = 0
    not_landed = 0
    overwritten = 0
    semantic_like = 0
    manual_review = 0

    for group_id, edited_group in edited_groups.items():
        regenerated_group = regenerated_groups.get(group_id)
        baseline_group = baseline_groups.get(group_id, {})
        edited_text = str(edited_group.get("display_text", ""))
        baseline_text = str(baseline_group.get("display_text", ""))
        if regenerated_group is None:
            status = "needs_human_review"
            reason = "missing_in_regenerated"
            similarity = 0.0
            regenerated_text = ""
            manual_review += 1
        else:
            regenerated_text = str(regenerated_group.get("display_text", ""))
            if edited_text == regenerated_text:
                status = "landed"
                reason = "exact_match"
                similarity = 1.0
                landed += 1
            elif normalized_text(edited_text) == normalized_text(regenerated_text):
                status = "semantic_like"
                reason = "normalized_match"
                similarity = 0.99
                semantic_like += 1
            else:
                similarity = difflib.SequenceMatcher(None, normalized_text(edited_text), normalized_text(regenerated_text)).ratio()
                if baseline_text == regenerated_text and edited_text != baseline_text:
                    status = "not_landed"
                    reason = "regenerated_matches_baseline"
                    not_landed += 1
                    overwritten += 1
                elif similarity >= 0.75:
                    status = "semantic_like"
                    reason = "high_similarity"
                    semantic_like += 1
                else:
                    status = "needs_human_review"
                    reason = "low_similarity"
                    manual_review += 1
        comparisons.append(
            {
                "group_id": group_id,
                "group_label": edited_group.get("group_label", ""),
                "status": status,
                "reason": reason,
                "similarity": round(similarity, 3),
                "edited_text": edited_text,
                "regenerated_text": regenerated_text,
                "baseline_text": baseline_text,
            }
        )

    total = len(edited_groups)
    changed_ratio = 0.0 if total == 0 else (not_landed + manual_review) / total
    report = {
        "schema_version": 1,
        "scope": "project_prompt_review",
        "generated_at": now_iso(),
        "status": "ok" if changed_ratio <= freeze_threshold else "frozen",
        "summary": {
            "group_count": total,
            "landed_count": landed,
            "not_landed_count": not_landed,
            "overwritten_count": overwritten,
            "semantic_like_count": semantic_like,
            "manual_review_count": manual_review,
            "diff_ratio": round(changed_ratio, 3),
            "freeze_threshold": freeze_threshold,
        },
        "groups": comparisons,
    }
    write_json(ROUNDTRIP_PATH, report)
    if changed_ratio > freeze_threshold:
        _write_conflict_state(
            frozen=True,
            reason="roundtrip_delta_exceeds_threshold",
            affected_groups=[item["group_id"] for item in comparisons if item["status"] in {"not_landed", "needs_human_review"}],
            details=[
                {
                    "diff_ratio": round(changed_ratio, 3),
                    "freeze_threshold": freeze_threshold,
                    "overwritten_count": overwritten,
                    "manual_review_count": manual_review,
                }
            ],
            trigger_revision_id=str(edited.get("head_revision_id", "") or ""),
            next_action="inspect_roundtrip_report_and_ambiguities",
        )
    else:
        _write_conflict_state(frozen=False)
    return report
