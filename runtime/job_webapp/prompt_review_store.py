from __future__ import annotations

import copy
import difflib
from pathlib import Path
from typing import Any

from .prompt_review_common import (
    ACTIVE_CONFLICT_PATH,
    AMBIGUITIES_PATH,
    BASELINE_PATH,
    COVERAGE_PATH,
    EDITED_PATH,
    MAP_PATH,
    PATCH_LOG_PATH,
    REVISIONS_DIR,
    REVISIONS_INDEX_PATH,
    ROUNDTRIP_PATH,
    SCHEMA_VERSION,
    SCOPE,
    build_patch_id,
    build_revision_id,
    empty_ambiguities,
    empty_conflict_state,
    empty_patch_log,
    empty_roundtrip_report,
    ensure_prompt_review_dirs,
    html_to_text,
    normalized_text,
    now_iso,
    read_json,
    write_json,
)
from .prompt_review_compiler import (
    compile_prompt_review_snapshot,
    ensure_prompt_review_baseline,
    prompt_review_file_manifest,
)


_LEGACY_ARTIFACT_TYPES = {
    "baseline",
    "edited",
    "revision_snapshot",
    "patch_log",
    "revisions_index",
    "ambiguities",
}
_SEED_ONLY_TRIGGERS = {
    "",
    "seed_from_baseline",
    "repair_missing_index",
    "seed_snapshot",
    "canonical_reseed_from_legacy",
}
_SEED_ONLY_KINDS = {
    "",
    "seed_snapshot",
    "full_immutable_snapshot",
    "canonical_seed_snapshot",
}


def _default_revisions_index() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "head_revision_id": "",
        "revisions": [],
    }


def _load_revisions_index() -> dict[str, Any]:
    return read_json(REVISIONS_INDEX_PATH, _default_revisions_index())


def _save_revisions_index(payload: dict[str, Any]) -> None:
    write_json(REVISIONS_INDEX_PATH, payload)


def _current_conflict() -> dict[str, Any]:
    return read_json(ACTIVE_CONFLICT_PATH, empty_conflict_state())


def _write_conflict_state(
    *,
    frozen: bool,
    reason: str = "",
    affected_groups: list[str] | None = None,
    details: list[dict[str, Any]] | None = None,
    trigger_revision_id: str = "",
    next_action: str = "",
) -> dict[str, Any]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "frozen": frozen,
        "trigger_revision_id": trigger_revision_id,
        "reason": reason,
        "affected_groups": affected_groups or [],
        "details": details or [],
        "next_action": next_action,
        "updated_at": now_iso(),
    }
    write_json(ACTIVE_CONFLICT_PATH, payload)
    if frozen:
        history_path = ACTIVE_CONFLICT_PATH.parent / "history" / f"conflict-{now_iso().replace(':', '').replace('+', '_')}.json"
        write_json(history_path, payload)
    return payload


def _load_patch_log() -> dict[str, Any]:
    return read_json(PATCH_LOG_PATH, empty_patch_log())


def _save_patch_log(payload: dict[str, Any]) -> None:
    write_json(PATCH_LOG_PATH, payload)


def _load_edited() -> dict[str, Any]:
    return read_json(EDITED_PATH, {})


def _save_edited(payload: dict[str, Any]) -> None:
    write_json(EDITED_PATH, payload)


def _is_legacy_seed_artifact(payload: dict[str, Any]) -> bool:
    if not payload:
        return False
    artifact_type = str(payload.get("artifact_type", "") or "").strip()
    if artifact_type in _LEGACY_ARTIFACT_TYPES:
        return True
    if payload.get("scope") != SCOPE and "scope" not in payload:
        return True
    if "build_kind" not in payload and "artifact_type" in payload:
        return True
    groups = payload.get("groups", [])
    if isinstance(groups, list) and groups:
        if all(isinstance(group, dict) and not group.get("blocks") for group in groups):
            return True
    return False


def _has_real_user_edits(patch_log: dict[str, Any], revisions_index: dict[str, Any]) -> bool:
    if any(isinstance(item, dict) for item in patch_log.get("patches", []) if item):
        return True
    for item in revisions_index.get("revisions", []) or []:
        if not isinstance(item, dict):
            continue
        patch_ids = item.get("patch_ids")
        if isinstance(patch_ids, list) and patch_ids:
            return True
        trigger = str(item.get("trigger", "") or item.get("kind", "") or "").strip()
        if trigger and trigger not in _SEED_ONLY_TRIGGERS and trigger not in _SEED_ONLY_KINDS:
            return True
    return False


def _group_signature(payload: dict[str, Any]) -> list[tuple[str, tuple[str, ...]]]:
    signature: list[tuple[str, tuple[str, ...]]] = []
    for group in payload.get("groups", []) or []:
        if not isinstance(group, dict):
            continue
        group_id = str(group.get("group_id", "") or "")
        block_ids = tuple(str(block.get("block_id", "") or "") for block in group.get("blocks", []) or [] if isinstance(block, dict))
        signature.append((group_id, block_ids))
    return signature


def _is_out_of_sync_with_current_compiler(payload: dict[str, Any]) -> bool:
    if not payload:
        return True
    current_snapshot, _, _, _ = compile_prompt_review_snapshot(regenerated=False)
    return _group_signature(payload) != _group_signature(current_snapshot)


