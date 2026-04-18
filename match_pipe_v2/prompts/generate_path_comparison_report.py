"""
生成交互式 HTML 报告：并排对比 match_pipe 各链路的完整 prompt。
核心特性：
  1. 完整视图 — 每个 view 显示完整的自然语言 prompt，无删减
  2. 共享句子联动编辑 — 修改一处，所有 view 中相同文本同步更新
  3. 语义对齐表 — 保留传统的段落级对比
  4. ByteDance 变体对比专页
"""
from __future__ import annotations

import difflib
import html
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1]))

from match_pipe_v2.registry import PromptRegistry

BLOCKS_DIR = ROOT / "blocks"
VIEWS_DIR = ROOT / "views"
OUTPUT = ROOT / "PATH_COMPARISON_REPORT.html"

PATHS = ["no_starter", "old_match", "new_dual_channel"]
ROLES = ["writer", "reviewer", "revision_writer", "planner", "planner_writer", "planner_revision_writer"]

ROLE_LABELS = {
    "writer": "Writer (主生成 / Retarget / Dual-channel)",
    "reviewer": "Reviewer (统一审查)",
    "revision_writer": "Revision Writer (升级重写)",
    "planner": "Planner (流程决策)",
    "planner_writer": "Planner-first Writer",
    "planner_revision_writer": "Planner-first Revision Writer",
}

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
        "old_match": "prompt_planner_user",
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

BYTEDANCE_ROLES = ["writer", "revision_writer", "planner_writer", "planner_revision_writer"]
BYTEDANCE_ROLE_LABELS = {
    "writer": "Writer — ByteDance 分支",
    "revision_writer": "Revision Writer — ByteDance 分支",
    "planner_writer": "Planner-first Writer — ByteDance 分支",
    "planner_revision_writer": "Planner-first Revision Writer — ByteDance 分支",
}
BYTEDANCE_ROLE_VIEW_MAP: dict[str, dict[str, str]] = {
    "writer": {
        "no_starter": "prompt_writer_generate_bytedance",
        "old_match": "prompt_retarget_old_match_bytedance",
        "new_dual_channel": "prompt_dual_channel_full_bytedance",
    },
    "revision_writer": {
        "no_starter": "prompt_upgrade_revision_bytedance",
        "old_match": "prompt_upgrade_revision_bytedance",
        "new_dual_channel": "prompt_upgrade_revision_bytedance",
    },
    "planner_writer": {
        "no_starter": "prompt_planner_writer_full_bytedance",
        "old_match": "prompt_planner_writer_full_bytedance",
        "new_dual_channel": "prompt_planner_writer_full_bytedance",
    },
    "planner_revision_writer": {
        "no_starter": "prompt_planner_revision_full_bytedance",
        "old_match": "prompt_planner_revision_full_bytedance",
        "new_dual_channel": "prompt_planner_revision_full_bytedance",
    },
}

VARIANT_SUFFIXES = [
    "_bytedance",
    "_generic_tiktok_branch",
    "_same_company_bytedance",
    "_same_company",
]


class _MockContext(dict):
    def __missing__(self, key):
        return f"{{{{ {key} }}}}"


