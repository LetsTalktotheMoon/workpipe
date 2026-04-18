#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RUNTIME_ROOT = ROOT / "runtime"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from Reviewer_Cal import aggregate
from config.candidate_framework import experience_framework_for_company
from core.prompt_builder import (
    UNIFIED_REVIEWER_SYSTEM,
    _review_immutable_block,
    build_unified_review_prompt,
)
from models.jd import JDProfile


DEFAULT_CASES_FILE = HERE / "cases.json"
DEFAULT_OUTPUT_ROOT = HERE / "runs"
DEFAULT_CODEX_MODEL = "gpt-5.4-mini"
DEFAULT_CLAUDE_MODEL = "claude-sonnet-4-6"
DEFAULT_REASONING_EFFORT = "medium"
DEFAULT_TIMEOUT = 900

CLAUDE_PATTERN = os.path.expanduser(
    "~/Library/Application Support/Claude/claude-code/*/claude.app/Contents/MacOS/claude"
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "case"


def load_cases(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def get_claude_bin() -> str:
    in_path = shutil.which("claude")
    if in_path:
        return in_path
    matches = sorted(
        Path(os.path.expanduser("~/Library/Application Support/Claude/claude-code")).glob(
            "*/claude.app/Contents/MacOS/claude"
        )
    )
    if matches:
        return str(matches[-1])
    raise FileNotFoundError("Claude CLI not found")


def get_codex_bin() -> str:
    codex = shutil.which("codex")
    if not codex:
        raise FileNotFoundError("codex CLI not found")
    return codex


def normalize_field(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def build_candidate_snapshot(company: str) -> list[dict[str, str]]:
    snapshot: list[dict[str, str]] = []
    for item in experience_framework_for_company(company):
        snapshot.append(
            {
                "company": normalize_field(item["company"]),
                "department": normalize_field(item["department"]),
                "title": normalize_field(item["title"]),
                "dates": normalize_field(item["dates"]),
                "location": normalize_field(item["location"]),
            }
        )
    return snapshot


def build_prompt(template: str, *, resume_md: str, job_md: str, jd: JDProfile) -> str:
    replacements = {
        "{company}": jd.company or "Unknown",
        "{title}": jd.title or "Unknown",
        "{role_type}": jd.role_type or "unknown",
        "{seniority}": jd.seniority or "unknown",
        "{tech_required}": ", ".join(jd.tech_required) if jd.tech_required else "（无）",
        "{tech_preferred}": ", ".join(jd.tech_preferred) if jd.tech_preferred else "（无）",
        "{team_direction}": jd.team_direction or "（未说明）",
        "{job_content}": job_md.strip(),
        "{immutable_block}": _review_immutable_block(jd.company),
        "{resume_content}": resume_md.strip(),
    }
    prompt = template
    for needle, value in replacements.items():
        prompt = prompt.replace(needle, value)
    return prompt


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


def normalize_reviewer_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    if "pass_4_localization" in normalized and "pass_5_localization" not in normalized:
        normalized["pass_5_localization"] = normalized.pop("pass_4_localization")

    for key in (
        "pass_1_structural",
        "pass_2_attention",
        "pass_3_substance",
        "pass_5_localization",
    ):
        section = dict(normalized.get(key) or {})
        findings = section.get("findings")
        section["findings"] = findings if isinstance(findings, list) else []
        normalized[key] = section

    for key in ("translation_recommendations", "revision_priority"):
        value = normalized.get(key)
        normalized[key] = value if isinstance(value, list) else []
    normalized["revision_instructions"] = str(normalized.get("revision_instructions", "") or "")
    return normalized


def summarize_findings(payload: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "by_section": {},
        "all_rule_ids": [],
        "high_or_critical": [],
    }
    all_rule_ids: list[str] = []
    high_or_critical: list[str] = []
    for section in (
        "pass_1_structural",
        "pass_2_attention",
        "pass_3_substance",
        "pass_5_localization",
    ):
        findings = list((payload.get(section) or {}).get("findings") or [])
        rules = [str(item.get("rule_id", "") or "") for item in findings if item.get("rule_id")]
        summary["by_section"][section] = {
            "count": len(findings),
            "rule_ids": rules,
        }
        all_rule_ids.extend(rules)
        for item in findings:
            severity = str(item.get("severity", "") or "")
            if severity in {"critical", "high"}:
                rule_id = str(item.get("rule_id", "") or "")
                field = str(item.get("field", "") or "")
                high_or_critical.append(f"{rule_id} @ {field}".strip())
    summary["all_rule_ids"] = sorted(dict.fromkeys(all_rule_ids))
    summary["high_or_critical"] = high_or_critical
    return summary


def score_delta_trend(old_gap: float | None, new_gap: float | None, *, tolerance: float = 0.1) -> str:
    if old_gap is None or new_gap is None:
        return "unknown"
    delta = new_gap - old_gap
    if abs(delta) <= tolerance:
        return "unchanged"
    return "larger" if delta > 0 else "smaller"


def direction(new_score: float | None, old_score: float | None, *, tolerance: float = 0.1) -> str:
    if new_score is None or old_score is None:
        return "unknown"
    delta = new_score - old_score
    if abs(delta) <= tolerance:
        return "unchanged"
    return "higher" if delta > 0 else "lower"


def fmt_score(value: float | None) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "?"
    return f"{value:.1f}"


def timeout_or_none(timeout: int) -> int | None:
    return None if timeout <= 0 else timeout


def run_codex(prompt: str, *, model: str, reasoning_effort: str, timeout: int, exec_root: Path) -> str:
    codex_bin = get_codex_bin()
    exec_root.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix="reviewer-compare-codex-", suffix=".txt", dir="/tmp", delete=False) as tmp:
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
                timeout=timeout_or_none(timeout),
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


def run_claude(prompt: str, *, model: str, timeout: int) -> str:
    claude_bin = get_claude_bin()
    cmd = [
        claude_bin,
        "-p",
        "--model",
        model,
        "--output-format",
        "text",
        "--tools",
        "",
    ]
    result = subprocess.run(
        cmd,
        input=prompt,
        text=True,
        capture_output=True,
        timeout=timeout_or_none(timeout),
        env=os.environ.copy(),
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "").strip() or f"claude exited {result.returncode}")
    text = (result.stdout or "").strip()
    if not text:
        raise RuntimeError("claude produced no stdout")
    return text


def run_one_model(
    *,
    model_key: str,
    prompt: str,
    output_dir: Path,
    codex_model: str,
    claude_model: str,
    reasoning_effort: str,
    timeout: int,
) -> dict[str, Any]:
    started_at = datetime.now().isoformat(timespec="seconds")
    if model_key == "codex":
        raw_text = run_codex(
            prompt,
            model=codex_model,
            reasoning_effort=reasoning_effort,
            timeout=timeout,
            exec_root=Path("/tmp/reviewer-compare-codex"),
        )
        model_name = codex_model
    elif model_key == "claude":
        raw_text = run_claude(prompt, model=claude_model, timeout=timeout)
        model_name = claude_model
    else:
        raise ValueError(f"Unknown model key: {model_key}")

    write_text(output_dir / f"{model_key}.raw.txt", raw_text + "\n")
    raw_json = normalize_reviewer_payload(extract_json_block(raw_text))
    aggregated = asdict(aggregate(raw_json))
    payload = {
        "runner": model_key,
        "model": model_name,
        "started_at": started_at,
        "completed_at": datetime.now().isoformat(timespec="seconds"),
        "raw_json": raw_json,
        "aggregated": aggregated,
        "finding_summary": summarize_findings(raw_json),
    }
    write_json(output_dir / f"{model_key}.json", payload)
    return payload


def build_case_record(case: dict[str, Any], case_dir: Path, template: str) -> tuple[dict[str, Any], str]:
    target_dir = (ROOT / case["target_dir"]).resolve()
    resume_path = target_dir / "resume.md"
    job_path = target_dir / "job.md"
    manifest_path = target_dir / "manifest.json"
    review_path = target_dir / "review.json"

    resume_md = read_text(resume_path)
    job_md = read_text(job_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    portfolio_review = json.loads(review_path.read_text(encoding="utf-8")) if review_path.exists() else {}

    jd = JDProfile.from_text(
        job_md,
        jd_id=str(manifest.get("job_id", "") or ""),
        company=str(manifest.get("company_name", "") or case.get("company", "") or ""),
    )
    prompt = build_prompt(template, resume_md=resume_md, job_md=job_md, jd=jd)
    original_prompt = build_unified_review_prompt(resume_md, jd, review_scope="full")

    metadata = {
        "label": case["label"],
        "company": jd.company,
        "title": jd.title,
        "role_type": jd.role_type,
        "seniority": jd.seniority,
        "team_direction": jd.team_direction,
        "tech_required": jd.tech_required,
        "tech_preferred": jd.tech_preferred,
        "resume_path": str(resume_path),
        "job_path": str(job_path),
        "manifest_path": str(manifest_path),
        "review_path": str(review_path),
        "historical": case.get("historical", {}),
        "portfolio_review": portfolio_review,
        "immutable_snapshot": build_candidate_snapshot(jd.company),
    }
    write_json(case_dir / "metadata.json", metadata)
    write_text(case_dir / "prompt.txt", prompt)
    write_text(case_dir / "original_reviewer_prompt.txt", original_prompt)
    write_text(case_dir / "original_reviewer_system.txt", UNIFIED_REVIEWER_SYSTEM.strip() + "\n")
    return metadata, prompt


def build_summary(cases: list[dict[str, Any]]) -> dict[str, Any]:
    summary_cases: list[dict[str, Any]] = []
    for case in cases:
        historical = case["historical"]
        codex = case.get("codex")
        claude = case.get("claude")
        old_gap = None
        if historical.get("official_score") is not None and historical.get("claude_score") is not None:
            old_gap = round(abs(float(historical["official_score"]) - float(historical["claude_score"])), 1)
        new_gap = None
        if codex and codex.get("aggregated") and claude and claude.get("aggregated"):
            new_gap = round(abs(float(codex["aggregated"]["weighted_score"]) - float(claude["aggregated"]["weighted_score"])), 1)
        summary_cases.append(
            {
                "label": case["label"],
                "old_official_score": historical.get("official_score"),
                "old_claude_score": historical.get("claude_score"),
                "new_codex_score": codex["aggregated"]["weighted_score"] if codex and codex.get("aggregated") else None,
                "new_claude_score": claude["aggregated"]["weighted_score"] if claude and claude.get("aggregated") else None,
                "old_gap": old_gap,
                "new_gap": new_gap,
                "gap_trend": score_delta_trend(old_gap, new_gap),
                "codex_direction": direction(
                    codex["aggregated"]["weighted_score"] if codex and codex.get("aggregated") else None,
                    historical.get("official_score"),
                ),
                "claude_direction": direction(
                    claude["aggregated"]["weighted_score"] if claude and claude.get("aggregated") else None,
                    historical.get("claude_score"),
                ),
                "codex_error": codex.get("error", "") if codex else "",
                "claude_error": claude.get("error", "") if claude else "",
            }
        )
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "case_count": len(summary_cases),
        "cases": summary_cases,
    }


def build_markdown(run_dir: Path, cases: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    lines = [
        "# Reviewer 对比",
        "",
        f"生成时间: {summary['generated_at']}",
        "",
        "| Case | 旧 Official | 旧 Claude | 旧分差 | 新 Codex | 新 Claude | 新分差 | 分差变化 | Codex 对旧分数 | Claude 对旧分数 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for item in summary["cases"]:
        lines.append(
            f"| {item['label']} | {fmt_score(item['old_official_score'])} | {fmt_score(item['old_claude_score'])} | "
            f"{fmt_score(item['old_gap'])} | {fmt_score(item['new_codex_score'])} | {fmt_score(item['new_claude_score'])} | "
            f"{fmt_score(item['new_gap'])} | {item['gap_trend']} | {item['codex_direction']} | {item['claude_direction']} |"
        )

    for case in cases:
        historical = case["historical"]
        codex = case.get("codex")
        claude = case.get("claude")
        lines.extend(
            [
                "",
                f"## {case['label']}",
                "",
                f"- 目标岗位: {case['metadata']['title']} @ {case['metadata']['company']}",
                f"- 目标目录: `{case['target_dir']}`",
                f"- 旧 official 分数/结论: {fmt_score(historical.get('official_score'))} / {historical.get('official_verdict', '?')}",
                f"- 旧 Claude 分数/结论: {fmt_score(historical.get('claude_score'))} / {historical.get('claude_verdict', '?')}",
                (
                    f"- 新 Codex 分数/结论: {fmt_score(codex['aggregated']['weighted_score'])} / {codex['aggregated']['overall_verdict']}"
                    if codex and codex.get("aggregated")
                    else f"- 新 Codex 错误: {codex.get('error', 'not run')}" if codex else "- 新 Codex: 未运行"
                ),
                (
                    f"- 新 Claude 分数/结论: {fmt_score(claude['aggregated']['weighted_score'])} / {claude['aggregated']['overall_verdict']}"
                    if claude and claude.get("aggregated")
                    else f"- 新 Claude 错误: {claude.get('error', 'not run')}" if claude else "- 新 Claude: 未运行"
                ),
                "",
                "### 历史基线",
            ]
        )
        for note in historical.get("official_notes", []):
            lines.append(f"- Official: {note}")
        for note in historical.get("claude_notes", []):
            lines.append(f"- Claude: {note}")
        if codex and codex.get("aggregated"):
            lines.extend(
                [
                    "",
                    "### 新 Codex 输出",
                    f"- High/Critical 数量: {len(codex['aggregated']['reviewer_raw']['pass_1_structural']['findings']) + len(codex['aggregated']['reviewer_raw']['pass_2_attention']['findings']) + len(codex['aggregated']['reviewer_raw']['pass_3_substance']['findings']) + len(codex['aggregated']['reviewer_raw']['pass_5_localization']['findings'])}",
                    f"- 严重度计数: critical={codex['aggregated']['critical_count']}, high={codex['aggregated']['high_count']}, medium={codex['aggregated']['medium_count']}, low={codex['aggregated']['low_count']}",
                    f"- 规则 ID: {', '.join(codex['finding_summary']['all_rule_ids']) or 'none'}",
                ]
            )
            for item in codex["aggregated"]["revision_priority"]:
                lines.append(f"- 优先项: {item}")
        elif codex and codex.get("error"):
            lines.extend(["", "### 新 Codex 输出", f"- 错误: {codex['error']}"])
        if claude and claude.get("aggregated"):
            lines.extend(
                [
                    "",
                    "### 新 Claude 输出",
                    f"- 严重度计数: critical={claude['aggregated']['critical_count']}, high={claude['aggregated']['high_count']}, medium={claude['aggregated']['medium_count']}, low={claude['aggregated']['low_count']}",
                    f"- 规则 ID: {', '.join(claude['finding_summary']['all_rule_ids']) or 'none'}",
                ]
            )
            for item in claude["aggregated"]["revision_priority"]:
                lines.append(f"- 优先项: {item}")
        elif claude and claude.get("error"):
            lines.extend(["", "### 新 Claude 输出", f"- 错误: {claude['error']}"])
        lines.extend(
            [
                "",
                "### 产物",
                f"- Prompt: `{run_dir / slugify(case['label']) / 'prompt.txt'}`",
                f"- 原 reviewer prompt: `{run_dir / slugify(case['label']) / 'original_reviewer_prompt.txt'}`",
                f"- 原 reviewer system: `{run_dir / slugify(case['label']) / 'original_reviewer_system.txt'}`",
                f"- Metadata: `{run_dir / slugify(case['label']) / 'metadata.json'}`",
                f"- Codex JSON: `{run_dir / slugify(case['label']) / 'codex.json'}`",
                f"- Claude JSON: `{run_dir / slugify(case['label']) / 'claude.json'}`",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Reviewer_4Stage via Codex CLI and Claude CLI, then compare against historical baselines.")
    parser.add_argument("--cases-file", default=str(DEFAULT_CASES_FILE))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--label", action="append", default=[], help="Only run matching case label(s). Repeatable.")
    parser.add_argument("--codex-model", default=DEFAULT_CODEX_MODEL)
    parser.add_argument("--claude-model", default=DEFAULT_CLAUDE_MODEL)
    parser.add_argument("--reasoning-effort", default=DEFAULT_REASONING_EFFORT)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--skip-codex", action="store_true")
    parser.add_argument("--skip-claude", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cases = load_cases(Path(args.cases_file).resolve())
    if args.label:
        allowed = {item.strip() for item in args.label if item.strip()}
        cases = [case for case in cases if case["label"] in allowed]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    run_dir = Path(args.output_root).resolve() / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    template = read_text(HERE / "Reviewer_4Stage.md")
    run_cases: list[dict[str, Any]] = []

    for case in cases:
        case_dir = run_dir / slugify(case["label"])
        case_dir.mkdir(parents=True, exist_ok=True)
        metadata, prompt = build_case_record(case, case_dir, template)
        case_record: dict[str, Any] = {
            "label": case["label"],
            "target_dir": case["target_dir"],
            "metadata": metadata,
            "historical": case["historical"],
        }
        if not args.skip_codex:
            try:
                case_record["codex"] = run_one_model(
                    model_key="codex",
                    prompt=prompt,
                    output_dir=case_dir,
                    codex_model=args.codex_model,
                    claude_model=args.claude_model,
                    reasoning_effort=args.reasoning_effort,
                    timeout=args.timeout,
                )
            except Exception as exc:
                case_record["codex"] = {
                    "runner": "codex",
                    "model": args.codex_model,
                    "error": str(exc),
                }
        if not args.skip_claude:
            try:
                case_record["claude"] = run_one_model(
                    model_key="claude",
                    prompt=prompt,
                    output_dir=case_dir,
                    codex_model=args.codex_model,
                    claude_model=args.claude_model,
                    reasoning_effort=args.reasoning_effort,
                    timeout=args.timeout,
                )
            except Exception as exc:
                case_record["claude"] = {
                    "runner": "claude",
                    "model": args.claude_model,
                    "error": str(exc),
                }
        write_json(case_dir / "case_summary.json", case_record)
        run_cases.append(case_record)

    summary = build_summary(run_cases)
    write_json(run_dir / "summary.json", summary)
    write_text(run_dir / "report.md", build_markdown(run_dir, run_cases, summary))
    write_text(HERE / "latest_run.txt", str(run_dir) + "\n")
    print(str(run_dir))


if __name__ == "__main__":
    main()
