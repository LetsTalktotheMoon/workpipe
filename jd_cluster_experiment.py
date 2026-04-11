#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
RUNTIME_ROOT = ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from automation.jd_cluster import (
    build_company_consistency_context,
    load_cluster_candidates,
    select_cluster_candidate,
)
from core.anthropic_client import configure_llm_client
from models.jd import JDProfile
from pipeline.cluster_experiment_orchestrator import ClusterExperimentOrchestrator
from reviewers.unified_reviewer import UnifiedReviewer


PORTFOLIO_INDEX = ROOT / "data" / "deliverables" / "resume_portfolio" / "portfolio_index.json"


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def artifact_job_dir(record: dict[str, Any]) -> Path:
    return Path(str(record.get("artifact_dir", "") or "")).resolve()


def record_review_verdict(record: dict[str, Any]) -> str:
    review = record.get("review", {}) if isinstance(record.get("review"), dict) else {}
    return str(review.get("verdict", "") or review.get("overall_verdict", "") or record.get("review_verdict", "") or "").strip().lower()


def record_review_score(record: dict[str, Any]) -> float:
    review = record.get("review", {}) if isinstance(record.get("review"), dict) else {}
    try:
        return float(review.get("final_score", review.get("weighted_score", 0.0)) or 0.0)
    except Exception:
        return 0.0


def load_case_inputs(record: dict[str, Any]) -> tuple[str, dict[str, Any], str]:
    job_dir = artifact_job_dir(record)
    resume_md = (job_dir / "resume.md").read_text(encoding="utf-8")
    row = load_json(job_dir / "sheet_row.json", default={})
    jd_text = (job_dir / "job.md").read_text(encoding="utf-8")
    return resume_md, row, jd_text


def select_cases(records: list[dict[str, Any]], *, category: str, limit: int) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    if category == "non_pass":
        for record in records:
            verdict = record_review_verdict(record)
            if verdict not in {"conditional_pass", "fail"}:
                continue
            if str(record.get("source_kind", "") or "") == "local_unified_pipeline":
                continue
            job_dir = artifact_job_dir(record)
            if not (job_dir / "resume.md").exists() or not (job_dir / "job.md").exists() or not (job_dir / "sheet_row.json").exists():
                continue
            candidates.append(record)
        candidates.sort(
            key=lambda item: (
                item.get("publish_time", ""),
                1 if record_review_verdict(item) == "fail" else 0,
                record_review_score(item),
            ),
            reverse=True,
        )
        return candidates[:limit]

    if category == "mature_company":
        company_counts = Counter(
            str(record.get("company_name", "") or "").strip()
            for record in records
            if str(record.get("resume_md", "") or "").strip()
        )
        seen_companies: set[str] = set()
        for record in sorted(records, key=lambda item: (item.get("publish_time", ""), record_review_score(item)), reverse=True):
            company = str(record.get("company_name", "") or "").strip()
            if not company or company_counts[company] < 2 or company in seen_companies:
                continue
            job_dir = artifact_job_dir(record)
            if not (job_dir / "resume.md").exists() or not (job_dir / "job.md").exists() or not (job_dir / "sheet_row.json").exists():
                continue
            seen_companies.add(company)
            candidates.append(record)
            if len(candidates) >= limit:
                break
        return candidates

    raise ValueError(f"Unsupported category: {category}")


