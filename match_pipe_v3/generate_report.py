#!/usr/bin/env python3
"""Generate an interactive HTML report for match_pipe_v3 parts catalog + assemblies."""

import json
import sys
from pathlib import Path

import yaml

# Allow importing runtime modules
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.job_webapp.prompt_library import (
    append_match_pipe_dual_channel_overlay,
    build_match_pipe_master_writer_prompt,
    build_match_pipe_planner_prompt,
    build_match_pipe_seed_retarget_prompt,
    build_match_pipe_unified_review_prompt,
    build_match_pipe_upgrade_revision_prompt,
    build_match_pipe_writer_prompt_from_planner,
    build_match_pipe_writer_revision_prompt,
    match_pipe_planner_system_prompt,
    match_pipe_reviewer_system_prompt,
    match_pipe_strict_revision_system_prompt,
    match_pipe_upgrade_revision_system_prompt,
    match_pipe_writer_system_prompt,
)
from runtime.models.jd import JDProfile
from match_pipe_v3.registry import PromptRegistry
from match_pipe_v3.runners._prompt_context import (
    build_dual_channel_context,
    build_planner_context,
    build_planner_revision_context,
    build_planner_writer_context,
    build_retarget_context,
    build_reviewer_context,
    build_upgrade_context,
    build_writer_context,
)


def _make_jd(company: str = "ExampleCorp") -> JDProfile:
    return JDProfile(
        company=company,
        title="Software Engineer",
        role_type="swe_backend",
        seniority="mid",
        team_direction="backend infra",
        tech_required=["Python", "Go"],
        tech_preferred=["Kubernetes"],
        tech_or_groups=[],
        soft_required=["collaboration"],
    )


def _make_review():
    from types import SimpleNamespace

    return SimpleNamespace(
        weighted_score=80.0,
        passed=False,
        needs_revision=True,
        revision_priority=["Fix summary"],
        dimensions={
            "r0": SimpleNamespace(
                findings=[{"severity": "high", "field": "summary", "issue": "weak", "fix": "strengthen"}]
            )
        },
    )


def _make_upgrade_result():
    return {
        "revision_priority": ["Fix summary", "Add Go evidence"],
        "scores": {
            "r0": {
                "findings": [
                    {"severity": "high", "field": "summary", "issue": "weak", "fix": "strengthen"},
                ]
            }
        },
        "revision_instructions": "Make it better.",
        "weighted_score": 75.0,
    }


