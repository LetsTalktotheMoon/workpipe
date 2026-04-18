"""
Prompt Path Comparator — 直观对比 match_pipe 三条链路在同一角色下的 prompt 差异。
"""
from __future__ import annotations

import difflib
import sys
from pathlib import Path
from typing import Iterable

import yaml

ROOT = Path(__file__).resolve().parent
BLOCKS_DIR = ROOT / "blocks"
VIEWS_DIR = ROOT / "views"

# 角色 -> 需要对比的 view_id 映射（覆盖三条核心链路）
ROLE_VIEW_MAP: dict[str, dict[str, str]] = {
    "writer": {
        "no_starter": "prompt_writer_generate",
        "old_match": "prompt_retarget_old_match",
        "new_dual_channel": "prompt_dual_channel_full",
    },
    "reviewer": {
        "no_starter": "prompt_reviewer_full",
        "old_match": "prompt_reviewer_full",
        "new_dual_channel": "prompt_reviewer_full",
    },
    "revision_writer": {
        "no_starter": "prompt_upgrade_revision",
        "old_match": "prompt_upgrade_revision",
        "new_dual_channel": "prompt_upgrade_revision",
    },
    "planner": {
        "no_starter": "prompt_planner_user",
        "old_match": "prompt_planner_user",  # downstream 没有 planner，但 planner runner 里的 new_dual_channel_planner 会用它
        "new_dual_channel": "prompt_planner_user",
    },
    "planner_writer": {
        "no_starter": "prompt_planner_writer_full",
        "old_match": "prompt_planner_writer_full",
        "new_dual_channel": "prompt_planner_writer_full",
    },
    "planner_revision_writer": {
        "no_starter": "prompt_planner_revision_full",
        "old_match": "prompt_planner_revision_full",
        "new_dual_channel": "prompt_planner_revision_full",
    },
}


def load_view(view_id: str) -> dict:
    path = VIEWS_DIR / f"{view_id}.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def render_view_flat(view_id: str, context: dict | None = None) -> str:
    """仅做静态拼接（不展开 Jinja2 变量），用于结构对比。"""
    view = load_view(view_id)
    parts = []
    sb = view.get("system_block")
    if sb:
        parts.append(f"[SYSTEM: {sb}]\n{load_block_text(sb)}")
    for bid in view.get("user_blocks", []):
        parts.append(f"[BLOCK: {bid}]\n{load_block_text(bid)}")
    return "\n\n".join(parts)


def load_block_text(block_id: str) -> str:
    path = BLOCKS_DIR / f"{block_id}.jinja2"
    if not path.exists():
        return f"[MISSING: {block_id}]"
    return path.read_text(encoding="utf-8").strip()


def ansi_same(text: str) -> str:
    return f"\033[90m{text}\033[0m"


def ansi_diff_a(text: str) -> str:
    return f"\033[91m{text}\033[0m"


def ansi_diff_b(text: str) -> str:
    return f"\033[92m{text}\033[0m"


def unified_diff_lines(a: str, b: str, a_name: str = "A", b_name: str = "B") -> Iterable[str]:
    la = a.splitlines()
    lb = b.splitlines()
    for line in difflib.unified_diff(la, lb, fromfile=a_name, tofile=b_name, lineterm=""):
        yield line


def side_by_side_diff(a: str, b: str, width: int = 80) -> Iterable[str]:
    """生成并排的相同/差异行，带 ANSI 颜色。"""
    sm = difflib.SequenceMatcher(None, a.splitlines(), b.splitlines())
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        a_lines = a.splitlines()[i1:i2]
        b_lines = b.splitlines()[j1:j2]
        max_len = max(len(a_lines), len(b_lines))
        for idx in range(max_len):
            a_line = a_lines[idx] if idx < len(a_lines) else ""
            b_line = b_lines[idx] if idx < len(b_lines) else ""
            a_display = a_line[:width].ljust(width)
            b_display = b_line[:width].ljust(width)
            if tag == "equal":
                yield f"  {ansi_same(a_display)} │ {ansi_same(b_display)}"
            else:
                yield f"  {ansi_diff_a(a_display)} │ {ansi_diff_b(b_display)}"


def block_level_diff(view_a: str, view_b: str) -> Iterable[str]:
    """在 block 粒度上对比两个 view：显示共同 block、独有 block。"""
    va = load_view(view_a)
    vb = load_view(view_b)
    a_blocks = tuple([va.get("system_block") or ""] + list(va.get("user_blocks", [])))
    b_blocks = tuple([vb.get("system_block") or ""] + list(vb.get("user_blocks", [])))
    sm = difflib.SequenceMatcher(None, a_blocks, b_blocks)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for bid in a_blocks[i1:i2]:
                if bid:
                    yield f"  [SHARED]  {bid}"
        elif tag == "replace":
            for bid_a, bid_b in zip(a_blocks[i1:i2], b_blocks[j1:j2]):
                yield f"  [DIFF]    {bid_a}  →  {bid_b}"
        elif tag == "delete":
            for bid in a_blocks[i1:i2]:
                if bid:
                    yield f"  [ONLY A]  {bid}"
        elif tag == "insert":
            for bid in b_blocks[j1:j2]:
                if bid:
                    yield f"  [ONLY B]  {bid}"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Compare match_pipe prompt paths")
    parser.add_argument("--role", default="writer", choices=list(ROLE_VIEW_MAP.keys()))
    parser.add_argument("--path-a", default="no_starter")
    parser.add_argument("--path-b", default="new_dual_channel")
    parser.add_argument("--mode", choices=["blocks", "side", "unified"], default="blocks")
    args = parser.parse_args()

    mapping = ROLE_VIEW_MAP[args.role]
    view_a = mapping.get(args.path_a)
    view_b = mapping.get(args.path_b)
    if not view_a or not view_b:
        print(f"Unknown path for role '{args.role}'")
        sys.exit(1)

    print(f"\n{'='*80}")
    print(f"Role: {args.role}")
    print(f"Comparing: {args.path_a}  vs  {args.path_b}")
    print(f"Views: {view_a}  vs  {view_b}")
    print(f"{'='*80}\n")

    if args.mode == "blocks":
        print("[Block-level structural diff]")
        for line in block_level_diff(view_a, view_b):
            print(line)
    elif args.mode == "side":
        print("[Side-by-side line diff]")
        a_text = render_view_flat(view_a)
        b_text = render_view_flat(view_b)
        for line in side_by_side_diff(a_text, b_text):
            print(line)
    elif args.mode == "unified":
        a_text = render_view_flat(view_a)
        b_text = render_view_flat(view_b)
        for line in unified_diff_lines(a_text, b_text, a_name=view_a, b_name=view_b):
            print(line)

    print("\n")


if __name__ == "__main__":
    main()
