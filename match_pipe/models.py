from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class CanonicalDefinition:
    canonical_id: str
    canonical_name: str
    content_type: str
    aliases: tuple[str, ...]
    parent_id: str | None = None


@dataclass
class JobDocument:
    job_id: str
    company_name: str
    title: str
    raw_text: str
    source_kind: str
    metadata: dict[str, Any] = field(default_factory=dict)
    row: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "company_name": self.company_name,
            "title": self.title,
            "source_kind": self.source_kind,
            "metadata": self.metadata,
        }


@dataclass
class SurfaceElement:
    text: str
    source_section: str
    constraint_type: str
    type_hint: str
    canonical_ids: list[str] = field(default_factory=list)
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RequirementUnit:
    unit_id: str
    content_type: str
    constraint_type: str
    logic_type: str
    hierarchy_level: str
    unit_weight: float
    members: list[str]
    display_name: str
    source_section: str
    member_weights: dict[str, float] = field(default_factory=dict)
    source_evidence: list[str] = field(default_factory=list)
    min_match_count: int | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["unit_weight"] = round(self.unit_weight, 3)
        return payload


@dataclass
class StructuredJob:
    job_id: str
    company_name: str
    title: str
    source_kind: str
    raw_text: str
    role_family: str
    seniority: str
    business_domains: list[str]
    canonical_elements: list[str]
    expanded_elements: list[str]
    surface_elements: list[SurfaceElement]
    requirement_units: list[RequirementUnit]
    pattern_signature: str
    recall_keys: list[str]
    pending_surface_texts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "company_name": self.company_name,
            "title": self.title,
            "source_kind": self.source_kind,
            "role_family": self.role_family,
            "seniority": self.seniority,
            "business_domains": self.business_domains,
            "canonical_elements": self.canonical_elements,
            "expanded_elements": self.expanded_elements,
            "surface_elements": [item.to_dict() for item in self.surface_elements],
            "requirement_units": [item.to_dict() for item in self.requirement_units],
            "pattern_signature": self.pattern_signature,
            "recall_keys": self.recall_keys,
            "pending_surface_texts": self.pending_surface_texts,
            "metadata": self.metadata,
        }


@dataclass
class UnitMatchDetail:
    unit_id: str
    display_name: str
    constraint_type: str
    logic_type: str
    score: float
    matched_members: list[str] = field(default_factory=list)
    weak_members: list[str] = field(default_factory=list)
    missing_members: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["score"] = round(self.score, 3)
        return payload


@dataclass
class MatchResult:
    candidate_job_id: str
    total_score: float
    requirement_score: float
    hard_requirement_score: float
    surface_score: float
    metadata_score: float
    recall_channels: list[str]
    candidate: StructuredJob
    matched_units: list[UnitMatchDetail]
    missing_critical_units: list[str]
    explanation: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_job_id": self.candidate_job_id,
            "total_score": round(self.total_score, 4),
            "requirement_score": round(self.requirement_score, 4),
            "hard_requirement_score": round(self.hard_requirement_score, 4),
            "surface_score": round(self.surface_score, 4),
            "metadata_score": round(self.metadata_score, 4),
            "recall_channels": self.recall_channels,
            "candidate": {
                "job_id": self.candidate.job_id,
                "company_name": self.candidate.company_name,
                "title": self.candidate.title,
                "role_family": self.candidate.role_family,
                "seniority": self.candidate.seniority,
            },
            "matched_units": [item.to_dict() for item in self.matched_units],
            "missing_critical_units": self.missing_critical_units,
            "explanation": self.explanation,
        }


@dataclass
class MatchResponse:
    query: StructuredJob
    total_jobs_indexed: int
    candidate_pool_size: int
    matches: list[MatchResult]

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": {
                "job_id": self.query.job_id,
                "company_name": self.query.company_name,
                "title": self.query.title,
                "role_family": self.query.role_family,
                "seniority": self.query.seniority,
                "pattern_signature": self.query.pattern_signature,
                "recall_keys": self.query.recall_keys,
            },
            "total_jobs_indexed": self.total_jobs_indexed,
            "candidate_pool_size": self.candidate_pool_size,
            "matches": [item.to_dict() for item in self.matches],
        }
