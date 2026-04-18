"""Combined resume and JD skill extraction pipeline."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from repo_paths import resolve_repo_path

from .descriptions import business_group_definitions, describe_skill, skill_focus
from .taxonomy import CATEGORY_ORDER, CATEGORY_TO_SKILLS, SKILL_ALIASES, canonicalize_skill, categorize_skill, taxonomy_snapshot

RESUME_SKILLS_BLOCK_RE = re.compile(r"^## Skills\s*\n(.*?)(?=^## )", flags=re.M | re.S)

DETECTION_PHRASES = sorted(
    {skill for skills in CATEGORY_TO_SKILLS.values() for skill in skills}.union(SKILL_ALIASES.keys()),
    key=lambda item: (-len(item), item),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume-root", default="data/deliverables", help="Root directory containing resume.md files.")
    parser.add_argument(
        "--jd-scraped-path",
        default="data/job_tracker/jobs_catalog.json",
        help="Structured full JD catalog path. Flag name is kept for compatibility.",
    )
    parser.add_argument(
        "--portfolio-index-path",
        default="data/deliverables/resume_portfolio/portfolio_index.json",
        help="Portfolio index used by the job webapp catalog.",
    )
    parser.add_argument("--out", default="build_skills/output", help="Directory to write outputs into.")
    return parser.parse_args()


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text())


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def to_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def normalize_scalar_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).replace("\u00a0", " ").split())


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "unknown"


def make_occurrence(
    *,
    source_type: str,
    source_scope: str,
    organization: str,
    record_id: str,
    record_title: str,
    record_path: str,
    record_key: str,
    source_label: str,
    raw_skill: str,
) -> dict[str, object]:
    canonical_skill = canonicalize_skill(raw_skill)
    return {
        "source_type": source_type,
        "source_scope": source_scope,
        "organization": organization,
        "record_id": record_id,
        "record_title": record_title,
        "record_path": record_path,
        "record_key": record_key,
        "source_label": source_label,
        "raw_skill": raw_skill,
        "canonical_skill": canonical_skill,
        "recategorized_label": categorize_skill(canonical_skill),
    }


def parse_resume(path: Path) -> list[tuple[str, str]]:
    text = path.read_text()
    match = RESUME_SKILLS_BLOCK_RE.search(text)
    if not match:
        raise ValueError(f"Missing skills block: {path}")

    pairs: list[tuple[str, str]] = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if not stripped.startswith("* **") or ":** " not in stripped:
            raise ValueError(f"Unexpected skills line format in {path}: {stripped}")
        source_label, raw_skills = stripped[len("* **") :].split(":** ", 1)
        for raw_skill in (item.strip() for item in raw_skills.split(",")):
            if raw_skill:
                pairs.append((source_label.strip(), raw_skill))
    return pairs


def collect_resume_occurrences(resume_root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(resume_root.rglob("resume.md")):
        parts = path.parts
        company = parts[-4]
        resume_date = parts[-3]
        resume_id = parts[-2]
        relative_path = path.relative_to(resume_root.parent).as_posix()
        record_title = f"{company}::{resume_id}"
        for source_label, raw_skill in parse_resume(path):
            rows.append(
                make_occurrence(
                    source_type="resume",
                    source_scope="resume",
                    organization=company,
                    record_id=resume_id,
                    record_title=record_title,
                    record_path=relative_path,
                    record_key=relative_path,
                    source_label=source_label,
                    raw_skill=raw_skill,
                )
            )
    return rows


def build_phrase_patterns() -> list[tuple[str, re.Pattern[str]]]:
    compiled: list[tuple[str, re.Pattern[str]]] = []
    short_case_sensitive = {"C", "R", "Go"}
    for phrase in DETECTION_PHRASES:
        boundary_pattern = rf"(?<![A-Za-z0-9]){re.escape(phrase)}(?![A-Za-z0-9])"
        flags = 0 if phrase in short_case_sensitive else re.IGNORECASE
        compiled.append((phrase, re.compile(boundary_pattern, flags=flags)))
    return compiled


PHRASE_PATTERNS = build_phrase_patterns()


def detect_skills_in_text(text: str) -> list[tuple[str, str]]:
    matches: list[tuple[str, str]] = []
    seen: set[str] = set()
    exact = normalize_scalar_text(text)
    if exact:
        candidate = canonicalize_skill(exact)
        if any(candidate in skills for skills in CATEGORY_TO_SKILLS.values()):
            seen.add(candidate)
            matches.append((exact, candidate))

    for raw_phrase, pattern in PHRASE_PATTERNS:
        if pattern.search(text):
            canonical = canonicalize_skill(raw_phrase)
            if canonical in seen:
                continue
            seen.add(canonical)
            matches.append((raw_phrase, canonical))
    return matches


def normalize_fragments(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [normalize_scalar_text(item) for item in value if normalize_scalar_text(item)]
    text = str(value)
    parts = re.split(r"[\n,]+", text)
    return [normalize_scalar_text(part) for part in parts if normalize_scalar_text(part)]


def load_job_md(portfolio_row: dict[str, Any]) -> str:
    job_md = str(portfolio_row.get("job_md", "") or "").strip()
    if not job_md:
        return ""
    path = resolve_repo_path(job_md)
    if not path.exists():
        return ""
    return path.read_text()


def build_jd_catalog(scraped_path: Path, portfolio_index_path: Path) -> list[dict[str, Any]]:
    scraped_rows = read_json(scraped_path, [])
    portfolio_rows = read_json(portfolio_index_path, [])
    scraped_by_id = {
        str(row.get("job_id", "") or "").strip(): row
        for row in scraped_rows
        if isinstance(row, dict) and str(row.get("job_id", "") or "").strip()
    }
    portfolio_by_id = {
        str(row.get("job_id", "") or "").strip(): row
        for row in portfolio_rows
        if isinstance(row, dict) and str(row.get("job_id", "") or "").strip()
    }

    catalog: list[dict[str, Any]] = []
    for job_id in sorted(set(scraped_by_id) | set(portfolio_by_id)):
        scraped_row = scraped_by_id.get(job_id, {})
        portfolio_row = portfolio_by_id.get(job_id, {})
        if scraped_row and portfolio_row:
            source_scope = "both"
        elif scraped_row:
            source_scope = "scraped_current"
        else:
            source_scope = "portfolio_history"
        company = normalize_scalar_text(scraped_row.get("company_name") or portfolio_row.get("company_name") or portfolio_row.get("company_slug"))
        title = normalize_scalar_text(scraped_row.get("job_title") or scraped_row.get("job_nlp_title") or portfolio_row.get("title"))
        record_path = normalize_scalar_text(scraped_row.get("original_url") or scraped_row.get("apply_link") or portfolio_row.get("job_md"))
        catalog.append(
            {
                "job_id": job_id,
                "company_name": company,
                "job_title": title,
                "record_path": record_path,
                "source_scope": source_scope,
                "scraped_row": scraped_row,
                "portfolio_row": portfolio_row,
                "job_md_text": load_job_md(portfolio_row),
            }
        )
    return catalog


def collect_jd_occurrences_from_catalog(catalog: list[dict[str, Any]]) -> list[dict[str, object]]:
    occurrences: list[dict[str, object]] = []
    for job in catalog:
        per_field_seen: dict[str, set[str]] = defaultdict(set)
        scraped_row = job["scraped_row"]
        field_payloads = {
            "core_skills": normalize_fragments(scraped_row.get("core_skills")),
            "must_have_quals": normalize_fragments(scraped_row.get("must_have_quals")),
            "preferred_quals": normalize_fragments(scraped_row.get("preferred_quals")),
            "core_responsibilities": normalize_fragments(scraped_row.get("core_responsibilities")),
            "job_summary": [normalize_scalar_text(scraped_row.get("job_summary"))],
            "portfolio_job_md": [job["job_md_text"]],
        }
        for source_label, fragments in field_payloads.items():
            for fragment in fragments:
                if not fragment:
                    continue
                for raw_match, canonical_skill in detect_skills_in_text(fragment):
                    if canonical_skill in per_field_seen[source_label]:
                        continue
                    per_field_seen[source_label].add(canonical_skill)
                    occurrences.append(
                        {
                            "source_type": "jd",
                            "source_scope": job["source_scope"],
                            "organization": job["company_name"],
                            "record_id": job["job_id"],
                            "record_title": job["job_title"],
                            "record_path": job["record_path"],
                            "record_key": job["job_id"],
                            "source_label": source_label,
                            "raw_skill": raw_match,
                            "canonical_skill": canonical_skill,
                            "recategorized_label": categorize_skill(canonical_skill),
                        }
                    )
    return occurrences


def collect_jd_occurrences(scraped_path: Path, portfolio_index_path: Path) -> tuple[list[dict[str, object]], int]:
    catalog = build_jd_catalog(scraped_path, portfolio_index_path)
    return collect_jd_occurrences_from_catalog(catalog), len(catalog)


def aggregate_raw_skills(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for occurrence in occurrences:
        grouped[str(occurrence["raw_skill"])].append(occurrence)

    rows: list[dict[str, object]] = []
    for raw_skill, items in grouped.items():
        rows.append(
            {
                "raw_skill": raw_skill,
                "canonical_skill": items[0]["canonical_skill"],
                "total_mentions": len(items),
                "record_count": len({item["record_key"] for item in items}),
                "source_labels": ", ".join(sorted({str(item["source_label"]) for item in items})),
                "source_scopes": ", ".join(sorted({str(item["source_scope"]) for item in items})),
                "categories": ", ".join(sorted({str(item["recategorized_label"]) for item in items})),
            }
        )
    rows.sort(key=lambda row: (-int(row["total_mentions"]), str(row["raw_skill"])))
    return rows


def aggregate_canonical_skills(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for occurrence in occurrences:
        grouped[str(occurrence["canonical_skill"])].append(occurrence)

    rows: list[dict[str, object]] = []
    for canonical_skill, items in grouped.items():
        rows.append(
            {
                "canonical_skill": canonical_skill,
                "category": items[0]["recategorized_label"],
                "total_mentions": len(items),
                "record_count": len({item["record_key"] for item in items}),
                "raw_variants": ", ".join(sorted({str(item["raw_skill"]) for item in items})),
                "source_scopes": ", ".join(sorted({str(item["source_scope"]) for item in items})),
            }
        )
    rows.sort(
        key=lambda row: (
            CATEGORY_ORDER.index(str(row["category"])),
            -int(row["record_count"]),
            str(row["canonical_skill"]),
        )
    )
    return rows


def aggregate_categories(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for occurrence in occurrences:
        grouped[str(occurrence["recategorized_label"])].append(occurrence)
    rows: list[dict[str, object]] = []
    for category in CATEGORY_ORDER:
        items = grouped.get(category, [])
        if not items:
            continue
        rows.append(
            {
                "category": category,
                "total_mentions": len(items),
                "record_count": len({item["record_key"] for item in items}),
                "unique_skills": len({item["canonical_skill"] for item in items}),
            }
        )
    return rows


def aggregate_source_labels(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for occurrence in occurrences:
        grouped[str(occurrence["source_label"])].append(occurrence)
    rows: list[dict[str, object]] = []
    for source_label, items in grouped.items():
        rows.append(
            {
                "source_label": source_label,
                "mention_count": len(items),
                "record_count": len({item["record_key"] for item in items}),
                "canonical_skills": ", ".join(sorted({str(item["canonical_skill"]) for item in items})),
            }
        )
    rows.sort(key=lambda row: (-int(row["record_count"]), str(row["source_label"])))
    return rows


def build_source_summary(name: str, occurrences: list[dict[str, object]], catalog_record_count: int | None = None) -> dict[str, object]:
    canonical_rows = aggregate_canonical_skills(occurrences)
    return {
        "source": name,
        "catalog_record_count": catalog_record_count if catalog_record_count is not None else len({row["record_key"] for row in occurrences}),
        "record_count": len({row["record_key"] for row in occurrences}),
        "skill_mentions": len(occurrences),
        "unique_canonical_skills": len(canonical_rows),
        "unique_categories": len({row["category"] for row in canonical_rows}),
    }


def write_source_outputs(
    source_name: str,
    occurrences: list[dict[str, object]],
    out_dir: Path,
    catalog_record_count: int | None = None,
) -> dict[str, object]:
    source_dir = out_dir / source_name
    raw_rows = aggregate_raw_skills(occurrences)
    canonical_rows = aggregate_canonical_skills(occurrences)
    category_rows = aggregate_categories(occurrences)
    source_label_rows = aggregate_source_labels(occurrences)
    summary = build_source_summary(source_name, occurrences, catalog_record_count=catalog_record_count)

    write_csv(
        source_dir / "skill_occurrences.csv",
        occurrences,
        [
            "source_type",
            "source_scope",
            "organization",
            "record_id",
            "record_title",
            "record_path",
            "record_key",
            "source_label",
            "raw_skill",
            "canonical_skill",
            "recategorized_label",
        ],
    )
    write_csv(
        source_dir / "raw_skill_frequency.csv",
        raw_rows,
        ["raw_skill", "canonical_skill", "total_mentions", "record_count", "source_labels", "source_scopes", "categories"],
    )
    write_csv(
        source_dir / "canonical_skill_frequency.csv",
        canonical_rows,
        ["canonical_skill", "category", "total_mentions", "record_count", "raw_variants", "source_scopes"],
    )
    write_csv(
        source_dir / "category_summary.csv",
        category_rows,
        ["category", "total_mentions", "record_count", "unique_skills"],
    )
    write_csv(
        source_dir / "source_label_summary.csv",
        source_label_rows,
        ["source_label", "mention_count", "record_count", "canonical_skills"],
    )
    write_json(source_dir / "summary.json", summary)
    return {
        "summary": summary,
        "raw_rows": raw_rows,
        "canonical_rows": canonical_rows,
        "category_rows": category_rows,
        "source_label_rows": source_label_rows,
    }


def source_coverage_label(in_resume: bool, in_jd: bool) -> str:
    if in_resume and in_jd:
        return "resume+jd"
    if in_resume:
        return "resume_only"
    return "jd_only"


def merge_canonical_rows(
    resume_rows: list[dict[str, object]],
    jd_rows: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, set[str]]]:
    resume_map = {str(row["canonical_skill"]): row for row in resume_rows}
    jd_map = {str(row["canonical_skill"]): row for row in jd_rows}
    all_skills = sorted(set(resume_map) | set(jd_map))
    combined_rows: list[dict[str, object]] = []
    source_rows: list[dict[str, object]] = []
    skill_sources: dict[str, set[str]] = {}

    for skill in all_skills:
        resume_row = resume_map.get(skill)
        jd_row = jd_map.get(skill)
        category = str((resume_row or jd_row)["category"])
        in_resume = resume_row is not None
        in_jd = jd_row is not None
        sources = set()
        if in_resume:
            sources.add("resume")
        if in_jd:
            sources.add("jd")
        skill_sources[skill] = sources
        combined_rows.append(
            {
                "canonical_skill": skill,
                "category": category,
                "total_mentions": int((resume_row or {}).get("total_mentions", 0)) + int((jd_row or {}).get("total_mentions", 0)),
                "resume_record_count": int((resume_row or {}).get("record_count", 0)),
                "jd_record_count": int((jd_row or {}).get("record_count", 0)),
                "source_coverage": source_coverage_label(in_resume, in_jd),
                "raw_variants": ", ".join(
                    sorted(
                        {
                            variant
                            for row in (resume_row, jd_row)
                            if row
                            for variant in str(row.get("raw_variants", "")).split(", ")
                            if variant
                        }
                    )
                ),
            }
        )
        source_rows.append(
            {
                "canonical_skill": skill,
                "category": category,
                "in_resume": "yes" if in_resume else "no",
                "in_jd": "yes" if in_jd else "no",
                "source_coverage": source_coverage_label(in_resume, in_jd),
                "resume_record_count": int((resume_row or {}).get("record_count", 0)),
                "jd_record_count": int((jd_row or {}).get("record_count", 0)),
            }
        )

    combined_rows.sort(
        key=lambda row: (
            CATEGORY_ORDER.index(str(row["category"])),
            -int(row["resume_record_count"]) - int(row["jd_record_count"]),
            str(row["canonical_skill"]),
        )
    )
    source_rows.sort(key=lambda row: (-int(row["resume_record_count"]) - int(row["jd_record_count"]), str(row["canonical_skill"])))
    return combined_rows, source_rows, skill_sources


def build_combined_category_rows(combined_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in combined_rows:
        grouped[str(row["category"])].append(row)
    results: list[dict[str, object]] = []
    for category in CATEGORY_ORDER:
        items = grouped.get(category, [])
        if not items:
            continue
        results.append(
            {
                "category": category,
                "unique_skills": len(items),
                "resume_coverage": sum(1 for item in items if int(item["resume_record_count"]) > 0),
                "jd_coverage": sum(1 for item in items if int(item["jd_record_count"]) > 0),
                "combined_mentions": sum(int(item["total_mentions"]) for item in items),
            }
        )
    return results


def build_overview(resume_rows: list[dict[str, object]], jd_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    resume_skills = {str(row["canonical_skill"]) for row in resume_rows}
    jd_skills = {str(row["canonical_skill"]) for row in jd_rows}
    return [
        {"scope": "resume", "unique_skills": len(resume_skills)},
        {"scope": "jd", "unique_skills": len(jd_skills)},
        {"scope": "overlap", "unique_skills": len(resume_skills & jd_skills)},
        {"scope": "union", "unique_skills": len(resume_skills | jd_skills)},
        {"scope": "resume_only", "unique_skills": len(resume_skills - jd_skills)},
        {"scope": "jd_only", "unique_skills": len(jd_skills - resume_skills)},
    ]


def build_grouped_narratives(
    combined_rows: list[dict[str, object]], skill_sources: dict[str, set[str]]
) -> list[dict[str, object]]:
    available_skills = {str(row["canonical_skill"]) for row in combined_rows}
    grouped_rows: list[dict[str, object]] = []
    for group in business_group_definitions():
        skills = [skill for skill in group["skills"] if skill in available_skills]
        if len(skills) < 2:
            continue
        grouped_rows.append(
            {
                "group_label": group["group_label"],
                "category": group["category"],
                "merged_skills_text": "、".join(skills),
                "common_introduction": group["common_introduction"],
                "common_business_scenario": group["common_business_scenario"],
                "skill_focuses": [
                    {
                        "skill": skill,
                        "focus": skill_focus(skill),
                        "source_coverage": source_coverage_label("resume" in skill_sources.get(skill, set()), "jd" in skill_sources.get(skill, set())),
                    }
                    for skill in skills
                ],
            }
        )
    grouped_rows.sort(key=lambda row: (-len(row["skill_focuses"]), str(row["group_label"])))
    return grouped_rows


def load_non_tech_frequency_payload(non_tech_out_dir: Path) -> dict[str, object]:
    summary = read_json(non_tech_out_dir / "summary.json", {})
    combined_rows = read_csv_rows(non_tech_out_dir / "phrase_frequency_combined.csv")
    generalized_rows = read_csv_rows(non_tech_out_dir / "generalized_tech_terms.csv")
    business_rows = read_csv_rows(non_tech_out_dir / "business_domains.csv")
    soft_skill_rows = read_csv_rows(non_tech_out_dir / "soft_skills.csv")
    merged_narratives = read_json(non_tech_out_dir / "merged_narratives.json", {}).get("groups", [])
    if not summary or not combined_rows:
        return {}
    bucket_summaries = summary.get("bucket_summaries", {})
    return {
        "summary": summary,
        "combined_rows": combined_rows,
        "merged_narratives": merged_narratives,
        "bucket_tables": [
            {
                "slug": "combined",
                "title": "非技术栈岗位要求总表",
                "rows": combined_rows,
            },
            {
                "slug": "generalized-tech",
                "title": "泛化技术称呼",
                "rows": generalized_rows,
            },
            {
                "slug": "business-domain",
                "title": "业务 Domain",
                "rows": business_rows,
            },
            {
                "slug": "soft-skill",
                "title": "软技能",
                "rows": soft_skill_rows,
            },
        ],
        "summary_node": {
            "catalog_record_count": int(summary.get("catalog_record_count", 0)),
            "accepted_rows": int(summary.get("accepted_rows", 0)),
            "final_title_count": int(summary.get("final_title_count", 0)),
            "bucket_title_counts": {
                bucket: int(payload.get("title_count", 0))
                for bucket, payload in bucket_summaries.items()
                if isinstance(payload, dict)
            },
        },
    }


def html_table(
    table_id: str,
    headers: list[str],
    rows: list[list[str]],
    column_widths: list[str] | None = None,
    page_size: int = 15,
) -> str:
    colgroup = ""
    if column_widths:
        colgroup = "<colgroup>" + "".join(f"<col style=\"width:{width}\">" for width in column_widths) + "</colgroup>"
    header_html = "".join(f"<th class=\"resizable\">{escape(header)}<span class=\"resize-handle\"></span></th>" for header in headers)
    body_html = []
    for row in rows:
        body_html.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")
    pager_html = ""
    if len(rows) > page_size:
        pager_html = (
            f"<div class=\"table-pager\" aria-label=\"{escape(table_id)} pagination\">"
            f"<button type=\"button\" class=\"pager-arrow pager-prev\" aria-label=\"上一页\">←</button>"
            f"<span class=\"pager-status\">1 / 1</span>"
            f"<button type=\"button\" class=\"pager-arrow pager-next\" aria-label=\"下一页\">→</button>"
            f"</div>"
        )
    return (
        f"<div class=\"table-shell\" data-page-size=\"{page_size}\">"
        f"<div class=\"table-viewport\">"
        f"<table id=\"{table_id}\" class=\"report-table\">{colgroup}<thead><tr>{header_html}</tr></thead><tbody>{''.join(body_html)}</tbody></table>"
        f"</div>"
        f"{pager_html}"
        f"</div>"
    )


def build_html_report(
    *,
    generated_at: str,
    resume_summary: dict[str, object],
    jd_summary: dict[str, object],
    overview_rows: list[dict[str, object]],
    combined_category_rows: list[dict[str, object]],
    combined_rows: list[dict[str, object]],
    source_coverage_rows: list[dict[str, object]],
    grouped_narratives: list[dict[str, object]],
    jd_non_tech_payload: dict[str, object],
    out_dir: Path,
) -> str:
    category_to_skills: dict[str, list[str]] = defaultdict(list)
    for row in combined_rows:
        category_to_skills[str(row["category"])].append(str(row["canonical_skill"]))

    category_blocks = []
    for category in CATEGORY_ORDER:
        skills = category_to_skills.get(category)
        if not skills:
            continue
        category_blocks.append(
            f"<section class=\"mini-card\"><h3>{escape(category)}</h3><p>{escape(', '.join(skills))}</p></section>"
        )

    merged_rows_html = [
        [
            escape(str(row["merged_skills_text"])),
            f"<div><strong>业务域：</strong>{escape(str(row['group_label']))}</div>"
            f"<div class=\"scenario\"><strong>共同介绍：</strong>{escape(str(row['common_introduction']))}</div>"
            f"<div class=\"scenario\"><strong>业务场景：</strong>{escape(str(row['common_business_scenario']))}</div>",
            "<div class=\"focus-list\">"
            + "".join(
                f"<div><strong>{escape(item['skill'])}</strong> <span class=\"source-tag\">[{escape(item['source_coverage'])}]</span>：{escape(item['focus'])}</div>"
                for item in row["skill_focuses"]
            )
            + "</div>",
        ]
        for row in grouped_narratives
    ]
    non_tech_merged_rows_html = []

    non_tech_section = ""
    if jd_non_tech_payload:
        non_tech_summary = jd_non_tech_payload["summary"]
        bucket_title_counts = jd_non_tech_payload["summary_node"]["bucket_title_counts"]
        noise_samples = "、".join(
            f"{escape(str(row['phrase']))}({escape(str(row['count']))})"
            for row in non_tech_summary.get("filtered_noise_samples", [])[:5]
        ) or "无"
        non_tech_tables_html = []
        for table in jd_non_tech_payload["bucket_tables"]:
            sorted_table_rows = sorted(
                table["rows"],
                key=lambda row: (-to_int(row.get("frequency", 0)), str(row.get("title", ""))),
            )
            rows = [
                [
                    escape(str(row["title"])),
                    escape(str(row["semantic_variants"])),
                    escape(str(row["frequency"])),
                ]
                for row in sorted_table_rows
            ]
            if not rows:
                continue
            non_tech_tables_html.append(
                f"""
                <div class="panel">
                  <h3>{escape(str(table["title"]))}</h3>
                  {html_table(
                      f"non-tech-{table['slug']}",
                      ["Title", "被合并的语义变体", "词频"],
                      rows,
                      ["18%", "64%", "18%"],
                  )}
                </div>
                """
            )
        merged_groups = sorted(
            jd_non_tech_payload.get("merged_narratives", []),
            key=lambda row: (-to_int(row.get("title_count", 0)), str(row.get("group_label", ""))),
        )
        non_tech_merged_rows_html = [
            [
                escape(str(row["group_label"])),
                escape(str(row["merged_titles_text"])),
                f"<div><strong>共同介绍：</strong>{escape(str(row['common_introduction']))}</div>"
                f"<div class=\"scenario\"><strong>业务场景：</strong>{escape(str(row['common_business_scenario']))}</div>",
                "<div class=\"focus-list\">"
                + "".join(
                    f"<div><strong>{escape(str(item['title']))}</strong>：{escape(str(item['focus']))}</div>"
                    for item in row.get("title_focuses", [])
                )
                + "</div>",
            ]
            for row in merged_groups
        ]
        non_tech_section = f"""
        <div class="panel">
          <h2>非技术栈岗位要求词频分析</h2>
          <p class="tagline">本节只统计 3999 份 JD 中 requirements / qualifications / responsibilities 等要求相关位置里的非技术栈短语。词频按出现该标题的不同 JD 数量统计；已被 skills 看板覆盖的具体技术栈不会在此重复展示。</p>
          <div class="meta">
            <div class="meta-card"><strong>JD Catalog Records</strong>{escape(str(non_tech_summary['catalog_record_count']))}</div>
            <div class="meta-card"><strong>Accepted Phrase Rows</strong>{escape(str(non_tech_summary['accepted_rows']))}</div>
            <div class="meta-card"><strong>Final Titles</strong>{escape(str(non_tech_summary['final_title_count']))}</div>
            <div class="meta-card"><strong>泛化技术称呼</strong>{escape(str(bucket_title_counts.get('generalized_tech', 0)))}</div>
            <div class="meta-card"><strong>业务 Domain</strong>{escape(str(bucket_title_counts.get('business_domain', 0)))}</div>
            <div class="meta-card"><strong>软技能</strong>{escape(str(bucket_title_counts.get('soft_skill', 0)))}</div>
          </div>
          <p class="tagline">已过滤噪声样例：{noise_samples}</p>
        </div>
        {''.join(non_tech_tables_html)}
        """

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Skills Coverage Report</title>
  <style>
    :root {{
      --bg: #f5f2eb;
      --panel: #fffdf8;
      --ink: #1f1d18;
      --muted: #675f52;
      --line: #d7cebf;
      --accent: #0f5bd8;
      --soft: #eef3ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
      background:
        radial-gradient(circle at top right, rgba(15, 91, 216, 0.10), transparent 28%),
        linear-gradient(180deg, #f7f4ed 0%, #f1ece2 100%);
      line-height: 1.55;
    }}
    .page {{ max-width: 1320px; margin: 0 auto; padding: 36px 22px 80px; }}
    .hero, .panel, .mini-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: 0 12px 36px rgba(52, 44, 25, 0.06);
    }}
    .hero {{ padding: 28px 30px; margin-bottom: 24px; }}
    .panel {{ padding: 20px 22px; margin-bottom: 18px; }}
    .mini-card {{ padding: 16px 18px; }}
    h1 {{ margin: 0 0 10px; font-size: 38px; letter-spacing: -0.03em; }}
    h2 {{ margin: 0 0 14px; font-size: 24px; }}
    h3 {{ margin: 0 0 8px; font-size: 18px; }}
    .tagline {{ color: var(--muted); max-width: 860px; }}
    .meta {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-top: 18px; }}
    .meta-card {{ background: #faf7f0; border: 1px solid var(--line); border-radius: 14px; padding: 12px 14px; }}
    .meta-card strong {{ display: block; font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin-bottom: 4px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; }}
    .table-shell {{ width: 100%; }}
    .table-viewport {{ width: 100%; overflow: hidden; transition: height 0.18s ease; }}
    .report-table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
    .report-table th, .report-table td {{ border: 1px solid var(--line); padding: 12px 14px; text-align: left; vertical-align: top; }}
    .report-table th {{ background: #f1ecdf; font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; position: relative; user-select: none; }}
    .report-table td {{ font-size: 15px; overflow-wrap: anywhere; }}
    .table-pager {{
      display: flex; align-items: center; justify-content: flex-end; gap: 12px;
      padding-top: 12px; min-height: 44px;
    }}
    .pager-arrow {{
      width: 36px; height: 36px; border-radius: 999px; border: 1px solid var(--line);
      background: #faf7f0; color: var(--ink); font-size: 20px; line-height: 1;
      cursor: pointer;
    }}
    .pager-arrow:disabled {{
      opacity: 0.4; cursor: not-allowed;
    }}
    .pager-status {{
      min-width: 78px; text-align: center; color: var(--muted); font-size: 13px; letter-spacing: 0.04em;
    }}
    .source-tag {{ color: var(--accent); font-size: 12px; }}
    .focus-list div + div {{ margin-top: 7px; }}
    .scenario {{ margin-top: 8px; }}
    .resize-handle {{
      position: absolute; top: 0; right: -3px; width: 8px; height: 100%;
      cursor: col-resize; user-select: none;
    }}
    @media (max-width: 720px) {{
      .page {{ padding: 18px 12px 42px; }}
      .hero, .panel {{ padding: 16px; }}
      h1 {{ font-size: 30px; }}
      .report-table th, .report-table td {{ padding: 10px; font-size: 14px; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <div class="hero">
      <h1>Skills Coverage Report</h1>
      <p class="tagline">本报告同时覆盖 resume 技术栈、JD 技术栈以及二者并集。JD 侧按照 web app 的真实岗位池口径构建：`jobs_catalog.json` 全量岗位为主体，`portfolio_index.json` 和 `job.md` 只用于补充历史 artifact 上下文。</p>
      <div class="meta">
        <div class="meta-card"><strong>Generated At</strong>{escape(generated_at)}</div>
        <div class="meta-card"><strong>Resume Records</strong>{escape(str(resume_summary['record_count']))}</div>
        <div class="meta-card"><strong>JD Catalog Records</strong>{escape(str(jd_summary['catalog_record_count']))}</div>
        <div class="meta-card"><strong>JD Records With Skills</strong>{escape(str(jd_summary['record_count']))}</div>
        <div class="meta-card"><strong>Combined Skill Union</strong>{escape(str(next(row['unique_skills'] for row in overview_rows if row['scope'] == 'union')))}</div>
        <div class="meta-card"><strong>Output Root</strong>{escape(out_dir.as_posix())}</div>
      </div>
    </div>

    <div class="panel">
      <h2>来源覆盖概览</h2>
      {html_table(
          "source-overview",
          ["Scope", "Unique Skills"],
          [
              [escape(str(row["scope"])), escape(str(row["unique_skills"]))]
              for row in sorted(overview_rows, key=lambda row: (-to_int(row["unique_skills"]), str(row["scope"])))
          ],
          ["60%", "40%"],
      )}
    </div>

    <div class="panel">
      <h2>分类覆盖概览（Resume + JD 并集）</h2>
      {html_table(
          "category-overview",
          ["Category", "Unique Skills", "Resume Coverage", "JD Coverage", "Combined Mentions"],
          [
              [
                  escape(str(row["category"])),
                  escape(str(row["unique_skills"])),
                  escape(str(row["resume_coverage"])),
                  escape(str(row["jd_coverage"])),
                  escape(str(row["combined_mentions"])),
              ]
              for row in sorted(
                  combined_category_rows,
                  key=lambda row: (-to_int(row["combined_mentions"]), str(row["category"])),
              )
          ],
          ["28%", "14%", "14%", "14%", "30%"],
      )}
    </div>

    <div class="panel">
      <h2>技术栈来源覆盖明细</h2>
      {html_table(
          "source-coverage",
          ["Skill", "Category", "Coverage", "Resume Records", "JD Records"],
          [
              [
                  escape(str(row["canonical_skill"])),
                  escape(str(row["category"])),
                  escape(str(row["source_coverage"])),
                  escape(str(row["resume_record_count"])),
                  escape(str(row["jd_record_count"])),
              ]
              for row in sorted(
                  source_coverage_rows,
                  key=lambda row: (
                      -to_int(row["jd_record_count"]),
                      -to_int(row["resume_record_count"]),
                      str(row["canonical_skill"]),
                  ),
              )
          ],
          ["28%", "22%", "16%", "17%", "17%"],
      )}
    </div>

    <div class="panel">
      <h2>Top Combined Canonical Skills</h2>
      {html_table(
          "top-combined",
          ["Skill", "Category", "Coverage", "Resume Records", "JD Records"],
          [
              [
                  escape(str(row["canonical_skill"])),
                  escape(str(row["category"])),
                  escape(str(row["source_coverage"])),
                  escape(str(row["resume_record_count"])),
                  escape(str(row["jd_record_count"])),
              ]
              for row in sorted(
                  combined_rows,
                  key=lambda item: (
                      -to_int(item["jd_record_count"]),
                      -to_int(item["resume_record_count"]),
                      str(item["canonical_skill"]),
                  ),
              )[:60]
          ],
          ["28%", "22%", "16%", "17%", "17%"],
      )}
    </div>
    {non_tech_section}

    <div class="panel">
      <h2>Canonical Skills By Category</h2>
      <div class="grid">
        {''.join(category_blocks)}
      </div>
    </div>

    <div class="panel">
      <h2>技术栈介绍与日常业务场景（合并版）</h2>
      <p class="tagline">同一技术栈允许出现在多个业务主题组中。表格默认给第三列更宽的空间，同时支持拖动表头右侧分隔条手动调整列宽。</p>
      {html_table(
          "merged-narratives-table",
          ["被合并的技术栈", "共同介绍和业务场景", "各自特性或侧重点"],
          merged_rows_html,
          ["20%", "28%", "52%"],
      )}
    </div>

    <div class="panel">
      <h2>非技术栈介绍与日常业务场景（合并版）</h2>
      <p class="tagline">这部分基于 JD 非技术栈词频板的 {escape(str(jd_non_tech_payload.get("summary_node", {}).get("final_title_count", 0)))} 个 title 重新合并成业务主题组。当前分组数不足 15，所以默认整页展示，不显示翻页按钮。</p>
      {html_table(
          "non-tech-merged-narratives-table",
          ["业务主题组", "被合并的非技术栈", "共同介绍和业务场景", "各自特性或侧重点"],
          non_tech_merged_rows_html,
          ["10%", "18%", "18%", "54%"],
      )}
    </div>
  </div>
  <script>
    (function () {{
      const syncViewport = (shell) => {{
        const viewport = shell.querySelector(".table-viewport");
        const table = shell.querySelector("table.report-table");
        if (!viewport || !table) return;
        const measuredHeight = Math.ceil(table.getBoundingClientRect().height);
        const cachedHeight = Number(shell.dataset.viewportHeight || "0");
        const nextHeight = Math.max(cachedHeight, measuredHeight);
        shell.dataset.viewportHeight = String(nextHeight);
        viewport.style.height = nextHeight + "px";
      }};

      const renderPage = (shell, requestedPage) => {{
        const rows = Array.from(shell.querySelectorAll("tbody tr"));
        const pageSize = Number(shell.dataset.pageSize || "30");
        const totalPages = Math.max(1, Math.ceil(rows.length / pageSize));
        const page = Math.min(totalPages, Math.max(1, requestedPage));
        const start = (page - 1) * pageSize;
        const end = start + pageSize;
        rows.forEach((row, index) => {{
          row.style.display = index >= start && index < end ? "" : "none";
        }});
        shell.dataset.currentPage = String(page);
        const prev = shell.querySelector(".pager-prev");
        const next = shell.querySelector(".pager-next");
        const status = shell.querySelector(".pager-status");
        if (prev) prev.disabled = page <= 1;
        if (next) next.disabled = page >= totalPages;
        if (status) status.textContent = `${{page}} / ${{totalPages}}`;
        window.requestAnimationFrame(() => syncViewport(shell));
      }};

      document.querySelectorAll(".table-shell").forEach((shell) => {{
        const prev = shell.querySelector(".pager-prev");
        const next = shell.querySelector(".pager-next");
        if (prev && prev.dataset.bound !== "1") {{
          prev.dataset.bound = "1";
          prev.addEventListener("click", () => {{
            renderPage(shell, Number(shell.dataset.currentPage || "1") - 1);
          }});
        }}
        if (next && next.dataset.bound !== "1") {{
          next.dataset.bound = "1";
          next.addEventListener("click", () => {{
            renderPage(shell, Number(shell.dataset.currentPage || "1") + 1);
          }});
        }}
        renderPage(shell, 1);
      }});

      document.querySelectorAll("table.report-table").forEach((table) => {{
        const cols = table.querySelectorAll("colgroup col");
        if (!cols.length) return;
        const headers = table.querySelectorAll("th");
        headers.forEach((header, index) => {{
          const handle = header.querySelector(".resize-handle");
          if (!handle || !cols[index] || handle.dataset.bound === "1") return;
          handle.dataset.bound = "1";
          handle.addEventListener("mousedown", (event) => {{
            event.preventDefault();
            const startX = event.clientX;
            const startWidth = cols[index].getBoundingClientRect().width;
            const onMove = (moveEvent) => {{
              const nextWidth = Math.max(120, startWidth + moveEvent.clientX - startX);
              cols[index].style.width = nextWidth + "px";
            }};
            const onUp = () => {{
              document.removeEventListener("mousemove", onMove);
              document.removeEventListener("mouseup", onUp);
              const shell = table.closest(".table-shell");
              if (shell) window.requestAnimationFrame(() => syncViewport(shell));
            }};
            document.addEventListener("mousemove", onMove);
            document.addEventListener("mouseup", onUp);
          }});
        }});
      }});
      window.addEventListener("resize", () => {{
        document.querySelectorAll(".table-shell").forEach((shell) => {{
          window.requestAnimationFrame(() => syncViewport(shell));
        }});
      }});
    }})();
  </script>
</body>
</html>
"""


