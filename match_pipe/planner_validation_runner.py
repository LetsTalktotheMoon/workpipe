#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from core.anthropic_client import LLMUnavailableError, configure_llm_client, get_llm_client
from core.prompt_builder import (
    MASTER_WRITER_SYSTEM,
    build_master_writer_prompt,
    build_unified_review_prompt,
)
from models.jd import JDProfile
from pipeline.revision_acceptance import should_adopt_revision
from reviewers.unified_reviewer import UNIFIED_REVIEWER_SYSTEM, UnifiedReviewer
from writers.master_writer import MasterWriter

from .loader import load_job_documents
from .starter_selector import StarterSelector


PLANNER_SYSTEM = """你是简历流程里的 Planner。你的职责不是直接写简历，而是基于 JD、matcher 证据和可选历史简历 starter，判断：
1. 这份 starter 是否适合作为起点；
2. 是否可以直接送 Reviewer；
3. 如果需要写作，哪些内容已覆盖、哪些缺失、哪些存在真实性/ownership/scope 风险；
4. Writer 应如何改写，优先级如何排序。

必须输出 JSON，不要输出解释性文字。不要复述 schema。"""


def _estimate_tokens(text: str) -> int:
    stripped = str(text or "")
    if not stripped:
        return 0
    return max(1, math.ceil(len(stripped) / 4))


def _serialize_review(review) -> dict[str, Any]:
    return {
        "weighted_score": review.weighted_score,
        "passed": review.passed,
        "critical_count": review.critical_count,
        "high_count": review.high_count,
        "needs_revision": review.needs_revision,
        "revision_priority": review.revision_priority,
        "revision_instructions": review.revision_instructions,
    }


def _review_prompt_tokens(jd: JDProfile, resume_md: str, review_summary) -> tuple[int, int]:
    prompt = build_unified_review_prompt(resume_md, jd, review_scope="full")
    prompt_tokens = _estimate_tokens(UNIFIED_REVIEWER_SYSTEM) + _estimate_tokens(prompt)
    call_count = len(review_summary.calibration_scores) if review_summary.calibrated and review_summary.calibration_scores else 1
    output_tokens = _estimate_tokens(review_summary.raw_response) * call_count
    return prompt_tokens * call_count, output_tokens


def _existing_resume_anchor(candidates: list[dict | None]) -> dict | None:
    for candidate in candidates:
        if not candidate:
            continue
        resume_path = str(candidate.get("resume_path", "") or "")
        if resume_path and Path(resume_path).exists():
            return candidate
    return None


@dataclass
class FlowResult:
    mode: str
    planner_decision: str
    planner_fit_label: str
    planner_prompt_tokens_est: int
    planner_output_tokens_est: int
    writer_prompt_tokens_est: int
    writer_output_tokens_est: int
    reviewer_prompt_tokens_est: int
    reviewer_output_tokens_est: int
    total_tokens_est: int
    elapsed_seconds: float
    final_score: float
    passed: bool
    reviewer_rounds: int
    writer_rounds: int
    planner_payload: dict[str, Any]
    anchor_summary: dict[str, Any]
    final_review: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["elapsed_seconds"] = round(self.elapsed_seconds, 2)
        payload["final_score"] = round(self.final_score, 1)
        return payload


def _build_matcher_packet(selector_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "semantic_cluster_mode": selector_payload.get("semantic_cluster_mode"),
        "semantic_best_anchor": selector_payload.get("semantic_best_anchor"),
        "semantic_starter_anchor": selector_payload.get("semantic_starter_anchor"),
        "semantic_positive_cluster": selector_payload.get("semantic_positive_cluster"),
        "semantic_top_k": selector_payload.get("semantic_top_k"),
        "company_best_anchor": selector_payload.get("company_best_anchor"),
        "company_top_k": selector_payload.get("company_top_k"),
        "delta_summary": selector_payload.get("delta_summary"),
        "semantic_explanation": selector_payload.get("semantic_explanation"),
        "company_explanation": selector_payload.get("company_explanation"),
    }


