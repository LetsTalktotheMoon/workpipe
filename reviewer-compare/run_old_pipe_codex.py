#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RUNTIME_ROOT = ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from core.prompt_builder import UNIFIED_REVIEWER_SYSTEM, build_unified_review_prompt
from models.jd import JDProfile


DEFAULT_CASES_FILE = HERE / "cases.json"
DEFAULT_OUTPUT_ROOT = HERE / "old-pipe-codex" / "runs"
DEFAULT_CODEX_MODEL = "gpt-5.4-mini"
DEFAULT_REASONING_EFFORT = "medium"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def strip_json_trailing_commas(text: str) -> str:
    out: list[str] = []
    in_string = False
    escape = False
    i = 0
    while i < len(text):
        ch = text[i]
        if in_string:
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue
        if ch == ",":
            j = i + 1
            while j < len(text) and text[j].isspace():
                j += 1
            if j < len(text) and text[j] in "}]":
                i += 1
                continue
        out.append(ch)
        i += 1
    return "".join(out)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "case"


def extract_json_block(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model output")
    candidate = stripped[start : end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return json.loads(strip_json_trailing_commas(candidate))


def get_codex_bin() -> str:
    codex = shutil.which("codex")
    if not codex:
        raise FileNotFoundError("codex CLI not found")
    return codex


def run_codex(prompt: str, *, model: str, reasoning_effort: str, exec_root: Path) -> str:
    codex_bin = get_codex_bin()
    exec_root.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix="old-pipe-codex-", suffix=".txt", dir="/tmp", delete=False) as tmp:
        output_path = tmp.name
    cmd = [
        codex_bin,
        "exec",
        "--ephemeral",
        "--skip-git-repo-check",
        "-C",
        str(exec_root),
        "-o",
        output_path,
        "-m",
        model,
        "-c",
        f'model_reasoning_effort="{reasoning_effort}"',
    ]
    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            text=True,
            capture_output=True,
            env=os.environ.copy(),
        )
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout or "").strip() or f"codex exited {result.returncode}")
        text = Path(output_path).read_text(encoding="utf-8").strip()
        if not text:
            raise RuntimeError("codex produced no final output file")
        return text
    finally:
        try:
            os.remove(output_path)
        except OSError:
            pass


