#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import statistics
import time

from repo_paths import repo_relative_path

from .benchmark import (
    BenchmarkCase,
    audit_legacy_benchmark,
    build_benchmark_suite,
    evaluate_cases,
    split_cases,
)
from .matcher import MatchEngine, TEACHER_CONFIGS
from .student import StudentMatchEngine, distill_student_weights


ROOT = Path(__file__).resolve().parents[1]


def dependency_audit() -> dict:
    return {
        "modules": [
            {
                "name": "match_pipe.taxonomy",
                "role": "Canonical taxonomy and parent-child graph.",
                "classification": "fully_new",
            },
            {
                "name": "match_pipe.units",
                "role": "Requirement-unit extraction, logic typing, weight assignment.",
                "classification": "fully_new",
            },
            {
                "name": "match_pipe.matcher",
                "role": "Recall, scoring, ranking, feature gating for teacher variants.",
                "classification": "fully_new",
            },
            {
                "name": "match_pipe.benchmark",
                "role": "Legacy benchmark, rebuilt hard pool, evaluation metrics.",
                "classification": "fully_new",
            },
            {
                "name": "runtime.automation.jd_builder.row_to_jd_markdown",
                "role": "Reconstruct raw JD markdown from existing sheet fields.",
                "classification": "reuse_old_field_wrapper",
            },
            {
                "name": "runtime.automation.text_utils.normalize_token",
                "role": "String normalization only; no old routing or seed logic.",
                "classification": "reuse_old_utility",
            },
        ],
        "data_structures": [
            {
                "name": "data/job_tracker/jobs_catalog.json",
                "role": "Current full JD pool input; merged from Google Sheet, local scraper cache, and portfolio history.",
                "classification": "reuse_old_field_source",
            },
            {
                "name": "data/deliverables/resume_portfolio/by_company/*/*/*/sheet_row.json",
                "role": "Historical JD rows only.",
                "classification": "reuse_old_field_source",
            },
            {
                "name": "data/deliverables/resume_portfolio/by_company/*/*/*/job.md",
                "role": "Historical raw JD text when available.",
                "classification": "reuse_old_field_source",
            },
            {
                "name": "portfolio_index.json",
                "role": "Used only for benchmark context in previous experiments; not required by the current matcher runtime.",
                "classification": "legacy_context_only",
            },
        ],
        "indices": [
            {
                "name": "pattern_index",
                "source": "requirement-unit pattern signature",
                "classification": "fully_new",
            },
            {
                "name": "member_index",
                "source": "canonical element and hierarchy expansion",
                "classification": "fully_new",
            },
            {
                "name": "combo_index",
                "source": "recall keys derived from high-weight requirement units",
                "classification": "fully_new",
            },
            {
                "name": "surface_token_index",
                "source": "title plus requirement-unit display text",
                "classification": "title_metadata_heuristic",
            },
        ],
        "feature_sources": [
            {
                "name": "canonical taxonomy / requirement-unit logic",
                "classification": "fully_new",
            },
            {
                "name": "company_name, job_title, job_seniority, work_model, job_summary, must_have_quals, preferred_quals",
                "classification": "reuse_old_fields",
            },
            {
                "name": "same_company recall and duplicate bonus",
                "classification": "may_introduce_history_bias",
            },
            {
                "name": "no seed registry / no seed index / no route_mode / no old cluster key at runtime",
                "classification": "explicitly_not_used",
            },
        ],
    }


