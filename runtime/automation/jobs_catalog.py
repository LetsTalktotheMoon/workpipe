from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "data"
JOB_TRACKER_ROOT = DATA_ROOT / "job_tracker"
PORTFOLIO_ROOT = DATA_ROOT / "deliverables" / "resume_portfolio"

LOCAL_SCRAPED_JOBS_PATH = JOB_TRACKER_ROOT / "scraped_jobs.json"
FULL_JOBS_CATALOG_PATH = JOB_TRACKER_ROOT / "jobs_catalog.json"

_DATE_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
)
_DISCOVERED_STATUSES = {"1_discovered", "已发现", "discovered"}


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp_path.replace(path)


def _normalize_status(value: Any) -> str:
    return str(value or "").strip().casefold().replace("-", "_").replace(" ", "_")


def _status_rank(value: Any) -> int:
    normalized = _normalize_status(value)
    if not normalized:
        return 0
    if normalized in _DISCOVERED_STATUSES:
        return 1
    return 2


def _is_empty(value: Any) -> bool:
    return value is None or value == ""


def _parse_timestamp(raw: Any) -> datetime | None:
    text = str(raw or "").strip()
    if not text:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def _sort_key(row: dict[str, Any]) -> tuple[datetime, datetime, str]:
    publish_time = (
        _parse_timestamp(row.get("publish_time"))
        or _parse_timestamp(row.get("publish_date"))
        or datetime.min
    )
    discovered_time = (
        _parse_timestamp(row.get("discovered_date"))
        or _parse_timestamp(row.get("discovered_at"))
        or datetime.min
    )
    job_id = _job_id(row)
    return (publish_time, discovered_time, job_id)


def _job_id(row: dict[str, Any]) -> str:
    return str(row.get("job_id", "") or row.get("jobId", "") or "").strip()


def _apply_link(row: dict[str, Any]) -> str:
    return str(row.get("apply_link", "") or row.get("applyLink", "") or "").strip()


