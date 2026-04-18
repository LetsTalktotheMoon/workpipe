from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from core.prompt_builder import (
    CANONICAL_OUTPUT_TEMPLATE,
    FORMAT_CONSTRAINTS,
    MASTER_WRITER_SYSTEM,
    UNIFIED_REVIEWER_SYSTEM,
    TIKTOK_IMMUTABLE_LINE,
    DIDI_IMMUTABLE_LINE,
    TEMU_IMMUTABLE_LINE,
    build_candidate_context,
    build_master_writer_prompt,
    build_seed_retarget_prompt,
    build_unified_review_prompt,
    build_upgrade_revision_prompt,
)
from config.candidate_framework import is_bytedance_target_company
from writers.master_writer import (
    STRICT_REVISION_SYSTEM_PROMPT,
    UPGRADE_REVISION_SYSTEM_PROMPT,
)


OVERRIDE_PATH = ROOT / "match_pipe" / "prompt_overrides.json"
NON_OVERRIDEABLE_BLOCKS: set[str] = set()


@dataclass(frozen=True)
class PromptTarget:
    pipeline: str
    stage: str
    role: str
    label: str
    path: str
    line: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "pipeline": self.pipeline,
            "stage": self.stage,
            "role": self.role,
            "label": self.label,
            "path": self.path,
            "line": self.line,
        }


@dataclass(frozen=True)
class PromptBlock:
    block_id: str
    title: str
    kind: str
    text: str
    targets: tuple[PromptTarget, ...]
    source_kind: str = "default"
    source_note: str = ""
    editor_visibility: str = "main"
    content_role: str = "natural_language"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.block_id,
            "title": self.title,
            "kind": self.kind,
            "text": self.text,
            "targets": [item.to_dict() for item in self.targets],
            "shared": len(self.targets) > 1,
            "source_kind": self.source_kind,
            "source_note": self.source_note,
            "editor_visibility": self.editor_visibility,
            "content_role": self.content_role,
            "source_ref": {
                "block_id": self.block_id,
                "source_kind": self.source_kind,
                "editor_visibility": self.editor_visibility,
                "content_role": self.content_role,
            },
            "target_refs": [item.to_dict() for item in self.targets],
        }


@dataclass(frozen=True)
class PromptView:
    prompt_id: str
    title: str
    pipeline: str
    stage: str
    role: str
    description: str
    block_ids: tuple[str, ...]
    targets: tuple[PromptTarget, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.prompt_id,
            "title": self.title,
            "pipeline": self.pipeline,
            "stage": self.stage,
            "role": self.role,
            "description": self.description,
            "block_ids": list(self.block_ids),
            "targets": [item.to_dict() for item in self.targets],
        }


@dataclass(frozen=True)
class EditorCardSpec:
    card_id: str
    title: str
    block_ids: tuple[str, ...]
    description: str = ""


@dataclass(frozen=True)
class EditorParagraphWriteRef:
    block_id: str
    block_title: str
    paragraph_index: int
    branch_kind: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "block_id": self.block_id,
            "block_title": self.block_title,
            "paragraph_index": self.paragraph_index,
            "branch_kind": self.branch_kind,
        }


@dataclass(frozen=True)
class EditorParagraph:
    paragraph_id: str
    card_id: str
    text: str
    write_refs: tuple[EditorParagraphWriteRef, ...]
    prompt_ids: tuple[str, ...]
    prompt_targets: tuple[PromptTarget, ...]
    stages: tuple[str, ...]
    branch_kind: str
    mapping_kind: str
    merge_strategy: str = "exact_paragraph_diff_hash"
    unit: str = "paragraph"
    merged_card_ids: tuple[str, ...] = ()
    display_owner_merged_card_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.paragraph_id,
            "card_id": self.card_id,
            "text": self.text,
            "unit": self.unit,
            "mapping_kind": self.mapping_kind,
            "merge_strategy": self.merge_strategy,
            "write_refs": [item.to_dict() for item in self.write_refs],
            "prompt_ids": list(self.prompt_ids),
            "prompt_targets": [item.to_dict() for item in self.prompt_targets],
            "stages": list(self.stages),
            "branch_kind": self.branch_kind,
            "merged_card_ids": list(self.merged_card_ids),
            "display_owner_merged_card_id": self.display_owner_merged_card_id,
        }


@dataclass(frozen=True)
class EditorBlockSegment:
    kind: str
    text: str
    paragraph_id: str | None = None
    hidden_reason: str = ""
    raw_index: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "text": self.text,
            "paragraph_id": self.paragraph_id,
            "hidden_reason": self.hidden_reason,
            "raw_index": self.raw_index,
        }


@dataclass(frozen=True)
class EditorCard:
    card_id: str
    title: str
    description: str
    block_ids: tuple[str, ...]
    prompt_ids: tuple[str, ...]
    paragraph_ids: tuple[str, ...]
    targets: tuple[PromptTarget, ...]
    blockers: tuple[str, ...] = ()
    merged_card_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.card_id,
            "title": self.title,
            "description": self.description,
            "block_ids": list(self.block_ids),
            "prompt_ids": list(self.prompt_ids),
            "paragraph_ids": list(self.paragraph_ids),
            "diff_block_ids": list(self.paragraph_ids),
            "targets": [item.to_dict() for item in self.targets],
            "blockers": list(self.blockers),
            "merged_card_ids": list(self.merged_card_ids),
        }


@dataclass(frozen=True)
class EditorMergedCard:
    merged_card_id: str
    pipeline: str
    stage: str
    role: str
    title: str
    member_card_ids: tuple[str, ...]
    diff_block_ids: tuple[str, ...]
    display_diff_block_ids: tuple[str, ...]
    prompt_ids: tuple[str, ...]
    targets: tuple[PromptTarget, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.merged_card_id,
            "pipeline": self.pipeline,
            "stage": self.stage,
            "role": self.role,
            "title": self.title,
            "member_card_ids": list(self.member_card_ids),
            "diff_block_ids": list(self.display_diff_block_ids),
            "all_diff_block_ids": list(self.diff_block_ids),
            "display_diff_block_ids": list(self.display_diff_block_ids),
            "prompt_ids": list(self.prompt_ids),
            "targets": [item.to_dict() for item in self.targets],
        }


EDITOR_CARD_SPECS: tuple[EditorCardSpec, ...] = (
    EditorCardSpec(
        "card_candidate_context",
        "候选人经历框架",
        (
            "candidate_context_shared_experience",
            "candidate_context_generic_tiktok_branch",
            "candidate_context_shared_education",
            "candidate_context_bytedance_education_branch",
            "candidate_context_shared_achievements",
            "candidate_context_bytedance_boundary",
        ),
        "共享经历主干与 ByteDance/TikTok 分支。",
    ),
    EditorCardSpec("card_writer_system", "Writer System Prompt", ("writer_system",)),
    EditorCardSpec("card_strict_revision_system", "Strict Revision System Prompt", ("strict_revision_system",)),
    EditorCardSpec("card_upgrade_revision_system", "Upgrade Revision System Prompt", ("upgrade_revision_system",)),
    EditorCardSpec("card_writer_jd_context", "Writer Prompt: 目标 JD 信息", ("writer_jd_context", "writer_jd_context_bytedance")),
    EditorCardSpec(
        "card_writer_user_header",
        "Writer User Prompt: JD 头部与 PLAN/RESUME 骨架",
        (
            "writer_plan_shared_intro",
            "writer_plan_generic_tiktok_branch",
            "writer_plan_shared_didi_temu",
            "writer_plan_shared_gt_coursework",
            "writer_plan_shared_tail",
        ),
        "共享经历主干、共享 GT coursework/projects 与 TikTok 分支。",
    ),
    EditorCardSpec(
        "card_format_constraints",
        "格式硬约束与 SKILLS 一致性规则",
        (
            "format_constraints_shared_head",
            "format_constraints_branch",
            "format_constraints_branch_bytedance",
            "format_constraints_shared_mid",
            "format_constraints_shared_tail",
        ),
    ),
    EditorCardSpec("card_output_contract", "统一输出合同", ("output_contract",)),
    EditorCardSpec("card_reviewer_system", "Reviewer System Prompt", ("reviewer_system",)),
    EditorCardSpec("card_reviewer_context", "Reviewer Prompt: JD 与待审查简历输入", ("reviewer_context", "reviewer_context_bytedance")),
    EditorCardSpec("card_reviewer_user", "Reviewer User Prompt", ("reviewer_user", "reviewer_user_bytedance"), "共享 reviewer 主干与 ByteDance 分支句。"),
    EditorCardSpec("card_retarget_prompt", "Retarget Prompt", ("retarget_prompt",)),
    EditorCardSpec("card_retarget_project_pool", "Retarget Prompt: 公司项目池约束", ("retarget_project_pool",)),
    EditorCardSpec("card_retarget_same_company", "Retarget Prompt: 同公司一致性分支", ("retarget_same_company", "retarget_same_company_bytedance")),
    EditorCardSpec("card_retarget_bytedance_special", "Retarget Prompt: ByteDance 特殊块", ("retarget_bytedance_special",)),
    EditorCardSpec("card_upgrade_prompt", "Upgrade Revision Prompt", ("upgrade_prompt",)),
    EditorCardSpec("card_upgrade_bytedance_special", "Upgrade Prompt: ByteDance 特殊块", ("upgrade_bytedance_special",)),
    EditorCardSpec("card_planner_system", "Planner System Prompt", ("planner_system",)),
    EditorCardSpec("card_planner_user", "Planner User Prompt", ("planner_user",)),
    EditorCardSpec("card_planner_writer_overlay", "Planner Writer Overlay", ("planner_writer_overlay",)),
    EditorCardSpec("card_planner_revision_overlay", "Planner Revision Overlay", ("planner_revision_overlay",)),
    EditorCardSpec("card_dual_channel_overlay", "Dual-channel Continuity Overlay", ("dual_channel_overlay",)),
)

EDITOR_CARD_BLOCKERS: dict[str, tuple[str, ...]] = {
    "card_candidate_context": (
        "当前已拆为共享经历/教育/成就主干 + TikTok/ByteDance 分支，但仍是段级，不是句级。",
    ),
    "card_writer_user_header": (
        "Writer PLAN/RESUME 已拆到共享段 + TikTok/GT 分支；如需进一步减少重复，需要继续细化到句级。",
    ),
    "card_format_constraints": (
        "格式约束已拆成共享头/中/尾 + generic/ByteDance 分支；如需进一步减少重复，需要继续细化到句级。",
    ),
}

SHELL_ONLY_LABELS = {
    "输出格式",
    "目标 JD",
    "目标 JD 关键信息",
    "目标 JD 信息",
    "待审查简历",
    "原始简历",
    "Seed 简历",
    "必须技术栈（SKILLS 中至少覆盖所有 JD 必须项，且必须有正文出处）",
    "加分技术栈（合理选择即可，不必全部包含）",
    "OR 组（满足其一即可）",
    "软性要求",
    "审查发现",
    "最优先修改事项",
    "原审查详细修改指令",
    "必须技术",
    "审查维度与权重",
    "Matcher Packet",
    "Starter Resume",
    "Planner 输入",
    "Planner-first Revision Context",
    "Planner Carry-over",
    "Planner Risks",
    "Reviewer Priority",
    "Reviewer Findings",
    "Must-have Tech",
    "Existing Resume Draft To Revise",
    "Historical Starter Resume",
    "Planner Decision",
    "Matcher Evidence",
}

NON_EDITABLE_CONTENT_ROLES = {"schema", "compat_alias", "context_template", "source_fragment"}
PARAGRAPH_OVERRIDE_SCOPE = "match_pipe_editor_paragraphs"
PLACEHOLDER_RE = re.compile(r"\{[a-zA-Z0-9_]+\}")
LEGACY_OVERRIDE_BLOCK_ALIASES: dict[str, str] = {
    "writer_plan_bytedance_gt_branch": "writer_plan_shared_gt_coursework",
}


def _dedupe_prompt_targets(items: list[PromptTarget]) -> tuple[PromptTarget, ...]:
    seen: set[tuple[str, str, str, str, str, int]] = set()
    ordered: list[PromptTarget] = []
    for item in items:
        key = (item.pipeline, item.stage, item.role, item.label, item.path, item.line)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(item)
    return tuple(ordered)


def _target(pipeline: str, stage: str, role: str, label: str, path: str, line: int) -> PromptTarget:
    return PromptTarget(
        pipeline=pipeline,
        stage=stage,
        role=role,
        label=label,
        path=path,
        line=line,
    )


def _placeholder_jd(company: str = "ExampleCorp") -> SimpleNamespace:
    return SimpleNamespace(
        company=company,
        title="{title}",
        role_type="{role_type}",
        seniority="{seniority}",
        team_direction="{team_direction}",
        tech_required=["{tech_required}"],
        tech_preferred=["{tech_preferred}"],
        tech_or_groups=[["{or_group}"]],
        soft_required=["{soft_required}"],
    )


def _master_writer_source_blocks(company: str = "ExampleCorp") -> tuple[str, str]:
    jd = _placeholder_jd(company)
    prompt = build_master_writer_prompt(jd)
    _, after_header = prompt.split("## 目标 JD 信息\n", 1)
    jd_context, after_jd = after_header.split("\n---\n\n", 1)
    _, after_constraints = after_jd.split("\n---\n\n", 1)
    writer_body, _ = after_constraints.rsplit(f"\n\n{CANONICAL_OUTPUT_TEMPLATE}", 1)
    return f"## 目标 JD 信息\n{jd_context.strip()}", writer_body.strip()


def _reviewer_source_blocks(company: str = "ExampleCorp") -> tuple[str, str]:
    jd = _placeholder_jd(company)
    prompt = build_unified_review_prompt("{resume_md}", jd, review_scope="{review_scope}")
    intro, after_header = prompt.split("## 目标 JD\n\n", 1)
    context, after_context = after_header.split("\n\n---\n\n", 1)
    return f"## 目标 JD\n\n{context.strip()}", f"{intro.strip()}\n\n{after_context.strip()}"


def _placeholder_review_result() -> dict[str, Any]:
    return {
        "revision_priority": ["{priority}"],
        "scores": {
            "r0": {
                "findings": [
                    {
                        "severity": "high",
                        "field": "{field}",
                        "issue": "{issue}",
                        "fix": "{fix}",
                    }
                ]
            }
        },
        "weighted_score": 91.5,
        "revision_instructions": "{revision_instructions}",
    }


def _placeholder_top_candidate(company: str, *, same_company: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "missing_required": ["{missing_required}"],
        "label": "{seed_label}",
        "project_ids": [],
    }
    if same_company:
        payload.update(
            {
                "same_company": True,
                "seed_company_name": company,
                "company_anchor": True,
            }
        )
    return payload


