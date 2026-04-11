#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_REVIEW_VERSION = "row_action_v1"


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Run write-review-PDF pipeline for one job.")
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--action", required=True, choices=["generate", "rewrite"])
    parser.add_argument("--write-model", default="gpt-5.4")
    parser.add_argument("--review-model", default="gpt-5.4-mini")
    parser.add_argument("--llm-transport", default="cli")
    parser.add_argument("--run-dir", default="")
    args = parser.parse_args()

    job_id = str(args.job_id or "").strip()
    run_dir = Path(args.run_dir).expanduser().resolve() if str(args.run_dir or "").strip() else (
        ROOT / "runs" / f"job_{args.action}_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    run_dir.mkdir(parents=True, exist_ok=True)

    stages: list[dict[str, Any]] = []

    if args.action == "generate":
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
            "--force-all",
            "--company-tier",
            "all",
            "--job-id",
            job_id,
            "--run-dir",
            str(run_dir / "resume_phase"),
        ]
        stages.append(_run_stage("generate_resume", resume_command, log_path=run_dir / "generate_resume.log"))
    else:
        rewrite_command = [
            sys.executable,
            str(ROOT / "rereview_resume_portfolio.py"),
            "--job-id",
            job_id,
            "--source-scope",
            "all",
            "--status-scope",
            "non_pass_only",
            "--company-tier",
            "all",
            "--review-version",
            DEFAULT_REVIEW_VERSION,
            "--write-model",
            args.write_model,
            "--review-model",
            args.review_model,
            "--llm-transport",
            args.llm_transport,
        ]
        stages.append(_run_stage("rewrite_resume", rewrite_command, log_path=run_dir / "rewrite_resume.log"))

    pdf_command = [
        sys.executable,
        str(ROOT / "portfolio_pdf_backfill.py"),
        "--job-id",
        job_id,
        "--source-scope",
        "all",
        "--company-tier",
        "all",
        "--run-dir",
        str(run_dir / "pdf_phase"),
    ]
    stages.append(_run_stage("pdf_backfill", pdf_command, log_path=run_dir / "pdf_backfill.log"))

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "job_id": job_id,
        "action": args.action,
        "stages": stages,
    }
    (run_dir / "single_job_action_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
