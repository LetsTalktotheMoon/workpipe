"""
Adapt resume_pipeline markdown into the fixed markdown structure expected by
the local PDF compiler.
"""
from __future__ import annotations

import os
from typing import Iterable

from models.resume import Resume


DEFAULT_NAME = os.environ.get("RESUME_PROFILE_NAME", "").strip()
DEFAULT_PHONE = os.environ.get("RESUME_PROFILE_PHONE", "").strip()
DEFAULT_EMAIL = os.environ.get("RESUME_PROFILE_EMAIL", "").strip()


def _header_lines(
    name: str | None = None,
    phone: str | None = None,
    email: str | None = None,
) -> list[str]:
    lines: list[str] = []
    final_name = name or DEFAULT_NAME
    final_phone = phone or DEFAULT_PHONE
    final_email = email or DEFAULT_EMAIL

    if final_name:
        lines.append(f"# {final_name}")
    contact_parts = [part for part in (final_phone, final_email) if part]
    if contact_parts:
        lines.append(" | ".join(contact_parts))
    if lines:
        lines.append("")
    return lines


def resume_to_pdf_markdown(
    resume: Resume,
    name: str | None = None,
    phone: str | None = None,
    email: str | None = None,
) -> str:
    lines: list[str] = []
    lines.extend(_header_lines(name=name, phone=phone, email=email))

    lines.append("## Professional Summary")
    for bullet in resume.summary:
        lines.append(f"* {bullet}")
    lines.append("")

    lines.append("## Skills")
    for category in resume.skills:
        lines.append(f"* **{category.name}:** {', '.join(category.skills)}")
    lines.append("")

    lines.append("## Work Experience")
    for exp in resume.experiences:
        company_team = f"{exp.company} · {exp.department}" if exp.department else exp.company
        heading = f"### {exp.title} | {company_team}"
        if exp.location:
            heading += f" | {exp.location}"
        lines.append(heading)
        if exp.dates:
            lines.append(f"**{exp.dates}**")
        if exp.cross_functional_note:
            lines.append(f"> {exp.cross_functional_note}")
        for bullet in exp.bullets:
            lines.append(f"* {bullet.text}")
        if exp.project:
            lines.append(f"**_Project: {exp.project.title}_**")
            if exp.project.baseline:
                lines.append(f"> {exp.project.baseline}")
            for bullet in exp.project.bullets:
                lines.append(f"* {bullet.text}")
        lines.append("")

    lines.append("## Education")
    lines.append("| Degree | Institution | Period |")
    lines.append("| --- | --- | --- |")
    for edu in resume.education:
        degree = edu.degree if not edu.track else f"{edu.degree} ({edu.track})"
        lines.append(f"| {degree} | {edu.school} | {edu.dates} |")
    lines.append("")

    if resume.achievement:
        lines.append("## Achievements")
        lines.append(f"* {resume.achievement}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"
