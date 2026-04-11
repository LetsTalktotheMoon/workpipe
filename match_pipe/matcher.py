from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
import math
import re
from typing import Iterable

from .loader import load_job_documents
from .models import MatchResponse, MatchResult, RequirementUnit, StructuredJob, UnitMatchDetail
from .taxonomy import DEFAULT_TAXONOMY, Taxonomy
from .units import build_structured_job


ROLE_COMPATIBILITY: dict[str, dict[str, float]] = {
    "ai_ml_swe": {"ai_ml_swe": 1.0, "data_science": 0.78, "platform": 0.62, "backend_generalist": 0.55},
    "backend_generalist": {"backend_generalist": 1.0, "fullstack": 0.84, "platform": 0.7, "generalist": 0.88},
    "data_platform": {"data_platform": 1.0, "platform": 0.8, "backend_generalist": 0.68},
    "data_science": {"data_science": 1.0, "ai_ml_swe": 0.78, "data_platform": 0.66},
    "embedded": {"embedded": 1.0, "platform": 0.42},
    "frontend": {"frontend": 1.0, "fullstack": 0.82},
    "fullstack": {"fullstack": 1.0, "backend_generalist": 0.82, "frontend": 0.82},
    "manager": {"manager": 1.0},
    "mobile": {"mobile": 1.0, "frontend": 0.35},
    "platform": {"platform": 1.0, "backend_generalist": 0.72, "security": 0.6, "data_platform": 0.76},
    "qa": {"qa": 1.0, "generalist": 0.32},
    "security": {"security": 1.0, "platform": 0.62, "backend_generalist": 0.44},
    "solutions": {"solutions": 1.0, "backend_generalist": 0.52, "ai_ml_swe": 0.62},
}

CONSTRAINT_ALIGNMENT: dict[str, dict[str, float]] = {
    "must_have": {
        "must_have": 1.0,
        "strong_preference": 0.9,
        "preferred": 0.72,
        "background": 0.44,
    },
    "strong_preference": {
        "must_have": 1.0,
        "strong_preference": 0.95,
        "preferred": 0.82,
        "background": 0.58,
    },
    "preferred": {
        "must_have": 0.96,
        "strong_preference": 0.94,
        "preferred": 1.0,
        "background": 0.74,
    },
    "background": {
        "must_have": 0.94,
        "strong_preference": 0.92,
        "preferred": 0.9,
        "background": 1.0,
    },
}

LOGIC_ALIGNMENT: dict[str, dict[str, float]] = {
    "SINGLE": {"SINGLE": 1.0, "OR": 0.9, "AND": 0.82, "AT_LEAST_K": 0.86, "PARENT_ANY_CHILD": 0.92},
    "OR": {"SINGLE": 0.94, "OR": 1.0, "AND": 0.86, "AT_LEAST_K": 0.88, "PARENT_ANY_CHILD": 0.9},
    "AND": {"SINGLE": 0.56, "OR": 0.62, "AND": 1.0, "AT_LEAST_K": 0.9, "PARENT_ANY_CHILD": 0.78},
    "AT_LEAST_K": {"SINGLE": 0.52, "OR": 0.72, "AND": 0.9, "AT_LEAST_K": 1.0, "PARENT_ANY_CHILD": 0.74},
    "PARENT_ANY_CHILD": {"SINGLE": 0.94, "OR": 0.9, "AND": 0.78, "AT_LEAST_K": 0.8, "PARENT_ANY_CHILD": 1.0},
}

SENIORITY_RANK = {
    "entry": 0,
    "mid": 1,
    "mid_senior": 2,
    "senior": 3,
    "lead": 4,
}


def _role_score(left: str, right: str) -> float:
    if left == right:
        return 1.0
    return ROLE_COMPATIBILITY.get(left, {}).get(right, 0.2)


def _seniority_score(left: str, right: str) -> float:
    if left == right:
        return 1.0
    left_rank = SENIORITY_RANK.get(left, 1)
    right_rank = SENIORITY_RANK.get(right, 1)
    delta = abs(left_rank - right_rank)
    if delta == 1:
        return 0.82
    if delta == 2:
        return 0.65
    return 0.45