def _extract_seed_retarget_prompt(company: str, *, same_company: bool = False) -> str:
    jd = _placeholder_jd(company)
    prompt = build_seed_retarget_prompt(
        "{seed_resume_md}",
        jd,
        seed_label="{seed_label}",
        route_mode="retarget",
        top_candidate=_placeholder_top_candidate(company, same_company=same_company),
    )
    prompt, _ = prompt.rsplit(f"\n\n{CANONICAL_OUTPUT_TEMPLATE}", 1)
    return prompt.strip()


def _extract_upgrade_prompt(company: str) -> str:
    prompt = build_upgrade_revision_prompt(
        "{resume_md}",
        _placeholder_review_result(),
        tech_required=["{tech_required}"],
        jd_title="{jd_title}",
        target_company=company,
        route_mode="{route_mode}",
        seed_label="{seed_label}",
    )
    prompt, _ = prompt.rsplit(f"\n\n{CANONICAL_OUTPUT_TEMPLATE}", 1)
    return prompt.strip()


def _extract_optional_section(text: str, heading: str) -> tuple[str, str]:
    marker = f"\n\n{heading}\n"
    if marker not in text:
        return text, ""
    before, after = text.split(marker, 1)
    next_section = after.find("\n\n## ")
    if next_section == -1:
        section_body = after.strip()
        remaining = before.strip()
    else:
        section_body = after[:next_section].strip()
        remaining = f"{before}{after[next_section:]}".strip()
    return remaining, f"{heading}\n{section_body}".strip()


def _extract_seed_retarget_blocks(company: str, *, same_company: bool = False) -> dict[str, str]:
    prompt = _extract_seed_retarget_prompt(company, same_company=same_company)
    before_seed, seed_tail = prompt.split("\n\n## Seed 简历\n", 1)
    project_prefix = "## 经验公司项目池（硬约束）"
    before_pool, project_pool = before_seed.split(f"\n\n{project_prefix}\n", 1)
    project_pool_block = f"{project_prefix}\n{project_pool.strip()}".strip()
    remaining = before_pool.strip()
    remaining, bytedance_special = _extract_optional_section(remaining, "## ByteDance 目标公司特殊模式")
    remaining, same_company_bytedance = _extract_optional_section(remaining, "## ByteDance seed 参考模式（覆盖同公司微调规则）")
    remaining, same_company_generic = _extract_optional_section(remaining, "## 同公司一致性模式（最高优先级）")
    return {
        "prompt": remaining.strip(),
        "seed_context": f"## Seed 简历\n{seed_tail.strip()}".strip(),
        "project_pool": project_pool_block,
        "bytedance_special": bytedance_special,
        "same_company_bytedance": same_company_bytedance,
        "same_company_generic": same_company_generic,
    }


def _extract_upgrade_blocks(company: str) -> dict[str, str]:
    prompt = _extract_upgrade_prompt(company)
    before_resume, resume_tail = prompt.split("\n\n## 原始简历\n", 1)
    remaining = before_resume.strip()
    remaining, bytedance_special = _extract_optional_section(remaining, "## ByteDance 特殊要求")
    return {
        "prompt": remaining.strip(),
        "resume_context": f"## 原始简历\n{resume_tail.strip()}".strip(),
        "bytedance_special": bytedance_special,
    }


def _extract_master_writer_target_company_block(company: str) -> str:
    prompt = build_master_writer_prompt(_placeholder_jd(company))
    prefix = build_candidate_context(company).strip()
    if not prompt.startswith(prefix):
        return ""
    tail = prompt[len(prefix):].lstrip()
    if tail.startswith("## 目标 JD 信息\n"):
        return ""
    special, _ = tail.split("## 目标 JD 信息\n", 1)
    return special.strip()


def _is_bytedance_company(company: str) -> bool:
    return bool(company and is_bytedance_target_company(company))


GENERIC_EXPERIENCE_ORDER = "TikTok（2025）→ DiDi（2022-2024）→ Temu（2021-2022）"
BYTEDANCE_EXPERIENCE_ORDER = "DiDi（2022-2024）→ Temu（2021-2022）"


def _planner_system_text() -> str:
    return (
        "你是简历流程里的 Planner。你的职责不是直接写简历，而是基于 JD、matcher 证据和可选历史简历 starter，判断："
        "这份 starter 是否适合作为起点；是否可以直接送 Reviewer；如果需要写作，哪些内容已覆盖、哪些缺失、哪些存在真实性/ownership/scope 风险；"
        "Writer 应如何改写，优先级如何排序。\n\n"
        "必须输出 JSON，不要输出解释性文字。不要复述 schema。"
    )


def _planner_user_text() -> str:
    return (
        "请作为 Planner，基于以下信息做流程决策：目标模式、目标 JD、Matcher Packet、Starter Resume。\n\n"
        "返回 JSON，schema 必须包含 decision、fit_label、reuse_ratio_estimate、already_covered、missing_or_weak、risk_flags、role_seniority_guidance、"
        "planner_summary、writer_plan、direct_review_rationale。\n\n"
        "规则：no_starter 模式下 decision 只能是 write；starter 高度贴合且 scope/真实性风险低时可以 direct_review；"
        "starter 语义相近但仍需改写时选择 write；starter 虽相似但会明显误导 summary、ownership、项目骨架或 scope 时选择 reject_starter；"
        "不要把 matcher 的相似度直接等同于可写作适配度。"
    )


def _planner_context_template() -> str:
    return (
        "## Planner 输入\n"
        "- 目标模式: {mode}\n"
        "- 公司: {company}\n"
        "- 职位: {title}\n"
        "- role_type: {role_type}\n"
        "- seniority: {seniority}\n"
        "- must-have 技术: {tech_required}\n"
        "- preferred 技术: {tech_preferred}\n\n"
        "## Matcher Packet\n"
        "```json\n"
        "{matcher_block}\n"
        "```\n\n"
        "## Starter Resume\n"
        "```md\n"
        "{starter_block}\n"
        "```"
    )


def _planner_writer_overlay_text() -> str:
    return (
        "Planner-first Rules：如果给了 starter resume，把它视为可复用参考骨架，而不是必须保留的模板；"
        "优先遵循 planner 对 coverage、missing、risk、role-seniority framing 的判断；"
        "如果 planner 指出了 scope 或真实性风险，必须主动改写 summary、ownership 和项目 framing；"
        "如果 planner 认为 starter 可高比例复用，可保留高价值证据，但仍以目标 JD 为准。"
    )


def _planner_writer_context_template() -> str:
    return (
        "## Planner Decision\n"
        "```json\n"
        "{planner_json}\n"
        "```\n\n"
        "## Matcher Evidence\n"
        "```json\n"
        "{matcher_json}\n"
        "```\n\n"
        "## Historical Starter Resume\n"
        "```md\n"
        "{starter_block}\n"
        "```"
    )


def _planner_revision_overlay_text() -> str:
    return (
        "Revision Rules：不要保留任何只是因为旧稿已经存在、但不再服务目标 JD 的 summary framing、ownership framing 或 bullet 结构；"
        "如果 planner 指出了 starter 的 scope、真实性、角色定位或 seniority 风险，必须优先修正；"
        "如果 reviewer 指出了 JD 缺口，优先补正文证据，而不是删除 must-have 技术；"
        "允许重写 summary、skills 分组、bullet 取舍、project baseline 和经历 framing，但不得破坏不可变字段与职业主线真实性；输出完整简历 Markdown，不要解释。"
    )


def _planner_revision_context_template() -> str:
    return (
        "## Planner-first Revision Context\n"
        "- 当前版本评分: {weighted_score}/100\n"
        "- 当前是否通过: {passed}\n"
        "- 当前 reviewer 是否要求继续修改: {needs_revision}\n\n"
        "## Planner Carry-over\n"
        "{planner_notes}\n\n"
        "## Planner Risks\n"
        "{risk_notes}\n\n"
        "## Reviewer Priority\n"
        "{priority}\n\n"
        "## Reviewer Findings\n"
        "{findings_block}\n\n"
        "## Must-have Tech\n"
        "- {must_have}\n\n"
        "## Existing Resume Draft To Revise\n"
        "```md\n"
        "{current_resume_md}\n"
        "```"
    )


def _dual_channel_overlay_template_text() -> str:
    return (
        "## Dual-channel continuity note\n"
        "- {{delta_summary_item}}\n"
        "- {{continuity_anchor_if_available}}\n"
        "- Use semantic anchor as the main skeleton. Apply company continuity only when it does not reintroduce hard gaps."
    )


def _render_dual_channel_overlay(
    *,
    delta_summary: list[str] | None = None,
    continuity_anchor: dict[str, Any] | None = None,
) -> str:
    lines = ["## Dual-channel continuity note"]
    for line in delta_summary or []:
        lines.append(f"- {line}")
    if continuity_anchor:
        lines.append(
            f"- Continuity anchor: {continuity_anchor.get('company_name', '')} / {continuity_anchor.get('title', '')} "
            f"(reuse_readiness={float(continuity_anchor.get('reuse_readiness', 0.0) or 0.0):.2f})."
        )
    lines.append("- Use semantic anchor as the main skeleton. Apply company continuity only when it does not reintroduce hard gaps.")
    return "\n".join(lines)


def _experience_order_for_company(company: str) -> str:
    return BYTEDANCE_EXPERIENCE_ORDER if _is_bytedance_company(company) else GENERIC_EXPERIENCE_ORDER


def _immutable_block_for_company(company: str) -> str:
    if _is_bytedance_company(company):
        return "\n".join(
            [
                DIDI_IMMUTABLE_LINE,
                TEMU_IMMUTABLE_LINE,
                "- TikTok / ByteDance intern experience must be absent for ByteDance target roles.",
            ]
        )
    return "\n".join([TIKTOK_IMMUTABLE_LINE, DIDI_IMMUTABLE_LINE, TEMU_IMMUTABLE_LINE])


def _writer_jd_context_template(text: str) -> str:
    return text.replace("ExampleCorp", "{company}")


def _reviewer_context_template(text: str) -> str:
    marker = "不可变字段（必须与此完全一致）:\n"
    prefix, _ = text.split(marker, 1)
    return prefix.replace("ExampleCorp", "{company}") + marker + "{immutable_block}"


def _reviewer_user_template(text: str) -> str:
    return (
        text.replace(
            "- TikTok 职称必须为 `Software Engineer Intern`，出现 `Backend Development Engineer Intern` 或任何其他变体 = CRITICAL",
            "- {r0_tiktok_rule}",
        )
        .replace(
            '  - TikTok 职称是否为 `Software Engineer Intern`（不得含 "Backend Development"）？违反 = critical',
            "  - {r1_tiktok_rule}",
        )
        .replace(
            "- TikTok intern 是否使用了过于高级的动词（Led/Architected/Drove）？",
            "- {r3_tiktok_rule}",
        )
        .replace(
            f"- Experience 顺序是否严格倒序（{GENERIC_EXPERIENCE_ORDER}）？",
            "- Experience 顺序是否严格倒序（{experience_order}）？",
        )
    )


def _split_reviewer_user_schema(text: str) -> tuple[str, str]:
    marker = "\n\n## 输出格式\n\n"
    before, after = text.split(marker, 1)
    return before.strip(), f"## 输出格式\n\n{after.strip()}"


def _reviewer_user_dynamic_values(company: str) -> dict[str, str]:
    if _is_bytedance_company(company):
        return {
            "r0_tiktok_rule": "TikTok / ByteDance intern 这段经历如果出现 = CRITICAL（ByteDance 目标岗位必须完全删掉）",
            "r1_tiktok_rule": "是否出现任何 TikTok / ByteDance intern 段落？若出现 = critical",
            "r3_tiktok_rule": "是否错误地重新引入了 ByteDance / TikTok intern，以规避工作经历和课程项目证据不足？",
            "experience_order": BYTEDANCE_EXPERIENCE_ORDER,
        }
    return {
        "r0_tiktok_rule": "TikTok 职称必须为 `Software Engineer Intern`，出现 `Backend Development Engineer Intern` 或任何其他变体 = CRITICAL",
        "r1_tiktok_rule": 'TikTok 职称是否为 `Software Engineer Intern`（不得含 "Backend Development"）？违反 = critical',
        "r3_tiktok_rule": "TikTok intern 是否使用了过于高级的动词（Led/Architected/Drove）？",
        "experience_order": GENERIC_EXPERIENCE_ORDER,
    }


def _reviewer_user_shared_and_schema(text: str) -> tuple[str, str]:
    templated_text = _reviewer_user_template(text)
    body_text, schema_text = _split_reviewer_user_schema(templated_text)
    return body_text.format(**_reviewer_user_dynamic_values("ExampleCorp")), schema_text


def _reviewer_user_bytedance_branch_text() -> str:
    values = _reviewer_user_dynamic_values("ByteDance")
    return "\n".join(
        [
            "R0: " + values["r0_tiktok_rule"],
            "R1: " + values["r1_tiktok_rule"],
            "R3: " + values["r3_tiktok_rule"],
            "R5: Experience 顺序是否严格倒序（" + values["experience_order"] + "）？",
        ]
    )


def _parse_reviewer_branch_text(text: str) -> dict[str, str]:
    replacements: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().upper()
        value = value.strip()
        if key in {"R0", "R1", "R3", "R5"} and value:
            replacements[key] = value
    return replacements


def _apply_reviewer_bytedance_branch(shared_text: str, branch_text: str) -> str:
    replacements = _parse_reviewer_branch_text(branch_text)
    generic = _reviewer_user_dynamic_values("ExampleCorp")
    fallback = _reviewer_user_dynamic_values("ByteDance")
    resolved = {
        "R0": replacements.get("R0", fallback["r0_tiktok_rule"]),
        "R1": replacements.get("R1", fallback["r1_tiktok_rule"]),
        "R3": replacements.get("R3", fallback["r3_tiktok_rule"]),
        "R5": replacements.get("R5", f"Experience 顺序是否严格倒序（{fallback['experience_order']}）？"),
    }
    updated = shared_text
    updated = updated.replace(f"- {generic['r0_tiktok_rule']}", f"- {resolved['R0']}")
    updated = updated.replace(f"  - {generic['r1_tiktok_rule']}", f"  - {resolved['R1']}")
    updated = updated.replace(f"- {generic['r3_tiktok_rule']}", f"- {resolved['R3']}")
    updated = updated.replace(
        f"- Experience 顺序是否严格倒序（{GENERIC_EXPERIENCE_ORDER}）？",
        f"- {resolved['R5']}",
    )
    return updated


def _retarget_prompt_template(text: str) -> str:
    return (
        text.replace("目标岗位: {title} @ ExampleCorp", "目标岗位: {title} @ {company}")
        .replace(GENERIC_EXPERIENCE_ORDER, "{experience_order}")
    )


def _upgrade_prompt_template(text: str) -> str:
    return text.replace(GENERIC_EXPERIENCE_ORDER, "{experience_order}")


