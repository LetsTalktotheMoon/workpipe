from __future__ import annotations

import argparse
import json
import os
import py_compile
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROMPT_REVIEW_DIR = ROOT / "prompt_review"
BACKUP_DIR = PROMPT_REVIEW_DIR / "backups"

_ARTIFACT_PATHS = {
    "map": PROMPT_REVIEW_DIR / "review.map.json",
    "edited": PROMPT_REVIEW_DIR / "review.edited.json",
    "baseline": PROMPT_REVIEW_DIR / "review.baseline.json",
    "regenerated": PROMPT_REVIEW_DIR / "review.regenerated.json",
    "patch_log": PROMPT_REVIEW_DIR / "patch.log.json",
    "ambiguities": PROMPT_REVIEW_DIR / "ambiguities.json",
    "conflicts": PROMPT_REVIEW_DIR / "conflicts" / "active.json",
    "roundtrip": PROMPT_REVIEW_DIR / "roundtrip.report.json",
}


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def _normalized_text(text: str) -> str:
    import re

    return re.sub(r"\s+", " ", str(text or "").strip())


def _backup(path: Path) -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{timestamp}-{path.name}"
    backup_path = BACKUP_DIR / filename
    backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return backup_path


def _get_json_pointer(data: dict[str, Any], pointer: str) -> tuple[Any, str]:
    """Resolve a dot-separated pointer like 'blocks.writer_system'."""
    parts = pointer.split(".")
    current = data
    for part in parts[:-1]:
        current = current.setdefault(part, {})
    return current, parts[-1]


def _patch_json_override(object_path: str, new_text: str) -> tuple[bool, str]:
    path = ROOT / "match_pipe" / "prompt_overrides.json"
    if not path.exists():
        return False, f"override file not found: {path}"

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON in {path}: {exc}"

    parent, key = _get_json_pointer(data, object_path)
    old_value = parent.get(key)
    parent[key] = new_text

    try:
        serialized = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    except (TypeError, ValueError) as exc:
        return False, f"JSON serialization failed: {exc}"

    _backup(path)
    path.write_text(serialized, encoding="utf-8")
    return True, f"patched {object_path} in {path} (old length {len(str(old_value))}, new length {len(new_text)})"


def _patch_python_constant(path: Path, object_path: str, new_text: str) -> tuple[bool, str]:
    if not path.exists():
        return False, f"file not found: {path}"

    content = path.read_text(encoding="utf-8")

    match = re.search(
        rf"^({re.escape(object_path)}\s*=\s*)('''|\"\"\")",
        content,
        re.MULTILINE,
    )
    if not match:
        return False, f"cannot find clean triple-quoted assignment for {object_path}"

    quote = match.group(2)
    start_idx = match.start(2)

    end_idx = content.find(quote, start_idx + 3)
    if end_idx == -1:
        return False, f"cannot find closing {quote} for {object_path}"

    if quote == '"""' and '"""' in new_text:
        if "'''" in new_text:
            return False, "new text contains both triple quotes"
        quote = "'''"
    elif quote == "'''" and "'''" in new_text:
        if '"""' in new_text:
            return False, "new text contains both triple quotes"
        quote = '"""'

    new_content = content[:start_idx] + quote + new_text + quote + content[end_idx + 3 :]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(new_content)
        tmp_path = f.name
    try:
        py_compile.compile(tmp_path, doraise=True)
    except py_compile.PyCompileError as exc:
        return False, f"patch would produce invalid python: {exc}"
    finally:
        os.unlink(tmp_path)

    _backup(path)
    path.write_text(new_content, encoding="utf-8")
    return True, f"patched {object_path} in {path}"


def _patch_markdown_document(path: Path, new_text: str) -> tuple[bool, str]:
    if not path.exists():
        return False, f"file not found: {path}"
    _backup(path)
    path.write_text(new_text, encoding="utf-8")
    return True, f"patched {path}"


def _resolve_patch_target(block: dict[str, Any]) -> dict[str, Any] | None:
    """Pick the best patchable source_ref for a block."""
    for ref in block.get("source_refs", []):
        if isinstance(ref, dict) and ref.get("source_type") == "json_override":
            return ref
    primary = block.get("primary_source")
    if isinstance(primary, dict) and primary.get("path"):
        return primary
    return None


