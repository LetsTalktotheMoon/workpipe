from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

import pytest

import managed_run


FIXED_NOW = datetime(2026, 4, 13, 10, 0, 0)


class FakeChildProcess:
    def __init__(self, *, returncode: int = 0, stdout_lines: list[str] | None = None) -> None:
        self.pid = 4242
        self.returncode = returncode
        self.stdout = iter(stdout_lines or [])

    def poll(self) -> int | None:
        return None

    def wait(self) -> int:
        return self.returncode


@pytest.fixture
def isolated_managed_run_env(monkeypatch: pytest.MonkeyPatch, tmp_path):
    root = tmp_path / "workspace"
    state_root = root / "state"
    runs_root = root / "runs"
    managed_log_root = runs_root / "managed_logs"
    priority_input_root = state_root / "priority_inputs"

    managed_log_root.mkdir(parents=True, exist_ok=True)
    priority_input_root.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(managed_run, "ROOT", root)
    monkeypatch.setattr(managed_run, "STATE_ROOT", state_root)
    monkeypatch.setattr(managed_run, "RUNS_ROOT", runs_root)
    monkeypatch.setattr(managed_run, "MONITOR_STATE_PATH", state_root / "managed_runs.json")
    monkeypatch.setattr(managed_run, "MONITOR_LOCK_PATH", state_root / "managed_runs.lock")
    monkeypatch.setattr(managed_run, "WAITING_QUEUE_PATH", state_root / "waiting_retry_queues.json")
    monkeypatch.setattr(managed_run, "PRIORITY_INPUT_ROOT", priority_input_root)
    monkeypatch.setattr(managed_run, "MANAGED_LOG_ROOT", managed_log_root)
    monkeypatch.setattr(managed_run, "_now", lambda: FIXED_NOW)
    monkeypatch.setattr(managed_run.signal, "signal", lambda *_args, **_kwargs: None)
    return root


def _load_single_process() -> dict[str, object]:
    state = managed_run.load_monitor_state()
    processes = state.get("processes", [])
    assert isinstance(processes, list)
    assert len(processes) == 1
    process = processes[0]
    assert isinstance(process, dict)
    return process


def test_managed_runner_runs_scraper_preset_backfill_before_launch(
    isolated_managed_run_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    order: list[str] = []
    calls: list[dict[str, object]] = []

    def fake_run_backfill(**kwargs):
        calls.append(dict(kwargs))
        order.append("backfill")
        return SimpleNamespace(
            processed_jobs=3,
            classified_jobs=12,
            report_path="/tmp/latest_backfill_status.json",
            generated_at="2026-04-13T10:00:00",
        )

    def fake_popen(command, **_kwargs):
        order.append("spawn")
        return FakeChildProcess()

    monkeypatch.setattr(managed_run.subprocess, "Popen", fake_popen)
    monkeypatch.setattr("backfill_status.runner.run_backfill", fake_run_backfill)

    runner = managed_run.ManagedRunner(
        label="daily_job_scraper",
        display_name="Daily Job Scraper",
        cwd=str(isolated_managed_run_env),
        command=["python", str(isolated_managed_run_env / "scraper_entry.py")],
        preset_id="daily_job_scraper",
        metadata={},
    )

    exit_code = runner.run()

    assert exit_code == 0
    assert order == ["backfill", "spawn"]
    assert calls == [{"force": True}]
    process = _load_single_process()
    assert process["status"] == "completed"
    metadata = process["metadata"]
    assert isinstance(metadata, dict)
    assert metadata["scraper_pre_hook"]["status"] == "completed"


def test_managed_runner_runs_backfill_for_pipeline_jobs_command(
    isolated_managed_run_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    order: list[str] = []

    def fake_run_backfill(**_kwargs):
        order.append("backfill")
        return SimpleNamespace(
            processed_jobs=1,
            classified_jobs=2,
            report_path="",
            generated_at="2026-04-13T10:00:00",
        )

    def fake_popen(command, **_kwargs):
        order.append("spawn")
        return FakeChildProcess()

    monkeypatch.setattr(managed_run.subprocess, "Popen", fake_popen)
    monkeypatch.setattr("backfill_status.runner.run_backfill", fake_run_backfill)

    runner = managed_run.ManagedRunner(
        label="jobs_only",
        display_name="Jobs Only",
        cwd=str(isolated_managed_run_env),
        command=["python", str(isolated_managed_run_env / "pipeline.py"), "jobs", "--lookback-hours", "48"],
        preset_id="scrape_only",
        metadata={},
    )

    exit_code = runner.run()

    assert exit_code == 0
    assert order == ["backfill", "spawn"]


def test_managed_runner_skips_backfill_for_non_scraper_task(
    isolated_managed_run_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    order: list[str] = []

    def fake_popen(command, **_kwargs):
        order.append("spawn")
        return FakeChildProcess()

    monkeypatch.setattr(managed_run.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(
        "backfill_status.runner.run_backfill",
        lambda **_kwargs: pytest.fail("backfill pre-hook should not run for non-scraper tasks"),
    )

    runner = managed_run.ManagedRunner(
        label="resume_only",
        display_name="Resume Only",
        cwd=str(isolated_managed_run_env),
        command=["python", str(isolated_managed_run_env / "pipeline.py"), "resume"],
        preset_id="resume_only",
        metadata={},
    )

    exit_code = runner.run()

    assert exit_code == 0
    assert order == ["spawn"]


def test_managed_runner_fails_fast_when_scraper_backfill_hook_fails(
    isolated_managed_run_env,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        managed_run.subprocess,
        "Popen",
        lambda *_args, **_kwargs: pytest.fail("child process should not start after backfill hook failure"),
    )
    monkeypatch.setattr(
        "backfill_status.runner.run_backfill",
        lambda **_kwargs: (_ for _ in ()).throw(ValueError("boom")),
    )

    runner = managed_run.ManagedRunner(
        label="daily_job_scraper",
        display_name="Daily Job Scraper",
        cwd=str(isolated_managed_run_env),
        command=["python", str(isolated_managed_run_env / "scraper_entry.py")],
        preset_id="daily_job_scraper",
        metadata={},
    )

    with pytest.raises(RuntimeError, match="Scraper pre-hook failed before child launch: boom"):
        runner.run()

    process = _load_single_process()
    assert process["status"] == "failed"
    assert "Scraper pre-hook failed before child launch: boom" in str(process["last_error"])
