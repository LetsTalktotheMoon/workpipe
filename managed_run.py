#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
STATE_ROOT = ROOT / "state"
RUNS_ROOT = ROOT / "runs"
DEFAULT_JOBS_JSON = ROOT / "data" / "job_tracker" / "scraped_jobs.json"
DEFAULT_PORTFOLIO_ROOT = ROOT / "data" / "deliverables" / "resume_portfolio"
MONITOR_STATE_PATH = STATE_ROOT / "managed_runs.json"
MONITOR_LOCK_PATH = STATE_ROOT / "managed_runs.lock"
WAITING_QUEUE_PATH = STATE_ROOT / "waiting_retry_queues.json"
PRIORITY_INPUT_ROOT = STATE_ROOT / "priority_inputs"
MANAGED_LOG_ROOT = RUNS_ROOT / "managed_logs"
MAX_TAIL_LINES = 24
PRIORITY_JOB_IDS_ENV = "MANAGED_PRIORITY_JOB_IDS_FILE"
MONITORED_PS_PATTERNS = (
    "pipeline.py all",
    "pipeline.py resume",
    "pipeline.py jobs",
    "pipeline.py pdf",
    "rereview_resume_portfolio.py",
    "scheduled_daily_pipeline.sh",
)
_PRESET_CACHE_SIGNATURE: tuple[int, int] | None = None
_PRESET_CACHE: list[dict[str, Any]] | None = None


def _now() -> datetime:
    return datetime.now()


def _now_iso() -> str:
    return _now().isoformat(timespec="seconds")