def _canonicalize_baseline_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    baseline = copy.deepcopy(snapshot)
    baseline["build_kind"] = "baseline"
    baseline["locked"] = True
    baseline["baseline_locked"] = True
    baseline["status"] = "baseline"
    return baseline


def _canonicalize_edited_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    edited = copy.deepcopy(snapshot)
    edited["build_kind"] = "edited"
    edited["status"] = "clean"
    edited["head_revision_id"] = ""
    edited["updated_at"] = now_iso()
    return edited


def _seed_revision_entry(*, revision_id: str, snapshot_path: Path, group_count: int, block_count: int) -> dict[str, Any]:
    return {
        "revision_id": revision_id,
        "timestamp": now_iso(),
        "parent_revision_id": "",
        "edited_path": str(snapshot_path),
        "patch_ids": [],
        "trigger": "canonical_reseed_from_legacy",
        "group_count": group_count,
        "block_count": block_count,
    }


def _stable_baseline_meta(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": str(BASELINE_PATH),
        "build_kind": str(payload.get("build_kind", "baseline") or "baseline"),
        "group_count": len(payload.get("groups", [])),
        "created_at": payload.get("created_at") or payload.get("generated_at", ""),
        "revision_id": payload.get("revision_id", ""),
        "locked": bool(payload.get("locked", True)),
    }


def _stable_revisions_payload(index: dict[str, Any]) -> dict[str, Any]:
    revisions: list[dict[str, Any]] = []
    for item in index.get("revisions", []) or []:
        if not isinstance(item, dict):
            continue
        revisions.append(
            {
                "revision_id": str(item.get("revision_id", "") or ""),
                "timestamp": str(item.get("timestamp", "") or ""),
                "parent_revision_id": str(item.get("parent_revision_id", "") or ""),
                "edited_path": str(item.get("edited_path", "") or item.get("path", "") or ""),
                "patch_ids": list(item.get("patch_ids", []) or []),
                "trigger": str(item.get("trigger", "") or item.get("kind", "") or ""),
                "group_count": int(item.get("group_count", 0) or 0),
                "block_count": int(item.get("block_count", 0) or 0),
            }
        )
    return {
        "head_revision_id": str(index.get("head_revision_id", "") or ""),
        "revision_count": len(revisions),
        "revisions": revisions,
    }


def _stable_conflict_payload(conflict: dict[str, Any]) -> dict[str, Any]:
    return {
        "frozen": bool(conflict.get("frozen", False)),
        "trigger_revision_id": str(conflict.get("trigger_revision_id", "") or ""),
        "reason": str(conflict.get("reason", "") or ""),
        "affected_groups": list(conflict.get("affected_groups", []) or []),
        "details": list(conflict.get("details", []) or []),
        "next_action": str(conflict.get("next_action", "") or ""),
        "updated_at": str(conflict.get("updated_at", "") or ""),
    }


def _stable_coverage_payload(coverage: dict[str, Any]) -> dict[str, Any]:
    uncovered = list(coverage.get("uncovered", []) or [])
    return {
        "coverage_ratio": float(coverage.get("coverage_ratio", 0.0) or 0.0),
        "group_count": int(coverage.get("group_count", coverage.get("covered_group_count", 0)) or 0),
        "block_count": int(coverage.get("block_count", coverage.get("covered_block_count", 0)) or 0),
        "source_item_count": int(coverage.get("source_item_count", 0) or 0),
        "covered_source_item_count": int(coverage.get("covered_source_item_count", 0) or 0),
        "uncovered_count": len(uncovered),
        "uncovered": uncovered,
        "low_confidence": list(coverage.get("low_confidence", coverage.get("low_confidence_groups", [])) or []),
        "duplicate_clusters": list(coverage.get("duplicate_clusters", coverage.get("duplicate_groups", [])) or []),
        "mirrors": list(coverage.get("mirrors", coverage.get("mirror_groups", [])) or []),
        "raw": coverage,
    }


def _stable_ambiguities_payload(ambiguities: dict[str, Any]) -> dict[str, Any]:
    items = list(ambiguities.get("items", []) or [])
    return {
        "ambiguity_count": len(items),
        "items": items,
        "raw": ambiguities,
    }


def _stable_roundtrip_payload(roundtrip: dict[str, Any]) -> dict[str, Any]:
    groups = list(roundtrip.get("groups", []) or [])
    summary = dict(roundtrip.get("summary", {}) or {})
    return {
        "status": str(roundtrip.get("status", "") or ""),
        "generated_at": str(roundtrip.get("generated_at", "") or ""),
        "group_count": int(summary.get("group_count", len(groups)) or len(groups)),
        "summary": summary,
        "groups": groups,
        "raw": roundtrip,
    }