def _split_candidate_context_fragments(generic_text: str, bytedance_text: str) -> dict[str, str]:
    marker_tiktok = "\n### TikTok — Software Engineer Intern (不可变)\n"
    marker_education = "\n### 教育经历（可根据 JD 方向选择列哪些）\n"
    marker_achievements = "\n\n### 成就（融入 Summary 第3句）\n"
    marker_bytedance_boundary = "\n\n### ByteDance 特殊写作边界\n"

    shared_experience, generic_after = generic_text.split(marker_tiktok, 1)
    generic_tiktok_body, generic_tail = generic_after.split(marker_education, 1)
    _, bytedance_tail = bytedance_text.split(marker_education, 1)

    generic_education, generic_after_education = generic_tail.split(marker_achievements, 1)
    bytedance_education, bytedance_after_education = bytedance_tail.split(marker_achievements, 1)
    shared_achievements_body, bytedance_boundary_body = bytedance_after_education.split(marker_bytedance_boundary, 1)

    shared_education_lines = generic_education.strip().splitlines()
    bytedance_education_lines = bytedance_education.strip().splitlines()
    bytedance_education_branch_lines = [line for line in bytedance_education_lines if line not in shared_education_lines]

    return {
        "shared_experience": shared_experience.strip(),
        "generic_tiktok": f"### TikTok — Software Engineer Intern (不可变)\n{generic_tiktok_body.strip()}".strip(),
        "shared_education": f"### 教育经历（可根据 JD 方向选择列哪些）\n{generic_education.strip()}".strip(),
        "bytedance_education_branch": "\n".join(bytedance_education_branch_lines).strip(),
        "shared_achievements": f"### 成就（融入 Summary 第3句）\n{shared_achievements_body.strip()}".strip(),
        "bytedance_boundary": f"### ByteDance 特殊写作边界\n{bytedance_boundary_body.strip()}".strip(),
    }


def _split_writer_plan_fragments(generic_text: str, bytedance_text: str) -> dict[str, str]:
    marker_tiktok = "\n### TikTok（intern，最灵活，承接 JD 核心技术）\n"
    marker_didi = "\n### DiDi（mid-senior acting lead，转行桥梁，连接分析和工程）\n"
    marker_gt = "\n### Georgia Tech CS coursework/projects（所有线路共享；ByteDance 可提升权重）\n"
    marker_skills = "\n## SKILLS 推导（= 上述经历/项目技术列表的并集）\n"

    shared_intro, generic_after = generic_text.split(marker_tiktok, 1)
    generic_tiktok_body, generic_after_tiktok = generic_after.split(marker_didi, 1)
    shared_didi_temu_body, generic_gt_and_tail = generic_after_tiktok.split(marker_gt, 1)
    gt_body, shared_tail = generic_gt_and_tail.split(marker_skills, 1)

    return {
        "shared_intro": shared_intro.strip(),
        "generic_tiktok": f"### TikTok（intern，最灵活，承接 JD 核心技术）\n{generic_tiktok_body.strip()}".strip(),
        "shared_didi_temu": f"### DiDi（mid-senior acting lead，转行桥梁，连接分析和工程）\n{shared_didi_temu_body.strip()}".strip(),
        "shared_gt": f"### Georgia Tech CS coursework/projects（所有线路共享；ByteDance 可提升权重）\n{gt_body.strip()}".strip(),
        "shared_tail": f"## SKILLS 推导（= 上述经历/项目技术列表的并集）\n{shared_tail.strip()}".strip(),
    }


def _split_format_constraint_fragments(generic_text: str, bytedance_text: str) -> dict[str, str]:
    generic_lines = generic_text.splitlines()
    bytedance_lines = bytedance_text.splitlines()

    order_idx = next(i for i, line in enumerate(generic_lines) if line.startswith("- Experience 顺序:"))
    immutable_idx = generic_lines.index("**不可变字段（绝不可修改）**")
    scope_idx = generic_lines.index("**职级 Scope 规则**")
    digits_idx = generic_lines.index("**数字合理性规则（违反 = r4 高风险）**")

    b_order_idx = next(i for i, line in enumerate(bytedance_lines) if line.startswith("- Experience 顺序:"))
    b_immutable_idx = bytedance_lines.index("**不可变字段（绝不可修改）**")
    b_scope_idx = bytedance_lines.index("**职级 Scope 规则**")
    b_digits_idx = bytedance_lines.index("**数字合理性规则（违反 = r4 高风险）**")

    return {
        "shared_head": "\n".join(generic_lines[:order_idx]).strip(),
        "generic_branch": "\n".join(
            [generic_lines[order_idx]]
            + generic_lines[immutable_idx:digits_idx]
        ).strip(),
        "bytedance_branch": "\n".join(
            [bytedance_lines[b_order_idx]]
            + bytedance_lines[b_immutable_idx:b_digits_idx]
        ).strip(),
        "shared_mid": "\n".join(generic_lines[order_idx + 1:immutable_idx]).strip(),
        "shared_tail": "\n".join(generic_lines[digits_idx:]).strip(),
    }


def _compose_candidate_context(company: str) -> str:
    shared_experience = get_match_pipe_block_text("candidate_context_shared_experience")
    shared_education = get_match_pipe_block_text("candidate_context_shared_education")
    shared_achievements = get_match_pipe_block_text("candidate_context_shared_achievements")
    parts = [shared_experience]
    if _is_bytedance_company(company):
        branch = get_match_pipe_block_text("candidate_context_bytedance_education_branch")
        if branch:
            shared_education = "\n".join([shared_education, branch]).strip()
    else:
        parts.append(get_match_pipe_block_text("candidate_context_generic_tiktok_branch"))
    parts.append(shared_education)
    parts.append(shared_achievements)
    if _is_bytedance_company(company):
        parts.append(get_match_pipe_block_text("candidate_context_bytedance_boundary"))
    return "\n\n".join(part for part in parts if part.strip())


def _compose_writer_user_header(company: str) -> str:
    parts = [
        get_match_pipe_block_text("writer_plan_shared_intro"),
    ]
    if not _is_bytedance_company(company):
        parts.append(get_match_pipe_block_text("writer_plan_generic_tiktok_branch"))
    parts.append(get_match_pipe_block_text("writer_plan_shared_didi_temu"))
    parts.append(get_match_pipe_block_text("writer_plan_shared_gt_coursework"))
    parts.append(get_match_pipe_block_text("writer_plan_shared_tail"))
    return "\n\n".join(part for part in parts if part.strip())


def _compose_format_constraints(company: str) -> str:
    parts = [
        get_match_pipe_block_text("format_constraints_shared_head"),
        _company_block_text("format_constraints_branch", company),
        get_match_pipe_block_text("format_constraints_shared_mid"),
        get_match_pipe_block_text("format_constraints_shared_tail"),
    ]
    return "\n\n".join(part for part in parts if part.strip())


def _writer_block_ids(company: str) -> tuple[str, ...]:
    block_ids = [
        "candidate_context_shared_experience",
    ]
    if _is_bytedance_company(company):
        block_ids.extend(
            [
                "candidate_context_shared_education",
                "candidate_context_bytedance_education_branch",
                "candidate_context_shared_achievements",
                "candidate_context_bytedance_boundary",
                "retarget_bytedance_special",
            ]
        )
    else:
        block_ids.extend(
            [
                "candidate_context_generic_tiktok_branch",
                "candidate_context_shared_education",
                "candidate_context_shared_achievements",
            ]
        )
    block_ids.append("writer_jd_context")
    block_ids.append("writer_plan_shared_intro")
    if not _is_bytedance_company(company):
        block_ids.append("writer_plan_generic_tiktok_branch")
    block_ids.append("writer_plan_shared_didi_temu")
    block_ids.append("writer_plan_shared_gt_coursework")
    block_ids.extend(
        [
            "writer_plan_shared_tail",
            "format_constraints_shared_head",
            "format_constraints_branch_bytedance" if _is_bytedance_company(company) else "format_constraints_branch",
            "format_constraints_shared_mid",
            "format_constraints_shared_tail",
            "output_contract",
        ]
    )
    return tuple(block_ids)


def _retarget_block_ids(company: str, *, include_dual: bool = False, include_same_company: bool = False) -> tuple[str, ...]:
    block_ids = ["retarget_prompt"]
    if _is_bytedance_company(company):
        block_ids.append("retarget_bytedance_special")
        if include_same_company:
            block_ids.append("retarget_same_company_bytedance")
    elif include_same_company:
        block_ids.append("retarget_same_company")
    block_ids.extend(["retarget_project_pool", "retarget_context"])
    if include_dual:
        block_ids.append("dual_channel_overlay")
    block_ids.extend(
        [
            "format_constraints_shared_head",
            "format_constraints_branch_bytedance" if _is_bytedance_company(company) else "format_constraints_branch",
            "format_constraints_shared_mid",
            "format_constraints_shared_tail",
            "output_contract",
        ]
    )
    return tuple(block_ids)


def _upgrade_block_ids(company: str) -> tuple[str, ...]:
    block_ids = ["upgrade_prompt"]
    if _is_bytedance_company(company):
        block_ids.append("upgrade_bytedance_special")
    block_ids.extend(
        [
            "upgrade_context",
            "format_constraints_shared_head",
            "format_constraints_branch_bytedance" if _is_bytedance_company(company) else "format_constraints_branch",
            "format_constraints_shared_mid",
            "format_constraints_shared_tail",
            "output_contract",
        ]
    )
    return tuple(block_ids)