def _slug(text: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", text.strip().lower())
    return normalized.strip("_") or "run"


@contextmanager
def _locked_state() -> Any:
    STATE_ROOT.mkdir(parents=True, exist_ok=True)
    with MONITOR_LOCK_PATH.open("a+", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        if MONITOR_STATE_PATH.exists():
            try:
                payload = json.loads(MONITOR_STATE_PATH.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                payload = {}
        else:
            payload = {}
        if not isinstance(payload, dict):
            payload = {}
        payload.setdefault("processes", [])
        payload.setdefault("updated_at", "")
        yield payload
        payload["updated_at"] = _now_iso()
        temp_path = MONITOR_STATE_PATH.with_suffix(".json.tmp")
        temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temp_path.replace(MONITOR_STATE_PATH)
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _update_state(mutator) -> Any:
    with _locked_state() as payload:
        return mutator(payload)


def load_monitor_state() -> dict[str, Any]:
    if not MONITOR_STATE_PATH.exists():
        return {"processes": [], "updated_at": ""}
    try:
        payload = json.loads(MONITOR_STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"processes": [], "updated_at": ""}
    if not isinstance(payload, dict):
        return {"processes": [], "updated_at": ""}
    payload.setdefault("processes", [])
    payload.setdefault("updated_at", "")
    return payload


def load_waiting_retry_queues() -> dict[str, Any]:
    if not WAITING_QUEUE_PATH.exists():
        return {"queues": {}, "updated_at": ""}
    try:
        payload = json.loads(WAITING_QUEUE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"queues": {}, "updated_at": ""}
    if not isinstance(payload, dict):
        return {"queues": {}, "updated_at": ""}
    queues = payload.get("queues", {})
    payload["queues"] = queues if isinstance(queues, dict) else {}
    payload.setdefault("updated_at", "")
    return payload


def _update_waiting_retry_queues(mutator) -> Any:
    STATE_ROOT.mkdir(parents=True, exist_ok=True)
    with MONITOR_LOCK_PATH.open("a+", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        if WAITING_QUEUE_PATH.exists():
            try:
                payload = json.loads(WAITING_QUEUE_PATH.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                payload = {}
        else:
            payload = {}
        if not isinstance(payload, dict):
            payload = {}
        queues = payload.get("queues", {})
        payload["queues"] = queues if isinstance(queues, dict) else {}
        result = mutator(payload)
        payload["updated_at"] = _now_iso()
        temp_path = WAITING_QUEUE_PATH.with_suffix(".json.tmp")
        temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temp_path.replace(WAITING_QUEUE_PATH)
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        return result


def _upsert_process(record: dict[str, Any]) -> None:
    def mutator(payload: dict[str, Any]) -> None:
        processes = payload.setdefault("processes", [])
        for index, existing in enumerate(processes):
            if str(existing.get("id", "")) == str(record.get("id", "")):
                processes[index] = record
                break
        else:
            processes.append(record)
        processes.sort(key=lambda item: str(item.get("started_at", "")), reverse=True)

    _update_state(mutator)


def _patch_process(run_id: str, **updates: Any) -> dict[str, Any] | None:
    def mutator(payload: dict[str, Any]) -> dict[str, Any] | None:
        processes = payload.setdefault("processes", [])
        for index, existing in enumerate(processes):
            if str(existing.get("id", "")) != run_id:
                continue
            updated = dict(existing)
            updated.update(updates)
            updated["updated_at"] = _now_iso()
            processes[index] = updated
            return updated
        return None

    return _update_state(mutator)


def merge_process_metadata(run_id: str, updates: dict[str, Any], *, log_line: str = "") -> dict[str, Any] | None:
    def mutator(payload: dict[str, Any]) -> dict[str, Any] | None:
        processes = payload.setdefault("processes", [])
        for index, existing in enumerate(processes):
            if str(existing.get("id", "")) != run_id:
                continue
            updated = dict(existing)
            metadata = updated.get("metadata", {})
            merged = dict(metadata) if isinstance(metadata, dict) else {}
            for key, value in updates.items():
                if value is None:
                    merged.pop(key, None)
                else:
                    merged[key] = value
            updated["metadata"] = merged
            if log_line:
                tail = list(updated.get("log_tail", []) or [])
                tail.append(log_line.rstrip())
                updated["log_tail"] = tail[-MAX_TAIL_LINES:]
            updated["updated_at"] = _now_iso()
            processes[index] = updated
            return updated
        return None

    return _update_state(mutator)


def find_waiting_process(preset_id: str) -> dict[str, Any] | None:
    state = load_monitor_state()
    matches = [
        item
        for item in state.get("processes", []) or []
        if isinstance(item, dict)
        and str(item.get("preset_id", "") or "") == preset_id
        and str(item.get("status", "") or "") == "waiting_retry"
        and str(item.get("quota_kind", "") or "") == "short_window"
    ]
    if not matches:
        return None
    matches.sort(key=lambda item: str(item.get("updated_at", "") or item.get("started_at", "") or ""), reverse=True)
    return matches[0]


def _waiting_queue_sort_key(item: dict[str, Any]) -> tuple[int, float, str]:
    raw = item.get("sort_key", [0, 0.0, ""])
    if isinstance(raw, list) and len(raw) >= 3:
        try:
            return (int(raw[0] or 0), float(raw[1] or 0), str(raw[2] or ""))
        except (TypeError, ValueError):
            return (0, 0.0, "")
    return (0, 0.0, "")


def load_waiting_retry_queue(run_id: str) -> dict[str, Any] | None:
    payload = load_waiting_retry_queues()
    queues = payload.get("queues", {})
    if not isinstance(queues, dict):
        return None
    queue = queues.get(run_id)
    return queue if isinstance(queue, dict) else None


def merge_waiting_retry_queue(run_id: str, *, preset_id: str, items: list[dict[str, Any]], source: str = "nightly_scrape") -> dict[str, Any]:
    def mutator(payload: dict[str, Any]) -> dict[str, Any]:
        queues = payload.setdefault("queues", {})
        existing = queues.get(run_id, {})
        existing_items = existing.get("items", []) if isinstance(existing, dict) else []
        combined: dict[str, dict[str, Any]] = {}
        for item in existing_items:
            if isinstance(item, dict):
                job_id = str(item.get("job_id", "") or "").strip()
                if job_id:
                    combined[job_id] = item
        for item in items:
            if not isinstance(item, dict):
                continue
            job_id = str(item.get("job_id", "") or "").strip()
            if not job_id:
                continue
            combined[job_id] = item
        merged_items = sorted(combined.values(), key=_waiting_queue_sort_key, reverse=True)
        queue_payload = {
            "run_id": run_id,
            "preset_id": preset_id,
            "source": source,
            "updated_at": _now_iso(),
            "items": merged_items,
        }
        queues[run_id] = queue_payload
        return queue_payload

    return _update_waiting_retry_queues(mutator)


def clear_waiting_retry_queue(run_id: str) -> None:
    def mutator(payload: dict[str, Any]) -> None:
        queues = payload.setdefault("queues", {})
        if isinstance(queues, dict):
            queues.pop(run_id, None)

    _update_waiting_retry_queues(mutator)


def _append_log_tail(run_id: str, line: str) -> None:
    def mutator(payload: dict[str, Any]) -> None:
        processes = payload.setdefault("processes", [])
        for index, existing in enumerate(processes):
            if str(existing.get("id", "")) != run_id:
                continue
            updated = dict(existing)
            tail = list(updated.get("log_tail", []) or [])
            tail.append(line.rstrip())
            updated["log_tail"] = tail[-MAX_TAIL_LINES:]
            updated["updated_at"] = _now_iso()
            processes[index] = updated
            return

    _update_state(mutator)


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def _count_results(payload: dict[str, Any]) -> tuple[int, int]:
    items = payload.get("results", []) or payload.get("targets", []) or []
    if not isinstance(items, list):
        return (0, 0)
    completed = sum(1 for item in items if isinstance(item, dict) and str(item.get("status", "") or "") not in {"", "running"})
    return (completed, len(items))


def compute_progress(command: list[str], run_dir: str) -> dict[str, Any]:
    if not run_dir:
        return {}
    target = Path(run_dir)
    if not target.exists():
        return {}

    progress: dict[str, Any] = {"run_dir": str(target)}
    command_text = " ".join(command)
    if "pipeline.py all" in command_text:
        resume_root = target / "resume_step"
        accepted = _read_json(resume_root / "accepted_jobs.json", [])
        rejected = _read_json(resume_root / "rejected_jobs.json", [])
        staged = len(list((resume_root / "jobs").glob("*"))) if (resume_root / "jobs").exists() else 0
        progress.update(
            {
                "mode": "all",
                "accepted_jobs": len(accepted) if isinstance(accepted, list) else 0,
                "rejected_jobs": len(rejected) if isinstance(rejected, list) else 0,
                "staged_jobs": staged,
            }
        )
        all_summary = _read_json(target / "all_summary.json", {})
        if isinstance(all_summary, dict) and all_summary:
            resume_summary = all_summary.get("resume_summary", {}) or {}
            pdf_summary = all_summary.get("pdf_summary", {}) or {}
            progress["handled_jobs"] = int(resume_summary.get("handled_jobs", 0) or 0)
            completed_targets, total_targets = _count_results(pdf_summary)
            progress["pdf_progress"] = {"completed": completed_targets, "total": total_targets}
        return progress

    if "pipeline.py resume" in command_text:
        accepted = _read_json(target / "accepted_jobs.json", [])
        rejected = _read_json(target / "rejected_jobs.json", [])
        staged = len(list((target / "jobs").glob("*"))) if (target / "jobs").exists() else 0
        progress.update(
            {
                "mode": "resume",
                "accepted_jobs": len(accepted) if isinstance(accepted, list) else 0,
                "rejected_jobs": len(rejected) if isinstance(rejected, list) else 0,
                "staged_jobs": staged,
            }
        )
        manifest = _read_json(target / "run_manifest.json", {})
        if isinstance(manifest, dict) and manifest:
            progress["handled_jobs"] = int(manifest.get("handled_jobs", 0) or 0)
        return progress

    if "pipeline.py jobs" in command_text:
        summary = _read_json(target / "jobs_summary.json", {})
        if isinstance(summary, dict) and summary:
            progress["mode"] = "jobs"
            progress["used_existing_json"] = bool(summary.get("used_existing_json", False))
        return progress

    if "pipeline.py pdf" in command_text:
        summary = _read_json(target / "pdf_summary.json", {})
        if isinstance(summary, dict) and summary:
            completed_targets, total_targets = _count_results(summary)
            progress["mode"] = "pdf"
            progress["pdf_progress"] = {"completed": completed_targets, "total": total_targets}
        return progress

    return progress


@dataclass
class QuotaSignal:
    kind: str
    next_retry_at: datetime | None
    reason: str


def _parse_time_only(value: str, now: datetime) -> datetime | None:
    text = value.strip().upper()
    for fmt in ("%I:%M %p", "%I %p", "%H:%M"):
        try:
            parsed = datetime.strptime(text, fmt)
            candidate = now.replace(hour=parsed.hour, minute=parsed.minute, second=0, microsecond=0)
            if candidate <= now:
                candidate = candidate + timedelta(days=1)
            return candidate
        except ValueError:
            continue
    return None


def _parse_absolute_datetime(text: str, now: datetime) -> datetime | None:
    normalized = re.sub(r"\s+", " ", text.strip().replace("T", " "))
    normalized = re.sub(r"\s+[A-Z]{2,5}$", "", normalized)
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%b %d %Y %I:%M %p",
        "%B %d %Y %I:%M %p",
        "%b %d, %Y %I:%M %p",
        "%B %d, %Y %I:%M %p",
        "%b %d %I:%M %p",
        "%B %d %I:%M %p",
        "%b %d, %I:%M %p",
        "%B %d, %I:%M %p",
    ):
        try:
            parsed = datetime.strptime(normalized, fmt)
            if "%Y" not in fmt:
                parsed = parsed.replace(year=now.year)
                if parsed < now - timedelta(days=1):
                    parsed = parsed.replace(year=now.year + 1)
            return parsed
        except ValueError:
            continue
    return _parse_time_only(normalized, now)


def parse_retry_time(message: str, now: datetime | None = None) -> datetime | None:
    current = now or _now()
    iso_match = re.search(r"(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2})?)", message)
    if iso_match:
        return _parse_absolute_datetime(iso_match.group(1), current)

    for pattern in (
        r"(?:reset|refresh|retry|try again|available again)\s+(?:at|on)\s+([A-Z][a-z]{2,9}\s+\d{1,2}(?:,\s*\d{4})?(?:\s+\d{1,2}:\d{2}\s*(?:AM|PM))?)",
        r"(?:reset|refresh|retry|try again|available again)\s+(?:at|on)\s+(\d{1,2}(?::\d{2})?\s*(?:AM|PM))",
        r"(?:resets?|refreshes?)\s+(?:in|after)\s+(?:(\d+)\s*(?:h|hr|hrs|hour|hours))?\s*(?:(\d+)\s*(?:m|min|mins|minute|minutes))?",
    ):
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            if match.lastindex and match.lastindex >= 2 and match.group(1) and match.group(1).isdigit():
                hours = int(match.group(1) or 0)
                minutes = int(match.group(2) or 0)
                if hours or minutes:
                    return current + timedelta(hours=hours, minutes=minutes)
            else:
                parsed = _parse_absolute_datetime(match.group(1), current)
                if parsed is not None:
                    return parsed

    relative_match = re.search(
        r"(?:in|after)\s+(?:(\d+)\s*(?:h|hr|hrs|hour|hours))?\s*(?:(\d+)\s*(?:m|min|mins|minute|minutes))?",
        message,
        re.IGNORECASE,
    )
    if relative_match:
        hours = int(relative_match.group(1) or 0)
        minutes = int(relative_match.group(2) or 0)
        if hours or minutes:
            return current + timedelta(hours=hours, minutes=minutes)
    return None


def classify_quota_error(message: str) -> QuotaSignal | None:
    text = str(message or "").strip()
    if not text:
        return None
    lower = text.lower()
    quota_markers = ("quota", "limit", "rate limit", "usage cap", "too many requests")
    if not any(marker in lower for marker in quota_markers):
        return None

    weekly_markers = ("weekly", "week limit", "week cap", "weekly quota", "per week", "7 days", "7-day", "seven days")
    if any(marker in lower for marker in weekly_markers):
        return QuotaSignal(kind="weekly", next_retry_at=None, reason=text[:800])

    short_markers = (
        "5h",
        "5-hour",
        "5 hour",
        "5hr",
        "5-hour cap",
        "5 hour cap",
        "5-hour limit",
        "5 hour limit",
        "hours",
        "resets at",
        "refreshes at",
        "try again at",
        "available again",
    )
    if any(marker in lower for marker in short_markers):
        return QuotaSignal(kind="short_window", next_retry_at=parse_retry_time(text), reason=text[:800])

    if "quota" in lower or "limit" in lower:
        return QuotaSignal(kind="short_window", next_retry_at=parse_retry_time(text), reason=text[:800])
    return None


def _safe_load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _extract_date(raw: str) -> str:
    text = str(raw or "").strip()
    return text[:10] if len(text) >= 10 else ""


def _portfolio_manifest_status(manifest: dict[str, Any]) -> str:
    review = manifest.get("review", {}) if isinstance(manifest.get("review"), dict) else {}
    return str(
        manifest.get("review_verdict", "")
        or review.get("verdict", "")
        or review.get("overall_verdict", "")
        or ""
    ).strip().lower()


def _resume_pdf_exists(manifest_path: Path, manifest: dict[str, Any]) -> bool:
    explicit = str(manifest.get("resume_pdf", "") or "").strip()
    if explicit:
        explicit_path = Path(explicit).expanduser()
        if not explicit_path.is_absolute():
            explicit_path = (ROOT / explicit_path).resolve()
        if explicit_path.exists():
            return True
    return (manifest_path.parent / "resume.pdf").exists()


def _safe_mtime(path: Path) -> int:
    try:
        return path.stat().st_mtime_ns
    except FileNotFoundError:
        return -1


def _preset_date_bounds_map() -> dict[str, dict[str, str]]:
    portfolio_index = _safe_load_json(DEFAULT_PORTFOLIO_ROOT / "portfolio_index.json", [])
    records = portfolio_index if isinstance(portfolio_index, list) else []
    rows = _safe_load_json(DEFAULT_JOBS_JSON, [])
    scraped_rows = rows if isinstance(rows, list) else []
    dates_by_preset: dict[str, set[str]] = {
        "resume_backlog": set(),
        "legacy_rereview": set(),
        "pdf_pass_backfill": set(),
    }

    for row in scraped_rows:
        if not isinstance(row, dict):
            continue
        value = _extract_date(row.get("publish_time", ""))
        if value:
            dates_by_preset["resume_backlog"].add(value)

    for record in records:
        if not isinstance(record, dict):
            continue
        value = _extract_date(record.get("publish_date", "") or record.get("publish_time", ""))
        if not value:
            continue
        if str(record.get("source_kind", "") or "") == "local_unified_pipeline":
            dates_by_preset["resume_backlog"].add(value)
        if str(record.get("source_kind", "") or "") != "local_unified_pipeline" and str(record.get("resume_md", "") or "").strip():
            dates_by_preset["legacy_rereview"].add(value)
        artifact_dir = str(record.get("artifact_dir", "") or "").strip()
        manifest_path = (
            Path(artifact_dir).expanduser() / "manifest.json"
            if artifact_dir
            else ROOT / "data" / "deliverables" / "resume_portfolio" / "by_company" / str(
                record.get("company_slug", "") or ""
            ) / value / str(record.get("job_id", "") or "") / "manifest.json"
        )
        if _portfolio_manifest_status(record) == "pass" and not _resume_pdf_exists(manifest_path, record):
            dates_by_preset["pdf_pass_backfill"].add(value)

    result: dict[str, dict[str, str]] = {}
    for preset_id, dates in dates_by_preset.items():
        ordered = sorted(dates)
        result[preset_id] = {"min": ordered[0], "max": ordered[-1]} if ordered else {"min": "", "max": ""}
    return result


def build_command_presets() -> list[dict[str, Any]]:
    global _PRESET_CACHE_SIGNATURE, _PRESET_CACHE
    signature = (_safe_mtime(DEFAULT_JOBS_JSON), _safe_mtime(DEFAULT_PORTFOLIO_ROOT / "portfolio_index.json"))
    if _PRESET_CACHE is not None and _PRESET_CACHE_SIGNATURE == signature:
        return [dict(item) for item in _PRESET_CACHE]

    python_bin = sys.executable
    rereview = str(ROOT / "rereview_resume_portfolio.py")
    backlog = str(ROOT / "resume_backlog_runner.py")
    pdf_backfill = str(ROOT / "portfolio_pdf_backfill.py")
    date_bounds = _preset_date_bounds_map()
    presets = [
        {
            "id": "resume_backlog",
            "title": "Resume Backlog Continuation",
            "description": "先补新岗位，再 rewrite 新链路非 pass，最后补 pass PDF。",
            "supports_filters": True,
            "date_bounds": date_bounds["resume_backlog"],
            "command": [
                python_bin,
                backlog,
                "--llm-transport",
                "cli",
            ],
        },
        {
            "id": "legacy_rereview",
            "title": "Legacy Rereview",
            "description": "只复审旧 pipeline 简历池，不包含 4 月 8 日后的新链路简历。",
            "supports_filters": True,
            "date_bounds": date_bounds["legacy_rereview"],
            "command": [
                python_bin,
                rereview,
                "--skip-rereviewed",
                "--source-scope",
                "legacy_only",
                "--llm-transport",
                "cli",
            ],
        },
        {
            "id": "pdf_pass_backfill",
            "title": "PDF Rebuild Missing",
            "description": "扫描 pass 且 PDF 文件缺失的简历，按当前统一编译链重建。",
            "supports_filters": True,
            "date_bounds": date_bounds["pdf_pass_backfill"],
            "command": [
                python_bin,
                pdf_backfill,
            ],
        },
    ]
    _PRESET_CACHE_SIGNATURE = signature
    _PRESET_CACHE = [dict(item) for item in presets]
    return presets


def _preset_by_id(preset_id: str) -> dict[str, Any]:
    for preset in build_command_presets():
        if preset["id"] == preset_id:
            return preset
    raise ValueError(f"Unknown preset: {preset_id}")


def _append_company_tiers(command: list[str], tiers: list[str]) -> list[str]:
    if not tiers:
        tiers = ["large"]
    normalized: list[str] = []
    for tier in tiers:
        value = str(tier or "").strip().lower()
        if value == "large":
            normalized.append("large")
        elif value == "mid":
            normalized.extend(["mid_large", "mid_small"])
        elif value == "small":
            normalized.append("small")
    seen: set[str] = set()
    deduped = [item for item in normalized if not (item in seen or seen.add(item))]
    for item in deduped:
        command.extend(["--company-tier", item])
    return command


def _append_date_filters(command: list[str], start_date: str, end_date: str) -> list[str]:
    start = str(start_date or "").strip()
    end = str(end_date or "").strip()
    if start and not end:
        command.extend(["--publish-date", start])
    elif start and end:
        command.extend(["--publish-date-from", start, "--publish-date-to", end])
    return command


def build_preset_command(preset_id: str, *, tiers: list[str] | None = None, start_date: str = "", end_date: str = "") -> list[str]:
    preset = _preset_by_id(preset_id)
    command = list(preset["command"])
    if preset.get("supports_filters"):
        command = _append_company_tiers(command, list(tiers or ["large"]))
        command = _append_date_filters(command, start_date, end_date)
    return command


def _with_injected_run_dir(command: list[str], label: str, run_id: str) -> tuple[list[str], str]:
    if "--run-dir" in command:
        try:
            run_dir = command[command.index("--run-dir") + 1]
        except IndexError:
            run_dir = ""
        return (command, run_dir)

    joined = " ".join(command)
    if (
        "pipeline.py all" not in joined
        and "pipeline.py resume" not in joined
        and "pipeline.py jobs" not in joined
        and "pipeline.py pdf" not in joined
        and "resume_backlog_runner.py" not in joined
        and "portfolio_pdf_backfill.py" not in joined
    ):
        return (command, "")

    timestamp = _now().strftime("%Y%m%d_%H%M%S")
    run_dir = ROOT / "runs" / f"{_slug(label)}_{timestamp}_{run_id[:8]}"
    updated = list(command) + ["--run-dir", str(run_dir)]
    return (updated, str(run_dir))


def _signal_process_group(pgid: int, sig: int) -> None:
    if pgid <= 0:
        return
    try:
        os.killpg(pgid, sig)
    except PermissionError:
        subprocess.run(
            ["kill", f"-{int(sig)}", f"-{pgid}"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except ProcessLookupError:
        return


def stop_process(*, pid: int | None = None, pgid: int | None = None) -> bool:
    if pgid:
        _signal_process_group(pgid, signal.SIGTERM)
        return True
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            return True
        except PermissionError:
            subprocess.run(
                ["kill", "-TERM", str(pid)],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except ProcessLookupError:
            return False
    return False


def spawn_managed_command(command: list[str], *, label: str, display_name: str, preset_id: str = "", metadata: dict[str, Any] | None = None) -> subprocess.Popen[str]:
    runner_cmd = [
        sys.executable,
        str(ROOT / "managed_run.py"),
        "--label",
        label,
        "--display-name",
        display_name,
        "--cwd",
        str(ROOT),
        "--preset-id",
        preset_id,
        "--metadata-json",
        json.dumps(metadata or {}, ensure_ascii=False),
        "--",
        *command,
    ]
    return subprocess.Popen(
        runner_cmd,
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
        start_new_session=True,
    )


def list_unmanaged_processes() -> list[dict[str, Any]]:
    try:
        result = subprocess.run(
            ["ps", "-ax", "-o", "pid=,etime=,command="],
            capture_output=True,
            text=True,
            check=False,
            timeout=1.5,
        )
    except Exception:
        return []

    managed_state = load_monitor_state()
    known_pids = {
        int(item.get(key, 0) or 0)
        for item in managed_state.get("processes", [])
        if isinstance(item, dict)
        for key in ("runner_pid", "child_pid")
    }
    rows: list[dict[str, Any]] = []
    for raw_line in (result.stdout or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split(None, 2)
        if len(parts) != 3:
            continue
        pid_text, elapsed, command = parts
        try:
            pid = int(pid_text)
        except ValueError:
            continue
        if pid in known_pids or pid == os.getpid():
            continue
        if "ps -ax -o pid=,etime=,command=" in command or "rg " in command:
            continue
        if not any(pattern in command for pattern in MONITORED_PS_PATTERNS):
            continue
        rows.append(
            {
                "id": f"unmanaged-{pid}",
                "source": "unmanaged",
                "display_name": command.split("pipeline.py")[-1].strip() if "pipeline.py" in command else command,
                "label": "External Process",
                "status": "running",
                "runner_pid": pid,
                "child_pid": pid,
                "elapsed": elapsed,
                "command": command,
                "effective_command": command,
                "started_at": "",
                "updated_at": _now_iso(),
                "log_tail": [],
                "progress": {},
            }
        )
    return rows


class ManagedRunner:
    def __init__(self, *, label: str, display_name: str, cwd: str, command: list[str], preset_id: str, metadata: dict[str, Any]) -> None:
        self.label = label
        self.display_name = display_name
        self.cwd = cwd
        self.original_command = list(command)
        self.preset_id = preset_id
        self.metadata = metadata
        self.run_id = uuid.uuid4().hex
        self.child: subprocess.Popen[str] | None = None
        self.stop_requested = False
        self.progress_stop = threading.Event()
        self.run_count = 0
        self.log_path = MANAGED_LOG_ROOT / f"{_slug(label)}_{_now().strftime('%Y%m%d_%H%M%S')}_{self.run_id[:8]}.log"
        self.current_run_dir = ""
        self.priority_input_path = PRIORITY_INPUT_ROOT / f"{self.run_id}.json"

    def _base_record(self) -> dict[str, Any]:
        return {
            "id": self.run_id,
            "label": self.label,
            "display_name": self.display_name,
            "preset_id": self.preset_id,
            "source": "managed",
            "status": "starting",
            "cwd": self.cwd,
            "command": self.original_command,
            "effective_command": self.original_command,
            "runner_pid": os.getpid(),
            "child_pid": 0,
            "pgid": os.getpgrp(),
            "started_at": _now_iso(),
            "updated_at": _now_iso(),
            "finished_at": "",
            "next_retry_at": "",
            "quota_kind": "",
            "last_error": "",
            "log_path": str(self.log_path),
            "log_tail": [],
            "run_count": 0,
            "progress": {},
            "metadata": self.metadata,
            "run_dir": "",
        }

    def _progress_loop(self) -> None:
        while not self.progress_stop.wait(3):
            if not self.current_run_dir:
                continue
            progress = compute_progress(self.original_command, self.current_run_dir)
            _patch_process(self.run_id, progress=progress, run_dir=self.current_run_dir)

    def _handle_stop_signal(self, signum: int, _frame: Any) -> None:
        self.stop_requested = True
        if self.child and self.child.poll() is None:
            try:
                os.killpg(os.getpgid(self.child.pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
        _patch_process(
            self.run_id,
            status="stopped",
            finished_at=_now_iso(),
            last_error=f"Stopped by signal {signum}",
        )
        raise SystemExit(128 + signum)

    def run(self) -> int:
        MANAGED_LOG_ROOT.mkdir(parents=True, exist_ok=True)
        PRIORITY_INPUT_ROOT.mkdir(parents=True, exist_ok=True)
        _upsert_process(self._base_record())
        signal.signal(signal.SIGTERM, self._handle_stop_signal)
        signal.signal(signal.SIGINT, self._handle_stop_signal)
        progress_thread = threading.Thread(target=self._progress_loop, daemon=True)
        progress_thread.start()

        exit_code = 0
        try:
            while True:
                self.run_count += 1
                effective_command, run_dir = _with_injected_run_dir(self.original_command, self.label, self.run_id)
                self.current_run_dir = run_dir
                _patch_process(
                    self.run_id,
                    status="running",
                    effective_command=effective_command,
                    next_retry_at="",
                    quota_kind="",
                    run_count=self.run_count,
                    run_dir=run_dir,
                    progress=compute_progress(self.original_command, run_dir),
                )

                with self.log_path.open("a", encoding="utf-8") as log_file:
                    log_file.write(f"\n===== run #{self.run_count} start {_now_iso()} =====\n")
                    log_file.write("command: " + shlex.join(effective_command) + "\n")
                    log_file.flush()

                    launch_env = {**os.environ, "MANAGED_RUN_ACTIVE": "1"}
                    queue_payload = load_waiting_retry_queue(self.run_id) or {}
                    queue_items = queue_payload.get("items", []) if isinstance(queue_payload, dict) else []
                    if queue_items:
                        priority_job_ids = [
                            str(item.get("job_id", "") or "").strip()
                            for item in queue_items
                            if isinstance(item, dict) and str(item.get("job_id", "") or "").strip()
                        ]
                        self.priority_input_path.write_text(
                            json.dumps({"job_ids": priority_job_ids}, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8",
                        )
                        launch_env[PRIORITY_JOB_IDS_ENV] = str(self.priority_input_path)
                        merge_process_metadata(
                            self.run_id,
                            {
                                "waiting_queue_count": len(priority_job_ids),
                                "waiting_queue_updated_at": str(queue_payload.get("updated_at", "") or ""),
                                "waiting_queue_preview": queue_items[:5],
                            },
                        )
                    elif self.priority_input_path.exists():
                        self.priority_input_path.unlink(missing_ok=True)

                    self.child = subprocess.Popen(
                        effective_command,
                        cwd=self.cwd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        env=launch_env,
                    )
                    _patch_process(self.run_id, child_pid=self.child.pid)

                    output_lines: list[str] = []
                    assert self.child.stdout is not None
                    for line in self.child.stdout:
                        log_file.write(line)
                        log_file.flush()
                        output_lines.append(line.rstrip())
                        _append_log_tail(self.run_id, line.rstrip())
                        _patch_process(self.run_id, progress=compute_progress(self.original_command, run_dir), run_dir=run_dir)

                    self.child.wait()
                    exit_code = int(self.child.returncode or 0)
                    output_text = "\n".join(output_lines)
                    quota_signal = classify_quota_error(output_text)

                    if self.stop_requested:
                        clear_waiting_retry_queue(self.run_id)
                        _patch_process(self.run_id, status="stopped", finished_at=_now_iso(), exit_code=exit_code)
                        return exit_code

                    if exit_code == 0:
                        clear_waiting_retry_queue(self.run_id)
                        _patch_process(
                            self.run_id,
                            status="completed",
                            finished_at=_now_iso(),
                            exit_code=0,
                            progress=compute_progress(self.original_command, run_dir),
                        )
                        return 0

                    if quota_signal is None:
                        clear_waiting_retry_queue(self.run_id)
                        _patch_process(
                            self.run_id,
                            status="failed",
                            finished_at=_now_iso(),
                            exit_code=exit_code,
                            last_error=output_text[-4000:],
                            progress=compute_progress(self.original_command, run_dir),
                        )
                        return exit_code

                    if quota_signal.kind == "weekly":
                        clear_waiting_retry_queue(self.run_id)
                        _patch_process(
                            self.run_id,
                            status="quota_weekly_exit",
                            finished_at=_now_iso(),
                            exit_code=exit_code,
                            quota_kind="weekly",
                            last_error=quota_signal.reason,
                            progress=compute_progress(self.original_command, run_dir),
                        )
                        return exit_code

                    next_retry_at = quota_signal.next_retry_at
                    if next_retry_at is None:
                        _patch_process(
                            self.run_id,
                            status="quota_wait_unknown",
                            finished_at=_now_iso(),
                            exit_code=exit_code,
                            quota_kind="short_window",
                            last_error=quota_signal.reason,
                            progress=compute_progress(self.original_command, run_dir),
                        )
                        return exit_code

                    _patch_process(
                        self.run_id,
                        status="waiting_retry",
                        quota_kind="short_window",
                        next_retry_at=next_retry_at.isoformat(timespec="seconds"),
                        last_error=quota_signal.reason,
                        exit_code=exit_code,
                        progress=compute_progress(self.original_command, run_dir),
                    )

                    while _now() < next_retry_at:
                        remaining = next_retry_at - _now()
                        if remaining <= timedelta(seconds=0):
                            break
                        sleep_for = min(30, max(1, int(remaining.total_seconds())))
                        time.sleep(sleep_for)
                        _patch_process(
                            self.run_id,
                            status="waiting_retry",
                            next_retry_at=next_retry_at.isoformat(timespec="seconds"),
                            progress=compute_progress(self.original_command, run_dir),
                        )
                        if self.stop_requested:
                            clear_waiting_retry_queue(self.run_id)
                            _patch_process(self.run_id, status="stopped", finished_at=_now_iso())
                            return exit_code
        except Exception as exc:  # noqa: BLE001
            clear_waiting_retry_queue(self.run_id)
            _patch_process(
                self.run_id,
                status="failed",
                finished_at=_now_iso(),
                last_error=str(exc),
                progress=compute_progress(self.original_command, self.current_run_dir),
            )
            raise
        finally:
            self.progress_stop.set()
            progress_thread.join(timeout=1)
            if self.priority_input_path.exists():
                self.priority_input_path.unlink(missing_ok=True)

        return exit_code


def main() -> None:
    parser = argparse.ArgumentParser(description="Managed runner with quota-aware retry + monitor state.")
    parser.add_argument("--label", default="managed_run")
    parser.add_argument("--display-name", default="Managed Run")
    parser.add_argument("--cwd", default=str(ROOT))
    parser.add_argument("--preset-id", default="")
    parser.add_argument("--metadata-json", default="{}")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command = list(args.command)
    while command and command[0] == "--":
        command = command[1:]
    if not command:
        raise SystemExit("missing child command")

    try:
        metadata = json.loads(args.metadata_json)
    except json.JSONDecodeError:
        metadata = {}
    if not isinstance(metadata, dict):
        metadata = {}

    runner = ManagedRunner(
        label=args.label,
        display_name=args.display_name,
        cwd=args.cwd,
        command=command,
        preset_id=args.preset_id,
        metadata=metadata,
    )
    raise SystemExit(runner.run())


if __name__ == "__main__":
    main()
