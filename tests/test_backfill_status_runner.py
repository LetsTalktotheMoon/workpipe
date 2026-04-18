from __future__ import annotations

import json
from pathlib import Path

import backfill_status.cli as cli_module
import backfill_status.persistence as persistence_module
import backfill_status.runner as runner_module
from backfill_status.models import DetectionResult, FetchedPage, JobAvailability, JobRecord
from backfill_status.pool import JobPoolSnapshot
from backfill_status.runner import BackfillRunSummary


def _job(job_id: str, host: str = "example.com", source_scope: str = "scraped_current") -> JobRecord:
    return JobRecord(
        job_id=job_id,
        company_name="Acme",
        title="Software Engineer",
        apply_url=f"https://{host}/jobs/{job_id}",
        host=host,
        source_scope=source_scope,
    )


def _result(job_id: str, status: JobAvailability, host: str = "example.com") -> DetectionResult:
    return DetectionResult(
        job_id=job_id,
        status=status,
        detector="test",
        confidence=0.8,
        reason="fixture",
        requested_url=f"https://{host}/jobs/{job_id}",
        final_url=f"https://{host}/jobs/{job_id}",
        host=host,
    )


def test_detection_result_serializes_status_value() -> None:
    payload = _result("job-1", JobAvailability.OPEN).to_dict()
    assert payload["status"] == "open"


def test_run_backfill_iterative_mode_skips_terminal_cached_jobs(monkeypatch) -> None:
    snapshot = JobPoolSnapshot(
        jobs=[
            _job("job-open-cached", "boards.greenhouse.io"),
            _job("job-recheck", "jobs.ashbyhq.com"),
            _job("job-new", "jobs.lever.co"),
        ],
        total_jobs=3,
        jobs_with_apply_url=3,
        unique_hosts=3,
        host_counts={"boards.greenhouse.io": 1, "jobs.ashbyhq.com": 1, "jobs.lever.co": 1},
    )
    monkeypatch.setattr(runner_module, "load_full_job_pool", lambda: snapshot)
    monkeypatch.setattr(
        runner_module,
        "load_backfill_cache",
        lambda path=None: {
            "job-open-cached": {"status": "open"},
            "job-recheck": {"status": "unknown"},
        },
    )

    detected_job_ids: list[str] = []

    def fake_detect(job: JobRecord, session=None) -> DetectionResult:
        detected_job_ids.append(job.job_id)
        if job.job_id == "job-recheck":
            return _result(job.job_id, JobAvailability.CLOSED, host=job.host)
        return _result(job.job_id, JobAvailability.UNKNOWN, host=job.host)

    monkeypatch.setattr(runner_module, "detect_job_status", fake_detect)

    cache_write_called = {"value": False}
    apply_called = {"value": False, "count": 0}

    def fake_cache_write(existing, results, path=None):
        cache_write_called["value"] = True
        return dict(existing)

    def fake_apply(results, dry_run, state_path=None):
        apply_called["value"] = True
        apply_called["count"] = len(results)
        return {}

    monkeypatch.setattr(runner_module, "write_backfill_cache", fake_cache_write)
    monkeypatch.setattr(runner_module, "apply_results_to_job_app_state", fake_apply)

    summary = runner_module.run_backfill(
        dry_run=True,
        force=False,
        request_timeout=None,
        write_report=False,
    )

    assert sorted(detected_job_ids) == ["job-new", "job-recheck"]
    assert summary.processed_jobs == 2
    assert summary.skipped_cached_jobs == 1
    assert abs(summary.coverage_ratio - (2 / 3)) < 1e-9
    assert cache_write_called["value"] is False
    assert apply_called["value"] is True
    assert apply_called["count"] == 2
    assert "jobs.lever.co" in summary.unresolved_hosts


