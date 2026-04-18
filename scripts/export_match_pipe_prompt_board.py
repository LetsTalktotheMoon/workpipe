#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.job_webapp.prompt_library import build_match_pipe_prompt_library

OUT_DIR = ROOT / "artifacts"
OUT_HTML = OUT_DIR / "match_pipe_prompt_board.html"
OUT_JSON = OUT_DIR / "match_pipe_prompt_board.json"


PROMPT_IDS = [
    "prompt_writer_system",
    "prompt_writer_generate",
    "prompt_writer_generate_bytedance",
    "prompt_strict_revision_system",
    "prompt_upgrade_system",
    "prompt_reviewer_system",
    "prompt_reviewer_full",
    "prompt_reviewer_full_bytedance",
    "prompt_retarget_old_match",
    "prompt_retarget_same_company",
    "prompt_retarget_old_match_bytedance",
    "prompt_upgrade_revision",
    "prompt_upgrade_revision_bytedance",
    "prompt_planner_system",
    "prompt_planner_user",
    "prompt_planner_writer_full",
    "prompt_planner_writer_full_bytedance",
    "prompt_planner_revision_full",
    "prompt_planner_revision_full_bytedance",
    "prompt_dual_channel_full",
    "prompt_dual_channel_full_bytedance",
]


BLOCK_IDS = [
    "planner_context",
    "planner_writer_context",
    "planner_writer_overlay",
    "planner_revision_context",
    "planner_revision_overlay",
    "retarget_context",
    "retarget_project_pool",
    "retarget_same_company",
    "retarget_same_company_bytedance",
    "retarget_bytedance_special",
    "upgrade_context",
    "upgrade_bytedance_special",
    "dual_channel_overlay",
    "reviewer_user",
    "reviewer_user_bytedance",
    "reviewer_context",
    "reviewer_context_bytedance",
    "reviewer_output_schema",
    "candidate_context_bytedance_education_branch",
    "candidate_context_bytedance_boundary",
    "format_constraints_branch_bytedance",
]


CANONICAL_SOURCE_MAP = {
    "writer_system": [
        {"label": "canonical constant", "path": "runtime/core/prompt_builder.py", "line": 413},
        {"label": "runtime wrapper", "path": "runtime/job_webapp/prompt_library.py", "line": 2741},
    ],
    "strict_revision_system": [
        {"label": "canonical constant", "path": "runtime/writers/master_writer.py", "line": 38},
        {"label": "runtime wrapper", "path": "runtime/job_webapp/prompt_library.py", "line": 2745},
    ],
    "upgrade_revision_system": [
        {"label": "canonical constant", "path": "runtime/writers/master_writer.py", "line": 42},
        {"label": "runtime wrapper", "path": "runtime/job_webapp/prompt_library.py", "line": 2749},
    ],
    "reviewer_system": [
        {"label": "canonical constant", "path": "runtime/core/prompt_builder.py", "line": 571},
        {"label": "runtime wrapper", "path": "runtime/job_webapp/prompt_library.py", "line": 2753},
    ],
    "master_writer_prompt": [
        {"label": "canonical builder", "path": "runtime/core/prompt_builder.py", "line": 478},
        {"label": "runtime wrapper", "path": "runtime/job_webapp/prompt_library.py", "line": 2761},
    ],
    "review_prompt": [
        {"label": "canonical builder", "path": "runtime/core/prompt_builder.py", "line": 595},
        {"label": "runtime wrapper", "path": "runtime/job_webapp/prompt_library.py", "line": 2794},
    ],
    "seed_retarget_prompt": [
        {"label": "canonical builder", "path": "runtime/core/prompt_builder.py", "line": 881},
        {"label": "runtime wrapper", "path": "runtime/job_webapp/prompt_library.py", "line": 2822},
    ],
    "upgrade_revision_prompt": [
        {"label": "canonical builder", "path": "runtime/core/prompt_builder.py", "line": 976},
        {"label": "runtime wrapper", "path": "runtime/job_webapp/prompt_library.py", "line": 2860},
    ],
    "planner_prompt": [
        {"label": "runtime-only builder", "path": "runtime/job_webapp/prompt_library.py", "line": 2898},
        {"label": "planner runner callsite", "path": "match_pipe/planner_validation_runner.py", "line": 171},
    ],
    "planner_writer_prompt": [
        {"label": "runtime-only builder", "path": "runtime/job_webapp/prompt_library.py", "line": 2923},
        {"label": "planner runner callsite", "path": "match_pipe/planner_validation_runner.py", "line": 346},
    ],
    "planner_revision_prompt": [
        {"label": "runtime-only builder", "path": "runtime/job_webapp/prompt_library.py", "line": 2945},
        {"label": "planner runner callsite", "path": "match_pipe/planner_validation_runner.py", "line": 303},
    ],
    "dual_channel_overlay": [
        {"label": "runtime-only builder", "path": "runtime/job_webapp/prompt_library.py", "line": 2976},
        {"label": "downstream runner callsite", "path": "match_pipe/downstream_validation_runner.py", "line": 305},
    ],
}


