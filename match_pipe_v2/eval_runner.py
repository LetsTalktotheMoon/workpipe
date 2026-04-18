#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import time

from .benchmark import build_benchmark_suite, evaluate_cases, split_cases
from .matcher import MatchEngine
from .student import StudentMatchEngine, distill_student_weights


def run_evaluation(output_path: str | Path | None = None) -> dict:
    build_start = time.perf_counter()
    teacher = MatchEngine.from_project_data(include_scraped=True, include_portfolio=True)
    build_seconds = time.perf_counter() - build_start

    suite = build_benchmark_suite(teacher.index.jobs)
    standard_train, standard_test = split_cases(suite.standard_cases)
    hard_train, hard_test = split_cases(suite.hard_cases)

    teacher_standard = evaluate_cases(teacher, standard_test)
    teacher_hard = evaluate_cases(teacher, hard_test)

    distilled_weights = distill_student_weights(teacher.index.jobs, standard_train)
    student = StudentMatchEngine(teacher.index.jobs, weights=distilled_weights)
    student_standard = evaluate_cases(student, standard_test)
    student_hard = evaluate_cases(student, hard_test)

    payload = {
        "build_seconds": round(build_seconds, 2),
        "suite": suite.to_dict(),
        "splits": {
            "standard_train": len(standard_train),
            "standard_test": len(standard_test),
            "hard_train": len(hard_train),
            "hard_test": len(hard_test),
        },
        "teacher": {
            "standard": teacher_standard.to_dict(),
            "hard": teacher_hard.to_dict(),
        },
        "student": {
            "weights": distilled_weights.to_dict(),
            "standard": student_standard.to_dict(),
            "hard": student_hard.to_dict(),
        },
    }

    if output_path is not None:
        output_path = Path(output_path).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run teacher/student evaluation for match_pipe.")
    parser.add_argument("--output", default="", help="Optional JSON output path.")
    args = parser.parse_args()

    output = Path(args.output).expanduser().resolve() if str(args.output or "").strip() else None
    payload = run_evaluation(output)
    if output is None:
        print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
