from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from runtime.job_webapp.main import ROOT, STATE_PATH

from .models import DetectionResult, JobAvailability


BACKFILL_STATE_PATH = ROOT / "state" / "job_status_backfill.json"
BACKFILL_REPORTS_DIR = ROOT / "output" / "backfill_status"


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp_path.replace(path)


def load_backfill_cache(*, path: Path | None = None) -> dict[str, dict[str, Any]]:
    target = path or BACKFILL_STATE_PATH
    payload = _load_json(target, {})
    return payload if isinstance(payload, dict) else {}


def _status_value(payload: dict[str, Any]) -> str:
    return str(payload.get("status", "") or "").strip().lower()


def _is_terminal_status(status: str) -> bool:
    return status in {"open", "closed"}


def merge_backfill_results(
    existing: dict[str, dict[str, Any]],
    results: list[DetectionResult],
    *,
    allow_unknown_overwrite_terminal: bool = False,
) -> dict[str, dict[str, Any]]:
    merged = dict(existing)
    for result in results:
        previous = merged.get(result.job_id, {})
        previous_status = _status_value(previous if isinstance(previous, dict) else {})
        next_payload = result.to_dict()
        next_status = _status_value(next_payload)
        if (
            next_status == "unknown"
            and _is_terminal_status(previous_status)
            and not allow_unknown_overwrite_terminal
        ):
            continue
        merged[result.job_id] = next_payload
    return merged


def write_backfill_cache(
    existing: dict[str, dict[str, Any]],
    results: list[DetectionResult],
    *,
    path: Path | None = None,
    allow_unknown_overwrite_terminal: bool = False,
) -> dict[str, dict[str, Any]]:
    target = path or BACKFILL_STATE_PATH
    merged = merge_backfill_results(
        existing,
        results,
        allow_unknown_overwrite_terminal=allow_unknown_overwrite_terminal,
    )
    _write_json(target, merged)
    return merged


def apply_results_to_job_app_state(
    results: list[DetectionResult],
    *,
    dry_run: bool,
    state_path: Path | None = None,
) -> dict[str, dict[str, Any]]:
    target = state_path or STATE_PATH
    existing = _load_json(target, {})
    state = existing if isinstance(existing, dict) else {}
    for result in results:
        record = state.get(result.job_id, {})
        if not isinstance(record, dict):
            record = {}
        if result.status == JobAvailability.CLOSED:
            state[result.job_id] = {
                "applied": bool(record.get("applied", False)),
                "abandoned": bool(record.get("abandoned", False)),
                "closed": True,
                "updated_at": result.checked_at,
            }
            continue
        if result.status == JobAvailability.OPEN and result.job_id in state:
            updated = {
                "applied": bool(record.get("applied", False)),
                "abandoned": bool(record.get("abandoned", False)),
                "closed": False,
                "updated_at": result.checked_at,
            }
            if updated["applied"] or updated["abandoned"] or updated["closed"]:
                state[result.job_id] = updated
            else:
                state.pop(result.job_id, None)
    if not dry_run:
        _write_json(target, state)
    return state


def write_backfill_report(
    payload: dict[str, Any],
    *,
    report_path: Path | None = None,
    report_dir: Path | None = None,
) -> Path:
    target = report_path
    if target is None:
        target_dir = report_dir or BACKFILL_REPORTS_DIR
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = target_dir / f"backfill_status_{ts}.json"
    _write_json(target, payload)
    return target


def write_summary(path: Path, payload: dict[str, Any]) -> None:
    _write_json(path, payload)
