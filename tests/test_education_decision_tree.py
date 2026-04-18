from __future__ import annotations

import sys
from types import SimpleNamespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from runtime.config.education_decision_tree import decide_education
from runtime.models.resume import Education, Resume
from runtime.writers.master_writer import _normalize_education_entries


def _jd(**overrides) -> SimpleNamespace:
    payload = {
        "jd_id": "jd-education-tree",
        "company": "Acme",
        "title": "Software Engineer",
        "role_type": "swe_backend",
        "business_domain": "infra",
        "seniority": "entry",
        "team_direction": "",
        "raw_text": "",
        "tech_required": ["Python"],
        "tech_preferred": [],
        "tech_or_groups": [],
        "soft_required": [],
        "soft_preferred": [],
        "responsibilities": [],
        "qualifications_required": [],
        "qualifications_preferred": [],
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def _edu(edu_id: str, degree: str, school: str, dates: str = "Expected May 2026") -> Education:
    return Education(id=edu_id, degree=degree, school=school, dates=dates)


def test_decide_education_defaults_to_gt_only() -> None:
    result = decide_education(_jd())

    assert result["selected_education"] == ["gt_mscs"]
    assert result["gt_label"] == "MSCS"
    assert result["bisu_track"] == "Finance"


def test_decide_education_keeps_uiuc_for_pm_direction() -> None:
    result = decide_education(
        _jd(
            title="Product Manager",
            raw_text="Location: Remote",
        )
    )

    assert result["selected_education"] == ["gt_mscs", "uiuc_msim"]
    assert result["gt_label"] == "OMSCS"


def test_decide_education_keeps_uiuc_for_information_management_and_illinois() -> None:
    result = decide_education(
        _jd(
            title="Software Engineer",
            qualifications_required=["Information management experience is required."],
            raw_text="Location: Chicago, IL",
        )
    )

    assert "uiuc_msim" in result["selected_education"]
    assert result["gt_label"] == "OMSCS"


def test_decide_education_keeps_bnu_for_ux_and_education_signals() -> None:
    result = decide_education(
        _jd(
            title="UX Researcher",
            business_domain="education",
            raw_text="China education product",
        )
    )

    assert "bnu_ba" in result["selected_education"]


def test_decide_education_keeps_bisu_for_finance_and_international_signals() -> None:
    result = decide_education(
        _jd(
            title="Software Engineer",
            business_domain="fintech",
            qualifications_preferred=["International business exposure."],
        )
    )

    assert "bisu_mib" in result["selected_education"]
    assert result["bisu_track"] == "Finance"


def test_normalize_education_entries_uses_full_jd_signals() -> None:
    resume = Resume(
        education=[
            _edu("gt_mscs", "M.S. Computer Science", "Georgia Institute of Technology"),
        ]
    )
    jd = _jd(
        title="Product Manager",
        business_domain="education",
        raw_text="Location: Chicago, IL. Required qualifications include information management experience.",
        qualifications_required=["Information management experience is required."],
        qualifications_preferred=["International business exposure."],
        responsibilities=["Build education platform products."],
    )

    changed = _normalize_education_entries(resume, jd)

    assert changed is True
    assert [edu.id for edu in resume.education] == [
        "gt_mscs",
        "uiuc_msim",
        "bisu_mib",
        "bnu_ba",
    ]
    assert resume.education[0].degree == "M.S. Computer Science (OMSCS)"
    assert resume.education[1].degree == "M.S. Information Management (MSIM)"
    assert resume.education[2].track == "Finance"
