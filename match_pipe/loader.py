from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from repo_paths import repo_relative_path
from runtime.automation.jd_builder import row_to_jd_markdown

from .models import JobDocument


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCRAPED_PATH = ROOT / "data" / "job_tracker" / "jobs_catalog.json"
DEFAULT_PORTFOLIO_ROOT = ROOT / "data" / "deliverables" / "resume_portfolio"


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _row_to_document(
    row: dict[str, Any],
    *,
    source_kind: str,
    raw_text: str | None = None,
    artifact_dir: Path | None = None,
    manifest: dict[str, Any] | None = None,
) -> JobDocument | None:
    job_id = str(row.get("job_id", "") or "").strip()
    title = str(row.get("job_title", "") or row.get("job_nlp_title", "") or "").strip()
    if not job_id or not title:
        return None
    if raw_text is None:
        raw_text = row_to_jd_markdown(row)
    return JobDocument(
        job_id=job_id,
        company_name=str(row.get("company_name", "") or "").strip(),
        title=title,
        raw_text=raw_text,
        source_kind=source_kind,
        metadata={
            "publish_time": str(row.get("publish_time", "") or "").strip(),
            "taxonomy_v3": str(row.get("taxonomy_v3", "") or "").strip(),
            "work_model": str(row.get("work_model", "") or "").strip(),
            "employment_type": str(row.get("employment_type", "") or "").strip(),
            "artifact_dir": repo_relative_path(artifact_dir) if artifact_dir else "",
            "review_final_score": float((manifest or {}).get("review_final_score", 0.0) or 0.0),
            "review_verdict": str((manifest or {}).get("review_verdict", "") or ""),
            "route_mode": str((manifest or {}).get("route_mode", "") or ""),
            "seed_label": str((manifest or {}).get("seed_label", "") or ""),
        },
        row=row,
    )


def document_from_row(
    row: dict[str, Any],
    *,
    source_kind: str = "ad_hoc",
    raw_text: str | None = None,
    artifact_dir: Path | None = None,
) -> JobDocument | None:
    return _row_to_document(
        row,
        source_kind=source_kind,
        raw_text=raw_text,
        artifact_dir=artifact_dir,
    )


def _load_scraped_jobs(scraped_path: Path) -> list[JobDocument]:
    rows = _load_json(scraped_path, default=[])
    if not isinstance(rows, list):
        return []
    documents: list[JobDocument] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        document = _row_to_document(row, source_kind="scraped")
        if document is not None:
            documents.append(document)
    return documents


def _load_portfolio_jobs(portfolio_root: Path) -> list[JobDocument]:
    documents: list[JobDocument] = []
    for row_path in sorted(portfolio_root.glob("by_company/*/*/*/sheet_row.json")):
        row = _load_json(row_path, default={})
        if not isinstance(row, dict):
            continue
        artifact_dir = row_path.parent
        manifest_path = artifact_dir / "manifest.json"
        manifest = _load_json(manifest_path, default={}) if manifest_path.exists() else {}
        job_md_path = artifact_dir / "job.md"
        raw_text = job_md_path.read_text(encoding="utf-8") if job_md_path.exists() else None
        document = _row_to_document(
            row,
            source_kind="portfolio_history",
            raw_text=raw_text,
            artifact_dir=artifact_dir,
            manifest=manifest if isinstance(manifest, dict) else None,
        )
        if document is not None:
            documents.append(document)
    return documents


def load_job_documents(
    *,
    scraped_path: str | Path = DEFAULT_SCRAPED_PATH,
    portfolio_root: str | Path = DEFAULT_PORTFOLIO_ROOT,
    include_scraped: bool = True,
    include_portfolio: bool = True,
) -> list[JobDocument]:
    documents_by_id: dict[str, JobDocument] = {}
    if include_portfolio:
        for document in _load_portfolio_jobs(Path(portfolio_root)):
            documents_by_id[document.job_id] = document
    if include_scraped:
        for document in _load_scraped_jobs(Path(scraped_path)):
            existing = documents_by_id.get(document.job_id)
            if existing is None or existing.source_kind != "portfolio_history":
                documents_by_id[document.job_id] = document
    return sorted(
        documents_by_id.values(),
        key=lambda item: (
            item.metadata.get("publish_time", ""),
            item.job_id,
        ),
        reverse=True,
    )