def test_run_backfill_preserves_terminal_cache_on_unknown_rerun(monkeypatch) -> None:
    snapshot = JobPoolSnapshot(
        jobs=[_job("job-terminal", "boards.greenhouse.io")],
        total_jobs=1,
        jobs_with_apply_url=1,
        unique_hosts=1,
        host_counts={"boards.greenhouse.io": 1},
    )
    monkeypatch.setattr(runner_module, "load_full_job_pool", lambda: snapshot)
    monkeypatch.setattr(
        runner_module,
        "load_backfill_cache",
        lambda path=None: {
            "job-terminal": {"status": "closed", "detector": "prior"},
        },
    )
    monkeypatch.setattr(
        runner_module,
        "detect_job_status",
        lambda job, session=None: _result(job.job_id, JobAvailability.UNKNOWN, host=job.host),
    )
    monkeypatch.setattr(runner_module, "apply_results_to_job_app_state", lambda results, dry_run, state_path=None: {})
    monkeypatch.setattr(runner_module, "write_backfill_cache", lambda existing, results, path=None, **kwargs: dict(existing))

    summary = runner_module.run_backfill(
        dry_run=True,
        force=True,
        request_timeout=None,
        write_report=False,
    )
    assert summary.closed_jobs == 1
    assert summary.unknown_jobs == 0
    assert abs(summary.coverage_ratio - 1.0) < 1e-9


