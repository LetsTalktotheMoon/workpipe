"""
Experimental B-pipeline orchestrator:
cluster retrieval -> explicit PLAN -> WRITE -> REVIEW.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any

from core.anthropic_client import LLMUnavailableError, configure_llm_client
from core.prompt_builder import CLUSTER_WRITER_SYSTEM, build_cluster_rewrite_prompt
from models.jd import JDProfile
from models.resume import Resume
from pipeline.revision_acceptance import should_adopt_revision
from reviewers.unified_reviewer import ReviewSummary, UnifiedReviewer
from security.audit_logger import AuditLogger
from writers.master_writer import MasterWriter

logger = logging.getLogger(__name__)


class ClusterExperimentOrchestrator:
    PASS_THRESHOLD = 93.0
    MAX_PLAN_ROUNDS = 2

    def __init__(
        self,
        output_dir: str = "output",
        enable_llm: bool = False,
        write_model: str = "gpt-5.4",
        review_model: str = "gpt-5.4-mini",
        llm_transport: str = "auto",
    ):
        configure_llm_client(
            enabled=enable_llm,
            write_model=write_model,
            review_model=review_model,
            transport=llm_transport,
        )
        self.writer = MasterWriter()
        self.reviewer = UnifiedReviewer()
        self.output_dir = output_dir
        self.audit = AuditLogger(output_dir)
        os.makedirs(output_dir, exist_ok=True)

    def run(
        self,
        *,
        base_resume_md: str,
        selection: Any,
        company_context: dict[str, Any],
        jd_text: str,
        jd_id: str = "",
        company: str = "",
    ) -> dict[str, Any]:
        jd = JDProfile.from_text(jd_text, jd_id=jd_id, company=company)
        self.audit.log(
            "cluster_jd_parsed",
            {
                "jd_id": jd.jd_id,
                "company": jd.company,
                "title": jd.title,
                "role_type": jd.role_type,
                "seniority": jd.seniority,
                "cluster_type": selection.cluster_type,
                "cluster_key": selection.cluster_key,
            },
        )

        current_base_md = base_resume_md
        previous_plan = ""
        best_result: dict[str, Any] | None = None

        for round_index in range(1, self.MAX_PLAN_ROUNDS + 1):
            base_rewrite_review = self.reviewer.review(current_base_md, jd, mode="rewrite")
            self.audit.log(
                f"cluster_base_review_round_{round_index}",
                self._review_payload(base_rewrite_review),
            )
            try:
                prompt = build_cluster_rewrite_prompt(
                    base_resume_md=current_base_md,
                    jd=jd,
                    cluster_type=selection.cluster_type,
                    cluster_key=selection.cluster_key,
                    candidate_match=selection.candidate_match.to_dict(),
                    top_matches=[item.to_dict() for item in selection.top_matches],
                    company_context=company_context,
                    base_rewrite_review=self._review_payload(base_rewrite_review),
                    previous_plan=previous_plan,
                    round_index=round_index,
                )
                resume_md, plan_text = self.writer.write_from_prompt(
                    prompt,
                    jd=jd,
                    system_prompt=CLUSTER_WRITER_SYSTEM,
                    cache_key_parts=(
                        jd.jd_id or "unknown",
                        jd.company or "",
                        selection.cluster_key,
                        f"cluster_experiment_round_{round_index}",
                    ),
                )
            except LLMUnavailableError as exc:
                return self._unavailable_result(jd_id, str(exc))

            resume = Resume.from_markdown(
                resume_md,
                target_jd_id=jd.jd_id,
                target_company=jd.company,
                target_role=jd.title,
                target_seniority=jd.seniority,
            )
            review = self.reviewer.review(resume_md, jd)
            self.audit.log(
                f"cluster_review_round_{round_index}",
                self._review_payload(review) | {"plan_length": len(plan_text or "")},
            )
            candidate_result = {
                "resume_markdown": resume_md,
                "resume": resume,
                "review": review,
                "plan_text": plan_text,
                "revised": round_index > 1,
                "final_score": review.weighted_score,
                "verdict": "pass" if review.passed else "pending",
            }

            if best_result is None:
                best_result = candidate_result
            else:
                adopted = should_adopt_revision(
                    score_before=best_result["review"].weighted_score,
                    critical_before=best_result["review"].critical_count,
                    high_before=best_result["review"].high_count,
                    score_after=review.weighted_score,
                    critical_after=review.critical_count,
                    high_after=review.high_count,
                    passed_after=review.passed,
                )
                self.audit.log(
                    f"cluster_revision_gate_round_{round_index}",
                    {
                        "adopted": adopted,
                        "score_before": best_result["review"].weighted_score,
                        "score_after": review.weighted_score,
                        "critical_before": best_result["review"].critical_count,
                        "critical_after": review.critical_count,
                        "high_before": best_result["review"].high_count,
                        "high_after": review.high_count,
                    },
                )
                if adopted:
                    best_result = candidate_result
                else:
                    break

            if review.passed or not review.needs_revision:
                break

            current_base_md = resume_md
            previous_plan = plan_text or previous_plan

        assert best_result is not None
        output_path = self._save_output(
            resume_md=best_result["resume_markdown"],
            review=best_result["review"],
            plan_text=best_result["plan_text"],
            jd=jd,
            verdict=best_result["verdict"],
            selection=selection,
            company_context=company_context,
        )
        best_result["output_path"] = output_path
        return best_result

    def _save_output(
        self,
        *,
        resume_md: str,
        review: ReviewSummary,
        plan_text: str,
        jd: JDProfile,
        verdict: str,
        selection: Any,
        company_context: dict[str, Any],
    ) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = f"{jd.jd_id or 'unknown'}_{timestamp}"

        md_path = os.path.join(self.output_dir, f"{prefix}_resume.md")
        with open(md_path, "w", encoding="utf-8") as handle:
            handle.write(resume_md)

        if plan_text:
            plan_path = os.path.join(self.output_dir, f"{prefix}_plan.txt")
            with open(plan_path, "w", encoding="utf-8") as handle:
                handle.write(plan_text)

        review_path = os.path.join(self.output_dir, f"{prefix}_review.json")
        payload = {
            "jd_id": jd.jd_id,
            "company": jd.company,
            "title": jd.title,
            "role_type": jd.role_type,
            "verdict": verdict,
            "final_score": round(review.weighted_score, 1),
            "cluster_type": selection.cluster_type,
            "cluster_key": selection.cluster_key,
            "selected_base_job_id": selection.candidate_match.candidate.job_id,
            "selected_base_company": selection.candidate_match.candidate.company_name,
            "selected_base_title": selection.candidate_match.candidate.title,
            "selected_base_artifact_dir": str(selection.candidate_match.candidate.artifact_dir),
            "company_context_version_count": int(company_context.get("version_count", 0) or 0),
            **self._review_payload(review),
        }
        with open(review_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)

        return md_path

    @staticmethod
    def _review_payload(review: ReviewSummary) -> dict[str, Any]:
        return review.__dict__ | {
            "scores": {key: vars(value) for key, value in review.dimensions.items()},
            "weighted_score": review.weighted_score,
            "revision_instructions": review.revision_instructions,
            "revision_priority": review.revision_priority,
        }

    @staticmethod
    def _unavailable_result(jd_id: str, error: str) -> dict[str, Any]:
        return {
            "resume_markdown": "",
            "resume": None,
            "review": None,
            "plan_text": "",
            "revised": False,
            "final_score": 0.0,
            "verdict": "error",
            "output_path": "",
            "error": error,
            "jd_id": jd_id,
        }
