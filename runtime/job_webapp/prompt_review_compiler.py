from __future__ import annotations

import copy
import json
import sys
from types import SimpleNamespace
from typing import Any

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from automation.project_pool import build_project_pool_prompt_block
from core.prompt_builder import (
    CANONICAL_OUTPUT_TEMPLATE,
    MASTER_WRITER_SYSTEM,
    UNIFIED_REVIEWER_SYSTEM,
    build_candidate_context,
    build_master_writer_prompt,
    build_revision_prompt,
    build_seed_retarget_prompt,
    build_unified_review_prompt,
    build_upgrade_revision_prompt,
)
from runtime.job_webapp.prompt_library import (
    _extract_upgrade_blocks,
    _placeholder_jd,
    _resolved_blocks,
    _retarget_block_ids,
    _upgrade_block_ids,
    _writer_block_ids,
    append_match_pipe_dual_channel_overlay,
    build_match_pipe_master_writer_prompt,
    build_match_pipe_planner_prompt,
    build_match_pipe_seed_retarget_prompt,
    build_match_pipe_unified_review_prompt,
    build_match_pipe_upgrade_revision_prompt,
    build_match_pipe_writer_prompt_from_planner,
    build_match_pipe_writer_revision_prompt,
    get_match_pipe_block_text,
    match_pipe_planner_system_prompt,
    match_pipe_reviewer_system_prompt,
    match_pipe_strict_revision_system_prompt,
    match_pipe_upgrade_revision_system_prompt,
    match_pipe_writer_system_prompt,
)
from writers.master_writer import STRICT_REVISION_SYSTEM_PROMPT, UPGRADE_REVISION_SYSTEM_PROMPT

from .prompt_review_common import (
    ACTIVE_CONFLICT_PATH,
    AMBIGUITIES_PATH,
    BASELINE_PATH,
    COVERAGE_PATH,
    EDITED_PATH,
    MAP_PATH,
    PROMPT_REVIEW_DIR,
    REGENERATED_PATH,
    SCHEMA_VERSION,
    SCOPE,
    ensure_prompt_review_dirs,
    empty_ambiguities,
    empty_conflict_state,
    extract_placeholders,
    normalized_text,
    now_iso,
    read_json,
    sha256_text,
    text_to_rich_html,
    write_json,
)


_PLACEHOLDER_COMPANY = "ExampleCorp"
_MATCH_PIPE_OVERRIDES_PATH = "match_pipe/prompt_overrides.json"


def _source_ref(
    path: str,
    *,
    source_type: str,
    object_path: str = "",
    line_start: int | None = None,
    line_end: int | None = None,
    primary: bool = False,
    mirror: bool = False,
    inherited: bool = False,
    override: bool = False,
    key_path: str = "",
    note: str = "",
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "path": path,
        "source_type": source_type,
        "object_path": object_path,
        "key_path": key_path,
        "primary": primary,
        "mirror": mirror,
        "inherited": inherited,
        "override": override,
        "note": note,
    }
    if line_start is not None:
        payload["line_start"] = line_start
    if line_end is not None:
        payload["line_end"] = line_end
    return payload


def _target_ref(
    pipeline: str,
    stage: str,
    role: str,
    *,
    label: str,
    path: str,
    line: int,
) -> dict[str, Any]:
    return {
        "pipeline": pipeline,
        "stage": stage,
        "role": role,
        "label": label,
        "path": path,
        "line": line,
    }


def _block(
    block_id: str,
    *,
    title: str,
    text: str,
    prompt_section: str,
    source_refs: list[dict[str, Any]],
    merge_rule: str = "ordered_concat",
    write_policy: str = "primary_only",
    propagation_rule: str = "recompile_dependents",
    confidence: float = 0.98,
    notes: str = "",
) -> dict[str, Any]:
    normalized = normalized_text(text)
    placeholders = [
        {
            "placeholder_text": token,
            "source": source_refs[0]["path"] if source_refs else "",
            "semantic_slot": token.strip("{}[]"),
            "write_strategy": "preserve_variable",
        }
        for token in extract_placeholders(text)
    ]
    return {
        "block_id": block_id,
        "title": title,
        "text": text.strip(),
        "normalized_text": normalized,
        "prompt_section": prompt_section,
        "source_refs": source_refs,
        "source_priority": 100 if source_refs and source_refs[0].get("primary") else 60,
        "primary_source": source_refs[0] if source_refs else {},
        "placeholder_refs": placeholders,
        "merge_rule": merge_rule,
        "write_policy": write_policy,
        "propagation_rule": propagation_rule,
        "confidence": confidence,
        "duplicate_fingerprint": f"sha256:{sha256_text(normalized)}",
        "notes": notes,
    }


