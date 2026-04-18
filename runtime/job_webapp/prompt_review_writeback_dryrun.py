from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[2]
PROMPT_REVIEW_DIR = ROOT / "prompt_review"
REPORT_PATH = PROMPT_REVIEW_DIR / "writeback.dryrun.report.json"

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


def _should_block(block: dict[str, Any], group_id: str) -> tuple[bool, str]:
    from runtime.job_webapp.prompt_review_writeback import _should_block_writeback

    return _should_block_writeback(block)


def run_writeback_dryrun(*, output_path: Path | None = None, write_report: bool = True) -> dict[str, Any]:
    map_data = _load_json(_ARTIFACT_PATHS["map"], {})
    edited_data = _load_json(_ARTIFACT_PATHS["edited"], {})
    baseline_data = _load_json(_ARTIFACT_PATHS["baseline"], {})
    regenerated_data = _load_json(_ARTIFACT_PATHS["regenerated"], {})
    patch_log = _load_json(_ARTIFACT_PATHS["patch_log"], {})
    ambiguities = _load_json(_ARTIFACT_PATHS["ambiguities"], {})
    conflicts = _load_json(_ARTIFACT_PATHS["conflicts"], {})
    roundtrip = _load_json(_ARTIFACT_PATHS["roundtrip"], {})

    # Build baseline normalized text lookup
    baseline_blocks: dict[tuple[str, str], str] = {}
    for group in baseline_data.get("groups", []) or []:
        gid = str(group.get("group_id", "") or "")
        for block in group.get("blocks", []) or []:
            bid = str(block.get("block_id", "") or "")
            baseline_blocks[(gid, bid)] = _normalized_text(str(block.get("normalized_text", block.get("text", ""))))

    planned_writes: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    requires_human_review: list[dict[str, Any]] = []

    # Iterate map groups/blocks as the canonical structure
    for group in map_data.get("groups", []) or []:
        group_id = str(group.get("group_id", "") or "")
        for block in group.get("blocks", []) or []:
            block_id = str(block.get("block_id", "") or "")
            source_refs = block.get("source_refs", [])
            primary_source = block.get("primary_source", {})
            policy = str(block.get("write_policy", "") or "").strip().lower()
            propagation = str(block.get("propagation_rule", "") or "").strip().lower()

            is_blocked, reason = _should_block(block, group_id)
            entry: dict[str, Any] = {
                "group_id": group_id,
                "block_id": block_id,
                "policy": policy,
                "propagation_rule": propagation,
                "reason": reason if is_blocked else "",
                "source_refs": source_refs,
                "primary_source": primary_source,
            }

            # Determine if there are effective edits by comparing to baseline
            baseline_norm = baseline_blocks.get((group_id, block_id), "")
            # Find corresponding edited block text
            edited_norm = ""
            for eg in edited_data.get("groups", []) or []:
                if str(eg.get("group_id", "") or "") == group_id:
                    for eb in eg.get("blocks", []) or []:
                        if str(eb.get("block_id", "") or "") == block_id:
                            edited_norm = _normalized_text(str(eb.get("normalized_text", eb.get("text", ""))))
                            break
                    break

            has_changes = edited_norm != baseline_norm and baseline_norm != ""

            if is_blocked:
                blocked.append({**entry, "has_changes": has_changes})
                continue

            if propagation == "manual_review_before_writeback":
                requires_human_review.append({
                    **entry,
                    "reason": "requires manual review before writeback",
                    "has_changes": has_changes,
                })
                continue

            if has_changes:
                planned_writes.append({
                    **entry,
                    "reason": "planned writeback: normalized text differs from baseline",
                })
            else:
                # No changes, no write needed
                pass

    ok = True

    summary = {
        "total_blocks": sum(len(list(g.get("blocks", []) or [])) for g in map_data.get("groups", []) or []),
        "planned_count": len(planned_writes),
        "blocked_count": len(blocked),
        "requires_human_review_count": len(requires_human_review),
        "ok": ok,
    }

    report = {
        "ok": ok,
        "dry_run": True,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "planned_writes": planned_writes,
        "blocked": blocked,
        "requires_human_review": requires_human_review,
        "summary": summary,
        "artifacts": {k: str(v) for k, v in _ARTIFACT_PATHS.items()},
    }

    target = output_path or REPORT_PATH
    if write_report:
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".tmp")
        tmp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(target)

    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prompt review writeback dry-run CLI")
    parser.add_argument("--output-path", default="", help="Override report output path")
    parser.add_argument("--no-report", action="store_true", help="Do not write report file")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    output_path: Path | None = None
    if str(args.output_path).strip():
        output_path = Path(str(args.output_path)).expanduser().resolve()
    report = run_writeback_dryrun(
        output_path=output_path,
        write_report=not bool(args.no_report),
    )
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