def _planner_prompt(
    *,
    jd: JDProfile,
    mode: str,
    matcher_packet: dict[str, Any] | None = None,
    starter_resume_md: str = "",
) -> str:
    matcher_block = json.dumps(matcher_packet or {}, indent=2, ensure_ascii=False)
    starter_block = starter_resume_md if starter_resume_md else "（无 starter resume）"
    return f"""请作为 Planner，基于以下信息做流程决策。

目标模式: {mode}

目标 JD:
- 公司: {jd.company}
- 职位: {jd.title}
- role_type: {jd.role_type}
- seniority: {jd.seniority}
- must-have 技术: {jd.tech_required}
- preferred 技术: {jd.tech_preferred}

Matcher Packet:
```json
{matcher_block}
```

Starter Resume:
```md
{starter_block}
```

返回 JSON，schema 必须包含：
{{
  "decision": "write" | "direct_review" | "reject_starter",
  "fit_label": "high" | "medium" | "low",
  "reuse_ratio_estimate": 0.0,
  "already_covered": ["..."],
  "missing_or_weak": ["..."],
  "risk_flags": ["..."],
  "role_seniority_guidance": ["..."],
  "planner_summary": "...",
  "writer_plan": ["..."],
  "direct_review_rationale": "..."
}}

规则：
1. no_starter 模式下 decision 只能是 "write"。
2. 如果 starter 已经高度贴合且 scope/真实性风险低，可以 direct_review。
3. 如果 starter 语义相近但需要改写，选 write。
4. 如果 starter 虽相似但会明显误导 summary / ownership / 项目骨架 / scope，选 reject_starter。
5. 不要把 matcher 的相似度直接等同于可写作适配度。"""


def _plan_flow(
    *,
    jd: JDProfile,
    mode: str,
    matcher_packet: dict[str, Any] | None = None,
    starter_resume_md: str = "",
    cache_key_suffix: str,
    planner_model: str,
) -> tuple[dict[str, Any], int, int]:
    client = get_llm_client()
    prompt = _planner_prompt(jd=jd, mode=mode, matcher_packet=matcher_packet, starter_resume_md=starter_resume_md)
    payload = client.call_json(
        prompt,
        model=planner_model,
        cache_key=client.make_cache_key(jd.jd_id or "unknown", jd.company or "", jd.title or "", cache_key_suffix),
        system=PLANNER_SYSTEM,
    )
    return payload, _estimate_tokens(prompt) + _estimate_tokens(PLANNER_SYSTEM), _estimate_tokens(json.dumps(payload, ensure_ascii=False))


def _writer_prompt_from_planner(
    *,
    jd: JDProfile,
    planner_payload: dict[str, Any],
    starter_resume_md: str = "",
    matcher_packet: dict[str, Any] | None = None,
) -> str:
    base = build_master_writer_prompt(jd)
    planner_json = json.dumps(planner_payload, indent=2, ensure_ascii=False)
    matcher_json = json.dumps(matcher_packet or {}, indent=2, ensure_ascii=False)
    starter_block = starter_resume_md if starter_resume_md else "（无 starter resume）"
    return f"""{base}

## Planner Decision
```json
{planner_json}
```

## Matcher Evidence
```json
{matcher_json}
```

## Historical Starter Resume
```md
{starter_block}
```

## Planner-first Rules
- 如果给了 starter resume，把它视为可复用参考骨架，而不是必须保留的模板。
- 优先遵循 planner 对 coverage / missing / risk / role-seniority framing 的判断。
- 如果 planner 指出了 scope 或真实性风险，必须主动改写 summary、ownership 和项目 framing。
- 如果 planner 认为 starter 可高比例复用，可保留高价值证据，但仍以目标 JD 为准。
"""


