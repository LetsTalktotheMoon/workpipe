#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def slugify(value: str) -> str:
    import re

    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "case"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_old_pipe(run_dir: Path) -> dict[str, dict[str, Any]]:
    data: dict[str, dict[str, Any]] = {}
    for case_dir in sorted([p for p in run_dir.iterdir() if p.is_dir()]):
        payload = load_json(case_dir / "codex.json")
        data[case_dir.name] = {
            "score": payload["weighted_score"],
            "verdict": payload["overall_verdict"],
            "duration_seconds": payload.get("duration_seconds"),
            "deductions": [
                f"{dim}:{f.get('severity')}:{f.get('field')}"
                for dim, dim_payload in payload.get("scores", {}).items()
                for f in dim_payload.get("findings", [])
                if f.get("severity") in {"critical", "high"}
            ][:6],
        }
    return data


def load_new_pipe(run_dir: Path) -> dict[str, dict[str, Any]]:
    data: dict[str, dict[str, Any]] = {}
    for case_dir in sorted([p for p in run_dir.iterdir() if p.is_dir()]):
        payload = load_json(case_dir / "codex.json")
        agg = payload["aggregated"]
        data[case_dir.name] = {
            "score": agg["weighted_score"],
            "verdict": agg["overall_verdict"],
            "duration_seconds": payload.get("duration_seconds"),
            "deductions": [
                f"{f.get('rule_id')}:{f.get('severity')}:{f.get('field')}"
                for section in ("pass_1_structural", "pass_2_attention", "pass_3_substance", "pass_5_localization")
                for f in payload.get("raw_json", {}).get(section, {}).get("findings", [])
                if f.get("severity") in {"critical", "high"}
            ][:6],
        }
    return data


def parse_version_arg(raw: str) -> tuple[str, Path]:
    if "=" not in raw:
        raise ValueError(f"Invalid --version {raw!r}; expected label=/path/to/run")
    label, path = raw.split("=", 1)
    return label.strip(), Path(path).expanduser().resolve()


def build_report(
    *,
    old_label: str,
    old_data: dict[str, dict[str, Any]],
    versions: list[tuple[str, dict[str, dict[str, Any]]]],
) -> str:
    case_names = sorted(old_data)
    lines = [
        "# Reviewer 迭代对比",
        "",
        "## 分数表",
        "",
    ]
    headers = ["Case", old_label]
    headers.extend(label for label, _ in versions)
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for case in case_names:
        row = [case, f"{old_data[case]['score']:.1f} ({old_data[case]['verdict']})"]
        for _, version_data in versions:
            row.append(f"{version_data[case]['score']:.1f} ({version_data[case]['verdict']})")
        lines.append("| " + " | ".join(row) + " |")

    lines.extend(["", "## 扣分项表", ""])
    headers = ["Case", f"{old_label} 主要扣分"]
    headers.extend(f"{label} 主要扣分" for label, _ in versions)
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for case in case_names:
        row = [case, "<br>".join(old_data[case]["deductions"]) or "none"]
        for _, version_data in versions:
            row.append("<br>".join(version_data[case]["deductions"]) or "none")
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a score matrix and deduction matrix across reviewer iterations.")
    parser.add_argument("--old-run", required=True)
    parser.add_argument("--old-label", default="旧pipe")
    parser.add_argument("--version", action="append", default=[], help="Format: label=/abs/path/to/run")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    old_data = load_old_pipe(Path(args.old_run).resolve())
    versions: list[tuple[str, dict[str, dict[str, Any]]]] = []
    for raw in args.version:
        label, path = parse_version_arg(raw)
        versions.append((label, load_new_pipe(path)))

    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_report(old_label=args.old_label, old_data=old_data, versions=versions), encoding="utf-8")
    print(str(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