def test_run_backfill_plumbs_request_timeout_to_fetch_page(monkeypatch) -> None:
    snapshot = JobPoolSnapshot(
        jobs=[_job("job-timeout", "boards.greenhouse.io")],
        total_jobs=1,
        jobs_with_apply_url=1,
        unique_hosts=1,
        host_counts={"boards.greenhouse.io": 1},
    )
    monkeypatch.setattr(runner_module, "load_full_job_pool", lambda: snapshot)
    monkeypatch.setattr(runner_module, "load_backfill_cache", lambda path=None: {})

    timeout_values: list[float] = []

    def fake_fetch_page(url: str, session=None, timeout: int = 20) -> FetchedPage:
        timeout_values.append(float(timeout))
        return FetchedPage(
            requested_url=url,
            final_url=url,
            status_code=200,
            title="Software Engineer",
            raw_html="Apply now",
            text="Apply now",
        )

    monkeypatch.setattr(runner_module, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(runner_module, "evaluate_fetched_page", lambda job, page: _result(job.job_id, JobAvailability.OPEN))
    monkeypatch.setattr(runner_module, "apply_results_to_job_app_state", lambda results, dry_run, state_path=None: {})
    monkeypatch.setattr(runner_module, "write_backfill_cache", lambda existing, results, path=None: dict(existing))

    summary = runner_module.run_backfill(
        dry_run=True,
        force=True,
        request_timeout=7.5,
        write_report=False,
    )

    assert timeout_values == [7.5]
    assert summary.processed_jobs == 1
    assert summary.open_jobs == 1
    assert abs(summary.coverage_ratio - 1.0) < 1e-9


def test_run_backfill_report_distinguishes_canonical_and_run_scope(monkeypatch, tmp_path: Path) -> None:
    snapshot = JobPoolSnapshot(
        jobs=[
            _job("job-open-cached", "boards.greenhouse.io", source_scope="scraped_current"),
            _job("job-recheck", "jobs.ashbyhq.com", source_scope="portfolio_history"),
            _job("job-new", "jobs.lever.co", source_scope="both"),
        ],
        total_jobs=5,
        jobs_with_apply_url=3,
        unique_hosts=3,
        host_counts={"boards.greenhouse.io": 1, "jobs.ashbyhq.com": 1, "jobs.lever.co": 1},
        source_scope_counts={"scraped_current": 1, "portfolio_history": 1, "both": 1},
        generated_at="2026-04-13T09:00:00",
    )
    monkeypatch.setattr(runner_module, "load_full_job_pool", lambda: snapshot)
    monkeypatch.setattr(
        runner_module,
        "load_backfill_cache",
        lambda path=None: {
            "job-open-cached": {"status": "open"},
        },
    )
    monkeypatch.setattr(
        runner_module,
        "detect_job_status",
        lambda job, session=None: _result(job.job_id, JobAvailability.CLOSED, host=job.host),
    )
    monkeypatch.setattr(runner_module, "apply_results_to_job_app_state", lambda results, dry_run, state_path=None: {})
    monkeypatch.setattr(runner_module, "write_backfill_cache", lambda existing, results, path=None, **kwargs: dict(existing))

    captured_report: dict[str, object] = {}

    def fake_write_backfill_report(payload, *, report_path=None, report_dir=None):
        captured_report.update(payload)
        assert report_path is not None
        return report_path

    monkeypatch.setattr(runner_module, "write_backfill_report", fake_write_backfill_report)

    summary = runner_module.run_backfill(
        dry_run=True,
        force=False,
        limit=1,
        report_path=tmp_path / "report.json",
    )

    assert summary.canonical_total_jobs == 5
    assert summary.canonical_total_jobs_with_apply_url == 3
    assert summary.run_scope_total_jobs == 1
    assert captured_report["canonical_total_jobs"] == 5
    assert captured_report["canonical_total_jobs_with_apply_url"] == 3
    assert captured_report["requested_scope_total_jobs"] == 3
    assert captured_report["eligible_scope_total_jobs"] == 2
    assert captured_report["run_scope_total_jobs"] == 1
    assert captured_report["canonical_source_scope_counts"] == {
        "scraped_current": 1,
        "portfolio_history": 1,
        "both": 1,
    }
    assert captured_report["run_scope_source_scope_counts"] == {"portfolio_history": 1}
    assert "Deprecated compat alias" in str(captured_report["pool_total_jobs_semantics"])


def test_run_backfill_timeout_path_preserves_linkedin_guest_detector(monkeypatch) -> None:
    snapshot = JobPoolSnapshot(
        jobs=[_job("job-linkedin", "www.linkedin.com")],
        total_jobs=1,
        jobs_with_apply_url=1,
        unique_hosts=1,
        host_counts={"www.linkedin.com": 1},
    )
    monkeypatch.setattr(runner_module, "load_full_job_pool", lambda: snapshot)
    monkeypatch.setattr(runner_module, "load_backfill_cache", lambda path=None: {})

    guest_timeout_values: list[float] = []

    def fake_fetch_linkedin_guest_page(job: JobRecord, session=None, timeout: float = 20.0) -> FetchedPage:
        guest_timeout_values.append(float(timeout))
        return FetchedPage(
            requested_url=job.apply_url,
            final_url=f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job.job_id}",
            status_code=200,
            title="Software Engineer",
            raw_html="guest payload",
            text="guest payload",
        )

    def fake_fetch_page(url: str, session=None, timeout: int = 20):
        raise AssertionError("LinkedIn timeout path should not bypass guest endpoint when guest detection is terminal")

    monkeypatch.setattr(runner_module, "fetch_linkedin_guest_page", fake_fetch_linkedin_guest_page)
    monkeypatch.setattr(runner_module, "fetch_page", fake_fetch_page)
    monkeypatch.setattr(
        runner_module,
        "evaluate_fetched_page",
        lambda job, page: _result(job.job_id, JobAvailability.OPEN, host=job.host),
    )
    monkeypatch.setattr(runner_module, "apply_results_to_job_app_state", lambda results, dry_run, state_path=None: {})
    monkeypatch.setattr(runner_module, "write_backfill_cache", lambda existing, results, path=None, **kwargs: dict(existing))

    summary = runner_module.run_backfill(
        dry_run=True,
        force=True,
        write_report=False,
    )

    assert guest_timeout_values == [20.0]
    assert summary.processed_jobs == 1
    assert summary.open_jobs == 1
    assert abs(summary.coverage_ratio - 1.0) < 1e-9


