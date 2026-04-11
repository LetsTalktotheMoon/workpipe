"""
Seed Retarget Orchestrator.

Use an existing promoted seed only as a starting draft and context anchor.
The writer is free to rewrite against reviewer instructions instead of preserving
seed phrasing or structure.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict

from config.frozen_constraints import verify_constraints_integrity
from core.anthropic_client import LLMUnavailableError, configure_llm_client
from core.prompt_builder import build_upgrade_revision_prompt
from models.jd import JDProfile
from models.resume import Resume
from pipeline.revision_acceptance import should_adopt_revision
from reviewers.unified_reviewer import ReviewSummary, UnifiedReviewer
from security.audit_logger import AuditLogger
from writers.master_writer import MasterWriter

logger = logging.getLogger(__name__)


class SeedRetargetOrchestrator:
    PASS_THRESHOLD = 93.0

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
        seed_resume_md: str,
        seed_label: str,
        route_mode: str,
        jd_text: str,
        jd_id: str = "",
        company: str = "",
        top_candidate: dict | None = None,
    ) -> Dict:
        verify_constraints_integrity()

        jd = JDProfile.from_text(jd_text, jd_id=jd_id, company=company)
        self.audit.log(
            "retarget_jd_parsed",
            {
                "jd_id": jd.jd_id,
                "company": jd.company,
                "role_type": jd.role_type,
                "seniority": jd.seniority,
                "tech_required": jd.tech_required,
                "seed_label": seed_label,
                "route_mode": route_mode,
            },
        )

        try:
            seed_rewrite_review = self.reviewer.review(seed_resume_md, jd, mode="rewrite")
            self.audit.log("retarget_seed_review", seed_rewrite_review.to_dict())
            revision_prompt = build_upgrade_revision_prompt(
                resume_md=seed_resume_md,
                review_result=seed_rewrite_review.__dict__ | {
                    "scores": {k: vars(v) for k, v in seed_rewrite_review.dimensions.items()},
                    "weighted_score": seed_rewrite_review.weighted_score,
                    "revision_instructions": seed_rewrite_review.revision_instructions,
                    "revision_priority": seed_rewrite_review.revision_priority,
                },
                tech_required=jd.tech_required,
                jd_title=jd.title,
                target_company=jd.company,
                route_mode=route_mode,
                seed_label=seed_label,
            )
            resume_md = self.writer.revise(
                seed_resume_md,
                revision_prompt,
                jd,
                rewrite_mode="upgrade",
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
        self.audit.log("retarget_resume_generated", {"length": len(resume_md)})

        review = self.reviewer.review(resume_md, jd)
        self.audit.log("retarget_review_complete", review.to_dict())
        revised = False

        if not review.passed and review.needs_revision:
            try:
                score_before = review.weighted_score
                critical_before = review.critical_count
                high_before = review.high_count
                rewrite_review = self.reviewer.review(resume_md, jd, mode="rewrite")
                revision_prompt = build_upgrade_revision_prompt(
                    resume_md=resume_md,
                    review_result=rewrite_review.__dict__ | {
                        "scores": {k: vars(v) for k, v in rewrite_review.dimensions.items()},
                        "weighted_score": rewrite_review.weighted_score,
                        "revision_instructions": rewrite_review.revision_instructions,
                        "revision_priority": rewrite_review.revision_priority,
                    },
                    tech_required=jd.tech_required,
                    jd_title=jd.title,
                    target_company=jd.company,
                    route_mode=route_mode,
                    seed_label=seed_label,
                )
                revised_md = self.writer.revise(
                    resume_md,
                    revision_prompt,
                    jd,
                    rewrite_mode="upgrade",
                )
                revised_review = self.reviewer.review(revised_md, jd)
                improved = should_adopt_revision(
                    score_before=score_before,
                    critical_before=critical_before,
                    high_before=high_before,
                    score_after=revised_review.weighted_score,
                    critical_after=revised_review.critical_count,
                    high_after=revised_review.high_count,
                    passed_after=revised_review.passed,
                )
                if improved:
                    resume_md = revised_md
                    review = revised_review
                    revised = True
                    resume = Resume.from_markdown(
                        resume_md,
                        target_jd_id=jd.jd_id,
                        target_company=jd.company,
                        target_role=jd.title,
                        target_seniority=jd.seniority,
                    )
                self.audit.log(
                    "retarget_revision_complete",
                    {
                        "adopted": improved,
                        "score_before": score_before,
                        "score_after": revised_review.weighted_score,
                        "critical_before": critical_before,
                        "critical_after": revised_review.critical_count,
                        "high_before": high_before,
                        "high_after": revised_review.high_count,
                    },
                )
            except LLMUnavailableError:
                pass

        verdict = "pass" if review.passed else "pending"

        output_path = self._save_output(
            resume_md=resume_md,
            review=review,
            jd=jd,
            verdict=verdict,
            revised=revised,
            seed_label=seed_label,
            route_mode=route_mode,
        )
        return {
            "resume_markdown": resume_md,
            "resume": resume,
            "review": review,
            "revised": revised,
            "final_score": review.weighted_score,
            "verdict": verdict,
            "output_path": output_path,
        }

    def _save_output(
        self,
        *,
        resume_md: str,
        review: ReviewSummary,
        jd: JDProfile,
        verdict: str,
        revised: bool,
        seed_label: str,
        route_mode: str,
    ) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = f"{jd.jd_id or 'unknown'}_{timestamp}"

        md_path = os.path.join(self.output_dir, f"{prefix}_resume.md")
        with open(md_path, "w", encoding="utf-8") as handle:
            handle.write(resume_md)

        review_path = os.path.join(self.output_dir, f"{prefix}_review.json")
        review_payload = {
            "jd_id": jd.jd_id,
            "company": jd.company,
            "title": jd.title,
            "role_type": jd.role_type,
            "verdict": verdict,
            "seed_label": seed_label,
            "route_mode": route_mode,
            "final_score": round(review.weighted_score, 1),
            "revised": revised,
            **review.to_dict(),
        }
        with open(review_path, "w", encoding="utf-8") as handle:
            json.dump(review_payload, handle, indent=2, ensure_ascii=False)

        return md_path

    @staticmethod
    def _unavailable_result(jd_id: str, error: str) -> Dict:
        return {
            "resume_markdown": "",
            "resume": None,
            "review": None,
            "revised": False,
            "final_score": 0.0,
            "verdict": "error",
            "output_path": "",
            "error": error,
        }
