"""
Experience-company project pool registry.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
PROJECT_POOL_CONFIG_PATH = ROOT / "config" / "experience_project_pools.json"


@dataclass(frozen=True)
class ProjectCard:
    project_id: str
    company_id: str
    company_name: str
    start: str
    end: str
    team: str
    business_domain: str
    project_goal: str
    scope_ceiling: str
    ownership_ceiling: str
    allowed_tech_surface: tuple[str, ...]
    allowed_role_lenses: tuple[str, ...]
    needs_scope_note: bool
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "project_id": self.project_id,
            "company_id": self.company_id,
            "company_name": self.company_name,
            "start": self.start,
            "end": self.end,
            "team": self.team,
            "business_domain": self.business_domain,
            "project_goal": self.project_goal,
            "scope_ceiling": self.scope_ceiling,
            "ownership_ceiling": self.ownership_ceiling,
            "allowed_tech_surface": list(self.allowed_tech_surface),
            "allowed_role_lenses": list(self.allowed_role_lenses),
            "needs_scope_note": self.needs_scope_note,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class CompanyProjectPool:
    company_id: str
    company_name: str
    aliases: tuple[str, ...]
    max_projects: int
    notes: str
    projects: tuple[ProjectCard, ...]

    def to_dict(self) -> dict:
        return {
            "company_id": self.company_id,
            "company_name": self.company_name,
            "aliases": list(self.aliases),
            "max_projects": self.max_projects,
            "notes": self.notes,
            "projects": [project.to_dict() for project in self.projects],
        }


@dataclass(frozen=True)
class ProjectPoolRegistry:
    resume_project_limit: int
    company_pools: tuple[CompanyProjectPool, ...]
    seed_assignments: dict[str, tuple[str, ...]]

    def project_index(self) -> dict[str, ProjectCard]:
        return {
            project.project_id: project
            for pool in self.company_pools
            for project in pool.projects
        }

    def seed_project_ids(self, seed_id: str) -> tuple[str, ...]:
        return self.seed_assignments.get(seed_id, ())

    def project_cards_for_seed(self, seed_id: str) -> list[ProjectCard]:
        project_index = self.project_index()
        return [
            project_index[project_id]
            for project_id in self.seed_project_ids(seed_id)
            if project_id in project_index
        ]

    def active_project_cards(self, project_ids: Iterable[str]) -> list[ProjectCard]:
        wanted = {project_id for project_id in project_ids if project_id}
        if not wanted:
            return []
        project_index = self.project_index()
        return [project_index[project_id] for project_id in wanted if project_id in project_index]

    def to_dict(self) -> dict:
        return {
            "resume_project_limit": self.resume_project_limit,
            "company_pools": [pool.to_dict() for pool in self.company_pools],
            "seed_assignments": {seed_id: list(project_ids) for seed_id, project_ids in self.seed_assignments.items()},
        }


def _load_registry(path: Path) -> ProjectPoolRegistry:
    if not path.exists():
        return ProjectPoolRegistry(
            resume_project_limit=2,
            company_pools=(),
            seed_assignments={},
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    company_pools: list[CompanyProjectPool] = []
    for company in payload.get("companies", []):
        company_id = str(company.get("company_id", "") or "").strip()
        company_name = str(company.get("company_name", "") or "").strip()
        projects: list[ProjectCard] = []
        for project in company.get("projects", []):
            projects.append(
                ProjectCard(
                    project_id=str(project.get("project_id", "") or "").strip(),
                    company_id=company_id,
                    company_name=company_name,
                    start=str(project.get("start", "") or "").strip(),
                    end=str(project.get("end", "") or "").strip(),
                    team=str(project.get("team", "") or "").strip(),
                    business_domain=str(project.get("business_domain", "") or "").strip(),
                    project_goal=str(project.get("project_goal", "") or "").strip(),
                    scope_ceiling=str(project.get("scope_ceiling", "") or "").strip(),
                    ownership_ceiling=str(project.get("ownership_ceiling", "") or "").strip(),
                    allowed_tech_surface=tuple(str(item).strip() for item in project.get("allowed_tech_surface", []) if str(item).strip()),
                    allowed_role_lenses=tuple(str(item).strip() for item in project.get("allowed_role_lenses", []) if str(item).strip()),
                    needs_scope_note=bool(project.get("needs_scope_note", False)),
                    notes=str(project.get("notes", "") or "").strip(),
                )
            )
        company_pools.append(
            CompanyProjectPool(
                company_id=company_id,
                company_name=company_name,
                aliases=tuple(str(item).strip() for item in company.get("aliases", []) if str(item).strip()),
                max_projects=int(company.get("max_projects", len(projects) or 4)),
                notes=str(company.get("notes", "") or "").strip(),
                projects=tuple(projects),
            )
        )
    seed_assignments = {
        str(seed_id).strip(): tuple(str(project_id).strip() for project_id in project_ids if str(project_id).strip())
        for seed_id, project_ids in (payload.get("seed_assignments", {}) or {}).items()
        if str(seed_id).strip()
    }
    return ProjectPoolRegistry(
        resume_project_limit=int(payload.get("resume_project_limit", 2) or 2),
        company_pools=tuple(company_pools),
        seed_assignments=seed_assignments,
    )


@lru_cache(maxsize=1)
def load_project_pool_registry(path: str | Path | None = None) -> ProjectPoolRegistry:
    config_path = PROJECT_POOL_CONFIG_PATH if path is None else Path(path)
    if not config_path.is_absolute():
        config_path = (ROOT / config_path).resolve()
    return _load_registry(config_path)


def build_project_pool_prompt_block(active_project_ids: Iterable[str] | None = None) -> str:
    registry = load_project_pool_registry()
    active_ids = {project_id for project_id in (active_project_ids or []) if project_id}
    lines = [
        "## 经验公司项目池（硬约束）",
        f"- 单篇简历最多保留 {registry.resume_project_limit} 个项目。",
        "- 项目只能从下面的公司主池里选，不允许发明新项目或把同一项目改写成完全不同的业务逻辑。",
        "- 同一项目可以换强调角度，但 team / domain / scope ceiling / ownership ceiling 不可越界。",
        "",
    ]
    for pool in registry.company_pools:
        lines.extend(
            [
                f"### {pool.company_name}",
                f"- 公司池上限: {pool.max_projects}",
                f"- 说明: {pool.notes or '保持同一人设与时间线。'}",
            ]
        )
        for project in pool.projects:
            active_marker = " [CURRENT SEED]" if project.project_id in active_ids else ""
            tech_surface = ", ".join(project.allowed_tech_surface)
            role_lenses = ", ".join(project.allowed_role_lenses)
            scope_note = "需要" if project.needs_scope_note else "通常不需要"
            lines.extend(
                [
                    f"- `{project.project_id}`{active_marker}",
                    f"  时间: {project.start} -> {project.end}",
                    f"  团队: {project.team}",
                    f"  业务域: {project.business_domain}",
                    f"  目标: {project.project_goal}",
                    f"  scope ceiling: {project.scope_ceiling}",
                    f"  ownership ceiling: {project.ownership_ceiling}",
                    f"  allowed tech surface: {tech_surface}",
                    f"  allowed role lenses: {role_lenses}",
                    f"  scope note: {scope_note}",
                ]
            )
            if project.notes:
                lines.append(f"  notes: {project.notes}")
        lines.append("")
    return "\n".join(lines).strip()