EVIDENCE_SAMPLES = [
    {
        "chain": "测试链路 no_starter 的落盘近似映射",
        "path": "data/deliverables/resume_portfolio/by_company/amazon/2026-04-03/6996d6d0ce78e77b4fdb0c7f",
        "mapping_note": "样本层没有字面值 `no_starter`；此处只能以 `seed_source` 作为最佳近似映射。",
    },
    {
        "chain": "测试链路 new_dual_channel 的落盘近似映射",
        "path": "data/deliverables/resume_portfolio/by_company/amazon-web-services-aws/2026-04-04/69d0ff1554f00230c6d17d6a",
        "mapping_note": "样本层没有字面值 `new_dual_channel`；此处只能以 `new_seed` / `retarget_trial` 作为最佳近似映射。",
    },
    {
        "chain": "主链路 retarget / review / revision / upgrade",
        "path": "data/deliverables/resume_portfolio/by_company/apple/2026-04-02/69cf3064891d7b11cfcd0cb8",
        "mapping_note": "这是样本层最接近字面 route 的 `retarget` 主链路证据。",
    },
]


FLOW_SECTIONS = [
    {
        "title": "1. 测试链路：no_starter - direct/planner_first - write/review/upgrade",
        "chains": [
            {
                "name": "no_starter / direct",
                "badge": "direct",
                "steps": [
                    {
                        "label": "Writer",
                        "role": "writer",
                        "summary": "从零生成。",
                        "refs": ["prompt_writer_system", "prompt_writer_generate"],
                    },
                    {
                        "label": "Reviewer",
                        "role": "reviewer",
                        "summary": "统一 full review。",
                        "refs": ["prompt_reviewer_system", "prompt_reviewer_full"],
                    },
                    {
                        "label": "Upgrade Writer",
                        "role": "writer",
                        "summary": "若 `not passed && needs_revision`，最多 1 次。",
                        "refs": ["prompt_upgrade_system", "prompt_upgrade_revision"],
                    },
                    {
                        "label": "Re-review",
                        "role": "reviewer",
                        "summary": "复用同一 reviewer prompt。",
                        "refs": ["prompt_reviewer_system", "prompt_reviewer_full"],
                    },
                ],
            },
            {
                "name": "no_starter / planner_first",
                "badge": "planner_first",
                "steps": [
                    {
                        "label": "Planner",
                        "role": "planner",
                        "summary": "`mode=no_starter`，强约束只允许 `decision=write`。",
                        "refs": ["prompt_planner_system", "prompt_planner_user"],
                    },
                    {
                        "label": "Writer",
                        "role": "writer",
                        "summary": "共享 writer 主干 + planner carry-over。",
                        "refs": ["prompt_writer_system", "prompt_planner_writer_full"],
                    },
                    {
                        "label": "Reviewer",
                        "role": "reviewer",
                        "summary": "统一 full review。",
                        "refs": ["prompt_reviewer_system", "prompt_reviewer_full"],
                    },
                    {
                        "label": "Planner Revision",
                        "role": "writer",
                        "summary": "升级 system prompt + planner revision context/overlay。",
                        "refs": ["prompt_upgrade_system", "prompt_planner_revision_full"],
                    },
                    {
                        "label": "Re-review",
                        "role": "reviewer",
                        "summary": "仍是同一 reviewer bundle。",
                        "refs": ["prompt_reviewer_system", "prompt_reviewer_full"],
                    },
                ],
            },
        ],
    },
    {
        "title": "2. 测试链路：new_dual_channel - direct/planner_first - write/review/upgrade",
        "chains": [
            {
                "name": "new_dual_channel / direct",
                "badge": "direct",
                "steps": [
                    {
                        "label": "Writer",
                        "role": "writer",
                        "summary": "strict revision system + retarget prompt + dual-channel continuity overlay。",
                        "refs": ["prompt_strict_revision_system", "prompt_dual_channel_full"],
                    },
                    {
                        "label": "Conditional",
                        "role": "writer",
                        "summary": "若 continuity anchor same company，则额外叠加 same-company 分支。",
                        "refs": ["prompt_retarget_same_company", "retarget_same_company", "retarget_same_company_bytedance"],
                    },
                    {
                        "label": "Reviewer",
                        "role": "reviewer",
                        "summary": "统一 full review。",
                        "refs": ["prompt_reviewer_system", "prompt_reviewer_full"],
                    },
                    {
                        "label": "Upgrade Writer",
                        "role": "writer",
                        "summary": "review 失败后升级式 revision。",
                        "refs": ["prompt_upgrade_system", "prompt_upgrade_revision"],
                    },
                    {
                        "label": "Re-review",
                        "role": "reviewer",
                        "summary": "复用 reviewer prompt。",
                        "refs": ["prompt_reviewer_system", "prompt_reviewer_full"],
                    },
                ],
            },
            {
                "name": "new_dual_channel / planner_first",
                "badge": "planner_first",
                "steps": [
                    {
                        "label": "Planner",
                        "role": "planner",
                        "summary": "读 matcher packet + starter resume，可能给出 `write` / `reject_starter` / `direct_review`。",
                        "refs": ["prompt_planner_system", "prompt_planner_user", "planner_context"],
                    },
                    {
                        "label": "Branch A",
                        "role": "reviewer",
                        "summary": "`decision=direct_review` 且存在 starter 时，跳过 writer，直接 review starter。",
                        "refs": ["prompt_reviewer_system", "prompt_reviewer_full"],
                    },
                    {
                        "label": "Branch B",
                        "role": "writer",
                        "summary": "`decision=reject_starter` 或 `write` 时，进入 planner-guided writer。",
                        "refs": ["prompt_writer_system", "prompt_planner_writer_full"],
                    },
                    {
                        "label": "Planner Revision",
                        "role": "writer",
                        "summary": "review 失败后统一进入 planner revision；`direct_review` 路径理论上可触发更多 writer rounds。",
                        "refs": ["prompt_upgrade_system", "prompt_planner_revision_full"],
                    },
                    {
                        "label": "Re-review",
                        "role": "reviewer",
                        "summary": "复用 reviewer full prompt。",
                        "refs": ["prompt_reviewer_system", "prompt_reviewer_full"],
                    },
                ],
            },
        ],
    },
    {
        "title": "3. 主链路：retarget / review / revision / upgrade",
        "chains": [
            {
                "name": "retarget / review / revision / upgrade",
                "badge": "mainline",
                "steps": [
                    {
                        "label": "Writer",
                        "role": "writer",
                        "summary": "decide_route 先选 seed，再用 strict revision system + retarget prompt 改写。",
                        "refs": ["prompt_strict_revision_system", "prompt_retarget_old_match"],
                    },
                    {
                        "label": "Same Company",
                        "role": "writer",
                        "summary": "`top_candidate.same_company=true` 时额外叠加同公司一致性 prompt。",
                        "refs": ["prompt_retarget_same_company", "retarget_same_company", "retarget_same_company_bytedance"],
                    },
                    {
                        "label": "Reviewer",
                        "role": "reviewer",
                        "summary": "统一 reviewer full prompt。",
                        "refs": ["prompt_reviewer_system", "prompt_reviewer_full"],
                    },
                    {
                        "label": "Upgrade Writer",
                        "role": "writer",
                        "summary": "upgrade revision prompt，最多 1 次 adoption loop。",
                        "refs": ["prompt_upgrade_system", "prompt_upgrade_revision"],
                    },
                    {
                        "label": "Re-review",
                        "role": "reviewer",
                        "summary": "复用 reviewer prompt，决定是否采纳 revision。",
                        "refs": ["prompt_reviewer_system", "prompt_reviewer_full"],
                    },
                ],
            }
        ],
    },
]