def _normalize_review_payload(payload: dict[str, Any], *, artifact_type: str) -> dict[str, Any]:
    if not payload:
        return {}
    normalized = copy.deepcopy(payload)
    review_map = read_json(MAP_PATH, {})
    map_groups = {
        str(group.get("group_id", "")): group
        for group in review_map.get("groups", [])
        if str(group.get("group_id", ""))
    }
    head_revision = (
        normalized.get("head_revision_id")
        or normalized.get("current_head_revision_id")
        or normalized.get("revision_id")
        or _load_revisions_index().get("head_revision_id", "")
    )
    normalized["schema_version"] = normalized.get("schema_version", SCHEMA_VERSION)
    normalized["scope"] = normalized.get("scope", SCOPE)
    normalized["build_kind"] = normalized.get("build_kind", artifact_type)
    normalized["created_at"] = normalized.get("created_at", normalized.get("generated_at", now_iso()))
    normalized["updated_at"] = normalized.get("updated_at", normalized.get("generated_at", now_iso()))
    normalized["head_revision_id"] = head_revision

    groups = list(normalized.get("groups", []))
    repaired_groups: list[dict[str, Any]] = []
    changed = False
    for group in groups:
        merged_group = copy.deepcopy(group)
        map_group = map_groups.get(str(group.get("group_id", "")), {})
        if not merged_group.get("blocks") and map_group.get("blocks"):
            merged_group["blocks"] = copy.deepcopy(map_group["blocks"])
            changed = True
        if "editable_rich_text" not in merged_group and map_group.get("editable_rich_text"):
            merged_group["editable_rich_text"] = map_group["editable_rich_text"]
            changed = True
        if "display_text" not in merged_group and map_group.get("display_text"):
            merged_group["display_text"] = map_group["display_text"]
            changed = True
        if "status" not in merged_group:
            merged_group["status"] = "clean"
            changed = True
        repaired_groups.append(merged_group)
    normalized["groups"] = repaired_groups
    normalized["_normalized_from_legacy"] = changed or _is_legacy_seed_artifact(payload)
    return normalized


def _revision_snapshot_path(revision_id: str) -> Path:
    return REVISIONS_DIR / f"{revision_id}.json"


def _append_revision_snapshot(edited_payload: dict[str, Any], *, trigger: str, patch_ids: list[str], parent_revision_id: str = "") -> str:
    index = _load_revisions_index()
    revision_sequence = len(index.get("revisions", [])) + 1
    revision_id = build_revision_id(revision_sequence)
    snapshot_payload = copy.deepcopy(edited_payload)
    snapshot_payload["snapshot_revision_id"] = revision_id
    snapshot_payload["snapshot_created_at"] = now_iso()
    snapshot_path = _revision_snapshot_path(revision_id)
    write_json(snapshot_path, snapshot_payload)
    revisions = list(index.get("revisions", []))
    revisions.append(
        {
            "revision_id": revision_id,
            "timestamp": now_iso(),
            "parent_revision_id": parent_revision_id,
            "edited_path": str(snapshot_path),
            "patch_ids": patch_ids,
            "trigger": trigger,
        }
    )
    index["head_revision_id"] = revision_id
    index["revisions"] = revisions
    _save_revisions_index(index)
    return revision_id


def _seed_edited_from_baseline() -> dict[str, Any]:
    baseline = ensure_prompt_review_baseline()
    edited = copy.deepcopy(baseline)
    edited["build_kind"] = "edited"
    edited["created_at"] = baseline.get("created_at", now_iso())
    edited["updated_at"] = now_iso()
    edited["head_revision_id"] = ""
    edited["status"] = "clean"
    _save_edited(edited)
    if not PATCH_LOG_PATH.exists():
        _save_patch_log(empty_patch_log())
    if not AMBIGUITIES_PATH.exists():
        write_json(AMBIGUITIES_PATH, empty_ambiguities())
    if not ROUNDTRIP_PATH.exists():
        write_json(ROUNDTRIP_PATH, empty_roundtrip_report())
    if not ACTIVE_CONFLICT_PATH.exists():
        write_json(ACTIVE_CONFLICT_PATH, empty_conflict_state())
    revision_id = _append_revision_snapshot(edited, trigger="seed_from_baseline", patch_ids=[])
    edited["head_revision_id"] = revision_id
    edited["updated_at"] = now_iso()
    _save_edited(edited)
    snapshot_path = _revision_snapshot_path(revision_id)
    if snapshot_path.exists():
        snapshot = read_json(snapshot_path, {})
        snapshot["head_revision_id"] = revision_id
        write_json(snapshot_path, snapshot)
    return edited


def _safe_canonical_reseed_from_legacy() -> dict[str, Any]:
    snapshot, review_map, coverage, ambiguities = compile_prompt_review_snapshot(regenerated=False)
    baseline = _canonicalize_baseline_payload(snapshot)
    edited = _canonicalize_edited_payload(snapshot)
    write_json(BASELINE_PATH, baseline)
    write_json(MAP_PATH, review_map)
    write_json(COVERAGE_PATH, coverage)
    write_json(AMBIGUITIES_PATH, ambiguities)
    patch_log = empty_patch_log()
    _save_patch_log(patch_log)
    write_json(ROUNDTRIP_PATH, empty_roundtrip_report())
    write_json(ACTIVE_CONFLICT_PATH, empty_conflict_state())
    revisions_index = _default_revisions_index()
    revision_id = build_revision_id(1)
    snapshot_path = _revision_snapshot_path(revision_id)
    edited["head_revision_id"] = revision_id
    edited["updated_at"] = now_iso()
    snapshot_payload = copy.deepcopy(edited)
    snapshot_payload["snapshot_revision_id"] = revision_id
    snapshot_payload["snapshot_created_at"] = now_iso()
    write_json(snapshot_path, snapshot_payload)
    revisions_index["head_revision_id"] = revision_id
    revisions_index["revisions"] = [
        _seed_revision_entry(
            revision_id=revision_id,
            snapshot_path=snapshot_path,
            group_count=len(edited.get("groups", [])),
            block_count=sum(len(group.get("blocks", [])) for group in edited.get("groups", [])),
        )
    ]
    _save_revisions_index(revisions_index)
    _save_edited(edited)
    return edited


