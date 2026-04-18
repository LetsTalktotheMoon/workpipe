from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from runtime.job_webapp.prompt_review_writeback_dryrun import (
    _should_block,
    run_writeback_dryrun,
)


def _make_block(**kwargs):
    defaults = {
        "write_policy": "direct",
        "propagation_rule": "auto",
        "confidence": 0.95,
        "source_refs": [
            {"path": "match_pipe/prompt_overrides.json", "source_type": "json_override", "object_path": "blocks.test"}
        ],
        "primary_source": {"path": "match_pipe/prompt_overrides.json", "source_type": "json_override"},
    }
    defaults.update(kwargs)
    return defaults


class TestShouldBlock:
    def test_blocked_when_all_four_rules_match(self):
        block = _make_block(
            write_policy="ambiguous",
            propagation_rule="manual_review_before_writeback",
            confidence=0.8,
        )
        is_blocked, reason = _should_block(block, "source_reference::example")
        assert is_blocked is True
        assert "ambiguous" in reason

    def test_blocked_when_any_single_rule_matches(self):
        # ambiguous policy alone
        is_blocked, reason = _should_block(
            _make_block(write_policy="ambiguous", propagation_rule="auto"),
            "other_group",
        )
        assert is_blocked is True
        assert "ambiguous" in reason

        # manual_review_before_writeback propagation alone
        is_blocked, reason = _should_block(
            _make_block(write_policy="direct", propagation_rule="manual_review_before_writeback"),
            "other_group",
        )
        assert is_blocked is True
        assert "manual_review_before_writeback" in reason

        # source_reference:: prefix alone (blocked by source_type / policy)
        is_blocked, reason = _should_block(
            _make_block(
                write_policy="direct",
                propagation_rule="auto",
                source_refs=[{"path": "docs/x.md", "source_type": "markdown_document"}],
                primary_source={"path": "docs/x.md", "source_type": "markdown_document"},
            ),
            "source_reference::example",
        )
        # markdown_document is blocked unless force_docs, which is off by default
        assert is_blocked is True

        # confidence < 0.9 alone for python_constant
        is_blocked, reason = _should_block(
            _make_block(
                write_policy="direct",
                propagation_rule="auto",
                confidence=0.5,
                source_refs=[{"path": "runtime/core/prompt_builder.py", "source_type": "python_constant"}],
                primary_source={"path": "runtime/core/prompt_builder.py", "source_type": "python_constant"},
            ),
            "other_group",
        )
        assert is_blocked is True
        assert "confidence" in reason

    def test_not_blocked_when_none_match(self):
        block = _make_block()
        is_blocked, reason = _should_block(block, "runtime_main::generate::writer")
        assert is_blocked is False
        assert reason == ""