def _compose_group_text(blocks: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for block in blocks:
        parts.append(f"## {block['title']}\n{block['text']}".strip())
    return "\n\n".join(part for part in parts if part.strip())


def _file_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8").strip()


def _sample_revision_result() -> dict[str, Any]:
    return {
        "revision_instructions": "补齐 JD 必须技术的正文证据，并把 summary 对齐到目标岗位。",
        "revision_priority": [
            "补全 Python / backend 相关正文证据",
            "压缩泛化措辞，提升 JD 对齐度",
        ],
        "weighted_score": 88.4,
        "scores": {
            "coverage": {
                "findings": [
                    {
                        "severity": "high",
                        "field": "Experience bullets",
                        "issue": "缺少对 must-have 技术的直接证据",
                        "fix": "在已有经历中补出 Python / backend 实战证据",
                    }
                ]
            }
        },
    }


def _group(
    *,
    group_id: str,
    group_label: str,
    production_chain: str,
    stage: str,
    role: str,
    display_order: int,
    blocks: list[dict[str, Any]],
    target_refs: list[dict[str, Any]],
    prompt_kind: str = "composite",
    description: str = "",
    variant: str = "",
) -> dict[str, Any]:
    display_text = _compose_group_text(blocks)
    return {
        "group_id": group_id,
        "group_label": group_label,
        "production_chain": production_chain,
        "stage": stage,
        "role": role,
        "variant": variant,
        "display_order": display_order,
        "display_text": display_text,
        "editable_rich_text": text_to_rich_html(display_text, group_id=group_id, blocks=blocks),
        "prompt_kind": prompt_kind,
        "description": description,
        "target_refs": target_refs,
        "blocks": blocks,
        "status": "clean",
    }


def _standard_writer_blocks(company: str) -> list[dict[str, Any]]:
    jd = _placeholder_jd(company)
    prompt = build_master_writer_prompt(jd).strip()
    candidate_context = build_candidate_context(company).strip()
    target_specific = ""
    tail = prompt
    if prompt.startswith(candidate_context):
        tail = prompt[len(candidate_context):].lstrip()
    if not tail.startswith("## 目标 JD 信息"):
        before_target, tail = tail.split("## 目标 JD 信息", 1)
        target_specific = before_target.strip()
        tail = f"## 目标 JD 信息{tail}"
    jd_section, after_jd = tail.split("\n---\n\n", 1)
    format_constraints, after_constraints = after_jd.split("\n---\n\n", 1)
    plan_and_resume, _ = after_constraints.rsplit(f"\n\n{CANONICAL_OUTPUT_TEMPLATE}", 1)
    blocks = [
        _block(
            f"standard_writer::{company.lower()}::system",
            title="System Prompt",
            text=MASTER_WRITER_SYSTEM.strip(),
            prompt_section="system",
            source_refs=[
                _source_ref(
                    "runtime/core/prompt_builder.py",
                    source_type="python_constant",
                    object_path="MASTER_WRITER_SYSTEM",
                    line_start=413,
                    primary=True,
                )
            ],
            notes="runtime_main / runtime_seed_retarget writer system prompt.",
        
        write_policy="direct",
        propagation_rule="auto",
    ),
        _block(
            f"standard_writer::{company.lower()}::candidate_context",
            title="Writer User · Candidate Context",
            text=candidate_context,
            prompt_section="user",
            source_refs=[
                _source_ref(
                    "runtime/core/prompt_builder.py",
                    source_type="python_function",
                    object_path="build_candidate_context",
                    line_start=325,
                    primary=True,
                ),
                _source_ref(
                    "runtime/config/candidate_framework.py",
                    source_type="python_constant",
                    object_path="CANDIDATE_FRAMEWORK",
                    line_start=11,
                    inherited=True,
                ),
                _source_ref(
                    "runtime/config/natural_tech.py",
                    source_type="python_constant",
                    object_path="BASE_NATURAL_TECH",
                    line_start=21,
                    inherited=True,
                ),
            ],
        
        write_policy="direct",
        propagation_rule="auto",
    ),
    ]
    if target_specific:
        blocks.append(
            _block(
                f"standard_writer::{company.lower()}::target_specific",
                title="Writer User · Target-specific Context",
                text=target_specific,
                prompt_section="user",
                source_refs=[
                    _source_ref(
                        "runtime/core/prompt_builder.py",
                        source_type="python_function",
                        object_path="_target_specific_context_block",
                        line_start=190,
                        primary=True,
                    )
                ],
            
        write_policy="direct",
        propagation_rule="auto",
    )
        )
    blocks.extend(
        [
            _block(
                f"standard_writer::{company.lower()}::jd_context",
                title="Writer User · Target JD Context",
                text=jd_section.strip(),
                prompt_section="user",
                source_refs=[
                    _source_ref(
                        "runtime/core/prompt_builder.py",
                        source_type="python_function",
                        object_path="build_master_writer_prompt",
                        line_start=478,
                        primary=True,
                    )
                ],
            
        write_policy="direct",
        propagation_rule="auto",
    ),
            _block(
                f"standard_writer::{company.lower()}::format_constraints",
                title="Writer User · Format Constraints",
                text=format_constraints.strip(),
                prompt_section="user",
                source_refs=[
                    _source_ref(
                        "runtime/core/prompt_builder.py",
                        source_type="python_function",
                        object_path="_format_constraints_for_company",
                        line_start=314,
                        primary=True,
                    ),
                    _source_ref(
                        "runtime/config/frozen_constraints.py",
                        source_type="python_constant",
                        object_path="FROZEN_CONSTRAINTS",
                        line_start=16,
                        inherited=True,
                    ),
                ],
            
        write_policy="direct",
        propagation_rule="auto",
    ),
            _block(
                f"standard_writer::{company.lower()}::plan_resume",
                title="Writer User · PLAN and RESUME Scaffold",
                text=plan_and_resume.strip(),
                prompt_section="user",
                source_refs=[
                    _source_ref(
                        "runtime/core/prompt_builder.py",
                        source_type="python_function",
                        object_path="_build_master_plan_template",
                        line_start=231,
                        primary=False,
                    ),
                    _source_ref(
                        "runtime/core/prompt_builder.py",
                        source_type="python_function",
                        object_path="build_master_writer_prompt",
                        line_start=478,
                        primary=True,
                    ),
                ],
            
        write_policy="direct",
        propagation_rule="auto",
    ),
            _block(
                f"standard_writer::{company.lower()}::output_contract",
                title="Writer User · Output Contract",
                text=CANONICAL_OUTPUT_TEMPLATE.strip(),
                prompt_section="user",
                source_refs=[
                    _source_ref(
                        "runtime/core/prompt_builder.py",
                        source_type="python_constant",
                        object_path="CANONICAL_OUTPUT_TEMPLATE",
                        line_start=1,
                        primary=True,
                    )
                ],
            
        write_policy="direct",
        propagation_rule="auto",
    ),
        ]
    )
    return blocks


def _standard_reviewer_blocks(company: str, *, review_scope: str) -> list[dict[str, Any]]:
    jd = _placeholder_jd(company)
    prompt = build_unified_review_prompt("{resume_md}", jd, review_scope=review_scope).strip()
    intro, after_header = prompt.split("## 目标 JD\n\n", 1)
    context, after_context = after_header.split("\n\n---\n\n", 1)
    return [
        _block(
            f"standard_reviewer::{company.lower()}::{review_scope}::system",
            title="System Prompt",
            text=UNIFIED_REVIEWER_SYSTEM.strip(),
            prompt_section="system",
            source_refs=[
                _source_ref(
                    "runtime/core/prompt_builder.py",
                    source_type="python_constant",
                    object_path="UNIFIED_REVIEWER_SYSTEM",
                    line_start=571,
                    primary=True,
                )
            ],
        
        write_policy="direct",
        propagation_rule="auto",
    ),
        _block(
            f"standard_reviewer::{company.lower()}::{review_scope}::context",
            title="Reviewer User · Target JD and Resume Context",
            text=f"## 目标 JD\n\n{context.strip()}",
            prompt_section="user",
            source_refs=[
                _source_ref(
                    "runtime/core/prompt_builder.py",
                    source_type="python_function",
                    object_path="build_unified_review_prompt",
                    line_start=595,
                    primary=True,
                )
            ],
        
        write_policy="direct",
        propagation_rule="auto",
    ),
        _block(
            f"standard_reviewer::{company.lower()}::{review_scope}::schema",
            title="Reviewer User · Instructions and JSON Schema",
            text=f"{intro.strip()}\n\n{after_context.strip()}",
            prompt_section="user",
            source_refs=[
                _source_ref(
                    "runtime/core/prompt_builder.py",
                    source_type="python_function",
                    object_path="build_unified_review_prompt",
                    line_start=595,
                    primary=True,
                )
            ],
        
        write_policy="direct",
        propagation_rule="auto",
    ),
    ]


def _standard_upgrade_blocks(company: str) -> list[dict[str, Any]]:
    extracted = _extract_upgrade_blocks(company)
    blocks = [
        _block(
            f"standard_upgrade::{company.lower()}::system",
            title="System Prompt",
            text=UPGRADE_REVISION_SYSTEM_PROMPT.strip(),
            prompt_section="system",
            source_refs=[
                _source_ref(
                    "runtime/writers/master_writer.py",
                    source_type="python_constant",
                    object_path="UPGRADE_REVISION_SYSTEM_PROMPT",
                    line_start=42,
                    primary=True,
                )
            ],
        
        write_policy="direct",
        propagation_rule="auto",
    ),
        _block(
            f"standard_upgrade::{company.lower()}::main",
            title="Writer User · Upgrade Instructions",
            text=extracted["prompt"],
            prompt_section="user",
            source_refs=[
                _source_ref(
                    "runtime/core/prompt_builder.py",
                    source_type="python_function",
                    object_path="build_upgrade_revision_prompt",
                    line_start=976,
                    primary=True,
                )
            ],
        
        write_policy="direct",
        propagation_rule="auto",
    ),
    ]
    if extracted["bytedance_special"]:
        blocks.append(
            _block(
                f"standard_upgrade::{company.lower()}::bytedance",
                title="Writer User · ByteDance Special Rules",
                text=extracted["bytedance_special"],
                prompt_section="user",
                source_refs=[
                    _source_ref(
                        "runtime/core/prompt_builder.py",
                        source_type="python_constant",
                        object_path="BYTEDANCE_UPGRADE_SPECIAL_BLOCK",
                        line_start=95,
                        primary=True,
                    )
                ],
            
        write_policy="direct",
        propagation_rule="auto",
    )
        )
    blocks.extend(
        [
            _block(
                f"standard_upgrade::{company.lower()}::resume_context",
                title="Writer User · Existing Resume Context",
                text=extracted["resume_context"],
                prompt_section="user",
                source_refs=[
                    _source_ref(
                        "runtime/core/prompt_builder.py",
                        source_type="python_function",
                        object_path="build_upgrade_revision_prompt",
                        line_start=976,
                        primary=True,
                    )
                ],
            
        write_policy="direct",
        propagation_rule="auto",
    ),
            _block(
                f"standard_upgrade::{company.lower()}::output_contract",
                title="Writer User · Output Contract",
                text=CANONICAL_OUTPUT_TEMPLATE.strip(),
                prompt_section="user",
                source_refs=[
                    _source_ref(
                        "runtime/core/prompt_builder.py",
                        source_type="python_constant",
                        object_path="CANONICAL_OUTPUT_TEMPLATE",
                        line_start=1,
                        primary=True,
                    )
                ],
            
        write_policy="direct",
        propagation_rule="auto",
    ),
        ]
    )
    return blocks


def _repair_prompt_blocks() -> list[dict[str, Any]]:
    user_text = (
        "将下面这段 reviewer 输出修复为合法 JSON。"
        "不要改动语义，不要省略字段，不要解释，只输出 JSON 对象。\n\n"
        "{raw_reviewer_output}"
    )
    system_text = (
        "你是 JSON 修复器。输入是一段可能有少量格式错误的 JSON。"
        "输出必须是严格合法的 JSON 对象，不要附加解释，不要使用 Markdown code fence。"
    )
    return [
        _block(
            "runtime_reviewer_fallback::json_repair::system",
            title="System Prompt",
            text=system_text,
            prompt_section="system",
            source_refs=[
                _source_ref(
                    "runtime/reviewers/unified_reviewer.py",
                    source_type="inline_string",
                    object_path="_attempt_review_json_repair.system",
                    line_start=391,
                    primary=True,
                )
            ],
            write_policy="ambiguous",
            propagation_rule="manual_review_before_writeback",
        ),
        _block(
            "runtime_reviewer_fallback::json_repair::user",
            title="User Prompt",
            text=user_text,
            prompt_section="user",
            source_refs=[
                _source_ref(
                    "runtime/reviewers/unified_reviewer.py",
                    source_type="inline_string",
                    object_path="_attempt_review_json_repair.user",
                    line_start=389,
                    primary=True,
                )
            ],
            write_policy="ambiguous",
            propagation_rule="manual_review_before_writeback",
        ),
    ]


def _match_pipe_block(block_id: str, block_map: dict[str, Any], *, prompt_section: str = "user") -> dict[str, Any]:
    prompt_block = block_map[block_id]
    return _block(
        block_id,
        title=prompt_block.title or block_id,
        text=prompt_block.text,
        prompt_section=prompt_section,
        source_refs=[
            _source_ref(
                "runtime/job_webapp/prompt_library.py",
                source_type="prompt_block",
                object_path=f"PromptBlock:{block_id}",
                primary=True,
                note=prompt_block.source_note,
            ),
            _source_ref(
                _MATCH_PIPE_OVERRIDES_PATH,
                source_type="json_override",
                object_path=f"blocks.{block_id}",
                mirror=True,
                override=True,
                note="Runtime override path for match_pipe blocks.",
            ),
        ],
        write_policy="direct",
        propagation_rule="auto",
        confidence=0.84 if prompt_block.source_kind != "default" else 0.9,
        notes=prompt_block.source_note,
    )


def _match_pipe_system_block(system_id: str, title: str, text: str) -> dict[str, Any]:
    object_path = {
        "writer_system": "match_pipe_writer_system_prompt",
        "strict_revision_system": "match_pipe_strict_revision_system_prompt",
        "upgrade_revision_system": "match_pipe_upgrade_revision_system_prompt",
        "reviewer_system": "match_pipe_reviewer_system_prompt",
        "planner_system": "match_pipe_planner_system_prompt",
    }[system_id]
    return _block(
        system_id,
        title=title,
        text=text,
        prompt_section="system",
        source_refs=[
            _source_ref(
                "runtime/job_webapp/prompt_library.py",
                source_type="python_function",
                object_path=object_path,
                line_start=2728 if system_id == "writer_system" else 2732,
                primary=True,
            ),
            _source_ref(
                _MATCH_PIPE_OVERRIDES_PATH,
                source_type="json_override",
                object_path=f"blocks.{system_id}",
                mirror=True,
                override=True,
            ),
        ],
        write_policy="direct",
        propagation_rule="auto",
    )


def _match_pipe_groups() -> list[dict[str, Any]]:
    resolved_block_map = {block.block_id: block for block in _resolved_blocks()}
    groups: list[dict[str, Any]] = []
    order = 100

    def add(group_id: str, label: str, stage: str, role: str, *, company: str, system_kind: str, block_ids: list[str], targets: list[dict[str, Any]], variant: str = "", description: str = "") -> None:
        nonlocal order
        system_lookup = {
            "writer": ("writer_system", "System Prompt", match_pipe_writer_system_prompt()),
            "strict_revision": ("strict_revision_system", "System Prompt", match_pipe_strict_revision_system_prompt()),
            "upgrade": ("upgrade_revision_system", "System Prompt", match_pipe_upgrade_revision_system_prompt()),
            "reviewer": ("reviewer_system", "System Prompt", match_pipe_reviewer_system_prompt()),
            "planner": ("planner_system", "System Prompt", match_pipe_planner_system_prompt()),
        }
        system_id, system_title, system_text = system_lookup[system_kind]
        blocks = [_match_pipe_system_block(system_id, system_title, system_text)]
        blocks.extend(_match_pipe_block(block_id, resolved_block_map) for block_id in block_ids)
        groups.append(
            _group(
                group_id=group_id,
                group_label=label,
                production_chain="match_pipe",
                stage=stage,
                role=role,
                display_order=order,
                blocks=blocks,
                target_refs=targets,
                description=description,
                variant=variant,
            )
        )
        order += 1

    add(
        "match_pipe::no_starter::writer",
        "match_pipe / no_starter / writer",
        "no_starter",
        "writer",
        company=_PLACEHOLDER_COMPANY,
        system_kind="writer",
        block_ids=list(_writer_block_ids(_PLACEHOLDER_COMPANY)),
        targets=[_target_ref("match_pipe", "no_starter", "writer", label="_run_no_starter", path="match_pipe/downstream_validation_runner.py", line=162)],
        description="从零生成路径的完整 writer 调用。",
    )
    add(
        "match_pipe::no_starter::writer::bytedance",
        "match_pipe / no_starter / writer / bytedance",
        "no_starter / bytedance",
        "writer",
        company="ByteDance",
        system_kind="writer",
        block_ids=list(_writer_block_ids("ByteDance")),
        targets=[_target_ref("match_pipe", "no_starter", "writer", label="_run_no_starter", path="match_pipe/downstream_validation_runner.py", line=162)],
        variant="bytedance",
    )
    for same_company in (False, True):
        suffix = "::same_company" if same_company else ""
        add(
            f"match_pipe::old_match_anchor::writer{suffix}",
            f"match_pipe / old_match_anchor / writer{' / same_company' if same_company else ''}",
            "old_match_anchor",
            "writer",
            company=_PLACEHOLDER_COMPANY,
            system_kind="strict_revision",
            block_ids=list(_retarget_block_ids(_PLACEHOLDER_COMPANY, include_same_company=same_company)),
            targets=[_target_ref("match_pipe", "old_match_anchor", "writer", label="_run_old_match", path="match_pipe/downstream_validation_runner.py", line=205)],
            variant="same_company" if same_company else "",
        )
        add(
            f"match_pipe::old_match_anchor::writer::bytedance{suffix}",
            f"match_pipe / old_match_anchor / writer / bytedance{' / same_company' if same_company else ''}",
            "old_match_anchor / bytedance",
            "writer",
            company="ByteDance",
            system_kind="strict_revision",
            block_ids=list(_retarget_block_ids("ByteDance", include_same_company=same_company)),
            targets=[_target_ref("match_pipe", "old_match_anchor", "writer", label="_run_old_match", path="match_pipe/downstream_validation_runner.py", line=205)],
            variant="bytedance_same_company" if same_company else "bytedance",
        )
    for same_company in (False, True):
        suffix = "::same_company" if same_company else ""
        add(
            f"match_pipe::new_dual_channel::writer{suffix}",
            f"match_pipe / new_dual_channel / writer{' / same_company' if same_company else ''}",
            "new_dual_channel",
            "writer",
            company=_PLACEHOLDER_COMPANY,
            system_kind="strict_revision",
            block_ids=list(_retarget_block_ids(_PLACEHOLDER_COMPANY, include_dual=True, include_same_company=same_company)),
            targets=[_target_ref("match_pipe", "new_dual_channel", "writer", label="_run_new_dual_channel", path="match_pipe/downstream_validation_runner.py", line=271)],
            variant="same_company" if same_company else "",
        )
        add(
            f"match_pipe::new_dual_channel::writer::bytedance{suffix}",
            f"match_pipe / new_dual_channel / writer / bytedance{' / same_company' if same_company else ''}",
            "new_dual_channel / bytedance",
            "writer",
            company="ByteDance",
            system_kind="strict_revision",
            block_ids=list(_retarget_block_ids("ByteDance", include_dual=True, include_same_company=same_company)),
            targets=[_target_ref("match_pipe", "new_dual_channel", "writer", label="_run_new_dual_channel", path="match_pipe/downstream_validation_runner.py", line=271)],
            variant="bytedance_same_company" if same_company else "bytedance",
        )
    add(
        "match_pipe::reviewer::full",
        "match_pipe / all reviewer steps / reviewer",
        "all reviewer steps",
        "reviewer",
        company=_PLACEHOLDER_COMPANY,
        system_kind="reviewer",
        block_ids=["reviewer_user", "reviewer_context", "reviewer_output_schema"],
        targets=[
            _target_ref("match_pipe", "all reviewer steps", "reviewer", label="_review_with_revision", path="match_pipe/downstream_validation_runner.py", line=100),
            _target_ref("match_pipe", "all reviewer steps", "reviewer", label="_review_direct_or_written", path="match_pipe/planner_validation_runner.py", line=156),
        ],
    )
    add(
        "match_pipe::reviewer::full::bytedance",
        "match_pipe / all reviewer steps / reviewer / bytedance",
        "all reviewer steps / bytedance",
        "reviewer",
        company="ByteDance",
        system_kind="reviewer",
        block_ids=["reviewer_user", "reviewer_user_bytedance", "reviewer_context", "reviewer_context_bytedance", "reviewer_output_schema"],
        targets=[
            _target_ref("match_pipe", "all reviewer steps", "reviewer", label="_review_with_revision", path="match_pipe/downstream_validation_runner.py", line=100),
            _target_ref("match_pipe", "all reviewer steps", "reviewer", label="_review_direct_or_written", path="match_pipe/planner_validation_runner.py", line=156),
        ],
        variant="bytedance",
    )
    add(
        "match_pipe::reviewer_followup::writer",
        "match_pipe / reviewer 后续改写 / writer",
        "reviewer 后续改写",
        "writer",
        company=_PLACEHOLDER_COMPANY,
        system_kind="upgrade",
        block_ids=list(_upgrade_block_ids(_PLACEHOLDER_COMPANY)),
        targets=[
            _target_ref("match_pipe", "reviewer 后续改写", "writer", label="_review_with_revision", path="match_pipe/downstream_validation_runner.py", line=114),
            _target_ref("match_pipe", "planner revision", "writer", label="_review_direct_or_written", path="match_pipe/planner_validation_runner.py", line=168),
        ],
    )
    add(
        "match_pipe::reviewer_followup::writer::bytedance",
        "match_pipe / reviewer 后续改写 / writer / bytedance",
        "reviewer 后续改写 / bytedance",
        "writer",
        company="ByteDance",
        system_kind="upgrade",
        block_ids=list(_upgrade_block_ids("ByteDance")),
        targets=[
            _target_ref("match_pipe", "reviewer 后续改写", "writer", label="_review_with_revision", path="match_pipe/downstream_validation_runner.py", line=114),
            _target_ref("match_pipe", "planner revision", "writer", label="_review_direct_or_written", path="match_pipe/planner_validation_runner.py", line=168),
        ],
        variant="bytedance",
    )
    add(
        "match_pipe::planner::planner",
        "match_pipe / planner / planner",
        "planner",
        "planner",
        company=_PLACEHOLDER_COMPANY,
        system_kind="planner",
        block_ids=["planner_user", "planner_context"],
        targets=[_target_ref("match_pipe", "planner", "planner", label="_plan_flow", path="match_pipe/planner_validation_runner.py", line=117)],
    )
    add(
        "match_pipe::planner_write::writer",
        "match_pipe / planner write / writer",
        "planner write",
        "writer",
        company=_PLACEHOLDER_COMPANY,
        system_kind="writer",
        block_ids=list(_writer_block_ids(_PLACEHOLDER_COMPANY)) + ["planner_writer_context", "planner_writer_overlay"],
        targets=[
            _target_ref("match_pipe", "planner write", "writer", label="_run_no_starter_planner", path="match_pipe/planner_validation_runner.py", line=225),
            _target_ref("match_pipe", "planner write", "writer", label="_run_new_dual_channel_planner", path="match_pipe/planner_validation_runner.py", line=263),
        ],
    )
    add(
        "match_pipe::planner_write::writer::bytedance",
        "match_pipe / planner write / writer / bytedance",
        "planner write / bytedance",
        "writer",
        company="ByteDance",
        system_kind="writer",
        block_ids=list(_writer_block_ids("ByteDance")) + ["planner_writer_context", "planner_writer_overlay"],
        targets=[
            _target_ref("match_pipe", "planner write", "writer", label="_run_no_starter_planner", path="match_pipe/planner_validation_runner.py", line=225),
            _target_ref("match_pipe", "planner write", "writer", label="_run_new_dual_channel_planner", path="match_pipe/planner_validation_runner.py", line=263),
        ],
        variant="bytedance",
    )
    add(
        "match_pipe::planner_direct_review::reviewer",
        "match_pipe / planner direct_review / reviewer",
        "planner direct_review",
        "reviewer",
        company=_PLACEHOLDER_COMPANY,
        system_kind="reviewer",
        block_ids=["reviewer_user", "reviewer_context", "reviewer_output_schema"],
        targets=[_target_ref("match_pipe", "planner direct_review", "reviewer", label="_run_new_dual_channel_planner", path="match_pipe/planner_validation_runner.py", line=329)],
    )
    add(
        "match_pipe::planner_direct_review::reviewer::bytedance",
        "match_pipe / planner direct_review / reviewer / bytedance",
        "planner direct_review / bytedance",
        "reviewer",
        company="ByteDance",
        system_kind="reviewer",
        block_ids=["reviewer_user", "reviewer_user_bytedance", "reviewer_context", "reviewer_context_bytedance", "reviewer_output_schema"],
        targets=[_target_ref("match_pipe", "planner direct_review", "reviewer", label="_run_new_dual_channel_planner", path="match_pipe/planner_validation_runner.py", line=329)],
        variant="bytedance",
    )
    add(
        "match_pipe::planner_revision::writer",
        "match_pipe / planner revision / writer",
        "planner revision",
        "writer",
        company=_PLACEHOLDER_COMPANY,
        system_kind="upgrade",
        block_ids=list(_writer_block_ids(_PLACEHOLDER_COMPANY)) + ["planner_revision_context", "planner_revision_overlay"],
        targets=[_target_ref("match_pipe", "planner revision", "writer", label="_review_direct_or_written", path="match_pipe/planner_validation_runner.py", line=168)],
    )
    add(
        "match_pipe::planner_revision::writer::bytedance",
        "match_pipe / planner revision / writer / bytedance",
        "planner revision / bytedance",
        "writer",
        company="ByteDance",
        system_kind="upgrade",
        block_ids=list(_writer_block_ids("ByteDance")) + ["planner_revision_context", "planner_revision_overlay"],
        targets=[_target_ref("match_pipe", "planner revision", "writer", label="_review_direct_or_written", path="match_pipe/planner_validation_runner.py", line=168)],
        variant="bytedance",
    )
    return groups


def _runtime_groups() -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    order = 1
    for company, variant in ((_PLACEHOLDER_COMPANY, ""), ("ByteDance", "bytedance")):
        label_suffix = " / bytedance" if variant else ""
        stage_suffix = " / bytedance" if variant else ""
        groups.append(
            _group(
                group_id=f"runtime_main::generate::writer{'::bytedance' if variant else ''}",
                group_label=f"runtime_main / generate / writer{label_suffix}",
                production_chain="runtime_main",
                stage=f"generate{stage_suffix}",
                role="writer",
                display_order=order,
                blocks=_standard_writer_blocks(company),
                target_refs=[_target_ref("runtime_main", "generate", "writer", label="PipelineOrchestrator.run", path="runtime/pipeline/orchestrator.py", line=96)],
                variant=variant,
            )
        )
        order += 1
        groups.append(
            _group(
                group_id=f"runtime_main::full_review::reviewer{'::bytedance' if variant else ''}",
                group_label=f"runtime_main / full_review / reviewer{label_suffix}",
                production_chain="runtime_main",
                stage=f"full_review{stage_suffix}",
                role="reviewer",
                display_order=order,
                blocks=_standard_reviewer_blocks(company, review_scope="full"),
                target_refs=[_target_ref("runtime_main", "full_review", "reviewer", label="PipelineOrchestrator.run", path="runtime/pipeline/orchestrator.py", line=117)],
                variant=variant,
            )
        )
        order += 1
        groups.append(
            _group(
                group_id=f"runtime_main::upgrade_revision::writer{'::bytedance' if variant else ''}",
                group_label=f"runtime_main / upgrade_revision / writer{label_suffix}",
                production_chain="runtime_main",
                stage=f"upgrade_revision{stage_suffix}",
                role="writer",
                display_order=order,
                blocks=_standard_upgrade_blocks(company),
                target_refs=[_target_ref("runtime_main", "upgrade_revision", "writer", label="PipelineOrchestrator.run", path="runtime/pipeline/orchestrator.py", line=140)],
                variant=variant,
            )
        )
        order += 1
        groups.append(
            _group(
                group_id=f"runtime_seed_retarget::rewrite_review::reviewer{'::bytedance' if variant else ''}",
                group_label=f"runtime_seed_retarget / rewrite_review / reviewer{label_suffix}",
                production_chain="runtime_seed_retarget",
                stage=f"rewrite_review{stage_suffix}",
                role="reviewer",
                display_order=order,
                blocks=_standard_reviewer_blocks(company, review_scope="rewrite"),
                target_refs=[_target_ref("runtime_seed_retarget", "rewrite_review", "reviewer", label="SeedRetargetOrchestrator.run", path="runtime/pipeline/retarget_orchestrator.py", line=80)],
                variant=variant,
            )
        )
        order += 1
        groups.append(
            _group(
                group_id=f"runtime_seed_retarget::rewrite_writer::writer{'::bytedance' if variant else ''}",
                group_label=f"runtime_seed_retarget / rewrite_writer / writer{label_suffix}",
                production_chain="runtime_seed_retarget",
                stage=f"rewrite_writer{stage_suffix}",
                role="writer",
                display_order=order,
                blocks=_standard_upgrade_blocks(company),
                target_refs=[_target_ref("runtime_seed_retarget", "rewrite_writer", "writer", label="SeedRetargetOrchestrator.run", path="runtime/pipeline/retarget_orchestrator.py", line=83)],
                variant=variant,
            )
        )
        order += 1
    groups.append(
        _group(
            group_id="runtime_reviewer_fallback::json_repair::reviewer_repairer",
            group_label="runtime_reviewer_fallback / json_repair / reviewer_repairer",
            production_chain="runtime_reviewer_fallback",
            stage="json_repair",
            role="reviewer_repairer",
            display_order=order,
            blocks=_repair_prompt_blocks(),
            target_refs=[_target_ref("runtime_reviewer_fallback", "json_repair", "reviewer_repairer", label="_attempt_review_json_repair", path="runtime/reviewers/unified_reviewer.py", line=382)],
        )
    )
    order += 1
    match_pipe_groups = _match_pipe_groups()
    for index, group in enumerate(match_pipe_groups, start=order):
        group["display_order"] = index
        groups.append(group)
    return groups


def _reference_groups(start_order: int) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    order = start_order
    placeholder_jd = _placeholder_jd(_PLACEHOLDER_COMPANY)
    revision_prompt = build_revision_prompt(
        resume_md="{resume_md}",
        review_result=_sample_revision_result(),
        plan_text="## 最终 PLAN\n- 把 Python/backend 证据优先放在最相关经历中。",
        tech_required=["Python", "REST APIs"],
        jd_title=placeholder_jd.title,
        target_company=placeholder_jd.company,
    ).strip()
    seed_retarget_prompt = build_seed_retarget_prompt(
        "## Professional Summary\nSeed resume placeholder.",
        placeholder_jd,
        seed_label="seed-placeholder",
        route_mode="retarget",
        top_candidate={
            "missing_required": ["Python"],
            "same_company": False,
            "company_anchor": False,
            "seed_source_job_id": "seed-job-placeholder",
            "seed_company_name": "ExampleCorp",
            "project_ids": [],
        },
    ).strip()
    reference_specs = [
        {
            "group_id": "source_reference::inactive_builder::revision_writer",
            "group_label": "source_reference / inactive_builder / writer / revision_prompt",
            "production_chain": "source_reference",
            "stage": "inactive_builder",
            "role": "writer",
            "description": "Callable but currently un-orchestrated revision builder. Kept as visible reference to avoid prompt omission.",
            "blocks": [
                _block(
                    "source_reference::inactive_builder::revision_writer::user",
                    title="Revision Builder User Prompt",
                    text=revision_prompt,
                    prompt_section="user",
                    source_refs=[
                        _source_ref(
                            "runtime/core/prompt_builder.py",
                            source_type="python_function",
                            object_path="build_revision_prompt",
                            line_start=792,
                            primary=True,
                        )
                    ],
                    merge_rule="source_locked",
                    write_policy="ambiguous",
                    propagation_rule="manual_review_before_writeback",
                    confidence=0.78,
                    notes="Inactive builder reference group, not an active orchestrator receiver.",
                )
            ],
            "target_refs": [
                _target_ref(
                    "source_reference",
                    "inactive_builder",
                    "writer",
                    label="build_revision_prompt",
                    path="runtime/core/prompt_builder.py",
                    line=792,
                )
            ],
        },
        {
            "group_id": "source_reference::indirect_runtime::seed_retarget_writer",
            "group_label": "source_reference / indirect_runtime / writer / seed_retarget",
            "production_chain": "source_reference",
            "stage": "indirect_runtime",
            "role": "writer",
            "description": "Callable retarget path in MasterWriter, not currently emitted by the top orchestrator.",
            "blocks": [
                _block(
                    "source_reference::indirect_runtime::seed_retarget_writer::system",
                    title="Strict Revision System Prompt",
                    text=STRICT_REVISION_SYSTEM_PROMPT.strip(),
                    prompt_section="system",
                    source_refs=[
                        _source_ref(
                            "runtime/writers/master_writer.py",
                            source_type="python_constant",
                            object_path="STRICT_REVISION_SYSTEM_PROMPT",
                            line_start=38,
                            primary=True,
                        )
                    ],
                    merge_rule="source_locked",
                    write_policy="ambiguous",
                    propagation_rule="manual_review_before_writeback",
                    confidence=0.74,
                    notes="Indirect runtime system prompt used by MasterWriter.revise(strict).",
                ),
                _block(
                    "source_reference::indirect_runtime::seed_retarget_writer::user",
                    title="Seed Retarget User Prompt",
                    text=seed_retarget_prompt,
                    prompt_section="user",
                    source_refs=[
                        _source_ref(
                            "runtime/core/prompt_builder.py",
                            source_type="python_function",
                            object_path="build_seed_retarget_prompt",
                            line_start=881,
                            primary=True,
                        ),
                        _source_ref(
                            "runtime/writers/master_writer.py",
                            source_type="python_method",
                            object_path="MasterWriter.retarget",
                            line_start=173,
                            mirror=True,
                        ),
                    ],
                    merge_rule="source_locked",
                    write_policy="ambiguous",
                    propagation_rule="manual_review_before_writeback",
                    confidence=0.74,
                    notes="Indirect runtime user prompt. Present for completeness and backfill planning.",
                ),
            ],
            "target_refs": [
                _target_ref(
                    "source_reference",
                    "indirect_runtime",
                    "writer",
                    label="MasterWriter.retarget",
                    path="runtime/writers/master_writer.py",
                    line=173,
                )
            ],
        },
        {
            "group_id": "source_reference::doc::prompt_canonical_review",
            "group_label": "source_reference / doc / reference / prompt_canonical_review",
            "production_chain": "source_reference",
            "stage": "doc",
            "role": "reference",
            "description": "Prompt review documentation source retained as editable reference text.",
            "blocks": [
                _block(
                    "source_reference::doc::prompt_canonical_review::document",
                    title="Document Source",
                    text=_file_text("docs/prompt_canonical_review.md"),
                    prompt_section="reference",
                    source_refs=[
                        _source_ref(
                            "docs/prompt_canonical_review.md",
                            source_type="markdown_document",
                            object_path="document_prompt_review",
                            line_start=1,
                            primary=True,
                        )
                    ],
                    merge_rule="source_locked",
                    write_policy="ambiguous",
                    propagation_rule="manual_review_before_writeback",
                    confidence=0.7,
                    notes="Non-runtime prompt-bearing document included to guarantee project-level coverage.",
                )
            ],
            "target_refs": [
                _target_ref(
                    "source_reference",
                    "doc",
                    "reference",
                    label="prompt_canonical_review",
                    path="docs/prompt_canonical_review.md",
                    line=1,
                )
            ],
        },
        {
            "group_id": "source_reference::doc::match_pipe_prompt_review",
            "group_label": "source_reference / doc / reference / match_pipe_prompt_review",
            "production_chain": "source_reference",
            "stage": "doc",
            "role": "reference",
            "description": "match_pipe prompt review document retained as editable reference text.",
            "blocks": [
                _block(
                    "source_reference::doc::match_pipe_prompt_review::document",
                    title="Document Source",
                    text=_file_text("docs/match_pipe_prompt_review.md"),
                    prompt_section="reference",
                    source_refs=[
                        _source_ref(
                            "docs/match_pipe_prompt_review.md",
                            source_type="markdown_document",
                            object_path="document_match_pipe_review",
                            line_start=1,
                            primary=True,
                        )
                    ],
                    merge_rule="source_locked",
                    write_policy="ambiguous",
                    propagation_rule="manual_review_before_writeback",
                    confidence=0.7,
                    notes="Non-runtime prompt-bearing document included to guarantee project-level coverage.",
                )
            ],
            "target_refs": [
                _target_ref(
                    "source_reference",
                    "doc",
                    "reference",
                    label="match_pipe_prompt_review",
                    path="docs/match_pipe_prompt_review.md",
                    line=1,
                )
            ],
        },
        {
            "group_id": "source_reference::design_guide::task_general_prompt",
            "group_label": "source_reference / design_guide / reference / task_general_prompt",
            "production_chain": "source_reference",
            "stage": "design_guide",
            "role": "reference",
            "description": "Design-guide prompt source retained as editable reference text.",
            "blocks": [
                _block(
                    "source_reference::design_guide::task_general_prompt::document",
                    title="Design Guide Source",
                    text=_file_text("match_pipe/design-guide/1. task-general-prompt.md"),
                    prompt_section="reference",
                    source_refs=[
                        _source_ref(
                            "match_pipe/design-guide/1. task-general-prompt.md",
                            source_type="markdown_document",
                            object_path="design_guide_prompt_1",
                            line_start=1,
                            primary=True,
                        )
                    ],
                    merge_rule="source_locked",
                    write_policy="ambiguous",
                    propagation_rule="manual_review_before_writeback",
                    confidence=0.68,
                    notes="Prompt-bearing design guide retained to keep project-wide coverage explicit.",
                )
            ],
            "target_refs": [
                _target_ref(
                    "source_reference",
                    "design_guide",
                    "reference",
                    label="task_general_prompt",
                    path="match_pipe/design-guide/1. task-general-prompt.md",
                    line=1,
                )
            ],
        },
        {
            "group_id": "source_reference::design_guide::execution_suggestions_prompt",
            "group_label": "source_reference / design_guide / reference / execution_suggestions_prompt",
            "production_chain": "source_reference",
            "stage": "design_guide",
            "role": "reference",
            "description": "Design-guide execution suggestions retained as editable reference text.",
            "blocks": [
                _block(
                    "source_reference::design_guide::execution_suggestions_prompt::document",
                    title="Design Guide Source",
                    text=_file_text("match_pipe/design-guide/3. execution-suggestions-prompt.md"),
                    prompt_section="reference",
                    source_refs=[
                        _source_ref(
                            "match_pipe/design-guide/3. execution-suggestions-prompt.md",
                            source_type="markdown_document",
                            object_path="design_guide_prompt_3",
                            line_start=1,
                            primary=True,
                        )
                    ],
                    merge_rule="source_locked",
                    write_policy="ambiguous",
                    propagation_rule="manual_review_before_writeback",
                    confidence=0.68,
                    notes="Prompt-bearing design guide retained to keep project-wide coverage explicit.",
                )
            ],
            "target_refs": [
                _target_ref(
                    "source_reference",
                    "design_guide",
                    "reference",
                    label="execution_suggestions_prompt",
                    path="match_pipe/design-guide/3. execution-suggestions-prompt.md",
                    line=1,
                )
            ],
        },
        {
            "group_id": "source_reference::test_fixture::prompt_merge_equivalence",
            "group_label": "source_reference / test_fixture / reference / prompt_merge_equivalence",
            "production_chain": "source_reference",
            "stage": "test_fixture",
            "role": "reference",
            "description": "Prompt-bearing test fixture retained as editable reference text.",
            "blocks": [
                _block(
                    "source_reference::test_fixture::prompt_merge_equivalence::python_source",
                    title="Test Fixture Source",
                    text=_file_text("tests/test_prompt_merge_equivalence.py"),
                    prompt_section="reference",
                    source_refs=[
                        _source_ref(
                            "tests/test_prompt_merge_equivalence.py",
                            source_type="python_test_fixture",
                            object_path="test_prompt_equivalence",
                            line_start=1,
                            primary=True,
                        )
                    ],
                    merge_rule="source_locked",
                    write_policy="ambiguous",
                    propagation_rule="manual_review_before_writeback",
                    confidence=0.64,
                    notes="Prompt-bearing test fixture included for auditability and round-trip search coverage.",
                )
            ],
            "target_refs": [
                _target_ref(
                    "source_reference",
                    "test_fixture",
                    "reference",
                    label="prompt_merge_equivalence",
                    path="tests/test_prompt_merge_equivalence.py",
                    line=1,
                )
            ],
        },
    ]
    for spec in reference_specs:
        groups.append(
            _group(
                group_id=spec["group_id"],
                group_label=spec["group_label"],
                production_chain=spec["production_chain"],
                stage=spec["stage"],
                role=spec["role"],
                display_order=order,
                blocks=spec["blocks"],
                target_refs=spec["target_refs"],
                prompt_kind="reference_bundle",
                description=spec["description"],
            )
        )
        order += 1
    return groups


def _enrich_duplicate_policies(groups: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    groups_copy = copy.deepcopy(groups)
    fingerprint_to_groups: dict[str, set[str]] = {}
    block_id_to_groups: dict[str, set[str]] = {}
    for group in groups_copy:
        for block in group["blocks"]:
            fingerprint_to_groups.setdefault(block["duplicate_fingerprint"], set()).add(group["group_id"])
            block_id_to_groups.setdefault(block["block_id"], set()).add(group["group_id"])
    duplicates: list[dict[str, Any]] = []
    low_confidence: list[dict[str, Any]] = []
    for group in groups_copy:
        for block in group["blocks"]:
            same_block_groups = block_id_to_groups.get(block["block_id"], set())
            same_text_groups = fingerprint_to_groups.get(block["duplicate_fingerprint"], set())
            if len(same_block_groups) > 1:
                block["propagation_rule"] = "recompile_dependents"
            if len(same_text_groups) > 1:
                block["write_policy"] = "primary_only"
            if block["confidence"] < 0.9:
                low_confidence.append(
                    {
                        "group_id": group["group_id"],
                        "block_id": block["block_id"],
                        "confidence": block["confidence"],
                        "notes": block.get("notes", ""),
                    }
                )
    for fingerprint, group_ids in sorted(fingerprint_to_groups.items()):
        if len(group_ids) <= 1:
            continue
        duplicates.append(
            {
                "duplicate_fingerprint": fingerprint,
                "group_ids": sorted(group_ids),
            }
        )
    mirrors = [
        {
            "block_id": block_id,
            "group_ids": sorted(group_ids),
        }
        for block_id, group_ids in sorted(block_id_to_groups.items())
        if len(group_ids) > 1
    ]
    return groups_copy, duplicates, mirrors


def _inactive_source_items() -> list[dict[str, Any]]:
    return []


def _build_source_catalog(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    catalog: list[dict[str, Any]] = []
    for group in groups:
        for block in group["blocks"]:
            for source_ref in block["source_refs"]:
                key = json.dumps(source_ref, sort_keys=True, ensure_ascii=False)
                if key in seen:
                    continue
                seen.add(key)
                catalog.append(source_ref)
    return catalog


def _build_map(groups: list[dict[str, Any]], duplicates: list[dict[str, Any]], mirrors: list[dict[str, Any]]) -> dict[str, Any]:
    flattened_blocks = [
        {
            "group_id": group["group_id"],
            "group_label": group["group_label"],
            "production_chain": group["production_chain"],
            "stage": group["stage"],
            "role": group["role"],
            **copy.deepcopy(block),
        }
        for group in groups
        for block in group["blocks"]
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "generated_at": now_iso(),
        "group_count": len(groups),
        "block_count": len(flattened_blocks),
        "groups": [
            {
                "group_id": group["group_id"],
                "group_label": group["group_label"],
                "production_chain": group["production_chain"],
                "stage": group["stage"],
                "role": group["role"],
                "display_order": group["display_order"],
                "display_text": group["display_text"],
                "editable_rich_text": group["editable_rich_text"],
                "blocks": group["blocks"],
                "target_refs": group["target_refs"],
            }
            for group in groups
        ],
        "blocks": flattened_blocks,
        "source_catalog": _build_source_catalog(groups),
        "source_registry": _build_source_catalog(groups),
        "duplicate_clusters": duplicates,
        "mirrors": mirrors,
        "inactive_sources": _inactive_source_items(),
        "orphan_sources": [],
    }


def _build_coverage(groups: list[dict[str, Any]], duplicates: list[dict[str, Any]], mirrors: list[dict[str, Any]], low_confidence: list[dict[str, Any]]) -> dict[str, Any]:
    active_source_items = _build_source_catalog(groups)
    inactive_items = _inactive_source_items()
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "generated_at": now_iso(),
        "source_item_count": len(active_source_items),
        "covered_source_item_count": len(active_source_items),
        "coverage_ratio": 1.0,
        "group_count": len(groups),
        "block_count": sum(len(group["blocks"]) for group in groups),
        "uncovered": [],
        "low_confidence": low_confidence,
        "duplicate_clusters": duplicates,
        "mirrors": mirrors,
        "excluded_non_runtime": inactive_items,
    }


def compile_prompt_review_snapshot(*, regenerated: bool = False) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    runtime_groups = _runtime_groups()
    reference_groups = _reference_groups(len(runtime_groups) + 1)
    groups, duplicates, mirrors = _enrich_duplicate_policies(runtime_groups + reference_groups)
    low_confidence = [
        {
            "group_id": group["group_id"],
            "block_id": block["block_id"],
            "confidence": block["confidence"],
            "notes": block.get("notes", ""),
        }
        for group in groups
        for block in group["blocks"]
        if block["confidence"] < 0.9
    ]
    build_kind = "regenerated" if regenerated else "baseline"
    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "build_kind": build_kind,
        "build_id": f"{build_kind}-{now_iso()}",
        "created_at": now_iso(),
        "source_commit": None,
        "groups": groups,
        "group_count": len(groups),
        "block_count": sum(len(group["blocks"]) for group in groups),
    }
    review_map = _build_map(groups, duplicates, mirrors)
    coverage = _build_coverage(groups, duplicates, mirrors, low_confidence)
    stored_ambiguities = read_json(AMBIGUITIES_PATH, empty_ambiguities())
    ambiguities = {
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "items": list(stored_ambiguities.get("items", []) or []),
    }
    return snapshot, review_map, coverage, ambiguities


def ensure_prompt_review_baseline() -> dict[str, Any]:
    ensure_prompt_review_dirs()
    existing = read_json(BASELINE_PATH, {})
    if existing:
        if not MAP_PATH.exists() or not COVERAGE_PATH.exists():
            _, review_map, coverage, ambiguities = compile_prompt_review_snapshot(regenerated=False)
            write_json(MAP_PATH, review_map)
            write_json(COVERAGE_PATH, coverage)
            if not AMBIGUITIES_PATH.exists():
                write_json(AMBIGUITIES_PATH, ambiguities)
        if not ACTIVE_CONFLICT_PATH.exists():
            write_json(ACTIVE_CONFLICT_PATH, empty_conflict_state())
        return existing
    snapshot, review_map, coverage, ambiguities = compile_prompt_review_snapshot(regenerated=False)
    write_json(BASELINE_PATH, snapshot)
    write_json(MAP_PATH, review_map)
    write_json(COVERAGE_PATH, coverage)
    if not AMBIGUITIES_PATH.exists():
        write_json(AMBIGUITIES_PATH, ambiguities)
    if not ACTIVE_CONFLICT_PATH.exists():
        write_json(ACTIVE_CONFLICT_PATH, empty_conflict_state())
    return snapshot


def regenerate_prompt_review() -> dict[str, Any]:
    ensure_prompt_review_dirs()
    ensure_prompt_review_baseline()
    snapshot, review_map, coverage, ambiguities = compile_prompt_review_snapshot(regenerated=True)
    write_json(REGENERATED_PATH, snapshot)
    write_json(MAP_PATH, review_map)
    write_json(COVERAGE_PATH, coverage)
    if not AMBIGUITIES_PATH.exists():
        write_json(AMBIGUITIES_PATH, ambiguities)
    return {
        "ok": True,
        "regenerated_path": str(REGENERATED_PATH),
        "map_path": str(MAP_PATH),
        "coverage_path": str(COVERAGE_PATH),
        "group_count": len(snapshot.get("groups", [])),
    }


def prompt_review_file_manifest() -> dict[str, str]:
    return {
        "root": str(PROMPT_REVIEW_DIR),
        "baseline": str(BASELINE_PATH),
        "edited": str(EDITED_PATH),
        "regenerated": str(REGENERATED_PATH),
        "map": str(MAP_PATH),
        "coverage": str(COVERAGE_PATH),
        "ambiguities": str(AMBIGUITIES_PATH),
        "active_conflict": str(ACTIVE_CONFLICT_PATH),
    }