def test_persistence_cache_and_state_semantics(tmp_path: Path) -> None:
    cache_path = tmp_path / "state" / "job_status_backfill.json"
    state_path = tmp_path / "state" / "job_app_status.json"

    existing_cache = {
        "job-a": {"status": "unknown", "detector": "seed"},
        "job-terminal": {"status": "open", "detector": "seed"},
    }
    persistence_module.write_backfill_cache(
        existing_cache,
        [
            _result("job-b", JobAvailability.CLOSED),
            _result("job-terminal", JobAvailability.UNKNOWN),
        ],
        path=cache_path,
    )
    loaded_cache = persistence_module.load_backfill_cache(path=cache_path)
    assert loaded_cache["job-a"]["status"] == "unknown"
    assert loaded_cache["job-b"]["status"] == "closed"
    assert loaded_cache["job-terminal"]["status"] == "open"

    overwritten = persistence_module.write_backfill_cache(
        loaded_cache,
        [_result("job-terminal", JobAvailability.UNKNOWN)],
        path=cache_path,
        allow_unknown_overwrite_terminal=True,
    )
    assert overwritten["job-terminal"]["status"] == "unknown"

    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "job-b": {
                    "applied": True,
                    "abandoned": False,
                    "closed": True,
                    "updated_at": "2026-01-01T00:00:00",
                },
                "job-z": {
                    "applied": False,
                    "abandoned": False,
                    "closed": True,
                    "updated_at": "2026-01-01T00:00:00",
                }
            }
        ),
        encoding="utf-8",
    )
    persistence_module.apply_results_to_job_app_state(
        [
            _result("job-b", JobAvailability.OPEN),
            _result("job-c", JobAvailability.CLOSED),
            _result("job-d", JobAvailability.OPEN),
            _result("job-z", JobAvailability.UNKNOWN),
        ],
        dry_run=False,
        state_path=state_path,
    )
    state_payload = json.loads(state_path.read_text(encoding="utf-8"))
    assert state_payload["job-b"]["applied"] is True
    assert state_payload["job-b"]["closed"] is False
    assert state_payload["job-c"]["closed"] is True
    assert state_payload["job-z"]["closed"] is True
    assert "job-d" not in state_payload


def test_cli_threshold_and_path_arguments(monkeypatch, tmp_path: Path, capsys) -> None:
    captured: dict[str, object] = {}

    def fake_run_backfill(**kwargs):
        captured.update(kwargs)
        return BackfillRunSummary(
            generated_at="2026-04-12T10:00:00",
            total_jobs=10,
            classified_jobs=5,
            open_jobs=3,
            closed_jobs=2,
            unknown_jobs=5,
            coverage_ratio=0.5,
            report_path="",
            unresolved_hosts={"example.com": 1},
            processed_jobs=4,
            skipped_cached_jobs=6,
            dry_run=True,
            request_timeout_seconds=9.0,
            cache_path=str(tmp_path / "cache.json"),
            job_app_state_path=str(tmp_path / "job_app_state.json"),
            allow_unknown_overwrite_terminal=False,
        )

    monkeypatch.setattr(cli_module, "run_backfill", fake_run_backfill)
    exit_code = cli_module.main(
        [
            "--dry-run",
            "--concurrency",
            "8",
            "--request-timeout",
            "9",
            "--cache-path",
            str(tmp_path / "cache.json"),
            "--job-app-state-path",
            str(tmp_path / "job_app_state.json"),
            "--report-path",
            str(tmp_path / "report.json"),
            "--summary-path",
            str(tmp_path / "summary.json"),
            "--no-report",
            "--min-coverage",
            "0.8",
        ]
    )
    assert exit_code == 2
    assert captured["concurrency"] == 8
    assert captured["request_timeout"] == 9.0
    assert captured["write_report"] is False
    assert captured["allow_unknown_overwrite_terminal"] is False
    assert str(captured["cache_path"]).endswith("cache.json")

    printed = capsys.readouterr().out
    payload = json.loads(printed)
    assert payload["coverage_ratio"] == 0.5
