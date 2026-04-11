"""
Build clean JD markdown text from a Google Sheet row.
"""
from __future__ import annotations

import re


def _split_field(text: str) -> list[str]:
    if not text:
        return []
    text = text.replace("•", ",").replace("\u2022", ",")
    parts = [part.strip(" -") for part in re.split(r",(?=\s*[A-Z0-9])|\n|;", text) if part.strip()]
    return parts


def row_to_jd_markdown(row: dict) -> str:
    title = row.get("job_title") or row.get("job_nlp_title") or "Job"
    company = row.get("company_name", "")
    location = row.get("job_location", "")
    seniority = row.get("job_seniority", "")
    work_model = row.get("work_model", "")
    employment_type = row.get("employment_type", "")
    summary = row.get("job_summary", "")

    lines = [f"# {title}", ""]
    metadata = [
        ("Company", company),
        ("Location", location),
        ("Seniority", seniority),
        ("Work Model", work_model),
        ("Employment Type", employment_type),
    ]
    for label, value in metadata:
        if value:
            lines.append(f"**{label}:** {value}")
    lines.append("")

    if summary:
        lines.append("## About the job")
        lines.append(summary.strip())
        lines.append("")

    core_skills = _split_field(str(row.get("core_skills", "")))
    if core_skills:
        lines.append("## Core Skills")
        for item in core_skills:
            lines.append(f"- {item}")
        lines.append("")

    required = _split_field(str(row.get("must_have_quals", "")))
    if required:
        lines.append("## Minimum qualifications")
        for item in required:
            lines.append(f"- {item}")
        lines.append("")

    preferred = _split_field(str(row.get("preferred_quals", "")))
    if preferred:
        lines.append("## Preferred qualifications")
        for item in preferred:
            lines.append(f"- {item}")
        lines.append("")

    responsibilities = _split_field(str(row.get("core_responsibilities", "")))
    if responsibilities:
        lines.append("## Responsibilities")
        for item in responsibilities:
            lines.append(f"- {item}")
        lines.append("")

    if row.get("apply_link"):
        lines.append(f"**Apply:** {row['apply_link']}")
    if row.get("original_url"):
        lines.append(f"**Source:** {row['original_url']}")

    return "\n".join(lines).strip() + "\n"