def _writer_revision_prompt(current_resume_md: str, review, jd: JDProfile, planner_payload: dict[str, Any]) -> str:
    planner_notes = "\n".join(f"- {item}" for item in planner_payload.get("writer_plan", []))
    risk_notes = "\n".join(f"- {item}" for item in planner_payload.get("risk_flags", []))
    priority = "\n".join(f"{idx + 1}. {item}" for idx, item in enumerate(review.revision_priority or []))
    findings: list[str] = []
    for dim_id, dim in review.dimensions.items():
        for finding in dim.findings:
            if finding.get("severity") in {"critical", "high", "medium"}:
                findings.append(
                    f"[{dim_id}] [{str(finding.get('severity', '')).upper()}] "
                    f"{finding.get('field', '')}: {finding.get('issue', '')} -> {finding.get('fix', '')}"
                )
    findings_block = "\n".join(f"- {item}" for item in findings) or "- 无结构化高优先发现"
    must_have = ", ".join(jd.tech_required) if jd.tech_required else "（无明确 must-have）"
    return f"""{build_master_writer_prompt(jd)}

## Planner-first Revision Context
- 当前版本评分: {review.weighted_score:.1f}/100
- 当前是否通过: {"PASS" if review.passed else "FAIL"}
- 当前 reviewer 是否要求继续修改: {"是" if review.needs_revision else "否"}
- 当前目标不是保留旧稿，而是基于 reviewer 与 planner 的判断，把简历提升到更稳的 pass。

## Planner Carry-over
{planner_notes or "- 无额外 writer plan"}

## Planner Risks
{risk_notes or "- 无额外风险"}

## Reviewer Priority
{priority or "1. Raise the resume to a stronger pass."}

## Reviewer Findings
{findings_block}

## Must-have Tech
- {must_have}

## Existing Resume Draft To Revise
```md
{current_resume_md}
```

## Revision Rules
- 这是一次以目标 JD 为准的升级式改写任务。
- 不要保留任何只是因为旧稿已经存在、但不再服务目标 JD 的 summary framing、ownership framing 或 bullet 结构。
- 如果 planner 指出了 starter 的 scope、真实性、角色定位或 seniority 风险，必须优先修正。
- 如果 reviewer 指出了 JD 缺口，优先补正文证据，而不是删除 must-have 技术。
- 允许重写 summary、skills 分组、bullet 取舍、project baseline 和经历 framing，但不得破坏不可变字段与职业主线真实性。
- 输出完整简历 Markdown，不要解释。
"""


def _review_direct_or_written(
    *,
    writer: MasterWriter,
    reviewer: UnifiedReviewer,
    jd: JDProfile,
    planner_payload: dict[str, Any],
    initial_resume_md: str,
    planner_prompt_tokens: int,
    planner_output_tokens: int,
    writer_prompt_tokens: int,
    anchor_summary: dict[str, Any],
    started_at: float,
    writer_rounds: int,
) -> FlowResult:
    review = reviewer.review(initial_resume_md, jd, mode="full")
    reviewer_rounds = 1
    total_writer_prompt_tokens = writer_prompt_tokens
    total_writer_output_tokens = _estimate_tokens(initial_resume_md) if writer_rounds else 0
    current_resume_md = initial_resume_md

    while not review.passed and review.needs_revision and writer_rounds < 2:
        writer_rounds += 1
        revision_prompt = _writer_revision_prompt(current_resume_md, review, jd, planner_payload)
        revised_md = writer.revise(current_resume_md, revision_prompt, jd, rewrite_mode="upgrade")
        revised_review = reviewer.review(revised_md, jd, mode="full")
        reviewer_rounds += 1
        adopted = should_adopt_revision(
            score_before=review.weighted_score,
            critical_before=review.critical_count,
            high_before=review.high_count,
            score_after=revised_review.weighted_score,
            critical_after=revised_review.critical_count,
            high_after=revised_review.high_count,
            passed_after=revised_review.passed,
        )
        total_writer_prompt_tokens += _estimate_tokens(revision_prompt)
        total_writer_output_tokens += _estimate_tokens(revised_md)
        if not adopted:
            break
        current_resume_md = revised_md
        review = revised_review

    reviewer_prompt_tokens, reviewer_output_tokens = _review_prompt_tokens(jd, current_resume_md, review)
    return FlowResult(
        mode="",
        planner_decision=str(planner_payload.get("decision", "")),
        planner_fit_label=str(planner_payload.get("fit_label", "")),
        planner_prompt_tokens_est=planner_prompt_tokens,
        planner_output_tokens_est=planner_output_tokens,
        writer_prompt_tokens_est=total_writer_prompt_tokens,
        writer_output_tokens_est=total_writer_output_tokens,
        reviewer_prompt_tokens_est=reviewer_prompt_tokens,
        reviewer_output_tokens_est=reviewer_output_tokens,
        total_tokens_est=planner_prompt_tokens + planner_output_tokens + total_writer_prompt_tokens + total_writer_output_tokens + reviewer_prompt_tokens + reviewer_output_tokens,
        elapsed_seconds=time.perf_counter() - started_at,
        final_score=review.weighted_score,
        passed=review.passed,
        reviewer_rounds=reviewer_rounds,
        writer_rounds=writer_rounds,
        planner_payload=planner_payload,
        anchor_summary=anchor_summary,
        final_review=_serialize_review(review),
    )


