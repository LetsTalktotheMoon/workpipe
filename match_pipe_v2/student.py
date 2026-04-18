from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .benchmark import BenchmarkCase, evaluate_cases
from .matcher import MatchEngine, TEACHER_CONFIGS, _jaccard, _role_score, _seniority_score
from .models import MatchResult, StructuredJob, UnitMatchDetail
from .taxonomy import DEFAULT_TAXONOMY, Taxonomy


@dataclass(frozen=True)
class LegacyStudentWeights:
    required_overlap: float
    all_overlap: float
    domain_overlap: float
    title_overlap: float
    role_score: float
    seniority_score: float

    def to_dict(self) -> dict:
        return {
            "required_overlap": self.required_overlap,
            "all_overlap": self.all_overlap,
            "domain_overlap": self.domain_overlap,
            "title_overlap": self.title_overlap,
            "role_score": self.role_score,
            "seniority_score": self.seniority_score,
        }


DEFAULT_LEGACY_STUDENT_WEIGHTS = LegacyStudentWeights(
    required_overlap=0.42,
    all_overlap=0.22,
    domain_overlap=0.1,
    title_overlap=0.1,
    role_score=0.1,
    seniority_score=0.06,
)


def _title_tokens(job: StructuredJob) -> set[str]:
    return {token for token in job.title.lower().replace("/", " ").replace("-", " ").split() if len(token) >= 3}


class LegacyStudentMatchEngine(MatchEngine):
    def __init__(
        self,
        jobs: Iterable[StructuredJob],
        *,
        weights: LegacyStudentWeights = DEFAULT_LEGACY_STUDENT_WEIGHTS,
        taxonomy: Taxonomy = DEFAULT_TAXONOMY,
    ):
        super().__init__(jobs, taxonomy=taxonomy)
        self.weights = weights

    def _score_candidate(
        self,
        query: StructuredJob,
        candidate: StructuredJob,
        recall_channels: set[str],
    ) -> MatchResult:
        query_required = {
            member
            for unit in query.requirement_units
            if unit.constraint_type in {"must_have", "strong_preference"}
            for member in unit.members
        }
        candidate_required = {
            member
            for unit in candidate.requirement_units
            if unit.constraint_type in {"must_have", "strong_preference"}
            for member in unit.members
        }
        required_overlap = _jaccard(query_required, candidate_required)
        all_overlap = _jaccard(set(query.canonical_elements), set(candidate.canonical_elements))
        domain_overlap = _jaccard(set(query.business_domains), set(candidate.business_domains))
        title_overlap = _jaccard(_title_tokens(query), _title_tokens(candidate))
        role = _role_score(query.role_family, candidate.role_family)
        seniority = _seniority_score(query.seniority, candidate.seniority)
        total = (
            self.weights.required_overlap * required_overlap
            + self.weights.all_overlap * all_overlap
            + self.weights.domain_overlap * domain_overlap
            + self.weights.title_overlap * title_overlap
            + self.weights.role_score * role
            + self.weights.seniority_score * seniority
        )
        pseudo_unit = UnitMatchDetail(
            unit_id=f"{query.job_id}::legacy_student",
            display_name="flat_student_overlap",
            constraint_type="summary",
            logic_type="FLAT",
            score=required_overlap,
            matched_members=sorted(query_required & candidate_required),
            weak_members=[],
            missing_members=sorted(query_required - candidate_required),
        )
        return MatchResult(
            candidate_job_id=candidate.job_id,
            total_score=total,
            requirement_score=required_overlap,
            hard_requirement_score=required_overlap,
            surface_score=title_overlap,
            metadata_score=(role + seniority + domain_overlap) / 3.0,
            recall_channels=sorted(recall_channels),
            candidate=candidate,
            matched_units=[pseudo_unit],
            missing_critical_units=[],
            explanation=[
                f"Legacy flat overlap required={required_overlap:.2f} all={all_overlap:.2f}.",
                f"Metadata role={role:.2f} seniority={seniority:.2f} domain={domain_overlap:.2f}.",
            ],
        )


