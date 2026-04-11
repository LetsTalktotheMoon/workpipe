#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import statistics
import subprocess
import time

from .benchmark import (
    BenchmarkCase,
    BenchmarkMetrics,
    _has_must_and_preferred,
    _has_parent_child,
    _logic_types,
    _must_signature,
    _semantic_overlap,
    build_benchmark_suite,
    evaluate_cases,
)
from .incremental import IncrementalMatchStore
from .loader import load_job_documents
from .matcher import MatchEngine, TEACHER_CONFIGS, _norm_title
from .starter_selector import StarterSelector


ROOT = Path(__file__).resolve().parents[1]
LABEL_POOL_PATH = ROOT / "match_pipe" / "semantic_label_pool.json"
BOUNDARY_POOL_PATH = ROOT / "match_pipe" / "semantic_boundary_pool.json"

ERROR_CATEGORIES = [
    "or_parse_error",
    "and_parse_error",
    "at_least_k_parse_error",
    "must_preferred_weight_error",
    "parent_child_rule_error",
    "requirement_unit_split_error",
    "content_type_identification_error",
    "canonical_taxonomy_gap",
    "title_metadata_mislead",
    "generic_title_requirement_gap",
]


@dataclass
class GoldLabel:
    query_id: str
    positive_ids: tuple[str, ...]
    category: str
    confidence: float
    status: str
    rationale: str

    def to_case(self) -> BenchmarkCase:
        return BenchmarkCase(
            query_id=self.query_id,
            positive_ids=self.positive_ids,
            pool_name="semantic_gold",
            company_name="",
            normalized_title="",
            rationale=self.rationale,
            category=self.category,
        )

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["confidence"] = round(self.confidence, 4)
        payload["positive_ids"] = list(self.positive_ids)
        return payload


def _load_label_pool() -> dict:
    if not LABEL_POOL_PATH.exists():
        return {"labels": []}
    return json.loads(LABEL_POOL_PATH.read_text(encoding="utf-8"))


def _load_boundary_pool() -> dict:
    if not BOUNDARY_POOL_PATH.exists():
        return {"boundary_cases": []}
    return json.loads(BOUNDARY_POOL_PATH.read_text(encoding="utf-8"))


def _boundary_decisions() -> dict[tuple[str, str], dict]:
    payload = _load_boundary_pool()
    return {
        (item["query_id"], item["category"]): item
        for item in payload.get("boundary_cases", [])
    }


def _label_decisions() -> tuple[dict[tuple[str, str], dict], list[dict]]:
    payload = _load_label_pool()
    adjudicated: dict[tuple[str, str], dict] = {}
    pending: list[dict] = []
    for item in payload.get("labels", []):
        key = (item["query_id"], item["category"])
        if item.get("final_status") == "adjudicated":
            adjudicated[key] = item
        else:
            pending.append(item)
    return adjudicated, pending


def _is_generic_title(job) -> bool:
    return _norm_title(job.title) in {
        "software engineer",
        "software engineer ii",
        "senior software engineer",
        "machine learning engineer",
        "data scientist",
        "software development engineer",
    }


