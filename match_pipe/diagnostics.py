#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


FREEZE_CRITERIA = {
    "teacher_standard_hit_at_1_min": 0.94,
    "teacher_standard_hit_at_3_min": 0.97,
    "teacher_hard_hit_at_1_min": 0.80,
    "teacher_hard_hit_at_3_min": 0.90,
    "teacher_runtime_ms_max": 1200.0,
}


def build_diagnostic_summary(eval_payload: dict, *, tests_passed: bool) -> dict:
    teacher_standard = eval_payload["teacher"]["standard"]
    teacher_hard = eval_payload["teacher"]["hard"]
    student_standard = eval_payload["student"]["standard"]
    student_hard = eval_payload["student"]["hard"]

    freeze_checks = {
        "teacher_standard_hit_at_1": teacher_standard["hit_at_1"] >= FREEZE_CRITERIA["teacher_standard_hit_at_1_min"],
        "teacher_standard_hit_at_3": teacher_standard["hit_at_3"] >= FREEZE_CRITERIA["teacher_standard_hit_at_3_min"],
        "teacher_hard_hit_at_1": teacher_hard["hit_at_1"] >= FREEZE_CRITERIA["teacher_hard_hit_at_1_min"],
        "teacher_hard_hit_at_3": teacher_hard["hit_at_3"] >= FREEZE_CRITERIA["teacher_hard_hit_at_3_min"],
        "teacher_runtime": teacher_standard["avg_runtime_ms"] <= FREEZE_CRITERIA["teacher_runtime_ms_max"] and teacher_hard["avg_runtime_ms"] <= FREEZE_CRITERIA["teacher_runtime_ms_max"],
        "regression_tests": tests_passed,
    }
    teacher_frozen = all(freeze_checks.values())
    student_ready = (
        student_standard["hit_at_1"] >= 0.88
        and student_hard["hit_at_1"] >= 0.72
    )
    recommendation = "teacher" if teacher_frozen else "student"
    if teacher_frozen and student_ready:
        recommendation = "student_for_online_retrieval_teacher_for_offline_audit"

    return {
        "freeze_criteria": FREEZE_CRITERIA,
        "freeze_checks": freeze_checks,
        "teacher_frozen": teacher_frozen,
        "student_ready": student_ready,
        "recommended_deployment": recommendation,
        "teacher_advantage": {
            "standard_hit_at_1_delta": round(teacher_standard["hit_at_1"] - student_standard["hit_at_1"], 4),
            "hard_hit_at_1_delta": round(teacher_hard["hit_at_1"] - student_hard["hit_at_1"], 4),
            "standard_hit_at_3_delta": round(teacher_standard["hit_at_3"] - student_standard["hit_at_3"], 4),
            "hard_hit_at_3_delta": round(teacher_hard["hit_at_3"] - student_hard["hit_at_3"], 4),
        },
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Summarize teacher/student freeze state from an eval JSON.")
    parser.add_argument("--eval-json", required=True)
    parser.add_argument("--output", default="")
    parser.add_argument("--tests-passed", action="store_true")
    args = parser.parse_args()

    eval_path = Path(args.eval_json).expanduser().resolve()
    payload = json.loads(eval_path.read_text())
    summary = build_diagnostic_summary(payload, tests_passed=args.tests_passed)

    output = Path(args.output).expanduser().resolve() if str(args.output or "").strip() else None
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
