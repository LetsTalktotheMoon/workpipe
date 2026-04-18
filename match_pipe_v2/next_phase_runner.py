#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from repo_paths import repo_relative_path

from .downstream_validation_runner import run_small_flow_validation
from .frozen_teacher import frozen_teacher_manifest
from .semantic_freeze_runner import run_semantic_freeze
from .student_distill_runner import run_student_distillation


ROOT = Path(__file__).resolve().parents[1]


def run_next_phase(output_dir: str | Path, *, small_flow_sample_size: int = 2) -> dict:
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = frozen_teacher_manifest()
    manifest_path = output_dir / "teacher_b_semantic_v1_manifest.json"
    manifest_path.write_text(json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    freeze_report_path = output_dir / "match_pipe_semantic_freeze_report.json"
    student_report_path = output_dir / "match_pipe_student_distill_report.json"
    small_flow_report_path = output_dir / "match_pipe_small_flow_validation_report.json"

    freeze_report = (
        json.loads(freeze_report_path.read_text(encoding="utf-8"))
        if freeze_report_path.exists()
        else run_semantic_freeze(output_dir)
    )
    student_report = (
        json.loads(student_report_path.read_text(encoding="utf-8"))
        if student_report_path.exists()
        else run_student_distillation(output_dir)
    )
    small_flow_report = (
        json.loads(small_flow_report_path.read_text(encoding="utf-8"))
        if small_flow_report_path.exists()
        else run_small_flow_validation(output_dir, sample_size=small_flow_sample_size)
    )

    payload = {
        "teacher_freeze_solidification": {
            "manifest_path": repo_relative_path(manifest_path),
            "teacher_manifest": manifest.to_dict(),
            "freeze_report_path": repo_relative_path(freeze_report_path),
            "freeze_passed": freeze_report["teacher_b_freeze_decision"]["passed"],
            "frozen_rule_layer": list(manifest.freeze_rule_layers),
            "growth_knowledge_layer": list(manifest.growth_knowledge_layers),
        },
        "student_redistillation": {
            "report_path": repo_relative_path(student_report_path),
            "teacher_vs_student": student_report["comparison"],
        },
        "small_flow_validation": {
            "report_path": repo_relative_path(small_flow_report_path),
            "execution_summary": small_flow_report["execution_summary"],
            "retry_plan": small_flow_report["retry_plan"],
        },
        "boundary_policy": freeze_report["boundary_policy"],
        "recommended_deployment": {
            "offline_teacher": manifest.version,
            "online_student": student_report["deployment_recommendation"]["online_student"],
            "company_channel": "separate auxiliary continuity channel",
        },
    }
    output_path = output_dir / "match_pipe_next_phase_report.json"
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run the post-freeze next phase for match_pipe.")
    parser.add_argument("--output-dir", default="output/analysis")
    parser.add_argument("--small-flow-sample-size", type=int, default=2)
    args = parser.parse_args()
    payload = run_next_phase(args.output_dir, small_flow_sample_size=args.small_flow_sample_size)
    print(
        json.dumps(
            {
                "report": repo_relative_path(Path(args.output_dir).expanduser() / "match_pipe_next_phase_report.json"),
                "student_report": payload["student_redistillation"]["report_path"],
                "small_flow_report": payload["small_flow_validation"]["report_path"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