def _default_blocks() -> list[PromptBlock]:
    writer_jd_context_text, writer_user_body_text = _master_writer_source_blocks()
    _, writer_user_body_bytedance_text = _master_writer_source_blocks("ByteDance")
    candidate_context_fragments = _split_candidate_context_fragments(
        build_candidate_context("").strip(),
        build_candidate_context("ByteDance").strip(),
    )
    writer_plan_fragments = _split_writer_plan_fragments(
        writer_user_body_text,
        writer_user_body_bytedance_text,
    )
    format_constraint_fragments = _split_format_constraint_fragments(
        FORMAT_CONSTRAINTS.strip(),
        build_master_writer_prompt(_placeholder_jd("ByteDance")).split("\n---\n\n", 1)[1].split("\n---\n\n", 1)[0].strip(),
    )
    reviewer_context_text, reviewer_user_text = _reviewer_source_blocks()
    reviewer_context_bytedance_text, _ = _reviewer_source_blocks("ByteDance")
    reviewer_user_body_text, reviewer_schema_text = _reviewer_user_shared_and_schema(reviewer_user_text)
    reviewer_user_bytedance_branch = _reviewer_user_bytedance_branch_text()
    retarget_generic = _extract_seed_retarget_blocks("ExampleCorp")
    retarget_generic_same_company = _extract_seed_retarget_blocks("ExampleCorp", same_company=True)
    retarget_bytedance = _extract_seed_retarget_blocks("ByteDance", same_company=True)
    upgrade_generic = _extract_upgrade_blocks("ExampleCorp")
    upgrade_bytedance = _extract_upgrade_blocks("ByteDance")
    return [
        PromptBlock(
            block_id="candidate_context",
            title="候选人经历框架",
            kind="compat_alias",
            text="",
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
            ),
            source_kind="compat_alias_hidden",
            source_note="旧整块 key 已降为隐藏兼容别名；真实数据源已拆为 candidate_context_shared_* + 分支块。",
            editor_visibility="hidden",
            content_role="compat_alias",
        ),
        PromptBlock(
            block_id="candidate_context_bytedance",
            title="候选人经历框架（ByteDance 分支）",
            kind="compat_alias",
            text="",
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
            ),
            source_kind="compat_alias_hidden",
            source_note="旧整块 ByteDance key 已降为隐藏兼容别名；真实数据源已拆为共享主干 + ByteDance 分支块。",
            editor_visibility="hidden",
            content_role="compat_alias",
        ),
        PromptBlock(
            block_id="candidate_context_shared_experience",
            title="候选人经历框架：共享经历主干",
            kind="shared_context",
            text=candidate_context_fragments["shared_experience"],
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
            ),
            source_kind="shared_trunk",
            source_note="候选人经历框架的共享经历主干，仅保留 Temu + DiDi 及总标题；TikTok 与 ByteDance 边界已拆成独立分支块。",
        ),
        PromptBlock(
            block_id="candidate_context_generic_tiktok_branch",
            title="候选人经历框架：TikTok 分支",
            kind="shared_context_variant",
            text=candidate_context_fragments["generic_tiktok"],
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
            ),
            source_kind="shared_variant_branch",
            source_note="通用目标岗位使用的 TikTok 经历分支；ByteDance 不再包含这段。",
            content_role="variant_branch",
        ),
        PromptBlock(
            block_id="candidate_context_shared_education",
            title="候选人经历框架：共享教育主干",
            kind="shared_context",
            text=candidate_context_fragments["shared_education"],
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
            ),
            source_kind="shared_trunk",
            source_note="候选人教育经历的共享主干；GT 教育本体对所有线路可用，ByteDance 仅对 GT coursework/projects 额外加权。",
        ),
        PromptBlock(
            block_id="candidate_context_bytedance_education_branch",
            title="候选人经历框架：ByteDance 教育加权说明",
            kind="shared_context_variant",
            text=candidate_context_fragments["bytedance_education_branch"],
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
            ),
            source_kind="shared_variant_branch",
            source_note="ByteDance 目标岗位对 Georgia Tech CS coursework/projects 的加权说明，不意味着 GT 教育主干只在 ByteDance 可用。",
            content_role="variant_branch",
        ),
        PromptBlock(
            block_id="candidate_context_shared_achievements",
            title="候选人经历框架：共享成就主干",
            kind="shared_context",
            text=candidate_context_fragments["shared_achievements"],
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
            ),
            source_kind="shared_trunk",
            source_note="候选人成就段的共享主干。",
        ),
        PromptBlock(
            block_id="candidate_context_bytedance_boundary",
            title="候选人经历框架：ByteDance 写作边界（GT 主干共享）",
            kind="shared_context_variant",
            text=candidate_context_fragments["bytedance_boundary"],
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
            ),
            source_kind="shared_variant_branch",
            source_note="ByteDance 特殊写作边界分支，明确禁止 TikTok / ByteDance intern；同时声明 GT 教育主干仍是共享材料。",
            content_role="variant_branch",
        ),
        PromptBlock(
            block_id="writer_system",
            title="Writer System Prompt",
            kind="system",
            text=MASTER_WRITER_SYSTEM.strip(),
            targets=(
                _target("match_pipe", "shared_writer", "writer", "match_pipe_writer_system_prompt", "runtime/job_webapp/prompt_library.py", 407),
            ),
            source_kind="stable_runtime_fragment",
            source_note="直接引用 core.prompt_builder.MASTER_WRITER_SYSTEM。",
        ),
        PromptBlock(
            block_id="strict_revision_system",
            title="Strict Revision System Prompt",
            kind="system",
            text=STRICT_REVISION_SYSTEM_PROMPT.strip(),
            targets=(
                _target("match_pipe", "revision", "writer", "match_pipe_strict_revision_system_prompt", "runtime/job_webapp/prompt_library.py", 411),
            ),
            source_kind="stable_runtime_fragment",
            source_note="直接引用 writers.master_writer.STRICT_REVISION_SYSTEM_PROMPT。",
        ),
        PromptBlock(
            block_id="upgrade_revision_system",
            title="Upgrade Revision System Prompt",
            kind="system",
            text=UPGRADE_REVISION_SYSTEM_PROMPT.strip(),
            targets=(
                _target("match_pipe", "revision", "writer", "match_pipe_upgrade_revision_system_prompt", "runtime/job_webapp/prompt_library.py", 415),
            ),
            source_kind="stable_runtime_fragment",
            source_note="直接引用 writers.master_writer.UPGRADE_REVISION_SYSTEM_PROMPT。",
        ),
        PromptBlock(
            block_id="writer_user_header",
            title="Writer User Prompt: JD 头部与 PLAN/RESUME 骨架",
            kind="compat_alias",
            text="",
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
            ),
            source_kind="compat_alias_hidden",
            source_note="旧整块 writer PLAN/RESUME 骨架已降为隐藏兼容别名；真实数据源已拆成共享主干 + 分支块。",
            editor_visibility="hidden",
            content_role="compat_alias",
        ),
        PromptBlock(
            block_id="writer_user_header_bytedance",
            title="Writer User Prompt: JD 头部与 PLAN/RESUME 骨架（ByteDance 分支）",
            kind="compat_alias",
            text="",
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
            ),
            source_kind="compat_alias_hidden",
            source_note="旧整块 ByteDance writer PLAN/RESUME 骨架已降为隐藏兼容别名；真实数据源已拆成共享主干 + 分支块。",
            editor_visibility="hidden",
            content_role="compat_alias",
        ),
        PromptBlock(
            block_id="writer_plan_shared_intro",
            title="Writer PLAN 骨架：共享开头",
            kind="user",
            text=writer_plan_fragments["shared_intro"],
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
            ),
            source_kind="shared_trunk",
            source_note="Writer PLAN/RESUME 骨架的共享开头；后续经历规划按 generic/ByteDance 分支拼接。",
        ),
        PromptBlock(
            block_id="writer_plan_generic_tiktok_branch",
            title="Writer PLAN 骨架：TikTok 分支",
            kind="user_variant_branch",
            text=writer_plan_fragments["generic_tiktok"],
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
            ),
            source_kind="shared_variant_branch",
            source_note="通用 writer PLAN 中的 TikTok 技术分配分支。",
            content_role="variant_branch",
        ),
        PromptBlock(
            block_id="writer_plan_shared_didi_temu",
            title="Writer PLAN 骨架：共享经历主体",
            kind="user",
            text=writer_plan_fragments["shared_didi_temu"],
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
            ),
            source_kind="shared_trunk",
            source_note="Writer PLAN 中 DiDi + Temu 的共享主体。",
        ),
        PromptBlock(
            block_id="writer_plan_shared_gt_coursework",
            title="Writer PLAN 骨架：共享 GT coursework/projects（ByteDance 可提升权重）",
            kind="user",
            text=writer_plan_fragments["shared_gt"],
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
            ),
            source_kind="shared_trunk",
            source_note="Writer PLAN 中所有线路共享的 Georgia Tech CS coursework/projects 规划块，ByteDance 场景仅进一步提升权重。",
        ),
        PromptBlock(
            block_id="writer_plan_shared_tail",
            title="Writer PLAN 骨架：共享结尾",
            kind="user",
            text=writer_plan_fragments["shared_tail"],
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
            ),
            source_kind="shared_trunk",
            source_note="Writer PLAN/RESUME 骨架的共享结尾，包含 SKILLS 推导、项目规划、教育经历选择与 RESUME 输出外壳。",
        ),
        PromptBlock(
            block_id="writer_jd_context",
            title="Writer Prompt: 目标 JD 信息",
            kind="context",
            text=_writer_jd_context_template(writer_jd_context_text),
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
            ),
            source_kind="stable_runtime_fragment",
            source_note="由 build_master_writer_prompt 的 JD 输入段稳定模板化，已去掉 ExampleCorp 固定值。",
            editor_visibility="appendix",
            content_role="context_template",
        ),
        PromptBlock(
            block_id="writer_jd_context_bytedance",
            title="Writer Prompt: 目标 JD 信息（ByteDance 分支）",
            kind="compat_alias",
            text="",
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
            ),
            source_kind="compat_alias_hidden",
            source_note="旧 writer ByteDance 特殊模式块已并入 retarget_bytedance_special 作为共享后端源；此 key 仅保留兼容，不再输出正文。",
            editor_visibility="hidden",
            content_role="compat_alias",
        ),
        PromptBlock(
            block_id="format_constraints",
            title="格式硬约束与 SKILLS 一致性规则",
            kind="compat_alias",
            text="",
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
                _target("match_pipe", "retarget_writer", "writer", "build_match_pipe_seed_retarget_prompt", "runtime/job_webapp/prompt_library.py", 488),
                _target("match_pipe", "upgrade_revision", "writer", "build_match_pipe_upgrade_revision_prompt", "runtime/job_webapp/prompt_library.py", 514),
            ),
            source_kind="compat_alias_hidden",
            source_note="旧整块格式硬约束已降为隐藏兼容别名；真实数据源已拆成共享头/中/尾 + 分支块。",
            editor_visibility="hidden",
            content_role="compat_alias",
        ),
        PromptBlock(
            block_id="format_constraints_bytedance",
            title="格式硬约束与 SKILLS 一致性规则（ByteDance 分支）",
            kind="compat_alias",
            text="",
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
                _target("match_pipe", "retarget_writer", "writer", "build_match_pipe_seed_retarget_prompt", "runtime/job_webapp/prompt_library.py", 488),
                _target("match_pipe", "upgrade_revision", "writer", "build_match_pipe_upgrade_revision_prompt", "runtime/job_webapp/prompt_library.py", 514),
            ),
            source_kind="compat_alias_hidden",
            source_note="旧整块 ByteDance 格式硬约束已降为隐藏兼容别名；真实数据源已拆成共享头/中/尾 + 分支块。",
            editor_visibility="hidden",
            content_role="compat_alias",
        ),
        PromptBlock(
            block_id="format_constraints_shared_head",
            title="格式硬约束：共享头部",
            kind="shared_constraints",
            text=format_constraint_fragments["shared_head"],
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
                _target("match_pipe", "retarget_writer", "writer", "build_match_pipe_seed_retarget_prompt", "runtime/job_webapp/prompt_library.py", 488),
                _target("match_pipe", "upgrade_revision", "writer", "build_match_pipe_upgrade_revision_prompt", "runtime/job_webapp/prompt_library.py", 514),
            ),
            source_kind="shared_trunk",
            source_note="格式硬约束的共享头部；Experience 顺序和后续不可变字段/Scope 分支已拆到独立块。",
        ),
        PromptBlock(
            block_id="format_constraints_branch",
            title="格式硬约束：通用分支",
            kind="shared_constraints_variant",
            text=format_constraint_fragments["generic_branch"],
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
                _target("match_pipe", "retarget_writer", "writer", "build_match_pipe_seed_retarget_prompt", "runtime/job_webapp/prompt_library.py", 488),
                _target("match_pipe", "upgrade_revision", "writer", "build_match_pipe_upgrade_revision_prompt", "runtime/job_webapp/prompt_library.py", 514),
            ),
            source_kind="shared_variant_branch",
            source_note="通用格式约束分支，承载 Experience 顺序、不可变字段和 Scope 规则中的 generic 部分。",
            content_role="variant_branch",
        ),
        PromptBlock(
            block_id="format_constraints_branch_bytedance",
            title="格式硬约束：ByteDance 分支",
            kind="shared_constraints_variant",
            text=format_constraint_fragments["bytedance_branch"],
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
                _target("match_pipe", "retarget_writer", "writer", "build_match_pipe_seed_retarget_prompt", "runtime/job_webapp/prompt_library.py", 488),
                _target("match_pipe", "upgrade_revision", "writer", "build_match_pipe_upgrade_revision_prompt", "runtime/job_webapp/prompt_library.py", 514),
            ),
            source_kind="shared_variant_branch",
            source_note="ByteDance 格式约束分支，承载 Experience 顺序、不可变字段和 Scope 规则中的 ByteDance 特殊部分。",
            content_role="variant_branch",
        ),
        PromptBlock(
            block_id="format_constraints_shared_mid",
            title="格式硬约束：共享中段",
            kind="shared_constraints",
            text=format_constraint_fragments["shared_mid"],
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
                _target("match_pipe", "retarget_writer", "writer", "build_match_pipe_seed_retarget_prompt", "runtime/job_webapp/prompt_library.py", 488),
                _target("match_pipe", "upgrade_revision", "writer", "build_match_pipe_upgrade_revision_prompt", "runtime/job_webapp/prompt_library.py", 514),
            ),
            source_kind="shared_trunk",
            source_note="格式硬约束在结构与具体分支规则之间的共享中段。",
        ),
        PromptBlock(
            block_id="format_constraints_shared_tail",
            title="格式硬约束：共享尾部",
            kind="shared_constraints",
            text=format_constraint_fragments["shared_tail"],
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "planner_writer_overlay", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
                _target("match_pipe", "planner_revision_overlay", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
                _target("match_pipe", "retarget_writer", "writer", "build_match_pipe_seed_retarget_prompt", "runtime/job_webapp/prompt_library.py", 488),
                _target("match_pipe", "upgrade_revision", "writer", "build_match_pipe_upgrade_revision_prompt", "runtime/job_webapp/prompt_library.py", 514),
            ),
            source_kind="shared_trunk",
            source_note="格式硬约束的共享尾部，包含数字合理性、围棋成就和 Achievements 规范。",
        ),
        PromptBlock(
            block_id="output_contract",
            title="统一输出合同",
            kind="shared_output",
            text=CANONICAL_OUTPUT_TEMPLATE.strip(),
            targets=(
                _target("match_pipe", "shared_writer", "writer", "build_match_pipe_master_writer_prompt", "runtime/job_webapp/prompt_library.py", 427),
                _target("match_pipe", "retarget_writer", "writer", "build_match_pipe_seed_retarget_prompt", "runtime/job_webapp/prompt_library.py", 488),
                _target("match_pipe", "upgrade_revision", "writer", "build_match_pipe_upgrade_revision_prompt", "runtime/job_webapp/prompt_library.py", 514),
            ),
            source_kind="stable_runtime_fragment",
            source_note="直接引用 core.prompt_builder.CANONICAL_OUTPUT_TEMPLATE。",
        ),
        PromptBlock(
            block_id="reviewer_system",
            title="Reviewer System Prompt",
            kind="system",
            text=UNIFIED_REVIEWER_SYSTEM.strip(),
            targets=(
                _target("match_pipe", "shared_reviewer", "reviewer", "match_pipe_reviewer_system_prompt", "runtime/job_webapp/prompt_library.py", 419),
            ),
            source_kind="stable_runtime_fragment",
            source_note="直接引用 core.prompt_builder.UNIFIED_REVIEWER_SYSTEM。",
        ),
        PromptBlock(
            block_id="reviewer_context",
            title="Reviewer Prompt: JD 与待审查简历输入",
            kind="shared_context",
            text=_reviewer_context_template(reviewer_context_text),
            targets=(
                _target("match_pipe", "shared_reviewer", "reviewer", "build_match_pipe_unified_review_prompt", "runtime/job_webapp/prompt_library.py", 452),
            ),
            source_kind="shared_trunk",
            source_note="由 build_unified_review_prompt 的 JD/immutable 输入段稳定模板化；共享主干保留 JD 与不可变字段插槽，ByteDance 特殊审查要求拆到独立分支块。",
            editor_visibility="appendix",
            content_role="context_template",
        ),
        PromptBlock(
            block_id="reviewer_context_bytedance",
            title="Reviewer Prompt: JD 与待审查简历输入（ByteDance 分支）",
            kind="shared_context_variant",
            text=_extract_optional_section(reviewer_context_bytedance_text, "## ByteDance 特殊审查要求")[1],
            targets=(
                _target("match_pipe", "shared_reviewer", "reviewer", "build_match_pipe_unified_review_prompt", "runtime/job_webapp/prompt_library.py", 452),
            ),
            source_kind="shared_variant_branch",
            source_note="只保留 ByteDance reviewer 特有审查附加段，作为共享 reviewer context 之上的分支块。",
            content_role="variant_branch",
        ),
        PromptBlock(
            block_id="reviewer_user",
            title="Reviewer User Prompt",
            kind="user",
            text=reviewer_user_body_text,
            targets=(
                _target("match_pipe", "shared_reviewer", "reviewer", "build_match_pipe_unified_review_prompt", "runtime/job_webapp/prompt_library.py", 452),
            ),
            source_kind="shared_trunk",
            source_note="由真实 reviewer user prompt 拆成共享正文主干；ByteDance 相关 4 处句子与 JSON schema 已拆到独立块。",
        ),
        PromptBlock(
            block_id="reviewer_user_bytedance",
            title="Reviewer User Prompt（ByteDance 分支）",
            kind="user_variant_branch",
            text=reviewer_user_bytedance_branch,
            targets=(
                _target("match_pipe", "shared_reviewer", "reviewer", "build_match_pipe_unified_review_prompt", "runtime/job_webapp/prompt_library.py", 452),
            ),
            source_kind="shared_variant_branch",
            source_note="ByteDance reviewer 只保留 4 条分支句：R0/R1/R3/R5；共享 reviewer 主干不再复制整块正文。",
            content_role="variant_branch",
        ),
        PromptBlock(
            block_id="reviewer_output_schema",
            title="Reviewer 输出 JSON Schema",
            kind="schema_fragment",
            text=reviewer_schema_text,
            targets=(
                _target("match_pipe", "shared_reviewer", "reviewer", "build_match_pipe_unified_review_prompt", "runtime/job_webapp/prompt_library.py", 452),
            ),
            source_kind="stable_runtime_fragment",
            source_note="由真实 reviewer prompt 拆出的输出 schema 与评分校准说明；属于结构说明附录，不应与自然语言正文同级编辑。",
            editor_visibility="appendix",
            content_role="schema",
        ),
        PromptBlock(
            block_id="retarget_prompt",
            title="Retarget Prompt",
            kind="user",
            text=_retarget_prompt_template(retarget_generic["prompt"]),
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "build_match_pipe_seed_retarget_prompt", "runtime/job_webapp/prompt_library.py", 488),
            ),
            source_kind="shared_trunk",
            source_note="由真实 build_seed_retarget_prompt 稳定模板化，已去掉固定公司名与通用顺序常量。",
        ),
        PromptBlock(
            block_id="retarget_prompt_bytedance",
            title="Retarget Prompt（ByteDance 分支）",
            kind="compat_alias",
            text="",
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "build_match_pipe_seed_retarget_prompt", "runtime/job_webapp/prompt_library.py", 488),
            ),
            source_kind="compat_alias_hidden",
            source_note="保留旧 key 兼容；ByteDance retarget 已改为共享主干 + 特殊块/同公司分支，此别名不再输出正文。",
            editor_visibility="hidden",
            content_role="compat_alias",
        ),
        PromptBlock(
            block_id="retarget_context",
            title="Retarget Prompt: 目标 JD 与 Seed 简历输入",
            kind="context",
            text=retarget_generic["seed_context"],
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "build_match_pipe_seed_retarget_prompt", "runtime/job_webapp/prompt_library.py", 488),
            ),
            source_kind="stable_runtime_fragment",
            source_note="由真实 retarget prompt 的 Seed 输入段拆出。",
            editor_visibility="appendix",
            content_role="source_fragment",
        ),
        PromptBlock(
            block_id="retarget_project_pool",
            title="Retarget Prompt: 公司项目池约束",
            kind="context",
            text=retarget_generic["project_pool"],
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "build_match_pipe_seed_retarget_prompt", "runtime/job_webapp/prompt_library.py", 488),
            ),
            source_kind="stable_runtime_fragment",
            source_note="由真实 retarget prompt 的项目池硬约束段拆出。",
            editor_visibility="appendix",
            content_role="source_fragment",
        ),
        PromptBlock(
            block_id="retarget_same_company",
            title="Retarget Prompt: 同公司一致性分支",
            kind="context_variant",
            text=retarget_generic_same_company["same_company_generic"],
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "build_match_pipe_seed_retarget_prompt", "runtime/job_webapp/prompt_library.py", 488),
            ),
            source_kind="shared_variant_branch",
            source_note="由真实 retarget prompt 的同公司分支拆出。",
            content_role="variant_branch",
        ),
        PromptBlock(
            block_id="retarget_same_company_bytedance",
            title="Retarget Prompt: ByteDance 同公司分支",
            kind="context_variant",
            text=retarget_bytedance["same_company_bytedance"],
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "build_match_pipe_seed_retarget_prompt", "runtime/job_webapp/prompt_library.py", 488),
            ),
            source_kind="shared_variant_branch",
            source_note="由真实 ByteDance retarget 的同公司分支拆出。",
            content_role="variant_branch",
        ),
        PromptBlock(
            block_id="retarget_bytedance_special",
            title="Retarget Prompt: ByteDance 特殊块",
            kind="context_variant",
            text=retarget_bytedance["bytedance_special"],
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "build_match_pipe_seed_retarget_prompt", "runtime/job_webapp/prompt_library.py", 488),
            ),
            source_kind="shared_variant_branch",
            source_note="由真实 ByteDance retarget 的特殊公司约束段拆出。",
            content_role="variant_branch",
        ),
        PromptBlock(
            block_id="upgrade_prompt",
            title="Upgrade Revision Prompt",
            kind="user",
            text=_upgrade_prompt_template(upgrade_generic["prompt"]),
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "build_match_pipe_upgrade_revision_prompt", "runtime/job_webapp/prompt_library.py", 514),
            ),
            source_kind="shared_trunk",
            source_note="由真实 build_upgrade_revision_prompt 稳定模板化，已去掉通用顺序常量。",
        ),
        PromptBlock(
            block_id="upgrade_prompt_bytedance",
            title="Upgrade Revision Prompt（ByteDance 分支）",
            kind="compat_alias",
            text="",
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "build_match_pipe_upgrade_revision_prompt", "runtime/job_webapp/prompt_library.py", 514),
            ),
            source_kind="compat_alias_hidden",
            source_note="保留旧 key 兼容；ByteDance upgrade 已改为共享主干 + 特殊块，此别名不再输出正文。",
            editor_visibility="hidden",
            content_role="compat_alias",
        ),
        PromptBlock(
            block_id="upgrade_context",
            title="Upgrade Prompt: 审查上下文与原始简历输入",
            kind="context",
            text=upgrade_generic["resume_context"],
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "build_match_pipe_upgrade_revision_prompt", "runtime/job_webapp/prompt_library.py", 514),
            ),
            source_kind="stable_runtime_fragment",
            source_note="由真实 upgrade prompt 的原始简历输入段拆出。",
            editor_visibility="appendix",
            content_role="source_fragment",
        ),
        PromptBlock(
            block_id="upgrade_bytedance_special",
            title="Upgrade Prompt: ByteDance 特殊块",
            kind="context_variant",
            text=upgrade_bytedance["bytedance_special"],
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "build_match_pipe_upgrade_revision_prompt", "runtime/job_webapp/prompt_library.py", 514),
            ),
            source_kind="shared_variant_branch",
            source_note="由真实 ByteDance upgrade 的特殊约束段拆出。",
            content_role="variant_branch",
        ),
        PromptBlock(
            block_id="planner_system",
            title="Planner System Prompt",
            kind="system",
            text=_planner_system_text(),
            targets=(
                _target("match_pipe", "planner_validation", "planner", "match_pipe_planner_system_prompt", "runtime/job_webapp/prompt_library.py", 423),
            ),
            source_kind="canonical_local_runtime_source",
            source_note="唯一运行时 system prompt，由 _plan_flow -> match_pipe_planner_system_prompt 直接消费。",
        ),
        PromptBlock(
            block_id="planner_user",
            title="Planner User Prompt",
            kind="user",
            text=_planner_user_text(),
            targets=(
                _target("match_pipe", "planner_validation", "planner", "build_match_pipe_planner_prompt", "runtime/job_webapp/prompt_library.py", 527),
            ),
            source_kind="canonical_local_runtime_source",
            source_note="planner user 指令本身没有更上游 builder；此处即唯一运行时源。",
        ),
        PromptBlock(
            block_id="planner_context",
            title="Planner Prompt: JD、Matcher、Starter 输入",
            kind="context",
            text=_planner_context_template(),
            targets=(
                _target("match_pipe", "planner_validation", "planner", "build_match_pipe_planner_prompt", "runtime/job_webapp/prompt_library.py", 527),
            ),
            source_kind="stable_runtime_fragment",
            source_note="由 build_match_pipe_planner_prompt 的实际插槽稳定模板化，直接对应运行时拼接结构。",
            editor_visibility="appendix",
            content_role="source_fragment",
        ),
        PromptBlock(
            block_id="planner_writer_overlay",
            title="Planner Writer Overlay",
            kind="overlay",
            text=_planner_writer_overlay_text(),
            targets=(
                _target("match_pipe", "planner_validation", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
            ),
            source_kind="canonical_local_runtime_source",
            source_note="planner-first 写作覆盖规则只在本地 runtime 中定义，无更上游共享 builder。",
        ),
        PromptBlock(
            block_id="planner_writer_context",
            title="Planner-first Writer Prompt: Planner 决策与历史起点输入",
            kind="context",
            text=_planner_writer_context_template(),
            targets=(
                _target("match_pipe", "planner_validation", "writer", "build_match_pipe_writer_prompt_from_planner", "runtime/job_webapp/prompt_library.py", 541),
            ),
            source_kind="stable_runtime_fragment",
            source_note="由 planner writer 实际运行时输入面稳定模板化，保留真实插槽与区块顺序。",
            editor_visibility="appendix",
            content_role="source_fragment",
        ),
        PromptBlock(
            block_id="planner_revision_overlay",
            title="Planner Revision Overlay",
            kind="overlay",
            text=_planner_revision_overlay_text(),
            targets=(
                _target("match_pipe", "planner_validation", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
            ),
            source_kind="canonical_local_runtime_source",
            source_note="planner-first revision 规则只在本地 runtime 中定义，无更上游 builder。",
        ),
        PromptBlock(
            block_id="planner_revision_context",
            title="Planner-first Revision Prompt: 审查与规划上下文",
            kind="context",
            text=_planner_revision_context_template(),
            targets=(
                _target("match_pipe", "planner_validation", "writer", "build_match_pipe_writer_revision_prompt", "runtime/job_webapp/prompt_library.py", 572),
            ),
            source_kind="stable_runtime_fragment",
            source_note="由 planner revision 实际运行时插槽稳定模板化，直接对应 writer revision carry-over 结构。",
            editor_visibility="appendix",
            content_role="source_fragment",
        ),
        PromptBlock(
            block_id="dual_channel_overlay",
            title="Dual-channel Continuity Overlay",
            kind="overlay",
            text=_dual_channel_overlay_template_text(),
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "append_match_pipe_dual_channel_overlay", "runtime/job_webapp/prompt_library.py", 624),
            ),
            source_kind="canonical_local_runtime_source",
            source_note="与 append_match_pipe_dual_channel_overlay 共用同一模板，不再依赖 override。",
        ),
    ]


