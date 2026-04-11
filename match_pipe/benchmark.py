from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
import time
from typing import Iterable

from .matcher import MatchEngine
from .models import StructuredJob


def _norm_title(text: str) -> str:
    return " ".join((text or "").lower().replace("/", " ").replace("-", " ").split())


@dataclass(frozen=True)
class BenchmarkCase:
    query_id: str
    positive_ids: tuple[str, ...]
    pool_name: str
    company_name: str
    normalized_title: str
    rationale: str
    category: str = ""
    distractor_ids: tuple[str, ...] = ()


@dataclass
class BenchmarkMetrics:
    case_count: int
    hit_at_1: float
    hit_at_3: float
    hit_at_5: float
    mean_reciprocal_rank: float
    median_positive_rank: float
    avg_runtime_ms: float
    avg_candidate_pool_size: float
    misses: list[dict]

    def to_dict(self) -> dict:
        return {
            "case_count": self.case_count,
            "hit_at_1": round(self.hit_at_1, 4),
            "hit_at_3": round(self.hit_at_3, 4),
            "hit_at_5": round(self.hit_at_5, 4),
            "mean_reciprocal_rank": round(self.mean_reciprocal_rank, 4),
            "median_positive_rank": round(self.median_positive_rank, 2),
            "avg_runtime_ms": round(self.avg_runtime_ms, 2),
            "avg_candidate_pool_size": round(self.avg_candidate_pool_size, 2),
            "misses": self.misses,
        }


@dataclass
class BenchmarkSuite:
    standard_cases: list[BenchmarkCase]
    hard_cases: list[BenchmarkCase]
    rebuilt_hard_cases: list[BenchmarkCase]

    def to_dict(self) -> dict:
        return {
            "standard_case_count": len(self.standard_cases),
            "hard_case_count": len(self.hard_cases),
            "rebuilt_hard_case_count": len(self.rebuilt_hard_cases),
        }


def _unit_signature(job: StructuredJob) -> set[tuple[str, str, tuple[str, ...]]]:
    return {
        (unit.constraint_type, unit.logic_type, tuple(sorted(unit.members)))
        for unit in job.requirement_units
        if unit.members
    }


def _must_signature(job: StructuredJob) -> set[tuple[str, str, tuple[str, ...]]]:
    return {
        (unit.constraint_type, unit.logic_type, tuple(sorted(unit.members)))
        for unit in job.requirement_units
        if unit.members and unit.constraint_type == "must_have"
    }


def _semantic_overlap(left: StructuredJob, right: StructuredJob) -> float:
    left_all = _unit_signature(left)
    right_all = _unit_signature(right)
    left_must = _must_signature(left)
    right_must = _must_signature(right)
    all_overlap = _jaccard(left_all, right_all)
    must_overlap = _jaccard(left_must, right_must)
    return 0.62 * must_overlap + 0.38 * all_overlap


def _jaccard(left: set, right: set) -> float:
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _logic_types(job: StructuredJob) -> set[str]:
    return {unit.logic_type for unit in job.requirement_units if unit.logic_type != "SINGLE"}


def _has_parent_child(job: StructuredJob) -> bool:
    return any(unit.logic_type == "PARENT_ANY_CHILD" or unit.hierarchy_level in {"parent", "child", "mixed"} for unit in job.requirement_units)


def _has_must_and_preferred(job: StructuredJob) -> bool:
    constraint_types = {unit.constraint_type for unit in job.requirement_units}
    return "must_have" in constraint_types and "preferred" in constraint_types