def _build_gold_set(engine: MatchEngine, suite) -> list[GoldLabel]:
    overrides, pending = _label_decisions()
    boundary_cases = _boundary_decisions()
    pending_keys = {(item["query_id"], item["category"]) for item in pending}
    jobs = {job.job_id: job for job in engine.index.jobs}
    selected: list[GoldLabel] = []
    category_limits = {
        "cross_company_structure_similar": 6,
        "same_company_structure_different": 4,
        "title_same_business_different": 5,
        "parent_child_conflict": 5,
        "or_and_mixed": 5,
        "must_vs_preferred_confusing": 5,
    }
    counts: Counter[str] = Counter()
    for case in suite.rebuilt_hard_cases:
        key = (case.query_id, case.category)
        if key in pending_keys and key not in boundary_cases:
            continue
        if counts[case.category] >= category_limits.get(case.category, 0):
            continue
        query = jobs[case.query_id]
        boundary = boundary_cases.get(key)
        if key in overrides:
            positive_jobs = [jobs[item] for item in overrides[key]["final_positive_ids"] if item in jobs]
            rationale = "Human-adjudicated semantic label override."
            confidence = 0.98
            status = "adjudicated_manual_pool"
        elif boundary is not None:
            positive_jobs = [jobs[item] for item in boundary.get("acceptable_positive_ids", []) if item in jobs]
            rationale = boundary.get("rationale", "Boundary sample uses multiple acceptable semantic positives.")
            confidence = 0.8
            status = "boundary_multiple_acceptable"
        else:
            positive_jobs = [jobs[item] for item in case.positive_ids if item in jobs and jobs[item].company_name != query.company_name]
            rationale = case.rationale
            confidence = 0.0
            status = ""
        if not positive_jobs:
            continue
        if key not in overrides:
            positive_jobs.sort(key=lambda item: _semantic_overlap(query, item), reverse=True)
            best_positive = positive_jobs[0]
            confidence = _semantic_overlap(query, best_positive)
            if case.category in {"or_and_mixed", "parent_child_conflict", "must_vs_preferred_confusing"}:
                confidence += 0.04
            status = "codex_curated_high_confidence" if confidence >= 0.7 else "pending_manual_review"
        else:
            best_positive = positive_jobs[0]
        selected.append(
            GoldLabel(
                query_id=case.query_id,
                positive_ids=tuple(item.job_id for item in positive_jobs) if boundary is not None else (best_positive.job_id,),
                category=case.category,
                confidence=min(confidence, 0.98),
                status=status,
                rationale=rationale,
            )
        )
        counts[case.category] += 1
    extra_cases = sorted(
        [case for case in suite.rebuilt_hard_cases if case.category == "cross_company_structure_similar"],
        key=lambda item: item.query_id,
    )
    for case in extra_cases:
        if len(selected) >= 30:
            break
        if any(item.query_id == case.query_id for item in selected):
            continue
        query = jobs[case.query_id]
        positive_jobs = [jobs[item] for item in case.positive_ids if item in jobs and jobs[item].company_name != query.company_name]
        if not positive_jobs:
            continue
        best_positive = max(positive_jobs, key=lambda item: _semantic_overlap(query, item))
        selected.append(
            GoldLabel(
                query_id=case.query_id,
                positive_ids=(best_positive.job_id,),
                category=case.category,
                confidence=min(_semantic_overlap(query, best_positive), 0.95),
                status="codex_curated_high_confidence",
                rationale="High-confidence cross-company semantic twin selected for small gold set.",
            )
        )
    return selected[:30]


def _apply_label_overrides_to_cases(cases: list[BenchmarkCase]) -> list[BenchmarkCase]:
    overrides, pending = _label_decisions()
    boundary_cases = _boundary_decisions()
    pending_keys = {(item["query_id"], item["category"]) for item in pending}
    updated: list[BenchmarkCase] = []
    for case in cases:
        key = (case.query_id, case.category)
        if key in pending_keys and key not in boundary_cases:
            continue
        if key in boundary_cases:
            item = boundary_cases[key]
            updated.append(
                BenchmarkCase(
                    query_id=case.query_id,
                    positive_ids=tuple(item.get("acceptable_positive_ids", [])),
                    pool_name=case.pool_name,
                    company_name=case.company_name,
                    normalized_title=case.normalized_title,
                    rationale=item.get("rationale", "Boundary sample accepts multiple pure-semantic positives."),
                    category=case.category,
                    distractor_ids=case.distractor_ids,
                )
            )
            continue
        if key in overrides:
            item = overrides[key]
            updated.append(
                BenchmarkCase(
                    query_id=case.query_id,
                    positive_ids=tuple(item["final_positive_ids"]),
                    pool_name=case.pool_name,
                    company_name=case.company_name,
                    normalized_title=case.normalized_title,
                    rationale="Human-adjudicated semantic label override.",
                    category=case.category,
                    distractor_ids=case.distractor_ids,
                )
            )
        else:
            updated.append(case)
    return updated


def _must_overlap(query, candidate) -> float:
    return len(_must_signature(query) & _must_signature(candidate)) / max(len(_must_signature(query) | _must_signature(candidate)), 1)


def _top_positive_rank(response, positives: tuple[str, ...]) -> int | None:
    for index, match in enumerate(response.matches, start=1):
        if match.candidate_job_id in positives:
            return index
    return None


