from __future__ import annotations

import argparse
import json
import mimetypes
import os
import signal
import subprocess
import sys
import threading
import webbrowser
from datetime import date, datetime, timedelta
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from managed_run import (  # noqa: E402
    build_command_presets,
    build_preset_command,
    compute_progress,
    load_monitor_state,
    list_unmanaged_processes,
    spawn_managed_command,
    stop_process,
)
from runtime.job_webapp.prompt_library import (  # noqa: E402
    build_match_pipe_prompt_library,
    save_match_pipe_paragraph_overrides,
    save_match_pipe_prompt_overrides,
)
from runtime.job_webapp.prompt_review_compiler import (  # noqa: E402
    regenerate_prompt_review,
)
from runtime.job_webapp.prompt_review_roundtrip import (  # noqa: E402
    run_prompt_review_roundtrip,
)
from runtime.job_webapp.prompt_review_writeback import (  # noqa: E402
    run_writeback,
)
from runtime.job_webapp.prompt_review_store import (  # noqa: E402
    get_prompt_review_ambiguities,
    get_prompt_review_conflict,
    get_prompt_review_coverage,
    get_prompt_review_payload,
    get_prompt_review_roundtrip_report,
    list_prompt_review_revisions,
    restore_prompt_review_revision,
    save_prompt_review_edit,
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
PROMPT_REVIEW_DIR = ROOT / "prompt_review"
JOBS_CATALOG_PATH = ROOT / "data" / "job_tracker" / "jobs_catalog.json"
PORTFOLIO_INDEX_PATH = ROOT / "data" / "deliverables" / "resume_portfolio" / "portfolio_index.json"
STATE_PATH = ROOT / "state" / "job_app_status.json"
YOE_CACHE_PATH = ROOT / "state" / "job_app_yoe_cache.json"
BACKFILL_STATUS_PATH = ROOT / "state" / "job_status_backfill.json"
SINGLE_JOB_ACTION_RUNNER = ROOT / "single_job_action_runner.py"

DATE_TIME_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
)


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


def _parse_timestamp(raw: str) -> datetime | None:
    text = str(raw or "").strip()
    if not text:
        return None
    for fmt in DATE_TIME_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def _safe_mtime(path: Path) -> int:
    try:
        return path.stat().st_mtime_ns
    except FileNotFoundError:
        return -1


def _display_timestamp(raw: str) -> str:
    parsed = _parse_timestamp(raw)
    if parsed is None:
        return str(raw or "").strip()
    return parsed.strftime("%Y-%m-%d %H:%M")


def _date_only(raw: str) -> str:
    parsed = _parse_timestamp(raw)
    if parsed is not None:
        return parsed.strftime("%Y-%m-%d")
    text = str(raw or "").strip()
    return text[:10] if len(text) >= 10 else text


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _infer_yoe_value(row: dict[str, Any]) -> int | None:
    raw = str(row.get("min_years_experience", "") or "").strip()
    if raw:
        try:
            return max(0, int(float(raw)))
        except ValueError:
            pass

    title_text = " ".join(
        str(row.get(key, "") or "").lower()
        for key in ("job_title", "job_nlp_title", "job_seniority")
    )
    if any(marker in title_text for marker in ("new grad", "new graduate", "graduate", "entry", "entry level", "junior")):
        return 0
    return None


def _yoe_label(value: int | None) -> str:
    if value is None:
        return "Unknown"
    return str(min(value, 5))