def run_resume_only(resume_root: Path, out_dir: Path) -> dict[str, object]:
    occurrences = collect_resume_occurrences(resume_root)
    return write_source_outputs("resume", occurrences, out_dir, catalog_record_count=len({row["record_key"] for row in occurrences}))


def run_jd_only(scraped_path: Path, portfolio_index_path: Path, out_dir: Path) -> dict[str, object]:
    occurrences, catalog_record_count = collect_jd_occurrences(scraped_path, portfolio_index_path)
    return write_source_outputs("jd", occurrences, out_dir, catalog_record_count=catalog_record_count)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    jd_non_tech_payload = load_non_tech_frequency_payload(Path("build_skills/词频分析/output"))

    resume_payload = run_resume_only(Path(args.resume_root), out_dir)
    jd_payload = run_jd_only(Path(args.jd_scraped_path), Path(args.portfolio_index_path), out_dir)
    combined_rows, source_coverage_rows, skill_sources = merge_canonical_rows(
        resume_payload["canonical_rows"],
        jd_payload["canonical_rows"],
    )
    overview_rows = build_overview(resume_payload["canonical_rows"], jd_payload["canonical_rows"])
    combined_category_rows = build_combined_category_rows(combined_rows)
    grouped_narratives = build_grouped_narratives(combined_rows, skill_sources)
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    write_csv(
        out_dir / "combined_canonical_skill_frequency.csv",
        combined_rows,
        [
            "canonical_skill",
            "category",
            "total_mentions",
            "resume_record_count",
            "jd_record_count",
            "source_coverage",
            "raw_variants",
        ],
    )
    write_csv(
        out_dir / "skill_source_coverage.csv",
        source_coverage_rows,
        [
            "canonical_skill",
            "category",
            "in_resume",
            "in_jd",
            "source_coverage",
            "resume_record_count",
            "jd_record_count",
        ],
    )
    write_csv(
        out_dir / "merged_skill_narratives.csv",
        [
            {
                "group_label": row["group_label"],
                "category": row["category"],
                "merged_skills_text": row["merged_skills_text"],
                "common_introduction": row["common_introduction"],
                "common_business_scenario": row["common_business_scenario"],
                "skill_focuses_text": "；".join(
                    f"{item['skill']}[{item['source_coverage']}]：{item['focus']}" for item in row["skill_focuses"]
                ),
            }
            for row in grouped_narratives
        ],
        [
            "group_label",
            "category",
            "merged_skills_text",
            "common_introduction",
            "common_business_scenario",
            "skill_focuses_text",
        ],
    )
    write_json(out_dir / "merged_skill_narratives.json", grouped_narratives)

    summary = {
        "generated_at_utc": generated_at,
        "resume_summary": resume_payload["summary"],
        "jd_summary": jd_payload["summary"],
        "combined_overview": overview_rows,
    }
    if jd_non_tech_payload:
        summary["jd_non_tech_frequency_summary"] = jd_non_tech_payload["summary_node"]
    write_json(out_dir / "summary.json", summary)
    write_json(out_dir / "taxonomy_snapshot.json", taxonomy_snapshot())
    (out_dir / "REPORT.html").write_text(
        build_html_report(
            generated_at=generated_at,
            resume_summary=resume_payload["summary"],
            jd_summary=jd_payload["summary"],
            overview_rows=overview_rows,
            combined_category_rows=combined_category_rows,
            combined_rows=combined_rows,
            source_coverage_rows=source_coverage_rows,
            grouped_narratives=grouped_narratives,
            jd_non_tech_payload=jd_non_tech_payload,
            out_dir=out_dir,
        )
    )
    report_md = out_dir / "REPORT.md"
    if report_md.exists():
        report_md.unlink()
    return 0
