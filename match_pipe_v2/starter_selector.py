from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from .matcher import MatchEngine, MatchFeatureConfig, TEACHER_CONFIGS, _jaccard, _norm_title, _role_score, _seniority_score
from .models import MatchResult, StructuredJob


ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_POOL_PATH = ROOT / "match_pipe" / "semantic_boundary_pool.json"
GENERIC_TITLES = {
    "software engineer",
    "software engineer ii",
    "senior software engineer",
    "machine learning engineer",
    "data scientist",
    "software development engineer",
    "new grad software engineer",
}


def _publish_time_key(job: StructuredJob) -> str:
    return str(job.metadata.get("publish_time", "") or "")


def _token_overlap(left: StructuredJob, right: StructuredJob) -> float:
    left_tokens = {token for token in left.title.lower().replace("/", " ").replace("-", " ").split() if len(token) >= 3}
    right_tokens = {token for token in right.title.lower().replace("/", " ").replace("-", " ").split() if len(token) >= 3}
    return _jaccard(left_tokens, right_tokens)


@dataclass
class StarterAnchor:
    job_id: str
    company_name: str
    title: str
    source_kind: str
    score: float
    reuse_readiness: float
    artifact_dir: str
    resume_path: str
    has_resume_artifact: bool
    explanation: list[str]
    missing_critical_units: list[str]

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["score"] = round(self.score, 4)
        payload["reuse_readiness"] = round(self.reuse_readiness, 4)
        return payload


@dataclass
class StarterSelectorResponse:
    query_id: str
    semantic_best_anchor: dict | None
    semantic_top_k: list[dict]
    semantic_positive_cluster: list[dict]
    semantic_cluster_mode: str
    semantic_starter_anchor: dict | None
    semantic_score: float
    semantic_explanation: list[str]
    company_best_anchor: dict | None
    company_top_k: list[dict]
    company_score: float
    company_explanation: list[str]
    delta_summary: list[str]
    writer_input: dict

    def to_dict(self) -> dict:
        return {
            "query_id": self.query_id,
            "semantic_best_anchor": self.semantic_best_anchor,
            "semantic_top_k": self.semantic_top_k,
            "semantic_positive_cluster": self.semantic_positive_cluster,
            "semantic_cluster_mode": self.semantic_cluster_mode,
            "semantic_starter_anchor": self.semantic_starter_anchor,
            "semantic_score": round(self.semantic_score, 4),
            "semantic_explanation": self.semantic_explanation,
            "company_best_anchor": self.company_best_anchor,
            "company_top_k": self.company_top_k,
            "company_score": round(self.company_score, 4),
            "company_explanation": self.company_explanation,
            "delta_summary": self.delta_summary,
            "writer_input": self.writer_input,
        }


