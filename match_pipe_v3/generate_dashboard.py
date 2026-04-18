#!/usr/bin/env python3
"""Generate an interactive HTML dashboard for match_pipe_v3.

Architecture: Source-first part editing.
- Selecting a view shows the ordered list of raw parts that compose it.
- Editing a part updates it in-memory and is logically reflected in every view
  that references the same part_id.
- No legacy diff, no virtual parts, no trace hacks.
"""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

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
        "scores": {"r0": {"findings": [{"severity": "high", "field": "summary", "issue": "weak", "fix": "strengthen"}]}},
        "revision_instructions": "Make it better.",
        "weighted_score": 75.0,
    }


def resolve_view_parts(registry: PromptRegistry, view_name: str, context: dict) -> list[str]:
    """Return ordered list of raw part_ids that compose a view for the given context."""
    assembly = registry._assemblies.get(view_name)
    if assembly is None:
        raise KeyError(f"Unknown view: {view_name}")
    parts: list[str] = []

    def walk(sections):
        for sec in sections:
            cond = sec.get("condition")
            if cond is not None and not registry._eval_condition(cond, context):
                continue
            if "sections" in sec or "group" in sec:
                walk(sec.get("sections", []))
            elif "part" in sec:
                parts.append(sec["part"])
            elif "template_part" in sec:
                parts.append(sec["template_part"])

    walk(assembly.get("sections", []))
    return parts