def _surface_tokens(text: str) -> set[str]:
    tokens = {
        token
        for token in re.findall(r"[a-z0-9+#.]{3,}", text.lower())
        if token not in {"with", "that", "this", "from", "into", "their", "using", "have", "will"}
    }
    return tokens


def _norm_title(text: str) -> str:
    return " ".join((text or "").lower().replace("/", " ").replace("-", " ").split())


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


@dataclass
class MatchIndex:
    jobs: list[StructuredJob]
    jobs_by_id: dict[str, StructuredJob]
    pattern_index: dict[str, set[str]]
    member_index: dict[str, set[str]]
    combo_index: dict[str, set[str]]
    surface_token_index: dict[str, set[str]]
    company_index: dict[str, set[str]]
    member_doc_freq: dict[str, int]


@dataclass(frozen=True)
class MatchFeatureConfig:
    name: str
    enable_pattern_recall: bool = True
    enable_hard_unit_recall: bool = True
    enable_hierarchy_recall: bool = True
    enable_combo_recall: bool = True
    enable_surface_recall: bool = True
    enable_same_company_recall: bool = True
    enable_surface_score: bool = True
    enable_metadata_score: bool = True
    enable_duplicate_score: bool = True
    duplicate_uses_same_company: bool = True
    allow_duplicate_override: bool = True


TEACHER_CONFIGS: dict[str, MatchFeatureConfig] = {
    "teacher_a": MatchFeatureConfig(name="teacher_a"),
    "teacher_b_pure_semantic": MatchFeatureConfig(
        name="teacher_b_pure_semantic",
        enable_surface_recall=False,
        enable_same_company_recall=False,
        enable_surface_score=False,
        enable_metadata_score=False,
        enable_duplicate_score=False,
        duplicate_uses_same_company=False,
        allow_duplicate_override=False,
    ),
    "teacher_c_semantic_duplicate": MatchFeatureConfig(
        name="teacher_c_semantic_duplicate",
        enable_same_company_recall=False,
        enable_metadata_score=False,
        duplicate_uses_same_company=False,
    ),
}


def build_index(jobs: Iterable[StructuredJob], *, taxonomy: Taxonomy = DEFAULT_TAXONOMY) -> MatchIndex:
    source_jobs = list(jobs)
    job_list: list[StructuredJob] = []
    jobs_by_id: dict[str, StructuredJob] = {}
    pattern_index: dict[str, set[str]] = defaultdict(set)
    member_index: dict[str, set[str]] = defaultdict(set)
    combo_index: dict[str, set[str]] = defaultdict(set)
    surface_token_index: dict[str, set[str]] = defaultdict(set)
    company_index: dict[str, set[str]] = defaultdict(set)
    member_doc_freq: dict[str, int] = defaultdict(int)

    for job in source_jobs:
        _add_to_index(
            job,
            jobs=job_list,
            jobs_by_id=jobs_by_id,
            pattern_index=pattern_index,
            member_index=member_index,
            combo_index=combo_index,
            surface_token_index=surface_token_index,
            company_index=company_index,
            member_doc_freq=member_doc_freq,
        )

    return MatchIndex(
        jobs=job_list,
        jobs_by_id=jobs_by_id,
        pattern_index=pattern_index,
        member_index=member_index,
        combo_index=combo_index,
        surface_token_index=surface_token_index,
        company_index=company_index,
        member_doc_freq=dict(member_doc_freq),
    )