def _run_no_starter_planner(
    writer: MasterWriter,
    reviewer: UnifiedReviewer,
    jd: JDProfile,
    *,
    planner_model: str,
) -> FlowResult:
    started = time.perf_counter()
    planner_payload, planner_prompt_tokens, planner_output_tokens = _plan_flow(
        jd=jd,
        mode="no_starter",
        cache_key_suffix="planner_no_starter_v1",
        planner_model=planner_model,
    )
    writer_prompt = _writer_prompt_from_planner(jd=jd, planner_payload=planner_payload)
    resume_md, _ = writer.write_from_prompt(
        writer_prompt,
        jd=jd,
        system_prompt=MASTER_WRITER_SYSTEM,
        cache_key_parts=(jd.jd_id or "unknown", jd.company or "", jd.role_type or "", "planner_no_starter_writer_v1"),
    )
    result = _review_direct_or_written(
        writer=writer,
        reviewer=reviewer,
        jd=jd,
        planner_payload=planner_payload,
        initial_resume_md=resume_md,
        planner_prompt_tokens=planner_prompt_tokens,
        planner_output_tokens=planner_output_tokens,
        writer_prompt_tokens=_estimate_tokens(writer_prompt),
        anchor_summary={"strategy": "planner_from_scratch"},
        started_at=started,
        writer_rounds=1,
    )
    result.mode = "no_starter_planner"
    return result


def _run_new_dual_channel_planner(
    writer: MasterWriter,
    reviewer: UnifiedReviewer,
    jd: JDProfile,
    *,
    selector_payload: dict[str, Any],
    planner_model: str,
) -> FlowResult:
    started = time.perf_counter()
    matcher_packet = _build_matcher_packet(selector_payload)
    primary_anchor = _existing_resume_anchor(
        [selector_payload.get("semantic_starter_anchor")]
        + [selector_payload["writer_input"].get("primary_anchor")]
        + list(selector_payload.get("semantic_positive_cluster", []))
        + list(selector_payload.get("semantic_top_k", []))
    )
    starter_resume_md = Path(primary_anchor["resume_path"]).read_text(encoding="utf-8") if primary_anchor else ""
    planner_payload, planner_prompt_tokens, planner_output_tokens = _plan_flow(
        jd=jd,
        mode="new_dual_channel",
        matcher_packet=matcher_packet,
        starter_resume_md=starter_resume_md,
        cache_key_suffix="planner_dual_channel_v1",
        planner_model=planner_model,
    )

    continuity_anchor = _existing_resume_anchor(
        [selector_payload["writer_input"].get("continuity_anchor")] + list(selector_payload.get("company_top_k", []))
    )
    anchor_summary = {
        "semantic_best_anchor": selector_payload.get("semantic_best_anchor"),
        "semantic_starter_anchor": selector_payload.get("semantic_starter_anchor"),
        "semantic_writer_anchor": primary_anchor,
        "company_best_anchor": selector_payload.get("company_best_anchor"),
        "continuity_anchor": continuity_anchor,
    }

    if planner_payload.get("decision") == "reject_starter":
        writer_prompt = _writer_prompt_from_planner(
            jd=jd,
            planner_payload=planner_payload,
            starter_resume_md="",
            matcher_packet=matcher_packet,
        )
        resume_md, _ = writer.write_from_prompt(
            writer_prompt,
            jd=jd,
            system_prompt=MASTER_WRITER_SYSTEM,
            cache_key_parts=(jd.jd_id or "unknown", jd.company or "", jd.role_type or "", "planner_dual_reject_writer_v1"),
        )
        result = _review_direct_or_written(
            writer=writer,
            reviewer=reviewer,
            jd=jd,
            planner_payload=planner_payload,
            initial_resume_md=resume_md,
            planner_prompt_tokens=planner_prompt_tokens,
            planner_output_tokens=planner_output_tokens,
            writer_prompt_tokens=_estimate_tokens(writer_prompt),
            anchor_summary=anchor_summary | {"planner_rejected_starter": True},
            started_at=started,
            writer_rounds=1,
        )
        result.mode = "new_dual_channel_planner"
        return result

    if planner_payload.get("decision") == "direct_review" and starter_resume_md:
        result = _review_direct_or_written(
            writer=writer,
            reviewer=reviewer,
            jd=jd,
            planner_payload=planner_payload,
            initial_resume_md=starter_resume_md,
            planner_prompt_tokens=planner_prompt_tokens,
            planner_output_tokens=planner_output_tokens,
            writer_prompt_tokens=0,
            anchor_summary=anchor_summary,
            started_at=started,
            writer_rounds=0,
        )
        result.mode = "new_dual_channel_planner"
        return result

    writer_prompt = _writer_prompt_from_planner(
        jd=jd,
        planner_payload=planner_payload,
        starter_resume_md=starter_resume_md,
        matcher_packet=matcher_packet,
    )
    resume_md, _ = writer.write_from_prompt(
        writer_prompt,
        jd=jd,
        system_prompt=MASTER_WRITER_SYSTEM,
        cache_key_parts=(jd.jd_id or "unknown", jd.company or "", jd.role_type or "", "planner_dual_writer_v1"),
    )
    result = _review_direct_or_written(
        writer=writer,
        reviewer=reviewer,
        jd=jd,
        planner_payload=planner_payload,
        initial_resume_md=resume_md,
        planner_prompt_tokens=planner_prompt_tokens,
        planner_output_tokens=planner_output_tokens,
        writer_prompt_tokens=_estimate_tokens(writer_prompt),
        anchor_summary=anchor_summary,
        started_at=started,
        writer_rounds=1,
    )
    result.mode = "new_dual_channel_planner"
    return result


