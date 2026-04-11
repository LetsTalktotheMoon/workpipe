#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from compare_reuse_target_reviews import (
    DEFAULT_CASES_FILE,
    build_rerun_payload,
    build_target_jd,
    compare_delta,
    format_score,
    load_json,
    load_source_artifacts,
    load_target_existing_review,
    normalize_review_payload,
    read_text,
    slugify_label,
    write_json,
)
from core.anthropic_client import LLMUnavailableError, configure_llm_client
from models.jd import JDProfile
from reviewers.unified_reviewer import UnifiedReviewer


DEFAULT_OUTPUT_DIR = ROOT / "output" / "claude_reuse_source_target_full_review"
LIMIT_SLEEP_SECONDS = 5 * 60 * 60
LIMIT_ERROR_TOKENS = (
    "5-hour",
    "5 hour",
    "hit your limit",
    "you've hit your limit",
    "resets ",
    "usage limit",
    "rate limit",
    "quota",
    "credit balance",
    "too many requests",
    "capacity",
    "exceeded",
)
AUTH_ERROR_TOKENS = (
    "401",
    "authentication_error",
    "invalid authentication credentials",
    "failed to authenticate",
    "unauthorized",
)


def build_source_jd(case: dict[str, Any], source_artifacts: dict[str, Any]) -> JDProfile:
    jd_text = read_text(Path(str(source_artifacts["job_path"])).resolve())
    manifest = source_artifacts.get("manifest") or {}
    company_name = str(manifest.get("company_name", "") or "")
    return JDProfile.from_text(jd_text, jd_id=str(case.get("source_id", "") or ""), company=company_name)


def looks_like_limit_error(exc: Exception) -> bool:
    text = str(exc or "").lower()
    return any(token in text for token in LIMIT_ERROR_TOKENS)


def looks_like_auth_error(exc: Exception) -> bool:
    text = str(exc or "").lower()
    return any(token in text for token in AUTH_ERROR_TOKENS)


def maybe_sleep_for_limit(
    *,
    label: str,
    stage: str,
    exc: Exception | None = None,
    resume_after_seconds: int,
) -> None:
    reason = str(exc) if exc else "approaching configured pause threshold"
    wake_at = datetime.now().timestamp() + resume_after_seconds
    wake_at_text = datetime.fromtimestamp(wake_at).isoformat(timespec="seconds")
    print(
        f"{label}\tstage={stage}\taction=sleep\treason={reason}\twake_at={wake_at_text}",
        flush=True,
    )
    time.sleep(resume_after_seconds)


