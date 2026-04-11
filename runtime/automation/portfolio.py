"""
Clean local portfolio publishing for real-job resumes.
"""
from __future__ import annotations

import json
import shutil
import zipfile
import fcntl
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Optional
from xml.sax.saxutils import escape

from automation.company_subseed_registry import load_company_subseed_registry
from automation.google_sheets import parse_publish_time
from automation.jd_builder import row_to_jd_markdown
from automation.project_pool import load_project_pool_registry
from automation.seed_registry import load_seed_registry
from automation.text_utils import slugify

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORTFOLIO_ROOT = ROOT / "deliverables" / "resume_portfolio"


def normalize_portfolio_root(path: str | Path | None = None) -> Path:
    if path is None:
        return DEFAULT_PORTFOLIO_ROOT
    root = Path(path)
    if not root.is_absolute():
        root = (ROOT / root).resolve()
    return root


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _publish_date(row: dict) -> str:
    parsed = parse_publish_time(row.get("publish_time", ""))
    if parsed is not None:
        return parsed.strftime("%Y-%m-%d")
    raw = str(row.get("publish_time", "") or "").strip()
    if len(raw) >= 10:
        return raw[:10]
    return "unknown-date"


def _job_title(row: dict) -> str:
    return str(row.get("job_title", "") or row.get("job_nlp_title", "") or "")