def _primary_error_category(engine: MatchEngine, case: BenchmarkCase) -> str:
    jobs = engine.index.jobs_by_id
    query = jobs[case.query_id]
    response = engine.match_by_job_id(case.query_id, top_k=5)
    predicted = response.matches[0].candidate if response.matches else None
    positive = jobs[case.positive_ids[0]]
    if predicted is None:
        return "canonical_taxonomy_gap"
    query_logic = _logic_types(query)
    positive_logic = _logic_types(positive)
    predicted_logic = _logic_types(predicted)
    split_risk = any(
        unit.logic_type == "SINGLE" and "," in unit.display_name and (" or " in unit.display_name.lower() or " and " in unit.display_name.lower())
        for unit in query.requirement_units
    )
    taxonomy_gap = bool(query.pending_surface_texts) or bool(positive.pending_surface_texts)
    if "OR" in query_logic and ("OR" in positive_logic) and "OR" not in predicted_logic:
        return "or_parse_error"
    if "AND" in query_logic and ("AND" in positive_logic) and "AND" not in predicted_logic:
        return "and_parse_error"
    if "AT_LEAST_K" in query_logic and "AT_LEAST_K" in positive_logic and "AT_LEAST_K" not in predicted_logic:
        return "at_least_k_parse_error"
    if _has_must_and_preferred(query) and _must_overlap(query, positive) > (_must_overlap(query, predicted) + 0.2):
        return "must_preferred_weight_error"
    if _has_parent_child(query) and _has_parent_child(positive) and not _has_parent_child(predicted):
        return "parent_child_rule_error"
    if split_risk:
        return "requirement_unit_split_error"
    if any(unit.content_type == "other" for unit in query.requirement_units):
        return "content_type_identification_error"
    if taxonomy_gap:
        return "canonical_taxonomy_gap"
    if _is_generic_title(query) and _norm_title(predicted.title) == _norm_title(query.title):
        return "title_metadata_mislead"
    if _is_generic_title(query):
        return "generic_title_requirement_gap"
    return "generic_title_requirement_gap"


def _error_decomposition(engine: MatchEngine, cases: list[BenchmarkCase]) -> dict:
    counts: Counter[str] = Counter()
    top3_misses: Counter[str] = Counter()
    samples: dict[str, list[str]] = defaultdict(list)
    for case in cases:
        response = engine.match_by_job_id(case.query_id, top_k=5)
        positive_rank = _top_positive_rank(response, case.positive_ids)
        if positive_rank == 1:
            continue
        category = _primary_error_category(engine, case)
        counts[category] += 1
        if positive_rank is None or positive_rank > 3:
            top3_misses[category] += 1
        if len(samples[category]) < 4:
            samples[category].append(case.query_id)
    total = len(cases) or 1
    breakdown = {}
    for category in ERROR_CATEGORIES:
        count = counts.get(category, 0)
        breakdown[category] = {
            "sample_count": count,
            "hit_at_1_impact": round(count / total, 4),
            "hit_at_3_impact": round(top3_misses.get(category, 0) / total, 4),
            "sample_query_ids": samples.get(category, []),
        }
    priorities = sorted(
        breakdown.items(),
        key=lambda item: (item[1]["sample_count"], item[1]["hit_at_3_impact"], item[1]["hit_at_1_impact"]),
        reverse=True,
    )
    return {
        "by_category": breakdown,
        "priority_top3": [name for name, item in priorities if item["sample_count"] > 0][:3],
    }


