#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from repo_paths import repo_relative_path, resolve_repo_path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from automation.job_router import build_job_fingerprint, build_skill_vocab_from_seeds, decide_route
from automation.seed_registry import load_seed_registry
from core.anthropic_client import LLMUnavailableError, configure_llm_client
from job_webapp.prompt_library import (
    append_match_pipe_dual_channel_overlay,
    build_match_pipe_master_writer_prompt,
    build_match_pipe_seed_retarget_prompt,
    build_match_pipe_unified_review_prompt,
    build_match_pipe_upgrade_revision_prompt,
    match_pipe_reviewer_system_prompt,
    match_pipe_strict_revision_system_prompt,
    match_pipe_upgrade_revision_system_prompt,
    match_pipe_writer_system_prompt,
)
from models.jd import JDProfile
from pipeline.revision_acceptance import should_adopt_revision
from reviewers.unified_reviewer import UnifiedReviewer
from writers.master_writer import MasterWriter

from .frozen_teacher import frozen_teacher_manifest
from .loader import load_job_documents
from .matcher import MatchEngine
from .starter_selector import StarterSelector


def _estimate_tokens(text: str) -> int:
    stripped = str(text or "")
    if not stripped:
        return 0
    return max(1, math.ceil(len(stripped) / 4))


def _existing_resume_anchor(candidates: list[dict | None]) -> dict | None:
    for candidate in candidates:
        if not candidate:
            continue
        resume_path = str(candidate.get("resume_path", "") or "")
        if resume_path and resolve_repo_path(resume_path).exists():
            return candidate
    return None


@dataclass
class FlowResult:
    mode: str
    final_score: float
    passed: bool
    rewrite_rounds: int
    writer_prompt_tokens_est: int
    writer_output_tokens_est: int
    reviewer_prompt_tokens_est: int
    reviewer_output_tokens_est: int
    total_tokens_est: int
    elapsed_seconds: float
    anchor_summary: dict[str, Any]
    error: str = ""

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["final_score"] = round(self.final_score, 1)
        payload["elapsed_seconds"] = round(self.elapsed_seconds, 2)
        return payload


def _review_prompt_tokens(jd: JDProfile, resume_md: str, review_summary) -> tuple[int, int]:
    prompt = build_match_pipe_unified_review_prompt(resume_md, jd, review_scope="full")
    prompt_tokens = _estimate_tokens(match_pipe_reviewer_system_prompt()) + _estimate_tokens(prompt)
    call_count = len(review_summary.calibration_scores) if review_summary.calibrated and review_summary.calibration_scores else 1
    output_tokens = _estimate_tokens(review_summary.raw_response) * call_count
    return prompt_tokens * call_count, output_tokens


def _review_with_revision(
    *,
    writer: MasterWriter,
    reviewer: UnifiedReviewer,
    jd: JDProfile,
    initial_resume_md: str,
    writer_prompt_tokens: int,
    anchor_summary: dict[str, Any],
    revision_prompt_builder,
    started_at: float,
) -> FlowResult:
    review = reviewer.review(
        initial_resume_md,
        jd,
        mode="full",
        prompt_override=build_match_pipe_unified_review_prompt(initial_resume_md, jd, review_scope="full"),
        system_prompt_override=match_pipe_reviewer_system_prompt(),
    )
    total_writer_prompt_tokens = writer_prompt_tokens
    total_writer_output_tokens = _estimate_tokens(initial_resume_md)
    rewrite_rounds = 0
    current_resume_md = initial_resume_md

    while not review.passed and review.needs_revision and rewrite_rounds < 1:
        rewrite_rounds += 1
        revision_prompt = revision_prompt_builder(current_resume_md, review)
        revised_md = writer.revise(
            current_resume_md,
            revision_prompt,
            jd,
            rewrite_mode="upgrade",
            system_prompt_override=match_pipe_upgrade_revision_system_prompt(),
        )
        revised_review = reviewer.review(
            revised_md,
            jd,
            mode="full",
            prompt_override=build_match_pipe_unified_review_prompt(revised_md, jd, review_scope="full"),
            system_prompt_override=match_pipe_reviewer_system_prompt(),
        )
        adopted = should_adopt_revision(
            score_before=review.weighted_score,
            critical_before=review.critical_count,
            high_before=review.high_count,
            score_after=revised_review.weighted_score,
            critical_after=revised_review.critical_count,
            high_after=revised_review.high_count,
            passed_after=revised_review.passed,
        )
        total_writer_prompt_tokens += _estimate_tokens(revision_prompt)
        total_writer_output_tokens += _estimate_tokens(revised_md)
        if not adopted:
            break
        current_resume_md = revised_md
        review = revised_review

    reviewer_prompt_tokens, reviewer_output_tokens = _review_prompt_tokens(jd, current_resume_md, review)
    elapsed = time.perf_counter() - started_at
    return FlowResult(
        mode="",
        final_score=review.weighted_score,
        passed=review.passed,
        rewrite_rounds=rewrite_rounds,
        writer_prompt_tokens_est=total_writer_prompt_tokens,
        writer_output_tokens_est=total_writer_output_tokens,
        reviewer_prompt_tokens_est=reviewer_prompt_tokens,
        reviewer_output_tokens_est=reviewer_output_tokens,
        total_tokens_est=total_writer_prompt_tokens + total_writer_output_tokens + reviewer_prompt_tokens + reviewer_output_tokens,
        elapsed_seconds=elapsed,
        anchor_summary=anchor_summary,
    )