PLACEHOLDER_RE = re.compile(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: str | Path) -> str:
    return str(Path(path).as_posix())


def placeholder_hits(text: str) -> list[str]:
    return sorted(set(PLACEHOLDER_RE.findall(text)))


def tag(text: str, kind: str) -> str:
    return f'<span class="tag {kind}">{html.escape(text)}</span>'


def file_link(path: str, line: int | None = None) -> str:
    target = ROOT / path
    suffix = f":{line}" if line else ""
    return f'<a href="file://{target}{suffix}">{html.escape(path + (f":{line}" if line else ""))}</a>'


def render_targets(targets: list[dict[str, Any]]) -> str:
    if not targets:
        return '<span class="muted">none</span>'
    items = []
    for item in targets:
        items.append(
            "<li>"
            f"{html.escape(item.get('pipeline', ''))} / {html.escape(item.get('stage', ''))} / {html.escape(item.get('role', ''))} "
            f"via {html.escape(item.get('label', ''))} @ {file_link(item.get('path', ''), item.get('line'))}"
            "</li>"
        )
    return "<ul>" + "".join(items) + "</ul>"


def render_source_map(refs: list[dict[str, Any]]) -> str:
    if not refs:
        return '<span class="muted">none</span>'
    items = []
    for ref in refs:
        items.append(f"<li>{html.escape(ref['label'])}: {file_link(ref['path'], ref['line'])}</li>")
    return "<ul>" + "".join(items) + "</ul>"