def gather_data() -> dict:
    root = Path(__file__).resolve().parent
    registry = PromptRegistry.from_dir(root)

    # Load parts and assemblies
    parts = {path.stem: path.read_text(encoding="utf-8") for path in sorted((root / "parts").glob("*.md"))}
    assemblies = {
        path.stem: yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted((root / "assemblies").glob("*.yaml"))
    }

    views = []

    def add_view(name: str, legacy_fn, v3_ctx: dict, extra_legacy_kwargs: dict | None = None):
        extra_legacy_kwargs = extra_legacy_kwargs or {}
        legacy = legacy_fn(**extra_legacy_kwargs)
        v3 = registry.render_view(name, context=v3_ctx)
        views.append({"name": name, "legacy": legacy, "v3": v3, "context_label": str(v3_ctx.get("company", "generic"))})

    jd_generic = _make_jd("ExampleCorp")
    jd_bytedance = _make_jd("ByteDance")
    resume_md = "# Resume\n\nSome content."
    seed_resume_md = "# Seed Resume\n\nSome experience."
    matcher_packet = {"semantic_best_anchor": "anchor1"}
    starter_resume_md = "# Starter\n\nText."
    planner_payload = {"decision": "write", "fit_label": "good"}
    review = _make_review()
    upgrade_result = _make_upgrade_result()

    # Generic views
    add_view("prompt_writer_generate", build_match_pipe_master_writer_prompt, build_writer_context(jd_generic), {"jd": jd_generic})
    add_view("prompt_retarget_old_match", build_match_pipe_seed_retarget_prompt, build_retarget_context(jd_generic, seed_resume_md=seed_resume_md), {"seed_resume_md": seed_resume_md, "jd": jd_generic, "seed_label": "seed_label", "route_mode": "retarget", "top_candidate": {"same_company": False, "missing_required": []}})
    add_view("prompt_upgrade_revision", build_match_pipe_upgrade_revision_prompt, build_upgrade_context(resume_md, upgrade_result, tech_required=jd_generic.tech_required, target_company=jd_generic.company), {"resume_md": resume_md, "review_result": upgrade_result, "tech_required": jd_generic.tech_required, "jd_title": jd_generic.title, "target_company": jd_generic.company})
    add_view("prompt_reviewer_full", build_match_pipe_unified_review_prompt, build_reviewer_context(resume_md, jd_generic, review_scope="full"), {"resume_md": resume_md, "jd": jd_generic, "review_scope": "full"})
    add_view("prompt_planner_user", build_match_pipe_planner_prompt, build_planner_context(jd_generic, mode="new_dual_channel", matcher_packet=matcher_packet, starter_resume_md=starter_resume_md), {"jd": jd_generic, "mode": "new_dual_channel", "matcher_packet": matcher_packet, "starter_resume_md": starter_resume_md})
    add_view("prompt_planner_writer_full", build_match_pipe_writer_prompt_from_planner, build_planner_writer_context(jd_generic, planner_payload=planner_payload, starter_resume_md=starter_resume_md, matcher_packet=matcher_packet), {"jd": jd_generic, "planner_payload": planner_payload, "starter_resume_md": starter_resume_md, "matcher_packet": matcher_packet})
    add_view("prompt_planner_revision_full", build_match_pipe_writer_revision_prompt, build_planner_revision_context(resume_md, review, planner_payload, jd=jd_generic), {"current_resume_md": resume_md, "review": review, "jd": jd_generic, "planner_payload": planner_payload})

    # Dual channel generic
    old_dc = build_match_pipe_seed_retarget_prompt(seed_resume_md, jd_generic, seed_label="semantic:ExampleCorp / SWE", route_mode="retarget", top_candidate={"label": "SWE", "seed_company_name": "ExampleCorp", "same_company": False, "missing_required": []})
    old_dc = append_match_pipe_dual_channel_overlay(old_dc, delta_summary=["Add Python coverage", "Strengthen backend signal"], continuity_anchor={"company_name": "ExampleCorp", "title": "SWE", "reuse_readiness": 0.85})
    ctx_dc = build_retarget_context(jd_generic, seed_resume_md=seed_resume_md)
    ctx_dc.update(build_dual_channel_context(delta_summary=["Add Python coverage", "Strengthen backend signal"], continuity_anchor={"company_name": "ExampleCorp", "title": "SWE", "reuse_readiness": 0.85}))
    v3_dc = registry.render_view("prompt_dual_channel_full", context=ctx_dc)
    views.append({"name": "prompt_dual_channel_full", "legacy": old_dc, "v3": v3_dc, "context_label": "generic"})

    # System prompts
    for old_fn, block_id, name in [
        (match_pipe_writer_system_prompt, "writer_system", "writer_system"),
        (match_pipe_strict_revision_system_prompt, "strict_revision_system", "strict_revision_system"),
        (match_pipe_upgrade_revision_system_prompt, "upgrade_revision_system", "upgrade_revision_system"),
        (match_pipe_reviewer_system_prompt, "reviewer_system", "reviewer_system"),
        (match_pipe_planner_system_prompt, "planner_system", "planner_system"),
    ]:
        legacy = old_fn()
        v3 = registry.render_block(block_id)
        views.append({"name": name, "legacy": legacy, "v3": v3, "context_label": "system", "is_system": True})

    # ByteDance views
    add_view("prompt_writer_generate", build_match_pipe_master_writer_prompt, build_writer_context(jd_bytedance), {"jd": jd_bytedance})
    add_view("prompt_retarget_old_match", build_match_pipe_seed_retarget_prompt, build_retarget_context(jd_bytedance, seed_resume_md=seed_resume_md), {"seed_resume_md": seed_resume_md, "jd": jd_bytedance, "seed_label": "seed_label", "route_mode": "retarget", "top_candidate": {"same_company": False, "missing_required": []}})
    add_view("prompt_upgrade_revision", build_match_pipe_upgrade_revision_prompt, build_upgrade_context(resume_md, upgrade_result, tech_required=jd_bytedance.tech_required, target_company=jd_bytedance.company), {"resume_md": resume_md, "review_result": upgrade_result, "tech_required": jd_bytedance.tech_required, "jd_title": jd_bytedance.title, "target_company": jd_bytedance.company})
    add_view("prompt_reviewer_full", build_match_pipe_unified_review_prompt, build_reviewer_context(resume_md, jd_bytedance, review_scope="full"), {"resume_md": resume_md, "jd": jd_bytedance, "review_scope": "full"})
    add_view("prompt_planner_user", build_match_pipe_planner_prompt, build_planner_context(jd_bytedance, mode="new_dual_channel", matcher_packet=matcher_packet, starter_resume_md=starter_resume_md), {"jd": jd_bytedance, "mode": "new_dual_channel", "matcher_packet": matcher_packet, "starter_resume_md": starter_resume_md})
    add_view("prompt_planner_writer_full", build_match_pipe_writer_prompt_from_planner, build_planner_writer_context(jd_bytedance, planner_payload=planner_payload, starter_resume_md=starter_resume_md, matcher_packet=matcher_packet), {"jd": jd_bytedance, "planner_payload": planner_payload, "starter_resume_md": starter_resume_md, "matcher_packet": matcher_packet})
    add_view("prompt_planner_revision_full", build_match_pipe_writer_revision_prompt, build_planner_revision_context(resume_md, review, planner_payload, jd=jd_bytedance), {"current_resume_md": resume_md, "review": review, "jd": jd_bytedance, "planner_payload": planner_payload})

    # Build dependency map: part_id -> list of view names where it appears verbatim
    dep_map: dict[str, list[str]] = {}
    for view in views:
        v3_output = view["v3"]
        for part_id, part_text in parts.items():
            if part_text.strip() and part_text.strip() in v3_output:
                dep_map.setdefault(part_id, []).append(view["name"])

    return {"parts": parts, "assemblies": assemblies, "views": views, "dep_map": dep_map}


