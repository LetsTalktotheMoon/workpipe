from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from core.anthropic_client import configure_llm_client, get_llm_client
from core.prompt_builder import (
    build_revision_prompt,
    build_seed_retarget_prompt,
    build_upgrade_revision_prompt,
)
from models.jd import JDProfile
from writers import master_writer as master_writer_module


EXPECTED_PROMPT_HASHES = {
    "build_revision_prompt": "1b2c27c056bc58e918336caf0362d7b07b7b871cda45394b965c25a61a73623d",
    "build_seed_retarget_prompt": "d2640f195691430867aec2526afaa7193d3328a1ec62b6d29963e2e7b8bc2de5",
    "build_upgrade_revision_prompt": "e91855093f935d3b871e5dfc89298a510a16cdbe4a87373153259838f6591aeb",
    "strict_revision_system_prompt": "6e5be20e6c84d700af09bf08c6fea6fba07587dc8639e0667f70114b7cb59c63",
    "upgrade_revision_system_prompt": "876266872c7cac3429703077309361577b211f98d6b88bf78688a507d5579907",
}


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sample_jd() -> JDProfile:
    return JDProfile(
        jd_id="jd-123",
        company="ExampleCo",
        title="Senior Backend Engineer",
        role_type="swe_backend",
        seniority="senior",
        tech_required=["Python", "Kafka", "AWS"],
        tech_preferred=["Go", "Kubernetes"],
    )


def _sample_review_result() -> dict:
    return {
        "revision_instructions": (
            "1. 强化 Summary 中的 backend ownership。\n"
            "2. 在 DiDi bullet 中补 Kafka 生产证据。"
        ),
        "revision_priority": ["补齐 Kafka 正文证据", "强化 senior backend scope"],
        "weighted_score": 91.4,
        "scores": {
            "r2_jd_fitness": {
                "findings": [
                    {
                        "severity": "high",
                        "field": "Experience",
                        "issue": "Kafka 仅出现在 Skills",
                        "fix": "在 DiDi bullet 写出生产使用场景",
                    }
                ]
            },
            "r4_rationality": {
                "findings": [
                    {
                        "severity": "medium",
                        "field": "Summary",
                        "issue": "Senior signal 偏弱",
                        "fix": "提升 owner/operator 表达",
                    }
                ]
            },
        },
    }


def _sample_resume_md() -> str:
    return (
        "## Professional Summary\n"
        "* **Backend:** Built services.\n\n"
        "## Skills\n"
        "* **Languages:** Python, SQL\n"
    )


def _sample_seed_resume_md() -> str:
    return (
        f"{_sample_resume_md()}\n"
        "## Experience\n"
        "### Engineer | ExampleCo · Platform\n"
        "*2024 | Remote*\n\n"
        "* Built pipelines.\n"
    )


def _sample_plan_text() -> str:
    return "## FINAL PLAN\n- TikTok: Python\n- DiDi: Kafka\n"


def _sample_top_candidate() -> dict:
    return {
        "missing_required": ["Kafka"],
        "label": "seed-main",
        "same_company": True,
        "seed_company_name": "ExampleCo",
        "source_job_id": "source-1",
        "company_anchor": True,
        "project_ids": [],
    }


def test_prompt_builder_hashes_remain_identical() -> None:
    jd = _sample_jd()
    review_result = _sample_review_result()
    resume_md = _sample_resume_md()
    seed_resume_md = _sample_seed_resume_md()
    plan_text = _sample_plan_text()

    samples = {
        "build_revision_prompt": build_revision_prompt(
            resume_md,
            review_result,
            plan_text=plan_text,
            tech_required=jd.tech_required,
            jd_title=jd.title,
            target_company=jd.company,
        ),
        "build_seed_retarget_prompt": build_seed_retarget_prompt(
            seed_resume_md,
            jd,
            seed_label="seed-main",
            route_mode="reuse",
            top_candidate=_sample_top_candidate(),
        ),
        "build_upgrade_revision_prompt": build_upgrade_revision_prompt(
            seed_resume_md,
            review_result,
            tech_required=jd.tech_required,
            jd_title=jd.title,
            target_company=jd.company,
            route_mode="reuse",
            seed_label="seed-main",
            plan_text=plan_text,
        ),
        "strict_revision_system_prompt": master_writer_module.STRICT_REVISION_SYSTEM_PROMPT,
        "upgrade_revision_system_prompt": master_writer_module.UPGRADE_REVISION_SYSTEM_PROMPT,
    }

    for key, value in samples.items():
        assert _sha256(value) == EXPECTED_PROMPT_HASHES[key], key


def test_master_writer_revision_prompts_stay_identical_on_kimi_path(monkeypatch) -> None:
    monkeypatch.setenv("KIMI_API_KEY", "test-kimi-key")
    configure_llm_client(
        enabled=True,
        write_model="kimi-for-coding",
        review_model="kimi-for-coding",
        transport="kimi",
    )
    client = get_llm_client()
    writer = master_writer_module.MasterWriter()
    captured: list[tuple[str, str, str]] = []

    monkeypatch.setattr(client, "is_available", lambda: True)
    monkeypatch.setattr(client, "_selected_transport", lambda: "kimi")

    def fake_run_kimi_api(prompt: str, model: str, system: str = "") -> str:
        captured.append((prompt, model, system))
        return _sample_resume_md()

    monkeypatch.setattr(client, "_run_kimi_api", fake_run_kimi_api)
    monkeypatch.setattr(master_writer_module, "get_llm_client", lambda: client)

    writer.revise(
        _sample_resume_md(),
        build_revision_prompt(
            _sample_resume_md(),
            _sample_review_result(),
            plan_text=_sample_plan_text(),
            tech_required=_sample_jd().tech_required,
            jd_title=_sample_jd().title,
            target_company=_sample_jd().company,
        ),
        rewrite_mode="strict",
    )
    writer.revise(
        _sample_seed_resume_md(),
        build_upgrade_revision_prompt(
            _sample_seed_resume_md(),
            _sample_review_result(),
            tech_required=_sample_jd().tech_required,
            jd_title=_sample_jd().title,
            target_company=_sample_jd().company,
            route_mode="reuse",
            seed_label="seed-main",
            plan_text=_sample_plan_text(),
        ),
        rewrite_mode="upgrade",
    )

    assert [item[1] for item in captured] == ["kimi-for-coding", "kimi-for-coding"]
    assert _sha256(captured[0][0]) == EXPECTED_PROMPT_HASHES["build_revision_prompt"]
    assert _sha256(captured[0][2]) == EXPECTED_PROMPT_HASHES["strict_revision_system_prompt"]
    assert _sha256(captured[1][0]) == EXPECTED_PROMPT_HASHES["build_upgrade_revision_prompt"]
    assert _sha256(captured[1][2]) == EXPECTED_PROMPT_HASHES["upgrade_revision_system_prompt"]
