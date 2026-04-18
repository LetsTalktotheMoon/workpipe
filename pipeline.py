#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = PROJECT_ROOT.parent
RUNTIME_ROOT = PROJECT_ROOT / "runtime"
JOB_TRACKER_ROOT = RUNTIME_ROOT / "job_tracker"
RESUME_PIPELINE_ROOT = RUNTIME_ROOT

RUNS_ROOT = PROJECT_ROOT / "runs"
STATE_ROOT = PROJECT_ROOT / "state"
STATE_FILE = STATE_ROOT / "resume_state.json"
DATA_ROOT = PROJECT_ROOT / "data"

DEFAULT_JOBS_JSON = DATA_ROOT / "job_tracker" / "jobs_catalog.json"
DEFAULT_PORTFOLIO_ROOT = DATA_ROOT / "deliverables" / "resume_portfolio"
DEFAULT_PROFILES_JSON = DEFAULT_PORTFOLIO_ROOT / "profiles.json"

if str(RESUME_PIPELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(RESUME_PIPELINE_ROOT))

from automation.artifacts import compile_markdown_to_pdf
from automation.job_router import build_job_fingerprint, build_skill_vocab_from_seeds, decide_route
from automation.jobs_catalog import FULL_JOBS_CATALOG_PATH, LOCAL_SCRAPED_JOBS_PATH, rebuild_catalog
from automation.job_screen import screen_job_for_pipeline
from automation.portfolio import publish_job_artifact, rebuild_portfolio_indexes
from automation.seed_registry import SeedEntry, load_seed_registry
from automation.text_utils import prepare_skill_tokens
from config.candidate_framework import is_bytedance_target_company
from core.provider_settings import PROVIDER_CHOICES, resolve_provider_settings
from pipeline.orchestrator import PipelineOrchestrator
from pipeline.retarget_orchestrator import SeedRetargetOrchestrator


def now_ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def relabel_provider(provider: str, write_model: str | None, review_model: str | None, transport: str | None) -> dict[str, str]:
    return resolve_provider_settings(provider, write_model, review_model, transport)


def load_resume_state() -> dict[str, Any]:
    return load_json(STATE_FILE, default={"processed_ids": [], "last_run": "", "last_run_manifest": ""})


def save_resume_state(state: dict[str, Any]) -> None:
    write_json(STATE_FILE, state)


def persist_resume_state(*, processed_ids: set[str], last_run_manifest: str = "") -> None:
    state = load_resume_state()
    state["processed_ids"] = sorted({str(item) for item in processed_ids if str(item).strip()})
    state["last_run"] = datetime.now().isoformat(timespec="seconds")
    if last_run_manifest:
        state["last_run_manifest"] = last_run_manifest
    save_resume_state(state)


_COMPANY_SIZE_RANK: dict[str, int] = {
    "10001+ employees": 8,
    "5001-10000 employees": 7,
    "1001-5000 employees": 6,
    "501-1000 employees": 5,
    "201-500 employees": 4,
    "51-200 employees": 3,
    "11-50 employees": 2,
    "2-10 employees": 1,
}

_COMPANY_SIZE_TO_TIER: dict[str, str] = {
    "10001+ employees": "large",
    "5001-10000 employees": "large",
    "1001-5000 employees": "mid_large",
    "501-1000 employees": "mid_small",
    "201-500 employees": "small",
    "51-200 employees": "small",
    "11-50 employees": "small",
    "2-10 employees": "small",
}

_COMPANY_TIER_ALIASES: dict[str, tuple[str, ...]] = {
    "large": ("large",),
    "big": ("large",),
    "major": ("large",),
    "大厂": ("large",),
    "10000+": ("large",),
    "10001+": ("large",),
    "5001-10000": ("large",),
    "5001-10000 employees": ("large",),
    "10001+ employees": ("large",),
    "mid": ("mid_large", "mid_small"),
    "medium": ("mid_large", "mid_small"),
    "中厂": ("mid_large", "mid_small"),
    "mid_large": ("mid_large",),
    "mid-1001-5000": ("mid_large",),
    "1001-5000": ("mid_large",),
    "1001-5000 employees": ("mid_large",),
    "mid_small": ("mid_small",),
    "mid-501-1000": ("mid_small",),
    "501-1000": ("mid_small",),
    "501-1000 employees": ("mid_small",),
    "small": ("small",),
    "小厂": ("small",),
    "<=500": ("small",),
    "201-500": ("small",),
    "201-500 employees": ("small",),
    "51-200": ("small",),
    "51-200 employees": ("small",),
    "11-50": ("small",),
    "11-50 employees": ("small",),
    "2-10": ("small",),
    "2-10 employees": ("small",),
    "all": (),
    "*": (),
}

def _parse_cli_date(value: str | None) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    return datetime.strptime(text, "%Y-%m-%d").date()


def _normalize_company_tiers(raw_values: list[str] | None) -> set[str] | None:
    if not raw_values:
        return {"large"}

    normalized: set[str] = set()
    for raw_value in raw_values:
        for part in str(raw_value or "").split(","):
            token = part.strip().lower()
            if not token:
                continue
            mapped = _COMPANY_TIER_ALIASES.get(token)
            if mapped == ():
                return None
            if mapped is not None:
                normalized.update(mapped)
                continue
            raise ValueError(f"Unsupported company tier: {part.strip()}")
    return normalized or {"large"}


def _job_publish_date(row: dict[str, Any]) -> date | None:
    for key in ("publish_time", "publish_date", "discovered_date", "discovered_at"):
        raw = str(row.get(key, "") or "").strip()
        if not raw:
            continue
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                continue
    return None


def _normalize_job_ids(job_ids: list[str] | None) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for item in job_ids or []:
        value = str(item or "").strip()
        if value and value not in seen:
            seen.add(value)
            normalized.append(value)
    return normalized


def _is_bytedance_target_job(row: dict[str, Any]) -> bool:
    company_name = str(row.get("company_name", "") or "").strip()
    return is_bytedance_target_company(company_name)


