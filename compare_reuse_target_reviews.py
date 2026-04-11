#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
RUNTIME_ROOT = ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from core.anthropic_client import LLMUnavailableError, configure_llm_client
from models.jd import JDProfile
from reviewers.unified_reviewer import ReviewSummary, UnifiedReviewer


DEFAULT_CASES_FILE = Path("/tmp/reuse_test_cases.json")
DEFAULT_OUTPUT_DIR = ROOT / "output" / "reuse_target_review_compare"
DEFAULT_WINDOW_HOURS = 3


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def slugify_label(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (label or "").strip().lower()).strip("_") or "case"


def parse_timestamp(raw: Any) -> datetime | None:
    text = str(raw or "").strip()
    if not text:
        return None
    for candidate in (text, text.replace("Z", "+00:00")):
        try:
            dt = datetime.fromisoformat(candidate)
            if dt.tzinfo is not None:
                return dt.replace(tzinfo=None)
            return dt
        except ValueError:
            pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def latest_review_timestamp(review_payload: dict[str, Any]) -> datetime | None:
    candidates = [
        parse_timestamp(review_payload.get("completed_at")),
        parse_timestamp(review_payload.get("rereviewed_at")),
        parse_timestamp(review_payload.get("repaired_at")),
    ]
    valid = [item for item in candidates if item is not None]
    return max(valid) if valid else None


def is_recent_enough(timestamp: datetime | None, *, window_hours: int, now: datetime) -> bool:
    if timestamp is None:
        return False
    return timestamp >= now - timedelta(hours=window_hours)


def review_verdict_label(review_payload: dict[str, Any]) -> str:
    for key in ("overall_verdict", "verdict"):
        value = str(review_payload.get(key, "") or "").strip()
        if value:
            return value
    final_score = review_payload.get("final_score", review_payload.get("weighted_score"))
    if final_score is None:
        return ""
    try:
        return "pass" if float(final_score) >= 93.0 else "fail"
    except (TypeError, ValueError):
        return ""


def normalize_review_payload(review_payload: dict[str, Any] | None) -> dict[str, Any]:
    payload = dict(review_payload or {})
    final_score = payload.get("final_score", payload.get("weighted_score"))
    try:
        payload["final_score"] = round(float(final_score), 1)
    except (TypeError, ValueError):
        payload["final_score"] = None
    payload["verdict"] = review_verdict_label(payload)
    payload["revision_priority"] = list(payload.get("revision_priority") or [])
    payload["revision_instructions"] = str(payload.get("revision_instructions", "") or "")
    payload["latest_timestamp"] = (
        latest_review_timestamp(payload).isoformat(timespec="seconds")
        if latest_review_timestamp(payload)
        else ""
    )
    return payload


def build_rerun_payload(review: ReviewSummary, *, jd: JDProfile, completed_at: datetime) -> dict[str, Any]:
    payload = review.to_dict()
    payload["scores"] = {
        dim_id: {
            "score": round(dim.score, 1),
            "weight": dim.weight,
            "verdict": dim.verdict,
            "findings_count": len(dim.findings),
            "findings": dim.findings,
        }
        for dim_id, dim in review.dimensions.items()
    }
    payload.update(
        {
            "jd_id": jd.jd_id,
            "company": jd.company,
            "title": jd.title,
            "role_type": jd.role_type,
            "final_score": round(review.weighted_score, 1),
            "verdict": "pass" if review.passed else "fail",
            "revision_priority": list(review.revision_priority),
            "revision_instructions": review.revision_instructions,
            "completed_at": completed_at.isoformat(timespec="seconds"),
        }
    )
    return normalize_review_payload(payload)


def resolve_source_dir(source_id: str) -> Path:
    matches = sorted((ROOT / "data" / "deliverables" / "resume_portfolio" / "by_company").glob(f"*/*/{source_id}"))
    if not matches:
        raise FileNotFoundError(f"Unable to locate source_id={source_id} in portfolio/by_company")
    if len(matches) > 1:
        raise RuntimeError(f"Expected one source directory for {source_id}, found {len(matches)}")
    return matches[0]


