from __future__ import annotations

import json
from pathlib import Path

from runtime.job_webapp import main as job_webapp_main


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_catalog_only_job_is_not_labeled_scraped_current(tmp_path: Path, monkeypatch) -> None:
    catalog_path = tmp_path / "jobs_catalog.json"
    portfolio_path = tmp_path / "portfolio_index.json"
    state_path = tmp_path / "job_app_status.json"
    yoe_cache_path = tmp_path / "job_app_yoe_cache.json"
    backfill_path = tmp_path / "job_status_backfill.json"

    _write_json(
        catalog_path,
        [
            {
                "job_id": "job-123",
                "company_name": "Acme",
                "job_title": "Data Scientist",
                "discovered_date": "2026-04-13",
                "publish_time": "2026-04-12",
                "apply_link": "https://example.com/apply/job-123",
            }
        ],
    )
    _write_json(portfolio_path, [])
    _write_json(state_path, {})
    _write_json(yoe_cache_path, {})
    _write_json(backfill_path, {})

    monkeypatch.setattr(job_webapp_main, "JOBS_CATALOG_PATH", catalog_path)
    monkeypatch.setattr(job_webapp_main, "PORTFOLIO_INDEX_PATH", portfolio_path)
    monkeypatch.setattr(job_webapp_main, "STATE_PATH", state_path)
    monkeypatch.setattr(job_webapp_main, "YOE_CACHE_PATH", yoe_cache_path)
    monkeypatch.setattr(job_webapp_main, "BACKFILL_STATUS_PATH", backfill_path)

    store = job_webapp_main.JobAppStore()
    payload = store.build_jobs_payload()

    assert payload["meta"]["total_jobs"] == 1
    job = payload["jobs"][0]
    assert job["source_scope"] == "catalog_only"
    assert job["review_status"] == "无简历"
    assert job["has_generated_resume"] is False
    assert job["seed_label"] == "No resume generated"
    assert job["resume_dir"] == ""
