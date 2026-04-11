from match_pipe.incremental import IncrementalMatchStore
from match_pipe.loader import load_job_documents
from match_pipe.starter_selector import StarterSelector


def test_starter_selector_outputs_dual_channel_fields():
    selector = StarterSelector.from_project_data()
    query_id = selector.semantic_engine.index.jobs[0].job_id
    response = selector.select_by_job_id(query_id, top_k=2).to_dict()
    assert "semantic_best_anchor" in response
    assert "semantic_cluster_mode" in response
    assert "semantic_positive_cluster" in response
    assert "semantic_starter_anchor" in response
    assert "company_best_anchor" in response
    assert "writer_input" in response
    assert "semantic_cluster_mode" in response["writer_input"]
    assert "semantic_positive_cluster" in response["writer_input"]
    assert len(response["semantic_top_k"]) <= 2
    assert len(response["company_top_k"]) <= 2
    if response["semantic_best_anchor"] is not None:
        assert "has_resume_artifact" in response["semantic_best_anchor"]
        assert "resume_path" in response["semantic_best_anchor"]


def test_incremental_store_indexes_new_job_and_records_alias_candidate():
    store = IncrementalMatchStore.from_project_data()
    source = load_job_documents(include_scraped=True, include_portfolio=False)[0]
    row = {
        **source.row,
        "job_id": f"{source.job_id}::pytest",
        "job_title": f"{source.title} Experimental ABCDEGraph",
        "must_have_quals": "ABCDEGraph platform experience",
        "core_skills": "Linux, CI/CD",
        "preferred_quals": "Scala or Python",
    }
    result = store.ingest_row(row)
    assert result.action == "indexed"
    assert any(item["token"] == "ABCDEGraph" for item in result.to_dict()["alias_candidates"])
    response = store.engine.match_by_job_id(result.job_id, top_k=3)
    assert response.candidate_pool_size > 0