def load_samples() -> list[dict[str, Any]]:
    samples = []
    for sample in EVIDENCE_SAMPLES:
        base = ROOT / sample["path"]
        manifest = read_json(base / "manifest.json")
        review = read_json(base / "review.json")
        samples.append(
            {
                **sample,
                "manifest": {
                    key: manifest.get(key)
                    for key in [
                        "source_kind",
                        "route_mode",
                        "seed_id",
                        "seed_label",
                        "parent_seed_id",
                        "primary_subseed_kind",
                        "primary_subseed_id",
                        "primary_subseed_label",
                        "review_final_score",
                        "review_verdict",
                    ]
                },
                "top_candidate": manifest.get("top_candidate") or {},
                "review": {
                    key: review.get(key)
                    for key in [
                        "route_mode",
                        "seed_label",
                        "revised",
                        "rereview_rounds",
                        "rereview_revised",
                        "previous_final_score",
                        "previous_verdict",
                        "final_score",
                        "verdict",
                    ]
                },
                "review_has_revision_instructions": bool(review.get("revision_instructions")),
            }
        )
    return samples


def build_payload() -> dict[str, Any]:
    lib = build_match_pipe_prompt_library()
    prompt_map = {item["id"]: item for item in lib["prompts"]}
    block_map = {item["id"]: item for item in lib["blocks"]}
    override_payload = read_json(ROOT / "match_pipe/prompt_overrides.json")
    override_blocks = override_payload.get("blocks", {})

    selected_prompts = [prompt_map[prompt_id] for prompt_id in PROMPT_IDS]
    selected_blocks = [block_map[block_id] for block_id in BLOCK_IDS]

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "meta": lib["meta"],
        "flows": FLOW_SECTIONS,
        "prompts": selected_prompts,
        "blocks": selected_blocks,
        "canonical_source_map": CANONICAL_SOURCE_MAP,
        "override_blocks": {key: override_blocks[key] for key in sorted(override_blocks)},
        "samples": load_samples(),
        "notes": [
            "当前 HTML 以 runtime/job_webapp/prompt_library.py 渲染结果为准，因为当前 workspace 存在活跃的 match_pipe/prompt_overrides.json。",
            "same-company 分支已显式纳入，覆盖普通 retarget_same_company 和 ByteDance 专用 retarget_same_company_bytedance。",
            "样本层只能反推 route/seed lineage，不能直接反推出 prompt 正文；因此 deliverables/tests 只作为旁证，不作为 prompt 文本主来源。",
            "部分 runtime prompt 当前仍残留占位符，如 {experience_order}、{role_type}、{tech_required}、{priority} 等；这也是页面中单独标出的漂移点。",
        ],
    }