def load_cases(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_case(case: dict[str, Any]) -> tuple[dict[str, Any], str, str, str]:
    target_dir = (ROOT / case["target_dir"]).resolve()
    resume_path = target_dir / "resume.md"
    job_path = target_dir / "job.md"
    manifest_path = target_dir / "manifest.json"

    resume_md = read_text(resume_path)
    job_md = read_text(job_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    jd = JDProfile.from_text(
        job_md,
        jd_id=str(manifest.get("job_id", "") or ""),
        company=str(manifest.get("company_name", "") or ""),
    )
    user_prompt = build_unified_review_prompt(resume_md, jd, review_scope="full")
    system_prompt = UNIFIED_REVIEWER_SYSTEM.strip()
    combined_prompt = (
        "以下内容按 system 与 user 两部分提供，请严格同时遵守。\n\n"
        "[SYSTEM]\n"
        f"{system_prompt}\n\n"
        "[USER]\n"
        f"{user_prompt.strip()}\n"
    )
    metadata = {
        "label": case["label"],
        "target_dir": case["target_dir"],
        "company": jd.company,
        "title": jd.title,
        "historical": case.get("historical", {}),
        "resume_path": str(resume_path),
        "job_path": str(job_path),
        "manifest_path": str(manifest_path),
    }
    return metadata, system_prompt, user_prompt, combined_prompt


def summarize_case(payload: dict[str, Any]) -> dict[str, Any]:
    scores = payload.get("scores", {}) or {}
    dim_summary: dict[str, Any] = {}
    for dim_id, dim in scores.items():
        findings = dim.get("findings", []) or []
        dim_summary[dim_id] = {
            "score": dim.get("score"),
            "verdict": dim.get("verdict"),
            "findings_count": len(findings),
            "top_findings": findings[:2],
        }
    return {
        "weighted_score": payload.get("weighted_score"),
        "overall_verdict": payload.get("overall_verdict"),
        "critical_count": payload.get("critical_count"),
        "high_count": payload.get("high_count"),
        "needs_revision": payload.get("needs_revision"),
        "revision_priority": payload.get("revision_priority", []) or [],
        "dimensions": dim_summary,
    }


def duration_seconds(started_at: str, completed_at: str) -> float:
    start = datetime.fromisoformat(started_at)
    end = datetime.fromisoformat(completed_at)
    return round((end - start).total_seconds(), 1)


def build_report(cases: list[dict[str, Any]], run_dir: Path) -> str:
    lines = [
        "# 旧 Reviewer Pipe 在 Codex 模式下的结果",
        "",
        f"生成时间: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "| Case | 分数 | 结论 | 耗时(秒) | Critical | High |",
        "| --- | ---: | --- | ---: | ---: | ---: |",
    ]
    for case in cases:
        result = case["result"]
        lines.append(
            f"| {case['label']} | {result['weighted_score']:.1f} | {result['overall_verdict']} | "
            f"{result['duration_seconds']:.1f} | {result['critical_count']} | {result['high_count']} |"
        )
    for case in cases:
        result = case["result"]
        lines.extend(
            [
                "",
                f"## {case['label']}",
                "",
                f"- 目标岗位: {case['metadata']['title']} @ {case['metadata']['company']}",
                f"- 综合分: {result['weighted_score']:.1f} / {result['overall_verdict']}",
                f"- 耗时: {result['duration_seconds']:.1f} 秒",
                f"- Critical: {result['critical_count']} / High: {result['high_count']}",
                "",
                "### 优先修改项",
            ]
        )
        for item in result.get("revision_priority", []):
            lines.append(f"- {item}")
        lines.extend(["", "### 维度摘要"])
        for dim_id, dim in result["summary"]["dimensions"].items():
            lines.append(
                f"- {dim_id}: {dim['score']} ({dim['verdict']}), findings={dim['findings_count']}"
            )
        lines.extend(
            [
                "",
                "### 产物",
                f"- system: `{run_dir / slugify(case['label']) / 'system.txt'}`",
                f"- user prompt: `{run_dir / slugify(case['label']) / 'prompt.txt'}`",
                f"- 合并 prompt: `{run_dir / slugify(case['label']) / 'combined_prompt.txt'}`",
                f"- 原始输出: `{run_dir / slugify(case['label']) / 'codex.raw.txt'}`",
                f"- JSON: `{run_dir / slugify(case['label']) / 'codex.json'}`",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the old reviewer pipe prompts through Codex CLI.")
    parser.add_argument("--cases-file", default=str(DEFAULT_CASES_FILE))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--label", action="append", default=[])
    parser.add_argument("--codex-model", default=DEFAULT_CODEX_MODEL)
    parser.add_argument("--reasoning-effort", default=DEFAULT_REASONING_EFFORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    labels = set(args.label or [])
    cases = load_cases(Path(args.cases_file))
    if labels:
        cases = [case for case in cases if case["label"] in labels]
    if not cases:
        raise SystemExit("No cases selected")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    run_dir = Path(args.output_root).resolve() / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    report_cases: list[dict[str, Any]] = []
    for case in cases:
        case_dir = run_dir / slugify(case["label"])
        case_dir.mkdir(parents=True, exist_ok=True)
        metadata, system_prompt, user_prompt, combined_prompt = build_case(case)
        write_json(case_dir / "metadata.json", metadata)
        write_text(case_dir / "system.txt", system_prompt + "\n")
        write_text(case_dir / "prompt.txt", user_prompt)
        write_text(case_dir / "combined_prompt.txt", combined_prompt)

        started_at = datetime.now().isoformat(timespec="seconds")
        raw_text = run_codex(
            combined_prompt,
            model=args.codex_model,
            reasoning_effort=args.reasoning_effort,
            exec_root=Path("/tmp/reviewer-compare-old-codex"),
        )
        completed_at = datetime.now().isoformat(timespec="seconds")
        write_text(case_dir / "codex.raw.txt", raw_text + "\n")
        payload = extract_json_block(raw_text)
        result = {
            "runner": "codex",
            "model": args.codex_model,
            "started_at": started_at,
            "completed_at": completed_at,
            "duration_seconds": duration_seconds(started_at, completed_at),
            **payload,
            "summary": summarize_case(payload),
        }
        write_json(case_dir / "codex.json", result)
        report_cases.append(
            {
                "label": case["label"],
                "metadata": metadata,
                "result": result,
            }
        )

    write_text(run_dir / "report.md", build_report(report_cases, run_dir))
    write_text(HERE / "latest_old_pipe_codex_run.txt", str(run_dir) + "\n")
    print(str(run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
