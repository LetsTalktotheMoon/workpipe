from __future__ import annotations

import json
from pathlib import Path

from runtime.job_webapp.prompt_review_common import SCHEMA_VERSION, SCOPE
from runtime.job_webapp.prompt_review_compiler import compile_prompt_review_snapshot
from runtime.job_webapp.prompt_review_store import (
    get_prompt_review_ambiguities,
    get_prompt_review_conflict,
    get_prompt_review_coverage,
    get_prompt_review_payload,
    get_prompt_review_roundtrip_report,
    list_prompt_review_revisions,
)


ROOT = Path(__file__).resolve().parents[1]
PROMPT_REVIEW_DIR = ROOT / "prompt_review"


def _load(name: str) -> dict:
    return json.loads((PROMPT_REVIEW_DIR / name).read_text(encoding="utf-8"))


def test_prompt_review_artifacts_exist_and_use_canonical_schema() -> None:
    required_files = [
        "review.baseline.json",
        "review.edited.json",
        "review.regenerated.json",
        "review.map.json",
        "coverage.report.json",
        "patch.log.json",
        "ambiguities.json",
        "roundtrip.report.json",
        "revisions/revisions.index.json",
        "revisions/rev-0001.json",
        "conflicts/active.json",
    ]
    for rel_path in required_files:
        assert (PROMPT_REVIEW_DIR / rel_path).exists(), rel_path

    baseline = _load("review.baseline.json")
    edited = _load("review.edited.json")
    regenerated = _load("review.regenerated.json")
    review_map = _load("review.map.json")
    patch_log = _load("patch.log.json")
    revisions_index = _load("revisions/revisions.index.json")
    roundtrip = _load("roundtrip.report.json")
    active_conflict = _load("conflicts/active.json")

    for payload in (baseline, edited, regenerated, review_map, patch_log, revisions_index, roundtrip, active_conflict):
        assert payload["schema_version"] == SCHEMA_VERSION
        assert payload["scope"] == SCOPE

    assert baseline["build_kind"] == "baseline"
    assert baseline["locked"] is True
    assert edited["build_kind"] == "edited"
    assert edited["status"] == "clean"
    assert regenerated["build_kind"] == "regenerated"

    assert patch_log["patches"] == []
    assert revisions_index["head_revision_id"] == edited["head_revision_id"]
    assert len(revisions_index["revisions"]) == 1
    assert roundtrip["status"] == "ok"
    assert active_conflict["frozen"] is False


def test_prompt_review_artifacts_match_current_compiler_snapshot() -> None:
    baseline = _load("review.baseline.json")
    edited = _load("review.edited.json")
    regenerated = _load("review.regenerated.json")
    review_map = _load("review.map.json")
    coverage = _load("coverage.report.json")

    compiled_snapshot, compiled_map, compiled_coverage, _ = compile_prompt_review_snapshot(regenerated=False)
    expected_groups = {group["group_id"]: group for group in compiled_snapshot["groups"]}

    for payload in (baseline, edited, regenerated):
        payload_groups = {group["group_id"]: group for group in payload["groups"]}
        assert set(payload_groups) == set(expected_groups)
        for group_id, expected in expected_groups.items():
            actual = payload_groups[group_id]
            assert actual["display_text"] == expected["display_text"]
            assert actual["production_chain"] == expected["production_chain"]
            assert actual["stage"] == expected["stage"]
            assert actual["role"] == expected["role"]
            assert [block["block_id"] for block in actual["blocks"]] == [block["block_id"] for block in expected["blocks"]]

    assert review_map["group_count"] == compiled_map["group_count"] == len(compiled_snapshot["groups"])
    assert review_map["block_count"] == compiled_map["block_count"]
    assert len(review_map["blocks"]) == compiled_map["block_count"]
    assert review_map["inactive_sources"] == []
    assert coverage["coverage_ratio"] == compiled_coverage["coverage_ratio"] == 1.0
    assert coverage["source_item_count"] == compiled_coverage["source_item_count"]
    assert coverage["covered_source_item_count"] == compiled_coverage["covered_source_item_count"]
    assert coverage["uncovered"] == []


def test_prompt_review_api_payloads_expose_stable_top_level_fields() -> None:
    bundle = get_prompt_review_payload()
    revisions = list_prompt_review_revisions()
    conflict = get_prompt_review_conflict()
    coverage = get_prompt_review_coverage()
    ambiguities = get_prompt_review_ambiguities()
    roundtrip = get_prompt_review_roundtrip_report()

    assert bundle["ok"] is True
    assert bundle["scope"] == SCOPE
    assert bundle["state"]["group_count"] == len(bundle["edited"]["groups"])
    assert bundle["edited"]["head_revision_id"] == bundle["revisions"]["head_revision_id"]
    assert bundle["coverage"]["coverage_ratio"] == 1.0
    assert bundle["conflict"]["frozen"] is False
    assert "items" in bundle["ambiguities"]
    assert "groups" in bundle["roundtrip"]
    assert bundle["map"]["group_count"] == len(bundle["edited"]["groups"])

    assert revisions["ok"] is True
    assert revisions["head_revision_id"] == bundle["edited"]["head_revision_id"]
    assert revisions["revision_count"] == len(revisions["revisions"])

    assert conflict["ok"] is True
    assert conflict["frozen"] is False
    assert conflict["conflict"]["frozen"] is False

    assert coverage["ok"] is True
    assert coverage["coverage_ratio"] == 1.0
    assert coverage["uncovered_count"] == 0

    assert ambiguities["ok"] is True
    assert ambiguities["ambiguity_count"] == len(ambiguities["items"])

    assert roundtrip["ok"] is True
    assert roundtrip["status"] == "ok"
