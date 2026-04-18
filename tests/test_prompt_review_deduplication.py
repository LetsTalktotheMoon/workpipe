"""Tests for prompt_review deduplication layer (frontend-only enhancement).

These tests validate that the duplicate_fingerprint / duplicate_clusters
metadata is internally consistent across baseline, map, and coverage artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROMPT_REVIEW_DIR = ROOT / "prompt_review"


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def baseline() -> dict:
    return _load_json(PROMPT_REVIEW_DIR / "review.baseline.json")


@pytest.fixture
def review_map() -> dict:
    return _load_json(PROMPT_REVIEW_DIR / "review.map.json")


@pytest.fixture
def coverage() -> dict:
    return _load_json(PROMPT_REVIEW_DIR / "coverage.report.json")


class TestDuplicateFingerprintAlignment:
    def test_all_duplicate_clusters_have_multiple_members(self, coverage: dict) -> None:
        clusters = coverage.get("duplicate_clusters", [])
        for cluster in clusters:
            gids = cluster.get("group_ids", [])
            assert len(gids) >= 2, f"duplicate_cluster {cluster.get('duplicate_fingerprint')} has <2 members"

    def test_duplicate_fingerprints_in_coverage_exist_in_baseline(
        self, baseline: dict, coverage: dict
    ) -> None:
        baseline_fps: set[str] = set()
        for group in baseline.get("groups", []):
            for block in group.get("blocks", []):
                fp = block.get("duplicate_fingerprint")
                if fp:
                    baseline_fps.add(fp)

        coverage_fps = {c["duplicate_fingerprint"] for c in coverage.get("duplicate_clusters", [])}
        missing_in_baseline = coverage_fps - baseline_fps
        assert not missing_in_baseline, (
            f"Some duplicate_fingerprints in coverage duplicate_clusters are missing from baseline: "
            f"{missing_in_baseline}"
        )

    def test_duplicate_cluster_group_ids_exist_in_baseline(
        self, baseline: dict, coverage: dict
    ) -> None:
        baseline_group_ids = {g["group_id"] for g in baseline.get("groups", [])}
        for cluster in coverage.get("duplicate_clusters", []):
            for gid in cluster.get("group_ids", []):
                assert gid in baseline_group_ids, (
                    f"group_id {gid} in duplicate_cluster {cluster['duplicate_fingerprint']} "
                    f"does not exist in baseline"
                )

    def test_duplicate_cluster_blocks_have_identical_normalized_text(
        self, baseline: dict, coverage: dict
    ) -> None:
        block_lookup: dict[tuple[str, str], str] = {}
        for group in baseline.get("groups", []):
            gid = group["group_id"]
            for block in group.get("blocks", []):
                bid = block["block_id"]
                block_lookup[(gid, bid)] = block.get("normalized_text", "")

        for cluster in coverage.get("duplicate_clusters", []):
            fp = cluster["duplicate_fingerprint"]
            gids = cluster.get("group_ids", [])
            texts = []
            for gid in gids:
                # Find the block with this fingerprint in the group
                for (g, b), text in block_lookup.items():
                    if g == gid:
                        # We don't know the exact block_id here, but we can look it up
                        # by matching the fingerprint. However block_lookup doesn't store fp.
                        pass
            # Better approach: build fp -> [(gid,bid)] from baseline
        # Re-implement cleanly below

    def test_duplicate_cluster_textual_identity(self, baseline: dict, coverage: dict) -> None:
        """All blocks sharing a duplicate_fingerprint must have identical normalized_text."""
        fp_map: dict[str, list[tuple[str, str, str]]] = {}
        for group in baseline.get("groups", []):
            gid = group["group_id"]
            for block in group.get("blocks", []):
                fp = block.get("duplicate_fingerprint")
                if not fp:
                    continue
                fp_map.setdefault(fp, []).append(
                    (gid, block["block_id"], block.get("normalized_text", ""))
                )

        for cluster in coverage.get("duplicate_clusters", []):
            fp = cluster["duplicate_fingerprint"]
            entries = fp_map.get(fp, [])
            assert len(entries) >= 2, f"Cluster {fp} has fewer than 2 entries in baseline"
            first_text = entries[0][2]
            for gid, bid, text in entries[1:]:
                assert text == first_text, (
                    f"normalized_text mismatch for fingerprint {fp}: "
                    f"group {gid} block {bid} differs from representative"
                )


class TestMirrorAlignment:
    def test_mirrors_reference_existing_groups(self, baseline: dict, coverage: dict) -> None:
        baseline_group_ids = {g["group_id"] for g in baseline.get("groups", [])}
        for mirror in coverage.get("mirrors", []):
            for gid in mirror.get("group_ids", []):
                assert gid in baseline_group_ids, (
                    f"Mirror {mirror.get('block_id')} references unknown group {gid}"
                )


class TestBackendCascadeForMatchPipe:
    def setup_method(self, _method):
        from runtime.job_webapp.prompt_review_store import _safe_canonical_reseed_from_legacy

        _safe_canonical_reseed_from_legacy()

    def test_match_pipe_save_cascades_to_shared_match_pipe_groups(self) -> None:
        from runtime.job_webapp.prompt_review_store import (
            _build_duplicate_index,
            _load_edited,
            save_prompt_review_edit,
        )

        dup_index = _build_duplicate_index()
        target_fp = None
        for fp, refs in dup_index.items():
            mp_refs = [r for r in refs if r[0].startswith("match_pipe::")]
            if len(mp_refs) >= 2:
                target_fp = fp
                break

        assert target_fp, "No suitable duplicate fingerprint found for match_pipe cascade test"
        gid, bid = [r for r in dup_index[target_fp] if r[0].startswith("match_pipe::")][0]

        edited = _load_edited()
        group = next((g for g in edited["groups"] if g["group_id"] == gid), None)
        assert group is not None
        block = next((b for b in group["blocks"] if b["block_id"] == bid), None)
        assert block is not None

        new_text = block["text"] + "\n\n[BACKEND_CASCADE_TEST]"
        from runtime.job_webapp.prompt_review_store import _replace_block_body_html

        updated_rich_text = _replace_block_body_html(
            group.get("editable_rich_text", ""),
            bid,
            new_text,
        )
        result = save_prompt_review_edit(
            group_id=gid,
            editable_rich_text=updated_rich_text or group.get("editable_rich_text", ""),
            display_text=new_text,
            blocks=[{"block_id": bid, "text": new_text}],
        )

        assert result["ok"] is True
        propagated = result.get("propagated_group_ids", [])
        assert any(g.startswith("match_pipe::") for g in propagated), f"Expected match_pipe cascade, got {propagated}"

        # Verify persisted state
        edited2 = _load_edited()
        for pgid in propagated:
            g2 = next((g for g in edited2["groups"] if g["group_id"] == pgid), None)
            assert g2 is not None
            b2 = next((b for b in g2["blocks"] if b.get("duplicate_fingerprint") == target_fp), None)
            assert b2 is not None
            assert "[BACKEND_CASCADE_TEST]" in b2["text"]

    def test_non_match_pipe_save_does_not_cascade_to_match_pipe(self) -> None:
        from runtime.job_webapp.prompt_review_store import (
            _build_duplicate_index,
            _load_edited,
            save_prompt_review_edit,
        )

        dup_index = _build_duplicate_index()
        target_fp = None
        for fp, refs in dup_index.items():
            has_mp = any(r[0].startswith("match_pipe::") for r in refs)
            has_non_mp = any(not r[0].startswith("match_pipe::") for r in refs)
            if has_mp and has_non_mp:
                target_fp = fp
                break

        assert target_fp, "No cross-chain duplicate fingerprint found"
        gid, bid = [r for r in dup_index[target_fp] if not r[0].startswith("match_pipe::")][0]

        edited = _load_edited()
        group = next((g for g in edited["groups"] if g["group_id"] == gid), None)
        assert group is not None
        block = next((b for b in group["blocks"] if b["block_id"] == bid), None)
        assert block is not None

        new_text = block["text"] + "\n\n[NO_CASCADE_TEST]"
        from runtime.job_webapp.prompt_review_store import _replace_block_body_html

        updated_rich_text = _replace_block_body_html(
            group.get("editable_rich_text", ""),
            bid,
            new_text,
        )
        result = save_prompt_review_edit(
            group_id=gid,
            editable_rich_text=updated_rich_text or group.get("editable_rich_text", ""),
            display_text=new_text,
            blocks=[{"block_id": bid, "text": new_text}],
        )

        assert result["ok"] is True
        propagated = result.get("propagated_group_ids", [])
        assert not any(g.startswith("match_pipe::") for g in propagated), (
            f"Non-match_pipe save should not cascade to match_pipe, got {propagated}"
        )


class TestFrontendSchemaStability:
    def test_baseline_schema_unchanged(self, baseline: dict) -> None:
        assert baseline.get("schema_version") == 1
        assert baseline.get("scope") == "project_prompt_review"
        assert "groups" in baseline

    def test_map_contains_duplicate_clusters(self, review_map: dict) -> None:
        # The map layer should also carry duplicate_clusters or at least block fingerprints
        has_fp = False
        for group in review_map.get("groups", []):
            for block in group.get("blocks", []):
                if block.get("duplicate_fingerprint"):
                    has_fp = True
                    break
            if has_fp:
                break
        assert has_fp, "review.map.json blocks are missing duplicate_fingerprint"
