from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from runtime.job_webapp.prompt_review_writeback import (
    _backup,
    _patch_json_override,
    _patch_markdown_document,
    _patch_python_constant,
    _should_block_writeback,
    run_writeback,
)


class TestShouldBlockWriteback:
    def test_json_override_never_blocked(self):
        block = {
            "write_policy": "direct",
            "propagation_rule": "auto",
            "confidence": 0.84,
            "source_refs": [
                {
                    "path": "match_pipe/prompt_overrides.json",
                    "source_type": "json_override",
                    "object_path": "blocks.writer_system",
                }
            ],
            "primary_source": {
                "path": "runtime/job_webapp/prompt_library.py",
                "source_type": "prompt_block",
            },
        }
        blocked, reason = _should_block_writeback(block)
        assert blocked is False

    def test_python_constant_blocked_when_low_confidence(self):
        block = {
            "write_policy": "direct",
            "propagation_rule": "auto",
            "confidence": 0.5,
            "source_refs": [
                {
                    "path": "runtime/core/prompt_builder.py",
                    "source_type": "python_constant",
                    "object_path": "MASTER_WRITER_SYSTEM",
                }
            ],
            "primary_source": {
                "path": "runtime/core/prompt_builder.py",
                "source_type": "python_constant",
            },
        }
        blocked, reason = _should_block_writeback(block)
        assert blocked is True
        assert "confidence" in reason

    def test_python_constant_allowed_when_high_confidence(self):
        block = {
            "write_policy": "direct",
            "propagation_rule": "auto",
            "confidence": 0.98,
            "source_refs": [
                {
                    "path": "runtime/core/prompt_builder.py",
                    "source_type": "python_constant",
                    "object_path": "MASTER_WRITER_SYSTEM",
                }
            ],
            "primary_source": {
                "path": "runtime/core/prompt_builder.py",
                "source_type": "python_constant",
            },
        }
        blocked, reason = _should_block_writeback(block)
        assert blocked is False

    def test_python_function_always_blocked(self):
        block = {
            "write_policy": "direct",
            "propagation_rule": "auto",
            "confidence": 0.98,
            "source_refs": [
                {
                    "path": "runtime/core/prompt_builder.py",
                    "source_type": "python_function",
                    "object_path": "build_master_writer_prompt",
                }
            ],
            "primary_source": {
                "path": "runtime/core/prompt_builder.py",
                "source_type": "python_function",
            },
        }
        blocked, reason = _should_block_writeback(block)
        assert blocked is True
        assert "unsupported" in reason

    def test_markdown_document_blocked_by_default(self):
        block = {
            "write_policy": "ambiguous",
            "propagation_rule": "manual_review_before_writeback",
            "confidence": 0.7,
            "source_refs": [
                {
                    "path": "docs/prompt_canonical_review.md",
                    "source_type": "markdown_document",
                }
            ],
            "primary_source": {
                "path": "docs/prompt_canonical_review.md",
                "source_type": "markdown_document",
            },
        }
        blocked, reason = _should_block_writeback(block)
        assert blocked is True

    def test_markdown_document_allowed_with_force_docs(self):
        block = {
            "write_policy": "direct",
            "propagation_rule": "auto",
            "confidence": 0.7,
            "source_refs": [
                {
                    "path": "docs/prompt_canonical_review.md",
                    "source_type": "markdown_document",
                }
            ],
            "primary_source": {
                "path": "docs/prompt_canonical_review.md",
                "source_type": "markdown_document",
            },
        }
        blocked, reason = _should_block_writeback(block, force_docs=True)
        assert blocked is False


class TestPatchJsonOverride:
    def test_creates_missing_key(self, tmp_path: Path, monkeypatch):
        match_pipe_dir = tmp_path / "match_pipe"
        match_pipe_dir.mkdir(parents=True, exist_ok=True)
        overrides = match_pipe_dir / "prompt_overrides.json"
        overrides.write_text(json.dumps({"scope": "match_pipe", "blocks": {}}), encoding="utf-8")
        monkeypatch.setattr(
            "runtime.job_webapp.prompt_review_writeback.ROOT",
            tmp_path,
        )
        ok, msg = _patch_json_override("blocks.new_block", "new text")
        assert ok is True
        data = json.loads(overrides.read_text(encoding="utf-8"))
        assert data["blocks"]["new_block"] == "new text"


