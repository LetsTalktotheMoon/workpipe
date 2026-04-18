#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def detect_mode(run_dir: Path) -> str:
    for case_dir in sorted(p for p in run_dir.iterdir() if p.is_dir()):
        if (case_dir / "case_summary.json").exists():
            return "new"
        if (case_dir / "codex.json").exists():
            return "old"
    raise FileNotFoundError(f"No readable case payloads found in {run_dir}")


def load_run(run_dir: Path, mode: str) -> dict[str, dict[str, Any]]:
    data: dict[str, dict[str, Any]] = {}
    for case_dir in sorted(p for p in run_dir.iterdir() if p.is_dir()):
        if mode == "new":
            case_path = case_dir / "case_summary.json"
            if not case_path.exists():
                continue
            payload = load_json(case_path)
            codex = payload["codex"]
            agg = codex["aggregated"]
            findings = [
                f"{f.get('rule_id')}:{f.get('severity')}:{f.get('field')}"
                for section in ("pass_1_structural", "pass_2_attention", "pass_3_substance", "pass_5_localization")
                for f in codex["raw_json"].get(section, {}).get("findings", [])
                if f.get("severity") in {"critical", "high"}
            ]
            label = payload["label"]
            data[label] = {
                "score": agg["weighted_score"],
                "verdict": agg["overall_verdict"],
                "findings": findings[:8],
            }
        else:
            case_path = case_dir / "codex.json"
            if not case_path.exists():
                continue
            payload = load_json(case_path)
            findings = [
                f"{dim}:{f.get('severity')}:{f.get('field')}"
                for dim, dim_payload in payload.get("scores", {}).items()
                for f in dim_payload.get("findings", [])
                if f.get("severity") in {"critical", "high"}
            ]
            label = case_dir.name
            data[label] = {
                "score": payload["weighted_score"],
                "verdict": payload["overall_verdict"],
                "findings": findings[:8],
            }
    return data


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "case"


def remap_old_labels(data: dict[str, dict[str, Any]], labels: dict[str, Any]) -> dict[str, dict[str, Any]]:
    slug_to_label = {slugify(label): label for label in labels}
    remapped: dict[str, dict[str, Any]] = {}
    for raw_label, payload in data.items():
        target = slug_to_label.get(raw_label, raw_label)
        remapped[target] = payload
    return remapped


def build_report(
    *,
    run_label: str,
    run_data: dict[str, dict[str, Any]],
    labels: dict[str, dict[str, str]],
    only_present: bool,
) -> str:
    case_items = [
        (case, target)
        for case, target in labels.items()
        if not only_present or case in run_data
    ]
    total = len(case_items)
    matched = 0
    wrong_cases: list[str] = []
    lines = [f"# {run_label} 对照 HR 标签", ""]

    headers = ["Case", "目标", "实际", "分数", "是否命中", "主要高/致命项", "标签理由"]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for case, target in case_items:
        actual = run_data.get(case)
        if actual is None:
            actual_verdict = "missing"
            score = "?"
            hit = "否"
            findings = "missing"
            wrong_cases.append(case)
        else:
            actual_verdict = actual["verdict"]
            score = f"{actual['score']:.1f}"
            is_hit = actual_verdict == target["target_verdict"]
            hit = "是" if is_hit else "否"
            findings = "<br>".join(actual["findings"]) or "none"
            if is_hit:
                matched += 1
            else:
                wrong_cases.append(case)
        lines.append(
            "| "
            + " | ".join(
                [
                    case,
                    target["target_verdict"],
                    actual_verdict,
                    score,
                    hit,
                    findings,
                    target["reason"],
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## 汇总",
            "",
            f"- 命中: `{matched}/{total}`",
            f"- 错判: `{len(wrong_cases)}`",
            f"- 错判列表: `{', '.join(wrong_cases) if wrong_cases else 'none'}`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a reviewer run against manual HR labels.")
    parser.add_argument("--run", action="append", required=True, help="Run directory; may be repeated")
    parser.add_argument("--labels", required=True, help="JSON file with target_verdict/reason per case label")
    parser.add_argument("--run-label", default="run")
    parser.add_argument("--mode", choices=("auto", "new", "old"), default="auto")
    parser.add_argument("--only-present", action="store_true")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    labels = load_json(Path(args.labels).resolve())
    run_data: dict[str, dict[str, Any]] = {}
    for raw_run in args.run:
        run_dir = Path(raw_run).resolve()
        mode = detect_mode(run_dir) if args.mode == "auto" else args.mode
        current = load_run(run_dir, mode)
        if mode == "old":
            current = remap_old_labels(current, labels)
        overlap = sorted(set(run_data) & set(current))
        if overlap:
            raise ValueError(f"Duplicate case labels across runs: {', '.join(overlap)}")
        run_data.update(current)

    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        build_report(run_label=args.run_label, run_data=run_data, labels=labels, only_present=args.only_present),
        encoding="utf-8",
    )
    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
