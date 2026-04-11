#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_PORTFOLIO_ROOT = ROOT / "data" / "deliverables" / "resume_portfolio"
RUNTIME_ROOT = ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from automation.resume_repair import audit_resume_markdown, normalize_resume_markdown


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def process_artifact(manifest_path: Path, *, write_changes: bool) -> dict:
    manifest = load_json(manifest_path)
    resume_path = Path(str(manifest.get("resume_md", "") or "")).expanduser()
    if not resume_path.is_absolute():
        resume_path = (ROOT / resume_path).resolve()
    if not resume_path.exists():
        return {"artifact": str(manifest_path.parent), "status": "missing_resume"}

    original_text = resume_path.read_text(encoding="utf-8")
    issues_before = audit_resume_markdown(original_text)
    normalized_text, changes = normalize_resume_markdown(original_text)
    issues_after = audit_resume_markdown(normalized_text)

    modified = normalized_text != original_text
    issue_codes_before = _dedupe([issue.code for issue in issues_before])
    issue_codes_after = _dedupe([issue.code for issue in issues_after])

    if write_changes and modified:
        resume_path.write_text(normalized_text, encoding="utf-8")

    if write_changes and (modified or issue_codes_before or changes):
        repaired_at = datetime.now().isoformat(timespec="seconds")
        manifest["repaired_at"] = repaired_at
        manifest["repair_changes"] = changes
        manifest["repair_issue_codes_before"] = issue_codes_before
        manifest["repair_issue_codes_after"] = issue_codes_after
        write_json(manifest_path, manifest)

        review_path = manifest_path.parent / "review.json"
        if review_path.exists():
            review_payload = load_json(review_path)
            review_payload["repaired_at"] = repaired_at
            review_payload["repair_changes"] = changes
            review_payload["repair_issue_codes_before"] = issue_codes_before
            review_payload["repair_issue_codes_after"] = issue_codes_after
            write_json(review_path, review_payload)

    return {
        "artifact": str(manifest_path.parent),
        "modified": modified,
        "changes": changes,
        "issue_codes_before": issue_codes_before,
        "issue_codes_after": issue_codes_after,
    }


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair historical resume portfolio artifacts.")
    parser.add_argument(
        "--portfolio-root",
        default=str(DEFAULT_PORTFOLIO_ROOT),
        help="Portfolio root containing by_company/*/*/*/manifest.json",
    )
    parser.add_argument("--dry-run", action="store_true", help="Audit and normalize without writing files.")
    args = parser.parse_args()

    portfolio_root = Path(args.portfolio_root).expanduser().resolve()
    manifests = sorted((portfolio_root / "by_company").glob("*/*/*/manifest.json"))
    summary = {
        "total_manifests": len(manifests),
        "modified": 0,
        "with_issues_before": 0,
        "with_issues_after": 0,
    }
    issue_histogram: dict[str, int] = {}

    for manifest_path in manifests:
        result = process_artifact(manifest_path, write_changes=not args.dry_run)
        issue_codes_before = result.get("issue_codes_before", [])
        issue_codes_after = result.get("issue_codes_after", [])
        if result.get("modified"):
            summary["modified"] += 1
        if issue_codes_before:
            summary["with_issues_before"] += 1
        if issue_codes_after:
            summary["with_issues_after"] += 1
        for code in issue_codes_before:
            issue_histogram[code] = issue_histogram.get(code, 0) + 1

    print(json.dumps({"summary": summary, "issue_histogram_before": issue_histogram}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