def _run_no_starter(writer: MasterWriter, reviewer: UnifiedReviewer, jd: JDProfile) -> FlowResult:
    started = time.perf_counter()
    prompt = build_match_pipe_master_writer_prompt(jd)
    resume_md, _ = writer.write_from_prompt(
        prompt,
        jd=jd,
        system_prompt=match_pipe_writer_system_prompt(),
        cache_key_parts=(jd.jd_id or "unknown", jd.company or "", jd.role_type or "", "small_flow_no_starter_v1"),
    )

    result = _review_with_revision(
        writer=writer,
        reviewer=reviewer,
        jd=jd,
        initial_resume_md=resume_md,
        writer_prompt_tokens=_estimate_tokens(prompt),
        anchor_summary={"strategy": "generate_from_scratch"},
        revision_prompt_builder=lambda current_md, review: build_match_pipe_upgrade_revision_prompt(
            current_md,
            review.__dict__ | {
                "scores": {
                    key: {
                        "score": dim.score,
                        "weight": dim.weight,
                        "verdict": dim.verdict,
                        "findings": dim.findings,
                    }
                    for key, dim in review.dimensions.items()
                },
                "weighted_score": review.weighted_score,
                "revision_instructions": review.revision_instructions,
                "revision_priority": review.revision_priority,
            },
            tech_required=jd.tech_required,
            jd_title=jd.title,
            target_company=jd.company,
        ),
        started_at=started,
    )
    result.mode = "no_starter"
    return result


def _run_old_match(
    writer: MasterWriter,
    reviewer: UnifiedReviewer,
    jd: JDProfile,
    *,
    row: dict[str, Any],
    seeds,
    skill_vocab: set[str],
) -> FlowResult:
    started = time.perf_counter()
    fingerprint = build_job_fingerprint(row, seeds, skill_vocab=skill_vocab)
    decision = decide_route(fingerprint, seeds)
    seed_entry = next(item for item in seeds if item.seed_id == decision.top_candidate.seed_id)
    seed_resume_md = seed_entry.source_md.read_text(encoding="utf-8")
    prompt = build_match_pipe_seed_retarget_prompt(
        seed_resume_md,
        jd,
        seed_label=decision.top_candidate.label,
        route_mode=decision.route_mode,
        top_candidate=decision.top_candidate.to_dict(),
    )
    resume_md = writer.revise(
        seed_resume_md,
        prompt,
        jd,
        system_prompt_override=match_pipe_strict_revision_system_prompt(),
    )
    result = _review_with_revision(
        writer=writer,
        reviewer=reviewer,
        jd=jd,
        initial_resume_md=resume_md,
        writer_prompt_tokens=_estimate_tokens(prompt),
        anchor_summary={
            "route_mode": decision.route_mode,
            "seed_label": decision.top_candidate.label,
            "seed_id": decision.top_candidate.seed_id,
        },
        revision_prompt_builder=lambda current_md, review: build_match_pipe_upgrade_revision_prompt(
            current_md,
            review.__dict__ | {
                "scores": {
                    key: {
                        "score": dim.score,
                        "weight": dim.weight,
                        "verdict": dim.verdict,
                        "findings": dim.findings,
                    }
                    for key, dim in review.dimensions.items()
                },
                "weighted_score": review.weighted_score,
                "revision_instructions": review.revision_instructions,
                "revision_priority": review.revision_priority,
            },
            tech_required=jd.tech_required,
            jd_title=jd.title,
            target_company=jd.company,
            route_mode=decision.route_mode,
            seed_label=decision.top_candidate.label,
        ),
        started_at=started,
    )
    result.mode = "old_match_anchor"
    return result


