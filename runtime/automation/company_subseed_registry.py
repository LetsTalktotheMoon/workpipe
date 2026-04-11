"""
Company subseed and outlier registry.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from automation.text_utils import normalize_token, slugify


ROOT = Path(__file__).resolve().parents[1]
COMPANY_SUBSEED_CONFIG_PATH = ROOT / "config" / "company_subseed_registry.json"


@dataclass(frozen=True)
class OutlierJob:
    job_id: str
    label: str
    title: str
    reason: str

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "label": self.label,
            "title": self.title,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class CompanySubseedDirection:
    subseed_id: str
    company_name: str
    company_slug: str
    label: str
    kind: str
    status: str
    primary_seed_id: str
    seed_ids: tuple[str, ...]
    candidate_job_ids: tuple[str, ...]
    target_role_families: tuple[str, ...]
    notes: str

    def to_dict(self) -> dict:
        return {
            "subseed_id": self.subseed_id,
            "company_name": self.company_name,
            "company_slug": self.company_slug,
            "label": self.label,
            "kind": self.kind,
            "status": self.status,
            "primary_seed_id": self.primary_seed_id,
            "seed_ids": list(self.seed_ids),
            "candidate_job_ids": list(self.candidate_job_ids),
            "target_role_families": list(self.target_role_families),
            "notes": self.notes,
        }


@dataclass(frozen=True)
class CompanySubseedPlan:
    company_name: str
    company_slug: str
    company_key: str
    max_mainline_directions: int
    notes: str
    directions: tuple[CompanySubseedDirection, ...]
    outlier_jobs: tuple[OutlierJob, ...]

    def to_dict(self) -> dict:
        return {
            "company_name": self.company_name,
            "company_slug": self.company_slug,
            "company_key": self.company_key,
            "max_mainline_directions": self.max_mainline_directions,
            "notes": self.notes,
            "directions": [item.to_dict() for item in self.directions],
            "outlier_jobs": [item.to_dict() for item in self.outlier_jobs],
        }


@dataclass(frozen=True)
class CompanySubseedRegistry:
    companies: tuple[CompanySubseedPlan, ...]

    def company_plans(self) -> tuple[CompanySubseedPlan, ...]:
        return self.companies

    def company_for_name(self, company_name: str) -> CompanySubseedPlan | None:
        target = normalize_token(company_name)
        for plan in self.companies:
            if plan.company_key == target:
                return plan
        return None

    def direction_index(self) -> dict[str, CompanySubseedDirection]:
        return {
            direction.subseed_id: direction
            for company in self.companies
            for direction in company.directions
        }

    def seed_subseed_ids(self, seed_id: str) -> tuple[str, ...]:
        wanted = []
        for company in self.companies:
            for direction in company.directions:
                if seed_id in direction.seed_ids:
                    wanted.append(direction.subseed_id)
        return tuple(wanted)

    def directions_for_company(self, company_name: str) -> tuple[CompanySubseedDirection, ...]:
        plan = self.company_for_name(company_name)
        if plan is None:
            return ()
        return plan.directions

    def direction_for_seed(self, seed_id: str) -> CompanySubseedDirection | None:
        for company in self.companies:
            for direction in company.directions:
                if direction.primary_seed_id == seed_id:
                    return direction
        ids = self.seed_subseed_ids(seed_id)
        if not ids:
            return None
        return self.direction_index().get(ids[0])

    def outlier_for_job(self, job_id: str) -> OutlierJob | None:
        job_id = str(job_id or "").strip()
        if not job_id:
            return None
        for company in self.companies:
            for outlier in company.outlier_jobs:
                if outlier.job_id == job_id:
                    return outlier
        return None

    def to_dict(self) -> dict:
        return {"companies": [company.to_dict() for company in self.companies]}


def _load_registry(path: Path) -> CompanySubseedRegistry:
    if not path.exists():
        return CompanySubseedRegistry(companies=())

    payload = json.loads(path.read_text(encoding="utf-8"))
    companies: list[CompanySubseedPlan] = []
    for company in payload.get("companies", []):
        company_name = str(company.get("company_name", "") or "").strip()
        company_slug = slugify(company_name) or normalize_token(company_name) or "unknown-company"
        directions: list[CompanySubseedDirection] = []
        for direction in company.get("directions", []):
            directions.append(
                CompanySubseedDirection(
                    subseed_id=str(direction.get("subseed_id", "") or "").strip(),
                    company_name=company_name,
                    company_slug=company_slug,
                    label=str(direction.get("label", "") or "").strip(),
                    kind=str(direction.get("kind", "mainline") or "mainline").strip(),
                    status=str(direction.get("status", "active") or "active").strip(),
                    primary_seed_id=str(direction.get("primary_seed_id", "") or "").strip(),
                    seed_ids=tuple(
                        str(item).strip()
                        for item in direction.get("seed_ids", [])
                        if str(item).strip()
                    ),
                    candidate_job_ids=tuple(
                        str(item).strip()
                        for item in direction.get("candidate_job_ids", [])
                        if str(item).strip()
                    ),
                    target_role_families=tuple(
                        str(item).strip()
                        for item in direction.get("target_role_families", [])
                        if str(item).strip()
                    ),
                    notes=str(direction.get("notes", "") or "").strip(),
                )
            )
        outlier_jobs = tuple(
            OutlierJob(
                job_id=str(item.get("job_id", "") or "").strip(),
                label=str(item.get("label", "") or "").strip(),
                title=str(item.get("title", "") or "").strip(),
                reason=str(item.get("reason", "") or "").strip(),
            )
            for item in company.get("outlier_jobs", [])
            if str(item.get("job_id", "") or "").strip()
        )
        companies.append(
            CompanySubseedPlan(
                company_name=company_name,
                company_slug=company_slug,
                company_key=normalize_token(company_name),
                max_mainline_directions=int(company.get("max_mainline_directions", 2) or 2),
                notes=str(company.get("notes", "") or "").strip(),
                directions=tuple(directions),
                outlier_jobs=outlier_jobs,
            )
        )

    return CompanySubseedRegistry(companies=tuple(companies))


@lru_cache(maxsize=1)
def load_company_subseed_registry(path: str | Path | None = None) -> CompanySubseedRegistry:
    config_path = COMPANY_SUBSEED_CONFIG_PATH if path is None else Path(path)
    if not config_path.is_absolute():
        config_path = (ROOT / config_path).resolve()
    return _load_registry(config_path)
