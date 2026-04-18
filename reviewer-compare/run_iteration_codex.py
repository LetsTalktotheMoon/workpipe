#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
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

from config.candidate_framework import experience_framework_for_company
from core.prompt_builder import _review_immutable_block
from models.jd import JDProfile


DEFAULT_CASES_FILE = HERE / "cases_extended_10.json"
DEFAULT_OUTPUT_ROOT = HERE / "iteration-runs"
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


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "case"


def load_cases(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def fmt_score(value: float | None) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "?"
    return f"{value:.1f}"


def run_codex(prompt: str, *, model: str, reasoning_effort: str, exec_root: Path) -> str:
    codex_bin = get_codex_bin()
    exec_root.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix="reviewer-iteration-codex-", suffix=".txt", dir="/tmp", delete=False) as tmp:
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


def load_aggregate_fn(path: Path):
    spec = importlib.util.spec_from_file_location(f"iter_scorer_{slugify(path.stem)}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load scorer module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    aggregate = getattr(module, "aggregate", None)
    if aggregate is None:
        raise AttributeError(f"aggregate() not found in {path}")
    return aggregate


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
    return metadata, prompt


def build_summary(cases: list[dict[str, Any]]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for case in cases:
        codex = case["codex"]
        aggregated = codex["aggregated"]
        items.append(
            {
                "label": case["label"],
                "score": aggregated["weighted_score"],
                "verdict": aggregated["overall_verdict"],
                "critical_count": aggregated["critical_count"],
                "high_count": aggregated["high_count"],
                "medium_count": aggregated["medium_count"],
                "low_count": aggregated["low_count"],
                "duration_seconds": codex["duration_seconds"],
                "top_rules": codex["finding_summary"]["all_rule_ids"][:8],
            }
        )
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "case_count": len(items),
        "cases": items,
    }


def build_markdown(run_dir: Path, version_label: str, cases: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    lines = [
        f"# {version_label} 结果",
        "",
        f"生成时间: {summary['generated_at']}",
        "",
        "| Case | 分数 | 结论 | 耗时(秒) | Critical | High | Medium | 主要规则 |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in summary["cases"]:
        lines.append(
            f"| {item['label']} | {fmt_score(item['score'])} | {item['verdict']} | {item['duration_seconds']:.1f} | "
            f"{item['critical_count']} | {item['high_count']} | {item['medium_count']} | {', '.join(item['top_rules']) or 'none'} |"
        )

    for case in cases:
        codex = case["codex"]
        aggregated = codex["aggregated"]
        lines.extend(
            [
                "",
                f"## {case['label']}",
                "",
                f"- 目标岗位: {case['metadata']['title']} @ {case['metadata']['company']}",
                f"- 分数/结论: {fmt_score(aggregated['weighted_score'])} / {aggregated['overall_verdict']}",
                f"- 耗时: {codex['duration_seconds']:.1f} 秒",
                f"- 严重度计数: critical={aggregated['critical_count']}, high={aggregated['high_count']}, medium={aggregated['medium_count']}, low={aggregated['low_count']}",
                f"- 规则 ID: {', '.join(codex['finding_summary']['all_rule_ids']) or 'none'}",
                "",
                "### 优先修改项",
            ]
        )
        for item in aggregated["revision_priority"]:
            lines.append(f"- {item}")
        lines.extend(
            [
                "",
                "### 产物",
                f"- Prompt: `{run_dir / slugify(case['label']) / 'prompt.txt'}`",
                f"- Metadata: `{run_dir / slugify(case['label']) / 'metadata.json'}`",
                f"- 原始输出: `{run_dir / slugify(case['label']) / 'codex.raw.txt'}`",
                f"- JSON: `{run_dir / slugify(case['label']) / 'codex.json'}`",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a specific reviewer prompt + scorer version through Codex on the 10-case benchmark.")
    parser.add_argument("--cases-file", default=str(DEFAULT_CASES_FILE))
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--scorer-file", required=True)
    parser.add_argument("--version-label", required=True)
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--label", action="append", default=[])
    parser.add_argument("--codex-model", default=DEFAULT_CODEX_MODEL)
    parser.add_argument("--reasoning-effort", default=DEFAULT_REASONING_EFFORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cases = load_cases(Path(args.cases_file))
    labels = set(args.label or [])
    if labels:
        cases = [case for case in cases if case["label"] in labels]
    if not cases:
        raise SystemExit("No cases selected")

    prompt_path = Path(args.prompt_file).resolve()
    scorer_path = Path(args.scorer_file).resolve()
    template = read_text(prompt_path)
    aggregate = load_aggregate_fn(scorer_path)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    run_dir = Path(args.output_root).resolve() / f"{slugify(args.version_label)}_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    write_text(run_dir / "Reviewer_4Stage.md", template)
    write_text(run_dir / "Reviewer_Cal.py", read_text(scorer_path))
    write_json(
        run_dir / "version.json",
        {
            "version_label": args.version_label,
            "prompt_file": str(prompt_path),
            "scorer_file": str(scorer_path),
            "cases_file": str(Path(args.cases_file).resolve()),
            "codex_model": args.codex_model,
            "reasoning_effort": args.reasoning_effort,
            "started_at": datetime.now().isoformat(timespec="seconds"),
        },
    )

    run_cases: list[dict[str, Any]] = []
    for case in cases:
        case_dir = run_dir / slugify(case["label"])
        case_dir.mkdir(parents=True, exist_ok=True)
        metadata, prompt = build_case_record(case, case_dir, template)
        started_at = datetime.now().isoformat(timespec="seconds")
        raw_text = run_codex(
            prompt,
            model=args.codex_model,
            reasoning_effort=args.reasoning_effort,
            exec_root=Path("/tmp/reviewer-compare-iteration-codex"),
        )
        completed_at = datetime.now().isoformat(timespec="seconds")
        write_text(case_dir / "codex.raw.txt", raw_text + "\n")
        raw_json = normalize_reviewer_payload(extract_json_block(raw_text))
        aggregated = asdict(aggregate(raw_json))
        duration_seconds = round(
            (datetime.fromisoformat(completed_at) - datetime.fromisoformat(started_at)).total_seconds(),
            1,
        )
        payload = {
            "runner": "codex",
            "model": args.codex_model,
            "started_at": started_at,
            "completed_at": completed_at,
            "duration_seconds": duration_seconds,
            "raw_json": raw_json,
            "aggregated": aggregated,
            "finding_summary": summarize_findings(raw_json),
        }
        write_json(case_dir / "codex.json", payload)
        case_record = {
            "label": case["label"],
            "target_dir": case["target_dir"],
            "historical": case.get("historical", {}),
            "metadata": metadata,
            "codex": payload,
        }
        write_json(case_dir / "case_summary.json", case_record)
        run_cases.append(case_record)

    summary = build_summary(run_cases)
    write_json(run_dir / "summary.json", summary)
    write_text(run_dir / "report.md", build_markdown(run_dir, args.version_label, run_cases, summary))
    write_text(HERE / "latest_iteration_run.txt", str(run_dir) + "\n")
    print(str(run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