class TestRunWritebackDryrun:
    def test_report_structure_and_dry_run_flag(self, tmp_path: Path):
        report_path = tmp_path / "writeback.dryrun.report.json"
        report = run_writeback_dryrun(output_path=report_path, write_report=True)

        assert report["dry_run"] is True
        assert "generated_at" in report
        assert "planned_writes" in report
        assert "blocked" in report
        assert "requires_human_review" in report
        assert "summary" in report
        assert "ok" in report
        assert report_path.exists()

        loaded = json.loads(report_path.read_text(encoding="utf-8"))
        assert loaded["dry_run"] is True

    def test_report_summary_counts(self, tmp_path: Path):
        report_path = tmp_path / "writeback.dryrun.report.json"
        report = run_writeback_dryrun(output_path=report_path, write_report=False)

        summary = report["summary"]
        assert "total_blocks" in summary
        assert "planned_count" in summary
        assert "blocked_count" in summary
        assert "requires_human_review_count" in summary
        assert isinstance(summary["total_blocks"], int)

    def test_planned_and_blocked_entries_have_required_fields(self, tmp_path: Path):
        report = run_writeback_dryrun(output_path=tmp_path / "report.json", write_report=False)

        for item in report["planned_writes"]:
            assert "group_id" in item
            assert "block_id" in item
            assert "policy" in item
            assert "reason" in item
            assert "source_refs" in item
            assert "primary_source" in item

        for item in report["blocked"]:
            assert "group_id" in item
            assert "block_id" in item
            assert "policy" in item
            assert "reason" in item
            assert "source_refs" in item
            assert "primary_source" in item

    def test_changed_direct_block_enters_planned_writes(self, tmp_path: Path):
        from runtime.job_webapp.prompt_review_writeback_dryrun import _ARTIFACT_PATHS

        original = dict(_ARTIFACT_PATHS)
        try:
            map_path = tmp_path / "map.json"
            baseline_path = tmp_path / "baseline.json"
            edited_path = tmp_path / "edited.json"
            for name in ["regenerated", "patch_log", "ambiguities", "conflicts", "roundtrip"]:
                (tmp_path / f"{name}.json").write_text("{}", encoding="utf-8")

            map_data = {
                "groups": [
                    {
                        "group_id": "test_group",
                        "blocks": [
                            {
                                "block_id": "b1",
                                "write_policy": "direct",
                                "propagation_rule": "auto",
                                "confidence": 0.95,
                                "source_refs": [
                                    {"path": "match_pipe/prompt_overrides.json", "source_type": "json_override", "object_path": "blocks.b1"}
                                ],
                                "primary_source": {"path": "match_pipe/prompt_overrides.json", "source_type": "json_override"},
                            }
                        ],
                    }
                ]
            }
            baseline_data = {
                "groups": [
                    {
                        "group_id": "test_group",
                        "blocks": [{"block_id": "b1", "text": "old text"}],
                    }
                ]
            }
            edited_data = {
                "groups": [
                    {
                        "group_id": "test_group",
                        "blocks": [{"block_id": "b1", "text": "new text"}],
                    }
                ]
            }

            map_path.write_text(json.dumps(map_data), encoding="utf-8")
            baseline_path.write_text(json.dumps(baseline_data), encoding="utf-8")
            edited_path.write_text(json.dumps(edited_data), encoding="utf-8")

            _ARTIFACT_PATHS["map"] = map_path
            _ARTIFACT_PATHS["baseline"] = baseline_path
            _ARTIFACT_PATHS["edited"] = edited_path
            _ARTIFACT_PATHS["regenerated"] = tmp_path / "regenerated.json"
            _ARTIFACT_PATHS["patch_log"] = tmp_path / "patch_log.json"
            _ARTIFACT_PATHS["ambiguities"] = tmp_path / "ambiguities.json"
            _ARTIFACT_PATHS["conflicts"] = tmp_path / "conflicts.json"
            _ARTIFACT_PATHS["roundtrip"] = tmp_path / "roundtrip.json"

            report = run_writeback_dryrun(output_path=tmp_path / "report.json", write_report=False)
            assert any(
                item["block_id"] == "b1" and item["policy"] == "direct"
                for item in report["planned_writes"]
            ), f"Expected direct block in planned_writes, got {report['planned_writes']}"
        finally:
            _ARTIFACT_PATHS.clear()
            _ARTIFACT_PATHS.update(original)

    def test_no_actual_source_files_modified(self, tmp_path: Path):
        from runtime.job_webapp.prompt_review_writeback_dryrun import _ARTIFACT_PATHS

        mtimes_before = {k: v.stat().st_mtime if v.exists() else None for k, v in _ARTIFACT_PATHS.items()}
        run_writeback_dryrun(output_path=tmp_path / "report.json", write_report=False)
        mtimes_after = {k: v.stat().st_mtime if v.exists() else None for k, v in _ARTIFACT_PATHS.items()}

        assert mtimes_before == mtimes_after

    def test_ok_true_even_when_blocked_items_exist(self, tmp_path: Path):
        report = run_writeback_dryrun(output_path=tmp_path / "report.json", write_report=False)
        if report["summary"]["blocked_count"] > 0:
            assert report["ok"] is True
        else:
            pytest.skip("No blocked items in current repo artifacts to verify this behavior")

    def test_main_returns_zero_for_current_repo_artifacts(self, tmp_path: Path):
        from runtime.job_webapp.prompt_review_writeback_dryrun import main

        out = tmp_path / "report.json"
        rc = main(["--output-path", str(out)])
        assert rc == 0
        assert out.exists()

    def test_cli_main_runs(self):
        from runtime.job_webapp.prompt_review_writeback_dryrun import main

        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "report.json"
            rc = main(["--output-path", str(out), "--no-report"])
            assert rc in (0, 1)
