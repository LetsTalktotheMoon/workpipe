from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import requests

from .models import DetectionResult, JobAvailability, JobRecord
from .persistence import (
    BACKFILL_REPORTS_DIR,
    BACKFILL_STATE_PATH,
    STATE_PATH,
    apply_results_to_job_app_state,
    load_backfill_cache,
    merge_backfill_results,
    write_backfill_cache,
    write_backfill_report,
    write_summary,
)
from .pool import JobPoolSnapshot, load_full_job_pool


def detect_job_status(job: JobRecord, session: requests.Session | None = None) -> DetectionResult:
    from .detectors import detect_job_status as _detect_job_status

    return _detect_job_status(job, session=session)


def fetch_page(url: str, session: requests.Session | None = None, timeout: float = 20.0):
    from .detectors import fetch_page as _fetch_page

    return _fetch_page(url, session=session, timeout=timeout)


def fetch_linkedin_guest_page(job: JobRecord, session: requests.Session | None = None, timeout: float = 20.0):
    from .detectors import fetch_linkedin_guest_page as _fetch_linkedin_guest_page

    return _fetch_linkedin_guest_page(job, session=session, timeout=timeout)


def evaluate_fetched_page(job: JobRecord, page) -> DetectionResult:
    from .detectors import evaluate_fetched_page as _evaluate_fetched_page

    return _evaluate_fetched_page(job, page)


def canonical_host(host: str) -> str:
    from .rules import canonical_host as _canonical_host

    return _canonical_host(host)


@dataclass(frozen=True)
class BackfillRunSummary:
    generated_at: str
    total_jobs: int
    classified_jobs: int
    open_jobs: int
    closed_jobs: int
    unknown_jobs: int
    coverage_ratio: float
    report_path: str
    unresolved_hosts: dict[str, int]
    processed_jobs: int
    skipped_cached_jobs: int
    dry_run: bool
    request_timeout_seconds: float | None
    cache_path: str
    job_app_state_path: str
    allow_unknown_overwrite_terminal: bool
    run_scope_total_jobs: int = 0
    canonical_total_jobs: int = 0
    canonical_total_jobs_with_apply_url: int = 0


def _filter_scope_jobs(
    snapshot: JobPoolSnapshot,
    *,
    job_ids: set[str] | None,
    hosts: set[str] | None,
) -> list[JobRecord]:
    selected: list[JobRecord] = []
    for job in snapshot.jobs:
        if job_ids is not None and job.job_id not in job_ids:
            continue
        if hosts is not None and job.host not in hosts:
            continue
        selected.append(job)
    return selected


def _iter_jobs_to_process(
    jobs: list[JobRecord],
    cache: dict[str, dict[str, object]],
    *,
    force: bool,
) -> tuple[list[JobRecord], int]:
    selected: list[JobRecord] = []
    skipped_cached = 0
    for job in jobs:
        cached = cache.get(job.job_id, {})
        cached_status = str(cached.get("status", "") or "")
        if not force and cached_status in {"open", "closed"}:
            skipped_cached += 1
            continue
        selected.append(job)
    return selected, skipped_cached


def _unknown_result_from_error(job: JobRecord, exc: Exception, *, detector_name: str) -> DetectionResult:
    return DetectionResult(
        job_id=job.job_id,
        status=JobAvailability.UNKNOWN,
        detector=detector_name,
        confidence=0.0,
        reason=str(exc),
        requested_url=job.apply_url,
        final_url=job.apply_url,
        host=job.host,
        signals={"error_type": type(exc).__name__},
    )


def _detect_with_timeout(job: JobRecord, session: requests.Session, request_timeout: float | None) -> DetectionResult:
    if request_timeout is None:
        return detect_job_status(job, session=session)
    try:
        if canonical_host(job.host) == "linkedin":
            guest_page = fetch_linkedin_guest_page(job, session=session, timeout=request_timeout)
            if guest_page and guest_page.status_code < 400:
                guest_result = evaluate_fetched_page(job, guest_page)
                if guest_result.status != JobAvailability.UNKNOWN:
                    return guest_result
        page = fetch_page(job.apply_url, session=session, timeout=request_timeout)
        return evaluate_fetched_page(job, page)
    except requests.RequestException as exc:
        return _unknown_result_from_error(job, exc, detector_name="request_error")
    except Exception as exc:  # pragma: no cover - defensive fallback
        return _unknown_result_from_error(job, exc, detector_name="unexpected_error")


def _normalized_status(raw_status: str) -> str:
    status = str(raw_status or "").strip().lower()
    if status in {"open", "closed", "unknown"}:
        return status
    return "missing"


def _count_source_scopes(jobs: list[JobRecord]) -> dict[str, int]:
    counts = Counter(job.source_scope or "unspecified" for job in jobs)
    return dict(counts.most_common())