def write_report(output_dir: Path, case_results: list[dict[str, Any]]) -> None:
    ordered = sorted(case_results, key=lambda item: item.get("label", ""))
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "case_count": len(ordered),
        "cases": ordered,
    }
    write_json(output_dir / "results.json", payload)

    lines = [
        "# Claude Reuse Source/Target Full Review",
        "",
        "| Case | Status | Source JD | Target JD | Delta |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for item in ordered:
        source_review = normalize_review_payload(item.get("source_claude_review"))
        target_review = normalize_review_payload(item.get("target_claude_review"))
        lines.append(
            f"| {item.get('label', '')} | {item.get('status', '')} | "
            f"{format_score(source_review.get('final_score'))} | "
            f"{format_score(target_review.get('final_score'))} | "
            f"{format_score(item.get('delta'))} |"
        )
    lines.append("")
    for item in ordered:
        source_review = normalize_review_payload(item.get("source_claude_review"))
        target_review = normalize_review_payload(item.get("target_claude_review"))
        lines.extend(
            [
                f"## {item.get('label', '')}",
                f"- Status: {item.get('status', '')}",
                f"- Source JD score: {format_score(source_review.get('final_score'))} ({source_review.get('verdict', '')})",
                f"- Target JD score: {format_score(target_review.get('final_score'))} ({target_review.get('verdict', '')})",
                f"- Delta: {format_score(item.get('delta'))}",
            ]
        )
        if item.get("error"):
            lines.append(f"- Error: {item['error']}")
        lines.append("")
    (output_dir / "results.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def review_one(
    *,
    reviewer: UnifiedReviewer,
    label: str,
    stage: str,
    resume_md: str,
    jd: JDProfile,
    resume_after_seconds: int,
    pause_after_seconds: int,
    last_pause_monotonic: float,
) -> tuple[dict[str, Any], float]:
    while True:
        if pause_after_seconds > 0 and (time.monotonic() - last_pause_monotonic) >= pause_after_seconds:
            maybe_sleep_for_limit(
                label=label,
                stage=stage,
                exc=None,
                resume_after_seconds=resume_after_seconds,
            )
            last_pause_monotonic = time.monotonic()
        try:
            completed_at = datetime.now()
            review = reviewer.review(resume_md, jd, mode="full")
            return build_rerun_payload(review, jd=jd, completed_at=completed_at), last_pause_monotonic
        except LLMUnavailableError as exc:
            print(f"{label}\tstage={stage}\tretryable_error={exc}", flush=True)
            if not looks_like_limit_error(exc) and not looks_like_auth_error(exc):
                raise
            maybe_sleep_for_limit(
                label=label,
                stage=stage,
                exc=exc,
                resume_after_seconds=resume_after_seconds,
            )
            last_pause_monotonic = time.monotonic()
        except Exception as exc:
            print(f"{label}\tstage={stage}\tretryable_error={exc}", flush=True)
            if not looks_like_limit_error(exc) and not looks_like_auth_error(exc):
                raise
            maybe_sleep_for_limit(
                label=label,
                stage=stage,
                exc=exc,
                resume_after_seconds=resume_after_seconds,
            )
            last_pause_monotonic = time.monotonic()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run production full-review scoring against source JD and target JD using Claude Sonnet 4.6."
    )
    parser.add_argument("--cases-file", default=str(DEFAULT_CASES_FILE))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--label", action="append", default=[], help="Only run matching case label(s). Repeatable.")
    parser.add_argument("--force-rerun", action="store_true")
    parser.add_argument("--review-model", default="claude-sonnet-4-6")
    parser.add_argument("--write-model", default="claude-sonnet-4-6")
    parser.add_argument("--resume-after-seconds", type=int, default=LIMIT_SLEEP_SECONDS)
    parser.add_argument(
        "--pause-after-seconds",
        type=int,
        default=0,
        help="Optional proactive pause threshold before sleeping and resuming later. 0 disables proactive pausing.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cases_path = Path(args.cases_file).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    cases_output_dir = output_dir / "cases"
    cases_output_dir.mkdir(parents=True, exist_ok=True)

    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    if args.label:
        labels = {item.strip() for item in args.label if item.strip()}
        cases = [case for case in cases if str(case.get("label", "") or "") in labels]
    if args.limit > 0:
        cases = cases[: args.limit]

    configure_llm_client(
        enabled=True,
        write_model=args.write_model,
        review_model=args.review_model,
        transport="claude",
    )
    reviewer = UnifiedReviewer()

    results_by_label: dict[str, dict[str, Any]] = {}
    for existing in sorted(cases_output_dir.glob("*.json")):
        payload = load_json(existing)
        label = str(payload.get("label", "") or "")
        if label:
            results_by_label[label] = payload

    last_pause_monotonic = time.monotonic()
    for index, case in enumerate(cases, start=1):
        label = str(case.get("label", "") or f"case_{index}")
        print(f"[{index}/{len(cases)}] {label}", flush=True)

        output_case_path = cases_output_dir / f"{slugify_label(label)}.json"
        prior_case = load_json(output_case_path) if output_case_path.exists() else {}
        source_artifacts = load_source_artifacts(case)
        target_existing = load_target_existing_review(case)

        result: dict[str, Any] = {
            "label": label,
            "seed_label": str(case.get("seed_label", "") or ""),
            "source_id": str(case.get("source_id", "") or ""),
            "target_job_id": str(case.get("job_id", "") or ""),
            "resume_path": str(Path(str(case.get("resume_path", ""))).resolve()),
            "source_jd_path": source_artifacts.get("job_path", ""),
            "target_jd_path": str(Path(str(case.get("target_jd_path", ""))).resolve()),
            "source_portfolio_review": source_artifacts.get("review") or {},
            "target_portfolio_review": target_existing.get("review") or {},
            "source_claude_review": prior_case.get("source_claude_review") or {},
            "target_claude_review": prior_case.get("target_claude_review") or {},
            "status": prior_case.get("status", "pending") or "pending",
            "error": "",
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }

        resume_md = read_text(Path(result["resume_path"]))
        source_jd = build_source_jd(case, source_artifacts)
        target_jd = build_target_jd(case, target_existing.get("manifest") or {})

        source_done = bool(result["source_claude_review"]) and not args.force_rerun
        target_done = bool(result["target_claude_review"]) and not args.force_rerun

        try:
            if not source_done:
                result["status"] = "running_source"
                write_json(output_case_path, result)
                source_review, last_pause_monotonic = review_one(
                    reviewer=reviewer,
                    label=label,
                    stage="source_jd",
                    resume_md=resume_md,
                    jd=source_jd,
                    resume_after_seconds=args.resume_after_seconds,
                    pause_after_seconds=args.pause_after_seconds,
                    last_pause_monotonic=last_pause_monotonic,
                )
                result["source_claude_review"] = source_review
                write_json(output_case_path, result)

            if not target_done:
                result["status"] = "running_target"
                write_json(output_case_path, result)
                target_review, last_pause_monotonic = review_one(
                    reviewer=reviewer,
                    label=label,
                    stage="target_jd",
                    resume_md=resume_md,
                    jd=target_jd,
                    resume_after_seconds=args.resume_after_seconds,
                    pause_after_seconds=args.pause_after_seconds,
                    last_pause_monotonic=last_pause_monotonic,
                )
                result["target_claude_review"] = target_review
                write_json(output_case_path, result)

            result["status"] = "completed"
        except Exception as exc:
            result["status"] = "error"
            result["error"] = str(exc)

        source_score = normalize_review_payload(result.get("source_claude_review")).get("final_score")
        target_score = normalize_review_payload(result.get("target_claude_review")).get("final_score")
        result["delta"] = compare_delta(source_score, target_score)
        result["updated_at"] = datetime.now().isoformat(timespec="seconds")
        write_json(output_case_path, result)
        results_by_label[label] = result
        write_report(output_dir, list(results_by_label.values()))

        source_verdict = normalize_review_payload(result.get("source_claude_review")).get("verdict", "")
        target_verdict = normalize_review_payload(result.get("target_claude_review")).get("verdict", "")
        print(
            f"{label}\tstatus={result['status']}\t"
            f"source={format_score(source_score)}({source_verdict})\t"
            f"target={format_score(target_score)}({target_verdict})\t"
            f"delta={format_score(result.get('delta'))}",
            flush=True,
        )
        if result.get("error"):
            print(f"{label}\terror={result['error']}", flush=True)

    print("", flush=True)
    print(f"Results JSON: {output_dir / 'results.json'}", flush=True)
    print(f"Results MD:   {output_dir / 'results.md'}", flush=True)


if __name__ == "__main__":
    main()