def gather_data(registry: PromptRegistry) -> tuple[list[dict], dict[str, str], dict[str, list[str]]]:
    parts_dir = Path(__file__).resolve().parent / "parts"
    static_parts = {path.stem: path.read_text(encoding="utf-8") for path in sorted(parts_dir.glob("*.md"))}

    jd_generic = _make_jd("ExampleCorp")
    jd_bytedance = _make_jd("ByteDance")
    resume_md = "# Resume\n\nSome content."
    seed_resume_md = "# Seed Resume\n\nSome experience."
    matcher_packet = {"semantic_best_anchor": "anchor1"}
    starter_resume_md = "# Starter\n\nText."
    planner_payload = {"decision": "write", "fit_label": "good"}
    review = _make_review()
    upgrade_result = _make_upgrade_result()

    views: list[dict] = []
    view_parts: dict[str, list[str]] = {}

    def add(
        route: str,
        has_planner: str,
        phase: str,
        variant: str | None,
        display: str,
        system_block_id: str | None,
        user_view_id: str,
        user_ctx: dict,
    ):
        if system_block_id:
            part_ids = [system_block_id] + resolve_view_parts(registry, user_view_id, user_ctx)
        else:
            part_ids = resolve_view_parts(registry, user_view_id, user_ctx)

        idx = len(views)
        views.append({
            "route": route,
            "has_planner": has_planner,
            "phase": phase,
            "variant": variant,
            "display": display,
        })
        view_parts[str(idx)] = part_ids

    # no_starter / direct
    add("no_starter", "direct", "generate", "generic", "Generate",
        "writer_system", "prompt_writer_generate", build_writer_context(jd_generic))
    add("no_starter", "direct", "generate", "bytedance", "Generate",
        "writer_system", "prompt_writer_generate", build_writer_context(jd_bytedance))
    add("no_starter", "direct", "review", "generic", "Review",
        "reviewer_system", "prompt_reviewer_full", build_reviewer_context(resume_md, jd_generic, review_scope="full"))
    add("no_starter", "direct", "review", "bytedance", "Review",
        "reviewer_system", "prompt_reviewer_full", build_reviewer_context(resume_md, jd_bytedance, review_scope="full"))
    add("no_starter", "direct", "upgrade", "generic", "Upgrade Revision",
        "upgrade_revision_system", "prompt_upgrade_revision",
        build_upgrade_context(resume_md, upgrade_result, tech_required=jd_generic.tech_required, target_company=jd_generic.company))
    add("no_starter", "direct", "upgrade", "bytedance", "Upgrade Revision",
        "upgrade_revision_system", "prompt_upgrade_revision",
        build_upgrade_context(resume_md, upgrade_result, tech_required=jd_bytedance.tech_required, target_company=jd_bytedance.company))

    # no_starter / planner_first
    add("no_starter", "planner_first", "plan", None, "Planner",
        "planner_system", "prompt_planner_user",
        build_planner_context(jd_generic, mode="no_starter", matcher_packet=matcher_packet, starter_resume_md=starter_resume_md))
    add("no_starter", "planner_first", "generate", "generic", "Planner-First Write",
        "writer_system", "prompt_planner_writer_full",
        build_planner_writer_context(jd_generic, planner_payload=planner_payload, starter_resume_md=starter_resume_md, matcher_packet=matcher_packet))
    add("no_starter", "planner_first", "generate", "bytedance", "Planner-First Write",
        "writer_system", "prompt_planner_writer_full",
        build_planner_writer_context(jd_bytedance, planner_payload=planner_payload, starter_resume_md=starter_resume_md, matcher_packet=matcher_packet))
    add("no_starter", "planner_first", "review", "generic", "Review",
        "reviewer_system", "prompt_reviewer_full", build_reviewer_context(resume_md, jd_generic, review_scope="full"))
    add("no_starter", "planner_first", "review", "bytedance", "Review",
        "reviewer_system", "prompt_reviewer_full", build_reviewer_context(resume_md, jd_bytedance, review_scope="full"))
    add("no_starter", "planner_first", "revision", "generic", "Planner Revision",
        "upgrade_revision_system", "prompt_planner_revision_full",
        build_planner_revision_context(resume_md, review, planner_payload, jd=jd_generic))
    add("no_starter", "planner_first", "revision", "bytedance", "Planner Revision",
        "upgrade_revision_system", "prompt_planner_revision_full",
        build_planner_revision_context(resume_md, review, planner_payload, jd=jd_bytedance))

    # old_match / direct
    add("old_match", "direct", "retarget", "generic", "Retarget",
        "strict_revision_system", "prompt_retarget_old_match",
        build_retarget_context(jd_generic, seed_resume_md=seed_resume_md))
    add("old_match", "direct", "retarget", "same_company", "Retarget",
        "strict_revision_system", "prompt_retarget_old_match",
        build_retarget_context(jd_generic, seed_resume_md=seed_resume_md, top_candidate={"same_company": True, "missing_required": []}))
    add("old_match", "direct", "retarget", "bytedance", "Retarget",
        "strict_revision_system", "prompt_retarget_old_match",
        build_retarget_context(jd_bytedance, seed_resume_md=seed_resume_md))
    add("old_match", "direct", "retarget", "same_company_bytedance", "Retarget",
        "strict_revision_system", "prompt_retarget_old_match",
        build_retarget_context(jd_bytedance, seed_resume_md=seed_resume_md, top_candidate={"same_company": True, "missing_required": []}))
    add("old_match", "direct", "review", "generic", "Review",
        "reviewer_system", "prompt_reviewer_full", build_reviewer_context(resume_md, jd_generic, review_scope="full"))
    add("old_match", "direct", "review", "bytedance", "Review",
        "reviewer_system", "prompt_reviewer_full", build_reviewer_context(resume_md, jd_bytedance, review_scope="full"))
    add("old_match", "direct", "upgrade", "generic", "Upgrade Revision",
        "upgrade_revision_system", "prompt_upgrade_revision",
        build_upgrade_context(resume_md, upgrade_result, tech_required=jd_generic.tech_required, target_company=jd_generic.company))
    add("old_match", "direct", "upgrade", "bytedance", "Upgrade Revision",
        "upgrade_revision_system", "prompt_upgrade_revision",
        build_upgrade_context(resume_md, upgrade_result, tech_required=jd_bytedance.tech_required, target_company=jd_bytedance.company))

    # new_dual_channel / direct
    def make_dc_ctx(jd, same_company):
        ctx = build_retarget_context(jd, seed_resume_md=seed_resume_md, top_candidate={
            "label": "SWE", "seed_company_name": "ExampleCorp" if jd.company == "ExampleCorp" else "ByteDance",
            "same_company": same_company, "missing_required": []
        })
        ctx.update(build_dual_channel_context(
            delta_summary=["Add Python coverage", "Strengthen backend signal"],
            continuity_anchor={"company_name": jd.company, "title": "SWE", "reuse_readiness": 0.85} if same_company else None
        ))
        return ctx

    add("new_dual_channel", "direct", "retarget", "generic", "Dual-Channel Retarget",
        "strict_revision_system", "prompt_dual_channel_full", make_dc_ctx(jd_generic, False))
    add("new_dual_channel", "direct", "retarget", "same_company", "Dual-Channel Retarget",
        "strict_revision_system", "prompt_dual_channel_full", make_dc_ctx(jd_generic, True))
    add("new_dual_channel", "direct", "retarget", "bytedance", "Dual-Channel Retarget",
        "strict_revision_system", "prompt_dual_channel_full", make_dc_ctx(jd_bytedance, False))
    add("new_dual_channel", "direct", "retarget", "same_company_bytedance", "Dual-Channel Retarget",
        "strict_revision_system", "prompt_dual_channel_full", make_dc_ctx(jd_bytedance, True))

    add("new_dual_channel", "direct", "review", "generic", "Review",
        "reviewer_system", "prompt_reviewer_full", build_reviewer_context(resume_md, jd_generic, review_scope="full"))
    add("new_dual_channel", "direct", "review", "bytedance", "Review",
        "reviewer_system", "prompt_reviewer_full", build_reviewer_context(resume_md, jd_bytedance, review_scope="full"))
    add("new_dual_channel", "direct", "upgrade", "generic", "Upgrade Revision",
        "upgrade_revision_system", "prompt_upgrade_revision",
        build_upgrade_context(resume_md, upgrade_result, tech_required=jd_generic.tech_required, target_company=jd_generic.company))
    add("new_dual_channel", "direct", "upgrade", "bytedance", "Upgrade Revision",
        "upgrade_revision_system", "prompt_upgrade_revision",
        build_upgrade_context(resume_md, upgrade_result, tech_required=jd_bytedance.tech_required, target_company=jd_bytedance.company))

    # new_dual_channel / planner_first
    add("new_dual_channel", "planner_first", "plan", None, "Planner",
        "planner_system", "prompt_planner_user",
        build_planner_context(jd_generic, mode="new_dual_channel", matcher_packet=matcher_packet, starter_resume_md=starter_resume_md))
    add("new_dual_channel", "planner_first", "generate", "generic", "Planner-First Write",
        "writer_system", "prompt_planner_writer_full",
        build_planner_writer_context(jd_generic, planner_payload=planner_payload, starter_resume_md=starter_resume_md, matcher_packet=matcher_packet))
    add("new_dual_channel", "planner_first", "generate", "bytedance", "Planner-First Write",
        "writer_system", "prompt_planner_writer_full",
        build_planner_writer_context(jd_bytedance, planner_payload=planner_payload, starter_resume_md=starter_resume_md, matcher_packet=matcher_packet))
    add("new_dual_channel", "planner_first", "review", "generic", "Review",
        "reviewer_system", "prompt_reviewer_full", build_reviewer_context(resume_md, jd_generic, review_scope="full"))
    add("new_dual_channel", "planner_first", "review", "bytedance", "Review",
        "reviewer_system", "prompt_reviewer_full", build_reviewer_context(resume_md, jd_bytedance, review_scope="full"))
    add("new_dual_channel", "planner_first", "revision", "generic", "Planner Revision",
        "upgrade_revision_system", "prompt_planner_revision_full",
        build_planner_revision_context(resume_md, review, planner_payload, jd=jd_generic))
    add("new_dual_channel", "planner_first", "revision", "bytedance", "Planner Revision",
        "upgrade_revision_system", "prompt_planner_revision_full",
        build_planner_revision_context(resume_md, review, planner_payload, jd=jd_bytedance))

    return views, static_parts, view_parts


