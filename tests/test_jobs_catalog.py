from runtime.automation.jobs_catalog import merge_job_rows


def test_merge_order_portfolio_sheet_local():
    portfolio_rows = [
        {
            "job_id": "job-1",
            "apply_link": "https://example.com/apply/1",
            "core_skills": "PortfolioSkill",
            "job_summary": "from-portfolio",
            "application_status": "1_Discovered",
        }
    ]
    sheet_rows = [
        {
            "job_id": "job-1",
            "apply_link": "https://example.com/apply/1",
            "core_skills": "SheetSkill",
            "job_summary": "from-sheet",
            "application_status": "已生成简历",
        }
    ]
    local_rows = [
        {
            "job_id": "job-1",
            "apply_link": "https://example.com/apply/1",
            "core_skills": "LocalSkill",
            "job_summary": "",
            "application_status": "1_Discovered",
        }
    ]

    merged = merge_job_rows(portfolio_rows, sheet_rows, local_rows)

    assert len(merged) == 1
    assert merged[0]["core_skills"] == "LocalSkill"
    # Empty local field should not erase stronger upstream value.
    assert merged[0]["job_summary"] == "from-sheet"
    # Weak discovered status should not downgrade generated.
    assert merged[0]["application_status"] == "已生成简历"


def test_dedup_by_apply_link_without_job_id():
    source_a = [{"apply_link": "https://example.com/apply/dup", "job_title": "A"}]
    source_b = [{"apply_link": "https://example.com/apply/dup", "job_title": "B"}]

    merged = merge_job_rows(source_a, source_b)

    assert len(merged) == 1
    assert merged[0]["job_title"] == "B"


def test_weak_status_does_not_override_strong_status():
    existing = [{"job_id": "job-2", "application_status": "generated"}]
    incoming = [{"job_id": "job-2", "application_status": "discovered"}]

    merged = merge_job_rows(existing, incoming)

    assert len(merged) == 1
    assert merged[0]["application_status"] == "generated"


def test_different_non_empty_job_ids_do_not_merge_on_same_apply_link():
    source_a = [
        {
            "job_id": "job-A",
            "apply_link": "https://example.com/shared-apply",
            "company_name": "Affirm",
        }
    ]
    source_b = [
        {
            "job_id": "job-B",
            "apply_link": "https://example.com/shared-apply",
            "company_name": "Affirm",
        }
    ]

    merged = merge_job_rows(source_a, source_b)
    merged_ids = {row.get("job_id", "") for row in merged}

    assert len(merged) == 2
    assert merged_ids == {"job-A", "job-B"}


def test_missing_job_id_can_merge_into_existing_job_id_by_apply_link():
    source_with_id = [
        {
            "job_id": "job-3",
            "apply_link": "https://example.com/apply/3",
            "job_title": "Original",
        }
    ]
    source_without_id = [
        {
            "job_id": "",
            "apply_link": "https://example.com/apply/3",
            "job_summary": "Fill missing details",
        }
    ]

    merged = merge_job_rows(source_with_id, source_without_id)

    assert len(merged) == 1
    assert merged[0]["job_id"] == "job-3"
    assert merged[0]["job_summary"] == "Fill missing details"