def build_benchmark_suite(jobs: Iterable[StructuredJob]) -> BenchmarkSuite:
    job_list = list(jobs)
    by_company_title: dict[tuple[str, str], list[StructuredJob]] = defaultdict(list)
    title_frequency: Counter[str] = Counter()
    jobs_by_id = {job.job_id: job for job in job_list}
    for job in job_list:
        normalized_title = _norm_title(job.title)
        title_frequency[normalized_title] += 1
        by_company_title[(job.company_name.lower().strip(), normalized_title)].append(job)

    standard_cases: list[BenchmarkCase] = []
    hard_cases: list[BenchmarkCase] = []
    for (company_key, normalized_title), group in by_company_title.items():
        if len(group) < 2:
            continue
        positive_ids = tuple(sorted(job.job_id for job in group))
        for job in group:
            others = tuple(item for item in positive_ids if item != job.job_id)
            if not others:
                continue
            standard_cases.append(
                BenchmarkCase(
                    query_id=job.job_id,
                    positive_ids=others,
                    pool_name="standard",
                    company_name=job.company_name,
                    normalized_title=normalized_title,
                    rationale="Same-company same-title JD duplicates/reposts form the standard positive group.",
                )
            )
            if title_frequency[normalized_title] >= 8:
                hard_cases.append(
                    BenchmarkCase(
                        query_id=job.job_id,
                        positive_ids=others,
                        pool_name="hard",
                        company_name=job.company_name,
                        normalized_title=normalized_title,
                        rationale="Generic title with many cross-company distractors; positives stay same-company same-title.",
                        category="legacy_duplicate_hard",
                    )
                )

    standard_cases.sort(key=lambda item: (item.normalized_title, item.company_name, item.query_id))
    hard_cases.sort(key=lambda item: (item.normalized_title, item.company_name, item.query_id))
    rebuilt_hard_cases = build_reconstructed_hard_pool(job_list, title_frequency=title_frequency)
    return BenchmarkSuite(standard_cases=standard_cases, hard_cases=hard_cases, rebuilt_hard_cases=rebuilt_hard_cases)