def _should_reseed_canonical_from_legacy(
    *,
    baseline: dict[str, Any],
    edited: dict[str, Any],
    patch_log: dict[str, Any],
    revisions_index: dict[str, Any],
) -> bool:
    if _has_real_user_edits(patch_log, revisions_index):
        return False
    return (
        _is_legacy_seed_artifact(baseline)
        or _is_legacy_seed_artifact(edited)
        or _is_out_of_sync_with_current_compiler(baseline)
        or _is_out_of_sync_with_current_compiler(edited)
    )


def ensure_prompt_review_state() -> dict[str, Any]:
    ensure_prompt_review_dirs()
    baseline = read_json(BASELINE_PATH, {})
    edited = _load_edited()
    patch_log = _load_patch_log()
    revisions_index = _load_revisions_index()
    if _should_reseed_canonical_from_legacy(
        baseline=baseline,
        edited=edited,
        patch_log=patch_log,
        revisions_index=revisions_index,
    ):
        return _safe_canonical_reseed_from_legacy()
    ensure_prompt_review_baseline()
    edited = _load_edited()
    if not edited:
        edited = _seed_edited_from_baseline()
    else:
        normalized = _normalize_review_payload(edited, artifact_type="edited")
        if normalized != edited:
            _save_edited(normalized)
            edited = normalized
    if not PATCH_LOG_PATH.exists():
        _save_patch_log(empty_patch_log())
    if not REVISIONS_INDEX_PATH.exists():
        _append_revision_snapshot(edited, trigger="repair_missing_index", patch_ids=[])
    if not AMBIGUITIES_PATH.exists():
        write_json(AMBIGUITIES_PATH, empty_ambiguities())
    if not ROUNDTRIP_PATH.exists():
        write_json(ROUNDTRIP_PATH, empty_roundtrip_report())
    if not ACTIVE_CONFLICT_PATH.exists():
        write_json(ACTIVE_CONFLICT_PATH, empty_conflict_state())
    return _load_edited()


def _group_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(group.get("group_id", "")): group
        for group in payload.get("groups", [])
        if str(group.get("group_id", ""))
    }


def _next_patch_id(patch_log: dict[str, Any] | None = None) -> str:
    if patch_log is None:
        patch_log = _load_patch_log()
    return build_patch_id(len(patch_log.get("patches", [])) + 1)


