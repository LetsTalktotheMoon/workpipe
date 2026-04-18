from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from runtime.job_webapp import prompt_library


def _sample_jd(company: str) -> SimpleNamespace:
    return SimpleNamespace(
        company=company,
        title="Software Engineer",
        role_type="swe_backend",
        seniority="entry",
        team_direction="infra",
        tech_required=["Python"],
        tech_preferred=["Go"],
        tech_or_groups=[],
        soft_required=[],
    )


def test_general_writer_prompt_includes_shared_gt_coursework_section() -> None:
    prompt = prompt_library.build_match_pipe_master_writer_prompt(_sample_jd("ExampleCorp"))

    assert "### TikTok（intern，最灵活，承接 JD 核心技术" in prompt
    assert "### Georgia Tech CS coursework/projects" in prompt
    assert "Georgia Tech CS coursework/projects（非工业项目" in prompt


def test_bytedance_prompt_keeps_gt_shared_and_adds_weighting_note() -> None:
    prompt = prompt_library.build_match_pipe_master_writer_prompt(_sample_jd("ByteDance"))

    assert "### Georgia Tech CS coursework/projects" in prompt
    assert "GT 教育主干仍按共享教育块保留" in prompt
    assert "Georgia Tech CS coursework/projects 可以作为主要软件工程/硬件/机械工程证据来源" in prompt


def test_bytedance_context_blocks_treat_gt_as_shared_main(tmp_path: Path, monkeypatch) -> None:
    override_path = tmp_path / "prompt_overrides.json"
    override_path.write_text(
        json.dumps({"scope": "match_pipe", "blocks": {}, "paragraphs": {}}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(prompt_library, "OVERRIDE_PATH", override_path)

    education_branch = prompt_library.get_match_pipe_block_text("candidate_context_bytedance_education_branch")
    boundary = prompt_library.get_match_pipe_block_text("candidate_context_bytedance_boundary")
    writer_system = prompt_library.get_match_pipe_block_text("writer_system")

    assert "GT 教育主干对所有线路共享" in education_branch
    assert "GT 教育主干仍按共享教育块保留" in boundary
    assert "GT MSCS 是所有线路共享的教育主干" in writer_system


def test_legacy_bytedance_gt_override_maps_to_shared_block(tmp_path: Path, monkeypatch) -> None:
    override_path = tmp_path / "prompt_overrides.json"
    override_path.write_text(
        json.dumps(
            {
                "scope": "match_pipe",
                "blocks": {
                    "writer_plan_bytedance_gt_branch": "### GT legacy override\n- shared text",
                },
                "paragraphs": {},
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(prompt_library, "OVERRIDE_PATH", override_path)

    block_text = prompt_library.get_match_pipe_block_text("writer_plan_shared_gt_coursework")
    editor_mapping = prompt_library.get_match_pipe_editor_mapping()
    paragraph = next(item for item in editor_mapping["paragraphs"] if item["text"] == block_text)

    assert block_text == "### GT legacy override\n- shared text"
    assert paragraph["branch_kind"] == "shared_trunk"
    assert paragraph["write_refs"][0]["block_id"] == "writer_plan_shared_gt_coursework"