def run_backfill(
    *,
    concurrency: int = 12,
    limit: int = 0,
    dry_run: bool = False,
    force: bool = False,
    job_ids: set[str] | None = None,
    hosts: set[str] | None = None,
    request_timeout: float | None = 20.0,
    cache_path: Path | None = None,
    job_app_state_path: Path | None = None,
    report_path: Path | None = None,
    summary_path: Path | None = None,
    write_report: bool = True,
    allow_unknown_overwrite_terminal: bool = False,
) -> BackfillRunSummary:
    resolved_cache_path = cache_path or BACKFILL_STATE_PATH
    resolved_job_app_state_path = job_app_state_path or STATE_PATH

    snapshot = load_full_job_pool()
    existing_cache = load_backfill_cache(path=resolved_cache_path)
    requested_scope_jobs = _filter_scope_jobs(
        snapshot,
        job_ids=job_ids,
        hosts=hosts,
    )
    eligible_jobs, skipped_cached = _iter_jobs_to_process(
        requested_scope_jobs,
        existing_cache,
        force=force,
    )
    jobs = eligible_jobs
    if limit > 0:
        jobs = jobs[:limit]

    results: list[DetectionResult] = []
    if jobs:
        with requests.Session() as session:
            session.headers.update({"Connection": "close"})
            with ThreadPoolExecutor(max_workers=max(1, concurrency)) as executor:
                future_map = {
                    executor.submit(_detect_with_timeout, job, session, request_timeout): job
                    for job in jobs
                }
                for future in as_completed(future_map):
                    results.append(future.result())

    merged_cache = merge_backfill_results(
        existing_cache,
        results,
        allow_unknown_overwrite_terminal=allow_unknown_overwrite_terminal,
    )
    if not dry_run and results:
        write_backfill_cache(
            existing_cache,
            results,
            path=resolved_cache_path,
            allow_unknown_overwrite_terminal=allow_unknown_overwrite_terminal,
        )
    apply_results_to_job_app_state(results, dry_run=dry_run, state_path=resolved_job_app_state_path)

    all_statuses = Counter()
    unresolved_hosts: Counter[str] = Counter()
    for job in snapshot.jobs:
        cached = merged_cache.get(job.job_id, {})
        status = _normalized_status(str(cached.get("status", "") or ""))
        all_statuses[status] += 1
        if status not in {"open", "closed"}:
            unresolved_hosts[job.host] += 1

    requested_scope_total_jobs = len(requested_scope_jobs)
    eligible_scope_total_jobs = len(eligible_jobs)
    run_scope_total_jobs = len(jobs)
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "canonical_total_jobs": snapshot.total_jobs,
        "canonical_total_jobs_with_apply_url": snapshot.jobs_with_apply_url,
        "canonical_source": snapshot.canonical_source,
        "canonical_source_path": snapshot.canonical_source_path,
        "canonical_source_generated_at": snapshot.generated_at,
        "canonical_source_scope_counts": snapshot.source_scope_counts,
        "requested_scope_total_jobs": requested_scope_total_jobs,
        "requested_scope_source_scope_counts": _count_source_scopes(requested_scope_jobs),
        "eligible_scope_total_jobs": eligible_scope_total_jobs,
        "run_scope_total_jobs": run_scope_total_jobs,
        "run_scope_source_scope_counts": _count_source_scopes(jobs),
        "pool_total_jobs": snapshot.total_jobs,
        "pool_total_jobs_semantics": "Deprecated compat alias for canonical_total_jobs; use run_scope_total_jobs and canonical_total_jobs instead.",
        "jobs_with_apply_url": snapshot.jobs_with_apply_url,
        "jobs_with_apply_url_semantics": "Deprecated compat alias for canonical_total_jobs_with_apply_url.",
        "processed_this_run": len(results),
        "skipped_cached_jobs": skipped_cached,
        "dry_run": dry_run,
        "request_timeout_seconds": request_timeout,
        "allow_unknown_overwrite_terminal": allow_unknown_overwrite_terminal,
        "cache_path": str(resolved_cache_path),
        "job_app_state_path": str(resolved_job_app_state_path),
        "status_counts": dict(all_statuses),
        "coverage_ratio": (
            (all_statuses.get("open", 0) + all_statuses.get("closed", 0)) / snapshot.jobs_with_apply_url
            if snapshot.jobs_with_apply_url
            else 0.0
        ),
        "top_hosts": dict(list(snapshot.host_counts.items())[:25]),
        "unresolved_hosts": dict(unresolved_hosts.most_common(25)),
        "results": [result.to_dict() for result in results],
    }

    output_report_path = ""
    if write_report:
        target_path = report_path
        if target_path is None:
            target_path = BACKFILL_REPORTS_DIR / "latest_backfill_status.json"
        output_report_path = str(
            write_backfill_report(
                report,
                report_path=target_path,
                report_dir=BACKFILL_REPORTS_DIR,
            )
        )

    classified = all_statuses.get("open", 0) + all_statuses.get("closed", 0)
    summary = BackfillRunSummary(
        generated_at=report["generated_at"],
        total_jobs=snapshot.jobs_with_apply_url,
        classified_jobs=classified,
        open_jobs=all_statuses.get("open", 0),
        closed_jobs=all_statuses.get("closed", 0),
        unknown_jobs=snapshot.jobs_with_apply_url - classified,
        coverage_ratio=report["coverage_ratio"],
        report_path=output_report_path,
        unresolved_hosts=dict(unresolved_hosts.most_common(15)),
        processed_jobs=len(results),
        skipped_cached_jobs=skipped_cached,
        dry_run=dry_run,
        request_timeout_seconds=request_timeout,
        cache_path=str(resolved_cache_path),
        job_app_state_path=str(resolved_job_app_state_path),
        allow_unknown_overwrite_terminal=allow_unknown_overwrite_terminal,
        run_scope_total_jobs=run_scope_total_jobs,
        canonical_total_jobs=snapshot.total_jobs,
        canonical_total_jobs_with_apply_url=snapshot.jobs_with_apply_url,
    )
    if summary_path is not None:
        write_summary(summary_path, summary.__dict__)
    return summary