def distill_legacy_student_weights(
    jobs: Iterable[StructuredJob],
    train_cases: Iterable[BenchmarkCase],
    *,
    taxonomy: Taxonomy = DEFAULT_TAXONOMY,
) -> LegacyStudentWeights:
    jobs_list = list(jobs)
    cases = list(train_cases)
    if not cases:
        return DEFAULT_LEGACY_STUDENT_WEIGHTS

    sampled_cases = sorted(cases, key=lambda item: item.query_id)[:24]
    candidates = [
        DEFAULT_LEGACY_STUDENT_WEIGHTS,
        LegacyStudentWeights(0.5, 0.18, 0.08, 0.08, 0.1, 0.06),
        LegacyStudentWeights(0.46, 0.18, 0.08, 0.14, 0.08, 0.06),
        LegacyStudentWeights(0.4, 0.26, 0.08, 0.1, 0.1, 0.06),
        LegacyStudentWeights(0.38, 0.24, 0.12, 0.1, 0.1, 0.06),
    ]
    best_score = -1.0
    best_weights = DEFAULT_LEGACY_STUDENT_WEIGHTS
    for weights in candidates:
        total = sum(weights.to_dict().values())
        normalized = LegacyStudentWeights(*(value / total for value in weights.to_dict().values()))
        engine = LegacyStudentMatchEngine(jobs_list, weights=normalized, taxonomy=taxonomy)
        metrics = evaluate_cases(engine, sampled_cases, top_k=5, max_misses=0)
        score = metrics.hit_at_1 + 0.5 * metrics.hit_at_3 + 0.25 * metrics.mean_reciprocal_rank
        if score > best_score:
            best_score = score
            best_weights = normalized
    return best_weights


@dataclass(frozen=True)
class TeacherTrace:
    query_id: str
    candidate_id: str
    teacher_rank: int
    teacher_total_score: float
    teacher_requirement_score: float
    teacher_hard_requirement_score: float
    label: str
    student_features: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "query_id": self.query_id,
            "candidate_id": self.candidate_id,
            "teacher_rank": self.teacher_rank,
            "teacher_total_score": round(self.teacher_total_score, 4),
            "teacher_requirement_score": round(self.teacher_requirement_score, 4),
            "teacher_hard_requirement_score": round(self.teacher_hard_requirement_score, 4),
            "label": self.label,
            "student_features": {key: round(value, 4) for key, value in self.student_features.items()},
        }


@dataclass(frozen=True)
class StudentWeights:
    must_overlap: float
    preferred_overlap: float
    background_overlap: float
    canonical_overlap: float
    hierarchy_overlap: float
    logic_overlap: float
    domain_overlap: float
    role_score: float
    seniority_score: float

    def to_dict(self) -> dict:
        return {
            "must_overlap": self.must_overlap,
            "preferred_overlap": self.preferred_overlap,
            "background_overlap": self.background_overlap,
            "canonical_overlap": self.canonical_overlap,
            "hierarchy_overlap": self.hierarchy_overlap,
            "logic_overlap": self.logic_overlap,
            "domain_overlap": self.domain_overlap,
            "role_score": self.role_score,
            "seniority_score": self.seniority_score,
        }


DEFAULT_STUDENT_WEIGHTS = StudentWeights(
    must_overlap=0.34,
    preferred_overlap=0.15,
    background_overlap=0.04,
    canonical_overlap=0.17,
    hierarchy_overlap=0.08,
    logic_overlap=0.08,
    domain_overlap=0.06,
    role_score=0.05,
    seniority_score=0.03,
)


def _member_strength(query_member: str, candidate: StructuredJob, taxonomy: Taxonomy) -> float:
    candidate_members = set(candidate.expanded_elements)
    candidate_canonical = set(candidate.canonical_elements)
    if query_member in candidate_members or query_member in candidate_canonical:
        return 1.0
    descendants = set(taxonomy.descendants_of(query_member))
    if descendants & candidate_members or descendants & candidate_canonical:
        return 1.0
    ancestors = set(taxonomy.ancestors_of(query_member))
    if ancestors & candidate_members or ancestors & candidate_canonical:
        return 0.18
    return 0.0


