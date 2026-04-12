"""
Seed registry for reuse/retarget/new-seed routing.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

from automation.company_subseed_registry import load_company_subseed_registry
from models.resume import Resume
from automation.project_pool import load_project_pool_registry
from automation.text_utils import canonicalize_skill, extract_domain_terms, normalize_token


ROOT = Path(__file__).resolve().parents[1]
PROMOTED_SEEDS_PATH = ROOT / "config" / "promoted_seeds.json"


@dataclass
class SeedEntry:
    seed_id: str
    label: str
    source_md: Path
    source_type: str
    role_family: str
    seniority: str
    keywords: set[str] = field(default_factory=set)
    core_stack: set[str] = field(default_factory=set)
    domains: set[str] = field(default_factory=set)
    taxonomy_hints: set[str] = field(default_factory=set)
    validated_score: Optional[float] = None
    company_name: str = ""
    company_key: str = ""
    source_job_id: str = ""
    company_anchor: bool = False
    project_ids: tuple[str, ...] = field(default_factory=tuple)
    subseed_ids: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict:
        return {
            "seed_id": self.seed_id,
            "label": self.label,
            "source_md": str(self.source_md),
            "source_type": self.source_type,
            "role_family": self.role_family,
            "seniority": self.seniority,
            "keywords": sorted(self.keywords),
            "core_stack": sorted(self.core_stack),
            "domains": sorted(self.domains),
            "taxonomy_hints": sorted(self.taxonomy_hints),
            "validated_score": self.validated_score,
            "company_name": self.company_name,
            "company_key": self.company_key,
            "source_job_id": self.source_job_id,
            "company_anchor": self.company_anchor,
            "project_ids": list(self.project_ids),
            "subseed_ids": list(self.subseed_ids),
        }


def _markdown_seed_keywords(md_path: Path) -> tuple[set[str], set[str]]:
    if not md_path.exists():
        return set(), set()
    try:
        resume = Resume.from_markdown(md_path.read_text(encoding="utf-8"))
    except Exception:
        return set(), set()

    skills = {canonicalize_skill(skill) for skill in resume.get_skills_list() if canonicalize_skill(skill)}
    body_terms = extract_domain_terms(md_path.read_text(encoding="utf-8"))
    return skills, body_terms


def _promoted_seed_to_entry(config: dict) -> Optional[SeedEntry]:
    md_path = Path(config["path"])
    if not md_path.exists():
        return None
    keywords, body_terms = _markdown_seed_keywords(md_path)
    company_name = str(config.get("source_company", "") or "")
    registry = load_project_pool_registry()
    subseed_registry = load_company_subseed_registry()
    configured_project_ids = tuple(str(item).strip() for item in config.get("project_ids", []) if str(item).strip())
    assigned_project_ids = registry.seed_project_ids(str(config.get("seed_id", "") or ""))
    project_ids = configured_project_ids or assigned_project_ids
    subseed_ids = subseed_registry.seed_subseed_ids(str(config.get("seed_id", "") or ""))
    return SeedEntry(
        seed_id=config["seed_id"],
        label=config["label"],
        source_md=md_path,
        source_type="promoted",
        role_family=config["role_family"],
        seniority=config["seniority"],
        keywords=keywords,
        core_stack=set(list(keywords)[:8]),
        domains=set(config["domains"]) | body_terms,
        taxonomy_hints=set(config["taxonomy_hints"]),
        validated_score=config.get("validated_score"),
        company_name=company_name,
        company_key=normalize_token(company_name),
        source_job_id=str(config.get("source_job_id", "") or ""),
        company_anchor=bool(config.get("company_anchor", False)),
        project_ids=project_ids,
        subseed_ids=subseed_ids,
    )


def _load_promoted_seed_configs() -> list[dict]:
    if not PROMOTED_SEEDS_PATH.exists():
        return []
    return json.loads(PROMOTED_SEEDS_PATH.read_text(encoding="utf-8"))


def load_seed_registry(include_promoted: bool = True) -> list[SeedEntry]:
    seeds: list[SeedEntry] = []
    if include_promoted:
        for config in _load_promoted_seed_configs():
            entry = _promoted_seed_to_entry(config)
            if entry is not None:
                seeds.append(entry)
    return seeds


def seed_registry_manifest(seeds: Iterable[SeedEntry]) -> list[dict]:
    return [seed.to_dict() for seed in seeds]