def _merge_row(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    merged = dict(existing)
    for key, value in incoming.items():
        if _is_empty(value):
            continue
        if key == "application_status":
            if _status_rank(existing.get(key)) > _status_rank(value):
                continue
        merged[key] = value
    return merged


def _ensure_row_copy(row: dict[str, Any]) -> dict[str, Any]:
    return {str(key): value for key, value in row.items()}


def load_local_scrape_rows(path: Path = LOCAL_SCRAPED_JOBS_PATH) -> list[dict[str, Any]]:
    payload = _load_json(path, default=[])
    if not isinstance(payload, list):
        return []
    return [_ensure_row_copy(row) for row in payload if isinstance(row, dict)]


def load_portfolio_history_rows(portfolio_root: Path = PORTFOLIO_ROOT) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row_path in sorted(portfolio_root.glob("by_company/*/*/*/sheet_row.json")):
        row = _load_json(row_path, default={})
        if isinstance(row, dict):
            rows.append(_ensure_row_copy(row))
    return rows


def load_google_sheet_rows(*, sort_by_publish_time: bool = False) -> list[dict[str, Any]]:
    from runtime.automation.google_sheets import GoogleSheetJobStore, default_sheet_config

    store = GoogleSheetJobStore(default_sheet_config())
    rows = store.fetch_jobs(sort_by_publish_time=sort_by_publish_time, sync_catalog=False)
    return [_ensure_row_copy(row) for row in rows if isinstance(row, dict)]


def _reindex_key_maps(
    rows_by_key: dict[str, dict[str, Any]],
    key_by_job_id: dict[str, str],
    key_by_apply_link: dict[str, str],
) -> None:
    key_by_job_id.clear()
    key_by_apply_link.clear()
    for key, row in rows_by_key.items():
        job_id = _job_id(row)
        apply_link = _apply_link(row)
        if job_id:
            key_by_job_id[job_id] = key
        if apply_link:
            key_by_apply_link[apply_link] = key


def merge_job_rows(*sources: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    rows_by_key: dict[str, dict[str, Any]] = {}
    key_by_job_id: dict[str, str] = {}
    key_by_apply_link: dict[str, str] = {}

    for source in sources:
        for raw_row in source:
            if not isinstance(raw_row, dict):
                continue
            row = _ensure_row_copy(raw_row)
            job_id = _job_id(row)
            apply_link = _apply_link(row)
            if not job_id and not apply_link:
                continue

            job_key = key_by_job_id.get(job_id, "") if job_id else ""
            apply_key = key_by_apply_link.get(apply_link, "") if apply_link else ""
            if job_id and not job_key and apply_key:
                apply_row = rows_by_key.get(apply_key, {})
                apply_row_job_id = _job_id(apply_row)
                # Never merge two records that both have non-empty but different job_id.
                if apply_row_job_id and apply_row_job_id != job_id:
                    apply_key = ""
            canonical_key = job_key or apply_key
            if job_key and apply_key and job_key != apply_key:
                primary_row_job_id = _job_id(rows_by_key.get(job_key, {}))
                secondary_row_job_id = _job_id(rows_by_key.get(apply_key, {}))
                if primary_row_job_id and secondary_row_job_id and primary_row_job_id != secondary_row_job_id:
                    # Keep separate buckets for different non-empty job_id.
                    canonical_key = job_key
                else:
                    # Collapse two dedupe buckets that represent the same job.
                    primary = job_key
                    secondary = apply_key
                    rows_by_key[primary] = _merge_row(rows_by_key[primary], rows_by_key[secondary])
                    del rows_by_key[secondary]
                    _reindex_key_maps(rows_by_key, key_by_job_id, key_by_apply_link)
                    canonical_key = primary
            if not canonical_key:
                canonical_key = job_id or f"apply::{apply_link}"
                rows_by_key[canonical_key] = row
            else:
                rows_by_key[canonical_key] = _merge_row(rows_by_key[canonical_key], row)

            merged_row = rows_by_key[canonical_key]
            merged_job_id = _job_id(merged_row)
            merged_apply_link = _apply_link(merged_row)
            if merged_job_id:
                key_by_job_id[merged_job_id] = canonical_key
            if merged_apply_link:
                key_by_apply_link[merged_apply_link] = canonical_key

    return sorted(rows_by_key.values(), key=_sort_key, reverse=True)


def merge_rows_into_catalog(
    rows: Iterable[dict[str, Any]],
    *,
    catalog_path: Path = FULL_JOBS_CATALOG_PATH,
) -> dict[str, Any]:
    existing_rows = load_catalog_rows(catalog_path)
    merged_rows = merge_job_rows(existing_rows, rows)
    _write_json(catalog_path, merged_rows)
    unique_job_ids = {
        _job_id(row)
        for row in merged_rows
        if _job_id(row)
    }
    return {
        "catalog_path": str(catalog_path),
        "catalog_count": len(merged_rows),
        "unique_job_ids": len(unique_job_ids),
    }


def load_catalog_rows(path: Path = FULL_JOBS_CATALOG_PATH) -> list[dict[str, Any]]:
    payload = _load_json(path, default=[])
    if not isinstance(payload, list):
        return []
    return [_ensure_row_copy(row) for row in payload if isinstance(row, dict)]


def rebuild_catalog(
    *,
    catalog_path: Path = FULL_JOBS_CATALOG_PATH,
    include_google_sheet: bool = True,
    include_existing_catalog: bool = True,
    include_local_scrape: bool = True,
    include_portfolio_history: bool = True,
) -> dict[str, Any]:
    sheet_rows: list[dict[str, Any]] = []
    if include_google_sheet:
        sheet_rows = load_google_sheet_rows()
    return rebuild_catalog_from_rows(
        sheet_rows,
        catalog_path=catalog_path,
        include_existing_catalog=include_existing_catalog,
        include_local_scrape=include_local_scrape,
        include_portfolio_history=include_portfolio_history,
    )


def rebuild_catalog_from_rows(
    sheet_rows: Iterable[dict[str, Any]],
    *,
    catalog_path: Path = FULL_JOBS_CATALOG_PATH,
    include_existing_catalog: bool = True,
    include_local_scrape: bool = True,
    include_portfolio_history: bool = True,
) -> dict[str, Any]:
    existing_rows = load_catalog_rows(catalog_path) if include_existing_catalog else []
    normalized_sheet_rows = [_ensure_row_copy(row) for row in sheet_rows if isinstance(row, dict)]
    sources: list[list[dict[str, Any]]] = [existing_rows]
    source_counts: dict[str, int] = {
        "existing_catalog": len(existing_rows),
        "google_sheet": 0,
        "local_scrape": 0,
        "portfolio_history": 0,
    }

    if include_portfolio_history:
        portfolio_rows = load_portfolio_history_rows()
        sources.append(portfolio_rows)
        source_counts["portfolio_history"] = len(portfolio_rows)
    sources.append(normalized_sheet_rows)
    source_counts["google_sheet"] = len(normalized_sheet_rows)
    if include_local_scrape:
        scrape_rows = load_local_scrape_rows()
        sources.append(scrape_rows)
        source_counts["local_scrape"] = len(scrape_rows)

    merged_rows = merge_job_rows(*sources)
    _write_json(catalog_path, merged_rows)
    source_counts["catalog_count"] = len(merged_rows)
    source_counts["unique_job_ids"] = len({_job_id(row) for row in merged_rows if _job_id(row)})
    source_counts["catalog_path"] = str(catalog_path)
    return source_counts


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rebuild full jobs catalog from sheet/local/portfolio sources.")
    parser.add_argument("--no-google-sheet", action="store_true", help="Skip Google Sheet pull.")
    parser.add_argument("--no-existing-catalog", action="store_true", help="Ignore existing catalog rows as baseline.")
    parser.add_argument("--no-local-scrape", action="store_true", help="Skip local scraper cache input.")
    parser.add_argument("--no-portfolio-history", action="store_true", help="Skip portfolio history input.")
    parser.add_argument("--catalog-path", default=str(FULL_JOBS_CATALOG_PATH), help="Output catalog path.")
    return parser


def main() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()
    summary = rebuild_catalog(
        catalog_path=Path(args.catalog_path),
        include_google_sheet=not args.no_google_sheet,
        include_existing_catalog=not args.no_existing_catalog,
        include_local_scrape=not args.no_local_scrape,
        include_portfolio_history=not args.no_portfolio_history,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