def _historical_flow_from_old_report(job_id: str, mode: str, old_report: dict[str, Any]) -> dict[str, Any] | None:
    for item in old_report.get("results", []):
        if item.get("job_id") != job_id:
            continue
        for flow in item.get("flows", []):
            if flow.get("mode") == mode:
                return flow
    return None


def _historical_manifest_snapshot(artifact_dir: str | Path) -> dict[str, Any]:
    manifest = json.loads((Path(artifact_dir) / "manifest.json").read_text(encoding="utf-8"))
    return {
        "job_id": manifest.get("job_id", ""),
        "company_name": manifest.get("company_name", ""),
        "title": manifest.get("title", ""),
        "review_final_score": float(manifest.get("review_final_score", 0.0) or 0.0),
        "review_verdict": str(manifest.get("review_verdict", "") or ""),
        "rereview_rounds": int(manifest.get("rereview_rounds", 0) or 0),
        "route_mode": str(manifest.get("route_mode", "") or ""),
        "seed_label": str(manifest.get("seed_label", "") or ""),
        "token_metrics_available": False,
    }


def _portfolio_case(artifact_dir: str | Path, selector: StarterSelector) -> dict[str, Any]:
    artifact_dir = Path(artifact_dir)
    manifest = json.loads((artifact_dir / "manifest.json").read_text(encoding="utf-8"))
    jd_text = (artifact_dir / "job.md").read_text(encoding="utf-8")
    selector_payload = selector.select_by_job_id(str(manifest["job_id"]), top_k=3).to_dict()
    return {
        "job_id": str(manifest["job_id"]),
        "company_name": str(manifest["company_name"]),
        "title": str(manifest["title"]),
        "jd_text": jd_text,
        "selector_payload": selector_payload,
        "historical": _historical_manifest_snapshot(artifact_dir),
    }


