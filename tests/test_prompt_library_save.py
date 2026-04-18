from __future__ import annotations

import json
from pathlib import Path

from runtime.job_webapp import prompt_library


def test_save_match_pipe_paragraph_overrides_persists_paragraph_log(tmp_path: Path, monkeypatch) -> None:
    override_path = tmp_path / "prompt_overrides.json"
    monkeypatch.setattr(prompt_library, "OVERRIDE_PATH", override_path)

    editor_mapping = prompt_library.get_match_pipe_editor_mapping()
    paragraph = next(
        item
        for item in editor_mapping["paragraphs"]
        if any(ref["block_id"] == "candidate_context_bytedance_education_branch" for ref in item["write_refs"])
    )
    updated_text = (
        "→ ByteDance 目标岗位中，Georgia Tech CS coursework/projects 可以作为主要软件工程"
        "与系统实现证据来源。"
    )

    result = prompt_library.save_match_pipe_paragraph_overrides({paragraph["id"]: updated_text})

    payload = json.loads(override_path.read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert result["saved_paragraph_count"] == 1
    assert result["updated_paragraph_count"] == 1
    assert payload["paragraphs"] == {paragraph["id"]: updated_text}
    assert payload["blocks"]["candidate_context_bytedance_education_branch"] == updated_text


def test_save_match_pipe_paragraph_overrides_preserves_existing_block_overrides(tmp_path: Path, monkeypatch) -> None:
    override_path = tmp_path / "prompt_overrides.json"
    monkeypatch.setattr(prompt_library, "OVERRIDE_PATH", override_path)

    editor_mapping = prompt_library.get_match_pipe_editor_mapping()
    first_paragraph = next(
        item
        for item in editor_mapping["paragraphs"]
        if any(ref["block_id"] == "writer_system" for ref in item["write_refs"])
    )
    first_update = "在 PLAN 阶段，你可以并应该：先明确 scope，再决定经历主次。"

    first_result = prompt_library.save_match_pipe_paragraph_overrides({first_paragraph["id"]: first_update})

    refreshed_mapping = prompt_library.get_match_pipe_editor_mapping()
    second_paragraph = next(
        item
        for item in refreshed_mapping["paragraphs"]
        if any(ref["block_id"] == "format_constraints_shared_mid" for ref in item["write_refs"])
        and "内容规则" in item["text"]
    )
    second_update = "**内容规则**\n- 所有 bullet 都必须服务于目标 JD 的证据链。"

    second_result = prompt_library.save_match_pipe_paragraph_overrides({second_paragraph["id"]: second_update})

    payload = json.loads(override_path.read_text(encoding="utf-8"))
    writer_system_text = payload["blocks"]["writer_system"]
    format_constraints_text = payload["blocks"]["format_constraints_shared_mid"]

    assert first_result["ok"] is True
    assert second_result["ok"] is True
    assert first_update in writer_system_text
    assert second_update in format_constraints_text
    assert second_result["updated_paragraph_count"] == 1
