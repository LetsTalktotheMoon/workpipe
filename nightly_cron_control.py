#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from managed_run import (
    find_waiting_process,
    merge_process_metadata,
    merge_waiting_retry_queue,
)

ROOT = Path(__file__).resolve().parent
PIPELINE_SPEC = importlib.util.spec_from_file_location("pipeline_cli_module", ROOT / "pipeline.py")
if PIPELINE_SPEC is None or PIPELINE_SPEC.loader is None:
    raise RuntimeError("Unable to load pipeline.py")
pipeline_cli = importlib.util.module_from_spec(PIPELINE_SPEC)
PIPELINE_SPEC.loader.exec_module(pipeline_cli)

DEFAULT_JOBS_JSON = pipeline_cli.DEFAULT_JOBS_JSON
RUNS_ROOT = pipeline_cli.RUNS_ROOT
_COMPANY_SIZE_RANK = pipeline_cli._COMPANY_SIZE_RANK
_job_sort_key = pipeline_cli._job_sort_key
_matches_job_filters = pipeline_cli._matches_job_filters
_normalize_company_tiers = pipeline_cli._normalize_company_tiers
load_json = pipeline_cli.load_json
load_resume_state = pipeline_cli.load_resume_state
run_jobs_step = pipeline_cli.run_jobs_step


def _now_slug() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _job_queue_item(row: dict[str, Any]) -> dict[str, Any]:
    company_rank, min_salary, publish_time = _job_sort_key(row)
    return {
        "job_id": str(row.get("job_id", "") or "").strip(),
        "company_name": str(row.get("company_name", "") or "").strip(),
        "title": str(row.get("job_title", "") or row.get("job_nlp_title", "") or "").strip(),
        "company_size": str(row.get("company_size", "") or "").strip(),
        "company_size_rank": _COMPANY_SIZE_RANK.get(str(row.get("company_size", "") or "").strip(), company_rank),
        "min_salary": float(row.get("min_salary", 0) or 0),
        "publish_time": str(row.get("publish_time", "") or row.get("publish_date", "") or "").strip(),
        "apply_link": str(row.get("apply_link", "") or "").strip(),
        "sort_key": [company_rank, float(min_salary or 0), str(publish_time or "")],
    }


def _load_job_rows(path: Path) -> list[dict[str, Any]]:
    rows = load_json(path, default=[])
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _enqueue_for_waiting_run(*, run_id: str, preset_id: str, lookback_hours: int, company_tiers: set[str] | None) -> dict[str, Any]:
    jobs_json = Path(DEFAULT_JOBS_JSON)
    before_rows = _load_job_rows(jobs_json)
    before_ids = {
        str(row.get("job_id", "") or "").strip()
        for row in before_rows
        if str(row.get("job_id", "") or "").strip()
    }

    run_dir = RUNS_ROOT / f"nightly_scrape_{_now_slug()}"
    jobs_summary = run_jobs_step(
        run_dir=run_dir,
        jobs_json=jobs_json,
        skip_scrape=False,
        lookback_hours=lookback_hours,
        allow_existing_json=True,
    )

    after_rows = _load_job_rows(jobs_json)
    processed_ids = {
        str(item)
        for item in (load_resume_state().get("processed_ids", []) or [])
        if str(item).strip()
    }
    new_rows = []
    for row in after_rows:
        job_id = str(row.get("job_id", "") or "").strip()
        if not job_id or job_id in before_ids or job_id in processed_ids:
            continue
        if not _matches_job_filters(
            row,
            allowed_company_tiers=company_tiers,
            publish_date=None,
            publish_date_from=None,
            publish_date_to=None,
        ):
            continue
        new_rows.append(row)

    queue_items = sorted((_job_queue_item(row) for row in new_rows), key=lambda item: tuple(item["sort_key"]), reverse=True)
    queue_payload = merge_waiting_retry_queue(
        run_id,
        preset_id=preset_id,
        items=queue_items,
        source="nightly_scrape",
    )

    merge_process_metadata(
        run_id,
        {
            "waiting_queue_count": len(queue_payload.get("items", []) or []),
            "waiting_queue_updated_at": str(queue_payload.get("updated_at", "") or ""),
            "waiting_queue_preview": list(queue_payload.get("items", []) or [])[:5],
            "nightly_scrape_run_dir": str(run_dir),
            "nightly_scrape_lookback_hours": lookback_hours,
        },
        log_line=(
            f"Nightly scrape queued {len(queue_items)} new jobs at {datetime.now().isoformat(timespec='seconds')}; "
            f"queue now has {len(queue_payload.get('items', []) or [])} jobs."
        ),
    )

    return {
        "action": "scrape_and_enqueue",
        "run_id": run_id,
        "preset_id": preset_id,
        "jobs_summary": jobs_summary,
        "new_jobs_queued": len(queue_items),
        "queue_size": len(queue_payload.get("items", []) or []),
        "queue_preview": list(queue_payload.get("items", []) or [])[:5],
        "run_dir": str(run_dir),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Nightly cron helper for waiting-retry daily pipeline runs.")
    parser.add_argument("--preset-id", default="daily_full_pipeline")
    parser.add_argument("--lookback-hours", type=int, default=48)
    parser.add_argument(
        "--company-tier",
        dest="company_tiers",
        action="append",
        default=["large"],
        help="Repeatable or comma-separated company tier filter. Default is large only.",
    )
    args = parser.parse_args()

    waiting_process = find_waiting_process(args.preset_id)
    if waiting_process is None:
        print(json.dumps({"action": "run_full_pipeline", "preset_id": args.preset_id}, ensure_ascii=False))
        raise SystemExit(1)

    company_tiers = _normalize_company_tiers(args.company_tiers)
    result = _enqueue_for_waiting_run(
        run_id=str(waiting_process.get("id", "") or ""),
        preset_id=args.preset_id,
        lookback_hours=int(args.lookback_hours or 48),
        company_tiers=company_tiers,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