def _light_unit_score(query_unit, candidate: StructuredJob, taxonomy: Taxonomy) -> float:
    if not query_unit.members:
        return 0.0
    member_weight_map = query_unit.member_weights or {member: 1.0 for member in query_unit.members}
    total_weight = sum(member_weight_map.get(member, 1.0) for member in query_unit.members) or 1.0
    scores = [(member, _member_strength(member, candidate, taxonomy)) for member in query_unit.members]
    if query_unit.logic_type == "SINGLE":
        return max((score for _, score in scores), default=0.0)
    if query_unit.logic_type == "OR":
        top = max((score for _, score in scores), default=0.0)
        exact_count = sum(1 for _, score in scores if score >= 0.95)
        return min(top + 0.03 * max(exact_count - 1, 0), 1.0)
    if query_unit.logic_type == "AND":
        weighted_hits = sum(member_weight_map.get(member, 1.0) * score for member, score in scores)
        missing_weight = sum(member_weight_map.get(member, 1.0) for member, score in scores if score <= 0.05)
        return max((weighted_hits / total_weight) - 0.12 * (missing_weight / total_weight), 0.0)
    if query_unit.logic_type == "AT_LEAST_K":
        k = max(query_unit.min_match_count or len(query_unit.members), 1)
        weighted_scores = sorted((member_weight_map.get(member, 1.0) * score for member, score in scores), reverse=True)
        member_weights = sorted((member_weight_map.get(member, 1.0) for member, _ in scores), reverse=True)
        required_weight = sum(member_weights[:k]) or float(k)
        return min(sum(weighted_scores[:k]) / required_weight, 1.0)
    if query_unit.logic_type == "PARENT_ANY_CHILD":
        return 1.0 if any(score >= 0.95 for _, score in scores) else max((score for _, score in scores), default=0.0)
    return max((score for _, score in scores), default=0.0)


def _weighted_unit_band(query: StructuredJob, candidate: StructuredJob, taxonomy: Taxonomy, constraints: set[str]) -> float:
    selected = [unit for unit in query.requirement_units if unit.constraint_type in constraints]
    if not selected:
        return 0.0
    total_weight = 0.0
    weighted = 0.0
    for unit in selected:
        unit_weight = unit.unit_weight
        total_weight += unit_weight
        weighted += unit_weight * _light_unit_score(unit, candidate, taxonomy)
    return weighted / total_weight if total_weight else 0.0


def _hierarchy_overlap(query: StructuredJob, candidate: StructuredJob, taxonomy: Taxonomy) -> float:
    if not query.canonical_elements:
        return 0.0
    hits = 0.0
    candidate_canonical = set(candidate.canonical_elements)
    candidate_expanded = set(candidate.expanded_elements)
    for element in query.canonical_elements:
        if element in candidate_canonical or element in candidate_expanded:
            hits += 1.0
            continue
        descendants = set(taxonomy.descendants_of(element))
        if descendants & candidate_expanded:
            hits += 1.0
            continue
        ancestors = set(taxonomy.ancestors_of(element))
        if ancestors & candidate_expanded:
            hits += 0.18
    return hits / max(len(query.canonical_elements), 1)


def _logic_overlap(query: StructuredJob, candidate: StructuredJob) -> float:
    query_logic = {unit.logic_type for unit in query.requirement_units if unit.logic_type != "SINGLE"}
    candidate_logic = {unit.logic_type for unit in candidate.requirement_units if unit.logic_type != "SINGLE"}
    if not query_logic and not candidate_logic:
        return 1.0
    if not query_logic or not candidate_logic:
        return 0.0
    return _jaccard(query_logic, candidate_logic)