def build_reconstructed_hard_pool(
    jobs: Iterable[StructuredJob],
    *,
    title_frequency: Counter[str] | None = None,
) -> list[BenchmarkCase]:
    job_list = list(jobs)
    title_frequency = title_frequency or Counter(_norm_title(job.title) for job in job_list)
    jobs_by_id = {job.job_id: job for job in job_list}
    cross_company_by_pattern: dict[str, list[StructuredJob]] = defaultdict(list)
    by_company: dict[str, list[StructuredJob]] = defaultdict(list)
    by_title: dict[str, list[StructuredJob]] = defaultdict(list)
    by_role: dict[str, list[StructuredJob]] = defaultdict(list)
    by_domain: dict[str, list[StructuredJob]] = defaultdict(list)
    for job in job_list:
        cross_company_by_pattern[job.pattern_signature].append(job)
        by_company[job.company_name.lower().strip()].append(job)
        by_title[_norm_title(job.title)].append(job)
        by_role[job.role_family].append(job)
        for domain in job.business_domains:
            by_domain[domain].append(job)

    category_limits = {
        "cross_company_structure_similar": 8,
        "same_company_structure_different": 6,
        "title_same_business_different": 6,
        "parent_child_conflict": 6,
        "or_and_mixed": 6,
        "must_vs_preferred_confusing": 6,
    }
    selected_counts: Counter[str] = Counter()
    cases: list[BenchmarkCase] = []
    seen_queries: set[tuple[str, str]] = set()

    def semantic_candidate_universe(query: StructuredJob) -> list[StructuredJob]:
        candidates: dict[str, StructuredJob] = {}
        for item in by_role.get(query.role_family, []):
            if item.job_id != query.job_id:
                candidates[item.job_id] = item
        for domain in query.business_domains:
            for item in by_domain.get(domain, []):
                if item.job_id != query.job_id:
                    candidates[item.job_id] = item
        for item in by_title.get(_norm_title(query.title), []):
            if item.job_id != query.job_id:
                candidates[item.job_id] = item
        if len(candidates) < 30:
            for item in job_list[:80]:
                if item.job_id != query.job_id:
                    candidates[item.job_id] = item
        return list(candidates.values())

    def add_case(category: str, query: StructuredJob, positives: list[StructuredJob], rationale: str, distractors: list[str]) -> None:
        key = (category, query.job_id)
        if selected_counts[category] >= category_limits[category] or key in seen_queries:
            return
        positive_ids = tuple(sorted({item.job_id for item in positives if item.job_id != query.job_id}))
        if not positive_ids:
            return
        seen_queries.add(key)
        selected_counts[category] += 1
        cases.append(
            BenchmarkCase(
                query_id=query.job_id,
                positive_ids=positive_ids,
                pool_name="rebuilt_hard",
                company_name=query.company_name,
                normalized_title=_norm_title(query.title),
                rationale=rationale,
                category=category,
                distractor_ids=tuple(sorted(set(distractors))),
            )
        )

    for query in job_list:
        pattern_peers = [
            item for item in cross_company_by_pattern.get(query.pattern_signature, [])
            if item.company_name != query.company_name and item.job_id != query.job_id
        ]
        if pattern_peers:
            add_case(
                "cross_company_structure_similar",
                query,
                pattern_peers,
                "Cross-company jobs share the same requirement-unit pattern signature.",
                [],
            )

        same_company_distractors = [
            item for item in by_company.get(query.company_name.lower().strip(), [])
            if item.job_id != query.job_id and _semantic_overlap(query, item) <= 0.34
        ]
        if pattern_peers and same_company_distractors:
            add_case(
                "same_company_structure_different",
                query,
                pattern_peers,
                "Cross-company semantic twins exist while same-company jobs are structurally different distractors.",
                [item.job_id for item in same_company_distractors[:5]],
            )

        title_distractors = [
            item
            for item in by_title.get(_norm_title(query.title), [])
            if item.job_id != query.job_id
            and item.company_name != query.company_name
            and set(item.business_domains) != set(query.business_domains)
            and _semantic_overlap(query, item) <= 0.36
        ]
        candidate_universe = semantic_candidate_universe(query)
        semantic_cross_company = [
            item
            for item in candidate_universe
            if item.job_id != query.job_id
            and item.company_name != query.company_name
            and _semantic_overlap(query, item) >= 0.72
        ]
        if title_distractors and semantic_cross_company:
            add_case(
                "title_same_business_different",
                query,
                semantic_cross_company[:3],
                "Same normalized title appears across companies with different business/requirement structure.",
                [item.job_id for item in title_distractors[:5]],
            )

        if _has_parent_child(query):
            parent_child_positives = [
                item for item in semantic_cross_company
                if _has_parent_child(item)
            ]
            parent_only_distractors = [
                item for item in candidate_universe
                if item.job_id != query.job_id
                and item.company_name != query.company_name
                and any(member in set(item.expanded_elements) for member in query.canonical_elements)
                and _semantic_overlap(query, item) < 0.55
            ]
            if parent_child_positives:
                add_case(
                    "parent_child_conflict",
                    query,
                    parent_child_positives[:3],
                    "Parent/child hierarchy must be resolved correctly; sibling/parent-only distractors exist.",
                    [item.job_id for item in parent_only_distractors[:5]],
                )

        if {"OR", "AND"} <= _logic_types(query):
            logic_positives = [
                item for item in semantic_cross_company
                if {"OR", "AND"} <= _logic_types(item)
            ]
            if logic_positives:
                add_case(
                    "or_and_mixed",
                    query,
                    logic_positives[:3],
                    "Query contains mixed OR/AND logic and should match jobs with the same logical structure.",
                    [],
                )

        if _has_must_and_preferred(query):
            must_positives = [
                item for item in semantic_cross_company
                if _has_must_and_preferred(item) and _jaccard(_must_signature(query), _must_signature(item)) >= 0.75
            ]
            preferred_distractors = [
                item
                for item in candidate_universe
                if item.job_id != query.job_id
                and _has_must_and_preferred(item)
                and _jaccard(_must_signature(query), _must_signature(item)) < 0.4
                and _jaccard(_unit_signature(query) - _must_signature(query), _unit_signature(item) - _must_signature(item)) >= 0.45
            ]
            if must_positives:
                add_case(
                    "must_vs_preferred_confusing",
                    query,
                    must_positives[:3],
                    "Must-have alignment should outrank preferred-only overlap.",
                    [item.job_id for item in preferred_distractors[:5]],
                )

    cases.sort(key=lambda item: (item.category, item.company_name, item.query_id))
    return cases