def load_source_artifacts(case: dict[str, Any]) -> dict[str, Any]:
    source_dir = resolve_source_dir(str(case["source_id"]))
    review_path = source_dir / "review.json"
    job_path = source_dir / "job.md"
    resume_path = source_dir / "resume.md"
    manifest_path = source_dir / "manifest.json"
    review_payload = normalize_review_payload(load_json(review_path)) if review_path.exists() else {}
    manifest = load_json(manifest_path) if manifest_path.exists() else {}
    return {
        "dir": str(source_dir),
        "job_path": str(job_path),
        "resume_path": str(resume_path),
        "job_title": read_text(job_path).splitlines()[0] if job_path.exists() else "",
        "review": review_payload,
        "manifest": manifest,
    }


def load_target_existing_review(case: dict[str, Any]) -> dict[str, Any]:
    target_dir = Path(str(case["resume_path"])).resolve().parent
    review_path = target_dir / "review.json"
    manifest_path = target_dir / "manifest.json"
    manifest = load_json(manifest_path) if manifest_path.exists() else {}
    payload = normalize_review_payload(load_json(review_path)) if review_path.exists() else {}
    return {
        "dir": str(target_dir),
        "review_path": str(review_path),
        "manifest": manifest,
        "review": payload,
    }


def build_target_jd(case: dict[str, Any], target_manifest: dict[str, Any]) -> JDProfile:
    jd_text = read_text(Path(str(case["target_jd_path"])).resolve())
    company_name = str(target_manifest.get("company_name", "") or "")
    return JDProfile.from_text(jd_text, jd_id=str(case.get("job_id", "") or ""), company=company_name)


def compare_delta(source_score: float | None, target_score: float | None) -> float | None:
    if source_score is None or target_score is None:
        return None
    return round(target_score - source_score, 1)


def format_score(value: float | None) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "?"
    return f"{value:.1f}"


