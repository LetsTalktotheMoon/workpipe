from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .matcher import MatchFeatureConfig, TEACHER_CONFIGS


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class FrozenTeacherManifest:
    version: str
    config_name: str
    report_path: str
    label_pool_path: str
    boundary_pool_path: str
    output_protocol: dict[str, str]
    dynamic_ingest_policy: dict[str, str]
    freeze_rule_layers: tuple[str, ...]
    growth_knowledge_layers: tuple[str, ...]
    allowed_mutations: tuple[str, ...]
    disallowed_mutations: tuple[str, ...]

    @property
    def feature_config(self) -> MatchFeatureConfig:
        return TEACHER_CONFIGS[self.config_name]

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["feature_config"] = {
            "name": self.feature_config.name,
            "enable_pattern_recall": self.feature_config.enable_pattern_recall,
            "enable_hard_unit_recall": self.feature_config.enable_hard_unit_recall,
            "enable_hierarchy_recall": self.feature_config.enable_hierarchy_recall,
            "enable_combo_recall": self.feature_config.enable_combo_recall,
            "enable_surface_recall": self.feature_config.enable_surface_recall,
            "enable_same_company_recall": self.feature_config.enable_same_company_recall,
            "enable_surface_score": self.feature_config.enable_surface_score,
            "enable_metadata_score": self.feature_config.enable_metadata_score,
            "enable_duplicate_score": self.feature_config.enable_duplicate_score,
            "duplicate_uses_same_company": self.feature_config.duplicate_uses_same_company,
            "allow_duplicate_override": self.feature_config.allow_duplicate_override,
        }
        return payload


TEACHER_B_SEMANTIC_V1 = FrozenTeacherManifest(
    version="teacher_b_semantic_v1",
    config_name="teacher_b_pure_semantic",
    report_path=str(ROOT / "output" / "analysis" / "match_pipe_semantic_freeze_report.json"),
    label_pool_path=str(ROOT / "match_pipe" / "semantic_label_pool.json"),
    boundary_pool_path=str(ROOT / "match_pipe" / "semantic_boundary_pool.json"),
    output_protocol={
        "semantic_best_anchor": "Global pure-semantic best anchor from requirement-unit matching.",
        "semantic_top_k": "Compact semantic candidate list for reuse.",
        "semantic_positive_cluster": "For generic-title low-anchor cases, the set of multiple acceptable semantic positives at JD level.",
        "semantic_cluster_mode": "single_positive or multi_acceptable_cluster.",
        "semantic_starter_anchor": "Final resume starter chosen from the semantic cluster by historical quality, reuse readiness, and semantic score.",
        "semantic_score": "Pure semantic channel score.",
        "semantic_explanation": "Requirement-unit hit explanation and hard-gap summary.",
        "company_best_anchor": "Same-company continuity anchor from the auxiliary channel.",
        "company_top_k": "Compact same-company continuity candidates.",
        "company_score": "Company continuity score, not part of the semantic teacher.",
        "company_explanation": "Duplicate/title/company continuity rationale.",
        "delta_summary": "Why the semantic anchor and company anchor differ, and how downstream should combine them.",
        "writer_input": "Downstream-ready payload with primary semantic anchor and optional continuity anchor.",
    },
    dynamic_ingest_policy={
        "index_new_job": "Immediate live indexing into jobs_by_id, pattern_index, member_index, combo_index, surface_token_index, and company_index.",
        "dedupe": "Exact near-duplicates merge by company/title/pattern/canonical fingerprint.",
        "quarantine": "Low-signal jobs with sparse semantics and heavy pending surface text are isolated from the main pool.",
        "alias_absorption": "New surface tokens enter the pending alias queue and are absorbed offline after review.",
        "taxonomy_rebuild": "Accepted alias and taxonomy changes require offline rebuild; job indexing does not.",
    },
    freeze_rule_layers=(
        "match_pipe/matcher.py",
        "match_pipe/units.py",
        "match_pipe/starter_selector.py",
    ),
    growth_knowledge_layers=(
        "match_pipe/taxonomy.py",
        "match_pipe/semantic_label_pool.json",
        "match_pipe/semantic_boundary_pool.json",
        "match_pipe/incremental.py",
    ),
    allowed_mutations=(
        "taxonomy expansion",
        "alias absorption",
        "gold set increment",
        "boundary pool increment",
        "small conservative rule fix",
    ),
    disallowed_mutations=(
        "aggressive parser rewrite",
        "same_company bias injection into semantic teacher",
        "duplicate shortcut injection into semantic teacher",
        "title-normalization shortcut promotion into semantic teacher",
    ),
)


def frozen_teacher_manifest() -> FrozenTeacherManifest:
    return TEACHER_B_SEMANTIC_V1