_REGISTRY = PromptRegistry.from_dir(ROOT)
_SENTENCES = _REGISTRY._data.get("sentences", {})
_VIEWS = sorted(_REGISTRY.list_views())
_VIEW_META: dict[str, dict] = {}
for vf in sorted(VIEWS_DIR.glob("*.yaml")):
    data = yaml.safe_load(vf.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "view_id" in data:
        _VIEW_META[data["view_id"]] = data


def _load_view(view_id: str) -> dict:
    path = VIEWS_DIR / f"{view_id}.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _render_block(block_id: str) -> str:
    try:
        return _REGISTRY.render_block(block_id, context=_MockContext()).strip()
    except Exception as e:
        return f"[ERROR rendering {block_id}: {e}]"


def _get_view_blocks(view_id: str) -> list[tuple[str, str]]:
    view = _load_view(view_id)
    out: list[tuple[str, str]] = []
    sb = view.get("system_block")
    if sb:
        out.append((sb, _render_block(sb)))
    for item in view.get("user_blocks", []):
        if isinstance(item, str):
            out.append((item, _render_block(item)))
        elif isinstance(item, dict):
            out.append((item["block_id"], _render_block(item["block_id"])))
    return out


def base_name(block_id: str) -> str:
    for suffix in VARIANT_SUFFIXES:
        if block_id.endswith(suffix):
            return block_id[: -len(suffix)]
    return block_id


def _build_js_data() -> str:
    """Prepare JS-friendly data structures for the interactive report."""
    blocks_data: dict[str, str] = {}
    views_data: dict[str, list[tuple[str, str]]] = {}
    for vid in _VIEWS:
        views_data[vid] = _get_view_blocks(vid)
        for bid, text in views_data[vid]:
            if bid not in blocks_data:
                blocks_data[bid] = text

    sentences_json = json.dumps(_SENTENCES, ensure_ascii=False)
    blocks_json = json.dumps(blocks_data, ensure_ascii=False)
    views_meta_json = json.dumps(_VIEW_META, ensure_ascii=False)
    role_view_map_json = json.dumps(ROLE_VIEW_MAP, ensure_ascii=False)
    bytedance_role_view_map_json = json.dumps(BYTEDANCE_ROLE_VIEW_MAP, ensure_ascii=False)
    role_labels_json = json.dumps(ROLE_LABELS, ensure_ascii=False)
    bytedance_role_labels_json = json.dumps(BYTEDANCE_ROLE_LABELS, ensure_ascii=False)

    return f"""
const SENTENCES = {sentences_json};
const BLOCKS = {blocks_json};
const VIEWS = {json.dumps(_VIEWS)};
const VIEWS_META = {views_meta_json};
const ROLE_VIEW_MAP = {role_view_map_json};
const BYTEDANCE_ROLE_VIEW_MAP = {bytedance_role_view_map_json};
const ROLE_LABELS = {role_labels_json};
const BYTEDANCE_ROLE_LABELS = {bytedance_role_labels_json};
"""


def _build_static_section(role: str, is_bytedance: bool = False) -> str:
    if is_bytedance:
        label = BYTEDANCE_ROLE_LABELS.get(role, role)
        mapping = BYTEDANCE_ROLE_VIEW_MAP[role]
    else:
        label = ROLE_LABELS.get(role, role)
        mapping = ROLE_VIEW_MAP[role]

    path_blocks: dict[str, list[tuple[str, str]]] = {}
    for p in PATHS:
        path_blocks[p] = _get_view_blocks(mapping[p])

    base_order: list[str] = []
    base_groups: dict[str, dict[str, tuple[str, str]]] = {}
    for p in PATHS:
        for bid, text in path_blocks[p]:
            bn = base_name(bid)
            if bn not in base_groups:
                base_order.append(bn)
                base_groups[bn] = {}
            base_groups[bn][p] = (bid, text)

    html_parts = [f"<h2>{html.escape(label)}</h2>"]

    all_bids = []
    seen_bids = set()
    for p in PATHS:
        for bid, _ in path_blocks[p]:
            if bid not in seen_bids:
                seen_bids.add(bid)
                all_bids.append(bid)

    block_sets = []
    for p in PATHS:
        block_sets.append({b[0] for b in path_blocks[p]})

    html_parts.append("<h3>Block 结构概览</h3>")
    html_parts.append("<table class='block-overview'>")
    html_parts.append("<tr><th>Block</th><th>no_starter</th><th>old_match</th><th>new_dual_channel</th></tr>")
    for bid in all_bids:
        cells = ""
        for bs in block_sets:
            cls = "has" if bid in bs else "missing"
            cells += f"<td class='{cls}'>{cls.upper()}</td>"
        html_parts.append(f"<tr><td><code>{bid}</code></td>{cells}</tr>")
    html_parts.append("</table>")

    html_parts.append("<h3>语义对齐段落对比（相同段落自动合并；缺失路径留空；列宽可拖拽调整）</h3>")
    html_parts.append("<table class='line-diff'>")
    html_parts.append("<tr><th>Base</th><th>no_starter</th><th>old_match</th><th>new_dual_channel</th></tr>")

    for bn in base_order:
        group = base_groups[bn]
        paras: dict[str, list[str]] = {}
        for p in PATHS:
            if p in group:
                paras[p] = group[p][1].split("\n\n")
            else:
                paras[p] = []

        aligned = _align_three(
            paras.get("no_starter", []),
            paras.get("old_match", []),
            paras.get("new_dual_channel", []),
        )

        for idx, (pa, pb, pc) in enumerate(aligned):
            texts = [pa, pb, pc]
            present = [t.strip() != "" for t in texts]
            count_present = sum(present)
            if count_present == 0:
                continue

            html_parts.append("<tr>")
            if idx == 0:
                html_parts.append(f"<td class='base-name' rowspan='{len(aligned)}'>{bn}</td>")

            groups = []
            current_text = texts[0]
            current_count = 1
            for t in texts[1:]:
                if t == current_text:
                    current_count += 1
                else:
                    groups.append((current_text, current_count))
                    current_text = t
                    current_count = 1
            groups.append((current_text, current_count))

            for text, count in groups:
                escaped = html.escape(text).replace(" ", "&nbsp;")
                if count == 3:
                    html_parts.append(f"<td colspan='3' class='same shared-cell'><pre>{escaped}</pre></td>")
                elif count == 2:
                    html_parts.append(f"<td colspan='2' class='partial-same'><pre>{escaped}</pre></td>")
                else:
                    if text.strip() == "":
                        html_parts.append("<td class='empty'><pre>[N/A]</pre></td>")
                    else:
                        html_parts.append(f"<td class='diff'><pre>{escaped}</pre></td>")
            html_parts.append("</tr>")

    html_parts.append("</table>")
    return "\n".join(html_parts)


def _align_three(a: list[str], b: list[str], c: list[str]) -> list[tuple[str, str, str]]:
    ab = _align_two(a, b)
    ab_flat = [f"{pa}\x00{pb}" for pa, pb in ab]
    abc = _align_two(ab_flat, c)
    result: list[tuple[str, str, str]] = []
    for ab_item, pc in abc:
        if "\x00" in ab_item:
            pa, pb = ab_item.split("\x00", 1)
        else:
            pa, pb = ab_item, ""
        result.append((pa, pb, pc))
    return result


def _align_two(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    sm = difflib.SequenceMatcher(None, a, b)
    result: list[tuple[str, str]] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        max_len = max(i2 - i1, j2 - j1)
        for k in range(max_len):
            pa = a[i1 + k] if k < (i2 - i1) else ""
            pb = b[j1 + k] if k < (j2 - j1) else ""
            result.append((pa, pb))
    return result


def _build_shared_matrix() -> str:
    parts = ["<h2>全局共享矩阵</h2>", "<table class='matrix'>", "<tr><th>Role / Path</th>"]
    for p in PATHS:
        parts.append(f"<th>{p}</th>")
    parts.append("<th>跨路径共享 blocks</th><th>独有 blocks</th></tr>")

    for role in ROLES:
        mapping = ROLE_VIEW_MAP[role]
        block_sets = []
        for p in PATHS:
            blocks = _get_view_blocks(mapping[p])
            block_sets.append({b[0] for b in blocks})
        shared = block_sets[0] & block_sets[1] & block_sets[2]
        all_b = set()
        for bs in block_sets:
            all_b |= bs
        unique = all_b - shared
        parts.append(f"<tr><td>{ROLE_LABELS.get(role, role)}</td>")
        for bs in block_sets:
            parts.append(f"<td>{len(bs)} blocks</td>")
        parts.append(f"<td>{len(shared)}</td><td>{len(unique)}</td></tr>")
    parts.append("</table>")
    return "\n".join(parts)


def main() -> None:
    sections = [_build_static_section(role) for role in ROLES]
    bytedance_sections = [_build_static_section(role, is_bytedance=True) for role in BYTEDANCE_ROLES]
    matrix = _build_shared_matrix()
    js_data = _build_js_data()

    view_options = "".join(f'<option value="{html.escape(vid)}">{html.escape(vid)}</option>' for vid in _VIEWS)

    style = """
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background: #fafafa; color: #222; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
    h1 { font-size: 24px; border-bottom: 2px solid #333; padding-bottom: 10px; margin: 20px 20px 10px; }
    h2 { font-size: 20px; margin-top: 30px; color: #1a1a1a; }
    h3 { font-size: 15px; margin-top: 20px; color: #444; }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; font-size: 13px; }
    th, td { border: 1px solid #ccc; padding: 6px 10px; text-align: left; vertical-align: top; }
    th { background: #f0f0f0; }
    .block-overview .has { background: #d4edda; color: #155724; font-weight: bold; text-align: center; }
    .block-overview .missing { background: #f8d7da; color: #721c24; text-align: center; }
    .line-diff .same { background: #f5f5f5; color: #888; }
    .line-diff .partial-same { background: #e8f5e9; color: #555; }
    .line-diff .diff { background: #fff3cd; color: #856404; }
    .line-diff .empty { background: #f8f8f8; color: #ccc; text-align: center; }
    .line-diff pre { margin: 0; font-family: "SFMono-Regular", Consolas, monospace; white-space: pre-wrap; }
    .line-diff td { resize: horizontal; overflow: auto; min-width: 120px; max-width: 600px; }
    .line-diff .shared-cell { text-align: center; }
    .base-name { background: #e3f2fd; color: #0d47a1; font-weight: bold; width: 120px; }
    .matrix td, .matrix th { text-align: center; }
    .legend { margin: 10px 20px; padding: 12px; background: #fff; border-left: 4px solid #333; }

    /* Interactive editor styles */
    #interactiveView { padding: 0 20px 20px; flex: 1; overflow: auto; }
    .editor-toolbar { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid #ddd; margin-bottom: 15px; flex-wrap: wrap; }
    .editor-toolbar label { font-size: 13px; font-weight: 500; }
    .editor-toolbar select { padding: 5px 8px; font-size: 13px; border: 1px solid #ccc; border-radius: 4px; min-width: 220px; }
    .editor-toolbar button { padding: 6px 14px; font-size: 13px; border: 1px solid #ccc; background: #fff; border-radius: 4px; cursor: pointer; }
    .editor-toolbar button:hover { background: #f3f4f6; }
    .editor-toolbar .btn-primary { background: #1f2328; color: #fff; border-color: #1f2328; }
    .editor-toolbar .btn-primary:hover { background: #333; }
    .view-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 16px; }
    .view-card { background: #fff; border: 1px solid #ddd; border-radius: 8px; display: flex; flex-direction: column; max-height: 85vh; }
    .view-header { padding: 12px 14px; border-bottom: 1px solid #eee; font-weight: 600; font-size: 14px; background: #f8f9fa; border-radius: 8px 8px 0 0; }
    .view-body { flex: 1; overflow: auto; padding: 14px; font-family: "SFMono-Regular", Consolas, monospace; font-size: 13px; line-height: 1.65; white-space: pre-wrap; }
    .block-segment { margin-bottom: 14px; padding: 10px 12px; border-left: 3px solid #e0e0e0; background: #fafafa; border-radius: 0 6px 6px 0; }
    .block-segment:hover { border-left-color: #1890ff; background: #f0f7ff; }
    .block-label { font-size: 11px; color: #888; font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin-bottom: 6px; font-weight: 500; }
    .shared-sentence { background: #e6f4ff; border-bottom: 2px dotted #1890ff; border-radius: 3px; padding: 0 2px; cursor: text; transition: background .15s; }
    .shared-sentence:hover { background: #bae0ff; }
    .shared-sentence:focus { outline: 2px solid #1890ff; background: #fff; }
    .tabs { display: flex; gap: 4px; padding: 0 20px; border-bottom: 1px solid #ddd; background: #fff; }
    .tab { padding: 10px 18px; font-size: 13px; cursor: pointer; border-bottom: 2px solid transparent; }
    .tab:hover { color: #1890ff; }
    .tab.active { border-bottom-color: #1890ff; font-weight: 600; }
    .tab-content { display: none; }
    .tab-content.active { display: block; }
    .toast { position: fixed; bottom: 20px; right: 20px; background: #1f2328; color: #fff; padding: 10px 16px; border-radius: 6px; font-size: 13px; opacity: 0; pointer-events: none; transition: opacity .2s; z-index: 9999; }
    .toast.show { opacity: 1; }
    """

    html_text = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>Match Pipe V2 Path Comparison</title>
<style>{style}</style>
</head>
<body>
<h1>Match Pipe V2 — 三条链路 Prompt 对比报告</h1>
<div class="legend">
  <strong>图例说明：</strong><br/>
  • <span style="background:#d4edda;padding:2px 6px;">HAS</span> = 该路径包含此 block
  • <span style="background:#f8d7da;padding:2px 6px;">MISSING</span> = 该路径不包含此 block
  • 语义对齐表中：灰色=三路径相同；淡绿=两路径相同；黄色=仅该路径有；[N/A]=缺失
</div>

<div class="tabs">
  <div class="tab active" onclick="switchTab('interactive')">完整 Prompt 联动编辑</div>
  <div class="tab" onclick="switchTab('matrix')">全局共享矩阵</div>
  <div class="tab" onclick="switchTab('semantic')">语义对齐对比</div>
  <div class="tab" onclick="switchTab('bytedance')">ByteDance 变体对比</div>
</div>

<div id="interactive" class="tab-content active">
  <div id="interactiveView">
    <div class="editor-toolbar">
      <label>View A</label><select id="selA">{view_options}</select>
      <label>View B</label><select id="selB">{view_options}</select>
      <label>View C</label><select id="selC"><option value="">— 不选 —</option>{view_options}</select>
      <button class="btn-primary" onclick="downloadOverrides()">导出修改 (overrides.json)</button>
    </div>
    <div class="view-grid" id="viewGrid"></div>
  </div>
</div>

<div id="matrix" class="tab-content">
  <div style="padding:20px;">{matrix}</div>
</div>

<div id="semantic" class="tab-content">
  <div style="padding:20px;">
    {"\\n".join(sections)}
  </div>
</div>

<div id="bytedance" class="tab-content">
  <div style="padding:20px;">
    <div class="legend">
      以下展示 ByteDance 目标岗位下的三条链路对比。注意观察 <code>candidate_context_generic_tiktok_branch</code> 在 ByteDance 视图中被直接移除（替换为 <code>candidate_context_bytedance_boundary</code>），而 <code>format_constraints_branch</code> 实际对应的是 <code>format_constraints_branch_bytedance</code>，其中 TikTok 相关规则已被 ByteDance 边界规则替换。
    </div>
    {"\\n".join(bytedance_sections)}
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
{js_data}

// Initialize mutable copies
let sentences = JSON.parse(JSON.stringify(SENTENCES));
let blocks = JSON.parse(JSON.stringify(BLOCKS));

function escapeHtml(text) {{
  return text.replace(/\u0026/g, "\u0026amp;").replace(/\u003c/g, "\u0026lt;").replace(/\u003e/g, "\u0026gt;");
}}

function showToast(msg) {{
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 1600);
}}

function switchTab(id) {{
  document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById(id).classList.add('active');
}}

function wrapSentences(text) {{
  const entries = Object.entries(sentences).sort((a, b) => b[1].length - a[1].length);
  if (entries.length === 0) return escapeHtml(text);
  let result = text;
  let phIdx = 0;
  const placeholders = {{}};
  for (const [key, value] of entries) {{
    if (!value) continue;
    const re = new RegExp(value.replace(/[.*+?^${{}}()|[\]\\\\]/g, '\\\\$\u0026'), 'g');
    result = result.replace(re, (match) => {{
      const ph = "___PH" + (phIdx++) + "___";
      placeholders[ph] = {{ key, match }};
      return ph;
    }});
  }}
  result = escapeHtml(result);
  for (const [ph, {{key, match}}] of Object.entries(placeholders)) {{
    const span = '<span class="shared-sentence" data-key="' + key + '" contenteditable="true" title="Shared: ' + key + '">' + escapeHtml(match) + '</span>';
    result = result.split(ph).join(span);
  }}
  return result;
}}

function renderViewCard(vid, containerId) {{
  if (!vid) {{
    document.getElementById(containerId).innerHTML = '';
    return;
  }}
  const meta = VIEWS_META[vid] || {{}};
  const title = meta.title || vid;
  const blockList = [];
  if (meta.system_block) blockList.push({{id: meta.system_block, label: 'system: ' + meta.system_block}});
  for (const item of (meta.user_blocks || [])) {{
    const bid = (typeof item === 'string') ? item : item.block_id;
    blockList.push({{id: bid, label: 'user: ' + bid}});
  }}

  let html = '<div class="view-card"><div class="view-header">' + escapeHtml(title) + '</div><div class="view-body">';
  for (const seg of blockList) {{
    const text = blocks[seg.id] || "";
    html += '<div class="block-segment"><div class="block-label">' + escapeHtml(seg.label) + '</div><div class="block-text" data-block-id="' + seg.id + '">' + wrapSentences(text) + '</div></div>';
  }}
  html += '</div></div>';

  const wrapper = document.createElement('div');
  wrapper.innerHTML = html;
  wrapper.querySelectorAll('.shared-sentence').forEach(span => {{
    span.addEventListener('blur', (e) => {{
      const key = e.target.dataset.key;
      const newText = e.target.innerText;
      if (newText !== sentences[key]) {{
        const oldText = sentences[key];
        sentences[key] = newText;
        for (const bid in blocks) {{
          blocks[bid] = blocks[bid].split(oldText).join(newText);
        }}
        showToast('共享句子已更新，重新渲染所有视图');
        renderAllCards();
      }}
    }});
  }});
  wrapper.querySelectorAll('.block-text').forEach(div => {{
    div.addEventListener('blur', (e) => {{
      const bid = e.target.dataset.blockId;
      const newText = e.target.innerText;
      if (newText !== blocks[bid]) {{
        blocks[bid] = newText;
        showToast('Block 已更新');
        renderAllCards();
      }}
    }});
  }});

  const grid = document.getElementById('viewGrid');
  const existing = document.getElementById(containerId);
  if (existing) {{
    existing.replaceWith(wrapper.firstElementChild);
    wrapper.remove();
  }} else {{
    wrapper.firstElementChild.id = containerId;
    grid.appendChild(wrapper.firstElementChild);
  }}
}}

function renderAllCards() {{
  const grid = document.getElementById('viewGrid');
  grid.innerHTML = '';
  renderViewCard(document.getElementById('selA').value, 'cardA');
  renderViewCard(document.getElementById('selB').value, 'cardB');
  renderViewCard(document.getElementById('selC').value, 'cardC');
}}

function downloadOverrides() {{
  const payload = {{ sentences: sentences, blocks: blocks }};
  const blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: "application/json" }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "overrides.json";
  a.click();
  URL.revokeObjectURL(url);
  showToast("已下载 overrides.json");
}}

document.getElementById('selA').addEventListener('change', renderAllCards);
document.getElementById('selB').addEventListener('change', renderAllCards);
document.getElementById('selC').addEventListener('change', renderAllCards);

// Defaults
document.getElementById('selA').value = "prompt_writer_generate";
document.getElementById('selB').value = "prompt_retarget_old_match";
renderAllCards();
</script>
</body>
</html>"""

    OUTPUT.write_text(html_text, encoding="utf-8")
    print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()
