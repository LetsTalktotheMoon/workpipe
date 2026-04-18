from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .runner import run_backfill


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Backfill job open/closed status for the local job app.")
    parser.add_argument("--concurrency", type=int, default=12)
    parser.add_argument("--limit", type=int, default=0, help="Only process the first N uncached jobs.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Recheck jobs even if cached.")
    parser.add_argument("--job-id", dest="job_ids", action="append", default=[])
    parser.add_argument("--host", dest="hosts", action="append", default=[])
    parser.add_argument(
        "--request-timeout",
        type=float,
        default=20.0,
        help="HTTP request timeout seconds. Use 0 to disable runner-side timeout override.",
    )
    parser.add_argument("--cache-path", default="", help="Optional cache file path override.")
    parser.add_argument("--job-app-state-path", default="", help="Optional job app state path override.")
    parser.add_argument("--report-path", default="", help="Optional report JSON path override.")
    parser.add_argument("--summary-path", default="", help="Optional summary JSON output path.")
    parser.add_argument("--no-report", action="store_true", help="Do not write run report file.")
    parser.add_argument(
        "--allow-unknown-overwrite-terminal",
        action="store_true",
        help="Allow unknown rerun results to overwrite cached open/closed statuses.",
    )
    parser.add_argument("--min-coverage", type=float, default=0.0, help="Exit with code 2 if coverage is below threshold.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    request_timeout: float | None = float(args.request_timeout)
    if request_timeout <= 0:
        request_timeout = None

    summary = run_backfill(
        concurrency=args.concurrency,
        limit=args.limit,
        dry_run=args.dry_run,
        force=args.force,
        job_ids={item.strip() for item in args.job_ids if str(item).strip()} or None,
        hosts={item.strip().lower() for item in args.hosts if str(item).strip()} or None,
        request_timeout=request_timeout,
        cache_path=Path(args.cache_path).expanduser().resolve() if str(args.cache_path).strip() else None,
        job_app_state_path=(
            Path(args.job_app_state_path).expanduser().resolve() if str(args.job_app_state_path).strip() else None
        ),
        report_path=Path(args.report_path).expanduser().resolve() if str(args.report_path).strip() else None,
        summary_path=Path(args.summary_path).expanduser().resolve() if str(args.summary_path).strip() else None,
        write_report=not bool(args.no_report),
        allow_unknown_overwrite_terminal=bool(args.allow_unknown_overwrite_terminal),
    )
    print(json.dumps(summary.__dict__, ensure_ascii=False, indent=2))
    if float(summary.coverage_ratio) < float(args.min_coverage):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