def _add_to_index(
    job: StructuredJob,
    *,
    jobs: list[StructuredJob],
    jobs_by_id: dict[str, StructuredJob],
    pattern_index: dict[str, set[str]],
    member_index: dict[str, set[str]],
    combo_index: dict[str, set[str]],
    surface_token_index: dict[str, set[str]],
    company_index: dict[str, set[str]],
    member_doc_freq: dict[str, int],
) -> None:
    if job.job_id not in jobs_by_id:
        jobs.append(job)
    jobs_by_id[job.job_id] = job
    pattern_index[job.pattern_signature].add(job.job_id)
    for member in job.expanded_elements:
        member_index[member].add(job.job_id)
    for member in set(job.canonical_elements):
        member_doc_freq[member] += 1
    anchors = [item for item in job.recall_keys if "+" not in item and "(" not in item]
    for left, right in combinations(anchors[:4], 2):
        combo_index[f"{left}+{right}"].add(job.job_id)
    for key in job.recall_keys:
        if "+" in key:
            combo_index[key].add(job.job_id)
    surface_text = " ".join(
        [job.title]
        + [item.display_name for item in job.requirement_units[:8]]
        + job.pending_surface_texts[:4]
    )
    for token in _surface_tokens(surface_text):
        surface_token_index[token].add(job.job_id)
    company_key = job.company_name.strip().lower()
    if company_key:
        company_index[company_key].add(job.job_id)