def run_planner_validation(
    output_dir: str | Path,
    *,
    llm_transport: str = "cli",
    write_model: str = "gpt-5.4",
    review_model: str = "gpt-5.4-mini",
    planner_model: str = "gpt-5.4",
) -> dict:
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    configure_llm_client(
        enabled=True,
        transport=llm_transport,
        write_model=write_model,
        review_model=review_model,
    )
    writer = MasterWriter()
    reviewer = UnifiedReviewer()
    selector = StarterSelector.from_project_data()

    previous_report_path = output_dir / "match_pipe_small_flow_validation_report.json"
    previous_report = json.loads(previous_report_path.read_text(encoding="utf-8")) if previous_report_path.exists() else {}

    current_scraped_cases: list[dict[str, Any]] = []
    for item in previous_report.get("results", [])[:2]:
        docs = {doc.job_id: doc for doc in load_job_documents(include_scraped=True, include_portfolio=False)}
        doc = docs.get(item["job_id"])
        if doc is None:
            continue
        current_scraped_cases.append(
            {
                "job_id": doc.job_id,
                "company_name": doc.company_name,
                "title": doc.title,
                "jd_text": doc.raw_text,
                "selector_payload": selector.select_by_job_id(doc.job_id, top_k=3).to_dict(),
                "historical_no_starter": _historical_flow_from_old_report(doc.job_id, "no_starter", previous_report),
                "historical_old_match_anchor": _historical_flow_from_old_report(doc.job_id, "old_match_anchor", previous_report),
            }
        )

    legacy_cases = [
        _portfolio_case("data/deliverables/resume_portfolio/by_company/affirm/2026-04-02/6941879614ee092a69ffa832", selector),
        _portfolio_case("data/deliverables/resume_portfolio/by_company/nvidia/2026-04-03/69cf8f82366bb95ba55176e0", selector),
    ]

    current_results: list[dict[str, Any]] = []
    for case in current_scraped_cases:
        jd = JDProfile.from_text(case["jd_text"], jd_id=case["job_id"], company=case["company_name"])
        current_results.append(
            {
                "job_id": case["job_id"],
                "company_name": case["company_name"],
                "title": case["title"],
                "historical_no_starter": case["historical_no_starter"],
                "historical_old_match_anchor": case["historical_old_match_anchor"],
                "no_starter_planner": _run_no_starter_planner(
                    writer,
                    reviewer,
                    jd,
                    planner_model=planner_model,
                ).to_dict(),
                "new_dual_channel_planner": _run_new_dual_channel_planner(
                    writer,
                    reviewer,
                    jd,
                    selector_payload=case["selector_payload"],
                    planner_model=planner_model,
                ).to_dict(),
            }
        )

    legacy_results: list[dict[str, Any]] = []
    for case in legacy_cases:
        jd = JDProfile.from_text(case["jd_text"], jd_id=case["job_id"], company=case["company_name"])
        legacy_results.append(
            {
                "job_id": case["job_id"],
                "company_name": case["company_name"],
                "title": case["title"],
                "historical_old_pipeline": case["historical"],
                "new_dual_channel_planner": _run_new_dual_channel_planner(
                    writer,
                    reviewer,
                    jd,
                    selector_payload=case["selector_payload"],
                    planner_model=planner_model,
                ).to_dict(),
            }
        )

    payload = {
        "experiment_type": "planner_first_dual_channel_validation",
        "current_scraped_pair": current_results,
        "legacy_conditional_and_fail_cases": legacy_results,
        "notes": {
            "old_pipeline_tokens_available": False,
            "reason": "Historical portfolio logs record score/verdict/rounds but do not persist comparable token usage or elapsed time.",
        },
    }
    output_path = output_dir / "match_pipe_planner_flow_validation_report.json"
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run planner-first validation for no-starter and dual-channel flows.")
    parser.add_argument("--output-dir", default=str(ROOT / "output" / "analysis"))
    parser.add_argument("--llm-transport", default="cli")
    parser.add_argument("--write-model", default="gpt-5.4")
    parser.add_argument("--review-model", default="gpt-5.4-mini")
    parser.add_argument("--planner-model", default="gpt-5.4")
    args = parser.parse_args()
    payload = run_planner_validation(
        args.output_dir,
        llm_transport=args.llm_transport,
        write_model=args.write_model,
        review_model=args.review_model,
        planner_model=args.planner_model,
    )
    print(
        json.dumps(
            {
                "report": str(Path(args.output_dir).expanduser().resolve() / "match_pipe_planner_flow_validation_report.json"),
                "current_scraped_pair": len(payload["current_scraped_pair"]),
                "legacy_cases": len(payload["legacy_conditional_and_fail_cases"]),
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