def audit_legacy_benchmark(suite: BenchmarkSuite, jobs: Iterable[StructuredJob]) -> dict:
    jobs_by_id = {job.job_id: job for job in jobs}

    def audit_cases(cases: list[BenchmarkCase]) -> dict:
        case_count = len(cases) or 1
        positive_pairs = 0
        same_company = 0
        exact_title = 0
        for case in cases:
            query = jobs_by_id[case.query_id]
            for positive_id in case.positive_ids:
                positive_pairs += 1
                positive = jobs_by_id[positive_id]
                if positive.company_name == query.company_name:
                    same_company += 1
                if _norm_title(positive.title) == _norm_title(query.title):
                    exact_title += 1
        return {
            "case_count": len(cases),
            "positive_pair_count": positive_pairs,
            "same_company_positive_ratio": round(same_company / max(positive_pairs, 1), 4),
            "exact_title_positive_ratio": round(exact_title / max(positive_pairs, 1), 4),
        }

    return {
        "standard": audit_cases(suite.standard_cases),
        "hard": audit_cases(suite.hard_cases),
        "rebuilt_hard": audit_cases(suite.rebuilt_hard_cases),
    }


def split_cases(cases: Iterable[BenchmarkCase], *, train_ratio: float = 0.8) -> tuple[list[BenchmarkCase], list[BenchmarkCase]]:
    train: list[BenchmarkCase] = []
    test: list[BenchmarkCase] = []
    for case in cases:
        digest = hashlib.md5(case.query_id.encode("utf-8")).hexdigest()
        bucket = int(digest[:8], 16) / 0xFFFFFFFF
        if bucket < train_ratio:
            train.append(case)
        else:
            test.append(case)
    return train, test


def evaluate_cases(
    engine: MatchEngine,
    cases: Iterable[BenchmarkCase],
    *,
    top_k: int = 5,
    max_misses: int = 12,
) -> BenchmarkMetrics:
    case_list = list(cases)
    hit1 = 0
    hit3 = 0
    hit5 = 0
    reciprocal_rank_sum = 0.0
    positive_ranks: list[int] = []
    runtimes_ms: list[float] = []
    candidate_pool_sizes: list[int] = []
    misses: list[dict] = []

    for case in case_list:
        start = time.perf_counter()
        response = engine.match_by_job_id(case.query_id, top_k=max(top_k, 10))
        runtimes_ms.append((time.perf_counter() - start) * 1000.0)
        candidate_pool_sizes.append(response.candidate_pool_size)

        ranked_ids = [item.candidate_job_id for item in response.matches]
        best_rank = None
        for index, candidate_id in enumerate(ranked_ids, start=1):
            if candidate_id in case.positive_ids:
                best_rank = index
                break
        if best_rank is not None:
            positive_ranks.append(best_rank)
            reciprocal_rank_sum += 1.0 / best_rank
            if best_rank <= 1:
                hit1 += 1
            if best_rank <= 3:
                hit3 += 1
            if best_rank <= 5:
                hit5 += 1
        else:
            positive_ranks.append(999)
            if len(misses) < max_misses:
                misses.append(
                    {
                        "query_id": case.query_id,
                        "company_name": case.company_name,
                        "normalized_title": case.normalized_title,
                        "positive_ids": list(case.positive_ids),
                        "top_candidates": ranked_ids[:5],
                        "rationale": case.rationale,
                    }
                )

    count = len(case_list) or 1
    sorted_ranks = sorted(positive_ranks)
    median_rank = sorted_ranks[len(sorted_ranks) // 2] if sorted_ranks else 999
    return BenchmarkMetrics(
        case_count=len(case_list),
        hit_at_1=hit1 / count,
        hit_at_3=hit3 / count,
        hit_at_5=hit5 / count,
        mean_reciprocal_rank=reciprocal_rank_sum / count,
        median_positive_rank=float(median_rank),
        avg_runtime_ms=sum(runtimes_ms) / max(len(runtimes_ms), 1),
        avg_candidate_pool_size=sum(candidate_pool_sizes) / max(len(candidate_pool_sizes), 1),
        misses=misses,
    )
