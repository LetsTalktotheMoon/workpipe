#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "runtime") not in sys.path:
    sys.path.insert(0, str(ROOT / "runtime"))

from repo_paths import relative_doc_link, repo_relative_path, resolve_repo_path
from runtime.automation.portfolio import rebuild_portfolio_indexes

TARGET_DIRS = [
    ROOT / "artifacts",
    ROOT / "build_skills",
    ROOT / "data" / "deliverables" / "resume_portfolio",
    ROOT / "docs",
    ROOT / "output" / "analysis",
    ROOT / "output" / "backfill_status",
    ROOT / "prompt_review",
    ROOT / "reviewer-compare",
    ROOT / "runtime" / "config",
]
TARGET_FILES = [
    ROOT / "README.md",
    ROOT / "MIGRATION_STATUS.md",
    ROOT / "SESSION_HANDOFF_2026-04-09.md",
]
TEXT_SUFFIXES = {".html", ".log", ".md", ".txt"}
JSON_SUFFIXES = {".json", ".jsonl"}
ABSOLUTE_PATH_RE = re.compile(
    r"(?P<path>/[^\s<>'\"`\]\)]+local_job_resume_pipeline(?:_prompt_worktree|_integration)?(?:/[^\s<>'\"`\]\)]+)+)(?::(?P<line>\d+))?"
)
FILE_URI_RE = re.compile(r"file://(?P<path>/[^\"'\s<>]+)")


def _split_line_suffix(raw: str) -> tuple[str, str]:
    match = re.match(r"^(?P<path>.+?)(?::(?P<line>\d+))?$", raw)
    if match is None:
        return raw, ""
    path = match.group("path") or raw
    line = match.group("line") or ""
    return path, f":{line}" if line else ""


def _replace_file_uri(text: str, *, doc_path: Path) -> str:
    def repl(match: re.Match[str]) -> str:
        raw = match.group("path")
        pure_path, _ = _split_line_suffix(raw)
        return relative_doc_link(doc_path, pure_path)

    return FILE_URI_RE.sub(repl, text)


def _replace_plain_paths(text: str, *, doc_path: Path | None, mode: str) -> str:
    def repl(match: re.Match[str]) -> str:
        raw = match.group("path")
        line_suffix = f":{match.group('line')}" if match.group("line") else ""
        if mode == "doc" and doc_path is not None:
            return relative_doc_link(doc_path, raw) + line_suffix
        return repo_relative_path(raw) + line_suffix

    return ABSOLUTE_PATH_RE.sub(repl, text)


def rewrite_text(text: str, *, path: Path, mode: str) -> str:
    rewritten = _replace_file_uri(text, doc_path=path)
    rewritten = _replace_plain_paths(rewritten, doc_path=path if mode == "doc" else None, mode=mode)
    return rewritten


def rewrite_json_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: rewrite_json_payload(item) for key, item in value.items()}
    if isinstance(value, list):
        return [rewrite_json_payload(item) for item in value]
    if isinstance(value, str):
        return rewrite_text(value, path=ROOT / "_json_context", mode="repo")
    return value


def rewrite_json_file(path: Path) -> bool:
    if path.suffix == ".jsonl":
        lines = path.read_text(encoding="utf-8").splitlines()
        rewritten_lines = []
        changed = False
        for line in lines:
            if not line.strip():
                rewritten_lines.append(line)
                continue
            payload = json.loads(line)
            rewritten = rewrite_json_payload(payload)
            if rewritten != payload:
                changed = True
            rewritten_lines.append(json.dumps(rewritten, ensure_ascii=False))
        if changed:
            path.write_text("\n".join(rewritten_lines) + "\n", encoding="utf-8")
        return changed

    payload = json.loads(path.read_text(encoding="utf-8"))
    rewritten = rewrite_json_payload(payload)
    if rewritten == payload:
        return False
    path.write_text(json.dumps(rewritten, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


def rewrite_text_file(path: Path) -> bool:
    mode = "repo" if path.name.startswith("latest_") else "doc"
    original = path.read_text(encoding="utf-8")
    rewritten = rewrite_text(original, path=path, mode=mode)
    if rewritten == original:
        return False
    path.write_text(rewritten, encoding="utf-8")
    return True


def iter_target_files() -> list[Path]:
    files: list[Path] = [path for path in TARGET_FILES if path.exists()]
    for root in TARGET_DIRS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix in JSON_SUFFIXES or path.suffix in TEXT_SUFFIXES:
                files.append(path)
    return sorted(files)


def main() -> None:
    changed = 0
    rebuild_portfolio_indexes(ROOT / "data" / "deliverables" / "resume_portfolio")
    for path in iter_target_files():
        if path.suffix in JSON_SUFFIXES:
            changed += int(rewrite_json_file(path))
        elif path.suffix in TEXT_SUFFIXES:
            changed += int(rewrite_text_file(path))
    print(json.dumps({"changed_files": changed}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