def student_feature_vector(query: StructuredJob, candidate: StructuredJob, taxonomy: Taxonomy = DEFAULT_TAXONOMY) -> dict[str, float]:
    return {
        "must_overlap": _weighted_unit_band(query, candidate, taxonomy, {"must_have"}),
        "preferred_overlap": _weighted_unit_band(query, candidate, taxonomy, {"strong_preference", "preferred"}),
        "background_overlap": _weighted_unit_band(query, candidate, taxonomy, {"background"}),
        "canonical_overlap": _jaccard(set(query.canonical_elements), set(candidate.canonical_elements)),
        "hierarchy_overlap": _hierarchy_overlap(query, candidate, taxonomy),
        "logic_overlap": _logic_overlap(query, candidate),
        "domain_overlap": _jaccard(set(query.business_domains), set(candidate.business_domains)),
        "role_score": _role_score(query.role_family, candidate.role_family),
        "seniority_score": _seniority_score(query.seniority, candidate.seniority),
    }


class StudentMatchEngine(MatchEngine):
    def __init__(
        self,
        jobs: Iterable[StructuredJob],
        *,
        weights: StudentWeights = DEFAULT_STUDENT_WEIGHTS,
        taxonomy: Taxonomy = DEFAULT_TAXONOMY,
    ):
        super().__init__(
            jobs,
            taxonomy=taxonomy,
            feature_config=TEACHER_CONFIGS["teacher_b_pure_semantic"],
        )
        self.weights = weights

    def _score_candidate(
        self,
        query: StructuredJob,
        candidate: StructuredJob,
        recall_channels: set[str],
    ) -> MatchResult:
        features = student_feature_vector(query, candidate, self.taxonomy)
        total = sum(getattr(self.weights, key) * value for key, value in features.items())
        requirement_score = 0.66 * features["must_overlap"] + 0.22 * features["preferred_overlap"] + 0.12 * features["canonical_overlap"]
        hard_requirement_score = 0.82 * features["must_overlap"] + 0.18 * features["logic_overlap"]
        if hard_requirement_score < 0.42:
            total *= 0.8
        elif hard_requirement_score < 0.58:
            total *= 0.9
        pseudo_unit = UnitMatchDetail(
            unit_id=f"{query.job_id}::semantic_student",
            display_name="semantic_student_summary",
            constraint_type="summary",
            logic_type="SEMANTIC",
            score=requirement_score,
            matched_members=[],
            weak_members=[],
            missing_members=[],
        )
        explanation = [
            f"Semantic student must={features['must_overlap']:.2f} pref={features['preferred_overlap']:.2f} canonical={features['canonical_overlap']:.2f}.",
            f"Logic={features['logic_overlap']:.2f} hierarchy={features['hierarchy_overlap']:.2f} domain={features['domain_overlap']:.2f}.",
        ]
        return MatchResult(
            candidate_job_id=candidate.job_id,
            total_score=total,
            requirement_score=requirement_score,
            hard_requirement_score=hard_requirement_score,
            surface_score=0.0,
            metadata_score=(features["role_score"] + features["seniority_score"] + features["domain_overlap"]) / 3.0,
            recall_channels=sorted(recall_channels),
            candidate=candidate,
            matched_units=[pseudo_unit],
            missing_critical_units=[],
            explanation=explanation,
        )