HTML_TEMPLATE = """
<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>match_pipe_v3 Prompt Dashboard</title>
<style>
:root {
  --bg:#fdfbf7; --panel:#f7f5f0; --elev:#fffefb; --text:#2d2a26; --muted:#8c8378;
  --accent:#c49a6c; --accent-2:#8fa39a; --stale:#eab308; --ok:#5a8a6e; --border:#e6e1d8;
}
* { box-sizing:border-box; }
html,body { height:100%; margin:0; background:var(--bg); color:var(--text); font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji"; font-size:14px; }
header { height:50px; border-bottom:1px solid var(--border); display:flex; align-items:center; justify-content:space-between; padding:0 16px; background:var(--panel); }
header h1 { font-size:15px; margin:0; letter-spacing:0.2px; }
.wrap { display:flex; height:calc(100% - 50px); }
.sidebar { width:280px; border-right:1px solid var(--border); display:flex; flex-direction:column; background:var(--panel); flex-shrink:0; }
.sidebar h2 { font-size:12px; text-transform:uppercase; color:var(--muted); margin:0; padding:12px 12px 6px; }
.filter-group { padding:6px 12px; }
.filter-label { font-size:11px; color:var(--muted); margin-bottom:4px; }
.filter-options { display:flex; flex-wrap:wrap; gap:6px; }
.chip { border:1px solid var(--border); background:var(--elev); color:var(--text); padding:4px 10px; border-radius:999px; font-size:12px; cursor:pointer; user-select:none; }
.chip:hover { border-color:var(--accent); }
.chip.active { background:var(--accent); color:#fffefb; border-color:var(--accent); font-weight:600; }
.chip.disabled { opacity:0.35; cursor:not-allowed; border-color:var(--border); }
.view-list { flex:1; overflow:auto; padding:8px; }
.view-item { padding:10px 12px; border:1px solid var(--border); border-radius:8px; margin-bottom:6px; cursor:pointer; background:var(--elev); display:flex; align-items:center; justify-content:space-between; }
.view-item:hover { border-color:var(--accent); }
.view-item.active { outline:2px solid var(--accent); }
.view-item .title { font-weight:600; font-size:13px; }
.view-item .meta { font-size:11px; color:var(--muted); }
.view-item .badge { font-size:10px; padding:2px 6px; border-radius:999px; margin-left:6px; }
.view-item .badge-generic { background:#dbeafe; color:#1e40af; }
.view-item .badge-bytedance { background:#ede9fe; color:#5b21b6; }
.view-item .badge-same_company { background:#d1fae5; color:#065f46; }
.view-item .badge-same_company_bytedance { background:#fce7f3; color:#831843; }
.main { flex:1; display:flex; flex-direction:column; min-width:0; }
.source-header { padding:10px 16px; border-bottom:1px solid var(--border); background:var(--panel); display:flex; justify-content:space-between; align-items:center; }
.source-header h3 { margin:0; font-size:12px; text-transform:uppercase; color:var(--muted); }
.part-list { flex:1; overflow:auto; padding:16px; }
.part-card { background:var(--elev); border:1px solid var(--border); border-radius:8px; margin-bottom:12px; overflow:hidden; }
.part-card-header { padding:8px 12px; background:var(--panel); border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; font-size:12px; }
.part-card-header code { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; background:rgba(0,0,0,0.04); padding:2px 6px; border-radius:4px; }
.part-card textarea { width:100%; min-height:60px; border:none; padding:12px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size:13px; line-height:1.6; resize:none; overflow:hidden; background:var(--elev); color:var(--text); }
.part-card textarea:focus { outline:none; background:#fff; }
.part-card .actions { display:flex; gap:8px; align-items:center; }
.part-card .btn-small { font-size:11px; padding:3px 8px; border:1px solid var(--border); background:var(--elev); border-radius:4px; cursor:pointer; }
.part-card .btn-small:hover { border-color:var(--accent); }
.empty-state { color:var(--muted); padding:24px; }
.btn { background:var(--elev); border:1px solid var(--border); color:var(--text); padding:6px 12px; border-radius:6px; cursor:pointer; font-size:12px; }
.btn:hover { border-color:var(--accent); }
.btn-primary { background:var(--accent); color:#fffefb; border-color:var(--accent); }
.status-stale { color:var(--stale); }
.status-ok { color:var(--ok); }
.help-box { font-size:11px; color:var(--muted); padding:8px 16px; border-top:1px solid var(--border); background:var(--panel); }
.toast { position:fixed; bottom:20px; right:20px; background:#1f2328; color:#fff; padding:10px 16px; border-radius:6px; font-size:13px; opacity:0; pointer-events:none; transition:opacity 0.2s; z-index:100; }
.toast.show { opacity:1; }
</style>
</head>
<body>
<header>
  <h1>match_pipe_v3 Prompt Dashboard</h1>
  <div style="display:flex; gap:10px; align-items:center;">
    <span id="globalStatus" style="font-size:12px; color:var(--muted);">No edits</span>
    <button class="btn" onclick="downloadChanges()">Export edited parts</button>
  </div>
</header>
<div class="wrap">
  <div class="sidebar">
    <h2>Filter</h2>
    <div class="filter-group">
      <div class="filter-label">Route</div>
      <div class="filter-options" id="routeFilters"></div>
    </div>
    <div class="filter-group">
      <div class="filter-label">Planner Mode</div>
      <div class="filter-options" id="plannerFilters"></div>
    </div>
    <div class="filter-group">
      <div class="filter-label">Phase</div>
      <div class="filter-options" id="phaseFilters"></div>
    </div>
    <div class="filter-group" id="variantFilterGroup">
      <div class="filter-label">Variant</div>
      <div class="filter-options" id="variantFilters"></div>
    </div>
    <div class="view-list" id="viewList"></div>
  </div>
  <div class="main">
    <div class="source-header">
      <h3>Editable Parts</h3>
      <span id="partCount" style="font-size:11px; color:var(--muted);"></span>
    </div>
    <div class="part-list" id="sourceList">
      <div class="empty-state">Select a view to see and edit its source parts.</div>
    </div>
  </div>
</div>
<div class="help-box">
  Tip: Each card below is a raw part file (including placeholders like <code>{company}</code>). Edits apply to every view that uses this part.
</div>
<script>
const views = /*VIEWS*/;
const parts = /*PARTS*/;
const viewParts = /*VIEWPARTS*/;

let editedParts = {};
let activeIdx = null;
let filters = { route: null, has_planner: null, phase: null, variant: null };

const LS_KEY = 'match_pipe_v3_edited_parts';

function saveToLocalStorage() {
  localStorage.setItem(LS_KEY, JSON.stringify(editedParts));
  showToast('已保存到浏览器本地（Ctrl+S）');
  updateGlobalStatus();
}

function loadFromLocalStorage() {
  const raw = localStorage.getItem(LS_KEY);
  if (raw) {
    try {
      editedParts = JSON.parse(raw);
      updateGlobalStatus();
      if (activeIdx !== null) { renderSource(); refresh(); }
    } catch (e) {
      console.error('Failed to load from localStorage', e);
    }
  }
}

function showToast(msg) {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 2000);
}

document.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
    e.preventDefault();
    saveToLocalStorage();
  }
});

function allValues(key) { return [...new Set(views.map(v=>v[key]).filter(v=>v!==null && v!==undefined))]; }
function availableValues(key, currentFilters) {
  const restKeys = ['route','has_planner','phase','variant'].filter(k=>k!==key);
  const base = views.filter(v => restKeys.every(k => currentFilters[k]===null || v[k]===currentFilters[k]));
  return [...new Set(base.map(v=>v[key]).filter(v=>v!==null && v!==undefined))];
}

function buildChips(containerId, values, key, available) {
  const el = document.getElementById(containerId);
  el.innerHTML = '';
  const allBtn = document.createElement('span');
  allBtn.className = 'chip' + (filters[key]===null?' active':'');
  allBtn.textContent = 'All';
  allBtn.onclick = () => { filters[key]=null; refresh(); };
  el.appendChild(allBtn);
  for (const v of values) {
    const disabled = !available.includes(v);
    const chip = document.createElement('span');
    chip.className = 'chip' + (filters[key]===v?' active':'') + (disabled?' disabled':'');
    chip.textContent = v;
    if (!disabled) chip.onclick = () => { filters[key]=v; refresh(); };
    el.appendChild(chip);
  }
}

function matchedViews() {
  return views.filter(v => {
    return (filters.route===null || v.route===filters.route) &&
           (filters.has_planner===null || v.has_planner===filters.has_planner) &&
           (filters.phase===null || v.phase===filters.phase) &&
           (filters.variant===null || v.variant===filters.variant);
  });
}

function isViewModified(idx) {
  const pids = viewParts[String(idx)] || [];
  return pids.some(pid => editedParts[pid] !== undefined);
}

function refresh() {
  buildChips('routeFilters', allValues('route'), 'route', availableValues('route', filters));
  buildChips('plannerFilters', allValues('has_planner'), 'has_planner', availableValues('has_planner', filters));
  buildChips('phaseFilters', allValues('phase'), 'phase', availableValues('phase', filters));
  const variantAvailable = availableValues('variant', filters);
  const variantGroup = document.getElementById('variantFilterGroup');
  if (variantAvailable.length === 0) {
    variantGroup.style.display = 'none';
    filters.variant = null;
  } else {
    variantGroup.style.display = 'block';
    buildChips('variantFilters', allValues('variant'), 'variant', variantAvailable);
  }
  const list = matchedViews().map(v=>({v, globalIdx: views.indexOf(v)}));
  const listEl = document.getElementById('viewList');
  listEl.innerHTML = '';
  for (const {v, globalIdx} of list) {
    const div = document.createElement('div');
    div.className = 'view-item' + (globalIdx===activeIdx?' active':'');
    const modified = isViewModified(globalIdx);
    const pids = viewParts[String(globalIdx)] || [];
    const badgeHtml = v.variant ? `<span class="badge badge-${v.variant}">${v.variant}</span>` : '';
    div.innerHTML = `<div><span class="title">${v.display}</span>${badgeHtml}</div><div class="meta ${modified?'status-stale':''}">${modified?'MODIFIED':pids.length+' parts'}</div>`;
    div.onclick = () => selectView(globalIdx);
    listEl.appendChild(div);
  }
  if (list.length===0) {
    listEl.innerHTML = '<div class="empty-state">No views match current filters.</div>';
  }
  updateGlobalStatus();
}

function selectView(idx) {
  activeIdx = idx;
  renderSource();
  refresh();
}

function renderSource() {
  const container = document.getElementById('sourceList');
  const countEl = document.getElementById('partCount');
  if (activeIdx === null) {
    container.innerHTML = '<div class="empty-state">Select a view to see and edit its source parts.</div>';
    countEl.textContent = '';
    return;
  }
  const pids = viewParts[String(activeIdx)] || [];
  if (pids.length === 0) {
    container.innerHTML = '<div class="empty-state">No backing parts for this view.</div>';
    countEl.textContent = '';
    return;
  }
  countEl.textContent = pids.length + ' part' + (pids.length===1?'':'s');
  container.innerHTML = '';
  for (const pid of pids) {
    const original = parts[pid] || '';
    const current = editedParts[pid] !== undefined ? editedParts[pid] : original;
    const dirty = editedParts[pid] !== undefined;
    const card = document.createElement('div');
    card.className = 'part-card';
    card.innerHTML = `
      <div class="part-card-header">
        <code>${pid}</code>
        <div class="actions">
          <span class="save-status" id="status-${pid}" style="font-size:11px;color:var(--muted);">auto-saved</span>
          <button class="btn-small" onclick="exportPart('${pid}')">Export</button>
          <button class="btn-small" onclick="resetPart('${pid}')">Reset</button>
        </div>
      </div>
      <textarea data-pid="${pid}">${escapeHtml(current)}</textarea>
    `;
    container.appendChild(card);
  }
  container.querySelectorAll('textarea').forEach(ta => {
    ta.style.height = 'auto';
    ta.style.height = ta.scrollHeight + 'px';
    ta.addEventListener('input', () => {
      ta.style.height = 'auto';
      ta.style.height = ta.scrollHeight + 'px';
      editedParts[ta.dataset.pid] = ta.value;
      const status = document.getElementById('status-' + ta.dataset.pid);
      if (status) { status.textContent = 'unsaved'; status.style.color = 'var(--stale)'; }
      refresh();
    });
  });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function exportPart(pid) {
  const payload = {};
  const text = editedParts[pid] !== undefined ? editedParts[pid] : parts[pid];
  payload[pid] = text;
  const blob = new Blob([JSON.stringify(payload, null, 2)], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `match_pipe_v3_overrides_${pid}.json`;
  a.click();
  URL.revokeObjectURL(url);
  const status = document.getElementById('status-' + pid);
  if (status) { status.textContent = 'exported'; status.style.color = 'var(--ok)'; }
}

function resetPart(pid) {
  delete editedParts[pid];
  renderSource();
  refresh();
}

function updateGlobalStatus() {
  const editedCount = Object.keys(editedParts).length;
  const el = document.getElementById('globalStatus');
  el.textContent = editedCount ? `${editedCount} part(s) edited` : 'No edits';
  el.style.color = editedCount ? 'var(--stale)' : 'var(--muted)';
}

function downloadChanges() {
  const payload = {};
  for (const [k,v] of Object.entries(editedParts)) {
    if (v !== parts[k]) payload[k] = v;
  }
  const blob = new Blob([JSON.stringify(payload, null, 2)], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'match_pipe_v3_overrides.json';
  a.click();
  URL.revokeObjectURL(url);
  for (const pid of Object.keys(editedParts)) {
    const status = document.getElementById('status-' + pid);
    if (status) { status.textContent = 'exported'; status.style.color = 'var(--ok)'; }
  }
}

loadFromLocalStorage();
refresh();
if (views.length) {
  const defIdx = views.findIndex(v => v.route==='no_starter' && v.has_planner==='direct' && v.phase==='generate' && v.variant==='generic');
  selectView(defIdx >= 0 ? defIdx : 0);
}
</script>
</body>
</html>
"""


def main():
    root = Path(__file__).resolve().parent
    registry = PromptRegistry.from_dir(root)
    views, all_parts, view_parts = gather_data(registry)

    data_views = [
        {"route": v["route"], "has_planner": v["has_planner"], "phase": v["phase"], "variant": v["variant"], "display": v["display"]}
        for v in views
    ]

    html = HTML_TEMPLATE.replace("/*VIEWS*/", json.dumps(data_views, ensure_ascii=False))
    html = html.replace("/*PARTS*/", json.dumps(all_parts, ensure_ascii=False))
    html = html.replace("/*VIEWPARTS*/", json.dumps(view_parts, ensure_ascii=False))

    out_path = root / "dashboard.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"Generated: {out_path}")


if __name__ == "__main__":
    main()