def render_flow_section(flow_group: dict[str, Any]) -> str:
    chains_html = []
    for chain in flow_group["chains"]:
        steps = []
        for idx, step in enumerate(chain["steps"], start=1):
            refs = "".join(
                f'<li><a href="#{html.escape(ref)}">{html.escape(ref)}</a></li>'
                for ref in step["refs"]
            )
            steps.append(
                '<div class="flow-step">'
                f'<div class="step-index">{idx}</div>'
                f'<div class="step-role">{html.escape(step["role"])}</div>'
                f'<h4>{html.escape(step["label"])}</h4>'
                f'<p>{html.escape(step["summary"])}</p>'
                f'<ul class="mini-list">{refs}</ul>'
                "</div>"
            )
        chains_html.append(
            '<div class="chain-card">'
            f'<div class="chain-head"><h3>{html.escape(chain["name"])}</h3>{tag(chain["badge"], "badge")}</div>'
            '<div class="flow-row">'
            + "".join(steps)
            + "</div></div>"
        )
    return f'<section class="panel"><h2>{html.escape(flow_group["title"])}</h2>{"".join(chains_html)}</section>'


def render_prompt_entry(item: dict[str, Any], kind: str) -> str:
    item_id = item["id"]
    text = item["rendered_text"] if kind == "prompt" else item["text"]
    placeholders = placeholder_hits(text)
    targets = item.get("targets") or item.get("target_refs") or []

    if item_id in {"prompt_writer_generate", "prompt_writer_generate_bytedance", "prompt_planner_writer_full", "prompt_planner_writer_full_bytedance"}:
        canonical_refs = CANONICAL_SOURCE_MAP["master_writer_prompt"]
    elif item_id in {"prompt_reviewer_full", "prompt_reviewer_full_bytedance", "reviewer_user", "reviewer_user_bytedance", "reviewer_context", "reviewer_context_bytedance", "reviewer_output_schema"}:
        canonical_refs = CANONICAL_SOURCE_MAP["review_prompt"]
    elif item_id in {"prompt_retarget_old_match", "prompt_retarget_old_match_bytedance", "prompt_dual_channel_full", "prompt_dual_channel_full_bytedance", "retarget_context", "retarget_project_pool", "retarget_same_company", "retarget_same_company_bytedance", "retarget_bytedance_special"}:
        canonical_refs = CANONICAL_SOURCE_MAP["seed_retarget_prompt"]
    elif item_id in {"prompt_upgrade_revision", "prompt_upgrade_revision_bytedance", "upgrade_context", "upgrade_bytedance_special"}:
        canonical_refs = CANONICAL_SOURCE_MAP["upgrade_revision_prompt"]
    elif item_id in {"prompt_planner_system", "prompt_planner_user", "planner_context"}:
        canonical_refs = CANONICAL_SOURCE_MAP["planner_prompt"]
    elif item_id in {"prompt_planner_revision_full", "prompt_planner_revision_full_bytedance", "planner_revision_context", "planner_revision_overlay"}:
        canonical_refs = CANONICAL_SOURCE_MAP["planner_revision_prompt"]
    elif item_id in {"planner_writer_context", "planner_writer_overlay"}:
        canonical_refs = CANONICAL_SOURCE_MAP["planner_writer_prompt"]
    elif item_id == "dual_channel_overlay":
        canonical_refs = CANONICAL_SOURCE_MAP["dual_channel_overlay"]
    else:
        canonical_refs = CANONICAL_SOURCE_MAP.get(item_id.replace("prompt_", ""), [])

    badges = [
        tag(kind, "kind"),
        tag(item.get("role", item.get("kind", "fragment")), "role"),
    ]
    if placeholders:
        badges.append(tag(f"placeholders: {', '.join(placeholders)}", "warn"))
    if item_id in {"retarget_same_company", "retarget_same_company_bytedance", "prompt_retarget_same_company"}:
        badges.append(tag("same-company", "accent"))
    if "bytedance" in item_id:
        badges.append(tag("bytedance", "accent"))

    meta_rows = [
        f"<tr><th>ID</th><td>{html.escape(item_id)}</td></tr>",
        f"<tr><th>Title</th><td>{html.escape(item.get('title', ''))}</td></tr>",
        f"<tr><th>Targets</th><td>{render_targets(targets)}</td></tr>",
        f"<tr><th>Canonical / upstream</th><td>{render_source_map(canonical_refs)}</td></tr>",
    ]
    if kind == "prompt":
        meta_rows.insert(2, f"<tr><th>Pipeline / stage / role</th><td>{html.escape(item['pipeline'])} / {html.escape(item['stage'])} / {html.escape(item['role'])}</td></tr>")
        meta_rows.insert(3, f"<tr><th>Block IDs</th><td>{', '.join(html.escape(x) for x in item['block_ids'])}</td></tr>")
    else:
        meta_rows.insert(2, f"<tr><th>Kind</th><td>{html.escape(item.get('kind', ''))}</td></tr>")
        meta_rows.insert(3, f"<tr><th>Source kind</th><td>{html.escape(item.get('source_kind', ''))}</td></tr>")

    return (
        f'<section class="panel prompt-card" id="{html.escape(item_id)}">'
        f'<div class="prompt-head"><h3>{html.escape(item.get("title", item_id))}</h3><div class="tags">{"".join(badges)}</div></div>'
        f'<table class="meta-table">{"".join(meta_rows)}</table>'
        f'<div class="copy-wrap"><button class="copy-btn" data-copy-target="{html.escape(item_id)}-text">Copy</button></div>'
        f'<pre id="{html.escape(item_id)}-text">{html.escape(text)}</pre>'
        "</section>"
    )