def _default_prompt_views() -> list[PromptView]:
    return [
        PromptView(
            prompt_id="prompt_writer_system",
            title="Writer System Prompt",
            pipeline="match_pipe",
            stage="writer system",
            role="writer",
            description="writer 在主生成和 planner-first 生成里都会先收到这段 system prompt。",
            block_ids=("writer_system",),
            targets=(
                _target("match_pipe", "shared_writer", "writer", "match_pipe_writer_system_prompt", "runtime/job_webapp/prompt_library.py", 407),
            ),
        ),
        PromptView(
            prompt_id="prompt_writer_generate",
            title="主生成 Writer Prompt",
            pipeline="match_pipe",
            stage="no_starter / writer",
            role="writer",
            description="从零生成路径使用的完整 Writer prompt。",
            block_ids=_writer_block_ids("ExampleCorp"),
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "_run_no_starter", "match_pipe/downstream_validation_runner.py", 130),
            ),
        ),
        PromptView(
            prompt_id="prompt_writer_generate_bytedance",
            title="主生成 Writer Prompt（ByteDance 分支）",
            pipeline="match_pipe",
            stage="no_starter / writer / bytedance",
            role="writer",
            description="ByteDance 目标岗位会切到共享正文 + ByteDance 分支块。",
            block_ids=_writer_block_ids("ByteDance"),
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "_run_no_starter", "match_pipe/downstream_validation_runner.py", 130),
            ),
        ),
        PromptView(
            prompt_id="prompt_strict_revision_system",
            title="Strict Revision System Prompt",
            pipeline="match_pipe",
            stage="retarget / strict revise",
            role="writer",
            description="seed retarget 和严格修稿时走这段 system prompt。",
            block_ids=("strict_revision_system",),
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "_run_old_match", "match_pipe/downstream_validation_runner.py", 168),
                _target("match_pipe", "downstream_validation", "writer", "_run_new_dual_channel", "match_pipe/downstream_validation_runner.py", 242),
            ),
        ),
        PromptView(
            prompt_id="prompt_upgrade_system",
            title="Upgrade Revision System Prompt",
            pipeline="match_pipe",
            stage="reviewer 后续改写",
            role="writer",
            description="review 失败后的升级重写会走这段 system prompt。",
            block_ids=("upgrade_revision_system",),
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "_review_with_revision", "match_pipe/downstream_validation_runner.py", 94),
                _target("match_pipe", "planner_validation", "writer", "_review_direct_or_written", "match_pipe/planner_validation_runner.py", 303),
            ),
        ),
        PromptView(
            prompt_id="prompt_reviewer_system",
            title="Reviewer System Prompt",
            pipeline="match_pipe",
            stage="reviewer system",
            role="reviewer",
            description="reviewer 的统一 system prompt。",
            block_ids=("reviewer_system",),
            targets=(
                _target("match_pipe", "shared_reviewer", "reviewer", "_review_prompt_tokens", "match_pipe/downstream_validation_runner.py", 70),
                _target("match_pipe", "shared_reviewer", "reviewer", "_review_prompt_tokens", "match_pipe/planner_validation_runner.py", 57),
            ),
        ),
        PromptView(
            prompt_id="prompt_reviewer_full",
            title="主 Reviewer Prompt",
            pipeline="match_pipe",
            stage="all reviewer steps",
            role="reviewer",
            description="所有 full review 路径共用的 Reviewer user prompt。",
            block_ids=("reviewer_user", "reviewer_context", "reviewer_output_schema"),
            targets=(
                _target("match_pipe", "shared_reviewer", "reviewer", "_review_prompt_tokens", "match_pipe/downstream_validation_runner.py", 70),
                _target("match_pipe", "shared_reviewer", "reviewer", "_review_prompt_tokens", "match_pipe/planner_validation_runner.py", 57),
            ),
        ),
        PromptView(
            prompt_id="prompt_reviewer_full_bytedance",
            title="主 Reviewer Prompt（ByteDance 分支）",
            pipeline="match_pipe",
            stage="all reviewer steps / bytedance",
            role="reviewer",
            description="ByteDance 目标岗位的 reviewer prompt 会启用专用审查分支。",
            block_ids=("reviewer_user", "reviewer_user_bytedance", "reviewer_context", "reviewer_context_bytedance", "reviewer_output_schema"),
            targets=(
                _target("match_pipe", "shared_reviewer", "reviewer", "_review_prompt_tokens", "match_pipe/downstream_validation_runner.py", 70),
                _target("match_pipe", "shared_reviewer", "reviewer", "_review_prompt_tokens", "match_pipe/planner_validation_runner.py", 57),
            ),
        ),
        PromptView(
            prompt_id="prompt_retarget_old_match",
            title="Retarget Prompt",
            pipeline="match_pipe",
            stage="old_match_anchor / writer",
            role="writer",
            description="旧 match anchor 路径使用的 retarget prompt。",
            block_ids=_retarget_block_ids("ExampleCorp"),
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "_run_old_match", "match_pipe/downstream_validation_runner.py", 168),
            ),
        ),
        PromptView(
            prompt_id="prompt_retarget_same_company",
            title="Retarget Prompt（同公司分支）",
            pipeline="match_pipe",
            stage="old_match_anchor / writer / same_company",
            role="writer",
            description="旧 match anchor 在同公司一致性模式下会额外叠加这段分支。",
            block_ids=("retarget_same_company",),
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "_run_old_match", "match_pipe/downstream_validation_runner.py", 168),
            ),
        ),
        PromptView(
            prompt_id="prompt_retarget_old_match_bytedance",
            title="Retarget Prompt（ByteDance 分支）",
            pipeline="match_pipe",
            stage="old_match_anchor / writer / bytedance",
            role="writer",
            description="ByteDance retarget 走共享主干 + 专用特殊块/同公司分支。",
            block_ids=_retarget_block_ids("ByteDance", include_same_company=True),
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "_run_old_match", "match_pipe/downstream_validation_runner.py", 168),
            ),
        ),
        PromptView(
            prompt_id="prompt_upgrade_revision",
            title="Upgrade Revision Prompt",
            pipeline="match_pipe",
            stage="reviewer 后续改写",
            role="writer",
            description="review 失败后的升级重写 prompt。",
            block_ids=_upgrade_block_ids("ExampleCorp"),
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "_review_with_revision", "match_pipe/downstream_validation_runner.py", 94),
                _target("match_pipe", "planner_validation", "writer", "_review_direct_or_written", "match_pipe/planner_validation_runner.py", 303),
            ),
        ),
        PromptView(
            prompt_id="prompt_upgrade_revision_bytedance",
            title="Upgrade Revision Prompt（ByteDance 分支）",
            pipeline="match_pipe",
            stage="reviewer 后续改写 / bytedance",
            role="writer",
            description="ByteDance upgrade 走共享主干 + 特殊要求块。",
            block_ids=_upgrade_block_ids("ByteDance"),
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "_review_with_revision", "match_pipe/downstream_validation_runner.py", 94),
                _target("match_pipe", "planner_validation", "writer", "_review_direct_or_written", "match_pipe/planner_validation_runner.py", 303),
            ),
        ),
        PromptView(
            prompt_id="prompt_planner_system",
            title="Planner System Prompt",
            pipeline="match_pipe",
            stage="planner system",
            role="planner",
            description="planner-only 的 system prompt。",
            block_ids=("planner_system",),
            targets=(
                _target("match_pipe", "planner_validation", "planner", "_plan_flow", "match_pipe/planner_validation_runner.py", 171),
            ),
        ),
        PromptView(
            prompt_id="prompt_planner_user",
            title="Planner User Prompt",
            pipeline="match_pipe",
            stage="planner user",
            role="planner",
            description="planner-only 的 user prompt。",
            block_ids=("planner_user", "planner_context"),
            targets=(
                _target("match_pipe", "planner_validation", "planner", "_plan_flow", "match_pipe/planner_validation_runner.py", 171),
            ),
        ),
        PromptView(
            prompt_id="prompt_planner_writer_full",
            title="Planner-first Writer Prompt",
            pipeline="match_pipe",
            stage="planner write",
            role="writer",
            description="planner 先决策，再把判断覆盖到 Writer prompt 上。",
            block_ids=_writer_block_ids("ExampleCorp") + ("planner_writer_context", "planner_writer_overlay"),
            targets=(
                _target("match_pipe", "planner_validation", "writer", "_run_no_starter_planner", "match_pipe/planner_validation_runner.py", 346),
                _target("match_pipe", "planner_validation", "writer", "_run_new_dual_channel_planner", "match_pipe/planner_validation_runner.py", 379),
            ),
        ),
        PromptView(
            prompt_id="prompt_planner_writer_full_bytedance",
            title="Planner-first Writer Prompt（ByteDance 分支）",
            pipeline="match_pipe",
            stage="planner write / bytedance",
            role="writer",
            description="planner-first writer 在 ByteDance 目标岗位上会切到专用 writer 分支。",
            block_ids=_writer_block_ids("ByteDance") + ("planner_writer_context", "planner_writer_overlay"),
            targets=(
                _target("match_pipe", "planner_validation", "writer", "_run_no_starter_planner", "match_pipe/planner_validation_runner.py", 346),
                _target("match_pipe", "planner_validation", "writer", "_run_new_dual_channel_planner", "match_pipe/planner_validation_runner.py", 379),
            ),
        ),
        PromptView(
            prompt_id="prompt_planner_revision_full",
            title="Planner-first Revision Prompt",
            pipeline="match_pipe",
            stage="planner revision",
            role="writer",
            description="planner 和 reviewer 的 carry-over 都会进入这条 revision prompt。",
            block_ids=_writer_block_ids("ExampleCorp") + ("planner_revision_context", "planner_revision_overlay"),
            targets=(
                _target("match_pipe", "planner_validation", "writer", "_review_direct_or_written", "match_pipe/planner_validation_runner.py", 303),
            ),
        ),
        PromptView(
            prompt_id="prompt_planner_revision_full_bytedance",
            title="Planner-first Revision Prompt（ByteDance 分支）",
            pipeline="match_pipe",
            stage="planner revision / bytedance",
            role="writer",
            description="planner revision 在 ByteDance 目标岗位上会切到专用 writer 分支。",
            block_ids=_writer_block_ids("ByteDance") + ("planner_revision_context", "planner_revision_overlay"),
            targets=(
                _target("match_pipe", "planner_validation", "writer", "_review_direct_or_written", "match_pipe/planner_validation_runner.py", 303),
            ),
        ),
        PromptView(
            prompt_id="prompt_dual_channel_full",
            title="Dual-channel Retarget Prompt",
            pipeline="match_pipe",
            stage="new_dual_channel / writer",
            role="writer",
            description="dual-channel 路径会在 retarget prompt 后面追加 continuity overlay。",
            block_ids=_retarget_block_ids("ExampleCorp", include_dual=True),
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "_run_new_dual_channel", "match_pipe/downstream_validation_runner.py", 242),
            ),
        ),
        PromptView(
            prompt_id="prompt_dual_channel_full_bytedance",
            title="Dual-channel Retarget Prompt（ByteDance 分支）",
            pipeline="match_pipe",
            stage="new_dual_channel / writer / bytedance",
            role="writer",
            description="dual-channel 的 ByteDance 路径在 retarget 主干外叠加专用分支。",
            block_ids=_retarget_block_ids("ByteDance", include_dual=True, include_same_company=True),
            targets=(
                _target("match_pipe", "downstream_validation", "writer", "_run_new_dual_channel", "match_pipe/downstream_validation_runner.py", 242),
            ),
        ),
    ]