def _should_block_writeback(block: dict[str, Any], *, force_docs: bool = False) -> tuple[bool, str]:
    policy = str(block.get("write_policy", "") or "").strip().lower()
    propagation = str(block.get("propagation_rule", "") or "").strip().lower()
    confidence = float(block.get("confidence", 1.0) or 1.0)

    target = _resolve_patch_target(block)
    if not target:
        return True, "no patchable source_ref"

    source_type = str(target.get("source_type", "") or "").strip().lower()

    if policy == "ambiguous" or propagation == "manual_review_before_writeback":
        return True, f"blocked by policy: {policy} + {propagation}"

    if source_type == "json_override":
        return False, ""

    if source_type == "python_constant":
        if confidence < 0.9:
            return True, f"blocked: python_constant with confidence {confidence} < 0.9"
        return False, ""

    if source_type == "markdown_document":
        if not force_docs:
            return True, "blocked: markdown_document requires --force-docs"
        return False, ""

    return True, f"blocked: unsupported source_type {source_type}"


def run_writeback(*, dry_run: bool = False, force_docs: bool = False) -> dict[str, Any]:
    baseline_data = _load_json(_ARTIFACT_PATHS["baseline"], {})
    edited_data = _load_json(_ARTIFACT_PATHS["edited"], {})

    baseline_blocks: dict[tuple[str, str], str] = {}
    for group in baseline_data.get("groups", []) or []:
        gid = str(group.get("group_id", "") or "")
        for block in group.get("blocks", []) or []:
            bid = str(block.get("block_id", "") or "")
            baseline_blocks[(gid, bid)] = _normalized_text(str(block.get("normalized_text", block.get("text", ""))))

    patched: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for group in edited_data.get("groups", []) or []:
        group_id = str(group.get("group_id", "") or "")
        for block in group.get("blocks", []) or []:
            block_id = str(block.get("block_id", "") or "")
            edited_norm = _normalized_text(str(block.get("normalized_text", block.get("text", ""))))
            baseline_norm = baseline_blocks.get((group_id, block_id), "")

            has_changes = edited_norm != baseline_norm and baseline_norm != ""
            if not has_changes:
                skipped.append({"group_id": group_id, "block_id": block_id, "reason": "no changes"})
                continue

            is_blocked, reason = _should_block_writeback(block, force_docs=force_docs)
            entry = {
                "group_id": group_id,
                "block_id": block_id,
                "policy": str(block.get("write_policy", "") or "").strip().lower(),
                "propagation_rule": str(block.get("propagation_rule", "") or "").strip().lower(),
                "reason": reason if is_blocked else "",
                "source_type": _resolve_patch_target(block).get("source_type", "unknown") if _resolve_patch_target(block) else "unknown",
            }

            if is_blocked:
                blocked.append(entry)
                continue

            if dry_run:
                patched.append({**entry, "reason": "planned writeback (dry-run)"})
                continue

            target = _resolve_patch_target(block)
            assert target is not None
            source_type = str(target.get("source_type", "") or "").strip().lower()
            source_path = ROOT / str(target.get("path", ""))
            object_path = str(target.get("object_path", "") or "")
            new_text = str(block.get("text", "") or "")

            try:
                if source_type == "json_override":
                    ok, msg = _patch_json_override(object_path, new_text)
                elif source_type == "python_constant":
                    ok, msg = _patch_python_constant(source_path, object_path, new_text)
                elif source_type == "markdown_document":
                    ok, msg = _patch_markdown_document(source_path, new_text)
                else:
                    ok, msg = False, f"unsupported source_type: {source_type}"
            except Exception as exc:  # noqa: BLE001
                ok, msg = False, f"exception during patch: {exc}"

            if ok:
                patched.append({**entry, "reason": msg})
            else:
                errors.append({**entry, "reason": msg})

    report = {
        "ok": len(errors) == 0,
        "dry_run": dry_run,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "patched_count": len(patched),
        "blocked_count": len(blocked),
        "skipped_count": len(skipped),
        "error_count": len(errors),
        "patched": patched,
        "blocked": blocked,
        "skipped": skipped,
        "errors": errors,
    }
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prompt review source-level writeback CLI")
    parser.add_argument("--dry-run", action="store_true", help="Analyze without modifying source files")
    parser.add_argument("--force-docs", action="store_true", help="Allow markdown_document patches")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = run_writeback(dry_run=args.dry_run, force_docs=args.force_docs)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
