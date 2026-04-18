import sys
from types import SimpleNamespace

sys.path.insert(0, "runtime")
sys.path.insert(0, ".")

from match_pipe_v2.registry import PromptRegistry
from match_pipe_v2.runners._prompt_context import (
    build_dual_channel_context,
    build_planner_context,
    build_planner_revision_context,
    build_planner_writer_context,
    build_reviewer_context,
    build_upgrade_context,
    build_writer_context,
)
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


registry = PromptRegistry.from_dir("match_pipe_v2/prompts")


def _make_jd() -> JDProfile:
    return JDProfile(
        company="ExampleCorp",
        title="Software Engineer",
        role_type="swe_backend",
        seniority="mid",
        team_direction="backend infra",
        tech_required=["Python", "Go"],
        tech_preferred=["Kubernetes"],
        tech_or_groups=[],
        soft_required=["collaboration"],
    )


def _diff_report(old: str, new: str, label: str) -> str | None:
    old_stripped = old.strip()
    new_stripped = new.strip()
    if old_stripped == new_stripped:
        return None
    max_len = max(len(old_stripped), len(new_stripped))
    for i in range(max_len):
        if i >= len(old_stripped) or i >= len(new_stripped) or old_stripped[i] != new_stripped[i]:
            context_old = old_stripped[max(0, i - 120) : i + 240]
            context_new = new_stripped[max(0, i - 120) : i + 240]
            return (
                f"\n{'='*60}\n"
                f"DIFF DETECTED: {label} (first mismatch at char {i})\n"
                f"{'-'*60}\n"
                f"OLD:\n{context_old}\n"
                f"{'-'*60}\n"
                f"NEW:\n{context_new}\n"
                f"{'='*60}\n"
            )
    return None


def test_core_views_and_report() -> None:
    jd = _make_jd()
    reports: list[str] = []

    # 1. writer_generate
    old = build_match_pipe_master_writer_prompt(jd)
    new = registry.render_view("prompt_writer_generate", context=build_writer_context(jd))
    if diff := _diff_report(old, new, "prompt_writer_generate"):
        reports.append(diff)

    # 2. retarget_old_match
    seed_resume_md = "# Seed Resume\n\nSome experience."
    old = build_match_pipe_seed_retarget_prompt(
        seed_resume_md,
        jd,
        seed_label="seed_label",
        route_mode="retarget",
        top_candidate={"same_company": False, "missing_required": []},
    )
    new = registry.render_view("prompt_retarget_old_match", context=build_writer_context(jd, seed_resume_md=seed_resume_md))
    if diff := _diff_report(old, new, "prompt_retarget_old_match"):
        reports.append(diff)

    # 3. upgrade_revision
    resume_md = "# Resume\n\nSome content."
    review_result = {
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
    old = build_match_pipe_upgrade_revision_prompt(
        resume_md,
        review_result,
        tech_required=jd.tech_required,
        jd_title=jd.title,
        target_company=jd.company,
    )
    new = registry.render_view(
        "prompt_upgrade_revision",
        context=build_upgrade_context(resume_md, review_result, tech_required=jd.tech_required),
    )
    if diff := _diff_report(old, new, "prompt_upgrade_revision"):
        reports.append(diff)

    # --- Additional coverage ---

    # reviewer_full
    old = build_match_pipe_unified_review_prompt(resume_md, jd, review_scope="full")
    new = registry.render_view("prompt_reviewer_full", context=build_reviewer_context(resume_md, jd, review_scope="full"))
    if diff := _diff_report(old, new, "prompt_reviewer_full"):
        reports.append(diff)

    # dual_channel_full
    delta_summary = ["Add Python coverage", "Strengthen backend signal"]
    continuity_anchor = {"company_name": "ExampleCorp", "title": "SWE", "reuse_readiness": 0.85}
    old = build_match_pipe_seed_retarget_prompt(
        seed_resume_md,
        jd,
        seed_label="semantic:ExampleCorp / SWE",
        route_mode="retarget",
        top_candidate={"label": "SWE", "seed_company_name": "ExampleCorp", "same_company": False, "missing_required": []},
    )
    old = append_match_pipe_dual_channel_overlay(old, delta_summary=delta_summary, continuity_anchor=continuity_anchor)
    ctx = build_writer_context(jd, seed_resume_md=seed_resume_md)
    ctx.update(build_dual_channel_context(delta_summary=delta_summary, continuity_anchor=continuity_anchor))
    new = registry.render_view("prompt_dual_channel_full", context=ctx)
    if diff := _diff_report(old, new, "prompt_dual_channel_full"):
        reports.append(diff)

    # system blocks
    for old_fn, block_id, name in [
        (match_pipe_writer_system_prompt, "writer_system", "writer_system"),
        (match_pipe_strict_revision_system_prompt, "strict_revision_system", "strict_revision_system"),
        (match_pipe_upgrade_revision_system_prompt, "upgrade_revision_system", "upgrade_revision_system"),
        (match_pipe_reviewer_system_prompt, "reviewer_system", "reviewer_system"),
        (match_pipe_planner_system_prompt, "planner_system", "planner_system"),
    ]:
        if diff := _diff_report(old_fn(), registry.render_block(block_id), name):
            reports.append(diff)

    # planner_user
    matcher_packet = {"semantic_best_anchor": "anchor1"}
    starter_resume_md = "# Starter\n\nText."
    old = build_match_pipe_planner_prompt(
        jd=jd,
        mode="new_dual_channel",
        matcher_packet=matcher_packet,
        starter_resume_md=starter_resume_md,
    )
    new = registry.render_view(
        "prompt_planner_user",
        context=build_planner_context(jd, mode="new_dual_channel", matcher_packet=matcher_packet, starter_resume_md=starter_resume_md),
    )
    if diff := _diff_report(old, new, "prompt_planner_user"):
        reports.append(diff)

    # planner_writer_full
    planner_payload = {"decision": "write", "fit_label": "good"}
    old = build_match_pipe_writer_prompt_from_planner(
        jd=jd,
        planner_payload=planner_payload,
        starter_resume_md=starter_resume_md,
        matcher_packet=matcher_packet,
    )
    new = registry.render_view(
        "prompt_planner_writer_full",
        context=build_planner_writer_context(jd, planner_payload=planner_payload, starter_resume_md=starter_resume_md, matcher_packet=matcher_packet),
    )
    if diff := _diff_report(old, new, "prompt_planner_writer_full"):
        reports.append(diff)

    # planner_revision_full
    current_resume_md = "# Resume\n\nText."
    planner_payload = {"writer_plan": ["Plan A"], "risk_flags": ["Risk 1"]}
    review = SimpleNamespace(
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
    old = build_match_pipe_writer_revision_prompt(current_resume_md, review, jd, planner_payload)
    new = registry.render_view(
        "prompt_planner_revision_full",
        context=build_planner_revision_context(current_resume_md, review, planner_payload, jd=jd),
    )
    if diff := _diff_report(old, new, "prompt_planner_revision_full"):
        reports.append(diff)

    if reports:
        full_report = "\n".join(reports)
        print(full_report)
        raise AssertionError(
            f"Detected {len(reports)} view/block diff(s) between old prompt_library and new PromptRegistry. "
            "See stdout for detailed diff report. These diffs are expected because the old runtime uses "
            "match_pipe/prompt_overrides.json, while the new v2 registry reads from match_pipe_v2/prompts/blocks/ "
            "without those overrides."
        )
