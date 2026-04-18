from __future__ import annotations

import hashlib
import html
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PROMPT_REVIEW_DIR = ROOT / "prompt_review"
BASELINE_PATH = PROMPT_REVIEW_DIR / "review.baseline.json"
EDITED_PATH = PROMPT_REVIEW_DIR / "review.edited.json"
REGENERATED_PATH = PROMPT_REVIEW_DIR / "review.regenerated.json"
MAP_PATH = PROMPT_REVIEW_DIR / "review.map.json"
PATCH_LOG_PATH = PROMPT_REVIEW_DIR / "patch.log.json"
COVERAGE_PATH = PROMPT_REVIEW_DIR / "coverage.report.json"
AMBIGUITIES_PATH = PROMPT_REVIEW_DIR / "ambiguities.json"
ROUNDTRIP_PATH = PROMPT_REVIEW_DIR / "roundtrip.report.json"
README_PATH = PROMPT_REVIEW_DIR / "README.md"
REVISIONS_DIR = PROMPT_REVIEW_DIR / "revisions"
REVISIONS_INDEX_PATH = REVISIONS_DIR / "revisions.index.json"
CONFLICTS_DIR = PROMPT_REVIEW_DIR / "conflicts"
CONFLICTS_HISTORY_DIR = CONFLICTS_DIR / "history"
ACTIVE_CONFLICT_PATH = CONFLICTS_DIR / "active.json"

SCHEMA_VERSION = 1
SCOPE = "project_prompt_review"

_TAG_RE = re.compile(r"<[^>]+>")
_PLACEHOLDER_RE = re.compile(r"\{[a-zA-Z0-9_]+\}")
_BRACKET_PLACEHOLDER_RE = re.compile(r"\[[^\]\n]{1,160}\]")


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def ensure_prompt_review_dirs() -> None:
    PROMPT_REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    REVISIONS_DIR.mkdir(parents=True, exist_ok=True)
    CONFLICTS_HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def normalized_text(text: str) -> str:
    compact = re.sub(r"\s+", " ", str(text or "").strip())
    return compact


def sha256_text(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def extract_placeholders(text: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for pattern in (_PLACEHOLDER_RE, _BRACKET_PLACEHOLDER_RE):
        for match in pattern.findall(str(text or "")):
            if match in seen:
                continue
            seen.add(match)
            found.append(match)
    return found


def html_to_text(raw_html: str) -> str:
    text = str(raw_html or "")
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</(p|div|section|article|h1|h2|h3|h4|h5|h6|li|ul|ol|pre|blockquote)>", "\n", text)
    text = _TAG_RE.sub("", text)
    text = html.unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def text_to_rich_html(text: str, *, group_id: str, blocks: list[dict[str, Any]]) -> str:
    parts = [f'<article class="prompt-review-group" data-group-id="{html.escape(group_id, quote=True)}">']
    for block in blocks:
        source_json = html.escape(json.dumps(block.get("source_refs", []), ensure_ascii=False), quote=True)
        block_id = html.escape(str(block.get("block_id", "")), quote=True)
        title = html.escape(str(block.get("title", block.get("block_id", ""))))
        prompt_section = html.escape(str(block.get("prompt_section", "")), quote=True)
        parts.append(
            f'<section class="prompt-review-block" data-block-id="{block_id}" '
            f'data-prompt-section="{prompt_section}" data-source-refs="{source_json}">'
        )
        parts.append(f"<h4>{title}</h4>")
        parts.append(f"<pre>{html.escape(str(block.get('text', '')))}</pre>")
        parts.append("</section>")
    parts.append("</article>")
    return "\n".join(parts)


def build_revision_id(sequence: int) -> str:
    return f"rev-{datetime.now().strftime('%Y%m%dT%H%M%S')}-{sequence:04d}"


def build_patch_id(sequence: int) -> str:
    return f"patch-{datetime.now().strftime('%Y%m%dT%H%M%S')}-{sequence:04d}"


def empty_patch_log() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "patches": [],
    }


def empty_ambiguities() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "items": [],
    }


def empty_conflict_state() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "frozen": False,
        "trigger_revision_id": "",
        "reason": "",
        "affected_groups": [],
        "details": [],
        "next_action": "",
        "updated_at": now_iso(),
    }


def empty_roundtrip_report() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "generated_at": now_iso(),
        "status": "not_run",
        "summary": {},
        "groups": [],
    }
