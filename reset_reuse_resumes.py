from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
RUNTIME_ROOT = ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from automation.portfolio import rebuild_portfolio_indexes


PORTFOLIO_ROOT = ROOT / "data" / "deliverables" / "resume_portfolio"


def _clear_file(path: Path, removed: list[str]) -> None:
    if path.exists():
        path.unlink()
        removed.append(str(path))


def _reset_manifest(manifest_path: Path, *, dry_run: bool) -> dict:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if str(payload.get("route_mode", "") or "").strip() != "reuse":
        return {"changed": False, "reason": "not_reuse"}

    if str(payload.get("source_kind", "") or "").strip() == "seed_source":
        return {"changed": False, "reason": "seed_source"}

    job_dir = manifest_path.parent
    removed_files: list[str] = []
    candidate_files = [
        job_dir / "resume.md",
        job_dir / "resume.pdf",
        job_dir / "pdf" / "resume.pdf",
        job_dir / "review.json",
    ]

    original_resume_md = str(payload.get("resume_md", "") or "").strip()
    if original_resume_md:
        candidate_files.append(Path(original_resume_md))
    original_resume_pdf = str(payload.get("resume_pdf", "") or "").strip()
    if original_resume_pdf:
        candidate_files.append(Path(original_resume_pdf))

    candidate_paths: list[Path] = []
    seen: set[str] = set()
    for path in candidate_files:
        resolved = path if path.is_absolute() else (ROOT / path).resolve()
        key = str(resolved)
        if key in seen:
            continue
        seen.add(key)
        candidate_paths.append(resolved)

    new_payload = dict(payload)
    new_payload["route_mode"] = "reuse"
    new_payload["resume_md"] = ""
    new_payload["resume_pdf"] = ""
    new_payload["artifact_dir"] = ""
    new_payload["by_date_link"] = ""
    new_payload["review"] = {}
    new_payload["review_final_score"] = 0.0
    new_payload["review_verdict"] = ""
    new_payload["repaired_at"] = ""
    new_payload["repair_changes"] = []
    new_payload["repair_issue_codes_before"] = []
    new_payload["repair_issue_codes_after"] = []
    new_payload["rereview_version"] = ""
    new_payload["rereviewed_at"] = ""
    new_payload["rereview_rounds"] = 0
    new_payload["rereview_revised"] = False
    new_payload["reset_to_reuse_at"] = datetime.now().isoformat(timespec="seconds")

    if dry_run:
        return {
            "changed": True,
            "job_id": str(payload.get("job_id", "") or ""),
            "manifest_path": str(manifest_path),
            "removed_files": [str(path) for path in candidate_paths if path.exists()],
        }

    for path in candidate_paths:
        _clear_file(path, removed_files)

    manifest_path.write_text(
        json.dumps(new_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return {
        "changed": True,
        "job_id": str(payload.get("job_id", "") or ""),
        "manifest_path": str(manifest_path),
        "removed_files": removed_files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Reset copied reuse resumes back to no-resume state.")
    parser.add_argument("--portfolio-root", default=str(PORTFOLIO_ROOT))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    portfolio_root = Path(args.portfolio_root).resolve()
    manifest_paths = sorted((portfolio_root / "by_company").glob("*/*/*/manifest.json"))
    changed: list[dict] = []

    for manifest_path in manifest_paths:
        result = _reset_manifest(manifest_path, dry_run=args.dry_run)
        if not result.get("changed"):
            continue
        changed.append(result)
        if args.limit and len(changed) >= args.limit:
            break

    if not args.dry_run:
        rebuild_portfolio_indexes(portfolio_root)

    print(json.dumps(
        {
            "portfolio_root": str(portfolio_root),
            "dry_run": bool(args.dry_run),
            "changed_count": len(changed),
            "sample": changed[:10],
        },
        indent=2,
        ensure_ascii=False,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