def _read_override_payload() -> dict[str, Any]:
    if not OVERRIDE_PATH.exists():
        return {}
    try:
        payload = json.loads(OVERRIDE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _read_override_texts() -> dict[str, str]:
    payload = _read_override_payload()
    blocks = payload.get("blocks", {})
    if not isinstance(blocks, dict):
        return {}
    resolved = {
        str(key): str(value)
        for key, value in blocks.items()
        if str(key) not in NON_OVERRIDEABLE_BLOCKS
    }
    for legacy_key, current_key in LEGACY_OVERRIDE_BLOCK_ALIASES.items():
        if current_key not in resolved and legacy_key in resolved:
            resolved[current_key] = resolved[legacy_key]
    return resolved


def _read_paragraph_override_texts() -> dict[str, str]:
    payload = _read_override_payload()
    paragraphs = payload.get("paragraphs", {})
    if not isinstance(paragraphs, dict):
        return {}
    return {str(key): str(value) for key, value in paragraphs.items()}


def save_match_pipe_prompt_overrides(block_text_map: dict[str, str]) -> dict[str, Any]:
    defaults = {block.block_id: block.text for block in _default_blocks()}
    filtered = {
        str(block_id): str(text)
        for block_id, text in block_text_map.items()
        if str(block_id) in defaults
        and str(block_id) not in NON_OVERRIDEABLE_BLOCKS
        and str(text) != defaults[str(block_id)]
    }
    OVERRIDE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = _read_override_payload()
    payload = {
        "scope": "match_pipe",
        "blocks": filtered,
        "paragraphs": payload.get("paragraphs", {}) if isinstance(payload.get("paragraphs", {}), dict) else {},
    }
    OVERRIDE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "path": str(OVERRIDE_PATH),
        "saved_block_count": len(filtered),
    }


def save_match_pipe_paragraph_overrides(paragraph_text_map: dict[str, str]) -> dict[str, Any]:
    editor_mapping = _build_editor_mapping(_resolved_blocks())
    paragraph_lookup = {
        entry["id"]: entry
        for entry in editor_mapping["paragraphs"]
    }
    block_templates = editor_mapping["block_templates"]
    current_paragraphs = {
        paragraph_id: str(entry["text"])
        for paragraph_id, entry in paragraph_lookup.items()
    }
    paragraph_updates = {
        str(paragraph_id): str(text)
        for paragraph_id, text in paragraph_text_map.items()
        if str(paragraph_id) in paragraph_lookup
    }
    merged_paragraphs = dict(current_paragraphs)
    merged_paragraphs.update(paragraph_updates)
    block_text_map: dict[str, str] = {}
    for block_id, segments in block_templates.items():
        rendered_parts: list[str] = []
        for segment in segments:
            if segment["kind"] == "paragraph":
                paragraph_id = segment["paragraph_id"]
                paragraph = paragraph_lookup.get(paragraph_id)
                if paragraph is None:
                    continue
                rendered_parts.append(merged_paragraphs.get(paragraph_id, paragraph["text"]).strip())
            else:
                rendered_parts.append(str(segment["text"]).strip())
        block_text_map[block_id] = "\n\n".join(part for part in rendered_parts if part)
    result = save_match_pipe_prompt_overrides(block_text_map)
    payload = _read_override_payload()
    payload["scope"] = "match_pipe"
    stored_paragraphs = {
        str(paragraph_id): str(text)
        for paragraph_id, text in _read_paragraph_override_texts().items()
        if paragraph_id in paragraph_lookup
    }
    stored_paragraphs.update(paragraph_updates)
    payload["paragraphs"] = stored_paragraphs
    OVERRIDE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result["saved_paragraph_count"] = len(stored_paragraphs)
    result["updated_paragraph_count"] = len(paragraph_updates)
    result["mapping_scope"] = PARAGRAPH_OVERRIDE_SCOPE
    return result


def _resolved_blocks() -> list[PromptBlock]:
    overrides = _read_override_texts()
    resolved: list[PromptBlock] = []
    for block in _default_blocks():
        text = overrides.get(block.block_id, block.text)
        resolved.append(
            PromptBlock(
                block_id=block.block_id,
                title=block.title,
                kind=block.kind,
                text=text,
                targets=block.targets,
                source_kind=block.source_kind,
                source_note=block.source_note,
                editor_visibility=block.editor_visibility,
                content_role=block.content_role,
            )
        )
    return resolved


def _block_map() -> dict[str, PromptBlock]:
    return {block.block_id: block for block in _resolved_blocks()}


def get_match_pipe_block_text(block_id: str) -> str:
    block = _block_map().get(block_id)
    if block is None:
        raise KeyError(f"unknown prompt block: {block_id}")
    return block.text


def _company_block_text(base_block_id: str, company: str) -> str:
    if _is_bytedance_company(company):
        variant_id = f"{base_block_id}_bytedance"
        block = _block_map().get(variant_id)
        if block is not None:
            return block.text
    return get_match_pipe_block_text(base_block_id)


def _split_block_sections(text: str) -> list[str]:
    stripped = text.strip()
    if not stripped:
        return []
    return [section.strip() for section in re.split(r"\n\s*\n", stripped) if section.strip()]


BLOCK_SECTION_MERGES: dict[str, tuple[tuple[int, ...], ...]] = {
    "writer_system": ((5, 6),),
    "writer_plan_shared_intro": ((1, 2, 3),),
    "writer_plan_shared_tail": ((4, 5, 6),),
    "format_constraints_shared_head": ((1, 2),),
    "output_contract": ((7, 8),),
    "retarget_prompt": ((1, 2, 3),),
    "upgrade_prompt": ((1, 2),),
}

DISPLAY_OWNER_BY_BLOCK: dict[str, tuple[str, str, str]] = {
    # Writer reusable shared trunk / branch blocks live under the shared writer card.
    "candidate_context_shared_experience": ("match_pipe", "shared_writer", "writer"),
    "candidate_context_generic_tiktok_branch": ("match_pipe", "shared_writer", "writer"),
    "candidate_context_shared_education": ("match_pipe", "shared_writer", "writer"),
    "candidate_context_bytedance_education_branch": ("match_pipe", "shared_writer", "writer"),
    "candidate_context_shared_achievements": ("match_pipe", "shared_writer", "writer"),
    "candidate_context_bytedance_boundary": ("match_pipe", "shared_writer", "writer"),
    "writer_system": ("match_pipe", "shared_writer", "writer"),
    "writer_plan_shared_intro": ("match_pipe", "shared_writer", "writer"),
    "writer_plan_generic_tiktok_branch": ("match_pipe", "shared_writer", "writer"),
    "writer_plan_shared_didi_temu": ("match_pipe", "shared_writer", "writer"),
    "writer_plan_shared_gt_coursework": ("match_pipe", "shared_writer", "writer"),
    "writer_plan_shared_tail": ("match_pipe", "shared_writer", "writer"),
    "format_constraints_shared_head": ("match_pipe", "shared_writer", "writer"),
    "format_constraints_branch": ("match_pipe", "shared_writer", "writer"),
    "format_constraints_branch_bytedance": ("match_pipe", "shared_writer", "writer"),
    "format_constraints_shared_mid": ("match_pipe", "shared_writer", "writer"),
    "format_constraints_shared_tail": ("match_pipe", "shared_writer", "writer"),
    "output_contract": ("match_pipe", "shared_writer", "writer"),
    # Reviewer reusable blocks live under the shared reviewer card.
    "reviewer_system": ("match_pipe", "shared_reviewer", "reviewer"),
    "reviewer_user": ("match_pipe", "shared_reviewer", "reviewer"),
    "reviewer_user_bytedance": ("match_pipe", "shared_reviewer", "reviewer"),
    "reviewer_context": ("match_pipe", "shared_reviewer", "reviewer"),
    "reviewer_context_bytedance": ("match_pipe", "shared_reviewer", "reviewer"),
    "reviewer_output_schema": ("match_pipe", "shared_reviewer", "reviewer"),
}


def _merge_block_sections(block_id: str, sections: list[str]) -> list[str]:
    merge_groups = BLOCK_SECTION_MERGES.get(block_id)
    if not merge_groups:
        return sections
    consumed: set[int] = set()
    merged: list[str] = []
    group_by_start = {group[0]: group for group in merge_groups if group}
    for idx, section in enumerate(sections, start=1):
        if idx in consumed:
            continue
        group = group_by_start.get(idx)
        if not group:
            merged.append(section)
            continue
        parts = [sections[group_idx - 1] for group_idx in group if 1 <= group_idx <= len(sections)]
        consumed.update(group)
        merged.append("\n\n".join(part for part in parts if part.strip()).strip())
    return merged


def _paragraph_display_owner(paragraph: EditorParagraph) -> tuple[str, str, str] | None:
    owner_keys = {
        DISPLAY_OWNER_BY_BLOCK[ref.block_id]
        for ref in paragraph.write_refs
        if ref.block_id in DISPLAY_OWNER_BY_BLOCK
    }
    if len(owner_keys) == 1:
        return next(iter(owner_keys))
    return None


def _strip_markdown_label(line: str) -> str:
    return re.sub(r"^[#>*\-\d\.\)\s]+", "", line).strip()


def _strip_inline_markup(text: str) -> str:
    return text.replace("**", "").replace("__", "").replace("`", "").strip()


def _looks_like_json_schema(text: str) -> bool:
    compact = text.strip()
    if not compact:
        return False
    if compact.startswith("{") and '"scores"' in compact:
        return True
    if compact.startswith("{") and compact.count("{") >= 3 and compact.count('":') >= 4:
        return True
    return False


def _placeholder_count(text: str) -> int:
    return len(PLACEHOLDER_RE.findall(text))