def feature_attribution() -> dict:
    return {
        "pure_jd_semantic": {
            "features": [
                "requirement units",
                "canonical taxonomy",
                "OR / AND / AT_LEAST_K / PARENT_ANY_CHILD",
                "must_have / preferred / background weights",
                "pattern_exact recall",
                "hard_unit recall",
                "hierarchy_expand recall",
                "combo recall",
            ],
            "participates_in_recall": True,
            "participates_in_ranking": True,
            "quantitative_impact": {
                "ranking_weight": 0.78,
                "components": {
                    "requirement_score": 0.64,
                    "hard_requirement_score": 0.14,
                },
            },
        },
        "duplicate_near_duplicate": {
            "features": [
                "surface_token recall",
                "duplicate_score",
                "normalized-title exact match inside duplicate score",
                "duplicate override on hard-requirement penalty",
            ],
            "participates_in_recall": True,
            "participates_in_ranking": True,
            "quantitative_impact": {
                "base_ranking_weight": 0.08,
                "same_title_same_company_bonus": 0.14,
                "gating": "Can bypass hard-requirement penalty when duplicate_score >= 0.85.",
            },
        },
        "same_company": {
            "features": [
                "same_company recall",
                "same_company term inside metadata_score",
                "same_company term inside duplicate_score for Teacher-A",
            ],
            "participates_in_recall": True,
            "participates_in_ranking": True,
            "quantitative_impact": {
                "metadata_contribution_max": 0.0156,
                "duplicate_contribution_max": 0.028,
                "bonus": 0.14,
            },
        },
        "title_metadata_heuristics": {
            "features": [
                "surface_score title token overlap",
                "surface_score normalized-title exactness",
                "role_family heuristic",
                "seniority heuristic",
                "domain overlap",
                "work-model / education / location canonicalized from metadata text",
            ],
            "participates_in_recall": True,
            "participates_in_ranking": True,
            "quantitative_impact": {
                "surface_score_weight": 0.08,
                "metadata_score_weight": 0.06,
            },
        },
    }


def _build_engine(config_name: str) -> tuple[MatchEngine, float]:
    start = time.perf_counter()
    engine = MatchEngine.from_project_data(
        include_scraped=True,
        include_portfolio=True,
        feature_config=TEACHER_CONFIGS[config_name],
    )
    return engine, time.perf_counter() - start


def _evaluate_variant(engine: MatchEngine, cases: list[BenchmarkCase]) -> dict:
    return evaluate_cases(engine, cases, top_k=5).to_dict()


def _top_matches(engine: MatchEngine, query_id: str, top_k: int = 3) -> list[dict]:
    response = engine.match_by_job_id(query_id, top_k=top_k)
    items = []
    query = engine.get_job(query_id)
    assert query is not None
    for match in response.matches[:top_k]:
        items.append(
            {
                "job_id": match.candidate.job_id,
                "company_name": match.candidate.company_name,
                "title": match.candidate.title,
                "score": round(match.total_score, 4),
                "same_company": match.candidate.company_name == query.company_name,
                "exact_title": match.candidate.title.strip().lower() == query.title.strip().lower(),
                "recall_channels": match.recall_channels,
            }
        )
    return items


def _query_diff_entry(case: BenchmarkCase, engines: dict[str, MatchEngine]) -> dict:
    query = next(engine.get_job(case.query_id) for engine in engines.values())
    assert query is not None
    variants = {name: _top_matches(engine, case.query_id, top_k=3) for name, engine in engines.items()}
    top1_a = variants["teacher_a"][0] if variants["teacher_a"] else {}
    top1_b = variants["teacher_b_pure_semantic"][0] if variants["teacher_b_pure_semantic"] else {}
    top1_c = variants["teacher_c_semantic_duplicate"][0] if variants["teacher_c_semantic_duplicate"] else {}
    return {
        "query_id": case.query_id,
        "pool_name": case.pool_name,
        "category": case.category,
        "query_company": query.company_name,
        "query_title": query.title,
        "positive_ids": list(case.positive_ids),
        "distractor_ids": list(case.distractor_ids),
        "variants": variants,
        "flags": {
            "same_company_to_cross_company_a_to_b": bool(top1_a) and top1_a.get("same_company") and bool(top1_b) and not top1_b.get("same_company"),
            "same_company_to_cross_company_a_to_c": bool(top1_a) and top1_a.get("same_company") and bool(top1_c) and not top1_c.get("same_company"),
            "title_driven_to_semantic_driven_a_to_b": bool(top1_a) and top1_a.get("exact_title") and bool(top1_b) and not top1_b.get("exact_title"),
            "title_driven_to_semantic_driven_a_to_c": bool(top1_a) and top1_a.get("exact_title") and bool(top1_c) and not top1_c.get("exact_title"),
            "top1_changes_between_a_b": top1_a.get("job_id") != top1_b.get("job_id"),
            "top1_changes_between_a_c": top1_a.get("job_id") != top1_c.get("job_id"),
        },
    }