def _normalize_yoe_value(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return max(0, min(int(value), 5))
    except (TypeError, ValueError):
        return None


def _normalize_apply_url_status(value: Any) -> str:
    status = str(value or "").strip().lower()
    if status in {"open", "closed", "unknown"}:
        return status
    return "unknown"


_COMPANY_SIZE_TIER: dict[str, str] = {
    "10001+ employees": "大厂(10000+)",
    "5001-10000 employees": "大厂(10000+)",
    "1001-5000 employees": "中厂(1001-5000)",
    "501-1000 employees": "中厂(501-1000)",
    "201-500 employees": "小厂(≤500)",
    "51-200 employees": "小厂(≤500)",
    "11-50 employees": "小厂(≤500)",
    "2-10 employees": "小厂(≤500)",
}


def _company_size_label(row: dict[str, Any]) -> str:
    raw = str(row.get("company_size", "") or "").strip()
    return _COMPANY_SIZE_TIER.get(raw, "未知")


def _company_size_value(*rows: dict[str, Any] | None) -> str:
    for row in rows:
        if not isinstance(row, dict):
            continue
        raw = str(row.get("company_size", "") or "").strip()
        if raw:
            return raw
    return ""


def _salary_floor_value(*rows: dict[str, Any] | None) -> float:
    for row in rows:
        if not isinstance(row, dict):
            continue
        for key in ("min_salary", "max_salary"):
            raw = row.get(key)
            if raw in (None, ""):
                continue
            try:
                val = float(raw)
            except (TypeError, ValueError):
                continue
            if val > 0:
                return val
    return 0.0


def _salary_label(row: dict[str, Any]) -> str:
    try:
        val = float(row.get("min_salary", 0) or 0)
    except (TypeError, ValueError):
        val = 0.0
    if val >= 200_000:
        return "≥200K"
    if val >= 150_000:
        return "150-200K"
    if val >= 100_000:
        return "100-150K"
    if val > 0:
        return "<100K"
    return "未标薪资"


def _infer_title_class(row: dict[str, Any]) -> str:
    title = " ".join(
        str(row.get(key, "") or "")
        for key in ("job_title", "job_nlp_title", "taxonomy_v3")
    ).lower()

    if any(marker in title for marker in ("product manager", "program manager", "project manager", "technical program manager", "tpm")):
        return "PM"

    if any(
        marker in title
        for marker in (
            "data engineer",
            "data scientist",
            "data analyst",
            "analytics",
            "business intelligence",
            "bi engineer",
            "bi analyst",
            "data engineering",
            "mlops",
        )
    ):
        return "Data"

    if any(
        marker in title
        for marker in (
            "machine learning",
            "ai engineer",
            "artificial intelligence",
            "applied scientist",
            "research scientist",
            "genai",
            "llm",
            " ai ",
            " ai/",
            "/ai",
            " ml ",
            " ml/",
            "/ml",
            "ai/ml",
        )
    ):
        return "ML/AI"

    if any(
        marker in title
        for marker in (
            "software engineer",
            "software developer",
            "developer",
            "backend engineer",
            "frontend",
            "fullstack",
            "full-stack",
            "engineer",
        )
    ):
        return "SWE"

    return "Other"


def _resume_dir_from_portfolio(record: dict[str, Any]) -> str:
    artifact_dir = str(record.get("artifact_dir", "") or "").strip()
    if artifact_dir:
        return artifact_dir
    resume_md = str(record.get("resume_md", "") or "").strip()
    if resume_md:
        return str(Path(resume_md).expanduser().resolve().parent)
    return ""


def _seed_label(record: dict[str, Any] | None) -> str:
    if not record:
        return "No resume generated"
    label = str(record.get("seed_label", "") or "").strip()
    if label:
        return label
    return "Generated resume (seed label missing)"


def _is_generation_blocked_company(company_name: str) -> bool:
    return False


def _normalized_review_status(record: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(record, dict):
        return {
            "status": "无简历",
            "score": 0.0,
            "pipeline_state": "none",
            "badge_kind": "none",
            "display_value": "无简历",
            "raw_verdict": "",
        }

    rereview_version = str(record.get("rereview_version", "") or "").strip()
    source_kind = str(record.get("source_kind", "") or "").strip()
    review_payload = record.get("review")
    verdict = ""
    final_score = 0.0
    if rereview_version:
        verdict = str(record.get("review_verdict", "") or "").strip().lower()
        try:
            final_score = float(record.get("review_final_score", 0) or 0)
        except (TypeError, ValueError):
            final_score = 0.0
    elif isinstance(review_payload, dict):
        verdict = str(review_payload.get("verdict", "") or "").strip().lower()
        if not verdict and bool(review_payload.get("passed", False)):
            verdict = "pass"
        if not verdict:
            overall_verdict = str(review_payload.get("overall_verdict", "") or "").strip().lower()
            if overall_verdict == "pass":
                verdict = "pass"
            elif overall_verdict == "fail":
                verdict = "pending"
        try:
            final_score = float(
                review_payload.get("final_score", review_payload.get("weighted_score", 0)) or 0
            )
        except (TypeError, ValueError):
            final_score = 0.0

    artifact_dir = str(record.get("artifact_dir", "") or "").strip()
    has_resume = bool(artifact_dir or str(record.get("resume_md", "") or "").strip())
    if not has_resume:
        return {
            "status": "无简历",
            "score": 0.0,
            "pipeline_state": "none",
            "badge_kind": "none",
            "display_value": "无简历",
            "raw_verdict": "",
        }
    if not verdict:
        return {
            "status": "未review",
            "score": 0.0,
            "pipeline_state": "unreviewed",
            "badge_kind": "pending",
            "display_value": "未review",
            "raw_verdict": "",
        }
    if verdict == "pass":
        return {
            "status": "pass",
            "score": final_score,
            "pipeline_state": "pass",
            "badge_kind": "pass",
            "display_value": f"{final_score:.1f}",
            "raw_verdict": verdict,
        }
    if verdict == "reject":
        return {
            "status": "reject",
            "score": final_score,
            "pipeline_state": "reject",
            "badge_kind": "fail",
            "display_value": f"Reject {final_score:.1f}" if final_score > 0 else "Reject",
            "raw_verdict": verdict,
        }
    bucket = "conditional_pass" if final_score >= 88.0 else "fail"
    return {
        "status": bucket,
        "score": final_score,
        "pipeline_state": "pending",
        "badge_kind": "cond" if bucket == "conditional_pass" else "fail",
        "display_value": f"{final_score:.1f}" if final_score > 0 else "0.0",
        "raw_verdict": verdict,
    }


def _read_sheet_row(record: dict[str, Any]) -> dict[str, Any]:
    artifact_dir = str(record.get("artifact_dir", "") or "").strip()
    if artifact_dir:
        sheet_row_path = Path(artifact_dir) / "sheet_row.json"
        payload = _load_json(sheet_row_path, {})
        if isinstance(payload, dict):
            return payload
    return {}


def _normalized_row_value(*values: Any) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _job_date(job: dict[str, Any]) -> date | None:
    for key in ("discovered_at", "discovered_date", "publish_at", "publish_date"):
        parsed = _parse_timestamp(str(job.get(key, "") or "").strip())
        if parsed is not None:
            return parsed.date()
    return None


def _portfolio_manifest_exists(job_id: str) -> bool:
    if not job_id:
        return False
    root = PORTFOLIO_INDEX_PATH.parent / "by_company"
    pattern = f"*/*/{job_id}/manifest.json"
    return any(root.glob(pattern))


def _collect_resume_run_details(run_dir: str, command_text: str) -> dict[str, Any]:
    if not run_dir:
        return {}
    target = Path(run_dir)
    if not target.exists():
        return {}

    resume_root = target / "resume_step" if "pipeline.py all" in command_text else target
    accepted_path = resume_root / "accepted_jobs.json"
    jobs_root = resume_root / "jobs"
    if not accepted_path.exists() or not jobs_root.exists():
        return {}

    accepted_rows = _load_json(accepted_path, [])
    if not isinstance(accepted_rows, list):
        return {}

    status_rows: list[dict[str, Any]] = []
    latest_activity: list[dict[str, Any]] = []
    current_job: dict[str, Any] | None = None
    max_staged_index = 0

    for index, item in enumerate(accepted_rows, start=1):
        if not isinstance(item, dict):
            continue
        job_id = str(item.get("job_id", "") or "").strip()
        company_name = str(item.get("company_name", "") or "").strip()
        title = str(item.get("title", "") or "").strip()
        publish_time = str(item.get("publish_time", "") or "").strip()
        route_mode = str(item.get("route_mode", "") or "").strip()
        job_dir = jobs_root / job_id
        state = "not_started"
        verdict = ""
        final_score = 0.0
        latest_rel = ""
        latest_mtime = 0.0

        if job_dir.exists():
            max_staged_index = index
            state = "staged_only"
            files = [path for path in job_dir.rglob("*") if path.is_file()]
            if files:
                latest_file = max(files, key=lambda path: path.stat().st_mtime)
                latest_rel = str(latest_file.relative_to(job_dir))
                latest_mtime = latest_file.stat().st_mtime
                latest_activity.append(
                    {
                        "job_id": job_id,
                        "company_name": company_name,
                        "title": title,
                        "path": latest_rel,
                        "updated_at": datetime.fromtimestamp(latest_mtime).isoformat(timespec="seconds"),
                        "mtime": latest_mtime,
                    }
                )

            generation_dir = job_dir / "generation"
            if generation_dir.exists():
                review_files = sorted(generation_dir.glob("*_review.json"))
                if review_files:
                    state = "reviewed"
                    review_payload = _load_json(review_files[-1], {})
                    if isinstance(review_payload, dict):
                        verdict = str(review_payload.get("verdict", "") or "").strip()
                        try:
                            final_score = float(review_payload.get("final_score", 0) or 0)
                        except (TypeError, ValueError):
                            final_score = 0.0
                else:
                    state = "generating"

        artifact_exists = _portfolio_manifest_exists(job_id)
        row = {
            "index": index,
            "job_id": job_id,
            "company_name": company_name,
            "title": title,
            "publish_time": publish_time,
            "route_mode": route_mode,
            "state": state,
            "verdict": verdict,
            "final_score": final_score,
            "artifact_exists": artifact_exists,
            "latest_path": latest_rel,
            "latest_mtime": latest_mtime,
        }
        status_rows.append(row)

        if state == "generating":
            if current_job is None or latest_mtime > float(current_job.get("latest_mtime", 0) or 0):
                current_job = row

    if current_job is None and max_staged_index > 0 and max_staged_index <= len(status_rows):
        current_job = status_rows[max_staged_index - 1]

    current_index = int(current_job.get("index", 1) or 1) if current_job else 1
    queue_preview = status_rows[current_index - 1 : current_index + 4]
    reviewed_count = sum(1 for row in status_rows if row["state"] == "reviewed")
    published_count = sum(1 for row in status_rows if row["artifact_exists"])
    pass_count = sum(1 for row in status_rows if row["verdict"] == "pass")

    detail_lines: list[str] = []
    if current_job:
        detail_lines.append(
            f"[live] current #{current_job['index']} {current_job['company_name']} | {current_job['title']} | {current_job['state']}"
        )
        if current_job.get("latest_path"):
            detail_lines.append(f"[live] current file {current_job['latest_path']}")
    detail_lines.append(
        f"[live] published {published_count}/{len(status_rows)} | reviewed {reviewed_count}/{len(status_rows)} | pass {pass_count}"
    )
    for item in queue_preview[:5]:
        detail_lines.append(
            f"[queue] #{item['index']} {item['company_name']} | {item['title']} | {item['state']} | {item['route_mode']}"
        )
    for item in sorted(latest_activity, key=lambda row: row.get("mtime", 0), reverse=True)[:5]:
        detail_lines.append(
            f"[activity] {item['updated_at']} | {item['company_name']} | {item['title']} | {item['path']}"
        )

    return {
        "current_job": current_job or {},
        "queue_preview": queue_preview[:5],
        "recent_activity": sorted(latest_activity, key=lambda row: row.get("mtime", 0), reverse=True)[:10],
        "reviewed_count": reviewed_count,
        "published_count": published_count,
        "pass_count": pass_count,
        "detail_lines": detail_lines,
    }


class JobAppStore:
    def __init__(self) -> None:
        self._state_lock = threading.Lock()
        self._catalog_lock = threading.Lock()
        self._process_lock = threading.Lock()
        self._catalog_signature: tuple[int, int] | None = None
        self._catalog_jobs: list[dict[str, Any]] = []

    def current_job_ids(self) -> set[str]:
        return {
            str(job.get("job_id", "") or "").strip()
            for job in self.base_jobs_catalog()
            if str(job.get("job_id", "") or "").strip()
        }

    def load_status_map(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(STATE_PATH, {})
        if not isinstance(payload, dict):
            return {}
        normalized: dict[str, dict[str, Any]] = {}
        for job_id, value in payload.items():
            if not isinstance(value, dict):
                continue
            normalized[str(job_id)] = {
                "applied": bool(value.get("applied", False)),
                "abandoned": bool(value.get("abandoned", False)),
                "closed": bool(value.get("closed", False)),
                "updated_at": str(value.get("updated_at", "") or ""),
            }
        return normalized

    def load_yoe_cache(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(YOE_CACHE_PATH, {})
        if not isinstance(payload, dict):
            return {}
        normalized: dict[str, dict[str, Any]] = {}
        for job_id, value in payload.items():
            if not isinstance(value, dict):
                continue
            yoe_value = _normalize_yoe_value(value.get("yoe_value"))
            if yoe_value is None:
                continue
            normalized[str(job_id)] = {
                "yoe_value": yoe_value,
                "source": str(value.get("source", "") or "").strip(),
                "confidence": float(value.get("confidence", 0) or 0),
                "updated_at": str(value.get("updated_at", "") or "").strip(),
            }
        return normalized

    def load_backfill_status_map(self) -> dict[str, dict[str, Any]]:
        payload = _load_json(BACKFILL_STATUS_PATH, {})
        if not isinstance(payload, dict):
            return {}
        normalized: dict[str, dict[str, Any]] = {}
        for job_id, value in payload.items():
            if not isinstance(value, dict):
                continue
            normalized[str(job_id)] = {
                "status": _normalize_apply_url_status(value.get("status")),
                "updated_at": str(value.get("checked_at", "") or value.get("updated_at", "") or "").strip(),
            }
        return normalized

    def base_jobs_catalog(self) -> list[dict[str, Any]]:
        signature = (_safe_mtime(JOBS_CATALOG_PATH), _safe_mtime(PORTFOLIO_INDEX_PATH))
        with self._catalog_lock:
            if self._catalog_signature == signature and self._catalog_jobs:
                return self._catalog_jobs

            catalog_rows = _load_json(JOBS_CATALOG_PATH, [])
            portfolio_rows = _load_json(PORTFOLIO_INDEX_PATH, [])

            catalog_by_job_id = {
                str(row.get("job_id", "") or "").strip(): row
                for row in catalog_rows
                if isinstance(row, dict) and str(row.get("job_id", "") or "").strip()
            }
            portfolio_by_job_id = {
                str(record.get("job_id", "") or "").strip(): record
                for record in portfolio_rows
                if isinstance(record, dict) and str(record.get("job_id", "") or "").strip()
            }

            jobs_by_id: dict[str, dict[str, Any]] = {}

            for job_id, portfolio_record in portfolio_by_job_id.items():
                sheet_row = _read_sheet_row(portfolio_record)
                catalog_row = catalog_by_job_id.get(job_id, {})
                merged_row = dict(sheet_row)
                merged_row.update(catalog_row)

                yoe_value = _infer_yoe_value(merged_row or sheet_row)
                discovered_raw = _normalized_row_value(
                    merged_row.get("discovered_date"),
                    sheet_row.get("discovered_date"),
                )
                publish_raw = _normalized_row_value(
                    merged_row.get("publish_time"),
                    sheet_row.get("publish_time"),
                    portfolio_record.get("publish_time"),
                )
                resume_dir = _resume_dir_from_portfolio(portfolio_record)

                review_status = _normalized_review_status(portfolio_record)
                company_name = _normalized_row_value(
                    merged_row.get("company_name"),
                    sheet_row.get("company_name"),
                    portfolio_record.get("company_name"),
                )

                company_size = _company_size_value(merged_row, sheet_row, portfolio_record)
                salary_floor = _salary_floor_value(merged_row, sheet_row, portfolio_record)
                jobs_by_id[job_id] = {
                    "job_id": job_id,
                    "company_name": company_name,
                    "title": _normalized_row_value(
                        merged_row.get("job_title"),
                        merged_row.get("job_nlp_title"),
                        sheet_row.get("job_title"),
                        portfolio_record.get("title"),
                    ),
                    "title_class": _infer_title_class(merged_row or sheet_row or portfolio_record),
                    "company_size": company_size,
                    "company_size_label": _company_size_label({"company_size": company_size}),
                    "min_salary": salary_floor,
                    "salary_label": _salary_label({"min_salary": salary_floor}),
                    "yoe_value": yoe_value,
                    "yoe_label": _yoe_label(yoe_value),
                    "discovered_at": _display_timestamp(discovered_raw),
                    "discovered_date": _date_only(discovered_raw),
                    "publish_at": _display_timestamp(publish_raw),
                    "publish_date": _date_only(publish_raw),
                    "apply_url": _normalized_row_value(
                        merged_row.get("apply_link"),
                        sheet_row.get("apply_link"),
                        portfolio_record.get("apply_link"),
                    ),
                    "resume_dir": resume_dir,
                    "resume_dir_exists": bool(resume_dir and Path(resume_dir).exists()),
                    "seed_label": _seed_label(portfolio_record),
                    "has_generated_resume": bool(resume_dir),
                    "source_scope": "both" if catalog_row else "portfolio_history",
                    "review_status": review_status["status"],
                    "review_final_score": review_status["score"],
                    "review_pipeline_state": review_status["pipeline_state"],
                    "review_badge_kind": review_status["badge_kind"],
                    "review_display_value": review_status["display_value"],
                    "review_raw_verdict": review_status["raw_verdict"],
                    "company_generation_blocked": _is_generation_blocked_company(company_name),
                }

            for job_id, catalog_row in catalog_by_job_id.items():
                if job_id in jobs_by_id:
                    continue

                yoe_value = _infer_yoe_value(catalog_row)
                discovered_raw = _normalized_row_value(catalog_row.get("discovered_date"))
                publish_raw = _normalized_row_value(catalog_row.get("publish_time"))
                company_size = _company_size_value(catalog_row)
                salary_floor = _salary_floor_value(catalog_row)

                jobs_by_id[job_id] = {
                    "job_id": job_id,
                    "company_name": _normalized_row_value(catalog_row.get("company_name")),
                    "title": _normalized_row_value(catalog_row.get("job_title"), catalog_row.get("job_nlp_title")),
                    "title_class": _infer_title_class(catalog_row),
                    "company_size": company_size,
                    "company_size_label": _company_size_label({"company_size": company_size}),
                    "min_salary": salary_floor,
                    "salary_label": _salary_label({"min_salary": salary_floor}),
                    "yoe_value": yoe_value,
                    "yoe_label": _yoe_label(yoe_value),
                    "discovered_at": _display_timestamp(discovered_raw),
                    "discovered_date": _date_only(discovered_raw),
                    "publish_at": _display_timestamp(publish_raw),
                    "publish_date": _date_only(publish_raw),
                    "apply_url": _normalized_row_value(catalog_row.get("apply_link")),
                    "resume_dir": "",
                    "resume_dir_exists": False,
                    "seed_label": "No resume generated",
                    "has_generated_resume": False,
                    "source_scope": "catalog_only",
                    "review_status": "无简历",
                    "review_final_score": 0,
                    "review_pipeline_state": "none",
                    "review_badge_kind": "none",
                    "review_display_value": "无简历",
                    "review_raw_verdict": "",
                    "company_generation_blocked": _is_generation_blocked_company(
                        _normalized_row_value(catalog_row.get("company_name"))
                    ),
                }

            jobs = list(jobs_by_id.values())
            jobs.sort(
                key=lambda item: (
                    _parse_timestamp(item["discovered_at"]) or datetime.min,
                    _parse_timestamp(item["publish_at"]) or datetime.min,
                ),
                reverse=True,
            )
            self._catalog_signature = signature
            self._catalog_jobs = jobs
            return self._catalog_jobs

    def update_status(self, job_id: str, applied: bool, abandoned: bool, closed: bool) -> dict[str, Any]:
        normalized_job_id = str(job_id or "").strip()
        if not normalized_job_id:
            raise ValueError("job_id is required")
        if normalized_job_id not in self.current_job_ids():
            raise ValueError(f"job_id is not in the current job pool: {normalized_job_id}")

        status = {
            "applied": bool(applied),
            "abandoned": bool(abandoned),
            "closed": bool(closed),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }

        if status["applied"] and status["abandoned"]:
            raise ValueError("applied and abandoned cannot both be true")

        with self._state_lock:
            state = self.load_status_map()
            if status["applied"] or status["abandoned"] or status["closed"]:
                state[normalized_job_id] = status
            else:
                state.pop(normalized_job_id, None)
            _write_json(STATE_PATH, state)
        return status

    def build_jobs_payload(self) -> dict[str, Any]:
        status_map = self.load_status_map()
        yoe_cache = self.load_yoe_cache()
        backfill_status_map = self.load_backfill_status_map()
        jobs: list[dict[str, Any]] = []
        for base_job in self.base_jobs_catalog():
            job_id = str(base_job.get("job_id", "") or "").strip()
            status = status_map.get(
                job_id,
                {"applied": False, "abandoned": False, "closed": False, "updated_at": ""},
            )
            backfill_status = backfill_status_map.get(job_id, {"status": "unknown", "updated_at": ""})
            cached_yoe = yoe_cache.get(job_id, {})
            display_yoe_value = base_job.get("yoe_value")
            display_yoe_source = "original"
            if display_yoe_value is None and cached_yoe:
                display_yoe_value = cached_yoe.get("yoe_value")
                display_yoe_source = str(cached_yoe.get("source", "") or "cache")
            apply_url_status = _normalize_apply_url_status(backfill_status.get("status", "unknown"))
            if bool(status.get("closed", False)):
                apply_url_status = "closed"
            jobs.append(
                {
                    **base_job,
                    "yoe_value": display_yoe_value,
                    "yoe_label": _yoe_label(display_yoe_value),
                    "yoe_source": display_yoe_source,
                    "yoe_confidence": float(cached_yoe.get("confidence", 0) or 0),
                    "applied": bool(status.get("applied", False)),
                    "abandoned": bool(status.get("abandoned", False)),
                    "closed": bool(status.get("closed", False)),
                    "apply_url_status": apply_url_status,
                    "apply_url_status_updated_at": str(backfill_status.get("updated_at", "") or ""),
                    "processed": bool(
                        status.get("applied", False)
                        or status.get("abandoned", False)
                        or status.get("closed", False)
                    ),
                    "review_action": (
                        "generate"
                        if base_job.get("review_status") == "无简历"
                        else "rewrite"
                        if base_job.get("review_pipeline_state") == "pending"
                        else ""
                    ),
                    "review_action_label": (
                        "生成"
                        if base_job.get("review_status") == "无简历"
                        else "重写"
                        if base_job.get("review_pipeline_state") == "pending"
                        else ""
                    ),
                }
            )

        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())

        return {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "jobs": jobs,
            "meta": {
                "total_jobs": len(jobs),
                "generated_resume_jobs": sum(1 for job in jobs if job["has_generated_resume"]),
                "review_passed_jobs": sum(1 for job in jobs if job.get("review_status") == "pass"),
                "processed_jobs": sum(1 for job in jobs if job["processed"]),
                "applied_jobs": sum(1 for job in jobs if job["applied"]),
                "closed_jobs": sum(1 for job in jobs if job["closed"]),
                "today_new_jobs": sum(1 for job in jobs if _job_date(job) == today),
                "week_new_jobs": sum(1 for job in jobs if (_job_date(job) or date.min) >= week_start),
            },
        }

    def open_resume_dir(self, job_id: str) -> Path:
        jobs_payload = self.build_jobs_payload()
        jobs_by_id = {job["job_id"]: job for job in jobs_payload["jobs"]}
        job = jobs_by_id.get(str(job_id or "").strip())
        if not job:
            raise FileNotFoundError(f"unknown job_id: {job_id}")
        resume_dir = str(job.get("resume_dir", "") or "").strip()
        if not resume_dir:
            raise FileNotFoundError("resume directory is empty for this job")

        target = Path(resume_dir)
        if not target.exists():
            raise FileNotFoundError(f"resume directory does not exist: {target}")

        if sys.platform == "darwin":
            subprocess.Popen(["open", str(target)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform.startswith("linux"):
            subprocess.Popen(["xdg-open", str(target)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform.startswith("win"):
            subprocess.Popen(["explorer", str(target)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            raise RuntimeError(f"unsupported platform: {sys.platform}")

        return target

    def launch_job_action(self, *, job_id: str, action: str) -> dict[str, Any]:
        normalized_job_id = str(job_id or "").strip()
        normalized_action = str(action or "").strip().lower()
        if not normalized_job_id:
            raise ValueError("job_id is required")
        if normalized_action not in {"generate", "rewrite"}:
            raise ValueError(f"unsupported action: {action}")

        jobs_payload = self.build_jobs_payload()
        jobs_by_id = {str(job["job_id"]): job for job in jobs_payload["jobs"]}
        job = jobs_by_id.get(normalized_job_id)
        if not job:
            raise ValueError(f"unknown job_id: {normalized_job_id}")
        if normalized_action == "generate" and str(job.get("review_status", "")) != "无简历":
            raise ValueError("generate action is only available for rows without resumes.")
        if normalized_action == "rewrite" and str(job.get("review_pipeline_state", "")) != "pending":
            raise ValueError("rewrite action is only available for pending resumes.")

        managed_state = load_monitor_state()
        for item in managed_state.get("processes", []) or []:
            if not isinstance(item, dict):
                continue
            if str(item.get("status", "") or "") not in {"running", "starting", "waiting_retry"}:
                continue
            metadata = item.get("metadata", {})
            if isinstance(metadata, dict) and str(metadata.get("job_id", "") or "") == normalized_job_id:
                raise ValueError("this job already has an active pipeline run")

        command = [
            sys.executable,
            str(SINGLE_JOB_ACTION_RUNNER),
            "--job-id",
            normalized_job_id,
            "--action",
            normalized_action,
        ]
        display_name = f"{'生成' if normalized_action == 'generate' else '重写'} · {job.get('company_name', '')} · {job.get('title', '')}"
        proc = spawn_managed_command(
            command,
            label=f"job_{normalized_action}",
            display_name=display_name,
            preset_id=f"job_{normalized_action}",
            metadata={
                "job_id": normalized_job_id,
                "job_action": normalized_action,
                "company_name": str(job.get("company_name", "") or ""),
                "title": str(job.get("title", "") or ""),
            },
        )
        return {
            "ok": True,
            "runner_pid": proc.pid,
            "job_id": normalized_job_id,
            "action": normalized_action,
            "display_name": display_name,
        }

    def build_monitor_payload(self) -> dict[str, Any]:
        managed_state = load_monitor_state()
        managed_processes = managed_state.get("processes", []) or []
        normalized: list[dict[str, Any]] = []
        active_statuses = {"running", "starting", "waiting_retry"}
        for item in managed_processes:
            if not isinstance(item, dict):
                continue
            status = str(item.get("status", "") or "")
            runner_pid = int(item.get("runner_pid", 0) or 0)
            child_pid = int(item.get("child_pid", 0) or 0)
            if status in active_statuses and not (_pid_alive(runner_pid) or _pid_alive(child_pid)):
                status = "failed"
            command_list = item.get("effective_command") or item.get("command") or []
            run_dir = str(item.get("run_dir", "") or "")
            progress = item.get("progress", {}) if isinstance(item.get("progress"), dict) else {}
            if status in active_statuses and isinstance(command_list, list) and run_dir:
                live_progress = compute_progress(command_list, run_dir)
                if live_progress:
                    progress = live_progress
            command_text = " ".join(command_list or [])
            metadata = item.get("metadata", {}) if isinstance(item.get("metadata"), dict) else {}
            if status in active_statuses and run_dir and ("pipeline.py all" in command_text or "pipeline.py resume" in command_text):
                live_details = _collect_resume_run_details(run_dir, command_text)
                if live_details:
                    metadata = {**metadata, **live_details}
            normalized.append(
                {
                    "id": str(item.get("id", "") or ""),
                    "source": str(item.get("source", "managed") or "managed"),
                    "label": str(item.get("label", "") or ""),
                    "display_name": str(item.get("display_name", "") or ""),
                    "preset_id": str(item.get("preset_id", "") or ""),
                    "status": status,
                    "cwd": str(item.get("cwd", "") or ""),
                    "command": " ".join(item.get("command", []) or []),
                    "effective_command": " ".join(command_list or []),
                    "runner_pid": runner_pid,
                    "child_pid": child_pid,
                    "pgid": int(item.get("pgid", 0) or 0),
                    "started_at": str(item.get("started_at", "") or ""),
                    "updated_at": str(item.get("updated_at", "") or ""),
                    "finished_at": str(item.get("finished_at", "") or ""),
                    "next_retry_at": str(item.get("next_retry_at", "") or ""),
                    "quota_kind": str(item.get("quota_kind", "") or ""),
                    "last_error": str(item.get("last_error", "") or ""),
                    "log_path": str(item.get("log_path", "") or ""),
                    "log_tail": list(item.get("log_tail", []) or []),
                    "run_count": int(item.get("run_count", 0) or 0),
                    "progress": progress,
                    "metadata": metadata,
                    "run_dir": run_dir,
                }
            )

        normalized.extend(list_unmanaged_processes())
        normalized.sort(
            key=lambda item: str(item.get("updated_at", "") or item.get("started_at", "") or ""),
            reverse=True,
        )
        normalized.sort(key=lambda item: item.get("status") not in {"running", "waiting_retry", "starting"})

        return {
            "generated_at": _now_iso(),
            "processes": normalized[:20],
            "presets": build_command_presets(),
            "meta": {
                "running_count": sum(1 for item in normalized if item.get("status") == "running"),
                "waiting_retry_count": sum(1 for item in normalized if item.get("status") == "waiting_retry"),
                "weekly_exit_count": sum(1 for item in normalized if item.get("status") == "quota_weekly_exit"),
            },
        }

    def launch_process(
        self,
        *,
        preset_id: str,
        tiers: list[str] | None,
        start_date: str,
        end_date: str,
    ) -> dict[str, Any]:
        preset = next((item for item in build_command_presets() if item["id"] == preset_id), None)
        if preset is None:
            raise ValueError(f"unknown preset_id: {preset_id}")

        with self._process_lock:
            command = build_preset_command(
                preset_id,
                tiers=tiers,
                start_date=start_date,
                end_date=end_date,
            )
            proc = spawn_managed_command(
                command,
                label=preset_id,
                display_name=str(preset.get("title", preset_id)),
                preset_id=preset_id,
                metadata={
                    "tiers": list(tiers or []),
                    "start_date": start_date,
                    "end_date": end_date,
                },
            )
        return {
            "ok": True,
            "runner_pid": proc.pid,
            "preset_id": preset_id,
            "display_name": str(preset.get("title", preset_id)),
        }

    def stop_process_by_id(self, process_id: str) -> dict[str, Any]:
        normalized_id = str(process_id or "").strip()
        if not normalized_id:
            raise ValueError("process_id is required")

        if normalized_id.startswith("unmanaged-"):
            pid_text = normalized_id.split("-", 1)[1]
            pid = int(pid_text)
            ok = stop_process(pid=pid)
            if not ok:
                raise RuntimeError(f"process not found: {pid}")
            return {"ok": True, "process_id": normalized_id, "pid": pid}

        managed_state = load_monitor_state()
        for item in managed_state.get("processes", []) or []:
            if not isinstance(item, dict) or str(item.get("id", "") or "") != normalized_id:
                continue
            pgid = int(item.get("pgid", 0) or 0)
            runner_pid = int(item.get("runner_pid", 0) or 0)
            child_pid = int(item.get("child_pid", 0) or 0)
            ok = stop_process(pgid=pgid or None, pid=runner_pid or child_pid or None)
            if not ok:
                raise RuntimeError(f"process not found: {normalized_id}")
            return {
                "ok": True,
                "process_id": normalized_id,
                "pgid": pgid,
                "runner_pid": runner_pid,
                "child_pid": child_pid,
            }

        raise RuntimeError(f"process not found: {normalized_id}")


class JobAppHandler(BaseHTTPRequestHandler):
    server: "JobAppServer"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/jobs":
            self._send_json(HTTPStatus.OK, self.server.store.build_jobs_payload())
            return
        if parsed.path == "/api/monitor":
            self._send_json(HTTPStatus.OK, self.server.store.build_monitor_payload())
            return
        if parsed.path == "/api/prompt-library":
            self._send_json(HTTPStatus.OK, build_match_pipe_prompt_library())
            return
        if parsed.path == "/api/prompt-review":
            self._send_json(HTTPStatus.OK, get_prompt_review_payload())
            return
        if parsed.path == "/api/prompt-review/revisions":
            self._send_json(HTTPStatus.OK, list_prompt_review_revisions())
            return
        if parsed.path == "/api/prompt-review/conflicts":
            self._send_json(HTTPStatus.OK, get_prompt_review_conflict())
            return
        if parsed.path == "/api/prompt-review/coverage":
            self._send_json(HTTPStatus.OK, get_prompt_review_coverage())
            return
        if parsed.path == "/api/prompt-review/ambiguities":
            self._send_json(HTTPStatus.OK, get_prompt_review_ambiguities())
            return
        if parsed.path == "/api/prompt-review/roundtrip":
            self._send_json(HTTPStatus.OK, get_prompt_review_roundtrip_report())
            return
        if parsed.path == "/api/open-dir":
            params = parse_qs(parsed.query)
            job_id = params.get("job_id", [""])[0]
            try:
                target = self.server.store.open_resume_dir(job_id)
            except Exception as exc:  # noqa: BLE001
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                return
            self._send_json(HTTPStatus.OK, {"ok": True, "path": str(target)})
            return
        self._serve_static(parsed.path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path not in {
            "/api/status",
            "/api/process/run",
            "/api/process/stop",
            "/api/job-action",
            "/api/prompt-library/save",
            "/api/prompt-review/save",
            "/api/prompt-review/restore",
            "/api/prompt-review/regenerate",
            "/api/prompt-review/roundtrip",
            "/api/prompt-review/writeback",
        }:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
            return

        payload = self._read_json_body()
        if payload is None:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid json"})
            return

        if parsed.path == "/api/status":
            job_id = str(payload.get("job_id", "") or "").strip()
            applied = bool(payload.get("applied", False))
            abandoned = bool(payload.get("abandoned", False))
            closed = bool(payload.get("closed", False))
            try:
                status = self.server.store.update_status(job_id, applied, abandoned, closed)
            except Exception as exc:  # noqa: BLE001
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                return
            self._send_json(HTTPStatus.OK, {"ok": True, "status": status})
            return

        if parsed.path == "/api/process/run":
            preset_id = str(payload.get("preset_id", "") or "").strip()
            tiers = payload.get("tiers", [])
            if not isinstance(tiers, list):
                tiers = []
            start_date = str(payload.get("start_date", "") or "").strip()
            end_date = str(payload.get("end_date", "") or "").strip()
            try:
                result = self.server.store.launch_process(
                    preset_id=preset_id,
                    tiers=[str(item or "").strip() for item in tiers if str(item or "").strip()],
                    start_date=start_date,
                    end_date=end_date,
                )
            except Exception as exc:  # noqa: BLE001
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                return
            self._send_json(HTTPStatus.OK, result)
            return

        if parsed.path == "/api/process/stop":
            process_id = str(payload.get("process_id", "") or "").strip()
            try:
                result = self.server.store.stop_process_by_id(process_id)
            except Exception as exc:  # noqa: BLE001
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                return
            self._send_json(HTTPStatus.OK, result)
            return

        if parsed.path == "/api/job-action":
            job_id = str(payload.get("job_id", "") or "").strip()
            action = str(payload.get("action", "") or "").strip()
            try:
                result = self.server.store.launch_job_action(job_id=job_id, action=action)
            except Exception as exc:  # noqa: BLE001
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                return
            self._send_json(HTTPStatus.OK, result)
            return

        if parsed.path == "/api/prompt-library/save":
            paragraphs = payload.get("paragraphs")
            if isinstance(paragraphs, dict):
                try:
                    result = save_match_pipe_paragraph_overrides(
                        {str(key): str(value) for key, value in paragraphs.items()}
                    )
                except Exception as exc:  # noqa: BLE001
                    self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                    return
                self._send_json(HTTPStatus.OK, result)
                return
            blocks = payload.get("blocks", {})
            if not isinstance(blocks, dict):
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"ok": False, "error": "paragraphs or blocks must be an object"},
                )
                return
            try:
                result = save_match_pipe_prompt_overrides(
                    {str(key): str(value) for key, value in blocks.items()}
                )
            except Exception as exc:  # noqa: BLE001
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                return
            self._send_json(HTTPStatus.OK, result)
            return

        if parsed.path == "/api/prompt-review/save":
            group_id = str(payload.get("group_id", "") or "").strip()
            editable_rich_text = str(payload.get("editable_rich_text", "") or "")
            display_text = payload.get("display_text")
            if display_text is not None:
                display_text = str(display_text)
            blocks = payload.get("blocks")
            if blocks is not None and not isinstance(blocks, list):
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "blocks must be an array"})
                return
            try:
                result = save_prompt_review_edit(
                    group_id=group_id,
                    client_revision_id=str(payload.get("client_revision_id", "") or ""),
                    editable_rich_text=editable_rich_text,
                    display_text=display_text,
                    blocks=blocks,
                    editor_meta=payload.get("editor_meta") if isinstance(payload.get("editor_meta"), dict) else {},
                )
            except Exception as exc:  # noqa: BLE001
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                return
            status = HTTPStatus.CONFLICT if not result.get("ok") and result.get("frozen") else HTTPStatus.OK
            self._send_json(status, result)
            return

        if parsed.path == "/api/prompt-review/restore":
            revision_id = str(payload.get("revision_id", "") or "").strip()
            try:
                result = restore_prompt_review_revision(
                    revision_id=revision_id,
                    client_revision_id=str(payload.get("client_revision_id", "") or ""),
                )
            except Exception as exc:  # noqa: BLE001
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                return
            status = HTTPStatus.CONFLICT if not result.get("ok") and result.get("frozen") else HTTPStatus.OK
            self._send_json(status, result)
            return

        if parsed.path == "/api/prompt-review/regenerate":
            try:
                result = regenerate_prompt_review()
            except Exception as exc:  # noqa: BLE001
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                return
            self._send_json(HTTPStatus.OK, result)
            return

        if parsed.path == "/api/prompt-review/roundtrip":
            raw_threshold = payload.get("freeze_threshold")
            try:
                threshold = float(raw_threshold) if raw_threshold is not None else 0.25
            except (TypeError, ValueError):
                threshold = 0.25
            try:
                report = run_prompt_review_roundtrip(freeze_threshold=threshold)
            except Exception as exc:  # noqa: BLE001
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                return
            self._send_json(HTTPStatus.OK, {"ok": True, "roundtrip": report})
            return

        if parsed.path == "/api/prompt-review/writeback":
            dry_run = bool(payload.get("dry_run", False))
            force_docs = bool(payload.get("force_docs", False))
            try:
                report = run_writeback(dry_run=dry_run, force_docs=force_docs)
            except Exception as exc:  # noqa: BLE001
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                return
            self._send_json(HTTPStatus.OK, report)
            return

    def _send_json(self, status: HTTPStatus, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_static(self, raw_path: str) -> None:
        if raw_path == "/prompt_review":
            raw_path = "/prompt_review/index.html"
        if raw_path.startswith("/prompt_review/"):
            self._serve_from_directory(PROMPT_REVIEW_DIR, raw_path[len("/prompt_review/"):], raw_path)
            return
        self._serve_from_directory(STATIC_DIR, raw_path.lstrip("/") or "index.html", raw_path)

    def _serve_from_directory(self, root_dir: Path, relative_path: str, raw_path: str) -> None:
        if root_dir == PROMPT_REVIEW_DIR:
            relative_path = relative_path or "index.html"
        else:
            relative_path = relative_path or "index.html"
        target = (root_dir / relative_path).resolve()
        try:
            target.relative_to(root_dir.resolve())
        except ValueError:
            self.send_error(HTTPStatus.FORBIDDEN.value)
            return

        if not target.exists() or not target.is_file():
            if raw_path == "/":
                target = root_dir / "index.html"
            else:
                self.send_error(HTTPStatus.NOT_FOUND.value)
                return

        content = target.read_bytes()
        content_type, _ = mimetypes.guess_type(str(target))
        self.send_response(HTTPStatus.OK.value)
        self.send_header("Content-Type", f"{content_type or 'application/octet-stream'}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _read_json_body(self) -> dict[str, Any] | None:
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            return None
        if not isinstance(payload, dict):
            return None
        return payload


class JobAppServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], store: JobAppStore) -> None:
        super().__init__(server_address, JobAppHandler)
        self.store = store


def run_server(host: str, port: int, open_browser: bool) -> None:
    store = JobAppStore()
    server = JobAppServer((host, port), store)
    url = f"http://{host}:{port}/"
    print(f"Job app listening on {url}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local downstream job web app.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open-browser", action="store_true")
    args = parser.parse_args()
    run_server(args.host, args.port, open_browser=not args.no_open_browser)


if __name__ == "__main__":
    main()