def _is_placeholder_heavy_line(line: str) -> bool:
    compact = _strip_inline_markup(line.strip())
    if not compact:
        return True
    count = _placeholder_count(compact)
    if count == 0:
        return False
    residue = PLACEHOLDER_RE.sub("", compact)
    residue = re.sub(r"[\[\]\(\)\-\*\d\.\s:：/|><=→_,]+", "", residue)
    return len(residue) <= 24


def _is_placeholder_assignment_line(line: str) -> bool:
    compact = _strip_inline_markup(line.strip())
    if not compact:
        return False
    if re.fullmatch(r"[-*]\s*\{[^}]+\}", compact):
        return True
    if re.fullmatch(r"[-*]\s*\{[^}]+\}.*", compact):
        return True
    if re.fullmatch(r"\{[^}]+\}", compact):
        return True
    if re.fullmatch(r"[-*]\s*[^:：]+[:：]\s*\{[^}]+\}.*", compact):
        return True
    if re.fullmatch(r"[^:：]+[:：]\s*\{[^}]+\}.*", compact):
        return True
    if re.fullmatch(r"\d+\.\s*\{[^}]+\}.*", compact):
        return True
    return False


def _clean_editable_section(text: str) -> tuple[str, str]:
    stripped = text.strip()
    if not stripped:
        return "", "empty"
    if _looks_like_json_schema(stripped):
        return "", "json_schema"
    cleaned_lines: list[str] = []
    for raw_line in stripped.splitlines():
        line = raw_line.rstrip()
        compact = line.strip()
        if not compact:
            cleaned_lines.append("")
            continue
        if compact in {"```", "```md", "```json", "---"}:
            continue
        if _is_placeholder_assignment_line(compact):
            continue
        if PLACEHOLDER_RE.fullmatch(compact):
            continue
        cleaned_lines.append(line)
    while cleaned_lines and not cleaned_lines[0].strip():
        cleaned_lines.pop(0)
    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop()
    if not cleaned_lines:
        return "", "placeholder_only"
    first_line_bare = _strip_markdown_label(_strip_inline_markup(cleaned_lines[0])).rstrip(":：")
    if first_line_bare in SHELL_ONLY_LABELS:
        remainder = [line for line in cleaned_lines[1:] if line.strip()]
        if not remainder or all(_is_placeholder_heavy_line(line) for line in remainder):
            return "", "shell_label_only"
    cleaned = "\n".join(cleaned_lines).strip()
    if not cleaned:
        return "", "placeholder_only"
    bare = _strip_markdown_label(_strip_inline_markup(cleaned)).rstrip(":：")
    if bare in SHELL_ONLY_LABELS and "\n" not in cleaned:
        return "", "shell_label_only"
    return cleaned, ""


def _block_branch_kind(block_id: str) -> str:
    if "bytedance" in block_id:
        return "bytedance_branch"
    if block_id.endswith("_variant") or block_id.endswith("_special") or "same_company" in block_id:
        return "variant_branch"
    return "shared_trunk"


def _is_block_editable(block: PromptBlock) -> bool:
    if block.editor_visibility != "main":
        return False
    if block.content_role in NON_EDITABLE_CONTENT_ROLES:
        return False
    return True


def _editor_card_specs() -> dict[str, EditorCardSpec]:
    return {spec.card_id: spec for spec in EDITOR_CARD_SPECS}


def _card_spec_by_block_id() -> dict[str, EditorCardSpec]:
    mapping: dict[str, EditorCardSpec] = {}
    for spec in EDITOR_CARD_SPECS:
        for block_id in spec.block_ids:
            mapping[block_id] = spec
    return mapping


def _diff_block_id(card_id: str, text: str) -> str:
    digest = hashlib.sha1(f"{card_id}\0{text}".encode("utf-8")).hexdigest()[:12]
    return f"{card_id}.blk.{digest}"


def _merged_card_id(pipeline: str, stage: str, role: str) -> str:
    key = f"{pipeline}::{stage}::{role}"
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]
    return f"merged.{digest}"


MERGED_CARD_STAGE_PRIORITY: dict[str, int] = {
    "shared_writer": 0,
    "shared_reviewer": 0,
    "writer system": 1,
    "reviewer system": 1,
    "planner system": 1,
    "planner user": 1,
    "revision": 2,
    "retarget_writer": 3,
    "upgrade_revision": 3,
    "downstream_validation": 4,
    "planner_validation": 5,
    "planner_writer_overlay": 6,
    "planner_revision_overlay": 7,
}


def _merged_card_display_priority(pipeline: str, stage: str, role: str) -> tuple[int, str, str, str]:
    return (MERGED_CARD_STAGE_PRIORITY.get(stage, 50), pipeline, stage, role)


def _build_editor_mapping(blocks: list[PromptBlock] | None = None) -> dict[str, Any]:
    blocks = list(blocks or _resolved_blocks())
    block_map = {block.block_id: block for block in blocks}
    prompt_views = _default_prompt_views()
    prompt_map = {prompt.prompt_id: prompt for prompt in prompt_views}
    block_to_prompts: dict[str, list[PromptView]] = {}
    for prompt in prompt_views:
        for block_id in prompt.block_ids:
            block_to_prompts.setdefault(block_id, []).append(prompt)

    card_specs = _editor_card_specs()
    block_to_card = _card_spec_by_block_id()
    editable_blocks = [block for block in blocks if _is_block_editable(block)]
    editable_segments_by_block: dict[str, list[tuple[int, str]]] = {}
    block_templates: dict[str, list[EditorBlockSegment]] = {}
    unmapped_editable_blocks: list[str] = []

    for block in editable_blocks:
        sections = _merge_block_sections(block.block_id, _split_block_sections(block.text))
        segments: list[EditorBlockSegment] = []
        editable_segments: list[tuple[int, str]] = []
        for raw_index, section in enumerate(sections, start=1):
            cleaned, hidden_reason = _clean_editable_section(section)
            if cleaned:
                editable_segments.append((raw_index, cleaned))
                segments.append(EditorBlockSegment(kind="paragraph", text=cleaned, raw_index=raw_index))
            else:
                segments.append(
                    EditorBlockSegment(
                        kind="hidden",
                        text=section,
                        hidden_reason=hidden_reason,
                        raw_index=raw_index,
                    )
                )
        if editable_segments:
            editable_segments_by_block[block.block_id] = editable_segments
            if block.block_id not in block_to_card:
                unmapped_editable_blocks.append(block.block_id)
        block_templates[block.block_id] = segments

    cards: list[EditorCard] = []
    paragraphs: list[EditorParagraph] = []
    paragraph_lookup: dict[str, EditorParagraph] = {}
    paragraph_ids_by_card: dict[str, list[str]] = {}
    block_template_payload: dict[str, list[dict[str, Any]]] = {}

    for spec in EDITOR_CARD_SPECS:
        members = [block_map[block_id] for block_id in spec.block_ids if block_id in editable_segments_by_block]
        if not members:
            continue
        card_paragraphs: dict[str, list[tuple[str, int]]] = {}
        card_prompt_ids: list[str] = []
        card_targets: list[PromptTarget] = []
        ordered_texts: list[str] = []
        for block in members:
            card_targets.extend(block.targets)
            card_prompt_ids.extend(prompt.prompt_id for prompt in block_to_prompts.get(block.block_id, ()))
            for paragraph_index, paragraph_text in editable_segments_by_block[block.block_id]:
                card_paragraphs.setdefault(paragraph_text, []).append((block.block_id, paragraph_index))
                if paragraph_text not in ordered_texts:
                    ordered_texts.append(paragraph_text)
        paragraph_ids: list[str] = []
        for paragraph_text in ordered_texts:
            write_refs = tuple(
                EditorParagraphWriteRef(
                    block_id=block_id,
                    block_title=block_map[block_id].title,
                    paragraph_index=paragraph_index,
                    branch_kind=_block_branch_kind(block_id),
                )
                for block_id, paragraph_index in card_paragraphs[paragraph_text]
            )
            prompt_ids = tuple(
                sorted(
                    {
                        prompt.prompt_id
                        for block_id, _ in card_paragraphs[paragraph_text]
                        for prompt in block_to_prompts.get(block_id, ())
                    }
                )
            )
            prompt_targets = _dedupe_prompt_targets(
                [
                    target
                    for prompt_id in prompt_ids
                    for target in prompt_map[prompt_id].targets
                ]
            )
            stages = tuple(sorted({target.stage for target in prompt_targets}))
            unique_branch_kinds = {item.branch_kind for item in write_refs}
            paragraph_branch_kind = next(iter(unique_branch_kinds)) if len(unique_branch_kinds) == 1 else "mixed"
            mapping_kind = "shared_block" if len(prompt_ids) > 1 or len(write_refs) > 1 else "branch_block"
            paragraph_id = _diff_block_id(spec.card_id, paragraph_text)
            paragraph = EditorParagraph(
                paragraph_id=paragraph_id,
                card_id=spec.card_id,
                text=paragraph_text,
                write_refs=write_refs,
                prompt_ids=prompt_ids,
                prompt_targets=prompt_targets,
                stages=stages,
                branch_kind=paragraph_branch_kind,
                mapping_kind=mapping_kind,
            )
            paragraphs.append(paragraph)
            paragraph_lookup[paragraph_id] = paragraph
            paragraph_ids.append(paragraph_id)
        paragraph_ids_by_card[spec.card_id] = paragraph_ids
        cards.append(
            EditorCard(
                card_id=spec.card_id,
                title=spec.title,
                description=spec.description,
                block_ids=tuple(block.block_id for block in members),
                prompt_ids=tuple(sorted(set(card_prompt_ids))),
                paragraph_ids=tuple(paragraph_ids),
                targets=_dedupe_prompt_targets(card_targets),
                blockers=EDITOR_CARD_BLOCKERS.get(spec.card_id, ()),
            )
        )

    merged_cards: list[EditorMergedCard] = []
    merged_card_ids_by_card: dict[str, list[str]] = {card.card_id: [] for card in cards}
    merged_card_ids_by_paragraph: dict[str, list[str]] = {paragraph.paragraph_id: [] for paragraph in paragraphs}
    cards_by_target: dict[tuple[str, str, str], list[EditorCard]] = {}
    for card in cards:
        seen_keys: set[tuple[str, str, str]] = set()
        for target in card.targets:
            key = (target.pipeline, target.stage, target.role)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            cards_by_target.setdefault(key, []).append(card)

    merged_card_targets: dict[str, tuple[str, str, str]] = {}
    merged_card_diff_ids: dict[str, list[str]] = {}

    for key in sorted(cards_by_target):
        pipeline, stage, role = key
        member_cards = cards_by_target[key]
        ordered_member_ids: list[str] = []
        ordered_diff_ids: list[str] = []
        prompt_ids: list[str] = []
        targets: list[PromptTarget] = []
        seen_diff_ids: set[str] = set()
        seen_member_ids: set[str] = set()
        for card in member_cards:
            if card.card_id not in seen_member_ids:
                ordered_member_ids.append(card.card_id)
                seen_member_ids.add(card.card_id)
            prompt_ids.extend(card.prompt_ids)
            for target in card.targets:
                if (target.pipeline, target.stage, target.role) == key:
                    targets.append(target)
            for diff_id in card.paragraph_ids:
                if diff_id in seen_diff_ids:
                    continue
                seen_diff_ids.add(diff_id)
                ordered_diff_ids.append(diff_id)
        merged_id = _merged_card_id(pipeline, stage, role)
        merged_card_targets[merged_id] = key
        merged_card_diff_ids[merged_id] = list(ordered_diff_ids)
        for member_id in ordered_member_ids:
            merged_card_ids_by_card.setdefault(member_id, []).append(merged_id)
        for diff_id in ordered_diff_ids:
            merged_card_ids_by_paragraph.setdefault(diff_id, []).append(merged_id)

        merged_cards.append(
            EditorMergedCard(
                merged_card_id=merged_id,
                pipeline=pipeline,
                stage=stage,
                role=role,
                title=f"{pipeline} / {stage} / {role}",
                member_card_ids=tuple(ordered_member_ids),
                diff_block_ids=tuple(ordered_diff_ids),
                display_diff_block_ids=(),
                prompt_ids=tuple(sorted(set(prompt_ids))),
                targets=_dedupe_prompt_targets(targets),
            )
        )

    display_owner_by_paragraph: dict[str, str] = {}
    display_diff_ids_by_merged: dict[str, list[str]] = {merged.merged_card_id: [] for merged in merged_cards}
    for paragraph in paragraphs:
        merged_ids = merged_card_ids_by_paragraph.get(paragraph.paragraph_id, [])
        if not merged_ids:
            continue
        preferred_owner_key = _paragraph_display_owner(paragraph)
        owner_id = ""
        if preferred_owner_key is not None:
            for merged_id in merged_ids:
                if merged_card_targets.get(merged_id) == preferred_owner_key:
                    owner_id = merged_id
                    break
        if not owner_id:
            owner_id = sorted(
                merged_ids,
                key=lambda merged_id: _merged_card_display_priority(*merged_card_targets[merged_id]),
            )[0]
        display_owner_by_paragraph[paragraph.paragraph_id] = owner_id
        display_diff_ids_by_merged.setdefault(owner_id, []).append(paragraph.paragraph_id)

    merged_cards = [
        EditorMergedCard(
            merged_card_id=merged.merged_card_id,
            pipeline=merged.pipeline,
            stage=merged.stage,
            role=merged.role,
            title=merged.title,
            member_card_ids=merged.member_card_ids,
            diff_block_ids=merged.diff_block_ids,
            display_diff_block_ids=tuple(display_diff_ids_by_merged.get(merged.merged_card_id, ())),
            prompt_ids=merged.prompt_ids,
            targets=merged.targets,
        )
        for merged in merged_cards
        if display_diff_ids_by_merged.get(merged.merged_card_id)
    ]

    card_map = {card.card_id: card for card in cards}
    merged_display_cards: list[EditorCard] = []
    for merged_card in merged_cards:
        member_cards = [card_map[card_id] for card_id in merged_card.member_card_ids if card_id in card_map]
        seen_block_ids: set[str] = set()
        ordered_block_ids: list[str] = []
        blockers: list[str] = []
        seen_blockers: set[str] = set()
        member_titles: list[str] = []
        seen_titles: set[str] = set()
        for member_card in member_cards:
            for block_id in member_card.block_ids:
                if block_id in seen_block_ids:
                    continue
                seen_block_ids.add(block_id)
                ordered_block_ids.append(block_id)
            for blocker in member_card.blockers:
                if blocker in seen_blockers:
                    continue
                seen_blockers.add(blocker)
                blockers.append(blocker)
            if member_card.title not in seen_titles:
                seen_titles.add(member_card.title)
                member_titles.append(member_card.title)
        description = "包含: " + "、".join(member_titles) if member_titles else ""
        merged_display_cards.append(
            EditorCard(
                card_id=merged_card.merged_card_id,
                title=merged_card.title,
                description=description,
                block_ids=tuple(ordered_block_ids),
                prompt_ids=merged_card.prompt_ids,
                paragraph_ids=merged_card.display_diff_block_ids,
                targets=merged_card.targets,
                blockers=tuple(blockers),
                merged_card_ids=(merged_card.merged_card_id,),
            )
        )

    cards = merged_display_cards
    paragraphs = [
        EditorParagraph(
            paragraph_id=paragraph.paragraph_id,
            card_id=paragraph.card_id,
            text=paragraph.text,
            write_refs=paragraph.write_refs,
            prompt_ids=paragraph.prompt_ids,
            prompt_targets=paragraph.prompt_targets,
            stages=paragraph.stages,
            branch_kind=paragraph.branch_kind,
            mapping_kind=paragraph.mapping_kind,
            merge_strategy=paragraph.merge_strategy,
            unit=paragraph.unit,
            merged_card_ids=tuple(merged_card_ids_by_paragraph.get(paragraph.paragraph_id, ())),
            display_owner_merged_card_id=display_owner_by_paragraph.get(paragraph.paragraph_id, ""),
        )
        for paragraph in paragraphs
    ]
    paragraph_lookup = {paragraph.paragraph_id: paragraph for paragraph in paragraphs}

    paragraph_id_by_ref: dict[tuple[str, int], str] = {}
    for paragraph in paragraphs:
        for ref in paragraph.write_refs:
            paragraph_id_by_ref[(ref.block_id, ref.paragraph_index)] = paragraph.paragraph_id

    for block_id, segments in block_templates.items():
        payload_segments: list[dict[str, Any]] = []
        for segment in segments:
            if segment.kind == "paragraph":
                paragraph_id = paragraph_id_by_ref.get((block_id, segment.raw_index))
                if not paragraph_id:
                    payload_segments.append(segment.to_dict())
                    continue
                payload_segments.append(
                    EditorBlockSegment(
                        kind="paragraph",
                        text=segment.text,
                        paragraph_id=paragraph_id,
                        raw_index=segment.raw_index,
                    ).to_dict()
                )
            else:
                payload_segments.append(segment.to_dict())
        block_template_payload[block_id] = payload_segments

    mapped_paragraph_ids = {paragraph.paragraph_id for paragraph in paragraphs}
    unmapped_card_specs = [
        spec.card_id
        for spec in EDITOR_CARD_SPECS
        if spec.card_id not in paragraph_ids_by_card
        and any(block_id in editable_segments_by_block for block_id in spec.block_ids)
    ]

    return {
        "scope": PARAGRAPH_OVERRIDE_SCOPE,
        "cards": [card.to_dict() for card in cards],
        "merged_cards": [card.to_dict() for card in merged_cards],
        "diff_blocks": [paragraph.to_dict() for paragraph in paragraphs],
        "paragraphs": [paragraph.to_dict() for paragraph in paragraphs],
        "block_templates": block_template_payload,
        "coverage": {
            "editable_block_count": len(editable_segments_by_block),
            "editable_paragraph_count": len(paragraphs),
            "diff_block_count": len(paragraphs),
            "mapped_paragraph_count": len(mapped_paragraph_ids),
            "merged_card_count": len(merged_cards),
            "unmapped_editable_blocks": sorted(set(unmapped_editable_blocks)),
            "unmapped_card_specs": sorted(unmapped_card_specs),
        },
        "boundaries": [
            {
                "card_id": card_id,
                "notes": list(notes),
            }
            for card_id, notes in sorted(EDITOR_CARD_BLOCKERS.items())
        ],
    }