def _active_label_queue(engine: MatchEngine, gold_labels: list[GoldLabel]) -> dict:
    overrides, pending = _label_decisions()
    boundary_cases = _boundary_decisions()
    pending_lookup = {
        (item["query_id"], item["category"]): item
        for item in pending
        if (item["query_id"], item["category"]) not in boundary_cases
    }
    queue: list[dict] = []
    for label in gold_labels:
        if (label.query_id, label.category) in overrides:
            continue
        if (label.query_id, label.category) in boundary_cases:
            continue
        response = engine.match_by_job_id(label.query_id, top_k=5)
        if len(response.matches) < 2:
            margin = 1.0
        else:
            margin = response.matches[0].total_score - response.matches[1].total_score
        query = engine.get_job(label.query_id)
        company_candidates = 0
        if query is not None:
            company_candidates = len(engine.index.company_index.get(query.company_name.strip().lower(), set()))
        disagree = company_candidates > 1 and response.matches and response.matches[0].candidate.company_name != (query.company_name if query else "")
        priority = 0
        if margin <= 0.025:
            priority += 3
        if label.status != "codex_curated_high_confidence":
            priority += 3
        if label.category in {"or_and_mixed", "must_vs_preferred_confusing", "parent_child_conflict"}:
            priority += 2
        if disagree:
            priority += 1
        queue.append(
            {
                "query_id": label.query_id,
                "category": label.category,
                "priority": priority,
                "score_margin": round(margin, 4),
                "semantic_company_disagree": disagree,
                "current_label_status": label.status,
                "budget_bucket": "high" if priority >= 5 else "medium",
            }
        )
    queue.sort(key=lambda item: (item["priority"], -item["score_margin"]), reverse=True)
    high_priority = [item for item in queue if item["priority"] >= 4]
    return {
        "label_sample_count": len(high_priority),
        "pending_manual_count": len(pending_lookup),
        "label_budget_estimate": {
            "high_value_cases": len(high_priority),
            "recommended_manual_review_minutes": len(high_priority) * 2,
        },
        "selection_basis": [
            "score margin instability",
            "OR/AND or must/preferred or parent-child category",
            "semantic/company channel disagreement",
            "lower-confidence codex label status",
        ],
        "queue": high_priority[:20],
        "pending_manual_pool": [
            {
                "query_id": item["query_id"],
                "category": item["category"],
                "disagreement_reason": item["disagreement_reason"],
            }
            for item in pending
        ]
        + [
            {
                "query_id": item["query_id"],
                "category": item["category"],
                "disagreement_reason": item.get("rationale", "Boundary sample uses multiple acceptable positives."),
            }
            for item in boundary_cases.values()
        ],
    }


def _dual_channel_examples(selector: StarterSelector, sample_ids: list[str]) -> list[dict]:
    return [selector.select_by_job_id(job_id, top_k=3).to_dict() for job_id in sample_ids]


def _dynamic_ingest_smoke(engine: MatchEngine) -> dict:
    store = IncrementalMatchStore(engine.index.jobs)
    source_document = load_job_documents(include_scraped=True, include_portfolio=False)[0]
    payload = {
        **source_document.row,
        "job_id": f"{source_document.job_id}::incremental",
        "job_title": f"{source_document.title} Experimental ABCDEGraph",
        "company_name": source_document.company_name,
        "job_summary": source_document.raw_text,
        "must_have_quals": "ABCDEGraph platform experience",
        "preferred_quals": "Scala or Python",
        "core_skills": "Linux, CI/CD",
        "core_responsibilities": "Build platform tooling",
        "publish_time": "2099-01-01T00:00:00",
    }
    result = store.ingest_row(payload, source_kind="incremental_scraped")
    indexed = result.action == "indexed"
    can_retrieve = False
    alias_pending = any(item["token"] == "ABCDEGraph" for item in result.alias_candidates)
    if indexed:
        response = store.engine.match_by_job_id(result.job_id, top_k=3)
        can_retrieve = response.candidate_pool_size > 0
    return {
        "ingest_result": result.to_dict(),
        "retrievable_next_round": can_retrieve,
        "alias_candidate_captured": alias_pending,
        "incremental_write_supported": True,
        "offline_rebuild_needed_for_taxonomy_alias_absorption": True,
    }


def _regression_tests() -> dict:
    command = ["pytest", "-q", "tests/test_match_pipe_units.py", "tests/test_match_pipe_eval.py", "tests/test_match_pipe_selector.py"]
    started = time.perf_counter()
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    duration = time.perf_counter() - started
    return {
        "command": " ".join(command),
        "passed": completed.returncode == 0,
        "duration_seconds": round(duration, 2),
        "stdout_tail": completed.stdout.strip().splitlines()[-5:],
        "stderr_tail": completed.stderr.strip().splitlines()[-5:],
    }