class StarterSelector:
    def __init__(
        self,
        *,
        semantic_engine: MatchEngine,
        semantic_config: MatchFeatureConfig | None = None,
    ):
        self.semantic_engine = semantic_engine
        self.semantic_config = semantic_config or TEACHER_CONFIGS["teacher_b_pure_semantic"]
        self.boundary_pool = self._load_boundary_pool()

    @classmethod
    def from_project_data(cls) -> "StarterSelector":
        engine = MatchEngine.from_project_data(
            include_scraped=True,
            include_portfolio=True,
            feature_config=TEACHER_CONFIGS["teacher_b_pure_semantic"],
        )
        return cls(semantic_engine=engine)

    def select_by_job_id(self, job_id: str, *, top_k: int = 3) -> StarterSelectorResponse:
        query = self.semantic_engine.get_job(job_id)
        if query is None:
            raise KeyError(f"Unknown job_id: {job_id}")
        return self.select(query, top_k=top_k)

    def select(self, query: StructuredJob, *, top_k: int = 3) -> StarterSelectorResponse:
        semantic_response = self.semantic_engine.match(query, top_k=max(top_k, 5))
        semantic_top = [self._match_to_anchor(match) for match in semantic_response.matches[:top_k]]
        semantic_cluster_mode, semantic_positive_cluster, semantic_starter_anchor = self._semantic_cluster(query, semantic_response.matches)
        company_top = self._company_channel(query, top_k=top_k)
        semantic_best = semantic_top[0] if semantic_top else None
        company_best = company_top[0] if company_top else None
        delta_summary = self._delta_summary(query, semantic_best, semantic_starter_anchor, company_best, semantic_cluster_mode)
        writer_input = self._writer_input(
            query,
            semantic_top,
            company_top,
            semantic_cluster_mode,
            semantic_positive_cluster,
            semantic_starter_anchor,
            delta_summary,
        )
        return StarterSelectorResponse(
            query_id=query.job_id,
            semantic_best_anchor=semantic_best,
            semantic_top_k=semantic_top,
            semantic_positive_cluster=semantic_positive_cluster,
            semantic_cluster_mode=semantic_cluster_mode,
            semantic_starter_anchor=semantic_starter_anchor,
            semantic_score=(semantic_starter_anchor or semantic_best)["score"] if (semantic_starter_anchor or semantic_best) else 0.0,
            semantic_explanation=(semantic_starter_anchor or semantic_best)["explanation"] if (semantic_starter_anchor or semantic_best) else ["No semantic anchor found."],
            company_best_anchor=company_best,
            company_top_k=company_top,
            company_score=company_best["score"] if company_best else 0.0,
            company_explanation=company_best["explanation"] if company_best else ["No same-company anchor found."],
            delta_summary=delta_summary,
            writer_input=writer_input,
        )

    def _match_to_anchor(self, match: MatchResult) -> dict:
        reuse_readiness = 0.72 * match.requirement_score + 0.28 * match.hard_requirement_score
        artifact_dir = str(match.candidate.metadata.get("artifact_dir", "") or "")
        resume_path = f"{artifact_dir}/resume.md" if artifact_dir else ""
        has_resume_artifact = bool(resume_path) and Path(resume_path).exists()
        review_final_score = float(match.candidate.metadata.get("review_final_score", 0.0) or 0.0)
        historical_quality = max(min(review_final_score / 100.0, 1.0), 0.0)
        starter_priority_score = 0.48 * historical_quality + 0.32 * reuse_readiness + 0.2 * match.total_score
        return StarterAnchor(
            job_id=match.candidate.job_id,
            company_name=match.candidate.company_name,
            title=match.candidate.title,
            source_kind=match.candidate.source_kind,
            score=match.total_score,
            reuse_readiness=reuse_readiness,
            artifact_dir=artifact_dir,
            resume_path=resume_path,
            has_resume_artifact=has_resume_artifact,
            explanation=list(match.explanation),
            missing_critical_units=list(match.missing_critical_units),
        ).to_dict() | {
            "review_final_score": round(review_final_score, 1),
            "review_verdict": str(match.candidate.metadata.get("review_verdict", "") or ""),
            "starter_priority_score": round(starter_priority_score, 4),
        }

    def _company_channel(self, query: StructuredJob, *, top_k: int) -> list[dict]:
        company_key = query.company_name.strip().lower()
        if not company_key:
            return []
        candidate_ids = [
            job_id
            for job_id in self.semantic_engine.index.company_index.get(company_key, set())
            if job_id != query.job_id
        ]
        semantic_response = self.semantic_engine.match(query, top_k=max(len(candidate_ids), top_k + 6))
        semantic_lookup = {item.candidate_job_id: item for item in semantic_response.matches}
        scored: list[tuple[float, dict]] = []
        for candidate_id in candidate_ids:
            semantic_match = semantic_lookup.get(candidate_id)
            if semantic_match is None:
                candidate = self.semantic_engine.get_job(candidate_id)
                if candidate is None:
                    continue
                semantic_match = self.semantic_engine._score_candidate(query, candidate, {"company_recheck"})
            candidate = semantic_match.candidate
            duplicate = self._company_consistency_score(query, semantic_match)
            artifact_dir = str(candidate.metadata.get("artifact_dir", "") or "")
            resume_path = f"{artifact_dir}/resume.md" if artifact_dir else ""
            anchor = StarterAnchor(
                job_id=candidate.job_id,
                company_name=candidate.company_name,
                title=candidate.title,
                source_kind=candidate.source_kind,
                score=duplicate,
                reuse_readiness=0.58 * semantic_match.requirement_score + 0.42 * duplicate,
                artifact_dir=artifact_dir,
                resume_path=resume_path,
                has_resume_artifact=bool(resume_path) and Path(resume_path).exists(),
                explanation=self._company_explanation(query, semantic_match, duplicate),
                missing_critical_units=list(semantic_match.missing_critical_units),
            ).to_dict() | {
                "review_final_score": round(float(candidate.metadata.get("review_final_score", 0.0) or 0.0), 1),
                "review_verdict": str(candidate.metadata.get("review_verdict", "") or ""),
                "starter_priority_score": round(
                    0.48 * max(min(float(candidate.metadata.get("review_final_score", 0.0) or 0.0) / 100.0, 1.0), 0.0)
                    + 0.32 * (0.58 * semantic_match.requirement_score + 0.42 * duplicate)
                    + 0.2 * duplicate,
                    4,
                ),
            }
            scored.append((duplicate, anchor))
        scored.sort(key=lambda item: (item[0], item[1]["reuse_readiness"]), reverse=True)
        return [anchor for _, anchor in scored[:top_k]]

    def _company_consistency_score(self, query: StructuredJob, semantic_match: MatchResult) -> float:
        candidate = semantic_match.candidate
        title_exact = 1.0 if _norm_title(query.title) == _norm_title(candidate.title) else 0.0
        title_overlap = _token_overlap(query, candidate)
        semantic_reuse = 0.64 * semantic_match.requirement_score + 0.36 * semantic_match.hard_requirement_score
        continuity = 0.0
        if query.seniority == candidate.seniority:
            continuity += 0.06
        else:
            continuity += 0.03 * _seniority_score(query.seniority, candidate.seniority)
        continuity += 0.06 * _role_score(query.role_family, candidate.role_family)
        if _publish_time_key(candidate) <= _publish_time_key(query):
            continuity += 0.04
        return min(0.46 * semantic_reuse + 0.34 * title_exact + 0.1 * title_overlap + continuity, 1.0)

    def _company_explanation(self, query: StructuredJob, semantic_match: MatchResult, company_score: float) -> list[str]:
        candidate = semantic_match.candidate
        suitability = "Suitable" if semantic_match.requirement_score >= 0.58 else "Weak"
        return [
            f"Company continuity score={company_score:.2f}; same-company history candidate for {query.company_name}.",
            f"Title overlap={_token_overlap(query, candidate):.2f}; semantic reuse={semantic_match.requirement_score:.2f}.",
            f"{suitability} as continuity anchor; hard gaps={len(semantic_match.missing_critical_units)}.",
        ]

    def _delta_summary(
        self,
        query: StructuredJob,
        semantic_best: dict | None,
        semantic_starter_anchor: dict | None,
        company_best: dict | None,
        semantic_cluster_mode: str,
    ) -> list[str]:
        if semantic_best is None and company_best is None:
            return ["No anchor available in either channel."]
        if semantic_best is not None and company_best is not None and semantic_best["job_id"] == company_best["job_id"]:
            return ["Semantic-best and company-best are the same anchor; downstream can use a single starter."]
        lines: list[str] = []
        if semantic_best is not None:
            lines.append(
                f"Semantic-best is {semantic_best['company_name']} / {semantic_best['title']}, optimized for global requirement-unit reuse."
            )
        if semantic_cluster_mode == "multi_acceptable_cluster" and semantic_starter_anchor is not None:
            lines.append(
                f"JD-level judgment is a multi-acceptable-positive cluster; final starter is {semantic_starter_anchor['company_name']} / {semantic_starter_anchor['title']} by historical quality and reuse priority."
            )
        if company_best is not None:
            lines.append(
                f"Company-best is {company_best['company_name']} / {company_best['title']}, optimized for internal version continuity."
            )
        if semantic_best is not None and company_best is not None:
            lines.append(
                "Downstream should use semantic_best as the main template and company_best as a continuity constraint when they differ."
            )
        return lines

    def _writer_input(
        self,
        query: StructuredJob,
        semantic_top: list[dict],
        company_top: list[dict],
        semantic_cluster_mode: str,
        semantic_positive_cluster: list[dict],
        semantic_starter_anchor: dict | None,
        delta_summary: list[str],
    ) -> dict:
        semantic_best = semantic_top[0] if semantic_top else None
        company_best = company_top[0] if company_top else None
        semantic_resume_anchor = self._usable_resume_anchor(semantic_top)
        company_resume_anchor = self._usable_resume_anchor(company_top)
        semantic_cluster_resume_anchor = self._usable_resume_anchor(semantic_positive_cluster)
        primary_semantic_anchor = semantic_cluster_resume_anchor or semantic_starter_anchor or semantic_resume_anchor or semantic_best
        if semantic_best is None:
            return {
                "query_id": query.job_id,
                "mode": "no_anchor",
                "primary_anchor": None,
                "continuity_anchor": company_resume_anchor or company_best,
                "semantic_cluster_mode": semantic_cluster_mode,
                "semantic_positive_cluster": semantic_positive_cluster,
                "guidance": delta_summary,
            }
        if company_best is None or semantic_best["job_id"] == company_best["job_id"]:
            return {
                "query_id": query.job_id,
                "mode": "single_anchor",
                "primary_anchor": primary_semantic_anchor,
                "continuity_anchor": company_resume_anchor or primary_semantic_anchor or company_best or semantic_best,
                "semantic_cluster_mode": semantic_cluster_mode,
                "semantic_positive_cluster": semantic_positive_cluster,
                "guidance": delta_summary,
            }
        downgrade_company = company_best["reuse_readiness"] < 0.54 or len(company_best["missing_critical_units"]) >= 3
        return {
            "query_id": query.job_id,
            "mode": "semantic_plus_company_constraint",
            "primary_anchor": primary_semantic_anchor,
            "continuity_anchor": None if downgrade_company else (company_resume_anchor or company_best),
            "continuity_anchor_degraded": downgrade_company,
            "semantic_cluster_mode": semantic_cluster_mode,
            "semantic_positive_cluster": semantic_positive_cluster,
            "guidance": delta_summary + [
                "Use semantic_best as the writing skeleton; only apply company_best-compatible wording where it does not reintroduce hard gaps."
            ],
        }

    @staticmethod
    def _usable_resume_anchor(anchors: list[dict | None]) -> dict | None:
        for anchor in anchors:
            if anchor and anchor.get("has_resume_artifact") and Path(str(anchor.get("resume_path", "") or "")).exists():
                return anchor
        return None

    @staticmethod
    def _load_boundary_pool() -> dict[tuple[str, str], dict]:
        if not BOUNDARY_POOL_PATH.exists():
            return {}
        payload = json.loads(BOUNDARY_POOL_PATH.read_text(encoding="utf-8"))
        return {
            (item["query_id"], item["category"]): item
            for item in payload.get("boundary_cases", [])
        }

    def _semantic_cluster(self, query: StructuredJob, matches: list[MatchResult]) -> tuple[str, list[dict], dict | None]:
        anchors = [self._match_to_anchor(match) for match in matches[:5]]
        boundary_items = [
            item
            for (query_id, _), item in self.boundary_pool.items()
            if query_id == query.job_id
        ]
        if boundary_items:
            acceptable_ids = {candidate_id for item in boundary_items for candidate_id in item.get("acceptable_positive_ids", [])}
            cluster = [anchor for anchor in anchors if anchor["job_id"] in acceptable_ids and anchor.get("has_resume_artifact")]
            if cluster:
                cluster.sort(key=lambda item: (item.get("starter_priority_score", 0.0), item.get("review_final_score", 0.0), item["score"]), reverse=True)
                return "multi_acceptable_cluster", cluster, cluster[0]

        if _norm_title(query.title) not in GENERIC_TITLES or len(anchors) < 2:
            return "single_positive", [], anchors[0] if anchors else None

        best_score = anchors[0]["score"]
        cluster = [
            anchor
            for anchor in anchors
            if anchor.get("has_resume_artifact")
            and best_score - anchor["score"] <= 0.025
            and anchor["reuse_readiness"] >= 0.78
        ]
        if len(cluster) >= 2:
            cluster.sort(key=lambda item: (item.get("starter_priority_score", 0.0), item.get("review_final_score", 0.0), item["score"]), reverse=True)
            return "multi_acceptable_cluster", cluster, cluster[0]
        return "single_positive", [], anchors[0] if anchors else None