def summarize_case_markdown(case_result: dict[str, Any]) -> str:
    source_review = case_result.get("source_review") or {}
    target_review = case_result.get("target_review") or {}
    lines = [
        f"## {case_result['label']}",
        f"- Seed: {case_result.get('seed_label', '')}",
        f"- Status: {case_result.get('status', '')}",
        f"- Source JD: {case_result.get('source_title', '')}",
        f"- Target JD: {case_result.get('target_title', '')}",
        f"- Source score: {format_score(source_review.get('final_score'))} ({source_review.get('verdict', '')})",
        f"- Target score: {format_score(target_review.get('final_score'))} ({target_review.get('verdict', '')})",
        f"- Delta: {format_score(case_result.get('delta'))}",
    ]
    if case_result.get("error"):
        lines.append(f"- Error: {case_result['error']}")
    lines.append("")
    lines.append("### Source reviewer suggestions")
    if source_review.get("revision_priority"):
        for item in source_review["revision_priority"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    if source_review.get("revision_instructions"):
        lines.append("")
        lines.append("```text")
        lines.append(source_review["revision_instructions"])
        lines.append("```")
    lines.append("")
    lines.append("### Target reviewer suggestions")
    if target_review.get("revision_priority"):
        for item in target_review["revision_priority"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    if target_review.get("revision_instructions"):
        lines.append("")
        lines.append("```text")
        lines.append(target_review["revision_instructions"])
        lines.append("```")
    lines.append("")
    return "\n".join(lines)


def write_report(output_dir: Path, case_results: list[dict[str, Any]]) -> None:
    ordered = sorted(case_results, key=lambda item: item["label"])
    summary_rows = []
    for item in ordered:
        source_review = item.get("source_review") or {}
        target_review = item.get("target_review") or {}
        summary_rows.append(
            {
                "label": item["label"],
                "status": item.get("status", ""),
                "source_score": source_review.get("final_score"),
                "target_score": target_review.get("final_score"),
                "delta": item.get("delta"),
                "source_verdict": source_review.get("verdict", ""),
                "target_verdict": target_review.get("verdict", ""),
                "error": item.get("error", ""),
            }
        )

    write_json(
        output_dir / "results.json",
        {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "case_count": len(ordered),
            "cases": ordered,
            "summary": summary_rows,
        },
    )

    lines = [
        "# Reuse Target Review Compare",
        "",
        "| Case | Status | Source | Target | Delta |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['label']} | {row['status']} | "
            f"{format_score(row['source_score'])} | {format_score(row['target_score'])} | {format_score(row['delta'])} |"
        )
    lines.append("")
    for item in ordered:
        lines.append(summarize_case_markdown(item))
    (output_dir / "results.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def sync_target_artifacts(case_result: dict[str, Any]) -> None:
    review_payload = dict(case_result.get("target_review") or {})
    review_path_raw = str(case_result.get("target_review_path", "") or "").strip()
    manifest_path_raw = str(case_result.get("target_manifest_path", "") or "").strip()
    if not review_payload or not review_path_raw:
        return
    review_path = Path(review_path_raw).expanduser()
    manifest_path = Path(manifest_path_raw).expanduser() if manifest_path_raw else None

    write_json(review_path, review_payload)
    if manifest_path and manifest_path.exists():
        manifest = load_json(manifest_path)
        manifest["review"] = review_payload
        if review_payload.get("final_score") is not None:
            manifest["review_final_score"] = review_payload.get("final_score")
        if review_payload.get("verdict"):
            manifest["review_verdict"] = review_payload.get("verdict")
        write_json(manifest_path, manifest)


def run_case(
    case: dict[str, Any],
    *,
    reviewer: UnifiedReviewer,
    output_case_path: Path,
    now: datetime,
    window_hours: int,
    force_rerun: bool,
    dry_run: bool,
) -> dict[str, Any]:
    source_artifacts = load_source_artifacts(case)
    target_existing = load_target_existing_review(case)
    prior_case_payload = load_json(output_case_path) if output_case_path.exists() else {}

    source_review = normalize_review_payload(source_artifacts.get("review"))
    existing_target_review = normalize_review_payload(target_existing.get("review"))
    prior_target_review = normalize_review_payload(prior_case_payload.get("target_review"))

    source_title = source_artifacts.get("job_title", "")
    target_title = read_text(Path(str(case["target_jd_path"])).resolve()).splitlines()[0]

    prior_case_ts = latest_review_timestamp(prior_case_payload)
    target_review_ts = latest_review_timestamp(existing_target_review)

    result: dict[str, Any] = {
        "label": str(case.get("label", "")),
        "seed_label": str(case.get("seed_label", "") or ""),
        "same_company": bool(case.get("same_company", False)),
        "source_id": str(case.get("source_id", "") or ""),
        "target_job_id": str(case.get("job_id", "") or ""),
        "source_title": source_title.lstrip("# ").strip(),
        "target_title": target_title.lstrip("# ").strip(),
        "source_resume_path": source_artifacts.get("resume_path", ""),
        "target_resume_path": str(Path(str(case["resume_path"])).resolve()),
        "source_jd_path": source_artifacts.get("job_path", ""),
        "target_jd_path": str(Path(str(case["target_jd_path"])).resolve()),
        "target_review_path": target_existing.get("review_path", ""),
        "target_manifest_path": str((Path(str(case["resume_path"])).resolve().parent / "manifest.json")),
        "source_review": source_review,
        "target_review": {},
        "status": "",
        "error": "",
        "completed_at": now.isoformat(timespec="seconds"),
    }

    target_review: dict[str, Any]
    if not force_rerun and prior_target_review and is_recent_enough(prior_case_ts, window_hours=window_hours, now=now):
        target_review = prior_target_review
        result["status"] = "skipped_recent_case_output"
    elif not force_rerun and existing_target_review and is_recent_enough(target_review_ts, window_hours=window_hours, now=now):
        target_review = existing_target_review
        result["status"] = "skipped_recent_target_review"
    elif dry_run:
        target_review = existing_target_review
        result["status"] = "dry_run"
    else:
        try:
            resume_md = read_text(Path(str(case["resume_path"])).resolve())
            target_jd = build_target_jd(case, target_existing.get("manifest") or {})
            completed_at = datetime.now()
            review = reviewer.review(resume_md, target_jd, mode="full")
            target_review = build_rerun_payload(review, jd=target_jd, completed_at=completed_at)
            result["status"] = "rerun"
            result["completed_at"] = completed_at.isoformat(timespec="seconds")
        except (LLMUnavailableError, Exception) as exc:
            target_review = existing_target_review or prior_target_review
            result["status"] = "rerun_failed_fallback_existing" if target_review else "rerun_failed_no_fallback"
            result["error"] = str(exc)

    result["target_review"] = target_review
    result["delta"] = compare_delta(source_review.get("final_score"), target_review.get("final_score"))
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare source portfolio scores against target-JD production reviewer scores for reuse samples."
    )
    parser.add_argument("--cases-file", default=str(DEFAULT_CASES_FILE))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--window-hours", type=int, default=DEFAULT_WINDOW_HOURS)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--label", action="append", default=[], help="Only run matching case label(s). Repeatable.")
    parser.add_argument("--force-rerun", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write-target-review", action="store_true")
    parser.add_argument("--review-model", default="gpt-5.4-mini")
    parser.add_argument("--write-model", default="gpt-5.4")
    parser.add_argument("--llm-transport", default="cli", choices=["auto", "api", "cli", "claude"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cases_path = Path(args.cases_file).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_cases_dir = output_dir / "cases"
    output_cases_dir.mkdir(parents=True, exist_ok=True)

    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    if args.label:
        allowed = {item.strip() for item in args.label if item.strip()}
        cases = [case for case in cases if str(case.get("label", "") or "") in allowed]
    if args.limit > 0:
        cases = cases[: args.limit]

    configure_llm_client(
        enabled=not args.dry_run,
        write_model=args.write_model,
        review_model=args.review_model,
        transport=args.llm_transport,
    )
    reviewer = UnifiedReviewer()

    results_by_label: dict[str, dict[str, Any]] = {}
    for existing_case in sorted(output_cases_dir.glob("*.json")):
        payload = load_json(existing_case)
        label = str(payload.get("label", "") or "")
        if label:
            results_by_label[label] = payload

    now = datetime.now()
    for index, case in enumerate(cases, start=1):
        label = str(case.get("label", "") or f"case_{index}")
        output_case_path = output_cases_dir / f"{slugify_label(label)}.json"
        print(f"[{index}/{len(cases)}] {label}")
        case_result = run_case(
            case,
            reviewer=reviewer,
            output_case_path=output_case_path,
            now=now,
            window_hours=args.window_hours,
            force_rerun=args.force_rerun,
            dry_run=args.dry_run,
        )
        write_json(output_case_path, case_result)
        results_by_label[label] = case_result
        if args.write_target_review and case_result.get("target_review"):
            sync_target_artifacts(case_result)
        write_report(output_dir, list(results_by_label.values()))

        source_review = case_result.get("source_review") or {}
        target_review = case_result.get("target_review") or {}
        print(
            "  "
            f"status={case_result.get('status')} "
            f"source={format_score(source_review.get('final_score'))} "
            f"target={format_score(target_review.get('final_score'))} "
            f"delta={format_score(case_result.get('delta'))}"
        )
        if case_result.get("error"):
            print(f"  error={case_result['error']}")

    print("")
    print(f"Results JSON: {output_dir / 'results.json'}")
    print(f"Results MD:   {output_dir / 'results.md'}")


if __name__ == "__main__":
    main()