def render_samples(samples: list[dict[str, Any]]) -> str:
    cards = []
    for sample in samples:
        cards.append(
            '<section class="panel sample-card">'
            f'<h3>{html.escape(sample["chain"])}</h3>'
            f'<p>{html.escape(sample["mapping_note"])}</p>'
            f'<p><strong>artifact dir:</strong> {file_link(sample["path"])}</p>'
            f'<p><strong>manifest:</strong> {html.escape(json.dumps(sample["manifest"], ensure_ascii=False, indent=2))}</p>'
            f'<p><strong>top_candidate:</strong> {html.escape(json.dumps(sample["top_candidate"], ensure_ascii=False, indent=2))}</p>'
            f'<p><strong>review:</strong> {html.escape(json.dumps(sample["review"], ensure_ascii=False, indent=2))}</p>'
            f'<p><strong>revision_instructions_present:</strong> {html.escape(str(sample["review_has_revision_instructions"]))}</p>'
            "</section>"
        )
    return "".join(cards)


def render_override_blocks(override_blocks: dict[str, str]) -> str:
    cards = []
    for key, text in override_blocks.items():
        placeholders = placeholder_hits(text)
        badges = [tag("override", "kind")]
        if placeholders:
            badges.append(tag(f"placeholders: {', '.join(placeholders)}", "warn"))
        if "same_company" in key:
            badges.append(tag("same-company", "accent"))
        cards.append(
            f'<section class="panel prompt-card" id="override-{html.escape(key)}">'
            f'<div class="prompt-head"><h3>{html.escape(key)}</h3><div class="tags">{"".join(badges)}</div></div>'
            f'<p class="muted">source: {file_link("match_pipe/prompt_overrides.json", 1)}</p>'
            f'<div class="copy-wrap"><button class="copy-btn" data-copy-target="override-{html.escape(key)}-text">Copy</button></div>'
            f'<pre id="override-{html.escape(key)}-text">{html.escape(text)}</pre>'
            "</section>"
        )
    return "".join(cards)


