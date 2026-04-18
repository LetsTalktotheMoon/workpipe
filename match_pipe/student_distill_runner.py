#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import time

from repo_paths import repo_relative_path

from .benchmark import evaluate_cases, split_cases
from .frozen_teacher import frozen_teacher_manifest
from .matcher import MatchEngine
from .semantic_freeze_runner import _apply_label_overrides_to_cases, _build_gold_set
from .student import (
    LegacyStudentMatchEngine,
    StudentMatchEngine,
    distill_legacy_student_weights,
    distill_student_weights,
    generate_teacher_traces,
)


ROOT = Path(__file__).resolve().parents[1]


def run_student_distillation(output_dir: str | Path) -> dict:
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = frozen_teacher_manifest()
    build_start = time.perf_counter()
    teacher = MatchEngine.from_project_data(
        include_scraped=True,
        include_portfolio=True,
        feature_config=manifest.feature_config,
    )
    build_seconds = time.perf_counter() - build_start

    from .benchmark import build_benchmark_suite

    suite = build_benchmark_suite(teacher.index.jobs)
    suite.rebuilt_hard_cases = _apply_label_overrides_to_cases(suite.rebuilt_hard_cases)
    gold_cases = [item.to_case() for item in _build_gold_set(teacher, suite)]

    rebuilt_train, rebuilt_eval = split_cases(suite.rebuilt_hard_cases)
    gold_train, gold_eval = split_cases(gold_cases)
    train_cases = sorted(rebuilt_train + gold_train, key=lambda item: (item.pool_name, item.query_id))
    traces = generate_teacher_traces(teacher, train_cases, top_k=5)
    traces_path = output_dir / "teacher_b_semantic_v1_traces.json"
    traces_path.write_text(
        json.dumps([item.to_dict() for item in traces], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    new_weights = distill_student_weights(teacher.index.jobs, train_cases, teacher=teacher)
    old_weights = distill_legacy_student_weights(teacher.index.jobs, train_cases)
    new_student = StudentMatchEngine(teacher.index.jobs, weights=new_weights)
    old_student = LegacyStudentMatchEngine(teacher.index.jobs, weights=old_weights)

    eval_sets = {
        "rebuilt_hard_all": suite.rebuilt_hard_cases,
        "rebuilt_hard_holdout": rebuilt_eval,
        "semantic_gold": gold_cases,
        "semantic_gold_holdout": gold_eval,
    }
    category_sets = {
        category: [case for case in suite.rebuilt_hard_cases if case.category == category]
        for category in sorted({case.category for case in suite.rebuilt_hard_cases})
    }

    results = {
        "teacher": {
            name: evaluate_cases(teacher, cases, top_k=5, max_misses=12).to_dict()
            for name, cases in eval_sets.items()
            if cases
        },
        "new_student": {
            "weights": new_weights.to_dict(),
            "metrics": {
                name: evaluate_cases(new_student, cases, top_k=5, max_misses=12).to_dict()
                for name, cases in eval_sets.items()
                if cases
            },
        },
        "old_student": {
            "weights": old_weights.to_dict(),
            "metrics": {
                name: evaluate_cases(old_student, cases, top_k=5, max_misses=12).to_dict()
                for name, cases in eval_sets.items()
                if cases
            },
        },
        "difficult_category_breakdown": {
            category: {
                "teacher": evaluate_cases(teacher, cases, top_k=5, max_misses=4).to_dict(),
                "new_student": evaluate_cases(new_student, cases, top_k=5, max_misses=4).to_dict(),
                "old_student": evaluate_cases(old_student, cases, top_k=5, max_misses=4).to_dict(),
            }
            for category, cases in category_sets.items()
            if cases
        },
    }

    comparison = {
        "teacher_vs_new_student": {
            "rebuilt_hard_all_hit_at_1_delta": round(
                results["teacher"]["rebuilt_hard_all"]["hit_at_1"] - results["new_student"]["metrics"]["rebuilt_hard_all"]["hit_at_1"],
                4,
            ),
            "semantic_gold_hit_at_1_delta": round(
                results["teacher"]["semantic_gold"]["hit_at_1"] - results["new_student"]["metrics"]["semantic_gold"]["hit_at_1"],
                4,
            ),
        },
        "new_vs_old_student": {
            "rebuilt_hard_all_hit_at_1_delta": round(
                results["new_student"]["metrics"]["rebuilt_hard_all"]["hit_at_1"] - results["old_student"]["metrics"]["rebuilt_hard_all"]["hit_at_1"],
                4,
            ),
            "semantic_gold_hit_at_1_delta": round(
                results["new_student"]["metrics"]["semantic_gold"]["hit_at_1"] - results["old_student"]["metrics"]["semantic_gold"]["hit_at_1"],
                4,
            ),
            "rebuilt_hard_all_runtime_ms_delta": round(
                results["new_student"]["metrics"]["rebuilt_hard_all"]["avg_runtime_ms"] - results["old_student"]["metrics"]["rebuilt_hard_all"]["avg_runtime_ms"],
                2,
            ),
        },
    }

    payload = {
        "teacher_version": manifest.version,
        "teacher_manifest": manifest.to_dict(),
        "build_seconds": round(build_seconds, 2),
        "distillation": {
            "train_case_count": len(train_cases),
            "rebuilt_hard_train": len(rebuilt_train),
            "rebuilt_hard_holdout": len(rebuilt_eval),
            "semantic_gold_train": len(gold_train),
            "semantic_gold_holdout": len(gold_eval),
            "trace_count": len(traces),
            "trace_path": str(traces_path),
            "student_scope": "Pure semantic channel only. No same_company or duplicate features.",
        },
        "results": results,
        "comparison": comparison,
        "deployment_recommendation": {
            "offline_teacher": manifest.version,
            "online_student": "student_semantic_v2",
            "company_channel": "keep separate; do not merge into student core",
        },
    }

    output_path = output_dir / "match_pipe_student_distill_report.json"
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Distill semantic student from frozen teacher_b_semantic_v1.")
    parser.add_argument("--output-dir", default="output/analysis")
    args = parser.parse_args()
    payload = run_student_distillation(args.output_dir)
    print(
        json.dumps(
            {
                "report": repo_relative_path(Path(args.output_dir).expanduser() / "match_pipe_student_distill_report.json"),
                "trace_count": payload["distillation"]["trace_count"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
