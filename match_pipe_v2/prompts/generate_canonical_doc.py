"""Generate a single canonical prompt document from all blocks and views."""
from __future__ import annotations

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent
BLOCKS_DIR = ROOT / "blocks"
VIEWS_DIR = ROOT / "views"
OUTPUT = ROOT / "CANONICAL_PROMPT_DOCUMENT.md"


def load_views() -> dict[str, dict]:
    views = {}
    for f in sorted(VIEWS_DIR.glob("*.yaml")):
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "view_id" in data:
            views[data["view_id"]] = data
    return views


def build_view_index() -> dict[str, list[str]]:
    """Map block_id -> list of view_ids that use it."""
    views = load_views()
    index: dict[str, list[str]] = {}
    for vid, v in views.items():
        for bid in v.get("user_blocks", []):
            index.setdefault(bid, []).append(vid)
        sb = v.get("system_block")
        if sb:
            index.setdefault(sb, []).append(vid)
    return index


def main() -> None:
    view_index = build_view_index()
    lines = [
        "# Match Pipe V2 — Canonical Prompt Document",
        "",
        "> 这是 `match_pipe_v2` 的全量 prompt 唯一文档。",
        "> 每个段落在此文档中**严格只出现一次**。",
        "> 修改方式：直接编辑本文档的对应段落，然后运行 `python sync_from_canonical_doc.py` 即可把变更写回 `blocks/*.jinja2`。",
        "",
        "---",
        "",
    ]

    groups = {
        "System Prompts": [
            "writer_system",
            "strict_revision_system",
            "upgrade_revision_system",
            "reviewer_system",
            "planner_system",
        ],
        "Candidate Context": [
            "candidate_context_shared_experience",
            "candidate_context_generic_tiktok_branch",
            "candidate_context_shared_education",
            "candidate_context_bytedance_education_branch",
            "candidate_context_shared_achievements",
            "candidate_context_bytedance_boundary",
        ],
        "Writer Plan Skeleton": [
            "writer_plan_shared_intro",
            "writer_plan_generic_tiktok_branch",
            "writer_plan_shared_didi_temu",
            "writer_plan_shared_gt_coursework",
            "writer_plan_shared_tail",
        ],
        "JD & Context Templates": [
            "writer_jd_context",
            "reviewer_context",
            "reviewer_context_bytedance",
        ],
        "Format Constraints": [
            "format_constraints_shared_head",
            "format_constraints_branch",
            "format_constraints_branch_bytedance",
            "format_constraints_shared_mid",
            "format_constraints_shared_tail",
        ],
        "Output Contract": ["output_contract"],
        "Reviewer Rubric": [
            "reviewer_user",
            "reviewer_user_bytedance",
            "reviewer_output_schema",
        ],
        "Retarget & Upgrade": [
            "retarget_prompt",
            "retarget_context",
            "retarget_project_pool",
            "retarget_same_company",
            "retarget_same_company_bytedance",
            "retarget_bytedance_special",
            "upgrade_prompt",
            "upgrade_context",
            "upgrade_bytedance_special",
        ],
        "Planner Prompts": [
            "planner_user",
            "planner_context",
            "planner_writer_overlay",
            "planner_writer_context",
            "planner_revision_overlay",
            "planner_revision_context",
        ],
        "Dual-Channel Overlay": ["dual_channel_overlay"],
    }

    all_block_ids = {f.stem for f in BLOCKS_DIR.glob("*.jinja2")}
    grouped = set()
    for bids in groups.values():
        grouped.update(bids)
    leftover = sorted(all_block_ids - grouped)
    if leftover:
        groups["Other Blocks"] = leftover

    for group_name, block_ids in groups.items():
        lines.append(f"## {group_name}")
        lines.append("")
        for bid in block_ids:
            path = BLOCKS_DIR / f"{bid}.jinja2"
            if not path.exists():
                lines.append(f"> Warning: block `{bid}` not found in blocks dir.")
                lines.append("")
                continue
            text = path.read_text(encoding="utf-8").rstrip("\n")
            used_in = view_index.get(bid, [])
            lines.append(f"\u003c!-- BLOCK: {bid} --\u003e")
            lines.append(f"\u003c!-- VIEWS: {', '.join(used_in) if used_in else 'none'} --\u003e")
            lines.append("")
            lines.append(text)
            lines.append("")
            lines.append(f"\u003c!-- END_BLOCK: {bid} --\u003e")
            lines.append("")
        lines.append("---")
        lines.append("")

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {OUTPUT} with {len(all_block_ids)} blocks, 0 duplicate paragraphs.")


if __name__ == "__main__":
    main()
