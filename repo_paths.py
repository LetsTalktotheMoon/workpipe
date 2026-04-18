from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import unquote, urlparse


REPO_ROOT = Path(__file__).resolve().parent
KNOWN_WORKTREE_NAMES = {
    REPO_ROOT.name,
    "local_job_resume_pipeline",
    "local_job_resume_pipeline_prompt_worktree",
    "local_job_resume_pipeline_integration",
}


def _as_path(value: str | Path | None) -> Path:
    if isinstance(value, Path):
        return value
    return Path(str(value or "").strip())


def _strip_file_uri(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "file":
        return value
    return unquote(parsed.path)


def resolve_repo_path(value: str | Path | None, *, base: Path | None = None) -> Path:
    path = _as_path(_strip_file_uri(str(value or "").strip()))
    if not str(path):
        return (base or REPO_ROOT)
    if path.is_absolute():
        relative = _legacy_relative_from_path(path)
        if relative is not None:
            return (REPO_ROOT / relative).resolve()
        return path
    return ((base or REPO_ROOT) / path).resolve()


def repo_relative_path(value: str | Path | None, *, base: Path | None = None) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    resolved = resolve_repo_path(text, base=base)
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        legacy_relative = _legacy_relative_from_path(resolved)
        if legacy_relative is not None:
            return legacy_relative.as_posix()
        return resolved.as_posix()


def relative_doc_link(source: str | Path, target: str | Path | None) -> str:
    target_text = str(target or "").strip()
    if not target_text:
        return ""
    source_path = resolve_repo_path(source)
    source_dir = source_path if source_path.is_dir() else source_path.parent
    target_path = resolve_repo_path(target)
    return Path(os.path.relpath(target_path, source_dir)).as_posix()


def _legacy_relative_from_path(path: Path) -> Path | None:
    parts = path.parts
    for index, part in enumerate(parts):
        if part in KNOWN_WORKTREE_NAMES:
            return Path(*parts[index + 1 :])
    return None