def build_match_pipe_prompt_library() -> dict[str, Any]:
    blocks = _resolved_blocks()
    block_map = {block.block_id: block for block in blocks}
    rendered_prompts: list[dict[str, Any]] = []
    for prompt in _default_prompt_views():
        payload = prompt.to_dict()
        payload["rendered_text"] = "\n\n".join(block_map[block_id].text for block_id in prompt.block_ids)
        rendered_prompts.append(payload)
    editor_mapping = _build_editor_mapping()
    return {
        "scope": "match_pipe",
        "blocks": [block.to_dict() for block in blocks],
        "prompts": rendered_prompts,
        "editor_mapping": editor_mapping,
        "meta": {
            "block_count": len(blocks),
            "prompt_count": len(rendered_prompts),
            "shared_block_count": sum(1 for block in blocks if len(block.targets) > 1),
            "override_path": str(OVERRIDE_PATH),
            "has_saved_overrides": OVERRIDE_PATH.exists(),
            "paragraph_override_count": len(_read_paragraph_override_texts()),
            "editable_card_count": len(editor_mapping["cards"]),
            "merged_card_count": editor_mapping["coverage"]["merged_card_count"],
            "editable_paragraph_count": editor_mapping["coverage"]["editable_paragraph_count"],
            "diff_block_count": editor_mapping["coverage"]["diff_block_count"],
            "unmapped_editable_blocks": editor_mapping["coverage"]["unmapped_editable_blocks"],
        },
    }


def get_match_pipe_editor_mapping() -> dict[str, Any]:
    return _build_editor_mapping()


def match_pipe_writer_system_prompt() -> str:
    return get_match_pipe_block_text("writer_system")


def match_pipe_strict_revision_system_prompt() -> str:
    return get_match_pipe_block_text("strict_revision_system")


def match_pipe_upgrade_revision_system_prompt() -> str:
    return get_match_pipe_block_text("upgrade_revision_system")


def match_pipe_reviewer_system_prompt() -> str:
    return get_match_pipe_block_text("reviewer_system")


def match_pipe_planner_system_prompt() -> str:
    return get_match_pipe_block_text("planner_system")


def build_match_pipe_master_writer_prompt(jd) -> str:
    tech_required = ", ".join(jd.tech_required) if jd.tech_required else "（无明确列出）"
    tech_preferred = ", ".join(jd.tech_preferred) if jd.tech_preferred else "（无）"
    or_groups = "\n".join(f"- {' / '.join(group)}" for group in (jd.tech_or_groups or [])) or "（无）"
    soft_required = "\n".join(f"- {item}" for item in (jd.soft_required or [])[:5]) or "（无）"
    jd_context = get_match_pipe_block_text("writer_jd_context").format(
        company=jd.company,
        title=jd.title,
        role_type=jd.role_type,
        seniority=jd.seniority,
        team_direction=jd.team_direction or "（未说明）",
        tech_required=tech_required,
        tech_preferred=tech_preferred,
        or_groups=or_groups,
        or_group=or_groups,
        soft_required=soft_required,
    )
    parts = [_compose_candidate_context(jd.company)]
    if _is_bytedance_company(jd.company):
        special = get_match_pipe_block_text("retarget_bytedance_special")
        if special:
            parts.append(special)
    parts.extend(
        [
            jd_context,
            _compose_writer_user_header(jd.company),
            _compose_format_constraints(jd.company),
            get_match_pipe_block_text("output_contract"),
        ]
    )
    return "\n\n".join(part for part in parts if part.strip())


def build_match_pipe_unified_review_prompt(resume_md: str, jd, review_scope: str = "full") -> str:
    tech_required = ", ".join(jd.tech_required) if jd.tech_required else "（无）"
    tech_preferred = ", ".join(jd.tech_preferred) if jd.tech_preferred else "（无）"
    reviewer_user = get_match_pipe_block_text("reviewer_user")
    if _is_bytedance_company(jd.company):
        reviewer_user = _apply_reviewer_bytedance_branch(
            reviewer_user,
            get_match_pipe_block_text("reviewer_user_bytedance"),
        )
    review_context = _company_block_text("reviewer_context", jd.company).format(
        company=jd.company,
        title=jd.title,
        role_type=jd.role_type,
        seniority=jd.seniority,
        tech_required=tech_required,
        tech_preferred=tech_preferred,
        team_direction=jd.team_direction or "（未说明）",
        immutable_block=_immutable_block_for_company(jd.company),
        review_scope=review_scope,
        resume_md=resume_md,
    )
    parts = [reviewer_user, review_context]
    if _is_bytedance_company(jd.company):
        parts.append(get_match_pipe_block_text("reviewer_context_bytedance"))
    parts.append(get_match_pipe_block_text("reviewer_output_schema"))
    return "\n\n".join(part for part in parts if part.strip())


def build_match_pipe_seed_retarget_prompt(
    seed_resume_md: str,
    jd,
    *,
    seed_label: str = "",
    route_mode: str = "retarget",
    top_candidate: dict | None = None,
) -> str:
    top_candidate = top_candidate or {}
    tech_required = ", ".join(jd.tech_required) if jd.tech_required else "（无明确列出）"
    tech_preferred = ", ".join(jd.tech_preferred) if jd.tech_preferred else "（无）"
    missing_required = ", ".join(top_candidate.get("missing_required", [])[:8]) or "（无明显缺口）"
    retarget_context = get_match_pipe_block_text("retarget_context").format(
        seed_resume_md=seed_resume_md,
    )
    parts = [_company_block_text("retarget_prompt", jd.company)]
    if _is_bytedance_company(jd.company):
        special = get_match_pipe_block_text("retarget_bytedance_special")
        if special:
            parts.append(special)
    same_company = bool(top_candidate.get("same_company"))
    if same_company:
        parts.append(
            get_match_pipe_block_text(
                "retarget_same_company_bytedance" if _is_bytedance_company(jd.company) else "retarget_same_company"
            )
        )
    parts.extend(
        [
            get_match_pipe_block_text("retarget_project_pool"),
            retarget_context,
            _compose_format_constraints(jd.company),
            get_match_pipe_block_text("output_contract"),
        ]
    )
    return "\n\n".join(part for part in parts if part.strip())


def build_match_pipe_upgrade_revision_prompt(
    resume_md: str,
    review_result: dict,
    *,
    tech_required: list[str] | None = None,
    jd_title: str = "",
    target_company: str = "",
    route_mode: str = "",
    seed_label: str = "",
) -> str:
    priority = "\n".join(f"{idx + 1}. {item}" for idx, item in enumerate(review_result.get("revision_priority", []) or [])) or "1. Raise the resume to a stronger pass."
    findings: list[str] = []
    for dim_id, dim_data in (review_result.get("scores", {}) or {}).items():
        for finding in dim_data.get("findings", []):
            if str(finding.get("severity", "")).lower() in {"critical", "high", "medium"}:
                findings.append(
                    f"[{dim_id}] [{str(finding.get('severity', '')).upper()}] {finding.get('field', '')}: {finding.get('issue', '')} -> {finding.get('fix', '')}"
                )
    findings_block = "\n".join(f"- {item}" for item in findings) or "- 无结构化高优先发现"
    tech_line = ", ".join(tech_required or []) or "（无明确 must-have 技术）"
    upgrade_context = get_match_pipe_block_text("upgrade_context").format(
        resume_md=resume_md,
    )
    parts = [_company_block_text("upgrade_prompt", target_company)]
    if _is_bytedance_company(target_company):
        special = get_match_pipe_block_text("upgrade_bytedance_special")
        if special:
            parts.append(special)
    parts.extend(
        [
            upgrade_context,
            _compose_format_constraints(target_company),
            get_match_pipe_block_text("output_contract"),
        ]
    )
    return "\n\n".join(part for part in parts if part.strip())


def build_match_pipe_planner_prompt(
    *,
    jd,
    mode: str,
    matcher_packet: dict[str, Any] | None = None,
    starter_resume_md: str = "",
) -> str:
    matcher_block = json.dumps(matcher_packet or {}, indent=2, ensure_ascii=False)
    starter_block = starter_resume_md if starter_resume_md else "（无 starter resume）"
    planner_context = get_match_pipe_block_text("planner_context").format(
        mode=mode,
        company=jd.company,
        title=jd.title,
        role_type=jd.role_type,
        seniority=jd.seniority,
        tech_required=jd.tech_required,
        tech_preferred=jd.tech_preferred,
        matcher_block=matcher_block,
        starter_block=starter_block,
    )
    return f"""{get_match_pipe_block_text("planner_user")}

{planner_context}"""


def build_match_pipe_writer_prompt_from_planner(
    *,
    jd,
    planner_payload: dict[str, Any],
    starter_resume_md: str = "",
    matcher_packet: dict[str, Any] | None = None,
) -> str:
    planner_json = json.dumps(planner_payload, indent=2, ensure_ascii=False)
    matcher_json = json.dumps(matcher_packet or {}, indent=2, ensure_ascii=False)
    starter_block = starter_resume_md if starter_resume_md else "（无 starter resume）"
    planner_writer_context = get_match_pipe_block_text("planner_writer_context").format(
        planner_json=planner_json,
        matcher_json=matcher_json,
        starter_block=starter_block,
    )
    return f"""{build_match_pipe_master_writer_prompt(jd)}

{planner_writer_context}

{get_match_pipe_block_text("planner_writer_overlay")}"""


def build_match_pipe_writer_revision_prompt(current_resume_md: str, review, jd, planner_payload: dict[str, Any]) -> str:
    planner_notes = "\n".join(f"- {item}" for item in planner_payload.get("writer_plan", [])) or "- 无额外 writer plan"
    risk_notes = "\n".join(f"- {item}" for item in planner_payload.get("risk_flags", [])) or "- 无额外风险"
    priority = "\n".join(f"{idx + 1}. {item}" for idx, item in enumerate(review.revision_priority or [])) or "1. Raise the resume to a stronger pass."
    findings: list[str] = []
    for dim_id, dim in review.dimensions.items():
        for finding in dim.findings:
            if finding.get("severity") in {"critical", "high", "medium"}:
                findings.append(
                    f"[{dim_id}] [{str(finding.get('severity', '')).upper()}] {finding.get('field', '')}: {finding.get('issue', '')} -> {finding.get('fix', '')}"
                )
    findings_block = "\n".join(f"- {item}" for item in findings) or "- 无结构化高优先发现"
    must_have = ", ".join(jd.tech_required) if jd.tech_required else "（无明确 must-have）"
    planner_revision_context = get_match_pipe_block_text("planner_revision_context").format(
        weighted_score=f"{review.weighted_score:.1f}",
        passed="PASS" if review.passed else "FAIL",
        needs_revision="是" if review.needs_revision else "否",
        planner_notes=planner_notes,
        risk_notes=risk_notes,
        priority=priority,
        findings_block=findings_block,
        must_have=must_have,
        current_resume_md=current_resume_md,
    )
    return f"""{build_match_pipe_master_writer_prompt(jd)}

{planner_revision_context}

{get_match_pipe_block_text("planner_revision_overlay")}"""


def append_match_pipe_dual_channel_overlay(
    prompt: str,
    *,
    delta_summary: list[str] | None = None,
    continuity_anchor: dict[str, Any] | None = None,
) -> str:
    return prompt + "\n\n" + _render_dual_channel_overlay(
        delta_summary=delta_summary,
        continuity_anchor=continuity_anchor,
    )