def build_html(payload: dict[str, Any]) -> str:
    prompt_cards = "".join(render_prompt_entry(item, "prompt") for item in payload["prompts"])
    block_cards = "".join(render_prompt_entry(item, "block") for item in payload["blocks"])
    flow_cards = "".join(render_flow_section(item) for item in payload["flows"])
    sample_cards = render_samples(payload["samples"])
    override_cards = render_override_blocks(payload["override_blocks"])
    notes_html = "".join(f"<li>{html.escape(note)}</li>" for note in payload["notes"])

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Match Pipe Prompt Board</title>
  <style>
    :root {{
      --bg: #f4efe7;
      --panel: #fffdfa;
      --ink: #1d1b18;
      --muted: #6a655d;
      --line: #d7cfc2;
      --accent: #9c4f2d;
      --accent-soft: #f4d9c9;
      --warn: #8a2c2c;
      --warn-soft: #f6d4d4;
      --role: #284b63;
      --role-soft: #d8e7f0;
      --shadow: 0 12px 30px rgba(40, 31, 23, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", serif;
      background:
        radial-gradient(circle at top right, rgba(156,79,45,0.12), transparent 30%),
        linear-gradient(180deg, #f7f1e8 0%, var(--bg) 100%);
      color: var(--ink);
      line-height: 1.45;
    }}
    .shell {{
      max-width: 1480px;
      margin: 0 auto;
      padding: 24px;
    }}
    .hero {{
      background: var(--panel);
      border: 1px solid var(--line);
      box-shadow: var(--shadow);
      border-radius: 20px;
      padding: 24px;
      margin-bottom: 20px;
    }}
    h1, h2, h3, h4 {{
      margin: 0 0 10px;
      line-height: 1.15;
    }}
    h1 {{ font-size: 34px; }}
    h2 {{ font-size: 24px; margin-bottom: 16px; }}
    h3 {{ font-size: 20px; }}
    h4 {{ font-size: 16px; }}
    p, li {{ font-size: 15px; }}
    .muted {{ color: var(--muted); }}
    .grid {{
      display: grid;
      gap: 18px;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: var(--shadow);
      padding: 18px;
      margin-bottom: 18px;
    }}
    .hero-grid {{
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 18px;
    }}
    .tag {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 4px 10px;
      font-size: 12px;
      border: 1px solid transparent;
      margin-right: 6px;
      margin-bottom: 6px;
      font-weight: 700;
      letter-spacing: 0.02em;
    }}
    .tag.kind {{ background: #ece3d7; }}
    .tag.badge {{ background: var(--accent-soft); color: var(--accent); }}
    .tag.role {{ background: var(--role-soft); color: var(--role); }}
    .tag.warn {{ background: var(--warn-soft); color: var(--warn); }}
    .tag.accent {{ background: #efe5b9; color: #6a5600; }}
    .flow-row {{
      display: grid;
      gap: 14px;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    }}
    .chain-card {{
      border-top: 1px solid var(--line);
      padding-top: 14px;
      margin-top: 14px;
    }}
    .chain-card:first-of-type {{
      border-top: 0;
      padding-top: 0;
      margin-top: 0;
    }}
    .chain-head {{
      display: flex;
      gap: 12px;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 10px;
      flex-wrap: wrap;
    }}
    .flow-step {{
      border: 1px solid var(--line);
      background: linear-gradient(180deg, #fffefb 0%, #f9f4ec 100%);
      border-radius: 16px;
      padding: 14px;
      position: relative;
      min-height: 196px;
    }}
    .step-index {{
      width: 28px;
      height: 28px;
      border-radius: 50%;
      display: grid;
      place-items: center;
      background: var(--accent);
      color: white;
      font-weight: 700;
      margin-bottom: 10px;
    }}
    .step-role {{
      text-transform: uppercase;
      font-size: 11px;
      letter-spacing: 0.08em;
      color: var(--muted);
      margin-bottom: 6px;
    }}
    .mini-list {{
      padding-left: 18px;
      margin: 8px 0 0;
    }}
    .prompt-head {{
      display: flex;
      gap: 14px;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      margin-bottom: 10px;
    }}
    .tags {{
      text-align: right;
    }}
    .meta-table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 12px;
      table-layout: fixed;
    }}
    .meta-table th,
    .meta-table td {{
      border-top: 1px solid var(--line);
      padding: 8px 10px;
      vertical-align: top;
      font-size: 14px;
    }}
    .meta-table th {{
      width: 210px;
      color: var(--muted);
      text-align: left;
    }}
    pre {{
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      background: #201d18;
      color: #f8f2e8;
      border-radius: 14px;
      padding: 16px;
      font-size: 13px;
      line-height: 1.45;
      overflow-wrap: anywhere;
    }}
    code {{ font-family: "SFMono-Regular", "Menlo", "Consolas", monospace; }}
    a {{
      color: var(--accent);
      text-decoration: none;
      border-bottom: 1px solid rgba(156,79,45,0.25);
    }}
    .copy-wrap {{
      display: flex;
      justify-content: flex-end;
      margin-bottom: 8px;
    }}
    .copy-btn {{
      border: 1px solid var(--line);
      background: white;
      border-radius: 999px;
      padding: 8px 12px;
      font: inherit;
      cursor: pointer;
    }}
    .toc {{
      columns: 2 260px;
      column-gap: 28px;
      padding-left: 18px;
    }}
    .sample-card p {{
      white-space: pre-wrap;
      word-break: break-word;
      font-family: "SFMono-Regular", "Menlo", "Consolas", monospace;
      font-size: 13px;
      background: #faf5ee;
      border-radius: 12px;
      padding: 10px;
      margin: 8px 0;
    }}
    @media (max-width: 960px) {{
      .hero-grid {{ grid-template-columns: 1fr; }}
      .meta-table th {{ width: 140px; }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <div class="hero-grid">
        <div>
          <h1>Match Pipe Prompt Board</h1>
          <p>目标范围：`no_starter - direct/planner_first - write/review/upgrade`、`new_dual_channel - direct/planner_first - write/review/upgrade`、`retarget / review / revision / upgrade`，外加你刚补充的 `same company` 分支。</p>
          <p class="muted">生成时间：{html.escape(payload["generated_at"])} | runtime prompt 总数：{payload["meta"]["prompt_count"]} | active overrides：{len(payload["override_blocks"])}</p>
          <ul>{notes_html}</ul>
        </div>
        <div class="panel" style="margin:0;">
          <h2>目录</h2>
          <ol class="toc">
            <li><a href="#flow-map">总流程图</a></li>
            <li><a href="#samples">tests / deliverables 旁证</a></li>
            <li><a href="#runtime-prompts">运行时完整版 prompt</a></li>
            <li><a href="#runtime-blocks">条件 fragment / overlay / same-company</a></li>
            <li><a href="#overrides">当前 active overrides</a></li>
          </ol>
          <p class="muted">说明：本页面把 current runtime prompt 作为主文本，把 canonical source 作为上游追踪；如果两者漂移，以 runtime 为当前真实链路。</p>
        </div>
      </div>
    </section>

    <section class="panel" id="flow-map">
      <h2>总流程图</h2>
      <p>每个节点都标出角色与直接引用的 prompt id。planner-first 的 `direct_review` / `reject_starter`，以及主链路与 dual-channel 的 `same company` 条件，都在图中单独展开。</p>
      {flow_cards}
    </section>

    <section class="panel" id="samples">
      <h2>tests / deliverables 旁证</h2>
      <p>这些样本只用于反向确认 route/seed lineage、review/revision 是否落盘，以及样本层能看到哪些字段。它们不能直接还原 prompt 正文。</p>
      {sample_cards}
    </section>

    <section id="runtime-prompts">
      <h2>运行时完整版 Prompt</h2>
      <p class="muted">以下是当前 workspace 真正会被 runner 消费的完整 prompt bundle。`same-company` 的条件块不总是并进主 prompt，因此同时单列在下一个区块。</p>
      {prompt_cards}
    </section>

    <section id="runtime-blocks">
      <h2>条件 Fragment / Overlay / same-company</h2>
      <p class="muted">这些 block 不是每次都单独作为完整 prompt 发送，但它们属于链路上“所有可能环节”的一部分，尤其是 planner carry-over、dual-channel overlay、same-company、ByteDance 分支与 reviewer schema。</p>
      {block_cards}
    </section>

    <section id="overrides">
      <h2>当前 Active Overrides</h2>
      <p>这些就是当前 workspace 里把 runtime prompt 从 canonical builder 拉开的活动 override。页面上面展示的 runtime prompt 已经包含了这些改写；这里单列是为了追溯来源。</p>
      {override_cards}
    </section>
  </div>
  <script>
    for (const button of document.querySelectorAll('.copy-btn')) {{
      button.addEventListener('click', async () => {{
        const id = button.getAttribute('data-copy-target');
        const target = document.getElementById(id);
        if (!target) return;
        await navigator.clipboard.writeText(target.innerText);
        const old = button.textContent;
        button.textContent = 'Copied';
        setTimeout(() => button.textContent = old, 1200);
      }});
    }}
  </script>
</body>
</html>
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_HTML.write_text(build_html(payload), encoding="utf-8")
    print(OUT_HTML)
    print(OUT_JSON)


if __name__ == "__main__":
    main()