def _classify_group_change(old_group: dict[str, Any], new_group: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    old_blocks = {str(block.get("block_id", "")): block for block in old_group.get("blocks", [])}
    new_blocks = {str(block.get("block_id", "")): block for block in new_group.get("blocks", [])}
    old_order = [str(block.get("block_id", "")) for block in old_group.get("blocks", [])]
    new_order = [str(block.get("block_id", "")) for block in new_group.get("blocks", [])]

    if old_order != new_order:
        entries.append(
            {
                "block_id": "",
                "action": "reorder_blocks",
                "original_text": " | ".join(old_order),
                "new_text": " | ".join(new_order),
                "decision_basis": "block_order_diff",
                "confidence": 0.99,
                "requires_human_review": False,
            }
        )

    for block_id in sorted(set(old_blocks) | set(new_blocks)):
        old_block = old_blocks.get(block_id)
        new_block = new_blocks.get(block_id)
        if old_block is None and new_block is not None:
            entries.append(
                {
                    "block_id": block_id,
                    "action": "insert_block",
                    "original_text": "",
                    "new_text": new_block.get("text", ""),
                    "decision_basis": "block_presence_diff",
                    "confidence": 0.95,
                    "requires_human_review": False,
                }
            )
            continue
        if old_block is not None and new_block is None:
            entries.append(
                {
                    "block_id": block_id,
                    "action": "delete_block",
                    "original_text": old_block.get("text", ""),
                    "new_text": "",
                    "decision_basis": "block_presence_diff",
                    "confidence": 0.95,
                    "requires_human_review": False,
                }
            )
            continue
        assert old_block is not None and new_block is not None
        old_text = str(old_block.get("text", ""))
        new_text = str(new_block.get("text", ""))
        if old_text == new_text and old_block.get("rich_text", "") == new_block.get("rich_text", ""):
            continue
        if normalized_text(old_text) == normalized_text(new_text):
            action = "format_only"
            confidence = 0.98
        else:
            old_parts = [part.strip() for part in old_text.split("\n\n") if part.strip()]
            new_parts = [part.strip() for part in new_text.split("\n\n") if part.strip()]
            if len(new_parts) > len(old_parts) and any(part in new_text for part in old_parts):
                action = "split_block"
            elif len(new_parts) < len(old_parts) and any(part in old_text for part in new_parts):
                action = "merge_blocks"
            else:
                action = "replace_block_text"
            confidence = 0.92
        entries.append(
            {
                "block_id": block_id,
                "action": action,
                "original_text": old_text,
                "new_text": new_text,
                "decision_basis": "block_text_diff",
                "confidence": confidence,
                "requires_human_review": False,
            }
        )

    if not entries and old_group.get("editable_rich_text") != new_group.get("editable_rich_text"):
        entries.append(
            {
                "block_id": "",
                "action": "format_only",
                "original_text": old_group.get("editable_rich_text", ""),
                "new_text": new_group.get("editable_rich_text", ""),
                "decision_basis": "rich_text_markup_diff",
                "confidence": 0.9,
                "requires_human_review": False,
            }
        )
    return entries


def _build_duplicate_index() -> dict[str, list[tuple[str, str]]]:
    baseline = read_json(BASELINE_PATH, {})
    index: dict[str, list[tuple[str, str]]] = {}
    for group in baseline.get("groups", []):
        gid = str(group.get("group_id", "") or "")
        for block in group.get("blocks", []):
            fp = str(block.get("duplicate_fingerprint", "") or "")
            if not fp:
                continue
            bid = str(block.get("block_id", "") or "")
            index.setdefault(fp, []).append((gid, bid))
    return index


def _extract_block_body_html(html: str, block_id: str) -> str | None:
    import re

    # Fast path for legacy prompt-review-block format (preserves raw casing inside <pre>)
    legacy_pattern = (
        rf'<section[^>]*class=["\'][^"\']*prompt-review-block[^"\']*["\'][^>]*data-block-id=["\']{re.escape(block_id)}["\'][^>]*>'
        rf'.*?<pre>(.*?)</pre>.*?</section>'
    )
    m = re.search(legacy_pattern, html, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1)

    from html.parser import HTMLParser

    class Extractor(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.in_target_section = False
            self.in_target_body = False
            self.body_depth = 0
            self.result = []
            self.section_format = ""

        def handle_starttag(self, tag, attrs):
            attrs_dict = dict(attrs)
            classes = attrs_dict.get("class", "").split()
            if tag == "section" and attrs_dict.get("data-block-id") == block_id:
                if "prompt-block" in classes:
                    self.in_target_section = True
                    self.section_format = "prompt-block"
                return
            if not self.in_target_section:
                return
            if self.section_format == "prompt-block" and tag == "div" and "prompt-block-body" in classes:
                self.in_target_body = True
                self.body_depth = 1
                return
            if self.in_target_body:
                self.body_depth += 1
                start_tag = self.get_starttag_text()
                self.result.append(start_tag if start_tag else "")

        def handle_endtag(self, tag):
            if not self.in_target_body:
                if self.in_target_section and tag == "section":
                    self.in_target_section = False
                    self.section_format = ""
                return
            if self.section_format == "prompt-block" and tag == "div" and self.body_depth == 1:
                self.in_target_body = False
                self.in_target_section = False
                self.section_format = ""
                return
            if self.in_target_body:
                self.body_depth -= 1
                self.result.append(f"</{tag}>")

        def handle_data(self, data):
            if self.in_target_body:
                self.result.append(data)

        def handle_entityref(self, name):
            if self.in_target_body:
                self.result.append(f"&{name};")

        def handle_charref(self, name):
            if self.in_target_body:
                self.result.append(f"&#{name};")

    try:
        extractor = Extractor()
        extractor.feed(html)
        return "".join(extractor.result)
    except Exception:
        return None


def _replace_block_body_html(html: str, block_id: str, new_body_html: str) -> str | None:
    from html.parser import HTMLParser

    class Replacer(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.result = []
            self.in_target_section = False
            self.in_target_body = False
            self.body_depth = 0
            self.section_format = ""

        def handle_starttag(self, tag, attrs):
            attrs_dict = dict(attrs)
            classes = attrs_dict.get("class", "").split()
            if tag == "section" and attrs_dict.get("data-block-id") == block_id:
                start_tag = self.get_starttag_text()
                self.result.append(start_tag if start_tag else "")
                if "prompt-block" in classes:
                    self.in_target_section = True
                    self.section_format = "prompt-block"
                elif "prompt-review-block" in classes:
                    self.in_target_section = True
                    self.section_format = "prompt-review-block"
                return
            if not self.in_target_section:
                start_tag = self.get_starttag_text()
                self.result.append(start_tag if start_tag else "")
                return
            if self.section_format == "prompt-block" and tag == "div" and "prompt-block-body" in classes:
                self.in_target_body = True
                self.body_depth = 1
                start_tag = self.get_starttag_text()
                self.result.append(start_tag if start_tag else '<div class="prompt-block-body">')
                self.result.append(new_body_html)
                return
            if self.section_format == "prompt-review-block" and tag == "pre":
                self.in_target_body = True
                self.result.append("<pre>")
                self.result.append(new_body_html)
                return
            if self.in_target_body:
                if self.section_format == "prompt-block":
                    self.body_depth += 1
                elif self.section_format == "prompt-review-block":
                    return
            start_tag = self.get_starttag_text()
            self.result.append(start_tag if start_tag else "")

        def handle_endtag(self, tag):
            if not self.in_target_body:
                self.result.append(f"</{tag}>")
                if self.in_target_section and tag == "section":
                    self.in_target_section = False
                    self.section_format = ""
                return
            if self.section_format == "prompt-block" and tag == "div" and self.body_depth == 1:
                self.in_target_body = False
                self.in_target_section = False
                self.section_format = ""
                self.result.append(f"</{tag}>")
                return
            if self.section_format == "prompt-review-block" and tag == "pre":
                self.in_target_body = False
                self.in_target_section = False
                self.section_format = ""
                self.result.append(f"</{tag}>")
                return
            if self.in_target_body:
                if self.section_format == "prompt-block":
                    self.body_depth -= 1
                elif self.section_format == "prompt-review-block":
                    return
            self.result.append(f"</{tag}>")

        def handle_data(self, data):
            if not self.in_target_body:
                self.result.append(data)

        def handle_entityref(self, name):
            if not self.in_target_body:
                self.result.append(f"&{name};")

        def handle_charref(self, name):
            if not self.in_target_body:
                self.result.append(f"&#{name};")

    try:
        replacer = Replacer()
        replacer.feed(html)
        return "".join(replacer.result)
    except Exception:
        return None


def get_prompt_review_payload() -> dict[str, Any]:
    edited = ensure_prompt_review_state()
    baseline = read_json(BASELINE_PATH, {})
    coverage = read_json(COVERAGE_PATH, {})
    ambiguities = read_json(AMBIGUITIES_PATH, empty_ambiguities())
    roundtrip = read_json(ROUNDTRIP_PATH, empty_roundtrip_report())
    revisions = _load_revisions_index()
    conflict = _current_conflict()
    patch_log = _load_patch_log()
    state = {
        "head_revision_id": str(edited.get("head_revision_id", "") or ""),
        "has_real_user_edits": _has_real_user_edits(patch_log, revisions),
        "is_legacy_seed_state": _is_legacy_seed_artifact(baseline) or _is_legacy_seed_artifact(edited),
        "frozen": bool(conflict.get("frozen", False)),
        "group_count": len(edited.get("groups", [])),
    }
    return {
        "ok": True,
        "scope": SCOPE,
        "state": state,
        "review": {
            "edited": edited,
            "baseline": _stable_baseline_meta(baseline),
        },
        "edited": edited,
        "baseline": _stable_baseline_meta(baseline),
        "map": read_json(MAP_PATH, {}),
        "coverage": _stable_coverage_payload(coverage),
        "conflict": _stable_conflict_payload(conflict),
        "revisions": _stable_revisions_payload(revisions),
        "ambiguities": _stable_ambiguities_payload(ambiguities),
        "roundtrip": _stable_roundtrip_payload(roundtrip),
        "files": prompt_review_file_manifest(),
    }


def save_prompt_review_edit(
    *,
    group_id: str,
    client_revision_id: str = "",
    editable_rich_text: str = "",
    display_text: str | None = None,
    blocks: list[dict[str, Any]] | None = None,
    editor_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    edited = ensure_prompt_review_state()
    head_revision_id = str(edited.get("head_revision_id", "") or "")
    if client_revision_id and head_revision_id and client_revision_id != head_revision_id:
        conflict = _write_conflict_state(
            frozen=True,
            reason="stale_client_revision",
            affected_groups=[group_id],
            details=[{"client_revision_id": client_revision_id, "head_revision_id": head_revision_id}],
            trigger_revision_id=head_revision_id,
            next_action="refresh_review_state_before_retry",
        )
        return {"ok": False, "error": "stale_client_revision", "frozen": True, "conflict": conflict}

    groups = list(edited.get("groups", []))
    group_lookup = _group_map(edited)
    old_group = copy.deepcopy(group_lookup.get(group_id))
    if old_group is None:
        conflict = _write_conflict_state(
            frozen=True,
            reason="unknown_group_id",
            affected_groups=[group_id],
            details=[{"group_id": group_id}],
            trigger_revision_id=head_revision_id,
            next_action="refresh_review_state_and_recompile_map",
        )
        return {"ok": False, "error": f"unknown group_id: {group_id}", "frozen": True, "conflict": conflict}

    new_group = copy.deepcopy(old_group)
    if blocks is not None:
        old_blocks_map = {
            str(block.get("block_id", "") or ""): copy.deepcopy(block)
            for block in old_group.get("blocks", [])
            if isinstance(block, dict)
        }
        seen_block_ids: set[str] = set()
        for item in blocks:
            block_id = str(item.get("block_id", "") or "")
            if not block_id or block_id in seen_block_ids:
                continue
            seen_block_ids.add(block_id)
            merged = copy.deepcopy(old_blocks_map.get(block_id, {"block_id": block_id}))
            if "text" in item:
                merged["text"] = str(item.get("text", ""))
                merged["normalized_text"] = normalized_text(merged["text"])
            if "rich_text" in item:
                merged["rich_text"] = str(item.get("rich_text", ""))
            old_blocks_map[block_id] = merged
        if old_blocks_map:
            # Preserve original order and append any new blocks at the end
            new_block_payloads: list[dict[str, Any]] = []
            processed: set[str] = set()
            for block in old_group.get("blocks", []) or []:
                bid = str(block.get("block_id", "") or "")
                if bid in old_blocks_map:
                    new_block_payloads.append(old_blocks_map[bid])
                    processed.add(bid)
            for bid, block in old_blocks_map.items():
                if bid not in processed:
                    new_block_payloads.append(block)
            new_group["blocks"] = new_block_payloads
    if editable_rich_text:
        new_group["editable_rich_text"] = str(editable_rich_text)
    if display_text is not None:
        new_group["display_text"] = str(display_text)
    elif editable_rich_text:
        new_group["display_text"] = html_to_text(editable_rich_text)

    if blocks is None and new_group.get("display_text"):
        text_value = str(new_group.get("display_text", ""))
        if new_group.get("blocks"):
            new_group["blocks"][0]["text"] = text_value
            new_group["blocks"][0]["normalized_text"] = normalized_text(text_value)
            for block in new_group["blocks"][1:]:
                block["text"] = ""
                block["normalized_text"] = ""

    patch_entries = _classify_group_change(old_group, new_group)
    if not patch_entries:
        return {
            "ok": True,
            "group_id": group_id,
            "head_revision_id": head_revision_id,
            "saved": False,
            "patches": [],
            "frozen": _current_conflict().get("frozen", False),
        }

    patch_log = _load_patch_log()
    patch_ids: list[str] = []
    for entry in patch_entries:
        patch_id = _next_patch_id(patch_log)
        patch_ids.append(patch_id)
        patch_log.setdefault("patches", []).append(
            {
                "patch_id": patch_id,
                "timestamp": now_iso(),
                "revision_id": "",
                "group_id": group_id,
                "block_id": entry["block_id"],
                "action": entry["action"],
                "original_text": entry["original_text"],
                "new_text": entry["new_text"],
                "related_source_refs": next(
                    (block.get("source_refs", []) for block in new_group.get("blocks", []) if block.get("block_id") == entry["block_id"]),
                    old_group.get("target_refs", []),
                ),
                "decision_basis": entry["decision_basis"],
                "confidence": entry["confidence"],
                "requires_human_review": entry["requires_human_review"],
                "editor_meta": editor_meta or {},
            }
        )

    # --- Match-pipe cascade for duplicate fingerprints ---
    propagated_group_ids: list[str] = []
    if patch_entries and group_id.startswith("match_pipe::"):
        dup_index = _build_duplicate_index()
        modified_block_fps: dict[str, str] = {}
        for entry in patch_entries:
            bid = str(entry.get("block_id", "") or "")
            if not bid:
                continue
            block = next((b for b in new_group.get("blocks", []) if str(b.get("block_id", "") or "") == bid), None)
            if block:
                fp = str(block.get("duplicate_fingerprint", "") or "")
                if fp:
                    modified_block_fps[bid] = fp

        for bid, fp in modified_block_fps.items():
            refs = dup_index.get(fp, [])
            for ref_gid, ref_bid in refs:
                if ref_gid == group_id:
                    continue
                if not ref_gid.startswith("match_pipe::"):
                    continue
                cascaded_old = group_lookup.get(ref_gid)
                if cascaded_old is None:
                    continue
                cascaded_new = copy.deepcopy(cascaded_old)

                target_block = next((b for b in new_group.get("blocks", []) if str(b.get("block_id", "") or "") == bid), None)
                if not target_block:
                    continue

                # Sync block text
                for block in cascaded_new.get("blocks", []):
                    if str(block.get("block_id", "") or "") == ref_bid:
                        block["text"] = target_block["text"]
                        block["normalized_text"] = normalized_text(block["text"])
                        if "rich_text" in target_block:
                            block["rich_text"] = target_block["rich_text"]
                        break

                # Sync editable_rich_text HTML
                new_body_html = _extract_block_body_html(new_group.get("editable_rich_text", ""), bid)
                if new_body_html is not None:
                    replaced_html = _replace_block_body_html(cascaded_new.get("editable_rich_text", ""), ref_bid, new_body_html)
                    if replaced_html is not None:
                        cascaded_new["editable_rich_text"] = replaced_html
                        cascaded_new["display_text"] = html_to_text(replaced_html)
                    else:
                        cascaded_new["display_text"] = html_to_text(cascaded_new.get("editable_rich_text", ""))

                cascaded_patches = _classify_group_change(cascaded_old, cascaded_new)
                if cascaded_patches:
                    for entry in cascaded_patches:
                        patch_id = _next_patch_id(patch_log)
                        patch_ids.append(patch_id)
                        patch_log.setdefault("patches", []).append(
                            {
                                "patch_id": patch_id,
                                "timestamp": now_iso(),
                                "revision_id": "",
                                "group_id": ref_gid,
                                "block_id": entry["block_id"],
                                "action": entry["action"],
                                "original_text": entry["original_text"],
                                "new_text": entry["new_text"],
                                "related_source_refs": next(
                                    (block.get("source_refs", []) for block in cascaded_new.get("blocks", []) if block.get("block_id") == entry["block_id"]),
                                    cascaded_old.get("target_refs", []),
                                ),
                                "decision_basis": entry["decision_basis"],
                                "confidence": entry["confidence"],
                                "requires_human_review": entry["requires_human_review"],
                                "editor_meta": editor_meta or {},
                            }
                        )
                    propagated_group_ids.append(ref_gid)
                    group_lookup[ref_gid] = cascaded_new

    # Ensure the source group itself is updated in the lookup
    group_lookup[group_id] = new_group

    updated_groups = []
    for group in groups:
        gid = group.get("group_id")
        if gid in group_lookup:
            updated_groups.append(group_lookup[gid])
        else:
            updated_groups.append(group)
    edited["groups"] = updated_groups
    edited["updated_at"] = now_iso()
    edited["status"] = "edited"

    revision_id = _append_revision_snapshot(edited, trigger="user_save", patch_ids=patch_ids, parent_revision_id=head_revision_id)
    edited["head_revision_id"] = revision_id
    _save_edited(edited)

    for patch in patch_log.get("patches", []):
        if patch["patch_id"] in patch_ids:
            patch["revision_id"] = revision_id
    _save_patch_log(patch_log)
    _write_conflict_state(frozen=False)

    return {
        "ok": True,
        "group_id": group_id,
        "head_revision_id": revision_id,
        "revision": {
            "head_revision_id": revision_id,
            "group_id": group_id,
        },
        "saved": True,
        "propagated_group_ids": propagated_group_ids,
        "patches": [patch for patch in patch_log.get("patches", []) if patch["patch_id"] in patch_ids],
        "frozen": False,
        "conflict": _stable_conflict_payload(_current_conflict()),
    }


def list_prompt_review_revisions() -> dict[str, Any]:
    ensure_prompt_review_state()
    return {"ok": True, **_stable_revisions_payload(_load_revisions_index())}


def restore_prompt_review_revision(*, revision_id: str, client_revision_id: str = "") -> dict[str, Any]:
    edited = ensure_prompt_review_state()
    head_revision_id = str(edited.get("head_revision_id", "") or "")
    if client_revision_id and head_revision_id and client_revision_id != head_revision_id:
        conflict = _write_conflict_state(
            frozen=True,
            reason="stale_client_revision",
            affected_groups=[],
            details=[{"client_revision_id": client_revision_id, "head_revision_id": head_revision_id}],
            trigger_revision_id=head_revision_id,
            next_action="refresh_review_state_before_restore",
        )
        return {"ok": False, "error": "stale_client_revision", "frozen": True, "conflict": conflict}

    snapshot_path = _revision_snapshot_path(revision_id)
    if not snapshot_path.exists():
        return {"ok": False, "error": f"unknown revision_id: {revision_id}"}

    restored = read_json(snapshot_path, {})
    if not restored:
        return {"ok": False, "error": f"failed to read revision: {revision_id}"}

    patch_log = _load_patch_log()
    patch_id = _next_patch_id()
    patch_log.setdefault("patches", []).append(
        {
            "patch_id": patch_id,
            "timestamp": now_iso(),
            "revision_id": "",
            "group_id": "",
            "block_id": "",
            "action": "restore_revision",
            "original_text": head_revision_id,
            "new_text": revision_id,
            "related_source_refs": [],
            "decision_basis": "restore_snapshot",
            "confidence": 1.0,
            "requires_human_review": False,
        }
    )
    restored["updated_at"] = now_iso()
    restored["status"] = "edited"
    new_revision_id = _append_revision_snapshot(restored, trigger="restore", patch_ids=[patch_id], parent_revision_id=head_revision_id)
    restored["head_revision_id"] = new_revision_id
    _save_edited(restored)
    for patch in patch_log.get("patches", []):
        if patch["patch_id"] == patch_id:
            patch["revision_id"] = new_revision_id
    _save_patch_log(patch_log)
    _write_conflict_state(frozen=False)
    return {
        "ok": True,
        "restored_from_revision_id": revision_id,
        "head_revision_id": new_revision_id,
        "revision": {
            "restored_from_revision_id": revision_id,
            "head_revision_id": new_revision_id,
        },
        "conflict": _stable_conflict_payload(_current_conflict()),
    }


def get_prompt_review_conflict() -> dict[str, Any]:
    ensure_prompt_review_state()
    conflict = _current_conflict()
    stable = _stable_conflict_payload(conflict)
    return {"ok": True, "frozen": stable["frozen"], "conflict": stable}


def get_prompt_review_coverage() -> dict[str, Any]:
    ensure_prompt_review_state()
    stable = _stable_coverage_payload(read_json(COVERAGE_PATH, {}))
    return {"ok": True, **{key: value for key, value in stable.items() if key != "raw"}, "coverage": stable["raw"]}


def get_prompt_review_ambiguities() -> dict[str, Any]:
    ensure_prompt_review_state()
    stable = _stable_ambiguities_payload(read_json(AMBIGUITIES_PATH, empty_ambiguities()))
    return {"ok": True, "ambiguity_count": stable["ambiguity_count"], "items": stable["items"], "ambiguities": stable["raw"]}


def get_prompt_review_roundtrip_report() -> dict[str, Any]:
    ensure_prompt_review_state()
    stable = _stable_roundtrip_payload(read_json(ROUNDTRIP_PATH, empty_roundtrip_report()))
    return {
        "ok": True,
        "status": stable["status"],
        "group_count": stable["group_count"],
        "summary": stable["summary"],
        "groups": stable["groups"],
        "roundtrip": stable["raw"],
    }