def _estimate_contribution(metrics_a: dict, metrics_b: dict, metrics_c: dict) -> dict:
    denom1 = max(metrics_a["hit_at_1"], 1e-6)
    denom3 = max(metrics_a["hit_at_3"], 1e-6)
    semantic1 = metrics_b["hit_at_1"]
    duplicate1 = max(metrics_c["hit_at_1"] - metrics_b["hit_at_1"], 0.0)
    same_company1 = max(metrics_a["hit_at_1"] - metrics_c["hit_at_1"], 0.0)
    semantic3 = metrics_b["hit_at_3"]
    duplicate3 = max(metrics_c["hit_at_3"] - metrics_b["hit_at_3"], 0.0)
    same_company3 = max(metrics_a["hit_at_3"] - metrics_c["hit_at_3"], 0.0)
    return {
        "hit_at_1": {
            "semantic_absolute": round(semantic1, 4),
            "duplicate_absolute": round(duplicate1, 4),
            "same_company_absolute": round(same_company1, 4),
            "semantic_share_of_A": round(semantic1 / denom1, 4),
            "duplicate_share_of_A": round(duplicate1 / denom1, 4),
            "same_company_share_of_A": round(same_company1 / denom1, 4),
        },
        "hit_at_3": {
            "semantic_absolute": round(semantic3, 4),
            "duplicate_absolute": round(duplicate3, 4),
            "same_company_absolute": round(same_company3, 4),
            "semantic_share_of_A": round(semantic3 / denom3, 4),
            "duplicate_share_of_A": round(duplicate3 / denom3, 4),
            "same_company_share_of_A": round(same_company3 / denom3, 4),
        },
    }


def _per_category_metrics(engine: MatchEngine, cases: list[BenchmarkCase]) -> dict:
    grouped: dict[str, list[BenchmarkCase]] = {}
    for case in cases:
        grouped.setdefault(case.category or "uncategorized", []).append(case)
    return {category: evaluate_cases(engine, group, top_k=5, max_misses=4).to_dict() for category, group in grouped.items()}