def _run_new_dual_channel(
    writer: MasterWriter,
    reviewer: UnifiedReviewer,
    jd: JDProfile,
    *,
    selector_payload: dict[str, Any],
) -> FlowResult:
    started = time.perf_counter()
    primary_anchor = _existing_resume_anchor(
        [selector_payload["writer_input"].get("primary_anchor")]
        + list(selector_payload.get("semantic_top_k", []))
    )
    if not primary_anchor:
        raise RuntimeError("No usable semantic resume anchor for dual-channel validation.")
    seed_resume_md = resolve_repo_path(primary_anchor["resume_path"]).read_text(encoding="utf-8")
    continuity_anchor = _existing_resume_anchor(
        [selector_payload["writer_input"].get("continuity_anchor")]
        + list(selector_payload.get("company_top_k", []))
    )
    prompt = build_match_pipe_seed_retarget_prompt(
        seed_resume_md,
        jd,
        seed_label=f"semantic:{primary_anchor['company_name']} / {primary_anchor['title']}",
        route_mode="retarget",
        top_candidate={
            "label": primary_anchor["title"],
            "seed_company_name": primary_anchor["company_name"],
            "same_company": bool(
                continuity_anchor
                and continuity_anchor.get("company_name") == jd.company
            ),
            "missing_required": primary_anchor.get("missing_critical_units", []),
        },
    )
    prompt = append_match_pipe_dual_channel_overlay(
        prompt,
        delta_summary=selector_payload.get("delta_summary", []),
        continuity_anchor=continuity_anchor,
    )
    resume_md = writer.revise(
        seed_resume_md,
        prompt,
        jd,
        system_prompt_override=match_pipe_strict_revision_system_prompt(),
    )
    result = _review_with_revision(
        writer=writer,
        reviewer=reviewer,
        jd=jd,
        initial_resume_md=resume_md,
        writer_prompt_tokens=_estimate_tokens(prompt),
        anchor_summary={
            "semantic_best_anchor": selector_payload.get("semantic_best_anchor"),
            "semantic_writer_anchor": primary_anchor,
            "company_best_anchor": selector_payload.get("company_best_anchor"),
        },
        revision_prompt_builder=lambda current_md, review: build_match_pipe_upgrade_revision_prompt(
            current_md,
            review.__dict__ | {
                "scores": {
                    key: {
                        "score": dim.score,
                        "weight": dim.weight,
                        "verdict": dim.verdict,
                        "findings": dim.findings,
                    }
                    for key, dim in review.dimensions.items()
                },
                "weighted_score": review.weighted_score,
                "revision_instructions": review.revision_instructions,
                "revision_priority": review.revision_priority,
            },
            tech_required=jd.tech_required,
            jd_title=jd.title,
            target_company=jd.company,
            route_mode="semantic_plus_company_constraint",
            seed_label=f"semantic:{primary_anchor['title']}",
        ),
        started_at=started,
    )
    result.mode = "new_dual_channel_anchor"
    return result


def _sample_jobs(limit: int = 2) -> list[dict[str, Any]]:
    manifest = frozen_teacher_manifest()
    engine = MatchEngine.from_project_data(include_scraped=True, include_portfolio=True, feature_config=manifest.feature_config)
    selector = StarterSelector(semantic_engine=engine)
    scraped_docs = {item.job_id: item for item in load_job_documents(include_scraped=True, include_portfolio=False)}
    seeds = load_seed_registry(include_promoted=True)
    skill_vocab = build_skill_vocab_from_seeds(seeds)
    selected: list[dict[str, Any]] = []
    for job in engine.index.jobs:
        if job.source_kind != "scraped":
            continue
        document = scraped_docs.get(job.job_id)
        if document is None:
            continue
        selector_payload = selector.select_by_job_id(job.job_id, top_k=3).to_dict()
        primary_anchor = _existing_resume_anchor(
            [selector_payload["writer_input"].get("primary_anchor")]
            + list(selector_payload.get("semantic_top_k", []))
        )
        if not primary_anchor:
            continue
        route_decision = decide_route(build_job_fingerprint(document.row, seeds, skill_vocab=skill_vocab), seeds)
        if route_decision.route_mode == "new_seed":
            continue
        seed_entry = next((item for item in seeds if item.seed_id == route_decision.top_candidate.seed_id), None)
        if seed_entry is None or not seed_entry.source_md.exists():
            continue
        selected.append(
            {
                "job_id": job.job_id,
                "company_name": job.company_name,
                "title": job.title,
                "row": document.row,
                "raw_text": document.raw_text,
                "selector_payload": selector_payload,
                "route_decision": route_decision.to_dict(),
            }
        )
        if len(selected) >= limit:
            break
    return selected


