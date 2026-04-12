from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from models.resume import Bullet, Education, Experience, Project, Resume, Seniority, SkillCategory
from automation.artifacts import CORE_REQUIRED_SECTIONS, _load_md_to_tex, _prepare_pdf_compile_input
from pdf_compiler.markdown_adapter import resume_to_pdf_markdown
from pdf_compiler.md_to_tex import ResumeParser


def _sample_resume() -> Resume:
    return Resume(
        summary=[
            "**Backend Delivery:** Built services for data workflows.",
            "**Platform Thinking:** Improved reliability for batch pipelines.",
            "**Analytical Judgment:** Applied structured problem-solving under ambiguity.",
        ],
        skills=[
            SkillCategory(name="Languages", skills=["Python", "SQL", "Go", "Bash"]),
            SkillCategory(name="Infra", skills=["Docker", "Kubernetes", "Airflow", "Kafka"]),
        ],
        experiences=[
            Experience(
                id="exp-didi",
                company="DiDi",
                department="IBG",
                title="Senior Data Analyst",
                dates="Sep 2022 – May 2024",
                location="Beijing/Mexico",
                seniority=Seniority.MID_SENIOR,
                cross_functional_note="Data lead within a 13-person cross-functional squad.",
                bullets=[
                    Bullet(text="Built Python data pipelines for weekly operations reporting."),
                    Bullet(text="Improved Kafka-based metrics freshness for dispatch dashboards."),
                ],
                project=Project(
                    title="Dispatch Analytics Platform",
                    parent_experience_id="exp-didi",
                    baseline="Unified reporting for cross-market operations.",
                    bullets=[
                        Bullet(text="Built Airflow jobs to refresh KPI datasets daily."),
                        Bullet(text="Delivered Dockerized services for internal reporting."),
                    ],
                ),
            )
        ],
        education=[
            Education(
                id="gt",
                degree="M.S. Computer Science",
                school="Georgia Tech",
                dates="Expected May 2026",
            )
        ],
        achievement="China national certified Go 2-dan — city champion (2022) and third place (2023).",
    )


def test_resume_to_pdf_markdown_emits_expected_sections() -> None:
    markdown = resume_to_pdf_markdown(
        _sample_resume(),
        name="Jane Doe",
        phone="555-123-4567",
        email="jane@example.com",
    )

    assert "# Jane Doe" in markdown
    assert "## Work Experience" in markdown
    assert "**_Project: Dispatch Analytics Platform_**" in markdown
    assert "## Achievements" in markdown


def test_pdf_parser_can_parse_adapter_output() -> None:
    markdown = resume_to_pdf_markdown(
        _sample_resume(),
        name="Jane Doe",
        phone="555-123-4567",
        email="jane@example.com",
    )
    parser = ResumeParser(markdown)
    parser.parse()

    assert parser.name == "Jane Doe"
    assert len(parser.summary_bullets) == 3
    assert len(parser.skills) == 2
    assert len(parser.work_experience) == 1
    assert parser.work_experience[0]["title"] == "Senior Data Analyst"
    assert parser.education[0][0] == "M.S. Computer Science"
    assert parser.additional


def test_prepare_pdf_compile_input_adds_header_to_headerless_resume(tmp_path: Path) -> None:
    source_path = tmp_path / "resume.md"
    source_path.write_text(_sample_resume().to_markdown(), encoding="utf-8")

    prepared_path = _prepare_pdf_compile_input(
        source_path,
        tmp_path,
        CORE_REQUIRED_SECTIONS,
        _load_md_to_tex(),
        name="Jane Doe",
        phone="555-123-4567",
        email="jane@example.com",
    )

    prepared_text = prepared_path.read_text(encoding="utf-8")
    parser = ResumeParser(prepared_text)
    parser.parse()

    assert prepared_text.startswith("# Jane Doe\n555-123-4567 | jane@example.com\n")
    assert parser.name == "Jane Doe"
    assert parser.phone == "555-123-4567"
    assert parser.email == "jane@example.com"


def test_prepare_pdf_compile_input_preserves_existing_header_without_explicit_profile(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "resume.md"
    source_path.write_text(
        resume_to_pdf_markdown(
            _sample_resume(),
            name="Existing Name",
            phone="555-111-2222",
            email="existing@example.com",
        ),
        encoding="utf-8",
    )

    prepared_path = _prepare_pdf_compile_input(
        source_path,
        tmp_path,
        CORE_REQUIRED_SECTIONS,
        _load_md_to_tex(),
    )

    parser = ResumeParser(prepared_path.read_text(encoding="utf-8"))
    parser.parse()

    assert parser.name == "Existing Name"
    assert parser.phone == "555-111-2222"
    assert parser.email == "existing@example.com"