def _matches_job_filters(
    row: dict[str, Any],
    *,
    allowed_company_tiers: set[str] | None,
    publish_date: date | None,
    publish_date_from: date | None,
    publish_date_to: date | None,
    job_ids: set[str] | None,
) -> bool:
    if job_ids is not None and str(row.get("job_id", "") or "").strip() not in job_ids:
        return False
    if allowed_company_tiers is not None:
        company_tier = _COMPANY_SIZE_TO_TIER.get(str(row.get("company_size", "") or "").strip())
        if company_tier not in allowed_company_tiers:
            return False

    row_publish_date = _job_publish_date(row)
    if publish_date is not None and row_publish_date != publish_date:
        return False
    if publish_date_from is not None and (row_publish_date is None or row_publish_date < publish_date_from):
        return False
    if publish_date_to is not None and (row_publish_date is None or row_publish_date > publish_date_to):
        return False
    return True


def _resolve_publish_date_filters(args: argparse.Namespace) -> tuple[date | None, date | None, date | None]:
    publish_date = _parse_cli_date(args.publish_date)
    publish_date_from = _parse_cli_date(args.publish_date_from)
    publish_date_to = _parse_cli_date(args.publish_date_to)
    if publish_date is not None and (publish_date_from is not None or publish_date_to is not None):
        raise ValueError("--publish-date cannot be combined with --publish-date-from/--publish-date-to")
    if publish_date_from is not None and publish_date_to is not None and publish_date_from > publish_date_to:
        raise ValueError("--publish-date-from cannot be later than --publish-date-to")
    return publish_date, publish_date_from, publish_date_to


def _job_sort_key(row: dict) -> tuple[int, float, str]:
    company_size_rank = _COMPANY_SIZE_RANK.get(str(row.get("company_size", "") or ""), 0)
    min_salary = float(row.get("min_salary", 0) or 0)
    publish_time = str(row.get("publish_time", "") or "")
    return (company_size_rank, min_salary, publish_time)


def normalize_jobs(
    rows: list[dict],
    *,
    force_all: bool,
    max_jobs: int,
    processed_ids: set[str],
    allowed_company_tiers: set[str] | None,
    publish_date: date | None,
    publish_date_from: date | None,
    publish_date_to: date | None,
    job_ids: set[str] | None,
) -> list[dict]:
    prefiltered = [
        row
        for row in rows
        if _matches_job_filters(
            row,
            allowed_company_tiers=allowed_company_tiers,
            publish_date=publish_date,
            publish_date_from=publish_date_from,
            publish_date_to=publish_date_to,
            job_ids=job_ids,
        )
    ]
    filtered = prefiltered if force_all else [row for row in prefiltered if str(row.get("job_id", "") or "") not in processed_ids]
    filtered = sorted(filtered, key=_job_sort_key, reverse=True)
    if max_jobs > 0:
        filtered = filtered[:max_jobs]
    return filtered


def _load_priority_job_ids_from_env() -> list[str]:
    path_value = str(os.environ.get("MANAGED_PRIORITY_JOB_IDS_FILE", "") or "").strip()
    if not path_value:
        return []
    path = Path(path_value)
    if not path.exists():
        return []
    payload = load_json(path, default={})
    if not isinstance(payload, dict):
        return []
    job_ids = payload.get("job_ids", [])
    if not isinstance(job_ids, list):
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for item in job_ids:
        value = str(item or "").strip()
        if value and value not in seen:
            seen.add(value)
            normalized.append(value)
    return normalized


def _prioritize_selected_rows(rows: list[dict], priority_job_ids: list[str]) -> list[dict]:
    if not rows or not priority_job_ids:
        return rows
    row_by_job_id = {
        str(row.get("job_id", "") or "").strip(): row
        for row in rows
        if str(row.get("job_id", "") or "").strip()
    }
    priority_set = set(priority_job_ids)
    prioritized = [row_by_job_id[job_id] for job_id in priority_job_ids if job_id in row_by_job_id]
    remaining = [row for row in rows if str(row.get("job_id", "") or "").strip() not in priority_set]
    return prioritized + remaining


def load_active_profile(profiles_path: Path) -> dict[str, str]:
    data = load_json(profiles_path, default={}) or {}
    active_id = str(data.get("active_profile", "default") or "default")
    profiles = data.get("profiles", []) or []
    for profile in profiles:
        if str(profile.get("profile_id", "") or "") == active_id:
            return {
                "profile_id": active_id,
                "name": str(profile.get("name", "") or ""),
                "phone": str(profile.get("phone", "") or ""),
                "email": str(profile.get("email", "") or ""),
            }
    return {"profile_id": active_id, "name": "", "phone": "", "email": ""}


def build_review_payload(result: dict[str, Any], *, route_mode: str, seed_label: str) -> dict[str, Any]:
    review_obj = result.get("review")
    if review_obj is not None and hasattr(review_obj, "to_dict"):
        payload = review_obj.to_dict()
    else:
        payload = {}
    payload.update(
        {
            "final_score": round(float(result.get("final_score", 0.0) or 0.0), 1),
            "verdict": str(result.get("verdict", "") or ""),
            "seed_label": seed_label,
            "route_mode": route_mode,
            "revised": bool(result.get("revised", False)),
        }
    )
    return payload


def _review_score(review: dict[str, Any]) -> float:
    try:
        return float(review.get("final_score", review.get("weighted_score", 0.0)) or 0.0)
    except Exception:
        return 0.0