def run_small_flow_validation(
    output_dir: str | Path,
    *,
    sample_size: int = 2,
    llm_transport: str = "cli",
    write_model: str = "gpt-5.4",
    review_model: str = "gpt-5.4-mini",
) -> dict:
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    configure_llm_client(
        enabled=True,
        transport=llm_transport,
        write_model=write_model,
        review_model=review_model,
    )
    writer = MasterWriter()
    reviewer = UnifiedReviewer()
    seeds = load_seed_registry(include_promoted=True)
    skill_vocab = build_skill_vocab_from_seeds(seeds)

    jobs = _sample_jobs(limit=sample_size)
    results: list[dict[str, Any]] = []
    rate_limit_triggered = False
    rate_limit_error = ""
    for item in jobs:
        jd = JDProfile.from_text(item["raw_text"], jd_id=item["job_id"], company=item["company_name"])
        job_result = {
            "job_id": item["job_id"],
            "company_name": item["company_name"],
            "title": item["title"],
            "route_decision": item["route_decision"],
            "selector_payload": item["selector_payload"],
            "flows": [],
        }
        try:
            job_result["flows"].append(_run_no_starter(writer, reviewer, jd).to_dict())
            job_result["flows"].append(
                _run_old_match(writer, reviewer, jd, row=item["row"], seeds=seeds, skill_vocab=skill_vocab).to_dict()
            )
            job_result["flows"].append(
                _run_new_dual_channel(writer, reviewer, jd, selector_payload=item["selector_payload"]).to_dict()
            )
        except (LLMUnavailableError, RuntimeError) as exc:
            message = str(exc)
            if "rate" in message.lower() or "limit" in message.lower() or "hour" in message.lower():
                rate_limit_triggered = True
                rate_limit_error = message
            job_result["error"] = message
        results.append(job_result)
        if rate_limit_triggered:
            break

    summary_by_mode: dict[str, dict[str, float]] = {}
    for mode in ("no_starter", "old_match_anchor", "new_dual_channel_anchor"):
        flows = [
            flow
            for item in results
            for flow in item.get("flows", [])
            if flow.get("mode") == mode
        ]
        if not flows:
            continue
        summary_by_mode[mode] = {
            "sample_count": len(flows),
            "avg_final_score": round(sum(flow["final_score"] for flow in flows) / len(flows), 2),
            "pass_rate": round(sum(1 for flow in flows if flow["passed"]) / len(flows), 4),
            "avg_rewrite_rounds": round(sum(flow["rewrite_rounds"] for flow in flows) / len(flows), 2),
            "avg_total_tokens_est": round(sum(flow["total_tokens_est"] for flow in flows) / len(flows), 2),
            "avg_elapsed_seconds": round(sum(flow["elapsed_seconds"] for flow in flows) / len(flows), 2),
        }

    retry_windows = []
    if rate_limit_triggered:
        retry_windows = [
            "America/Chicago 02:54",
            "America/Chicago 07:54",
        ]

    payload = {
        "experiment_type": "small_flow_real_downstream_validation",
        "sample_size_requested": sample_size,
        "sample_size_executed": len(results),
        "business_metrics": [
            "writer token consumption",
            "reviewer token consumption",
            "total processing time",
            "rewrite rounds",
            "review pass rate",
            "final score",
        ],
        "execution_summary": summary_by_mode,
        "results": results,
        "future_scale_recommendation": {
            "next_sample_size": 12,
            "mix": [
                "4 generic-title high-risk jobs",
                "4 cross-company semantic-heavy jobs",
                "4 same-company continuity-sensitive jobs",
            ],
        },
        "retry_plan": {
            "rate_limit_triggered": rate_limit_triggered,
            "error": rate_limit_error,
            "retry_windows": retry_windows,
        },
    }
    output_path = output_dir / "match_pipe_small_flow_validation_report.json"
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run a small real downstream validation for the starter selector.")
    parser.add_argument("--output-dir", default="output/analysis")
    parser.add_argument("--sample-size", type=int, default=2)
    parser.add_argument("--llm-transport", default="cli")
    parser.add_argument("--write-model", default="gpt-5.4")
    parser.add_argument("--review-model", default="gpt-5.4-mini")
    args = parser.parse_args()
    payload = run_small_flow_validation(
        args.output_dir,
        sample_size=args.sample_size,
        llm_transport=args.llm_transport,
        write_model=args.write_model,
        review_model=args.review_model,
    )
    print(
        json.dumps(
            {
                "report": repo_relative_path(Path(args.output_dir).expanduser() / "match_pipe_small_flow_validation_report.json"),
                "sample_size_executed": payload["sample_size_executed"],
                "rate_limit_triggered": payload["retry_plan"]["rate_limit_triggered"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