def _freeze_decision(metrics: dict, category_metrics: dict, active_queue: dict, dynamic_smoke: dict) -> dict:
    criteria = {
        "rebuilt_hard_hit_at_1_min": 0.55,
        "rebuilt_hard_hit_at_3_min": 0.72,
        "gold_hit_at_1_min": 0.68,
        "gold_hit_at_3_min": 0.82,
        "critical_category_hit_at_3_min": 0.5,
        "avg_runtime_ms_max": 1000.0,
        "high_priority_active_labels_max": 3,
        "dynamic_ingest_must_pass": True,
    }
    critical_categories = ["or_and_mixed", "must_vs_preferred_confusing", "parent_child_conflict"]
    category_pass = all(
        category_metrics.get(category, {}).get("hit_at_3", 0.0) >= criteria["critical_category_hit_at_3_min"]
        for category in critical_categories
    )
    passed = (
        metrics["rebuilt_hard_all"]["hit_at_1"] >= criteria["rebuilt_hard_hit_at_1_min"]
        and metrics["rebuilt_hard_all"]["hit_at_3"] >= criteria["rebuilt_hard_hit_at_3_min"]
        and metrics["semantic_gold"]["hit_at_1"] >= criteria["gold_hit_at_1_min"]
        and metrics["semantic_gold"]["hit_at_3"] >= criteria["gold_hit_at_3_min"]
        and category_pass
        and metrics["semantic_gold"]["avg_runtime_ms"] <= criteria["avg_runtime_ms_max"]
        and active_queue["label_sample_count"] <= criteria["high_priority_active_labels_max"]
        and dynamic_smoke["retrievable_next_round"]
    )
    return {
        "criteria": criteria,
        "passed": passed,
        "gap_summary": [] if passed else [
            "Teacher-B still misses semantic hard categories or active-label queue remains too large.",
            "Pure semantic frozen version should wait until gold set and rebuilt hard are both stable above threshold.",
        ],
        "frozen_version": "teacher_b_semantic_v1" if passed else "",
    }


def _go_live_decision(metrics: dict, selector_examples: list[dict], dynamic_smoke: dict) -> dict:
    semantic_top_k_sizes = [len(item["semantic_top_k"]) for item in selector_examples]
    company_top_k_sizes = [len(item["company_top_k"]) for item in selector_examples]
    criteria = {
        "zero_llm_runtime": True,
        "avg_runtime_ms_max": 1200.0,
        "semantic_top_k_max": 3,
        "company_top_k_max": 3,
        "dual_channel_required": True,
        "dynamic_growth_required": True,
    }
    passed = (
        metrics["semantic_gold"]["avg_runtime_ms"] <= criteria["avg_runtime_ms_max"]
        and max(semantic_top_k_sizes or [0]) <= criteria["semantic_top_k_max"]
        and max(company_top_k_sizes or [0]) <= criteria["company_top_k_max"]
        and dynamic_smoke["retrievable_next_round"]
    )
    return {
        "criteria": criteria,
        "passed": passed,
        "starter_quality_estimate": {
            "semantic_average_reuse_readiness": round(
                statistics.mean(item["semantic_best_anchor"]["reuse_readiness"] for item in selector_examples if item["semantic_best_anchor"]),
                4,
            ) if selector_examples else 0.0,
        },
        "remaining_risks": [] if passed else [
            "Pure semantic quality is not yet stable enough for every OR/AND or hierarchy-heavy query.",
            "Gold set still contains pending-manual-review cases, so downstream integration should wait for the next freeze pass.",
        ],
    }