class TestPatchPythonConstant:
    def test_replaces_triple_quoted_string(self, tmp_path: Path):
        py_file = tmp_path / "test_const.py"
        py_file.write_text(
            'SOME_PROMPT = """original text"""\n',
            encoding="utf-8",
        )
        ok, msg = _patch_python_constant(py_file, "SOME_PROMPT", "replaced text")
        assert ok is True
        content = py_file.read_text(encoding="utf-8")
        assert 'SOME_PROMPT = """replaced text"""' in content

    def test_rejects_invalid_python(self, tmp_path: Path, monkeypatch):
        py_file = tmp_path / "test_const.py"
        py_file.write_text(
            'SOME_PROMPT = """original"""\n',
            encoding="utf-8",
        )
        import py_compile

        def fake_compile(*args, **kwargs):
            raise py_compile.PyCompileError(Exception, Exception("fail"), file="test.py")

        monkeypatch.setattr(py_compile, "compile", fake_compile)
        ok, msg = _patch_python_constant(py_file, "SOME_PROMPT", "replaced")
        assert ok is False
        assert "invalid python" in msg
        # Original file should remain unchanged because backup is not restored
        # (we didn't create a real backup in this isolated test).
        # Actually _backup is called before py_compile, so the file hasn't been written yet.
        assert py_file.read_text(encoding="utf-8") == 'SOME_PROMPT = """original"""\n'

    def test_switches_quote_delimiter_when_needed(self, tmp_path: Path):
        py_file = tmp_path / "test_const.py"
        py_file.write_text(
            'SOME_PROMPT = """original"""\n',
            encoding="utf-8",
        )
        ok, msg = _patch_python_constant(py_file, "SOME_PROMPT", "contains \"\"\"")
        assert ok is True
        content = py_file.read_text(encoding="utf-8")
        assert "SOME_PROMPT = '''contains \"\"\"'''" in content


class TestPatchMarkdownDocument:
    def test_overwrites_file(self, tmp_path: Path):
        md_file = tmp_path / "doc.md"
        md_file.write_text("old content", encoding="utf-8")
        ok, msg = _patch_markdown_document(md_file, "new content")
        assert ok is True
        assert md_file.read_text(encoding="utf-8") == "new content"


class TestRunWriteback:
    def test_dry_run_no_changes(self, monkeypatch):
        # Provide identical baseline and edited
        baseline = {"groups": []}
        edited = {"groups": []}
        monkeypatch.setattr(
            "runtime.job_webapp.prompt_review_writeback._ARTIFACT_PATHS",
            {"baseline": Path("/dev/null"), "edited": Path("/dev/null")},
        )
        # We can't easily monkeypatch _load_json because it checks path.exists.
        # Instead, override the whole function locally by monkeypatching the module dict.
        import runtime.job_webapp.prompt_review_writeback as wb

        original_load = wb._load_json
        def fake_load(path, default):
            if "baseline" in str(path):
                return baseline
            if "edited" in str(path):
                return edited
            return default
        monkeypatch.setattr(wb, "_load_json", fake_load)

        report = run_writeback(dry_run=True)
        assert report["ok"] is True
        assert report["dry_run"] is True
        assert report["patched_count"] == 0
        assert report["skipped_count"] == 0

    def test_blocks_unsupported_source_type(self, monkeypatch, tmp_path: Path):
        baseline = {
            "groups": [
                {
                    "group_id": "g1",
                    "blocks": [
                        {"block_id": "b1", "text": "old", "normalized_text": "old"}
                    ],
                }
            ]
        }
        edited = {
            "groups": [
                {
                    "group_id": "g1",
                    "blocks": [
                        {
                            "block_id": "b1",
                            "text": "new",
                            "normalized_text": "new",
                            "write_policy": "direct",
                            "propagation_rule": "auto",
                            "confidence": 0.98,
                            "source_refs": [
                                {
                                    "path": "runtime/core/prompt_builder.py",
                                    "source_type": "python_function",
                                    "object_path": "foo",
                                }
                            ],
                            "primary_source": {
                                "path": "runtime/core/prompt_builder.py",
                                "source_type": "python_function",
                                "object_path": "foo",
                            },
                        }
                    ],
                }
            ]
        }
        import runtime.job_webapp.prompt_review_writeback as wb

        def fake_load(path, default):
            if "baseline" in str(path):
                return baseline
            if "edited" in str(path):
                return edited
            return default
        monkeypatch.setattr(wb, "_load_json", fake_load)

        report = run_writeback(dry_run=False)
        assert report["blocked_count"] == 1
        assert report["patched_count"] == 0
        assert report["errors"] == []

    def test_creates_backup(self, tmp_path: Path):
        from runtime.job_webapp.prompt_review_writeback import BACKUP_DIR
        # Ensure BACKUP_DIR is under tmp_path so test is isolated
        original_backup_dir = BACKUP_DIR
        # We can't monkeypatch the global easily because it's used at module load time.
        # Instead test _backup directly by temporarily overriding the module global.
        import runtime.job_webapp.prompt_review_writeback as wb
        wb.BACKUP_DIR = tmp_path / "backups"
        try:
            file_to_backup = tmp_path / "source.py"
            file_to_backup.write_text("original", encoding="utf-8")
            backup_path = _backup(file_to_backup)
            assert backup_path.exists()
            assert backup_path.read_text(encoding="utf-8") == "original"
        finally:
            wb.BACKUP_DIR = original_backup_dir
