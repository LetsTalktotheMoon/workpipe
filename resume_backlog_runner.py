#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
RUNTIME_ROOT = ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from rereview_resume_portfolio import UNIFIED_REWRITE_VERSION
from job_webapp.main import JobAppStore


_TIER_LABELS: dict[str, set[str]] = {
    "large": {"大厂(10000+)"},
    "mid": {"中厂(1001-5000)", "中厂(501-1000)"},
    "small": {"小厂(≤500)"},
}


def _append_company_tiers(command: list[str], tiers: list[str]) -> list[str]:
    normalized: list[str] = []
    for tier in tiers or ["large"]:
        value = str(tier or "").strip().lower()
        if value == "large":
            normalized.append("large")
        elif value == "mid":
            normalized.extend(["mid_large", "mid_small"])
        elif value == "small":
            normalized.append("small")
    seen: set[str] = set()
    for item in normalized:
        if item not in seen:
            seen.add(item)
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


def _parse_date(value: str) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    return datetime.strptime(text, "%Y-%m-%d").date()


def _matches_date(job: dict[str, Any], *, publish_date: date | None, publish_date_from: date | None, publish_date_to: date | None) -> bool:
    raw = str(job.get("publish_date", "") or "").strip()
    if not raw:
        return False
    job_date = _parse_date(raw)
    if job_date is None:
        return False
    if publish_date is not None:
        return job_date == publish_date
    if publish_date_from is not None and job_date < publish_date_from:
        return False
    if publish_date_to is not None and job_date > publish_date_to:
        return False
    return True


def _collect_missing_resume_job_ids(*, tiers: list[str], publish_date_text: str, publish_date_from_text: str, publish_date_to_text: str) -> list[str]:
    store = JobAppStore()
    jobs = store.build_jobs_payload().get("jobs", [])
    allowed_labels: set[str] = set()
    for tier in tiers or ["large"]:
        allowed_labels.update(_TIER_LABELS.get(str(tier or "").strip().lower(), set()))
    publish_date = _parse_date(publish_date_text)
    publish_date_from = _parse_date(publish_date_from_text)
    publish_date_to = _parse_date(publish_date_to_text)

    selected: list[str] = []
    for job in jobs:
        if allowed_labels and str(job.get("company_size_label", "") or "") not in allowed_labels:
            continue
        if not _matches_date(
            job,
            publish_date=publish_date,
            publish_date_from=publish_date_from,
            publish_date_to=publish_date_to,
        ):
            continue
        if str(job.get("review_status", "") or "") != "无简历":
            continue
        job_id = str(job.get("job_id", "") or "").strip()
        if job_id:
            selected.append(job_id)
    return selected


