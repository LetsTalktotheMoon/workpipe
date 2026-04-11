from match_pipe.loader import load_job_documents
from match_pipe.units import build_structured_job


def _find_job_by_terms(*terms: str):
    for document in load_job_documents(include_scraped=True, include_portfolio=False):
        text = (document.raw_text or "").lower()
        if all(term in text for term in terms):
            return document
    raise AssertionError(f"missing job with terms: {terms}")


def test_or_unit_separates_years_from_tech():
    job = build_structured_job(_find_job_by_terms("python or java", "years"))
    or_units = [unit for unit in job.requirement_units if unit.logic_type == "OR"]
    assert any({"TECH_PYTHON", "TECH_JAVA"} <= set(unit.members) for unit in or_units)
    assert all("EXP_" not in member for unit in or_units for member in unit.members)


def test_parent_any_child_detected():
    job = build_structured_job(_find_job_by_terms("modern programming language"))
    assert any(unit.logic_type == "PARENT_ANY_CHILD" and unit.members == ["TECH_MAINSTREAM_PROGRAMMING_LANGUAGE"] for unit in job.requirement_units)


def test_at_least_k_not_created_from_years_phrase():
    job = build_structured_job(_find_job_by_terms("at least 1 year of experience working with machine learning"))
    assert all(
        unit.logic_type != "AT_LEAST_K"
        for unit in job.requirement_units
        if "at least 1 year of experience working with machine learning" in unit.display_name.lower()
    )