def review_existing_resume(*, reviewer: UnifiedReviewer, record: dict[str, Any]) -> dict[str, Any]:
    resume_md, row, jd_text = load_case_inputs(record)
    jd = JDProfile.from_text(
        jd_text,
        jd_id=str(record.get("job_id", "") or ""),
        company=str(row.get("company_name", "") or record.get("company_name", "") or ""),
    )
    review = reviewer.review(resume_md, jd)
    return {
        "final_score": round(review.weighted_score, 1),
        "verdict": "pass" if review.passed else "pending",
        "critical_count": review.critical_count,
        "high_count": review.high_count,
        "revision_priority": review.revision_priority,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run B-pipeline JD-cluster experiments against existing A resumes.")
    parser.add_argument("--category", action="append", choices=["non_pass", "mature_company"], default=[])
    parser.add_argument("--limit-per-category", type=int, default=2)
    parser.add_argument("--job-id", action="append", default=[])
    parser.add_argument("--retrieval-only", action="store_true")
    parser.add_argument("--run-dir", default="")
    parser.add_argument("--write-model", default="gpt-5.4")
    parser.add_argument("--review-model", default="gpt-5.4-mini")
    parser.add_argument("--llm-transport", default="cli")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve() if str(args.run_dir or "").strip() else (
        ROOT / "runs" / f"jd_cluster_experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    run_dir.mkdir(parents=True, exist_ok=True)

    records = load_json(PORTFOLIO_INDEX, default=[])
    if not isinstance(records, list):
        raise SystemExit("portfolio_index.json must be a list")

    selected_records: list[dict[str, Any]] = []
    selected_job_ids = {str(item).strip() for item in args.job_id if str(item).strip()}
    if selected_job_ids:
        for record in records:
            if str(record.get("job_id", "") or "").strip() in selected_job_ids:
                selected_records.append(record)
    else:
        categories = args.category or ["non_pass", "mature_company"]
        for category in categories:
            selected_records.extend(select_cases(records, category=category, limit=int(args.limit_per_category or 2)))

    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in selected_records:
        job_id = str(record.get("job_id", "") or "").strip()
        if not job_id or job_id in seen:
            continue
        seen.add(job_id)
        deduped.append(record)
    selected_records = deduped

    if not selected_records:
        raise SystemExit("No experiment cases selected.")

    reviewer = None
    orchestrator = None
    if not args.retrieval_only:
        configure_llm_client(
            enabled=True,
            write_model=args.write_model,
            review_model=args.review_model,
            transport=args.llm_transport,
        )
        reviewer = UnifiedReviewer()
        orchestrator = ClusterExperimentOrchestrator(
            output_dir=str(run_dir),
            enable_llm=True,
            write_model=args.write_model,
            review_model=args.review_model,
            llm_transport=args.llm_transport,
        )
    cluster_candidates = load_cluster_candidates()

    results: list[dict[str, Any]] = []
    for record in selected_records:
        job_id = str(record.get("job_id", "") or "").strip()
        _, row, jd_text = load_case_inputs(record)
        baseline = review_existing_resume(reviewer=reviewer, record=record) if reviewer is not None else {}
        selection = select_cluster_candidate(
            target_row=row,
            candidates=cluster_candidates,
            exclude_job_ids={job_id},
        )
        company_context = build_company_consistency_context(
            target_row=row,
            candidates=cluster_candidates,
            exclude_job_ids={job_id},
        )
        result = {}
        if orchestrator is not None:
            experiment_dir = run_dir / job_id
            experiment_dir.mkdir(parents=True, exist_ok=True)
            result = orchestrator.run(
                base_resume_md=selection.candidate_match.candidate.resume_md_path.read_text(encoding="utf-8"),
                selection=selection,
                company_context=company_context,
                jd_text=jd_text,
                jd_id=job_id,
                company=str(row.get("company_name", "") or ""),
            )
        payload = {
            "job_id": job_id,
            "company_name": str(record.get("company_name", "") or ""),
            "title": str(record.get("title", "") or ""),
            "mode": "retrieval_only" if args.retrieval_only else "full",
            "category": (
                "non_pass"
                if record_review_verdict(record) in {"conditional_pass", "fail"}
                else "mature_company"
            ),
            "a_baseline": baseline,
            "b_selection": {
                "cluster_type": selection.cluster_type,
                "cluster_key": selection.cluster_key,
                "reason": selection.reason,
                "company_candidate_count": selection.company_candidate_count,
                "mature_company_cluster": selection.mature_company_cluster,
                "selected_candidate": selection.candidate_match.to_dict(),
                "top_matches": [item.to_dict() for item in selection.top_matches],
            },
            "b_result": (
                {
                    "final_score": round(float(result.get("final_score", 0.0) or 0.0), 1),
                    "verdict": str(result.get("verdict", "") or ""),
                    "output_path": str(result.get("output_path", "") or ""),
                    "plan_path": str((Path(str(result.get("output_path", "") or "")).with_name(Path(str(result.get("output_path", "") or "")).stem.replace("_resume", "_plan") + ".txt"))),
                }
                if result
                else {}
            ),
            "company_context_version_count": company_context.get("version_count", 0),
            "company_context_high_risk_flags": company_context.get("high_risk_flags", []),
        }
        results.append(payload)
        print(json.dumps(payload, ensure_ascii=False))

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "run_dir": str(run_dir),
        "case_count": len(results),
        "results": results,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