def _discover_pdf(resume_md_path: Path) -> Path | None:
    candidates = [
        resume_md_path.with_suffix(".pdf"),
        resume_md_path.parent / "resume.pdf",
        resume_md_path.parent / "pdf" / "resume.pdf",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def ensure_profiles_json(portfolio_root: str | Path | None = None) -> Path:
    root = normalize_portfolio_root(portfolio_root)
    root.mkdir(parents=True, exist_ok=True)
    profiles_path = root / "profiles.json"
    defaults = {
        "active_profile": "default",
        "profiles": [
            {
                "profile_id": "default",
                "name": "",
                "phone": "",
                "email": "",
            }
        ],
        "portfolio_root": str(root),
        "by_company_root": str(root / "by_company"),
        "by_date_root": str(root / "by_date"),
        "seeds_root": str(root / "seeds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "job_count": 0,
    }
    if profiles_path.exists():
        try:
            current = json.loads(profiles_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            current = {}
        payload = dict(current)
        payload.setdefault("active_profile", defaults["active_profile"])
        payload.setdefault("profiles", defaults["profiles"])
        payload.setdefault("portfolio_root", defaults["portfolio_root"])
        payload.setdefault("by_company_root", defaults["by_company_root"])
        payload.setdefault("by_date_root", defaults["by_date_root"])
        payload.setdefault("seeds_root", defaults["seeds_root"])
        if payload != current:
            _write_json(profiles_path, payload)
        return profiles_path
    _write_json(profiles_path, defaults)
    return profiles_path


def _remove_path(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    shutil.rmtree(path)


def _ensure_path_link(link_path: Path, target_path: Path) -> Path:
    _remove_path(link_path)
    link_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        link_path.symlink_to(target_path, target_is_directory=target_path.is_dir())
    except OSError:
        if target_path.is_dir():
            link_path.mkdir(parents=True, exist_ok=True)
            (link_path / "TARGET.txt").write_text(str(target_path), encoding="utf-8")
        else:
            link_path.write_text(str(target_path), encoding="utf-8")
    return link_path


def _ensure_by_date_link(root: Path, publish_date: str, job_id: str, target_dir: Path) -> Path:
    by_date_dir = root / "by_date" / publish_date
    by_date_dir.mkdir(parents=True, exist_ok=True)
    link_path = by_date_dir / job_id
    return _ensure_path_link(link_path, target_dir)


@lru_cache(maxsize=1)
def _portfolio_annotation_context() -> tuple[object, dict, dict]:
    registry = load_company_subseed_registry()
    direction_index = registry.direction_index()
    seeds = {
        seed.seed_id: seed for seed in load_seed_registry(include_atomizer=False, include_promoted=True)
    }
    return registry, direction_index, seeds


def _annotate_record_metadata(record: dict) -> dict:
    annotated = dict(record)
    registry, direction_index, seeds = _portfolio_annotation_context()

    seed_id = str(annotated.get("parent_seed_id", "") or annotated.get("seed_id", "") or "").strip()
    subseed_ids: list[str] = []
    if seed_id:
        seed = seeds.get(seed_id)
        if seed is not None and seed.subseed_ids:
            subseed_ids = list(seed.subseed_ids)
        else:
            subseed_ids = list(registry.seed_subseed_ids(seed_id))

    subseed_labels = [
        direction_index[subseed_id].label
        for subseed_id in subseed_ids
        if subseed_id in direction_index
    ]
    primary_subseed = direction_index.get(subseed_ids[0]) if subseed_ids else None
    outlier = registry.outlier_for_job(str(annotated.get("job_id", "") or ""))

    annotated.update(
        {
            "subseed_ids": subseed_ids,
            "subseed_labels": subseed_labels,
            "primary_subseed_id": primary_subseed.subseed_id if primary_subseed else "",
            "primary_subseed_label": primary_subseed.label if primary_subseed else "",
            "primary_subseed_kind": primary_subseed.kind if primary_subseed else "",
            "is_outlier": bool(outlier),
            "outlier_label": outlier.label if outlier else "",
            "outlier_reason": outlier.reason if outlier else "",
        }
    )
    return annotated


def publish_job_artifact(
    row: dict,
    resume_md_path: str | Path,
    *,
    portfolio_root: str | Path | None = None,
    source_kind: str,
    seed_id: str = "",
    seed_label: str = "",
    route_mode: str = "",
    top_candidate: Optional[dict] = None,
    review_payload: Optional[dict] = None,
    parent_seed_id: str = "",
    rebuild_indexes: bool = True,
    job_md_text: str = "",
) -> dict:
    root = normalize_portfolio_root(portfolio_root)
    ensure_profiles_json(root)

    resume_md_path = Path(resume_md_path)
    if not resume_md_path.is_absolute():
        resume_md_path = (ROOT / resume_md_path).resolve()
    if not resume_md_path.exists():
        raise FileNotFoundError(f"resume markdown not found: {resume_md_path}")

    job_id = str(row.get("job_id", "") or "").strip()
    if not job_id:
        raise ValueError("Sheet row is missing job_id")

    company_name = str(row.get("company_name", "") or "Unknown")
    company_slug = slugify(company_name) or "unknown-company"
    publish_date = _publish_date(row)
    job_dir = root / "by_company" / company_slug / publish_date / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    resume_target = job_dir / "resume.md"
    shutil.copyfile(resume_md_path, resume_target)

    pdf_source = _discover_pdf(resume_md_path)
    pdf_target = ""
    if pdf_source is not None:
        dest = job_dir / "resume.pdf"
        shutil.copyfile(pdf_source, dest)
        pdf_target = str(dest)

    jd_text = job_md_text or row_to_jd_markdown(row)
    (job_dir / "job.md").write_text(jd_text, encoding="utf-8")
    _write_json(job_dir / "sheet_row.json", row)
    if review_payload:
        _write_json(job_dir / "review.json", review_payload)

    link_path = _ensure_by_date_link(root, publish_date, job_id, job_dir)
    top_candidate = top_candidate or {}
    project_ids = [str(item).strip() for item in top_candidate.get("project_ids", []) if str(item).strip()]
    manifest = {
        "job_id": job_id,
        "company_name": company_name,
        "company_slug": company_slug,
        "publish_time": str(row.get("publish_time", "") or ""),
        "publish_date": publish_date,
        "title": _job_title(row),
        "application_status": str(row.get("application_status", "") or ""),
        "apply_link": str(row.get("apply_link", "") or ""),
        "source_kind": source_kind,
        "route_mode": route_mode,
        "seed_id": seed_id,
        "seed_label": seed_label,
        "parent_seed_id": parent_seed_id or seed_id,
        "top_candidate": top_candidate,
        "project_ids": project_ids,
        "resume_md": str(resume_target),
        "resume_pdf": pdf_target,
        "job_md": str(job_dir / "job.md"),
        "artifact_dir": str(job_dir),
        "by_date_link": str(link_path),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "review": review_payload or {},
    }
    manifest = _annotate_record_metadata(manifest)
    _write_json(job_dir / "manifest.json", manifest)
    if rebuild_indexes:
        rebuild_portfolio_indexes(root)
    return manifest


def delete_job_artifact(
    artifact_path: str | Path,
    *,
    portfolio_root: str | Path | None = None,
    rebuild_indexes: bool = True,
) -> dict:
    root = normalize_portfolio_root(portfolio_root)
    path = Path(artifact_path)
    if path.is_dir():
        manifest_path = path / "manifest.json"
    elif path.name == "manifest.json":
        manifest_path = path
    else:
        manifest_path = path.parent / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest not found for artifact: {artifact_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    job_dir = manifest_path.parent
    by_date_link = Path(str(manifest.get("by_date_link", "") or ""))
    _remove_path(by_date_link)
    _remove_path(job_dir)

    if rebuild_indexes:
        rebuild_portfolio_indexes(root)

    return {
        "job_id": str(manifest.get("job_id", "") or ""),
        "company_name": str(manifest.get("company_name", "") or ""),
        "artifact_dir": str(job_dir),
        "deleted": True,
    }


def collect_portfolio_records(portfolio_root: str | Path | None = None) -> list[dict]:
    root = normalize_portfolio_root(portfolio_root)
    records: list[dict] = []
    for path in sorted((root / "by_company").glob("*/*/*/manifest.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        annotated = _annotate_record_metadata(record)
        if annotated != record:
            _write_json(path, annotated)
        records.append(annotated)

    def sort_key(record: dict) -> tuple:
        parsed = parse_publish_time(record.get("publish_time", ""))
        sort_stamp = parsed.isoformat() if parsed is not None else record.get("publish_time", "")
        return (sort_stamp, record.get("company_name", ""), record.get("job_id", ""))

    records.sort(key=sort_key, reverse=True)
    return records


def _rebuild_by_date_views(root: Path, records: Iterable[dict]) -> None:
    by_date_root = root / "by_date"
    if by_date_root.exists():
        for child in by_date_root.iterdir():
            _remove_path(child)
    by_date_root.mkdir(parents=True, exist_ok=True)

    for record in records:
        artifact_dir = Path(str(record.get("artifact_dir", "") or "")).resolve()
        publish_date = str(record.get("publish_date", "") or "unknown-date")
        job_id = str(record.get("job_id", "") or "").strip()
        if not job_id or not artifact_dir.exists():
            continue
        _ensure_by_date_link(root, publish_date, job_id, artifact_dir)


def _write_seed_catalog(root: Path, records: Iterable[dict]) -> dict:
    seeds_root = root / "seeds"
    if seeds_root.exists():
        for child in seeds_root.iterdir():
            _remove_path(child)
    seeds_root.mkdir(parents=True, exist_ok=True)

    records_by_seed: dict[str, list[dict]] = {}
    source_record_by_seed: dict[str, dict] = {}
    for record in records:
        seed_id = str(record.get("parent_seed_id", "") or record.get("seed_id", "") or "").strip()
        if not seed_id:
            continue
        records_by_seed.setdefault(seed_id, []).append(record)
        if str(record.get("source_kind", "") or "") == "seed_source":
            source_record_by_seed[seed_id] = record

    catalog: list[dict] = []
    project_registry = load_project_pool_registry()
    subseed_registry = load_company_subseed_registry()
    direction_index = subseed_registry.direction_index()
    for seed in load_seed_registry(include_atomizer=False, include_promoted=True):
        seed_dir = seeds_root / seed.seed_id
        derived_dir = seed_dir / "derived_jobs"
        derived_dir.mkdir(parents=True, exist_ok=True)
        project_cards = [card.to_dict() for card in project_registry.project_cards_for_seed(seed.seed_id)]
        subseed_labels = [
            direction_index[subseed_id].label
            for subseed_id in seed.subseed_ids
            if subseed_id in direction_index
        ]

        source_path = seed.source_md.resolve()
        if source_path.exists():
            _ensure_path_link(seed_dir / "source_resume.md", source_path)

        source_record = source_record_by_seed.get(seed.seed_id)
        if source_record:
            artifact_dir = Path(str(source_record.get("artifact_dir", "") or "")).resolve()
            if artifact_dir.exists():
                _ensure_path_link(seed_dir / "source_artifact", artifact_dir)

        derived_records = sorted(
            records_by_seed.get(seed.seed_id, []),
            key=lambda item: (str(item.get("publish_time", "") or ""), str(item.get("job_id", "") or "")),
            reverse=True,
        )
        for record in derived_records:
            job_id = str(record.get("job_id", "") or "").strip()
            artifact_dir = Path(str(record.get("artifact_dir", "") or "")).resolve()
            if not job_id or not artifact_dir.exists():
                continue
            _ensure_path_link(derived_dir / job_id, artifact_dir)

        manifest = {
            "seed_id": seed.seed_id,
            "label": seed.label,
            "role_family": seed.role_family,
            "seniority": seed.seniority,
            "validated_score": seed.validated_score,
            "company_name": seed.company_name,
            "source_job_id": seed.source_job_id,
            "company_anchor": seed.company_anchor,
            "project_ids": list(seed.project_ids),
            "subseed_ids": list(seed.subseed_ids),
            "subseed_labels": subseed_labels,
            "project_cards": project_cards,
            "source_resume_md": str(source_path),
            "seed_dir": str(seed_dir),
            "source_artifact_dir": str(Path(str(source_record.get("artifact_dir", "") or "")).resolve()) if source_record else "",
            "derived_count": len(derived_records),
            "derived_jobs": [
                {
                    "job_id": str(record.get("job_id", "") or ""),
                    "company_name": str(record.get("company_name", "") or ""),
                    "publish_time": str(record.get("publish_time", "") or ""),
                    "title": str(record.get("title", "") or ""),
                    "source_kind": str(record.get("source_kind", "") or ""),
                    "route_mode": str(record.get("route_mode", "") or ""),
                    "artifact_dir": str(record.get("artifact_dir", "") or ""),
                    "resume_md": str(record.get("resume_md", "") or ""),
                    "resume_pdf": str(record.get("resume_pdf", "") or ""),
                }
                for record in derived_records
            ],
        }
        _write_json(seed_dir / "manifest.json", manifest)

        lines = [
            f"# {seed.label}",
            "",
            f"* `seed_id`: `{seed.seed_id}`",
            f"* `role_family`: `{seed.role_family}`",
            f"* `seniority`: `{seed.seniority}`",
            f"* `validated_score`: `{seed.validated_score or ''}`",
            f"* `company_name`: `{seed.company_name or ''}`",
            f"* `source_job_id`: `{seed.source_job_id or ''}`",
            f"* `project_ids`: `{', '.join(seed.project_ids) or ''}`",
            f"* `subseed_ids`: `{', '.join(seed.subseed_ids) or ''}`",
            f"* `source_resume_md`: {source_path}",
            f"* `source_artifact_dir`: {manifest['source_artifact_dir'] or ''}",
            f"* `derived_count`: `{len(derived_records)}`",
            "",
            "## Derived Jobs",
            "",
        ]
        if derived_records:
            for record in derived_records:
                lines.append(
                    f"- `{record.get('job_id', '')}` | {record.get('company_name', '')} | {record.get('publish_time', '')} | "
                    f"{record.get('title', '')} | {record.get('route_mode', '')} | {record.get('artifact_dir', '')}"
                )
        else:
            lines.append("- None yet")
        (seed_dir / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        catalog.append(manifest)

    _write_json(root / "seed_index.json", catalog)
    lines = ["# Seed Index", ""]
    for item in catalog:
        lines.append(
            f"- `{item['seed_id']}` | {item['label']} | score `{item['validated_score'] or ''}` | "
            f"derived `{item['derived_count']}` | {item['seed_dir']}"
        )
    (root / "seed_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "seed_count": len(catalog),
        "seeds_root": str(seeds_root),
        "seed_index_json": str(root / "seed_index.json"),
        "seed_index_markdown": str(root / "seed_index.md"),
    }


def _write_company_subseed_catalog(root: Path, records: Iterable[dict]) -> dict:
    registry = load_company_subseed_registry()
    subseeds_root = root / "subseeds"
    if subseeds_root.exists():
        for child in subseeds_root.iterdir():
            _remove_path(child)
    subseeds_root.mkdir(parents=True, exist_ok=True)

    record_list = list(records)
    records_by_seed: dict[str, list[dict]] = {}
    records_by_job_id: dict[str, dict] = {}
    for record in record_list:
        seed_id = str(record.get("parent_seed_id", "") or record.get("seed_id", "") or "").strip()
        if seed_id:
            records_by_seed.setdefault(seed_id, []).append(record)
        job_id = str(record.get("job_id", "") or "").strip()
        if job_id:
            records_by_job_id[job_id] = record

    payload: list[dict] = []
    lines = ["# Company Subseed Index", ""]
    seed_root = root / "seeds"

    for plan in registry.company_plans():
        company_dir = subseeds_root / plan.company_slug
        company_dir.mkdir(parents=True, exist_ok=True)

        company_payload = {
            "company_name": plan.company_name,
            "company_slug": plan.company_slug,
            "max_mainline_directions": plan.max_mainline_directions,
            "notes": plan.notes,
            "directions": [],
            "outlier_jobs": [],
        }
        lines.extend(
            [
                f"## {plan.company_name}",
                "",
                f"* `max_mainline_directions`: `{plan.max_mainline_directions}`",
                f"* `notes`: {plan.notes}",
                "",
            ]
        )

        for direction in plan.directions:
            direction_dir = company_dir / direction.subseed_id
            matched_dir = direction_dir / "matched_jobs"
            seed_links_dir = direction_dir / "seeds"
            matched_dir.mkdir(parents=True, exist_ok=True)
            seed_links_dir.mkdir(parents=True, exist_ok=True)

            matched_records = sorted(
                [
                    record
                    for seed_id in direction.seed_ids
                    for record in records_by_seed.get(seed_id, [])
                ],
                key=lambda item: (str(item.get("publish_time", "") or ""), str(item.get("job_id", "") or "")),
                reverse=True,
            )
            seen_jobs: set[str] = set()
            deduped_records: list[dict] = []
            for record in matched_records:
                job_id = str(record.get("job_id", "") or "").strip()
                if not job_id or job_id in seen_jobs:
                    continue
                seen_jobs.add(job_id)
                deduped_records.append(record)

            for seed_id in direction.seed_ids:
                seed_dir = seed_root / seed_id
                if seed_dir.exists():
                    _ensure_path_link(seed_links_dir / seed_id, seed_dir)

            for record in deduped_records:
                job_id = str(record.get("job_id", "") or "").strip()
                artifact_dir = Path(str(record.get("artifact_dir", "") or "")).resolve()
                if job_id and artifact_dir.exists():
                    _ensure_path_link(matched_dir / job_id, artifact_dir)

            manifest = direction.to_dict()
            manifest.update(
                {
                    "direction_dir": str(direction_dir),
                    "seed_dirs": [
                        str((seed_root / seed_id).resolve())
                        for seed_id in direction.seed_ids
                        if (seed_root / seed_id).exists()
                    ],
                    "derived_count": len(deduped_records),
                    "derived_jobs": [
                        {
                            "job_id": str(record.get("job_id", "") or ""),
                            "title": str(record.get("title", "") or ""),
                            "publish_time": str(record.get("publish_time", "") or ""),
                            "route_mode": str(record.get("route_mode", "") or ""),
                            "source_kind": str(record.get("source_kind", "") or ""),
                            "artifact_dir": str(record.get("artifact_dir", "") or ""),
                            "is_outlier": bool(record.get("is_outlier", False)),
                        }
                        for record in deduped_records
                    ],
                }
            )
            _write_json(direction_dir / "manifest.json", manifest)

            direction_lines = [
                f"# {direction.label}",
                "",
                f"* `subseed_id`: `{direction.subseed_id}`",
                f"* `kind`: `{direction.kind}`",
                f"* `status`: `{direction.status}`",
                f"* `primary_seed_id`: `{direction.primary_seed_id}`",
                f"* `seed_ids`: `{', '.join(direction.seed_ids)}`",
                f"* `candidate_job_ids`: `{', '.join(direction.candidate_job_ids)}`",
                f"* `target_role_families`: `{', '.join(direction.target_role_families)}`",
                f"* `notes`: {direction.notes}",
                f"* `derived_count`: `{len(deduped_records)}`",
                "",
                "## Matched Jobs",
                "",
            ]
            if deduped_records:
                for record in deduped_records:
                    direction_lines.append(
                        f"- `{record.get('job_id', '')}` | {record.get('title', '')} | "
                        f"{record.get('route_mode', '')} | {record.get('artifact_dir', '')}"
                    )
            else:
                direction_lines.append("- None yet")
            (direction_dir / "index.md").write_text("\n".join(direction_lines) + "\n", encoding="utf-8")

            company_payload["directions"].append(manifest)
            lines.extend(
                [
                    f"### {direction.label}",
                    "",
                    f"* `subseed_id`: `{direction.subseed_id}`",
                    f"* `kind/status`: `{direction.kind}` / `{direction.status}`",
                    f"* `primary_seed_id`: `{direction.primary_seed_id}`",
                    f"* `seed_ids`: `{', '.join(direction.seed_ids)}`",
                    f"* `derived_count`: `{len(deduped_records)}`",
                    "",
                ]
            )

        outlier_dir = company_dir / "outliers"
        outlier_dir.mkdir(parents=True, exist_ok=True)
        if plan.outlier_jobs:
            lines.extend(["### Outliers", ""])
        for outlier in plan.outlier_jobs:
            record = records_by_job_id.get(outlier.job_id)
            if record:
                artifact_dir = Path(str(record.get("artifact_dir", "") or "")).resolve()
                if artifact_dir.exists():
                    _ensure_path_link(outlier_dir / outlier.job_id, artifact_dir)
            outlier_payload = {
                **outlier.to_dict(),
                "generated": bool(record),
                "artifact_dir": str(record.get("artifact_dir", "") or "") if record else "",
                "seed_id": str(record.get("seed_id", "") or "") if record else "",
                "final_score": (record.get("review") or {}).get("final_score", "") if record else "",
                "verdict": (record.get("review") or {}).get("verdict", "") if record else "",
            }
            company_payload["outlier_jobs"].append(outlier_payload)
            lines.append(
                f"- `{outlier.job_id}` | {outlier.title} | generated `{outlier_payload['generated']}` | {outlier.reason}"
            )
        if plan.outlier_jobs:
            lines.append("")
        payload.append(company_payload)

    _write_json(root / "company_subseed_index.json", payload)
    (root / "company_subseed_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "subseeds_root": str(subseeds_root),
        "company_subseed_index_json": str(root / "company_subseed_index.json"),
        "company_subseed_index_markdown": str(root / "company_subseed_index.md"),
    }


def _write_company_seed_index(root: Path) -> dict:
    registry = load_company_subseed_registry()
    direction_index = registry.direction_index()
    grouped: dict[str, list[dict]] = {}
    for seed in load_seed_registry(include_atomizer=False, include_promoted=True):
        grouped.setdefault(seed.company_name or "Unknown", []).append(
            {
                **seed.to_dict(),
                "subseed_labels": [
                    direction_index[subseed_id].label
                    for subseed_id in seed.subseed_ids
                    if subseed_id in direction_index
                ],
            }
        )

    payload = {}
    lines = ["# Company Seed Index", ""]
    for company in sorted(grouped):
        items = sorted(
            grouped[company],
            key=lambda item: (item.get("validated_score") or 0.0, item.get("seed_id") or ""),
            reverse=True,
        )
        payload[company] = items
        lines.extend([f"## {company}", ""])
        for item in items:
            lines.append(
                f"- `{item.get('seed_id', '')}` | {item.get('label', '')} | score `{item.get('validated_score', '')}` | "
                f"subseed `{', '.join(item.get('subseed_ids', []))}` | {item.get('source_md', '')}"
            )
        lines.append("")

    _write_json(root / "company_seed_index.json", payload)
    (root / "company_seed_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "company_seed_index_json": str(root / "company_seed_index.json"),
        "company_seed_index_markdown": str(root / "company_seed_index.md"),
    }


def _write_project_pool_index(root: Path) -> dict:
    registry = load_project_pool_registry()
    json_path = root / "experience_project_pool.json"
    markdown_path = root / "experience_project_pool.md"
    _write_json(json_path, registry.to_dict())

    lines = [
        "# Experience Project Pool",
        "",
        f"* `resume_project_limit`: `{registry.resume_project_limit}`",
        "",
    ]
    for pool in registry.company_pools:
        lines.extend(
            [
                f"## {pool.company_name}",
                "",
                f"* `max_projects`: `{pool.max_projects}`",
                f"* `aliases`: `{', '.join(pool.aliases)}`",
                f"* `notes`: {pool.notes}",
                "",
            ]
        )
        for project in pool.projects:
            lines.extend(
                [
                    f"### {project.project_id}",
                    "",
                    f"* `time`: `{project.start} -> {project.end}`",
                    f"* `team`: {project.team}",
                    f"* `business_domain`: {project.business_domain}",
                    f"* `project_goal`: {project.project_goal}",
                    f"* `scope_ceiling`: {project.scope_ceiling}",
                    f"* `ownership_ceiling`: {project.ownership_ceiling}",
                    f"* `allowed_tech_surface`: `{', '.join(project.allowed_tech_surface)}`",
                    f"* `allowed_role_lenses`: `{', '.join(project.allowed_role_lenses)}`",
                    f"* `needs_scope_note`: `{project.needs_scope_note}`",
                ]
            )
            if project.notes:
                lines.append(f"* `notes`: {project.notes}")
            lines.append("")
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "project_pool_json": str(json_path),
        "project_pool_markdown": str(markdown_path),
    }


def _xlsx_col_name(index: int) -> str:
    letters = []
    while index > 0:
        index, rem = divmod(index - 1, 26)
        letters.append(chr(65 + rem))
    return "".join(reversed(letters))


def _formula_literal(text: str) -> str:
    return text.replace('"', '""')


def _cell(ref: str, value, *, cell_type: str = "str") -> str:
    if value is None or value == "":
        return f'<c r="{ref}"/>'
    if cell_type == "num":
        return f'<c r="{ref}"><v>{value}</v></c>'
    if cell_type == "formula":
        return f'<c r="{ref}"><f>{escape(str(value))}</f></c>'
    return f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'


def _write_workbook(records: Iterable[dict], workbook_path: Path) -> None:
    headers = [
        "company_name",
        "publish_time",
        "job_id",
        "title",
        "application_status",
        "source_kind",
        "route_mode",
        "seed_id",
        "seed_label",
        "primary_subseed_id",
        "primary_subseed_kind",
        "is_outlier",
        "outlier_label",
        "final_score",
        "verdict",
        "resume_md",
        "resume_pdf",
        "apply_link",
    ]

    rows_xml = []
    for row_idx, header in enumerate([headers], start=1):
        cells = []
        for col_idx, value in enumerate(header, start=1):
            cells.append(_cell(f"{_xlsx_col_name(col_idx)}{row_idx}", value))
        rows_xml.append(f"<row r=\"{row_idx}\">{''.join(cells)}</row>")

    for row_idx, record in enumerate(records, start=2):
        review = record.get("review") or {}
        final_score = review.get("final_score") or review.get("weighted_score") or ""
        verdict = review.get("verdict") or review.get("overall_verdict") or ""
        values = [
            (record.get("company_name", ""), "str"),
            (record.get("publish_time", ""), "str"),
            (record.get("job_id", ""), "str"),
            (record.get("title", ""), "str"),
            (record.get("application_status", ""), "str"),
            (record.get("source_kind", ""), "str"),
            (record.get("route_mode", ""), "str"),
            (record.get("seed_id", ""), "str"),
            (record.get("seed_label", ""), "str"),
            (record.get("primary_subseed_id", ""), "str"),
            (record.get("primary_subseed_kind", ""), "str"),
            ("yes" if record.get("is_outlier") else "", "str"),
            (record.get("outlier_label", ""), "str"),
            (final_score, "num" if final_score != "" else "str"),
            (verdict, "str"),
            (None, "formula"),
            (None, "formula"),
            (None, "formula"),
        ]
        resume_path = str(record.get("resume_md", "") or "")
        pdf_path = str(record.get("resume_pdf", "") or "")
        apply_link = str(record.get("apply_link", "") or "")
        if resume_path:
            values[15] = (f'HYPERLINK("{_formula_literal(Path(resume_path).resolve().as_uri())}","{_formula_literal(resume_path)}")', "formula")
        if pdf_path:
            values[16] = (f'HYPERLINK("{_formula_literal(Path(pdf_path).resolve().as_uri())}","{_formula_literal(pdf_path)}")', "formula")
        if apply_link:
            values[17] = (f'HYPERLINK("{_formula_literal(apply_link)}","{_formula_literal(apply_link)}")', "formula")

        cells = []
        for col_idx, (value, value_type) in enumerate(values, start=1):
            cells.append(_cell(f"{_xlsx_col_name(col_idx)}{row_idx}", value, cell_type=value_type))
        rows_xml.append(f"<row r=\"{row_idx}\">{''.join(cells)}</row>")

    sheet_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
    {''.join(rows_xml)}
  </sheetData>
</worksheet>
'''

    workbook_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Jobs" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>
'''
    workbook_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>
'''
    root_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>
'''
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>
'''
    styles_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>
  <fills count="1"><fill><patternFill patternType="none"/></fill></fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>
'''

    workbook_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(workbook_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", root_rels)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)
        zf.writestr("xl/styles.xml", styles_xml)


def _write_markdown_index(records: Iterable[dict], markdown_path: Path) -> None:
    lines = [
        "# Resume Portfolio",
        "",
        "| company | publish_time | job_id | title | source_kind | route_mode | seed_id | subseed | outlier | score | resume_md | pdf | apply_link |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for record in records:
        review = record.get("review") or {}
        score = review.get("final_score") or review.get("weighted_score") or ""
        resume_md = str(record.get("resume_md", "") or "")
        resume_pdf = str(record.get("resume_pdf", "") or "")
        apply_link = str(record.get("apply_link", "") or "")
        lines.append(
            f"| {record.get('company_name', '')} | {record.get('publish_time', '')} | {record.get('job_id', '')} | "
            f"{record.get('title', '')} | {record.get('source_kind', '')} | {record.get('route_mode', '')} | "
            f"{record.get('seed_id', '')} | {record.get('primary_subseed_id', '')} | "
            f"{record.get('outlier_label', '')} | {score} | {resume_md} | {resume_pdf} | {apply_link} |"
        )
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def rebuild_portfolio_indexes(portfolio_root: str | Path | None = None) -> dict:
    root = normalize_portfolio_root(portfolio_root)
    root.mkdir(parents=True, exist_ok=True)
    lock_path = root / ".portfolio_rebuild.lock"
    with lock_path.open("w", encoding="utf-8") as lock_handle:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        try:
            ensure_profiles_json(root)
            records = collect_portfolio_records(root)
            _rebuild_by_date_views(root, records)
            _write_json(root / "portfolio_index.json", records)
            _write_markdown_index(records, root / "portfolio_index.md")
            _write_workbook(records, root / "resume_portfolio.xlsx")
            seed_catalog_summary = _write_seed_catalog(root, records)
            company_subseed_summary = _write_company_subseed_catalog(root, records)
            company_seed_summary = _write_company_seed_index(root)
            project_pool_summary = _write_project_pool_index(root)

            profiles_path = root / "profiles.json"
            profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
            profiles.update(
                {
                    "portfolio_root": str(root),
                    "by_company_root": str(root / "by_company"),
                    "by_date_root": str(root / "by_date"),
                    "seeds_root": str(root / "seeds"),
                    "portfolio_index": str(root / "portfolio_index.json"),
                    "portfolio_markdown": str(root / "portfolio_index.md"),
                    "resume_workbook": str(root / "resume_portfolio.xlsx"),
                    "seed_index_json": str(root / "seed_index.json"),
                    "seed_index_markdown": str(root / "seed_index.md"),
                    "company_seed_index_json": company_seed_summary["company_seed_index_json"],
                    "company_seed_index_markdown": company_seed_summary["company_seed_index_markdown"],
                    "company_subseed_index_json": company_subseed_summary["company_subseed_index_json"],
                    "company_subseed_index_markdown": company_subseed_summary["company_subseed_index_markdown"],
                    "subseeds_root": company_subseed_summary["subseeds_root"],
                    "experience_project_pool_json": project_pool_summary["project_pool_json"],
                    "experience_project_pool_markdown": project_pool_summary["project_pool_markdown"],
                    "updated_at": datetime.now().isoformat(timespec="seconds"),
                    "job_count": len(records),
                    "seed_count": seed_catalog_summary["seed_count"],
                }
            )
            _write_json(profiles_path, profiles)
            return {
                "portfolio_root": str(root),
                "record_count": len(records),
                "markdown": str(root / "portfolio_index.md"),
                "workbook": str(root / "resume_portfolio.xlsx"),
                "profiles": str(profiles_path),
                "seed_index_markdown": str(root / "seed_index.md"),
                "company_seed_index_markdown": company_seed_summary["company_seed_index_markdown"],
                "company_subseed_index_markdown": company_subseed_summary["company_subseed_index_markdown"],
            }
        finally:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
