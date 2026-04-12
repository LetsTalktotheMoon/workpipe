from match_pipe.loader import document_from_row
from match_pipe.units import build_structured_job


def _build_job(
    *,
    must_have_quals: str = "",
    preferred_quals: str = "",
    core_skills: str = "",
    core_responsibilities: str = "",
    job_summary: str = "",
) -> object:
    document = document_from_row(
        {
            "job_id": "test-job",
            "job_title": "Software Engineer",
            "company_name": "ExampleCo",
            "must_have_quals": must_have_quals,
            "preferred_quals": preferred_quals,
            "core_skills": core_skills,
            "core_responsibilities": core_responsibilities,
            "job_summary": job_summary,
            "work_model": "remote",
            "job_location": "Austin, TX",
            "taxonomy_v3": "Software Engineering",
        },
        source_kind="test_fixture",
    )
    assert document is not None
    return build_structured_job(document)


def test_or_unit_separates_years_from_tech():
    job = _build_job(
        must_have_quals="4+ years of experience with Python or Java in production systems."
    )
    or_units = [unit for unit in job.requirement_units if unit.logic_type == "OR"]
    assert any({"TECH_PYTHON", "TECH_JAVA"} <= set(unit.members) for unit in or_units)
    assert all("EXP_" not in member for unit in or_units for member in unit.members)


def test_parent_any_child_detected():
    job = _build_job(
        must_have_quals="Experience with a modern programming language in production systems."
    )
    assert any(
        unit.logic_type == "PARENT_ANY_CHILD"
        and unit.members == ["TECH_MAINSTREAM_PROGRAMMING_LANGUAGE"]
        for unit in job.requirement_units
    )


def test_at_least_k_not_created_from_years_phrase():
    phrase = "At least 1 year of experience working with machine learning."
    job = _build_job(must_have_quals=phrase)
    assert all(
        unit.logic_type != "AT_LEAST_K"
        for unit in job.requirement_units
        if phrase.lower() in unit.display_name.lower()
    )