def generate_teacher_traces(
    teacher: MatchEngine,
    cases: Iterable[BenchmarkCase],
    *,
    top_k: int = 5,
    taxonomy: Taxonomy = DEFAULT_TAXONOMY,
) -> list[TeacherTrace]:
    traces: list[TeacherTrace] = []
    for case in cases:
        response = teacher.match_by_job_id(case.query_id, top_k=max(top_k, 8))
        seen = set()
        for rank, match in enumerate(response.matches[:top_k], start=1):
            seen.add(match.candidate_job_id)
            traces.append(
                TeacherTrace(
                    query_id=case.query_id,
                    candidate_id=match.candidate_job_id,
                    teacher_rank=rank,
                    teacher_total_score=match.total_score,
                    teacher_requirement_score=match.requirement_score,
                    teacher_hard_requirement_score=match.hard_requirement_score,
                    label="positive" if match.candidate_job_id in case.positive_ids else "teacher_topk",
                    student_features=student_feature_vector(response.query, match.candidate, taxonomy),
                )
            )
        for positive_id in case.positive_ids:
            if positive_id in seen:
                continue
            candidate = teacher.get_job(positive_id)
            query = teacher.get_job(case.query_id)
            if candidate is None or query is None:
                continue
            student_features = student_feature_vector(query, candidate, taxonomy)
            scored = teacher._score_candidate(query, candidate, {"positive_recheck"})
            traces.append(
                TeacherTrace(
                    query_id=case.query_id,
                    candidate_id=positive_id,
                    teacher_rank=top_k + 1,
                    teacher_total_score=scored.total_score,
                    teacher_requirement_score=scored.requirement_score,
                    teacher_hard_requirement_score=scored.hard_requirement_score,
                    label="positive",
                    student_features=student_features,
                )
            )
    return traces


def _teacher_trace_alignment(weights: StudentWeights, traces: list[TeacherTrace]) -> float:
    if not traces:
        return 0.0
    by_query: dict[str, list[TeacherTrace]] = {}
    for trace in traces:
        by_query.setdefault(trace.query_id, []).append(trace)
    aligned = 0.0
    total = 0.0
    for items in by_query.values():
        ranked = sorted(items, key=lambda item: item.teacher_rank)
        teacher_best = ranked[0].candidate_id
        student_best = max(
            items,
            key=lambda item: sum(getattr(weights, key) * value for key, value in item.student_features.items()),
        ).candidate_id
        aligned += 1.0 if student_best == teacher_best else 0.0
        total += 1.0
    return aligned / max(total, 1.0)


def distill_student_weights(
    jobs: Iterable[StructuredJob],
    train_cases: Iterable[BenchmarkCase],
    *,
    taxonomy: Taxonomy = DEFAULT_TAXONOMY,
    teacher: MatchEngine | None = None,
) -> StudentWeights:
    jobs_list = list(jobs)
    cases = list(train_cases)
    if not cases:
        return DEFAULT_STUDENT_WEIGHTS

    teacher = teacher or MatchEngine(jobs_list, taxonomy=taxonomy, feature_config=TEACHER_CONFIGS["teacher_b_pure_semantic"])
    sampled_cases = sorted(cases, key=lambda item: item.query_id)[:28]
    traces = generate_teacher_traces(teacher, sampled_cases, taxonomy=taxonomy)
    candidates = [
        DEFAULT_STUDENT_WEIGHTS,
        StudentWeights(0.36, 0.14, 0.04, 0.16, 0.08, 0.08, 0.06, 0.05, 0.03),
        StudentWeights(0.38, 0.12, 0.04, 0.17, 0.09, 0.08, 0.05, 0.04, 0.03),
        StudentWeights(0.34, 0.16, 0.04, 0.16, 0.08, 0.09, 0.06, 0.04, 0.03),
        StudentWeights(0.32, 0.18, 0.05, 0.17, 0.08, 0.07, 0.06, 0.04, 0.03),
        StudentWeights(0.4, 0.12, 0.03, 0.16, 0.08, 0.08, 0.05, 0.05, 0.03),
    ]
    best_score = -1.0
    best_weights = DEFAULT_STUDENT_WEIGHTS
    for weights in candidates:
        total = sum(weights.to_dict().values())
        normalized = StudentWeights(*(value / total for value in weights.to_dict().values()))
        engine = StudentMatchEngine(jobs_list, weights=normalized, taxonomy=taxonomy)
        metrics = evaluate_cases(engine, sampled_cases, top_k=5, max_misses=0)
        agreement = _teacher_trace_alignment(normalized, traces)
        score = (
            0.54 * metrics.hit_at_1
            + 0.24 * metrics.hit_at_3
            + 0.12 * metrics.mean_reciprocal_rank
            + 0.1 * agreement
        )
        if score > best_score:
            best_score = score
            best_weights = normalized
    return best_weights