class MatchEngine:
    def __init__(
        self,
        jobs: Iterable[StructuredJob],
        *,
        taxonomy: Taxonomy = DEFAULT_TAXONOMY,
        feature_config: MatchFeatureConfig | None = None,
    ):
        self.taxonomy = taxonomy
        self.feature_config = feature_config or TEACHER_CONFIGS["teacher_a"]
        self.index = build_index(jobs, taxonomy=taxonomy)

    @classmethod
    def from_project_data(
        cls,
        *,
        include_scraped: bool = True,
        include_portfolio: bool = True,
        taxonomy: Taxonomy = DEFAULT_TAXONOMY,
        feature_config: MatchFeatureConfig | None = None,
    ) -> "MatchEngine":
        documents = load_job_documents(
            include_scraped=include_scraped,
            include_portfolio=include_portfolio,
        )
        jobs = [build_structured_job(document, taxonomy=taxonomy) for document in documents]
        return cls(jobs, taxonomy=taxonomy, feature_config=feature_config)

    def get_job(self, job_id: str) -> StructuredJob | None:
        return self.index.jobs_by_id.get(job_id)

    def add_structured_job(self, job: StructuredJob) -> None:
        if job.job_id in self.index.jobs_by_id:
            return
        _add_to_index(
            job,
            jobs=self.index.jobs,
            jobs_by_id=self.index.jobs_by_id,
            pattern_index=self.index.pattern_index,
            member_index=self.index.member_index,
            combo_index=self.index.combo_index,
            surface_token_index=self.index.surface_token_index,
            company_index=self.index.company_index,
            member_doc_freq=self.index.member_doc_freq,
        )

    def match_by_job_id(self, job_id: str, *, top_k: int = 10) -> MatchResponse:
        query = self.get_job(job_id)
        if query is None:
            raise KeyError(f"Unknown job_id: {job_id}")
        return self.match(query, top_k=top_k)

    def match(self, query: StructuredJob, *, top_k: int = 10) -> MatchResponse:
        candidates, recall_channels = self._candidate_pool(query)
        results: list[MatchResult] = []
        for candidate_id in candidates:
            if candidate_id == query.job_id:
                continue
            candidate = self.index.jobs_by_id[candidate_id]
            results.append(self._score_candidate(query, candidate, recall_channels.get(candidate_id, set())))
        results.sort(
            key=lambda item: (
                item.total_score,
                item.hard_requirement_score,
                item.requirement_score,
                item.surface_score,
            ),
            reverse=True,
        )
        return MatchResponse(
            query=query,
            total_jobs_indexed=len(self.index.jobs),
            candidate_pool_size=len(candidates),
            matches=results[:top_k],
        )

    def _candidate_pool(self, query: StructuredJob) -> tuple[set[str], dict[str, set[str]]]:
        candidates: set[str] = set()
        recall_channels: dict[str, set[str]] = defaultdict(set)

        if self.feature_config.enable_pattern_recall and query.pattern_signature in self.index.pattern_index:
            for candidate_id in self.index.pattern_index[query.pattern_signature]:
                candidates.add(candidate_id)
                recall_channels[candidate_id].add("pattern_exact")

        must_units = [unit for unit in query.requirement_units if unit.constraint_type == "must_have"]
        hard_units = must_units or [unit for unit in query.requirement_units if unit.constraint_type == "strong_preference"]
        if self.feature_config.enable_hard_unit_recall:
            for unit in hard_units[:6]:
                for member in unit.members:
                    for candidate_id in self.index.member_index.get(member, set()):
                        candidates.add(candidate_id)
                        recall_channels[candidate_id].add("hard_unit")
                    if self.feature_config.enable_hierarchy_recall:
                        for descendant in self.taxonomy.descendants_of(member):
                            for candidate_id in self.index.member_index.get(descendant, set()):
                                candidates.add(candidate_id)
                                recall_channels[candidate_id].add("hierarchy_expand")

        anchor_keys = [key for key in query.recall_keys if "+" not in key and "(" not in key][:4]
        if self.feature_config.enable_combo_recall:
            for left, right in combinations(anchor_keys, 2):
                combo = f"{left}+{right}"
                for candidate_id in self.index.combo_index.get(combo, set()):
                    candidates.add(candidate_id)
                    recall_channels[candidate_id].add("combo")

        if self.feature_config.enable_surface_recall:
            surface_counter: dict[str, int] = defaultdict(int)
            query_surface_tokens = _surface_tokens(
                " ".join(
                    [query.title]
                    + [unit.display_name for unit in query.requirement_units[:8]]
                    + query.pending_surface_texts[:4]
                )
            )
            for token in query_surface_tokens:
                for candidate_id in self.index.surface_token_index.get(token, set()):
                    surface_counter[candidate_id] += 1
            for candidate_id, overlap in sorted(surface_counter.items(), key=lambda item: item[1], reverse=True)[:120]:
                if overlap >= 2:
                    candidates.add(candidate_id)
                    recall_channels[candidate_id].add("surface")

        if self.feature_config.enable_same_company_recall:
            query_company = query.company_name.strip().lower()
            if query_company:
                for candidate_id in self.index.company_index.get(query_company, set()):
                    if candidate_id == query.job_id:
                        continue
                    candidates.add(candidate_id)
                    recall_channels[candidate_id].add("same_company")

        if not candidates:
            for job in self.index.jobs[:200]:
                if job.job_id != query.job_id:
                    candidates.add(job.job_id)
                    recall_channels[job.job_id].add("fallback")

        candidates.discard(query.job_id)
        if self.feature_config.name == "teacher_b_pure_semantic" and len(candidates) > 420:
            channel_weight = {
                "pattern_exact": 4.0,
                "combo": 3.2,
                "hard_unit": 3.0,
                "hierarchy_expand": 2.4,
                "surface": 1.2,
                "same_company": 0.8,
                "fallback": 0.4,
            }
            ranked_candidates = sorted(
                candidates,
                key=lambda candidate_id: (
                    sum(channel_weight.get(channel, 1.0) for channel in recall_channels.get(candidate_id, set())),
                    len(recall_channels.get(candidate_id, set())),
                    candidate_id,
                ),
                reverse=True,
            )
            candidates = set(ranked_candidates[:420])
            recall_channels = defaultdict(set, {candidate_id: recall_channels[candidate_id] for candidate_id in candidates})
        return candidates, recall_channels

    def _score_candidate(
        self,
        query: StructuredJob,
        candidate: StructuredJob,
        recall_channels: set[str],
    ) -> MatchResult:
        matched_units: list[UnitMatchDetail] = []
        band_scores: dict[str, list[tuple[float, float]]] = defaultdict(list)
        total_weight = 0.0
        weighted_score = 0.0

        for unit in query.requirement_units:
            detail = self._score_unit(unit, candidate)
            matched_units.append(detail)
            effective_weight = unit.unit_weight * self._semantic_specificity(unit)
            total_weight += effective_weight
            weighted_score += effective_weight * detail.score
            band_scores[unit.constraint_type].append((effective_weight, detail.score))

        weighted_requirement = weighted_score / total_weight if total_weight else 0.0
        must_score = self._weighted_band_score(band_scores.get("must_have", []))
        strong_score = self._weighted_band_score(band_scores.get("strong_preference", []))
        preferred_score = self._weighted_band_score(band_scores.get("preferred", []))
        background_score = self._weighted_band_score(band_scores.get("background", []))
        semantic_layers = [
            (0.52, must_score),
            (0.2, strong_score),
            (0.18, preferred_score),
            (0.1, background_score),
        ]
        semantic_weight = sum(weight for weight, score in semantic_layers if score is not None)
        semantic_band_score = (
            sum(weight * score for weight, score in semantic_layers if score is not None) / semantic_weight
            if semantic_weight
            else weighted_requirement
        )
        requirement_score = 0.58 * weighted_requirement + 0.42 * semantic_band_score
        hard_requirement_layers = [
            (0.76, must_score),
            (0.24, strong_score),
        ]
        hard_weight = sum(weight for weight, score in hard_requirement_layers if score is not None)
        hard_requirement_score = (
            sum(weight * score for weight, score in hard_requirement_layers if score is not None) / hard_weight
            if hard_weight
            else requirement_score
        )
        surface_score = self._surface_score(query, candidate) if self.feature_config.enable_surface_score else 0.0
        metadata_score = self._metadata_score(query, candidate) if self.feature_config.enable_metadata_score else 0.0
        duplicate_score = self._duplicate_score(query, candidate) if self.feature_config.enable_duplicate_score else 0.0

        total_score = (
            0.64 * requirement_score
            + 0.14 * hard_requirement_score
            + 0.08 * surface_score
            + 0.06 * metadata_score
            + 0.08 * duplicate_score
        )
        if (
            self.feature_config.enable_duplicate_score
            and self.feature_config.duplicate_uses_same_company
            and query.company_name
            and query.company_name == candidate.company_name
            and _norm_title(query.title) == _norm_title(candidate.title)
        ):
            total_score += 0.14
        if hard_requirement_score < 0.45 and (not self.feature_config.allow_duplicate_override or duplicate_score < 0.85):
            total_score *= 0.72
        elif hard_requirement_score < 0.6 and (not self.feature_config.allow_duplicate_override or duplicate_score < 0.85):
            total_score *= 0.86

        missing_critical_units = [
            detail.display_name
            for detail, unit in zip(matched_units, query.requirement_units)
            if unit.constraint_type == "must_have" and detail.score < 0.5
        ]
        explanation = self._explanation(
            query=query,
            candidate=candidate,
            matched_units=matched_units,
            missing_critical_units=missing_critical_units,
            hard_requirement_score=hard_requirement_score,
        )

        return MatchResult(
            candidate_job_id=candidate.job_id,
            total_score=total_score,
            requirement_score=requirement_score,
            hard_requirement_score=hard_requirement_score,
            surface_score=surface_score,
            metadata_score=metadata_score,
            recall_channels=sorted(recall_channels),
            candidate=candidate,
            matched_units=matched_units,
            missing_critical_units=missing_critical_units,
            explanation=explanation,
        )

    def _weighted_band_score(self, items: list[tuple[float, float]]) -> float | None:
        if not items:
            return None
        total_weight = sum(weight for weight, _ in items)
        if total_weight <= 0:
            return None
        return sum(weight * score for weight, score in items) / total_weight

    def _semantic_specificity(self, unit: RequirementUnit) -> float:
        if not unit.members:
            return 1.0
        corpus_size = max(len(self.index.jobs), 1)
        idf_values = []
        for member in unit.members:
            df = self.index.member_doc_freq.get(member, 1)
            idf_values.append(math.log((corpus_size + 1) / (df + 1)) + 1.0)
        avg_idf = sum(idf_values) / len(idf_values)
        normalized = min(max(avg_idf / 3.5, 0.0), 1.0)
        if unit.constraint_type == "must_have":
            return 1.0 + 0.04 * normalized
        if unit.constraint_type == "strong_preference":
            return 1.0 + 0.14 * normalized
        if unit.constraint_type == "preferred":
            return 1.0 + 0.08 * normalized
        return 1.0 + 0.03 * normalized

    def _score_unit(self, unit: RequirementUnit, candidate: StructuredJob) -> UnitMatchDetail:
        member_scores = [
            (
                member,
                self._member_match_score(
                    query_member=member,
                    query_constraint_type=unit.constraint_type,
                    candidate=candidate,
                ),
            )
            for member in unit.members
        ]
        exact_matches = [member for member, score in member_scores if score >= 0.92]
        weak_matches = [member for member, score in member_scores if 0.0 < score < 0.92]
        missing = [member for member, score in member_scores if score <= 0.0]
        member_weight_map = unit.member_weights or {member: 1.0 for member in unit.members}
        total_member_weight = sum(member_weight_map.get(member, 1.0) for member in unit.members) or 1.0
        structure_alignment = self._best_structure_alignment(unit, candidate)

        score = 0.0
        if not unit.members:
            score = 0.0
        elif unit.logic_type == "SINGLE":
            score = max((value for _, value in member_scores), default=0.0)
        elif unit.logic_type == "OR":
            if exact_matches:
                bonus = 0.04 * max(len(exact_matches) - 1, 0)
                score = min(1.08, max((value for _, value in member_scores), default=0.0) + bonus)
            else:
                score = max((value for _, value in member_scores), default=0.0)
        elif unit.logic_type == "AND":
            weighted_hits = sum(member_weight_map.get(member, 1.0) * value for member, value in member_scores)
            missing_weight = sum(member_weight_map.get(member, 1.0) for member, value in member_scores if value <= 0.05)
            score = max((weighted_hits / total_member_weight) - 0.14 * (missing_weight / total_member_weight), 0.0)
        elif unit.logic_type == "AT_LEAST_K":
            k = unit.min_match_count or len(unit.members)
            weighted_member_scores = sorted(
                (member_weight_map.get(member, 1.0) * value for member, value in member_scores),
                reverse=True,
            )
            member_weights = sorted((member_weight_map.get(member, 1.0) for member, _ in member_scores), reverse=True)
            required_weight = sum(member_weights[: max(k, 1)]) or float(max(k, 1))
            score = min(sum(weighted_member_scores[: max(k, 1)]) / required_weight, 1.0)
        elif unit.logic_type == "PARENT_ANY_CHILD":
            score = 1.0 if any(value >= 0.9 for _, value in member_scores) else max((value for _, value in member_scores), default=0.0)
        else:
            score = max((value for _, value in member_scores), default=0.0)
        if unit.logic_type in {"AND", "AT_LEAST_K", "PARENT_ANY_CHILD", "OR"}:
            score *= 0.82 + 0.18 * structure_alignment
        score = min(max(score, 0.0), 1.08)

        return UnitMatchDetail(
            unit_id=unit.unit_id,
            display_name=unit.display_name,
            constraint_type=unit.constraint_type,
            logic_type=unit.logic_type,
            score=score,
            matched_members=exact_matches,
            weak_members=weak_matches,
            missing_members=missing,
        )

    def _member_match_score(
        self,
        *,
        query_member: str,
        query_constraint_type: str,
        candidate: StructuredJob,
    ) -> float:
        best_score = 0.0
        exact_elements = set(candidate.canonical_elements)
        descendants = set(self.taxonomy.descendants_of(query_member))
        ancestors = set(self.taxonomy.ancestors_of(query_member))
        for unit in candidate.requirement_units:
            constraint_alignment = CONSTRAINT_ALIGNMENT.get(query_constraint_type, {}).get(unit.constraint_type, 0.74)
            if query_member in unit.members:
                best_score = max(best_score, 1.0 * constraint_alignment)
                continue
            if descendants and descendants.intersection(unit.members):
                best_score = max(best_score, 1.0 * constraint_alignment)
                continue
            if ancestors and ancestors.intersection(unit.members):
                best_score = max(best_score, 0.18 * constraint_alignment)
        if best_score > 0.0:
            return best_score
        if query_member in exact_elements:
            return CONSTRAINT_ALIGNMENT.get(query_constraint_type, {}).get("background", 0.44)
        if descendants and descendants.intersection(exact_elements):
            return CONSTRAINT_ALIGNMENT.get(query_constraint_type, {}).get("background", 0.44)
        if ancestors and ancestors.intersection(exact_elements):
            return 0.12
        return 0.0

    def _best_structure_alignment(self, query_unit: RequirementUnit, candidate: StructuredJob) -> float:
        best = 0.0
        query_members = set(query_unit.members)
        for candidate_unit in candidate.requirement_units:
            overlap = 0.0
            for member in query_members:
                if member in candidate_unit.members:
                    overlap += 1.0
                    continue
                descendants = self.taxonomy.descendants_of(member)
                if descendants and set(descendants).intersection(candidate_unit.members):
                    overlap += 1.0
                    continue
                ancestors = self.taxonomy.ancestors_of(member)
                if ancestors and set(ancestors).intersection(candidate_unit.members):
                    overlap += 0.18
            overlap /= max(len(query_members), 1)
            if overlap <= 0:
                continue
            logic_alignment = LOGIC_ALIGNMENT.get(query_unit.logic_type, {}).get(candidate_unit.logic_type, 0.76)
            content_alignment = 1.0 if query_unit.content_type == candidate_unit.content_type else 0.82
            score = overlap * (0.58 + 0.22 * logic_alignment + 0.2 * content_alignment)
            best = max(best, score)
        return max(best, 0.72 if len(query_unit.members) == 1 else 0.58)

    def _surface_score(self, query: StructuredJob, candidate: StructuredJob) -> float:
        query_tokens = _surface_tokens(query.title + " " + " ".join(unit.display_name for unit in query.requirement_units[:10]))
        candidate_tokens = _surface_tokens(candidate.title + " " + " ".join(unit.display_name for unit in candidate.requirement_units[:10]))
        token_overlap = _jaccard(query_tokens, candidate_tokens)
        title_overlap = _jaccard(_surface_tokens(query.title), _surface_tokens(candidate.title))
        title_exact = 1.0 if _norm_title(query.title) == _norm_title(candidate.title) else 0.0
        return 0.45 * token_overlap + 0.35 * title_overlap + 0.2 * title_exact

    def _metadata_score(self, query: StructuredJob, candidate: StructuredJob) -> float:
        role = _role_score(query.role_family, candidate.role_family)
        seniority = _seniority_score(query.seniority, candidate.seniority)
        domain = _jaccard(set(query.business_domains), set(candidate.business_domains))
        same_company = 1.0 if query.company_name and query.company_name == candidate.company_name else 0.0
        return 0.34 * role + 0.22 * seniority + 0.18 * domain + 0.26 * same_company

    def _duplicate_score(self, query: StructuredJob, candidate: StructuredJob) -> float:
        same_company = 1.0 if self.feature_config.duplicate_uses_same_company and query.company_name and query.company_name == candidate.company_name else 0.0
        title_exact = 1.0 if _norm_title(query.title) == _norm_title(candidate.title) else 0.0
        title_overlap = _jaccard(_surface_tokens(query.title), _surface_tokens(candidate.title))
        surface_overlap = _jaccard(
            _surface_tokens(" ".join(item.display_name for item in query.requirement_units[:8])),
            _surface_tokens(" ".join(item.display_name for item in candidate.requirement_units[:8])),
        )
        score = 0.35 * same_company + 0.3 * title_exact + 0.2 * title_overlap + 0.15 * surface_overlap
        if same_company and title_exact:
            score = max(score, 0.96)
        return score

    def _explanation(
        self,
        *,
        query: StructuredJob,
        candidate: StructuredJob,
        matched_units: list[UnitMatchDetail],
        missing_critical_units: list[str],
        hard_requirement_score: float,
    ) -> list[str]:
        top_hits = sorted(matched_units, key=lambda item: item.score, reverse=True)[:3]
        lines = [
            f"Role/seniority: {query.role_family}/{query.seniority} -> {candidate.role_family}/{candidate.seniority}.",
            f"Hard-requirement coverage is {hard_requirement_score:.2f}.",
        ]
        if top_hits:
            summaries = []
            for detail in top_hits:
                matched = detail.matched_members or detail.weak_members
                if matched:
                    summaries.append(f"{detail.display_name} => {', '.join(matched[:3])}")
            if summaries:
                lines.append("Best aligned units: " + " | ".join(summaries[:3]))
        if missing_critical_units:
            lines.append("Critical gaps: " + " | ".join(missing_critical_units[:3]))
        return lines