def _run_stage(name: str, command: list[str], *, log_path: Path) -> dict[str, Any]:
    print(f"\n=== {name} ===")
    print("COMMAND:", " ".join(command))
    completed = subprocess.run(
        command,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        env=os.environ.copy(),
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    log_path.write_text(output, encoding="utf-8")
    if completed.stdout:
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
    if completed.stderr:
        print(completed.stderr, end="" if completed.stderr.endswith("\n") else "\n", file=sys.stderr)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return {
        "name": name,
        "command": command,
        "returncode": completed.returncode,
        "log_path": str(log_path),
    }


def _skip_stage(name: str, *, log_path: Path, reason: str) -> dict[str, Any]:
    payload = {"name": name, "status": "skipped", "reason": reason}
    log_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return payload


def main() -> None:
    if os.environ.get("MANAGED_RUN_ACTIVE", "").strip() != "1" and len(sys.argv) > 1:
        os.execv(
            sys.executable,
            [
                sys.executable,
                str(ROOT / "managed_run.py"),
                "--label",
                "resume_backlog",
                "--display-name",
                "Resume Backlog Continuation",
                "--cwd",
                str(ROOT),
                "--preset-id",
                "resume_backlog",
                "--",
                sys.executable,
                str(ROOT / "resume_backlog_runner.py"),
                *sys.argv[1:],
            ],
        )

    parser = argparse.ArgumentParser(description="Continue new-pipeline resume backlog until pass or hard reject.")
    parser.add_argument("--company-tier", dest="company_tiers", action="append", default=["large"])
    parser.add_argument("--publish-date", default="")
    parser.add_argument("--publish-date-from", default="")
    parser.add_argument("--publish-date-to", default="")
    parser.add_argument("--write-model", default="gpt-5.4")
    parser.add_argument("--review-model", default="gpt-5.4-mini")
    parser.add_argument("--llm-transport", default="cli")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--run-dir", default="")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve() if str(args.run_dir or "").strip() else (
        ROOT / "runs" / f"resume_backlog_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    run_dir.mkdir(parents=True, exist_ok=True)

    tiers = [str(item or "").strip() for item in args.company_tiers if str(item or "").strip()]
    publish_date_text = str(args.publish_date or "")
    publish_date_from_text = str(args.publish_date_from or "")
    publish_date_to_text = str(args.publish_date_to or "")
    missing_resume_job_ids = _collect_missing_resume_job_ids(
        tiers=tiers or ["large"],
        publish_date_text=publish_date_text,
        publish_date_from_text=publish_date_from_text,
        publish_date_to_text=publish_date_to_text,
    )

    resume_command = [
        sys.executable,
        str(ROOT / "pipeline.py"),
        "resume",
        "--enable-llm",
        "--publish-portfolio",
        "--provider",
        "codex",
        "--write-model",
        args.write_model,
        "--review-model",
        args.review_model,
        "--llm-transport",
        args.llm_transport,
        "--run-dir",
        str(run_dir / "resume_phase"),
        "--force-all",
    ]
    if args.dry_run:
        resume_command.append("--dry-run")
    resume_command = _append_company_tiers(resume_command, tiers)
    resume_command = _append_date_filters(resume_command, publish_date_text or publish_date_from_text, publish_date_to_text)
    for job_id in missing_resume_job_ids:
        resume_command.extend(["--job-id", job_id])

    rewrite_command = [
        sys.executable,
        str(ROOT / "rereview_resume_portfolio.py"),
        "--source-scope",
        "unified_only",
        "--status-scope",
        "non_pass_only",
        "--review-version",
        UNIFIED_REWRITE_VERSION,
        "--write-model",
        args.write_model,
        "--review-model",
        args.review_model,
        "--llm-transport",
        args.llm_transport,
    ]
    if args.dry_run:
        rewrite_command.append("--dry-run")
    rewrite_command = _append_company_tiers(rewrite_command, tiers)
    rewrite_command = _append_date_filters(rewrite_command, publish_date_text or publish_date_from_text, publish_date_to_text)

    pdf_command = [
        sys.executable,
        str(ROOT / "portfolio_pdf_backfill.py"),
        "--source-scope",
        "unified_only",
        "--run-dir",
        str(run_dir / "pdf_phase"),
    ]
    if args.dry_run:
        pdf_command.append("--dry-run")
    pdf_command = _append_company_tiers(pdf_command, tiers)
    pdf_command = _append_date_filters(pdf_command, publish_date_text or publish_date_from_text, publish_date_to_text)

    stages = [
        _run_stage("resume_generation", resume_command, log_path=run_dir / "resume_generation.log")
        if missing_resume_job_ids
        else _skip_stage(
            "resume_generation",
            log_path=run_dir / "resume_generation.log",
            reason="no jobs currently in 无简历 state for the selected filters",
        ),
        _run_stage("rewrite_non_pass", rewrite_command, log_path=run_dir / "rewrite_non_pass.log"),
        _run_stage("pdf_backfill", pdf_command, log_path=run_dir / "pdf_backfill.log"),
    ]

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "stages": stages,
        "tiers": tiers or ["large"],
        "publish_date": publish_date_text,
        "publish_date_from": publish_date_from_text,
        "publish_date_to": publish_date_to_text,
        "missing_resume_job_ids": missing_resume_job_ids,
    }
    (run_dir / "resume_backlog_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
