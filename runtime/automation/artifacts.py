"""
Artifact helpers for seed manifests and local PDF generation.
"""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Sequence

from repo_paths import repo_relative_path

from pdf_compiler.markdown_adapter import resume_to_pdf_markdown
from automation.seed_registry import SeedEntry
from models.resume import Resume

PDF_COMPILER_ROOT = Path(__file__).resolve().parents[1] / "pdf_compiler"

CORE_REQUIRED_SECTIONS: tuple[str, ...] = (
    "Professional Summary",
    "Skills",
    "Work Experience",
    "Education",
)
PROMOTED_REQUIRED_SECTIONS: tuple[str, ...] = CORE_REQUIRED_SECTIONS + (
    "Achievements",
)
SECTION_TO_PARSER_ATTR = {
    "Professional Summary": "summary_bullets",
    "Skills": "skills",
    "Work Experience": "work_experience",
    "Education": "education",
    "Achievements": "additional",
    "Additional Information": "additional",
}


def _load_md_to_tex():
    module_path = PDF_COMPILER_ROOT / "md_to_tex.py"
    spec = importlib.util.spec_from_file_location("resume_pdf_md_to_tex", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compile_markdown_to_pdf(
    md_path: Path,
    output_dir: Path,
    required_sections: Sequence[str] = CORE_REQUIRED_SECTIONS,
    name: str | None = None,
    phone: str | None = None,
    email: str | None = None,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    tex_dir = output_dir / "tex"
    pdf_dir = output_dir / "pdf"
    tex_dir.mkdir(parents=True, exist_ok=True)
    pdf_dir.mkdir(parents=True, exist_ok=True)

    md_to_tex = _load_md_to_tex()
    compile_input = _prepare_pdf_compile_input(
        md_path, output_dir, required_sections, md_to_tex, name=name, phone=phone, email=email
    )
    tex_path = Path(md_to_tex.convert_file(str(compile_input), str(tex_dir), level=0))
    _postprocess_pdf_tex(tex_path)
    missing_tex_sections = _missing_sections_in_tex(tex_path, required_sections)
    if missing_tex_sections:
        raise RuntimeError(
            f"{md_path.name} generated incomplete TeX output; missing sections: "
            f"{', '.join(missing_tex_sections)}"
        )
    cmd = [
        "xelatex",
        "-interaction=nonstopmode",
        "-output-directory",
        str(pdf_dir),
        str(tex_path),
    ]
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=120,
        check=False,
    )
    pdf_path = pdf_dir / tex_path.with_suffix(".pdf").name
    if not pdf_path.exists():
        raise RuntimeError(
            f"xelatex failed for {md_path.name}: {result.stderr[-500:] or result.stdout[-500:]}"
        )
    missing_pdf_sections = _missing_sections_in_pdf(pdf_path, required_sections)
    if missing_pdf_sections:
        raise RuntimeError(
            f"{md_path.name} generated incomplete PDF output; missing sections: "
            f"{', '.join(missing_pdf_sections)}"
        )
    final_pdf_path = pdf_dir / "resume.pdf"
    if pdf_path != final_pdf_path:
        shutil.copyfile(pdf_path, final_pdf_path)
        return final_pdf_path
    return pdf_path


def _prepare_pdf_compile_input(
    md_path: Path,
    output_dir: Path,
    required_sections: Sequence[str],
    md_to_tex,
    name: str | None = None,
    phone: str | None = None,
    email: str | None = None,
) -> Path:
    text = md_path.read_text(encoding="utf-8")
    normalized_text = _normalize_pdf_heading_aliases(text)
    existing_name, existing_phone, existing_email = _extract_existing_pdf_header_fields(
        normalized_text,
        md_to_tex,
    )
    final_name = name or existing_name
    final_phone = phone or existing_phone
    final_email = email or existing_email

    try:
        resume = Resume.from_markdown(_normalize_resume_parser_headings(normalized_text))
    except Exception as exc:
        raise RuntimeError(f"Unable to normalize {md_path.name} for PDF compilation: {exc}") from exc

    adapted = resume_to_pdf_markdown(
        resume,
        name=final_name,
        phone=final_phone,
        email=final_email,
    )
    missing_sections = _missing_sections_in_pdf_markdown(
        adapted,
        required_sections,
        md_to_tex,
    )
    if missing_sections:
        raise RuntimeError(
            f"{md_path.name} could not be normalized into a complete PDF source markdown; "
            f"missing sections after adaptation: {', '.join(missing_sections)}"
        )
    adapted_name, _, _ = _extract_existing_pdf_header_fields(adapted, md_to_tex)
    if not adapted_name:
        raise RuntimeError(
            f"{md_path.name} could not be normalized into a PDF source markdown with a header; "
            "candidate name is missing."
        )
    adapted_path = output_dir / "resume_pdf_input.md"
    adapted_path.write_text(adapted, encoding="utf-8")
    return adapted_path


def publish_seed_artifact(seed: SeedEntry, output_root: Path, generate_pdf: bool = False) -> dict:
    seed_dir = output_root / "seeds" / seed.seed_id
    seed_dir.mkdir(parents=True, exist_ok=True)
    md_target = seed_dir / "resume.md"
    shutil.copyfile(seed.source_md, md_target)

    pdf_target = None
    if generate_pdf:
        required_sections = (
            PROMOTED_REQUIRED_SECTIONS
            if seed.source_type == "promoted"
            else CORE_REQUIRED_SECTIONS
        )
        pdf_target = compile_markdown_to_pdf(
            md_target,
            seed_dir,
            required_sections=required_sections,
        )

    manifest = {
        **seed.to_dict(),
        "artifact_dir": repo_relative_path(seed_dir),
        "resume_md": repo_relative_path(md_target),
        "resume_pdf": repo_relative_path(pdf_target) if pdf_target else "",
    }
    (seed_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return manifest


def _normalize_pdf_heading_aliases(text: str) -> str:
    replacements = {
        "## Experience": "## Work Experience",
        "## Achievement": "## Achievements",
        "## Additional Information": "## Achievements",
    }
    return _replace_heading_aliases(text, replacements)


def _normalize_resume_parser_headings(text: str) -> str:
    replacements = {
        "## Work Experience": "## Experience",
        "## Additional Information": "## Achievements",
    }
    return _replace_heading_aliases(text, replacements)


def _replace_heading_aliases(text: str, replacements: dict[str, str]) -> str:
    lines = text.splitlines()
    normalized_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        normalized_lines.append(replacements.get(stripped, line))
    normalized = "\n".join(normalized_lines)
    if text.endswith("\n"):
        normalized += "\n"
    return normalized


def _missing_sections_in_pdf_markdown(
    text: str,
    required_sections: Sequence[str],
    md_to_tex,
) -> list[str]:
    parser = md_to_tex.ResumeParser(text)
    parser.parse()
    missing: list[str] = []
    for section in required_sections:
        attr_name = SECTION_TO_PARSER_ATTR[section]
        value = getattr(parser, attr_name)
        if not value:
            missing.append(section)
    return missing


def _extract_existing_pdf_header_fields(
    text: str,
    md_to_tex,
) -> tuple[str | None, str | None, str | None]:
    parser = md_to_tex.ResumeParser(text)
    parser.parse()
    name = parser.name.strip() or None
    phone = parser.phone.strip() or None
    email = parser.email.strip() or None
    return name, phone, email


def _missing_sections_in_tex(tex_path: Path, required_sections: Sequence[str]) -> list[str]:
    text = tex_path.read_text(encoding="utf-8")
    missing: list[str] = []
    for section in required_sections:
        if not any(f"\\section{{{alias}}}" in text for alias in _section_aliases(section)):
            missing.append(section)
    return missing


def _missing_sections_in_pdf(pdf_path: Path, required_sections: Sequence[str]) -> list[str]:
    pdf_text = _extract_pdf_text(pdf_path)
    if not pdf_text:
        return []
    normalized_pdf_text = _normalize_extracted_pdf_text(pdf_text)
    missing: list[str] = []
    for section in required_sections:
        if not any(_normalize_extracted_pdf_text(alias) in normalized_pdf_text for alias in _section_aliases(section)):
            missing.append(section)
    return missing


def _section_aliases(section: str) -> tuple[str, ...]:
    if section == "Achievements":
        return ("Achievements", "Additional Information")
    if section == "Additional Information":
        return ("Additional Information", "Achievements")
    return (section,)


def _postprocess_pdf_tex(tex_path: Path) -> None:
    text = tex_path.read_text(encoding="utf-8")
    updated = text.replace(r"\section{Additional Information}", r"\section{Achievements}")
    reordered = _reorder_tex_sections(
        updated,
        (
            "Professional Summary",
            "Skills",
            "Work Experience",
            "Education",
            "Achievements",
        ),
    )
    if reordered != text:
        tex_path.write_text(reordered, encoding="utf-8")


def _reorder_tex_sections(text: str, order: Sequence[str]) -> str:
    first_section = text.find(r"\section{")
    end_document = text.rfind(r"\end{document}")
    if first_section == -1 or end_document == -1 or end_document <= first_section:
        return text

    prefix = text[:first_section]
    body = text[first_section:end_document]
    suffix = text[end_document:]
    parts = re.split(r"(?=\\section\{)", body)
    section_map: dict[str, str] = {}
    extras: list[str] = []
    for part in parts:
        if not part.strip():
            continue
        match = re.match(r"\\section\{([^}]+)\}", part)
        if not match:
            extras.append(part)
            continue
        name = match.group(1)
        if name not in section_map:
            section_map[name] = part
        else:
            extras.append(part)

    ordered_parts = [section_map.pop(name) for name in order if name in section_map]
    ordered_parts.extend(section_map.values())
    ordered_parts.extend(extras)
    return prefix + "".join(ordered_parts) + suffix


def _extract_pdf_text(pdf_path: Path) -> str:
    ghostscript = shutil.which("gs")
    if not ghostscript:
        return ""
    result = subprocess.run(
        [
            ghostscript,
            "-q",
            "-dNOPAUSE",
            "-dBATCH",
            "-sDEVICE=txtwrite",
            "-sOutputFile=-",
            str(pdf_path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=120,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Ghostscript text extraction failed for {pdf_path.name}: "
            f"{result.stderr[-500:] or result.stdout[-500:]}"
        )
    return result.stdout


def _normalize_extracted_pdf_text(text: str) -> str:
    return re.sub(r"\s+", "", text).casefold()


def write_route_outputs(decisions: list[dict], summary: dict, output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_root / "job_routes.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for decision in decisions:
            handle.write(json.dumps(decision, ensure_ascii=False) + "\n")
    (output_root / "route_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