def run_purity_audit(output_dir: str | Path) -> dict:
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    engines: dict[str, MatchEngine] = {}
    build_times: dict[str, float] = {}
    for config_name in ("teacher_a", "teacher_b_pure_semantic", "teacher_c_semantic_duplicate"):
        engine, seconds = _build_engine(config_name)
        engines[config_name] = engine
        build_times[config_name] = round(seconds, 2)

    suite = build_benchmark_suite(engines["teacher_a"].index.jobs)
    standard_train, standard_test = split_cases(suite.standard_cases)
    hard_train, hard_test = split_cases(suite.hard_cases)
    rebuilt_hard = suite.rebuilt_hard_cases

    experiments = {
        "legacy_standard_test": standard_test,
        "legacy_hard_test": hard_test,
        "rebuilt_hard_all": rebuilt_hard,
    }

    metrics: dict[str, dict] = {}
    for variant_name, engine in engines.items():
        metrics[variant_name] = {
            dataset_name: _evaluate_variant(engine, cases)
            for dataset_name, cases in experiments.items()
        }

    query_ids = []
    for cases in experiments.values():
        for case in cases:
            if case.query_id not in query_ids:
                query_ids.append(case.query_id)
    case_by_query = {}
    for dataset_name, cases in experiments.items():
        for case in cases:
            case_by_query[(dataset_name, case.query_id)] = case
    query_diffs = [
        _query_diff_entry(case_by_query[(dataset_name, query_id)], engines)
        for dataset_name, cases in experiments.items()
        for query_id in [case.query_id for case in cases]
    ]

    benchmark_audit = audit_legacy_benchmark(suite, engines["teacher_a"].index.jobs)
    category_metrics = {
        variant_name: _per_category_metrics(engine, rebuilt_hard)
        for variant_name, engine in engines.items()
    }

    contribution_estimates = {
        "legacy_standard_test": _estimate_contribution(
            metrics["teacher_a"]["legacy_standard_test"],
            metrics["teacher_b_pure_semantic"]["legacy_standard_test"],
            metrics["teacher_c_semantic_duplicate"]["legacy_standard_test"],
        ),
        "legacy_hard_test": _estimate_contribution(
            metrics["teacher_a"]["legacy_hard_test"],
            metrics["teacher_b_pure_semantic"]["legacy_hard_test"],
            metrics["teacher_c_semantic_duplicate"]["legacy_hard_test"],
        ),
        "rebuilt_hard_all": _estimate_contribution(
            metrics["teacher_a"]["rebuilt_hard_all"],
            metrics["teacher_b_pure_semantic"]["rebuilt_hard_all"],
            metrics["teacher_c_semantic_duplicate"]["rebuilt_hard_all"],
        ),
    }

    student_weights = distill_student_weights(
        engines["teacher_a"].index.jobs,
        standard_train,
    )
    student = StudentMatchEngine(engines["teacher_a"].index.jobs, weights=student_weights)
    student_metrics = {
        dataset_name: _evaluate_variant(student, cases)
        for dataset_name, cases in experiments.items()
    }

    payload = {
        "dependency_audit": dependency_audit(),
        "feature_attribution": feature_attribution(),
        "variant_build_seconds": build_times,
        "benchmark_suite": suite.to_dict(),
        "benchmark_audit": benchmark_audit,
        "splits": {
            "legacy_standard_train": len(standard_train),
            "legacy_standard_test": len(standard_test),
            "legacy_hard_train": len(hard_train),
            "legacy_hard_test": len(hard_test),
            "rebuilt_hard_all": len(rebuilt_hard),
        },
        "metrics": metrics,
        "rebuilt_hard_category_metrics": category_metrics,
        "query_diffs": query_diffs,
        "student_reference": {
            "weights": student_weights.to_dict(),
            "metrics": student_metrics,
        },
        "capability_attribution": contribution_estimates,
        "final_judgement": {
            "current_teacher_is_pure_jd_teacher": False,
            "current_teacher_is_mixed_bias_teacher": True,
            "freeze_status_of_current_teacher_a": "do_not_freeze_as_final_teacher",
            "teacher_b_requires_retraining_or_re-freeze": True,
            "current_student_is_valid_for_final_deployment": False,
            "must_redistill_from_pure_semantic_teacher": True,
            "recommended_architecture": {
                "pure_semantic_channel": "Teacher-B style channel should own canonical taxonomy, requirement units, logic, hierarchy and must/preferred ranking.",
                "duplicate_channel": "Teacher-C style duplicate/near-duplicate channel should be explicit and separately audited.",
                "same_company_channel": "Move same-company consistency to a separate downstream constraint/reranker instead of embedding it into the semantic teacher.",
            },
        },
    }

    output_path = output_dir / "match_pipe_purity_audit.json"
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run match_pipe purity audit and A/B/C comparison.")
    parser.add_argument("--output-dir", default="output/analysis")
    args = parser.parse_args()

    payload = run_purity_audit(args.output_dir)
    print(json.dumps(
        {
            "written_to": repo_relative_path(Path(args.output_dir).expanduser() / "match_pipe_purity_audit.json"),
            "variant_build_seconds": payload["variant_build_seconds"],
            "benchmark_suite": payload["benchmark_suite"],
        },
        indent=2,
        ensure_ascii=False,
    ))


if __name__ == "__main__":
    main()