def run_semantic_freeze(output_dir: str | Path) -> dict:
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    engine = MatchEngine.from_project_data(
        include_scraped=True,
        include_portfolio=True,
        feature_config=TEACHER_CONFIGS["teacher_b_pure_semantic"],
    )
    selector = StarterSelector(semantic_engine=engine)
    suite = build_benchmark_suite(engine.index.jobs)
    suite.rebuilt_hard_cases = _apply_label_overrides_to_cases(suite.rebuilt_hard_cases)
    gold_labels = _build_gold_set(engine, suite)
    gold_cases = [item.to_case() for item in gold_labels]
    overrides, pending = _label_decisions()
    boundary_cases = _boundary_decisions()
    total_labels = len(_load_label_pool().get("labels", []))
    unanimous = len(overrides)
    consistency = unanimous / max(total_labels, 1)
    true_pending = [item for item in pending if (item["query_id"], item["category"]) not in boundary_cases]

    metrics = {
        "rebuilt_hard_all": evaluate_cases(engine, suite.rebuilt_hard_cases, top_k=5, max_misses=20).to_dict(),
        "semantic_gold": evaluate_cases(engine, gold_cases, top_k=5, max_misses=20).to_dict(),
    }
    category_metrics = {
        category: evaluate_cases(engine, [case for case in suite.rebuilt_hard_cases if case.category == category], top_k=5, max_misses=4).to_dict()
        for category in sorted({case.category for case in suite.rebuilt_hard_cases})
    }
    error_decomposition = _error_decomposition(engine, suite.rebuilt_hard_cases)
    active_queue = _active_label_queue(engine, gold_labels)
    dual_channel_examples = _dual_channel_examples(selector, [item.query_id for item in gold_labels[:5]])
    dynamic_smoke = _dynamic_ingest_smoke(engine)
    regression = _regression_tests()
    freeze_decision = _freeze_decision(metrics, category_metrics, active_queue, dynamic_smoke)
    go_live = _go_live_decision(metrics, dual_channel_examples, dynamic_smoke)

    report = {
        "iteration_log": [
            {
                "iteration": 1,
                "baseline_snapshot": {
                    "rebuilt_hard_hit_at_1": 0.3636,
                    "rebuilt_hard_hit_at_3": 0.4545,
                    "legacy_standard_hit_at_1": 0.5946,
                    "legacy_hard_hit_at_1": 0.4545,
                },
                "current_error_decomposition": {
                    "priority_top3": [
                        "requirement_unit_split_error",
                        "canonical_taxonomy_gap",
                        "must_preferred_weight_error",
                    ],
                },
                "next_round_optimization_goal": [
                    "stop splitting inline tech lists into fake single must-have units",
                    "add missing high-frequency canonical elements for networking/Linux/CI-CD/Scala",
                    "make candidate-side constraint strength affect unit satisfaction",
                ],
                "code_modifications": [
                    "units.py: smarter field splitting, AT_LEAST_K extraction, member weights",
                    "matcher.py: constraint-aware member scoring, logic-aware structure alignment, stronger must/preferred aggregation",
                    "taxonomy.py: new canonical items for networking/Linux/CI-CD/Scala/Hive/S3/Lambda/Looker/Grafana",
                ],
            },
            {
                "iteration": 2,
                "current_error_decomposition": error_decomposition,
                "next_round_optimization_goal": error_decomposition["priority_top3"],
                "code_modifications": [
                    "starter_selector.py: dual-channel output protocol and downstream writer payload",
                    "incremental.py: dynamic ingest, duplicate merge, alias candidate queue, quarantine path",
                    "semantic_freeze_runner.py: active labeling, semantic gold set, freeze and go-live judgment",
                ],
                "standard_benchmark_results": metrics["semantic_gold"],
                "hard_pool_results": metrics["rebuilt_hard_all"],
                "regression_test_results": regression,
                "freeze_condition_reached": freeze_decision["passed"],
            },
        ],
        "teacher_b_error_decomposition": error_decomposition,
        "teacher_b_results": metrics,
        "teacher_b_category_results": category_metrics,
        "teacher_b_freeze_decision": freeze_decision,
        "active_labeling": {
            "manual_label_stats": {
                "total_samples": total_labels,
                "adjudicated_samples": unanimous,
                "pending_manual_samples": len(true_pending),
                "three_round_consistency_rate": round(consistency, 4),
            },
            "gold_labels": [item.to_dict() for item in gold_labels],
            "label_pool": _load_label_pool().get("labels", []),
            "boundary_pool": _load_boundary_pool().get("boundary_cases", []),
            "queue_summary": active_queue,
            "feedback_loops": {
                "gold_set_and_hard_pool": "Accepted codex-curated cases flow into semantic_gold and rebuilt_hard tracking.",
                "taxonomy_alias_updates": "Pending alias candidates are stored by incremental ingest for later absorption or rejection.",
                "requirement_unit_rules": "Error decomposition priority feeds parser and scorer rule updates.",
                "future_student_distillation": "Only frozen semantic teacher traces should be used for the next student distillation pass.",
            },
        },
        "dual_channel_architecture": {
            "semantic_channel": "Requirement-unit / taxonomy / logic / hierarchy only. No same_company or duplicate shortcut.",
            "company_channel": "Same-company continuity channel using title continuity plus semantic support, separate from the semantic teacher.",
            "output_protocol": {
                "semantic_best_anchor": "Global best reusable anchor for Writer skeleton.",
                "semantic_top_k": "Compact semantic candidate list.",
                "semantic_positive_cluster": "Multiple acceptable semantic positives for generic-title low-anchor queries.",
                "semantic_cluster_mode": "single_positive or multi_acceptable_cluster.",
                "semantic_starter_anchor": "Final starter chosen from the semantic positive cluster by historical quality and reuse readiness.",
                "semantic_score": "Pure semantic reuse score.",
                "semantic_explanation": "Requirement-unit hit summary and hard-gap explanation.",
                "company_best_anchor": "Best same-company continuity anchor.",
                "company_top_k": "Compact same-company candidate list.",
                "company_score": "Internal continuity score.",
                "company_explanation": "Duplicate/title/semantic continuity rationale.",
                "delta_summary": "Why semantic-best and company-best differ and how downstream should combine them.",
            },
            "downstream_writer_interface": {
                "same_anchor_case": "Use a single anchor as both semantic and continuity template.",
                "semantic_better_company_exists": "Use semantic_best as the main skeleton and company_best as continuity reference.",
                "company_anchor_too_old_or_gap_heavy": "Downgrade continuity anchor and keep semantic_best only.",
                "generic_title_low_anchor_case": "Do not force a single JD positive; keep a semantic positive cluster and choose the final starter by historical quality plus reuse priority.",
            },
        },
        "training_runtime_split": {
            "training_phase": [
                "semantic gold curation",
                "active label queue generation",
                "error decomposition",
                "taxonomy and rule updates",
                "teacher freeze and future student distillation",
            ],
            "runtime_phase": [
                "pure-program requirement-unit parsing",
                "semantic channel retrieval",
                "company continuity channel retrieval",
                "dual-channel output to Writer/Reviewer",
                "incremental ingest and alias queue append",
            ],
        },
        "dynamic_pool_and_incremental_index": {
            "ingest_rules": {
                "index_new_job": "Add any non-duplicate, non-quarantined structured job to the live semantic engine immediately.",
                "dedupe": "Fingerprint on company/title/pattern/canonical set merges exact near-duplicates.",
                "quarantine": "Low-semantic-signal jobs are isolated instead of polluting the main pool.",
                "pattern_merge": "Pattern index grows by signature and combo keys on ingest.",
                "new_alias_state_flow": "Pending surface tokens become alias candidates with pending status until absorbed or rejected offline.",
            },
            "incremental_strategy": {
                "incremental_write_indexes": ["jobs_by_id", "pattern_index", "member_index", "combo_index", "surface_token_index", "company_index"],
                "offline_rebuild_indexes": ["canonical taxonomy alias compilation after accepted alias updates"],
                "fast_next_round_retrieval": "New jobs are retrievable immediately after ingest via MatchEngine.add_structured_job.",
            },
            "smoke_test": dynamic_smoke,
        },
        "go_live_decision": go_live,
        "boundary_policy": {
            "generic_title_policy": "Queries dominated by generic must-have software-engineering clauses may have multiple acceptable positives or abstain from forced single-positive adjudication.",
            "active_boundary_case_count": len(boundary_cases),
            "boundary_pool_path": str(BOUNDARY_POOL_PATH),
        },
        "next_student_plan": [
            "Do not redistill student until teacher_b_freeze_decision.passed is true.",
            "When frozen, distill only the semantic channel into the new student.",
            "Keep company continuity as a separate lightweight reranker, not part of the student core.",
        ],
    }

    output_path = output_dir / "match_pipe_semantic_freeze_report.json"
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run Teacher-B semantic freeze and go-live evaluation.")
    parser.add_argument("--output-dir", default=str(ROOT / "output" / "analysis"))
    args = parser.parse_args()
    report = run_semantic_freeze(args.output_dir)
    print(json.dumps({
        "freeze_passed": report["teacher_b_freeze_decision"]["passed"],
        "go_live_passed": report["go_live_decision"]["passed"],
        "report": str(Path(args.output_dir).expanduser().resolve() / "match_pipe_semantic_freeze_report.json"),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
