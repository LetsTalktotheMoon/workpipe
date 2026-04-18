from __future__ import annotations

import json
from pathlib import Path

from runtime.job_webapp.prompt_review_compiler import compile_prompt_review_snapshot


ROOT = Path(__file__).resolve().parents[1]
PROMPT_REVIEW_DIR = ROOT / "prompt_review"


def _load(name: str) -> dict:
    return json.loads((PROMPT_REVIEW_DIR / name).read_text(encoding="utf-8"))


def test_prompt_review_includes_runtime_and_reference_groups() -> None:
    baseline = _load("review.baseline.json")
    group_ids = {group["group_id"] for group in baseline["groups"]}

    required_group_ids = {
        "runtime_main::generate::writer",
        "runtime_main::full_review::reviewer",
        "runtime_main::upgrade_revision::writer",
        "runtime_seed_retarget::rewrite_review::reviewer",
        "runtime_seed_retarget::rewrite_writer::writer",
        "runtime_reviewer_fallback::json_repair::reviewer_repairer",
        "match_pipe::no_starter::writer",
        "match_pipe::planner_revision::writer::bytedance",
        "source_reference::inactive_builder::revision_writer",
        "source_reference::indirect_runtime::seed_retarget_writer",
        "source_reference::doc::prompt_canonical_review",
        "source_reference::doc::match_pipe_prompt_review",
        "source_reference::design_guide::task_general_prompt",
        "source_reference::design_guide::execution_suggestions_prompt",
        "source_reference::test_fixture::prompt_merge_equivalence",
    }
    assert required_group_ids.issubset(group_ids)


def test_prompt_review_map_preserves_group_and_block_level_source_metadata() -> None:
    review_map = _load("review.map.json")
    groups = {group["group_id"]: group for group in review_map["groups"]}
    blocks = {(block["group_id"], block["block_id"]): block for block in review_map["blocks"]}

    sample_keys = [
        ("runtime_main::generate::writer", "standard_writer::examplecorp::system"),
        ("match_pipe::no_starter::writer", "writer_system"),
        ("source_reference::indirect_runtime::seed_retarget_writer", "source_reference::indirect_runtime::seed_retarget_writer::user"),
        ("source_reference::doc::prompt_canonical_review", "source_reference::doc::prompt_canonical_review::document"),
    ]

    for group_id, block_id in sample_keys:
        assert group_id in groups
        assert (group_id, block_id) in blocks
        block = blocks[(group_id, block_id)]
        assert block["normalized_text"]
        assert block["source_refs"]
        assert block["primary_source"]
        assert "write_policy" in block
        assert "propagation_rule" in block
        assert "duplicate_fingerprint" in block
        assert isinstance(block["placeholder_refs"], list)


def test_prompt_review_artifacts_track_current_group_order_and_counts() -> None:
    baseline = _load("review.baseline.json")
    regenerated = _load("review.regenerated.json")
    revisions_index = _load("revisions/revisions.index.json")
    patch_log = _load("patch.log.json")
    roundtrip = _load("roundtrip.report.json")

    compiled_snapshot, _, _, _ = compile_prompt_review_snapshot(regenerated=False)
    expected_order = [group["group_id"] for group in compiled_snapshot["groups"]]

    assert baseline["group_count"] == len(expected_order)
    assert regenerated["group_count"] == len(expected_order)
    assert [group["group_id"] for group in baseline["groups"]] == expected_order
    assert [group["group_id"] for group in regenerated["groups"]] == expected_order
    assert patch_log["patches"] == []
    assert roundtrip["summary"]["group_count"] == len(expected_order)
