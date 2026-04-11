#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
RUNTIME_ROOT = ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from automation.artifacts import compile_markdown_to_pdf
from automation.portfolio import ensure_profiles_json, rebuild_portfolio_indexes
from rereview_resume_portfolio import (
    DEFAULT_PORTFOLIO_ROOT,
    _manifest_matches_filters,
    _manifest_review_status,
    _manifest_sort_key,
    _matches_source_scope,
    _normalize_company_tiers,
    _resolve_publish_date_filters,
)

_PIPELINE_SPEC = importlib.util.spec_from_file_location("local_pipeline_cli", ROOT / "pipeline.py")
if _PIPELINE_SPEC is None or _PIPELINE_SPEC.loader is None:
    raise RuntimeError("unable to load pipeline.py")
_PIPELINE_MODULE = importlib.util.module_from_spec(_PIPELINE_SPEC)
_PIPELINE_SPEC.loader.exec_module(_PIPELINE_MODULE)
load_active_profile = _PIPELINE_MODULE.load_active_profile
update_portfolio_manifest_pdf = _PIPELINE_MODULE.update_portfolio_manifest_pdf


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resume_pdf_exists(job_dir: Path, manifest: dict[str, Any]) -> bool:
    explicit = str(manifest.get("resume_pdf", "") or "").strip()
    if explicit:
        explicit_path = Path(explicit).expanduser()
        if not explicit_path.is_absolute():
            explicit_path = (ROOT / explicit_path).resolve()
        if explicit_path.exists():
            return True
    return (job_dir / "resume.pdf").exists()


def _resolve_resume_md(job_dir: Path, manifest: dict[str, Any]) -> Path | None:
    local = job_dir / "resume.md"
    if local.exists():
        return local
    raw = str(manifest.get("resume_md", "") or "").strip()
    if not raw:
        return None
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    return path if path.exists() else None


def main() -> None:
    if os.environ.get("MANAGED_RUN_ACTIVE", "").strip() != "1" and len(sys.argv) > 1:
        os.execv(
            sys.executable,
            [
                sys.executable,
                str(ROOT / "managed_run.py"),
                "--label",
                "pdf_pass_backfill",
                "--display-name",
                "PDF Backfill Passed",
                "--cwd",
                str(ROOT),
                "--preset-id",
                "pdf_pass_backfill",
                "--",
                sys.executable,
                str(ROOT / "portfolio_pdf_backfill.py"),
                *sys.argv[1:],
            ],
        )

    parser = argparse.ArgumentParser(description="Generate PDFs for pass resumes missing resume.pdf.")
    parser.add_argument("--portfolio-root", default=str(DEFAULT_PORTFOLIO_ROOT))
    parser.add_argument("--company-tier", dest="company_tiers", action="append", default=["large"])
    parser.add_argument("--publish-date", default="")
    parser.add_argument("--publish-date-from", default="")
    parser.add_argument("--publish-date-to", default="")
    parser.add_argument("--source-scope", default="all", choices=["legacy_only", "unified_only", "all"])
    parser.add_argument("--job-id", default="")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--oldest-first", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--run-dir", default="")
    args = parser.parse_args()

    portfolio_root = Path(args.portfolio_root).expanduser().resolve()
    profiles_path = ensure_profiles_json(portfolio_root)
    profile = load_active_profile(profiles_path)
    company_tiers = _normalize_company_tiers(args.company_tiers)
    publish_date, publish_date_from, publish_date_to = _resolve_publish_date_filters(args)

    run_dir = Path(args.run_dir).expanduser().resolve() if str(args.run_dir or "").strip() else (
        ROOT / "runs" / f"pdf_pass_backfill_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    run_dir.mkdir(parents=True, exist_ok=True)

    manifests = sorted(
        (portfolio_root / "by_company").glob("*/*/*/manifest.json"),
        key=_manifest_sort_key,
        reverse=not args.oldest_first,
    )

    selected: list[Path] = []
    for path in manifests:
        try:
            manifest = load_json(path)
        except Exception:
            continue
        if not _manifest_matches_filters(
            path,
            allowed_company_tiers=company_tiers,
            publish_date=publish_date,
            publish_date_from=publish_date_from,
            publish_date_to=publish_date_to,
        ):
            continue
        if not _matches_source_scope(manifest, args.source_scope):
            continue
        if args.job_id and str(manifest.get("job_id", "") or "").strip() != str(args.job_id or "").strip():
            continue
        if _manifest_review_status(manifest).lower() != "pass":
            continue
        if _resume_pdf_exists(path.parent, manifest):
            continue
        if _resolve_resume_md(path.parent, manifest) is None:
            continue
        selected.append(path)

    if args.limit > 0:
        selected = selected[: args.limit]

    results: list[dict[str, Any]] = []
    portfolio_changed = False
    for index, manifest_path in enumerate(selected, start=1):
        manifest = load_json(manifest_path)
        job_dir = manifest_path.parent
        resume_md = _resolve_resume_md(job_dir, manifest)
        result = {
            "index": index,
            "total": len(selected),
            "job_id": str(manifest.get("job_id", "") or ""),
            "company_name": str(manifest.get("company_name", "") or ""),
            "publish_time": str(manifest.get("publish_time", "") or ""),
            "status": "",
            "resume_pdf": "",
        }
        if resume_md is None:
            result["status"] = "missing_resume_md"
            results.append(result)
            print(json.dumps(result, ensure_ascii=False))
            continue
        if args.dry_run:
            result["status"] = "dry_run"
            results.append(result)
            print(json.dumps(result, ensure_ascii=False))
            continue
        compiled_pdf = compile_markdown_to_pdf(
            resume_md,
            job_dir,
            name=profile["name"],
            phone=profile["phone"],
            email=profile["email"],
        )
        final_pdf = job_dir / "resume.pdf"
        if compiled_pdf.resolve() != final_pdf.resolve():
            final_pdf.write_bytes(compiled_pdf.read_bytes())
        update_portfolio_manifest_pdf(job_dir, final_pdf)
        portfolio_changed = True
        result["status"] = "generated"
        result["resume_pdf"] = str(final_pdf)
        results.append(result)
        print(json.dumps(result, ensure_ascii=False))

    if portfolio_changed and not args.dry_run:
        rebuild_portfolio_indexes(portfolio_root)

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total": len(selected),
        "generated": sum(1 for item in results if item["status"] == "generated"),
        "dry_run": bool(args.dry_run),
        "source_scope": args.source_scope,
        "results": results,
    }
    (run_dir / "pdf_backfill_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