def _index_portfolio_records(records: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    by_job_id: dict[str, dict[str, Any]] = {}
    by_seed_id: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        job_id = str(record.get("job_id", "") or "").strip()
        if job_id:
            by_job_id[job_id] = record
        seed_id = str(record.get("parent_seed_id", "") or record.get("seed_id", "") or "").strip()
        if seed_id:
            by_seed_id.setdefault(seed_id, []).append(record)
    for seed_id, items in by_seed_id.items():
        items.sort(
            key=lambda item: (
                1 if review_pipeline_state(item.get("review", {}) | {"verdict": item.get("review_verdict", "")}) == "pass" else 0,
                _review_score(item.get("review", {}) if isinstance(item.get("review"), dict) else {}),
                str(item.get("generated_at", "") or ""),
            ),
            reverse=True,
        )
    return by_job_id, by_seed_id


def _best_reuse_source_record(
    *,
    seed: SeedEntry,
    portfolio_by_job_id: dict[str, dict[str, Any]],
    portfolio_by_seed_id: dict[str, list[dict[str, Any]]],
) -> dict[str, Any] | None:
    source_job_id = str(seed.source_job_id or "").strip()
    if source_job_id:
        record = portfolio_by_job_id.get(source_job_id)
        if isinstance(record, dict) and str(record.get("resume_md", "") or "").strip():
            return record
    for record in portfolio_by_seed_id.get(seed.seed_id, []):
        if str(record.get("resume_md", "") or "").strip():
            return record
    return None


def review_pipeline_state(review: dict[str, Any]) -> str:
    verdict = str(review.get("verdict", "") or review.get("overall_verdict", "") or "").strip().lower()
    if verdict == "pass" or effective_pass(review):
        return "pass"
    if verdict == "reject":
        return "reject"
    return "pending"


def effective_pass(review: dict[str, Any]) -> bool:
    try:
        final_score = float(review.get("final_score", review.get("weighted_score", 0.0)) or 0.0)
    except Exception:
        final_score = 0.0
    return (
        bool(review.get("passed", False))
        and final_score >= 93.0
        and int(review.get("critical_count", 0) or 0) == 0
        and int(review.get("high_count", 0) or 0) == 0
    )


def make_run_dir(prefix: str, provided: str | None = None) -> Path:
    if provided:
        target = Path(provided)
        if not target.is_absolute():
            target = (PROJECT_ROOT / target).resolve()
        ensure_dir(target)
        return target
    return ensure_dir(RUNS_ROOT / f"{prefix}_{now_ts()}")


def stage_job_bundle(run_dir: Path, row: dict[str, Any], route_payload: dict[str, Any]) -> tuple[Path, Path]:
    from automation.jd_builder import row_to_jd_markdown

    job_id = str(row.get("job_id", "") or "unknown-job")
    job_dir = ensure_dir(run_dir / "jobs" / job_id)
    jd_path = job_dir / "job.md"
    jd_path.write_text(row_to_jd_markdown(row), encoding="utf-8")
    write_json(job_dir / "job_row.json", row)
    write_json(job_dir / "route.json", route_payload)
    return job_dir, jd_path


def find_latest_resume_manifest() -> Path:
    manifests = sorted(RUNS_ROOT.glob("resume_*/run_manifest.json"))
    if not manifests:
        raise FileNotFoundError("No resume run manifest found. Run the resume command first or pass --run-manifest.")
    return manifests[-1]


def update_portfolio_manifest_pdf(job_dir: Path, pdf_path: Path) -> None:
    manifest_path = job_dir / "manifest.json"
    if not manifest_path.exists():
        return
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["resume_pdf"] = str(pdf_path)
    payload["pdf_generated_at"] = datetime.now().isoformat(timespec="seconds")
    write_json(manifest_path, payload)


def run_jobs_step(
    *,
    run_dir: Path,
    jobs_json: Path,
    skip_scrape: bool,
    lookback_hours: int,
    allow_existing_json: bool,
) -> dict[str, Any]:
    ensure_dir(run_dir)
    log_path = run_dir / "jobs_step.log"
    ensure_dir(jobs_json.parent)
    ensure_dir(LOCAL_SCRAPED_JOBS_PATH.parent)

    if skip_scrape:
        if not jobs_json.exists():
            raise FileNotFoundError(f"jobs json not found: {jobs_json}")
        summary = {
            "step": "jobs",
            "action": "skip_scrape",
            "jobs_json": str(jobs_json),
            "used_existing_json": True,
            "returncode": 0,
        }
        write_json(run_dir / "jobs_summary.json", summary)
        return summary

    cmd = [sys.executable, str(JOB_TRACKER_ROOT / "main.py"), "--scrape-only", "--lookback-hours", str(lookback_hours)]
    completed = subprocess.run(
        cmd,
        cwd=str(JOB_TRACKER_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    log_path.write_text((completed.stdout or "") + (completed.stderr or ""), encoding="utf-8")

    runtime_jobs_json = JOB_TRACKER_ROOT / "scraped_jobs.json"
    if runtime_jobs_json.exists():
        shutil.copyfile(runtime_jobs_json, LOCAL_SCRAPED_JOBS_PATH)

    used_existing = completed.returncode != 0 and allow_existing_json and FULL_JOBS_CATALOG_PATH.exists()
    if completed.returncode != 0 and not used_existing:
        raise RuntimeError(f"job-tracker scrape failed with code {completed.returncode}; see {log_path}")

    catalog_summary = rebuild_catalog(
        catalog_path=FULL_JOBS_CATALOG_PATH,
        include_google_sheet=False,
        include_existing_catalog=True,
        include_local_scrape=True,
        include_portfolio_history=True,
    )
    if jobs_json.resolve() != FULL_JOBS_CATALOG_PATH.resolve():
        shutil.copyfile(FULL_JOBS_CATALOG_PATH, jobs_json)

    summary = {
        "step": "jobs",
        "action": "scrape_only",
        "jobs_json": str(jobs_json),
        "local_scrape_json": str(LOCAL_SCRAPED_JOBS_PATH),
        "catalog_json": str(FULL_JOBS_CATALOG_PATH),
        "catalog_count": int(catalog_summary.get("catalog_count", 0) or 0),
        "catalog_unique_job_ids": int(catalog_summary.get("unique_job_ids", 0) or 0),
        "used_existing_json": used_existing,
        "returncode": completed.returncode,
        "command": cmd,
        "log_path": str(log_path),
    }
    write_json(run_dir / "jobs_summary.json", summary)
    return summary


def run_resume_step(
    *,
    run_dir: Path,
    jobs_json: Path,
    max_jobs: int,
    force_all: bool,
    dry_run: bool,
    enable_llm: bool,
    provider_settings: dict[str, str],
    publish_portfolio: bool,
    no_state_update: bool,
    new_seed_mode: str,
    portfolio_root: Path,
    company_tiers: set[str] | None,
    publish_date: date | None,
    publish_date_from: date | None,
    publish_date_to: date | None,
    max_runtime_minutes: int,
    job_ids: set[str] | None,
) -> dict[str, Any]:
    ensure_dir(run_dir)
    rows = load_json(jobs_json, default=[])
    if not isinstance(rows, list):
        raise ValueError(f"jobs json must contain a list: {jobs_json}")

    state = load_resume_state()
    processed_ids = {str(item) for item in state.get("processed_ids", []) or []}
    selected_rows = normalize_jobs(
        rows,
        force_all=force_all,
        max_jobs=max_jobs,
        processed_ids=processed_ids,
        allowed_company_tiers=company_tiers,
        publish_date=publish_date,
        publish_date_from=publish_date_from,
        publish_date_to=publish_date_to,
        job_ids=job_ids,
    )
    selected_rows = _prioritize_selected_rows(selected_rows, _load_priority_job_ids_from_env())

    seeds = load_seed_registry(include_promoted=True)
    seeds_by_id: dict[str, SeedEntry] = {seed.seed_id: seed for seed in seeds}
    portfolio_records = load_json(portfolio_root / "portfolio_index.json", default=[])
    portfolio_by_job_id, portfolio_by_seed_id = _index_portfolio_records(
        portfolio_records if isinstance(portfolio_records, list) else []
    )
    skill_vocab = build_skill_vocab_from_seeds(seeds)
    skill_tokens = prepare_skill_tokens(skill_vocab)

    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    handled_job_ids: set[str] = set()

    def flush_partial_state() -> None:
        if no_state_update:
            return
        persist_resume_state(processed_ids=processed_ids | handled_job_ids)

    for row in selected_rows:
        job_id = str(row.get("job_id", "") or "")
        title = str(row.get("job_title", "") or row.get("job_nlp_title", "") or "")
        company = str(row.get("company_name", "") or "")
        decision = screen_job_for_pipeline(row)
        base = {
            "job_id": job_id,
            "company_name": company,
            "title": title,
            "publish_time": str(row.get("publish_time", "") or ""),
            "apply_link": str(row.get("apply_link", "") or ""),
            "screen_level": decision.level,
            "screen_reason": decision.reason,
            "screen_tags": list(decision.tags),
        }
        if not decision.accepted:
            rejected.append(base)
            if job_id:
                handled_job_ids.add(job_id)
                flush_partial_state()
            continue

        fingerprint = build_job_fingerprint(row, seeds, skill_vocab=skill_vocab, skill_tokens=skill_tokens)
        route = decide_route(fingerprint, seeds)
        effective_route_mode = route.route_mode
        decision_reason = route.decision_reason
        if _is_bytedance_target_job(row) and effective_route_mode == "reuse":
            effective_route_mode = "retarget"
            decision_reason = f"{route.decision_reason} | bytedance_special_rewrite"
        accepted.append(
            {
                **base,
                "route_mode": effective_route_mode,
                "decision_reason": decision_reason,
                "should_generate": route.should_generate,
                "top_candidate": route.top_candidate.to_dict(),
                "top_candidates": [candidate.to_dict() for candidate in route.top_candidates],
            }
        )

    write_json(run_dir / "selected_rows.json", selected_rows)
    write_json(run_dir / "accepted_jobs.json", accepted)
    write_json(run_dir / "rejected_jobs.json", rejected)

    generated_results: list[dict[str, Any]] = []
    portfolio_touched = False
    runtime_limit_hit = False
    runtime_limit_remaining_jobs = 0
    deadline = time.monotonic() + (max_runtime_minutes * 60) if max_runtime_minutes > 0 else None

    for index, entry in enumerate(accepted):
        if deadline is not None and time.monotonic() >= deadline:
            runtime_limit_hit = True
            remaining_entries = accepted[index:]
            runtime_limit_remaining_jobs = len(remaining_entries)
            for remaining in remaining_entries:
                generated_results.append(
                    {
                        "job_id": remaining["job_id"],
                        "company_name": remaining["company_name"],
                        "title": remaining["title"],
                        "route_mode": remaining["route_mode"],
                        "decision_reason": remaining["decision_reason"],
                        "status": "skipped_runtime_limit",
                        "job_dir": "",
                        "jd_path": "",
                        "resume_output_path": "",
                        "artifact_dir": "",
                        "seed_id": str(remaining["top_candidate"].get("seed_id", "") or ""),
                        "seed_label": str(remaining["top_candidate"].get("label", "") or ""),
                        "final_score": 0.0,
                        "verdict": "",
                        "review": {},
                    }
                )
            break

        row = next(item for item in selected_rows if str(item.get("job_id", "") or "") == entry["job_id"])
        job_dir, jd_path = stage_job_bundle(run_dir, row, entry)
        result_summary = {
            "job_id": entry["job_id"],
            "company_name": entry["company_name"],
            "title": entry["title"],
            "route_mode": entry["route_mode"],
            "decision_reason": entry["decision_reason"],
            "status": "",
            "job_dir": str(job_dir),
            "jd_path": str(jd_path),
            "resume_output_path": "",
            "artifact_dir": "",
            "seed_id": str(entry["top_candidate"].get("seed_id", "") or ""),
            "seed_label": str(entry["top_candidate"].get("label", "") or ""),
            "final_score": 0.0,
            "verdict": "",
            "review": {},
        }
        top_candidate = entry["top_candidate"]
        seed_id = str(top_candidate.get("seed_id", "") or "")
        seed_label = str(top_candidate.get("label", "") or "")

        if entry["route_mode"] == "reuse":
            seed = seeds_by_id.get(seed_id)
            if seed is None:
                result_summary["status"] = "error"
                result_summary["verdict"] = "error"
                result_summary["review"] = {"error": f"missing seed for {seed_id}"}
                generated_results.append(result_summary)
                handled_job_ids.add(entry["job_id"])
                flush_partial_state()
                continue
            source_record = _best_reuse_source_record(
                seed=seed,
                portfolio_by_job_id=portfolio_by_job_id,
                portfolio_by_seed_id=portfolio_by_seed_id,
            )
            resume_source_path = (
                str(source_record.get("resume_md", "") or "").strip()
                if isinstance(source_record, dict)
                else str(seed.source_md)
            )
            if not resume_source_path:
                resume_source_path = str(seed.source_md)
            reused_review = {}
            if isinstance(source_record, dict):
                reused_review = dict(source_record.get("review", {}) or {})
            if not reused_review:
                score = float(seed.validated_score or 0.0)
                verdict = "pass" if score >= 93.0 else "pending"
                reused_review = {
                    "final_score": round(score, 1),
                    "weighted_score": round(score, 1),
                    "passed": verdict == "pass",
                    "verdict": verdict,
                    "seed_label": seed.label,
                    "route_mode": entry["route_mode"],
                    "revised": False,
                    "reused_from_seed": True,
                }
            else:
                reused_review = dict(reused_review)
                reused_review.setdefault("seed_label", seed.label)
                reused_review["route_mode"] = entry["route_mode"]
                reused_review["reused_from_seed"] = True
            result_summary["review"] = reused_review
            result_summary["resume_output_path"] = resume_source_path
            result_summary["final_score"] = _review_score(reused_review)
            result_summary["verdict"] = review_pipeline_state(reused_review)
            result_summary["status"] = "reused_artifact"
            result_summary["seed_id"] = seed_id
            result_summary["seed_label"] = seed.label
            if publish_portfolio:
                manifest = publish_job_artifact(
                    row,
                    resume_source_path,
                    portfolio_root=str(portfolio_root),
                    source_kind="local_unified_pipeline",
                    seed_id=seed_id,
                    seed_label=seed.label,
                    route_mode=entry["route_mode"],
                    top_candidate=top_candidate,
                    review_payload=reused_review,
                    parent_seed_id=seed_id,
                    rebuild_indexes=False,
                    job_md_text=jd_path.read_text(encoding="utf-8"),
                )
                result_summary["artifact_dir"] = str(manifest.get("artifact_dir", "") or "")
                portfolio_touched = True
            generated_results.append(result_summary)
            handled_job_ids.add(entry["job_id"])
            flush_partial_state()
            continue

        if dry_run or not enable_llm:
            result_summary["status"] = "dry_run"
            generated_results.append(result_summary)
            handled_job_ids.add(entry["job_id"])
            flush_partial_state()
            continue

        generation_dir = ensure_dir(job_dir / "generation")

        if entry["route_mode"] == "retarget":
            seed = seeds_by_id.get(seed_id)
            if seed is None:
                result_summary["status"] = "error"
                result_summary["verdict"] = "error"
                result_summary["review"] = {"error": f"missing seed for {seed_id}"}
                generated_results.append(result_summary)
                handled_job_ids.add(entry["job_id"])
                flush_partial_state()
                continue
            orchestrator = SeedRetargetOrchestrator(
                output_dir=str(generation_dir),
                enable_llm=True,
                write_model=provider_settings["write_model"],
                review_model=provider_settings["review_model"],
                llm_transport=provider_settings["llm_transport"],
            )
            result = orchestrator.run(
                seed_resume_md=seed.source_md.read_text(encoding="utf-8"),
                seed_label=seed.label,
                route_mode=entry["route_mode"],
                jd_text=jd_path.read_text(encoding="utf-8"),
                jd_id=entry["job_id"],
                company=entry["company_name"],
                top_candidate=top_candidate,
            )
        elif new_seed_mode == "free_write":
            orchestrator = PipelineOrchestrator(
                output_dir=str(generation_dir),
                enable_llm=True,
                write_model=provider_settings["write_model"],
                review_model=provider_settings["review_model"],
                llm_transport=provider_settings["llm_transport"],
            )
            result = orchestrator.run(
                jd_text=jd_path.read_text(encoding="utf-8"),
                jd_id=entry["job_id"],
                company=entry["company_name"],
            )
            seed_id = ""
            seed_label = ""
        else:
            result_summary["status"] = "skipped_new_seed"
            generated_results.append(result_summary)
            handled_job_ids.add(entry["job_id"])
            flush_partial_state()
            continue

        review_payload = build_review_payload(result, route_mode=entry["route_mode"], seed_label=seed_label)
        result_summary["review"] = review_payload
        result_summary["resume_output_path"] = str(result.get("output_path", "") or "")
        result_summary["final_score"] = float(review_payload.get("final_score", 0.0) or 0.0)
        result_summary["verdict"] = str(review_payload.get("verdict", "") or "")
        result_summary["status"] = "generated" if result.get("output_path") else "failed"
        result_summary["seed_id"] = seed_id
        result_summary["seed_label"] = seed_label

        pipeline_state = review_pipeline_state(review_payload)
        if publish_portfolio and result.get("output_path") and pipeline_state != "reject":
            manifest = publish_job_artifact(
                row,
                result["output_path"],
                portfolio_root=str(portfolio_root),
                source_kind="local_unified_pipeline",
                seed_id=seed_id,
                seed_label=seed_label,
                route_mode=entry["route_mode"],
                top_candidate=top_candidate,
                review_payload=review_payload,
                parent_seed_id=seed_id,
                rebuild_indexes=False,
                job_md_text=jd_path.read_text(encoding="utf-8"),
            )
            result_summary["artifact_dir"] = str(manifest.get("artifact_dir", "") or "")
            portfolio_touched = True

        generated_results.append(result_summary)
        handled_job_ids.add(entry["job_id"])
        flush_partial_state()

    if publish_portfolio and portfolio_touched:
        rebuild_portfolio_indexes(portfolio_root)

    summary = {
        "step": "resume",
        "jobs_json": str(jobs_json),
        "selected_jobs": len(selected_rows),
        "accepted_jobs": len(accepted),
        "rejected_jobs": len(rejected),
        "results": generated_results,
        "provider": provider_settings["provider"],
        "write_model": provider_settings["write_model"],
        "review_model": provider_settings["review_model"],
        "llm_transport": provider_settings["llm_transport"],
        "dry_run": dry_run or not enable_llm,
        "enable_llm": enable_llm,
        "publish_portfolio": publish_portfolio,
        "company_tiers": sorted(company_tiers) if company_tiers is not None else ["all"],
        "publish_date": publish_date.isoformat() if publish_date is not None else "",
        "publish_date_from": publish_date_from.isoformat() if publish_date_from is not None else "",
        "publish_date_to": publish_date_to.isoformat() if publish_date_to is not None else "",
        "max_runtime_minutes": max_runtime_minutes,
        "runtime_limit_hit": runtime_limit_hit,
        "runtime_limit_remaining_jobs": runtime_limit_remaining_jobs,
        "handled_jobs": len(handled_job_ids),
    }
    manifest_path = run_dir / "run_manifest.json"
    write_json(manifest_path, summary)
    if not no_state_update:
        persist_resume_state(processed_ids=processed_ids | handled_job_ids, last_run_manifest=str(manifest_path))
    return {"summary": summary, "manifest_path": manifest_path}


def collect_pdf_targets(*, run_manifest: Path | None, resume_md: Path | None, output_dir: Path | None) -> list[dict[str, Any]]:
    if resume_md is not None:
        if output_dir is None:
            raise ValueError("--output-dir is required when using --resume-md")
        return [
            {
                "target_dir": str(output_dir),
                "resume_md": str(resume_md),
                "portfolio_target": False,
            }
        ]

    if run_manifest is None:
        run_manifest = find_latest_resume_manifest()

    payload = load_json(run_manifest, default={}) or {}
    targets: list[dict[str, Any]] = []
    for item in payload.get("results", []) or []:
        review_payload = item.get("review", {}) if isinstance(item.get("review"), dict) else {}
        if review_pipeline_state(review_payload | {"verdict": item.get("verdict", "")}) != "pass":
            continue
        artifact_dir = str(item.get("artifact_dir", "") or "")
        resume_output_path = str(item.get("resume_output_path", "") or "")
        if artifact_dir:
            target_dir = Path(artifact_dir)
            md_path = target_dir / "resume.md"
            portfolio_target = True
        elif resume_output_path:
            md_path = Path(resume_output_path)
            target_dir = md_path.parent
            portfolio_target = False
        else:
            continue
        targets.append(
            {
                "target_dir": str(target_dir),
                "resume_md": str(md_path),
                "portfolio_target": portfolio_target,
            }
        )
    return targets


def run_pdf_step(
    *,
    run_dir: Path,
    run_manifest: Path | None,
    resume_md: Path | None,
    output_dir: Path | None,
    profiles_path: Path,
    portfolio_root: Path,
    dry_run: bool,
) -> dict[str, Any]:
    ensure_dir(run_dir)
    profile = load_active_profile(profiles_path)
    targets = collect_pdf_targets(run_manifest=run_manifest, resume_md=resume_md, output_dir=output_dir)

    results: list[dict[str, Any]] = []
    portfolio_changed = False

    for target in targets:
        target_dir = Path(target["target_dir"])
        md_path = Path(target["resume_md"])
        result = {
            "target_dir": str(target_dir),
            "resume_md": str(md_path),
            "portfolio_target": bool(target["portfolio_target"]),
            "status": "",
            "resume_pdf": "",
        }
        if not md_path.exists():
            result["status"] = "missing_resume_md"
            results.append(result)
            continue

        if dry_run:
            result["status"] = "dry_run"
            results.append(result)
            continue

        compiled_pdf = compile_markdown_to_pdf(
            md_path,
            target_dir,
            name=profile["name"],
            phone=profile["phone"],
            email=profile["email"],
        )
        final_pdf = target_dir / "resume.pdf"
        if compiled_pdf.resolve() != final_pdf.resolve():
            shutil.copyfile(compiled_pdf, final_pdf)
        result["status"] = "generated"
        result["resume_pdf"] = str(final_pdf)

        if bool(target["portfolio_target"]):
            update_portfolio_manifest_pdf(target_dir, final_pdf)
            portfolio_changed = True
        results.append(result)

    if portfolio_changed:
        rebuild_portfolio_indexes(portfolio_root)

    summary = {
        "step": "pdf",
        "profile_id": profile["profile_id"],
        "targets": results,
        "dry_run": dry_run,
    }
    write_json(run_dir / "pdf_summary.json", summary)
    return summary


def command_jobs(args: argparse.Namespace) -> None:
    run_dir = make_run_dir("jobs", args.run_dir)
    summary = run_jobs_step(
        run_dir=run_dir,
        jobs_json=Path(args.jobs_json),
        skip_scrape=args.skip_scrape,
        lookback_hours=args.lookback_hours,
        allow_existing_json=args.allow_existing_json,
    )
    print(json.dumps({"run_dir": str(run_dir), **summary}, indent=2, ensure_ascii=False))


def command_resume(args: argparse.Namespace) -> None:
    run_dir = make_run_dir("resume", args.run_dir)
    provider_settings = relabel_provider(args.provider, args.write_model, args.review_model, args.llm_transport)
    company_tiers = _normalize_company_tiers(args.company_tiers)
    publish_date, publish_date_from, publish_date_to = _resolve_publish_date_filters(args)
    job_ids = set(_normalize_job_ids(args.job_ids)) or None
    result = run_resume_step(
        run_dir=run_dir,
        jobs_json=Path(args.jobs_json),
        max_jobs=args.max_jobs,
        force_all=args.force_all,
        dry_run=args.dry_run,
        enable_llm=args.enable_llm,
        provider_settings=provider_settings,
        publish_portfolio=args.publish_portfolio,
        no_state_update=args.no_state_update,
        new_seed_mode=args.new_seed_mode,
        portfolio_root=Path(args.portfolio_root),
        company_tiers=company_tiers,
        publish_date=publish_date,
        publish_date_from=publish_date_from,
        publish_date_to=publish_date_to,
        max_runtime_minutes=args.max_runtime_minutes,
        job_ids=job_ids,
    )
    print(json.dumps({"run_dir": str(run_dir), "manifest_path": str(result["manifest_path"]), **result["summary"]}, indent=2, ensure_ascii=False))


def command_pdf(args: argparse.Namespace) -> None:
    run_dir = make_run_dir("pdf", args.run_dir)
    resume_md = Path(args.resume_md) if args.resume_md else None
    output_dir = Path(args.output_dir) if args.output_dir else None
    run_manifest = Path(args.run_manifest) if args.run_manifest else None
    summary = run_pdf_step(
        run_dir=run_dir,
        run_manifest=run_manifest,
        resume_md=resume_md,
        output_dir=output_dir,
        profiles_path=Path(args.profiles_json),
        portfolio_root=Path(args.portfolio_root),
        dry_run=args.dry_run,
    )
    print(json.dumps({"run_dir": str(run_dir), **summary}, indent=2, ensure_ascii=False))


def command_all(args: argparse.Namespace) -> None:
    run_dir = make_run_dir("all", args.run_dir)
    jobs_dir = ensure_dir(run_dir / "jobs_step")
    resume_dir = ensure_dir(run_dir / "resume_step")
    pdf_dir = ensure_dir(run_dir / "pdf_step")

    jobs_summary = run_jobs_step(
        run_dir=jobs_dir,
        jobs_json=Path(args.jobs_json),
        skip_scrape=args.skip_scrape,
        lookback_hours=args.lookback_hours,
        allow_existing_json=args.allow_existing_json,
    )
    provider_settings = relabel_provider(args.provider, args.write_model, args.review_model, args.llm_transport)
    company_tiers = _normalize_company_tiers(args.company_tiers)
    publish_date, publish_date_from, publish_date_to = _resolve_publish_date_filters(args)
    job_ids = set(_normalize_job_ids(args.job_ids)) or None
    resume_result = run_resume_step(
        run_dir=resume_dir,
        jobs_json=Path(jobs_summary["jobs_json"]),
        max_jobs=args.max_jobs,
        force_all=args.force_all,
        dry_run=args.dry_run,
        enable_llm=args.enable_llm,
        provider_settings=provider_settings,
        publish_portfolio=args.publish_portfolio,
        no_state_update=args.no_state_update,
        new_seed_mode=args.new_seed_mode,
        portfolio_root=Path(args.portfolio_root),
        company_tiers=company_tiers,
        publish_date=publish_date,
        publish_date_from=publish_date_from,
        publish_date_to=publish_date_to,
        max_runtime_minutes=args.max_runtime_minutes,
        job_ids=job_ids,
    )

    pdf_summary = run_pdf_step(
        run_dir=pdf_dir,
        run_manifest=resume_result["manifest_path"],
        resume_md=None,
        output_dir=None,
        profiles_path=Path(args.profiles_json),
        portfolio_root=Path(args.portfolio_root),
        dry_run=args.dry_run,
    )

    combined = {
        "run_dir": str(run_dir),
        "jobs_summary": jobs_summary,
        "resume_manifest_path": str(resume_result["manifest_path"]),
        "resume_summary": resume_result["summary"],
        "pdf_summary": pdf_summary,
    }
    write_json(run_dir / "all_summary.json", combined)
    print(json.dumps(combined, indent=2, ensure_ascii=False))


def command_state(args: argparse.Namespace) -> None:
    state = load_resume_state()
    processed_ids = {str(item) for item in state.get("processed_ids", []) or []}

    if args.state_action == "show":
        payload = {
            "state_file": str(STATE_FILE),
            "processed_count": len(processed_ids),
            "processed_ids": sorted(processed_ids),
            "last_run": str(state.get("last_run", "") or ""),
            "last_run_manifest": str(state.get("last_run_manifest", "") or ""),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    if args.state_action == "clear":
        updated = {
            "processed_ids": [],
            "last_run": "",
            "last_run_manifest": "",
        }
        save_resume_state(updated)
        print(json.dumps({"state_file": str(STATE_FILE), "cleared": True}, indent=2, ensure_ascii=False))
        return

    target_ids = set(_normalize_job_ids(args.job_ids))
    if not target_ids:
        raise ValueError("At least one --job-id is required for this state action.")

    if args.state_action == "remove":
        updated_ids = sorted(processed_ids - target_ids)
        state["processed_ids"] = updated_ids
        save_resume_state(state)
        print(
            json.dumps(
                {
                    "state_file": str(STATE_FILE),
                    "action": "remove",
                    "requested_job_ids": sorted(target_ids),
                    "remaining_processed_count": len(updated_ids),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    if args.state_action == "add":
        updated_ids = sorted(processed_ids | target_ids)
        state["processed_ids"] = updated_ids
        save_resume_state(state)
        print(
            json.dumps(
                {
                    "state_file": str(STATE_FILE),
                    "action": "add",
                    "requested_job_ids": sorted(target_ids),
                    "processed_count": len(updated_ids),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    raise ValueError(f"Unsupported state action: {args.state_action}")


def add_common_resume_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--jobs-json", default=str(DEFAULT_JOBS_JSON))
    parser.add_argument("--max-jobs", type=int, default=0, help="Maximum jobs to process; 0 means no limit.")
    parser.add_argument("--force-all", action="store_true")
    parser.add_argument("--job-id", dest="job_ids", action="append", default=[], help="Only process specific job_id values.")
    parser.add_argument(
        "--company-tier",
        dest="company_tiers",
        action="append",
        default=["large"],
        help="Filter by company tier. Default is large only. Repeatable or comma-separated.",
    )
    parser.add_argument("--publish-date", default="", help="Only process jobs published on YYYY-MM-DD.")
    parser.add_argument("--publish-date-from", default="", help="Only process jobs published on/after YYYY-MM-DD.")
    parser.add_argument("--publish-date-to", default="", help="Only process jobs published on/before YYYY-MM-DD.")
    parser.add_argument(
        "--max-runtime-minutes",
        type=int,
        default=0,
        help="Stop the generation loop after this many minutes. 0 means no runtime limit.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--enable-llm", action="store_true")
    parser.add_argument("--provider", choices=PROVIDER_CHOICES, default="codex")
    parser.add_argument("--write-model", default=None)
    parser.add_argument("--review-model", default=None)
    parser.add_argument("--llm-transport", default=None)
    parser.add_argument("--publish-portfolio", action="store_true")
    parser.add_argument("--portfolio-root", default=str(DEFAULT_PORTFOLIO_ROOT))
    parser.add_argument("--new-seed-mode", choices=["free_write", "skip"], default="free_write")
    parser.add_argument("--no-state-update", action="store_true")
    parser.add_argument("--run-dir", default="")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Unified local job -> resume -> PDF pipeline around the current stable deliverables stack."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    jobs_parser = subparsers.add_parser("jobs", help="Run local job scraping and refresh jobs_catalog.json.")
    jobs_parser.add_argument("--jobs-json", default=str(DEFAULT_JOBS_JSON))
    jobs_parser.add_argument("--lookback-hours", type=int, default=8)
    jobs_parser.add_argument("--skip-scrape", action="store_true")
    jobs_parser.add_argument("--allow-existing-json", action="store_true", default=True)
    jobs_parser.add_argument("--run-dir", default="")
    jobs_parser.set_defaults(func=command_jobs)

    resume_parser = subparsers.add_parser("resume", help="Screen and route local jobs; optionally generate resumes.")
    add_common_resume_args(resume_parser)
    resume_parser.set_defaults(func=command_resume)

    pdf_parser = subparsers.add_parser("pdf", help="Compile PDFs for the latest resume run or an explicit markdown file.")
    pdf_parser.add_argument("--run-manifest", default="")
    pdf_parser.add_argument("--resume-md", default="")
    pdf_parser.add_argument("--output-dir", default="")
    pdf_parser.add_argument("--profiles-json", default=str(DEFAULT_PROFILES_JSON))
    pdf_parser.add_argument("--portfolio-root", default=str(DEFAULT_PORTFOLIO_ROOT))
    pdf_parser.add_argument("--dry-run", action="store_true")
    pdf_parser.add_argument("--run-dir", default="")
    pdf_parser.set_defaults(func=command_pdf)

    state_parser = subparsers.add_parser("state", help="Inspect or edit resume backlog processing state.")
    state_subparsers = state_parser.add_subparsers(dest="state_action", required=True)

    state_show_parser = state_subparsers.add_parser("show", help="Show processed job ids and last-run metadata.")
    state_show_parser.set_defaults(func=command_state)

    state_clear_parser = state_subparsers.add_parser("clear", help="Clear all processed job ids.")
    state_clear_parser.set_defaults(func=command_state)

    state_remove_parser = state_subparsers.add_parser("remove", help="Remove specific job ids from processed state.")
    state_remove_parser.add_argument("--job-id", dest="job_ids", action="append", default=[])
    state_remove_parser.set_defaults(func=command_state)

    state_add_parser = state_subparsers.add_parser("add", help="Mark specific job ids as already processed.")
    state_add_parser.add_argument("--job-id", dest="job_ids", action="append", default=[])
    state_add_parser.set_defaults(func=command_state)

    all_parser = subparsers.add_parser("all", help="Run jobs -> resume -> PDF in one local command.")
    all_parser.add_argument("--jobs-json", default=str(DEFAULT_JOBS_JSON))
    all_parser.add_argument("--lookback-hours", type=int, default=8)
    all_parser.add_argument("--skip-scrape", action="store_true")
    all_parser.add_argument("--allow-existing-json", action="store_true", default=True)
    all_parser.add_argument("--max-jobs", type=int, default=0, help="Maximum jobs to process; 0 means no limit.")
    all_parser.add_argument("--force-all", action="store_true")
    all_parser.add_argument("--job-id", dest="job_ids", action="append", default=[], help="Only process specific job_id values.")
    all_parser.add_argument(
        "--company-tier",
        dest="company_tiers",
        action="append",
        default=["large"],
        help="Filter by company tier. Default is large only. Repeatable or comma-separated.",
    )
    all_parser.add_argument("--publish-date", default="", help="Only process jobs published on YYYY-MM-DD.")
    all_parser.add_argument("--publish-date-from", default="", help="Only process jobs published on/after YYYY-MM-DD.")
    all_parser.add_argument("--publish-date-to", default="", help="Only process jobs published on/before YYYY-MM-DD.")
    all_parser.add_argument(
        "--max-runtime-minutes",
        type=int,
        default=0,
        help="Stop the generation loop after this many minutes. 0 means no runtime limit.",
    )
    all_parser.add_argument("--dry-run", action="store_true")
    all_parser.add_argument("--enable-llm", action="store_true")
    all_parser.add_argument("--provider", choices=PROVIDER_CHOICES, default="codex")
    all_parser.add_argument("--write-model", default=None)
    all_parser.add_argument("--review-model", default=None)
    all_parser.add_argument("--llm-transport", default=None)
    all_parser.add_argument("--publish-portfolio", action="store_true")
    all_parser.add_argument("--portfolio-root", default=str(DEFAULT_PORTFOLIO_ROOT))
    all_parser.add_argument("--profiles-json", default=str(DEFAULT_PROFILES_JSON))
    all_parser.add_argument("--new-seed-mode", choices=["free_write", "skip"], default="free_write")
    all_parser.add_argument("--no-state-update", action="store_true")
    all_parser.add_argument("--run-dir", default="")
    all_parser.set_defaults(func=command_all)

    return parser


def main() -> None:
    ensure_dir(RUNS_ROOT)
    ensure_dir(STATE_ROOT)
    if os.environ.get("MANAGED_RUN_ACTIVE", "").strip() != "1" and len(sys.argv) > 1:
        command_name = str(sys.argv[1] or "").strip()
        if command_name in {"jobs", "resume", "pdf", "all"}:
            labels = {
                "jobs": ("jobs_only", "Jobs Only", "scrape_only"),
                "resume": ("resume_only", "Resume Only", "resume_only"),
                "pdf": ("pdf_latest", "PDF Latest", "pdf_latest"),
                "all": ("daily_full_pipeline", "Daily Full Pipeline", "daily_full_pipeline"),
            }
            label, display_name, preset_id = labels[command_name]
            if command_name == "all" and "--skip-scrape" in sys.argv and "--force-all" in sys.argv:
                label, display_name = ("full_table_generate", "Full Table Generate")
            os.execv(
                sys.executable,
                [
                    sys.executable,
                    str(PROJECT_ROOT / "managed_run.py"),
                    "--label",
                    label,
                    "--display-name",
                    display_name,
                    "--cwd",
                    str(PROJECT_ROOT),
                    "--preset-id",
                    preset_id,
                    "--",
                    sys.executable,
                    str(PROJECT_ROOT / "pipeline.py"),
                    *sys.argv[1:],
                ],
            )
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