HTML_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>match_pipe_v3 Parts Catalog + Assembly Sheet</title>
<style>
  :root { --bg:#0f172a; --panel:#1e293b; --text:#e2e8f0; --muted:#94a3b8; --accent:#38bdf8; --danger:#f87171; --ok:#4ade80; --border:#334155; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--text); font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size:13px; }
  header { padding:12px 16px; border-bottom:1px solid var(--border); display:flex; align-items:center; justify-content:space-between; }
  h1 { margin:0; font-size:16px; }
  .wrap { display:flex; height:calc(100vh - 53px); }
  .sidebar { width:320px; border-right:1px solid var(--border); display:flex; flex-direction:column; }
  .sidebar .toolbar { padding:8px 12px; border-bottom:1px solid var(--border); display:flex; gap:8px; }
  .sidebar .list { flex:1; overflow:auto; padding:8px; }
  .part-item { padding:8px; border:1px solid var(--border); border-radius:6px; margin-bottom:6px; cursor:pointer; background:var(--panel); }
  .part-item:hover { border-color:var(--accent); }
  .part-item.active { outline:2px solid var(--accent); }
  .part-item .title { font-weight:700; color:var(--accent); }
  .part-item .meta { color:var(--muted); font-size:11px; margin-top:2px; }
  .editor { flex:1; display:flex; flex-direction:column; }
  .editor .tabs { display:flex; gap:8px; padding:8px 12px; border-bottom:1px solid var(--border); }
  .editor .tabs button { background:transparent; border:1px solid var(--border); color:var(--text); padding:6px 10px; border-radius:4px; cursor:pointer; }
  .editor .tabs button.active { background:var(--accent); color:#0f172a; border-color:var(--accent); }
  .editor .body { flex:1; display:flex; overflow:hidden; }
  .pane { flex:1; display:flex; flex-direction:column; min-width:0; }
  .pane + .pane { border-left:1px solid var(--border); }
  .pane h3 { margin:0; padding:8px 12px; border-bottom:1px solid var(--border); font-size:12px; text-transform:uppercase; color:var(--muted); }
  textarea { flex:1; width:100%; background:var(--bg); color:var(--text); border:none; padding:12px; resize:none; outline:none; line-height:1.6; }
  .preview { flex:1; overflow:auto; padding:12px; white-space:pre-wrap; word-break:break-word; }
  .badge { display:inline-block; padding:2px 6px; border-radius:4px; font-size:11px; margin-left:6px; }
  .badge-system { background:#475569; }
  .badge-generic { background:#2563eb; }
  .badge-bytedance { background:#7c3aed; }
  .status-bar { padding:8px 12px; border-top:1px solid var(--border); color:var(--muted); font-size:12px; display:flex; justify-content:space-between; }
  .diff-ok { color:var(--ok); }
  .diff-bad { color:var(--danger); }
  .hidden { display:none !important; }
</style>
</head>
<body>
<header>
  <h1>match_pipe_v3 — Parts Catalog + Assembly Sheet</h1>
  <div>
    <span id="matchStatus" class="diff-ok">All views match legacy</span>
    <button onclick="downloadParts()">Export parts JSON</button>
  </div>
</header>
<div class="wrap">
  <div class="sidebar">
    <div class="toolbar">
      <input id="filter" placeholder="Filter parts..." style="flex:1; background:var(--bg); color:var(--text); border:1px solid var(--border); padding:6px 8px; border-radius:4px;">
    </div>
    <div class="list" id="partList"></div>
  </div>
  <div class="editor">
    <div class="tabs" id="viewTabs"></div>
    <div class="body">
      <div class="pane" id="partPane">
        <h3>Part Editor <span id="partDeps" class="meta" style="float:right; text-transform:none; color:var(--muted);"></span></h3>
        <textarea id="partEditor" placeholder="Select a part to edit..."></textarea>
      </div>
      <div class="pane" id="rightPane">
        <h3 id="rightTitle">V3 Output</h3>
        <div class="preview" id="rightPreview"></div>
      </div>
    </div>
    <div class="status-bar">
      <span id="partName">No part selected</span>
      <span id="viewName">No view selected</span>
    </div>
  </div>
</div>
<script>
const data = /*DATA*/;
let activePartId = null;
let activeViewName = null;
let editedParts = {};

function buildPartList(filter="") {
  const el = document.getElementById('partList');
  el.innerHTML = '';
  const ids = Object.keys(data.parts).filter(id => id.toLowerCase().includes(filter.toLowerCase()));
  for (const id of ids) {
    const div = document.createElement('div');
    div.className = 'part-item' + (id===activePartId ? ' active' : '');
    const deps = data.dep_map[id] || [];
    div.innerHTML = `<div class="title">${id}</div><div class="meta">Used in ${deps.length} view(s)</div>`;
    div.onclick = () => selectPart(id);
    el.appendChild(div);
  }
}

function buildViewTabs() {
  const el = document.getElementById('viewTabs');
  el.innerHTML = '';
  const names = [...new Set(data.views.map(v => v.name))];
  for (const name of names) {
    const btn = document.createElement('button');
    btn.textContent = name;
    btn.className = name===activeViewName ? 'active' : '';
    btn.onclick = () => selectView(name);
    el.appendChild(btn);
  }
}

function getViewData(name) {
  return data.views.filter(v => v.name === name);
}

function computeViewOutput(view) {
  let out = view.v3;
  for (const [pid, text] of Object.entries(editedParts)) {
    const orig = data.parts[pid];
    if (orig && out.includes(orig)) {
      out = out.split(orig).join(text);
    }
  }
  return out;
}

function selectPart(id) {
  activePartId = id;
  document.getElementById('partEditor').value = editedParts[id] !== undefined ? editedParts[id] : data.parts[id];
  document.getElementById('partName').textContent = id;
  const deps = data.dep_map[id] || [];
  document.getElementById('partDeps').textContent = deps.length ? `Used in: ${deps.join(', ')}` : 'Not used verbatim in any view';
  buildPartList(document.getElementById('filter').value);
  if (deps.length && !activeViewName) {
    selectView(deps[0]);
  } else if (activeViewName) {
    renderRightPane();
  }
}

function selectView(name) {
  activeViewName = name;
  buildViewTabs();
  renderRightPane();
}

function renderRightPane() {
  const viewVariants = getViewData(activeViewName);
  if (!viewVariants.length) return;
  // For views with multiple variants, prefer the one whose context_label matches activePart usage if any
  let view = viewVariants[0];
  if (activePartId) {
    const depViews = data.dep_map[activePartId] || [];
    if (depViews.includes(activeViewName)) {
      // Try to match generic/bytedance heuristic based on part id
      const isBdPart = activePartId.includes('bytedance');
      const matched = viewVariants.find(v => (isBdPart && v.context_label==='ByteDance') || (!isBdPart && v.context_label==='generic'));
      if (matched) view = matched;
      else if (viewVariants.length > 1) {
        view = viewVariants.find(v => v.context_label==='generic') || viewVariants[0];
      }
    }
  }
  const out = computeViewOutput(view);
  const legacy = view.legacy;
  const isMatch = out.trim() === legacy.trim();
  document.getElementById('rightTitle').innerHTML = `V3 Output <span class="badge badge-${view.context_label==='system'?'system':view.context_label==='ByteDance'?'bytedance':'generic'}">${view.context_label}</span> <span class="${isMatch?'diff-ok':'diff-bad'}">${isMatch?'MATCH':'DIFF'}</span>`;
  document.getElementById('rightPreview').textContent = out;
  document.getElementById('viewName').textContent = `${view.name} (${view.context_label})`;
  updateGlobalStatus();
}

function updateGlobalStatus() {
  let allMatch = true;
  for (const v of data.views) {
    if (computeViewOutput(v).trim() !== v.legacy.trim()) {
      allMatch = false; break;
    }
  }
  const el = document.getElementById('matchStatus');
  el.textContent = allMatch ? 'All views match legacy' : 'Some views DIFF from legacy';
  el.className = allMatch ? 'diff-ok' : 'diff-bad';
}

function downloadParts() {
  const blob = new Blob([JSON.stringify(editedParts, null, 2)], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'edited_parts.json';
  a.click();
  URL.revokeObjectURL(url);
}

document.getElementById('partEditor').addEventListener('input', (e) => {
  if (!activePartId) return;
  editedParts[activePartId] = e.target.value;
  renderRightPane();
});

document.getElementById('filter').addEventListener('input', (e) => {
  buildPartList(e.target.value);
});

buildPartList();
buildViewTabs();
if (Object.keys(data.parts).length) selectPart(Object.keys(data.parts)[0]);
</script>
</body>
</html>
"""


def main():
    data = gather_data()
    json_data = json.dumps(data, ensure_ascii=False, indent=2)
    html = HTML_TEMPLATE.replace("/*DATA*/;", json_data)
    out_path = Path(__file__).resolve().parent / "parts_editor_report.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"Generated: {out_path}")


if __name__ == "__main__":
    main()
