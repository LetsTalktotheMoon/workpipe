"""Extract non-technical requirement phrases from the 3999-JD catalog.

This module is intentionally standalone. It produces intermediate phrase rows
for a later merge/frequency layer, but it does not perform final synonym
consolidation or touch the top-level build_skills report.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from build_skills.词频分析.rules import (
    BUCKET_BUSINESS_DOMAIN,
    BUCKET_GENERALIZED_TECH,
    BUCKET_SOFT_SKILL,
    classify_phrase,
    is_noise_phrase,
    is_specific_tech_phrase,
    normalize_for_matching,
    normalize_phrase,
)


DEFAULT_JD_CATALOG_PATH = Path("data/job_tracker/jobs_catalog.json")
DEFAULT_PORTFOLIO_INDEX_PATH = Path("data/deliverables/resume_portfolio/portfolio_index.json")
DEFAULT_OUT_DIR = Path("build_skills/词频分析/output")

REQUIREMENT_TEXT_FIELDS = ("must_have_quals", "preferred_quals", "core_responsibilities")
IGNORED_FIELDS = ("job_summary", "core_skills")


@dataclass(frozen=True)
class PatternRule:
    rule_id: str
    bucket: str
    pattern: re.Pattern[str]


@dataclass
class SourceStats:
    jobs_with_content: int = 0
    jobs_with_candidate: int = 0
    raw_match_count: int = 0
    unique_phrases: set[str] = None  # type: ignore[assignment]
    phrase_counts: Counter[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.unique_phrases is None:
            self.unique_phrases = set()
        if self.phrase_counts is None:
            self.phrase_counts = Counter()


@dataclass(frozen=True)
class NarrativeGroupSpec:
    group_label: str
    titles: tuple[str, ...]
    common_introduction: str
    common_business_scenario: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--jd-catalog-path",
        default=str(DEFAULT_JD_CATALOG_PATH),
        help="Primary 3999-row JD catalog.",
    )
    parser.add_argument(
        "--portfolio-index-path",
        default=str(DEFAULT_PORTFOLIO_INDEX_PATH),
        help="Optional portfolio index for job_id-level supplementation.",
    )
    parser.add_argument("--out", default=str(DEFAULT_OUT_DIR), help="Output directory for this module.")
    return parser.parse_args()


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text())


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_jsonl(path: Path, rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open() as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).replace("\u00a0", " ").split()).strip()


def parse_full_job_json(value: Any) -> dict[str, Any]:
    if not value:
        return {}
    if isinstance(value, dict):
        return value
    if not isinstance(value, str):
        return {}
    try:
        payload = json.loads(value)
    except json.JSONDecodeError:
        return {}
    if isinstance(payload, dict):
        job_result = payload.get("jobResult")
        if isinstance(job_result, dict):
            return job_result
    return {}


def build_jd_catalog(jd_catalog_path: Path, portfolio_index_path: Path) -> list[dict[str, Any]]:
    catalog_rows = read_json(jd_catalog_path, [])
    portfolio_rows = read_json(portfolio_index_path, [])

    catalog_by_id = {
        str(row.get("job_id", "")).strip(): row
        for row in catalog_rows
        if isinstance(row, dict) and str(row.get("job_id", "")).strip()
    }
    portfolio_by_id = {
        str(row.get("job_id", "")).strip(): row
        for row in portfolio_rows
        if isinstance(row, dict) and str(row.get("job_id", "")).strip()
    }

    merged: list[dict[str, Any]] = []
    for job_id in sorted(set(catalog_by_id) | set(portfolio_by_id)):
        catalog_row = catalog_by_id.get(job_id, {})
        portfolio_row = portfolio_by_id.get(job_id, {})
        if catalog_row and portfolio_row:
            source_scope = "both"
        elif catalog_row:
            source_scope = "catalog_only"
        else:
            source_scope = "portfolio_only"

        job_result = parse_full_job_json(catalog_row.get("full_job_json"))
        merged.append(
            {
                "job_id": job_id,
                "company_name": normalize_text(catalog_row.get("company_name") or portfolio_row.get("company_name") or portfolio_row.get("company_slug")),
                "job_title": normalize_text(catalog_row.get("job_title") or catalog_row.get("job_nlp_title") or portfolio_row.get("title")),
                "job_summary": normalize_text(catalog_row.get("job_summary")),
                "must_have_quals": normalize_text(catalog_row.get("must_have_quals")),
                "preferred_quals": normalize_text(catalog_row.get("preferred_quals")),
                "core_responsibilities": normalize_text(catalog_row.get("core_responsibilities")),
                "core_skills": normalize_text(catalog_row.get("core_skills")),
                "full_job_json": job_result,
                "source_scope": source_scope,
            }
        )
    return merged


def build_rule_patterns() -> list[PatternRule]:
    def pat(rule_id: str, bucket: str, pattern: str) -> PatternRule:
        return PatternRule(rule_id=rule_id, bucket=bucket, pattern=re.compile(pattern, flags=re.IGNORECASE))

    rules = [
        # generalized tech descriptors
        pat("software_development", "generalized_tech", r"(?<![A-Za-z0-9])software development(?: experience| life cycle| lifecycle)?(?![A-Za-z0-9])"),
        pat("software_engineering", "generalized_tech", r"(?<![A-Za-z0-9])software engineering(?: experience)?(?![A-Za-z0-9])"),
        pat("software_engineer", "generalized_tech", r"(?<![A-Za-z0-9])software engineer(?:ing)?(?![A-Za-z0-9])"),
        pat("software_developer", "generalized_tech", r"(?<![A-Za-z0-9])software developer(?: experience)?(?![A-Za-z0-9])"),
        pat("swe", "generalized_tech", r"(?<![A-Za-z0-9])swe(?![A-Za-z0-9])"),
        pat("sde", "generalized_tech", r"(?<![A-Za-z0-9])sde(?: [ivx]+)?(?![A-Za-z0-9])"),
        pat("application_development", "generalized_tech", r"(?<![A-Za-z0-9])application development(?![A-Za-z0-9])"),
        pat("application_engineering", "generalized_tech", r"(?<![A-Za-z0-9])application engineering(?![A-Za-z0-9])"),
        pat("full_stack", "generalized_tech", r"(?<![A-Za-z0-9])full[- ]?stack(?: development)?(?![A-Za-z0-9])"),
        pat("backend_development", "generalized_tech", r"(?<![A-Za-z0-9])back[- ]?end development(?![A-Za-z0-9])"),
        pat("frontend_development", "generalized_tech", r"(?<![A-Za-z0-9])front[- ]?end development(?![A-Za-z0-9])"),
        pat("web_development", "generalized_tech", r"(?<![A-Za-z0-9])web development(?![A-Za-z0-9])"),
        pat("data_engineering", "generalized_tech", r"(?<![A-Za-z0-9])data engineering(?![A-Za-z0-9])"),
        pat("data_analytics", "generalized_tech", r"(?<![A-Za-z0-9])data analytics?(?![A-Za-z0-9])"),
        pat("data_science", "generalized_tech", r"(?<![A-Za-z0-9])data science(?![A-Za-z0-9])"),
        pat("data_analysis", "generalized_tech", r"(?<![A-Za-z0-9])data analysis(?![A-Za-z0-9])"),
        pat("machine_learning", "generalized_tech", r"(?<![A-Za-z0-9])machine learning(?![A-Za-z0-9])"),
        pat("deep_learning", "generalized_tech", r"(?<![A-Za-z0-9])deep learning(?![A-Za-z0-9])"),
        pat("data_pipelines", "generalized_tech", r"(?<![A-Za-z0-9])data pipelines?(?![A-Za-z0-9])"),
        pat("data_visualization", "generalized_tech", r"(?<![A-Za-z0-9])data visualization(?: tools?)?(?![A-Za-z0-9])"),
        pat("apis", "generalized_tech", r"(?<![A-Za-z0-9])apis?(?![A-Za-z0-9])"),
        pat("relational_databases", "generalized_tech", r"(?<![A-Za-z0-9])relational databases?(?![A-Za-z0-9])"),
        pat("non_relational_databases", "generalized_tech", r"(?<![A-Za-z0-9])non[- ]?relational databases?(?![A-Za-z0-9])"),
        pat("mpp_databases", "generalized_tech", r"(?<![A-Za-z0-9])mpp databases?(?![A-Za-z0-9])"),
        pat("databases", "generalized_tech", r"(?<![A-Za-z0-9])databases?(?![A-Za-z0-9])"),
        pat("distributed_systems", "generalized_tech", r"(?<![A-Za-z0-9])distributed systems?(?![A-Za-z0-9])"),
        pat("system_design", "generalized_tech", r"(?<![A-Za-z0-9])system design(?![A-Za-z0-9])"),
        pat("devops", "generalized_tech", r"(?<![A-Za-z0-9])devops(?![A-Za-z0-9])"),
        pat("ci_cd", "generalized_tech", r"(?<![A-Za-z0-9])ci/cd(?![A-Za-z0-9])"),
        pat("version_control", "generalized_tech", r"(?<![A-Za-z0-9])version control(?![A-Za-z0-9])"),
        pat("quality_assurance", "generalized_tech", r"(?<![A-Za-z0-9])quality assurance(?![A-Za-z0-9])"),
        pat("testing", "generalized_tech", r"(?<![A-Za-z0-9])testing(?![A-Za-z0-9])"),

        # business domain
        pat("fintech", "business_domain", r"(?<![A-Za-z0-9])fintech(?![A-Za-z0-9])"),
        pat("financial_services", "business_domain", r"(?<![A-Za-z0-9])financial services(?![A-Za-z0-9])"),
        pat("financial_markets", "business_domain", r"(?<![A-Za-z0-9])financial markets(?![A-Za-z0-9])"),
        pat("banking", "business_domain", r"(?<![A-Za-z0-9])banking(?![A-Za-z0-9])"),
        pat("payments", "business_domain", r"(?<![A-Za-z0-9])payments?(?![A-Za-z0-9])"),
        pat("healthcare", "business_domain", r"(?<![A-Za-z0-9])healthcare(?![A-Za-z0-9])"),
        pat("life_science", "business_domain", r"(?<![A-Za-z0-9])life science(?:s)?(?![A-Za-z0-9])"),
        pat("pharma", "business_domain", r"(?<![A-Za-z0-9])pharma(?![A-Za-z0-9])"),
        pat("biotech", "business_domain", r"(?<![A-Za-z0-9])biotech(?![A-Za-z0-9])"),
        pat("trading", "business_domain", r"(?<![A-Za-z0-9])trading(?![A-Za-z0-9])"),
        pat("retail", "business_domain", r"(?<![A-Za-z0-9])retail(?![A-Za-z0-9])"),
        pat("ecommerce", "business_domain", r"(?<![A-Za-z0-9])e[- ]commerce(?![A-Za-z0-9])"),
        pat("consumer", "business_domain", r"(?<![A-Za-z0-9])consumer(?![A-Za-z0-9])"),
        pat("enterprise", "business_domain", r"(?<![A-Za-z0-9])enterprise(?![A-Za-z0-9])"),
        pat("insurance", "business_domain", r"(?<![A-Za-z0-9])insurance(?![A-Za-z0-9])"),
        pat("supply_chain", "business_domain", r"(?<![A-Za-z0-9])supply chain(?![A-Za-z0-9])"),
        pat("logistics", "business_domain", r"(?<![A-Za-z0-9])logistics(?![A-Za-z0-9])"),
        pat("gaming", "business_domain", r"(?<![A-Za-z0-9])gaming(?![A-Za-z0-9])"),
        pat("education", "business_domain", r"(?<![A-Za-z0-9])education(?![A-Za-z0-9])"),
        pat("media", "business_domain", r"(?<![A-Za-z0-9])media(?![A-Za-z0-9])"),
        pat("telecom", "business_domain", r"(?<![A-Za-z0-9])telecom(?:munications)?(?![A-Za-z0-9])"),
        pat("manufacturing", "business_domain", r"(?<![A-Za-z0-9])manufacturing(?![A-Za-z0-9])"),
        pat("real_estate", "business_domain", r"(?<![A-Za-z0-9])real estate(?![A-Za-z0-9])"),
        pat("mortgage", "business_domain", r"(?<![A-Za-z0-9])mortgage(?![A-Za-z0-9])"),
        pat("lending", "business_domain", r"(?<![A-Za-z0-9])lending(?![A-Za-z0-9])"),
        pat("credit", "business_domain", r"(?<![A-Za-z0-9])credit(?![A-Za-z0-9])"),
        pat("risk", "business_domain", r"(?<![A-Za-z0-9])risk(?![A-Za-z0-9])"),
        pat("fraud", "business_domain", r"(?<![A-Za-z0-9])fraud(?![A-Za-z0-9])"),
        pat("marketplace", "business_domain", r"(?<![A-Za-z0-9])marketplace(?![A-Za-z0-9])"),
        pat("advertising", "business_domain", r"(?<![A-Za-z0-9])advertising(?![A-Za-z0-9])"),
        pat("ad_tech", "business_domain", r"(?<![A-Za-z0-9])ad tech(?![A-Za-z0-9])"),
        pat("wealth_management", "business_domain", r"(?<![A-Za-z0-9])wealth management(?![A-Za-z0-9])"),
        pat("government", "business_domain", r"(?<![A-Za-z0-9])government(?![A-Za-z0-9])"),
        pat("public_sector", "business_domain", r"(?<![A-Za-z0-9])public sector(?![A-Za-z0-9])"),
        pat("transportation", "business_domain", r"(?<![A-Za-z0-9])transportation(?![A-Za-z0-9])"),
        pat("travel", "business_domain", r"(?<![A-Za-z0-9])travel(?![A-Za-z0-9])"),
        pat("hospitality", "business_domain", r"(?<![A-Za-z0-9])hospitality(?![A-Za-z0-9])"),
        pat("energy", "business_domain", r"(?<![A-Za-z0-9])energy(?![A-Za-z0-9])"),
        pat("b2b", "business_domain", r"(?<![A-Za-z0-9])b2b(?![A-Za-z0-9])"),
        pat("b2c", "business_domain", r"(?<![A-Za-z0-9])b2c(?![A-Za-z0-9])"),

        # soft skills
        pat("problem_solving", "soft_skill", r"(?<![A-Za-z0-9])problem[- ]solving(?: skills)?(?![A-Za-z0-9])"),
        pat("communication_skills", "soft_skill", r"(?<![A-Za-z0-9])communication(?: skills)?(?![A-Za-z0-9])"),
        pat("effective_communication", "soft_skill", r"(?<![A-Za-z0-9])effective communication(?![A-Za-z0-9])"),
        pat("clear_communication", "soft_skill", r"(?<![A-Za-z0-9])clear communication(?![A-Za-z0-9])"),
        pat("written_communication", "soft_skill", r"(?<![A-Za-z0-9])written communication(?![A-Za-z0-9])"),
        pat("verbal_communication", "soft_skill", r"(?<![A-Za-z0-9])verbal communication(?![A-Za-z0-9])"),
        pat("collaboration", "soft_skill", r"(?<![A-Za-z0-9])collaboration(?![A-Za-z0-9])"),
        pat("collaborative", "soft_skill", r"(?<![A-Za-z0-9])collaborative(?![A-Za-z0-9])"),
        pat("teamwork", "soft_skill", r"(?<![A-Za-z0-9])teamwork(?![A-Za-z0-9])"),
        pat("leadership", "soft_skill", r"(?<![A-Za-z0-9])leadership(?![A-Za-z0-9])"),
        pat("mentoring", "soft_skill", r"(?<![A-Za-z0-9])mentoring(?![A-Za-z0-9])"),
        pat("attention_to_detail", "soft_skill", r"(?<![A-Za-z0-9])attention to detail(?![A-Za-z0-9])"),
        pat("analytical_skills", "soft_skill", r"(?<![A-Za-z0-9])analytical skills?(?![A-Za-z0-9])"),
        pat("analytical_thinking", "soft_skill", r"(?<![A-Za-z0-9])analytical thinking(?![A-Za-z0-9])"),
        pat("analytical", "soft_skill", r"(?<![A-Za-z0-9])analytical(?![A-Za-z0-9])"),
        pat("adaptability", "soft_skill", r"(?<![A-Za-z0-9])adaptability(?![A-Za-z0-9])"),
        pat("curiosity", "soft_skill", r"(?<![A-Za-z0-9])curiosity(?![A-Za-z0-9])"),
        pat("ownership", "soft_skill", r"(?<![A-Za-z0-9])ownership(?![A-Za-z0-9])"),
        pat("interpersonal_skills", "soft_skill", r"(?<![A-Za-z0-9])interpersonal skills?(?![A-Za-z0-9])"),
        pat("cross_functional_collaboration", "soft_skill", r"(?<![A-Za-z0-9])cross[- ]functional collaboration(?![A-Za-z0-9])"),
        pat("cross_functional_teams", "soft_skill", r"(?<![A-Za-z0-9])cross[- ]functional teams?(?![A-Za-z0-9])"),
        pat("stakeholder_management", "soft_skill", r"(?<![A-Za-z0-9])stakeholder management(?![A-Za-z0-9])"),
        pat("stakeholder", "soft_skill", r"(?<![A-Za-z0-9])stakeholders?(?![A-Za-z0-9])"),
        pat("critical_thinking", "soft_skill", r"(?<![A-Za-z0-9])critical thinking(?![A-Za-z0-9])"),
        pat("time_management", "soft_skill", r"(?<![A-Za-z0-9])time management(?![A-Za-z0-9])"),
        pat("creativity", "soft_skill", r"(?<![A-Za-z0-9])creativity(?![A-Za-z0-9])"),
        pat("self_starter", "soft_skill", r"(?<![A-Za-z0-9])self[- ]starter(?![A-Za-z0-9])"),
        pat("initiative", "soft_skill", r"(?<![A-Za-z0-9])initiative(?![A-Za-z0-9])"),
        pat("independent_work", "soft_skill", r"(?<![A-Za-z0-9])independent work(?![A-Za-z0-9])"),
        pat("independence", "soft_skill", r"(?<![A-Za-z0-9])independence(?![A-Za-z0-9])"),
        pat("quick_learner", "soft_skill", r"(?<![A-Za-z0-9])quick learner(?![A-Za-z0-9])"),
        pat("willingness_to_learn", "soft_skill", r"(?<![A-Za-z0-9])willingness to learn(?![A-Za-z0-9])"),
        pat("eagerness_to_learn", "soft_skill", r"(?<![A-Za-z0-9])eagerness to learn(?![A-Za-z0-9])"),
        pat("accountability", "soft_skill", r"(?<![A-Za-z0-9])accountability(?![A-Za-z0-9])"),
        pat("accountable", "soft_skill", r"(?<![A-Za-z0-9])accountable(?![A-Za-z0-9])"),
        pat("proactive", "soft_skill", r"(?<![A-Za-z0-9])proactive(?![A-Za-z0-9])"),
        pat("flexibility", "soft_skill", r"(?<![A-Za-z0-9])flexibility(?![A-Za-z0-9])"),
        pat("organizational_skills", "soft_skill", r"(?<![A-Za-z0-9])organizational skills?(?![A-Za-z0-9])"),
        pat("business_acumen", "soft_skill", r"(?<![A-Za-z0-9])business acumen(?![A-Za-z0-9])"),
    ]
    # longer / more specific rules first to avoid nested overlaps such as
    # "communication skills" versus "communication".
    return sorted(rules, key=lambda rule: len(rule.pattern.pattern), reverse=True)


RULES = build_rule_patterns()

GENERALIZED_TECH_EXCLUDED = {
    "API",
    "APIs",
    "CI/CD",
    "Data Pipelines",
    "Data Science",
    "Data Visualization",
    "Deep Learning",
    "DevOps",
    "Distributed Systems",
    "Machine Learning",
    "Quality Assurance",
    "Testing",
    "Version Control",
}


AGGREGATION_BUCKET_ORDER = {
    BUCKET_GENERALIZED_TECH: 0,
    BUCKET_BUSINESS_DOMAIN: 1,
    BUCKET_SOFT_SKILL: 2,
}


AGGREGATION_FALLBACK_GROUPS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "Database Systems",
        BUCKET_GENERALIZED_TECH,
        (
            "database",
            "databases",
            "database system",
            "database systems",
            "relational database",
            "relational databases",
            "non relational database",
            "non relational databases",
            "non-relational database",
            "non-relational databases",
            "mpp database",
            "mpp databases",
            "rdbms",
            "db administration",
            "database architecture",
            "database design",
            "data modeling",
        ),
    ),
    (
        "Data Science / Analytics",
        BUCKET_GENERALIZED_TECH,
        (
            "data analysis",
            "data analytics",
            "business analytics",
            "product analytics",
            "applied analytics",
            "data visualization",
            "data visualization tool",
            "data visualization tools",
        ),
    ),
    (
        "Software Engineering",
        BUCKET_GENERALIZED_TECH,
        (
            "software development life cycle",
            "software development lifecycle",
            "software dev lifecycle",
            "software development experience",
            "software development lifecycle experience",
            "application development",
            "application engineering",
            "software application development",
        ),
    ),
    (
        "Web Development",
        BUCKET_GENERALIZED_TECH,
        (
            "web development",
            "web application development",
            "web applications",
            "web application engineering",
        ),
    ),
    (
        "Data Engineering",
        BUCKET_GENERALIZED_TECH,
        (
            "data pipeline",
            "data pipelines",
            "data platform engineering",
            "data infrastructure engineering",
            "analytics engineering",
        ),
    ),
    (
        "Architecture / Systems",
        BUCKET_GENERALIZED_TECH,
        (
            "distributed system",
            "distributed systems",
            "system architecture",
            "systems architecture",
        ),
    ),
    (
        "Finance / FinTech",
        BUCKET_BUSINESS_DOMAIN,
        (
            "financial markets",
            "capital markets",
            "fintech",
            "financial services",
            "finance",
            "payment",
            "payments",
            "wealth management",
        ),
    ),
    (
        "Banking",
        BUCKET_BUSINESS_DOMAIN,
        (
            "banking",
            "bank",
            "lending",
            "lender",
            "mortgage",
        ),
    ),
    (
        "Risk / Fraud / Credit",
        BUCKET_BUSINESS_DOMAIN,
        (
            "risk",
            "fraud",
            "credit",
        ),
    ),
    (
        "Enterprise Software / SaaS",
        BUCKET_BUSINESS_DOMAIN,
        (
            "enterprise",
        ),
    ),
    (
        "Consumer Products / Consumer Internet",
        BUCKET_BUSINESS_DOMAIN,
        (
            "consumer",
        ),
    ),
    (
        "Trading",
        BUCKET_BUSINESS_DOMAIN,
        (
            "trading",
        ),
    ),
    (
        "Media / Advertising",
        BUCKET_BUSINESS_DOMAIN,
        (
            "ad tech",
            "adtech",
        ),
    ),
    (
        "B2B / B2C",
        BUCKET_BUSINESS_DOMAIN,
        (
            "b2b",
            "b2c",
        ),
    ),
    (
        "思辨与创新",
        BUCKET_SOFT_SKILL,
        (
            "problem solving",
            "problem-solving",
            "critical thinking",
            "analytical",
            "analytical skill",
            "analytical skills",
            "analytical thinking",
            "learning agility",
            "willingness to learn",
            "eagerness to learn",
            "quick learner",
            "fast learner",
            "curiosity",
            "curious",
            "business acumen",
            "creativity",
            "innovation",
        ),
    ),
    (
        "合作",
        BUCKET_SOFT_SKILL,
        (
            "communication",
            "communicate",
            "written communication",
            "verbal communication",
            "effective communication",
            "clear communication",
            "interpersonal skill",
            "interpersonal skills",
            "collaborative",
            "collaboration",
            "collaborate",
            "teamwork",
            "team player",
            "partner with",
            "cross-team collaboration",
            "cross functional team",
            "cross functional teams",
            "cross functional teamwork",
            "cross-functional team",
            "cross-functional teams",
            "cross-functional teamwork",
            "cross-functional collaboration",
            "cross functional collaboration",
        ),
    ),
    (
        "管理/领导",
        BUCKET_SOFT_SKILL,
        (
            "leadership",
            "lead a team",
            "lead the team",
            "influence",
            "influencing",
            "mentoring",
            "mentor",
            "coaching",
            "coach others",
            "stakeholder",
            "stakeholders",
            "stakeholder management",
            "manage stakeholders",
            "align stakeholders",
            "proactive",
            "initiative",
            "accountability",
            "accountable",
            "ownership",
            "take ownership",
            "own outcomes",
            "self starter",
            "self-starter",
            "presentation",
            "presenting",
            "storytelling",
            "public speaking",
        ),
    ),
    (
        "抗压",
        BUCKET_SOFT_SKILL,
        (
            "adaptability",
            "adaptable",
            "flexibility",
            "flexible",
            "independence",
            "independent work",
            "prioritization",
            "prioritize",
            "time management",
            "manage priorities",
            "attention to detail",
            "detail oriented",
            "detail-oriented",
            "organization",
            "organizational skill",
            "organizational skills",
        ),
    ),
)

AGGREGATION_FALLBACK_LOOKUP: dict[str, tuple[str, str]] = {}
for title, bucket, aliases in AGGREGATION_FALLBACK_GROUPS:
    for alias in aliases:
        AGGREGATION_FALLBACK_LOOKUP[normalize_for_matching(alias)] = (title, bucket)

AGGREGATION_TITLE_REMAP: dict[tuple[str, str], tuple[str, str]] = {
    (BUCKET_SOFT_SKILL, "Communication"): (BUCKET_SOFT_SKILL, "合作"),
    (BUCKET_SOFT_SKILL, "Collaboration"): (BUCKET_SOFT_SKILL, "合作"),
    (BUCKET_SOFT_SKILL, "Cross-Functional Collaboration"): (BUCKET_SOFT_SKILL, "合作"),
    (BUCKET_SOFT_SKILL, "Customer Focus"): (BUCKET_SOFT_SKILL, "合作"),
    (BUCKET_SOFT_SKILL, "Stakeholder Management"): (BUCKET_SOFT_SKILL, "合作"),
    (BUCKET_SOFT_SKILL, "Problem Solving"): (BUCKET_SOFT_SKILL, "思辨与创新"),
    (BUCKET_SOFT_SKILL, "Analytical Thinking"): (BUCKET_SOFT_SKILL, "思辨与创新"),
    (BUCKET_SOFT_SKILL, "Learning Agility"): (BUCKET_SOFT_SKILL, "思辨与创新"),
    (BUCKET_SOFT_SKILL, "Innovation"): (BUCKET_SOFT_SKILL, "思辨与创新"),
    (BUCKET_SOFT_SKILL, "Business Acumen"): (BUCKET_SOFT_SKILL, "思辨与创新"),
    (BUCKET_SOFT_SKILL, "Critical Thinking / Innovation"): (BUCKET_SOFT_SKILL, "思辨与创新"),
    (BUCKET_SOFT_SKILL, "Leadership"): (BUCKET_SOFT_SKILL, "管理/领导"),
    (BUCKET_SOFT_SKILL, "Mentoring"): (BUCKET_SOFT_SKILL, "管理/领导"),
    (BUCKET_SOFT_SKILL, "Ownership / Accountability"): (BUCKET_SOFT_SKILL, "管理/领导"),
    (BUCKET_SOFT_SKILL, "Presentation"): (BUCKET_SOFT_SKILL, "管理/领导"),
    (BUCKET_SOFT_SKILL, "Management / Leadership"): (BUCKET_SOFT_SKILL, "管理/领导"),
    (BUCKET_SOFT_SKILL, "Adaptability"): (BUCKET_SOFT_SKILL, "抗压"),
    (BUCKET_SOFT_SKILL, "Prioritization / Time Management"): (BUCKET_SOFT_SKILL, "抗压"),
    (BUCKET_SOFT_SKILL, "Independence"): (BUCKET_SOFT_SKILL, "抗压"),
    (BUCKET_SOFT_SKILL, "Organization"): (BUCKET_SOFT_SKILL, "抗压"),
    (BUCKET_SOFT_SKILL, "Attention to Detail"): (BUCKET_SOFT_SKILL, "抗压"),
    (BUCKET_SOFT_SKILL, "Resilience / Pressure Tolerance"): (BUCKET_SOFT_SKILL, "抗压"),
}


def remap_aggregated_title(bucket: str, title: str) -> tuple[str, str]:
    return AGGREGATION_TITLE_REMAP.get((bucket, title), (bucket, title))


def _display_semantic_variant(raw_phrase: str) -> str:
    text = clean_display_phrase(raw_phrase)
    return text or normalize_text(raw_phrase)


def classify_aggregated_phrase(raw_phrase: str) -> tuple[str, str, str, str] | None:
    """Classify a phrase into the final aggregation buckets.

    Returns ``(title, bucket, normalized_display_phrase, source_kind)``.
    """

    normalized = normalize_phrase(raw_phrase)
    if not normalized:
        return None
    if is_noise_phrase(normalized):
        return None

    decision = classify_phrase(normalized)
    if decision is not None:
        bucket, title = remap_aggregated_title(decision.bucket, decision.title)
        return title, bucket, _display_semantic_variant(decision.normalized_phrase), "rules"

    fallback = AGGREGATION_FALLBACK_LOOKUP.get(normalize_for_matching(normalized))
    if fallback is None:
        if is_specific_tech_phrase(normalized):
            return None
        return None
    title, bucket = fallback
    bucket, title = remap_aggregated_title(bucket, title)
    return title, bucket, _display_semantic_variant(normalized), "fallback"


def read_jsonl_rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    if not path.exists():
        return rows
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if isinstance(payload, dict):
                rows.append(payload)
    return rows


def build_frequency_tables(phrase_rows_path: Path) -> tuple[dict[str, list[dict[str, object]]], dict[str, object]]:
    rows = read_jsonl_rows(phrase_rows_path)
    grouped: dict[tuple[str, str], dict[str, object]] = {}
    drop_reason_counts: Counter[str] = Counter()
    noise_samples: Counter[str] = Counter()
    excluded_tech_samples: Counter[str] = Counter()
    accepted_rows = 0
    accepted_jobs: set[str] = set()
    dropped_rows = 0
    accepted_variant_rows = 0

    for row in rows:
        phrase = normalize_text(row.get("normalized_phrase"))
        if not phrase:
            continue

        classification = classify_aggregated_phrase(phrase)
        if classification is None:
            dropped_rows += 1
            if is_noise_phrase(phrase):
                drop_reason = "noise"
            elif is_specific_tech_phrase(phrase):
                drop_reason = "specific_tech"
            else:
                drop_reason = "unmapped"
            drop_reason_counts[drop_reason] += 1
            if drop_reason == "noise":
                noise_samples[_display_semantic_variant(phrase)] += 1
            elif drop_reason == "specific_tech":
                excluded_tech_samples[_display_semantic_variant(phrase)] += 1
            continue

        title, bucket, display_variant, source_kind = classification
        accepted_rows += 1
        job_id = normalize_text(row.get("job_id"))
        if job_id:
            accepted_jobs.add(job_id)

        accepted_variant_rows += 1
        key = (bucket, title)
        group = grouped.setdefault(
            key,
            {
                "bucket": bucket,
                "title": title,
                "job_ids": set(),
                "mention_count": 0,
                "variants": Counter(),
                "source_kinds": Counter(),
            },
        )
        group["mention_count"] = int(group["mention_count"]) + 1
        if job_id:
            cast_job_ids = group["job_ids"]  # type: ignore[assignment]
            cast_job_ids.add(job_id)
        variants: Counter[str] = group["variants"]  # type: ignore[assignment]
        variants[display_variant] += 1
        source_kinds: Counter[str] = group["source_kinds"]  # type: ignore[assignment]
        source_kinds[source_kind] += 1

    bucket_rows: dict[str, list[dict[str, object]]] = {
        BUCKET_GENERALIZED_TECH: [],
        BUCKET_BUSINESS_DOMAIN: [],
        BUCKET_SOFT_SKILL: [],
    }
    bucket_summaries: dict[str, dict[str, object]] = {}

    for (bucket, title), group in grouped.items():
        variants_counter: Counter[str] = group["variants"]  # type: ignore[assignment]
        job_ids: set[str] = group["job_ids"]  # type: ignore[assignment]
        ordered_variants = [
            variant
            for variant, _ in sorted(variants_counter.items(), key=lambda item: (-item[1], item[0].casefold()))
        ]
        row = {
            "bucket": bucket,
            "title": title,
            "semantic_variants": "、".join(ordered_variants),
            "frequency": len(job_ids),
            "job_count": len(job_ids),
            "mention_count": int(group["mention_count"]),
        }
        bucket_rows[bucket].append(row)

    for bucket, rows_for_bucket in bucket_rows.items():
        rows_for_bucket.sort(key=lambda row: (-int(row["frequency"]), -int(row["mention_count"]), str(row["title"]).casefold()))
        bucket_summaries[bucket] = {
            "title_count": len(rows_for_bucket),
            "job_count_total": sum(int(row["job_count"]) for row in rows_for_bucket),
            "mention_count_total": sum(int(row["mention_count"]) for row in rows_for_bucket),
            "top_10": [
                {
                    "title": row["title"],
                    "frequency": row["frequency"],
                    "semantic_variants": row["semantic_variants"],
                }
                for row in rows_for_bucket[:10]
            ],
        }

    combined_rows = [
        {
            "bucket": row["bucket"],
            "title": row["title"],
            "semantic_variants": row["semantic_variants"],
            "frequency": row["frequency"],
            "job_count": row["job_count"],
            "mention_count": row["mention_count"],
        }
        for bucket in (BUCKET_GENERALIZED_TECH, BUCKET_BUSINESS_DOMAIN, BUCKET_SOFT_SKILL)
        for row in bucket_rows[bucket]
    ]
    combined_rows.sort(
        key=lambda row: (
            -int(row["frequency"]),
            -int(row["mention_count"]),
            AGGREGATION_BUCKET_ORDER[str(row["bucket"])],
            str(row["title"]).casefold(),
        )
    )

    final_tables = {
        "combined": combined_rows,
        "generalized_tech": bucket_rows[BUCKET_GENERALIZED_TECH],
        "business_domain": bucket_rows[BUCKET_BUSINESS_DOMAIN],
        "soft_skill": bucket_rows[BUCKET_SOFT_SKILL],
    }

    summary = {
        "accepted_rows": accepted_rows,
        "dropped_rows": dropped_rows,
        "accepted_jobs": len(accepted_jobs),
        "accepted_variant_rows": accepted_variant_rows,
        "final_title_count": len(combined_rows),
        "drop_reason_counts": dict(drop_reason_counts),
        "filtered_noise_samples": [
            {"phrase": phrase, "count": count}
            for phrase, count in noise_samples.most_common(20)
        ],
        "excluded_tech_samples": [
            {"phrase": phrase, "count": count}
            for phrase, count in excluded_tech_samples.most_common(20)
        ],
        "bucket_summaries": bucket_summaries,
    }
    return final_tables, summary


NARRATIVE_TITLE_FOCUS: dict[str, str] = {
    "Software Engineering": "强调从需求到上线的端到端工程方法，关注可维护性、可扩展性和持续交付。",
    "Web Development": "强调 Web 页面、应用交互和浏览器端交付链路。",
    "Database Systems": "强调数据建模、事务一致性、查询效率和存储治理。",
    "Data Science / Analytics": "强调把数据转成洞察、指标和决策建议。",
    "Full-Stack Development": "强调前后端协同实现和一体化交付。",
    "Data Engineering": "强调数据采集、清洗、建模和管道治理。",
    "Architecture / Systems": "强调系统拆分、扩展性、容量规划和长期演进。",
    "Backend Development": "强调服务端业务逻辑、接口设计和数据读写。",
    "Frontend Development": "强调页面交互、组件组织和用户体验呈现。",
    "Enterprise Software / SaaS": "强调面向企业客户的标准化产品交付和多租户能力。",
    "Finance / FinTech": "强调金融业务数字化、支付结算和资金流转场景。",
    "Banking": "强调账户、授信、支付和资金安全。",
    "Risk / Fraud / Credit": "强调风险识别、欺诈防控和授信决策。",
    "Trading": "强调行情、订单、撮合和交易执行。",
    "Retail / E-commerce": "强调商品、交易、订单和用户增长链路。",
    "Consumer Products / Consumer Internet": "强调面向大众用户的产品增长和体验优化。",
    "Media / Advertising": "强调内容分发、投放效果和商业化转化。",
    "Gaming / Entertainment": "强调内容玩法、用户留存和实时体验。",
    "Logistics / Supply Chain": "强调仓储、运输和供应链协同。",
    "Manufacturing / Industrial": "强调生产流程、设备协同和制造数字化。",
    "Energy / Utilities": "强调能源生产、调度和运营监控。",
    "Real Estate / PropTech": "强调房产交易、租赁和资产管理流程数字化。",
    "Telecom": "强调通信网络、运营支撑和服务质量保障。",
    "Public Sector / Government": "强调政务流程、公共服务和合规交付。",
    "Education / EdTech": "强调教学、学习和教育运营流程的数字化。",
    "Healthcare": "强调医疗流程、合规与服务效率优化。",
    "Life Sciences / Biotech": "强调研发、试验和监管合规。",
    "Travel / Hospitality": "强调出行、预订和服务履约体验。",
    "B2B / B2C": "强调同时兼顾企业客户和个人用户的产品设计与交付。",
    "合作": "强调协作、沟通、跨团队配合和利益相关方对齐。",
    "管理/领导": "强调带人、推进闭环、承担结果和驱动团队前进。",
    "思辨与创新": "强调结构化分析、问题拆解、学习迁移和提出更优方案。",
    "抗压": "强调在压力、变化和多任务环境下保持稳定推进、节奏控制和质量把关。",
}


NARRATIVE_GROUP_SPECS: tuple[NarrativeGroupSpec, ...] = (
    NarrativeGroupSpec(
        group_label="软件研发与产品交付",
        titles=(
            "Software Engineering",
            "Web Development",
            "Full-Stack Development",
            "Backend Development",
            "Frontend Development",
            "Architecture / Systems",
            "Enterprise Software / SaaS",
            "B2B / B2C",
        ),
        common_introduction="这组标题描述的是把业务需求转成可维护软件产品的研发链路，强调设计、实现、联调和上线的完整交付。",
        common_business_scenario="常见于企业内部平台、SaaS 产品和面向用户的业务系统，团队需要在功能、性能和可维护性之间平衡。",
    ),
    NarrativeGroupSpec(
        group_label="数据平台与分析决策",
        titles=(
            "Database Systems",
            "Data Engineering",
            "Data Science / Analytics",
            "Architecture / Systems",
            "思辨与创新",
        ),
        common_introduction="这组标题描述的是把业务数据转成可查询、可分析、可决策的资产，覆盖存储、加工、建模和解释。",
        common_business_scenario="常见于报表、数仓、指标体系、实验分析和数据治理场景，团队需要兼顾稳定性与分析效率。",
    ),
    NarrativeGroupSpec(
        group_label="行业数字化转型",
        titles=(
            "Enterprise Software / SaaS",
            "Finance / FinTech",
            "Banking",
            "Risk / Fraud / Credit",
            "Trading",
            "Retail / E-commerce",
            "Consumer Products / Consumer Internet",
            "Media / Advertising",
            "Gaming / Entertainment",
            "Logistics / Supply Chain",
            "Manufacturing / Industrial",
            "Energy / Utilities",
            "Real Estate / PropTech",
            "Telecom",
            "Education / EdTech",
            "Healthcare",
            "Life Sciences / Biotech",
            "Public Sector / Government",
            "Travel / Hospitality",
            "B2B / B2C",
        ),
        common_introduction="这组标题描述的是业务所处的行业和场景，强调在特定行业约束下把通用产品和流程数字化。",
        common_business_scenario="常见于需要理解行业规则、交易流程、监管要求或用户行为的团队，重点是把平台能力落到具体行业语境里。",
    ),
    NarrativeGroupSpec(
        group_label="跨团队协作与项目推进",
        titles=(
            "合作",
            "管理/领导",
            "思辨与创新",
        ),
        common_introduction="这组标题描述的是团队协作、对齐和推进结果的能力，强调跨角色沟通和共同闭环。",
        common_business_scenario="常见于需求推进、方案评审、里程碑管理和协作交付场景，团队需要把不同角色拉到同一目标上。",
    ),
    NarrativeGroupSpec(
        group_label="自驱成长与执行质量",
        titles=(
            "思辨与创新",
            "抗压",
            "管理/领导",
        ),
        common_introduction="这组标题描述的是个人的工作方式和执行质量，强调自驱、节奏控制和持续改进。",
        common_business_scenario="常见于快速变化或高不确定性的工作环境，团队需要成员能够独立推进任务并持续提升结果质量。",
    ),
    NarrativeGroupSpec(
        group_label="高变化环境下的个人执行",
        titles=(
            "抗压",
            "思辨与创新",
            "管理/领导",
            "合作",
        ),
        common_introduction="这组标题描述的是高变化环境里的个人执行方式，强调快速调整、独立推进和持续优化。",
        common_business_scenario="常见于目标变化快、协同链路长或需要不断试错的团队，成员既要能自我驱动，也要能把事情落到结果上。",
    ),
    NarrativeGroupSpec(
        group_label="产品增长与商业化",
        titles=(
            "Retail / E-commerce",
            "Consumer Products / Consumer Internet",
            "Media / Advertising",
            "Gaming / Entertainment",
            "B2B / B2C",
            "合作",
            "思辨与创新",
        ),
        common_introduction="这组标题描述的是面向用户增长和商业化转化的业务场景，强调产品、内容和运营协同。",
        common_business_scenario="常见于增长、营销、内容和商业化团队，需要把用户触达、转化和留存串成闭环。",
    ),
    NarrativeGroupSpec(
        group_label="金融科技与风控交易",
        titles=(
            "Finance / FinTech",
            "Banking",
            "Risk / Fraud / Credit",
            "Trading",
            "思辨与创新",
            "管理/领导",
            "合作",
        ),
        common_introduction="这组标题描述的是金融业务的交易、资金、风控和合规场景，强调高可信度和高准确性。",
        common_business_scenario="常见于支付、授信、结算、交易和风险控制团队，需要同时满足业务效率、合规与稳定性。",
    ),
    NarrativeGroupSpec(
        group_label="产业运营与线下基础设施",
        titles=(
            "Logistics / Supply Chain",
            "Manufacturing / Industrial",
            "Energy / Utilities",
            "Real Estate / PropTech",
            "Telecom",
            "Travel / Hospitality",
            "合作",
            "抗压",
        ),
        common_introduction="这组标题描述的是围绕线下运营、供应链和基础设施的行业场景，强调流程协同和服务连续性。",
        common_business_scenario="常见于仓储运输、生产调度、能源运维、资产管理和通信服务团队，需要把复杂流程在线化并保持稳定运行。",
    ),
    NarrativeGroupSpec(
        group_label="公共服务与受监管行业",
        titles=(
            "Public Sector / Government",
            "Education / EdTech",
            "Healthcare",
            "Life Sciences / Biotech",
            "Travel / Hospitality",
            "管理/领导",
            "思辨与创新",
        ),
        common_introduction="这组标题描述的是受监管或强流程行业中的数字化场景，强调合规、服务质量和流程规范。",
        common_business_scenario="常见于政务、教育、医疗和科研相关团队，需要在满足监管和流程要求的前提下提升服务效率。",
    ),
    NarrativeGroupSpec(
        group_label="数据驱动与实验分析",
        titles=(
            "Data Science / Analytics",
            "Data Engineering",
            "Database Systems",
            "思辨与创新",
            "合作",
        ),
        common_introduction="这组标题描述的是用数据评估产品和业务效果的分析场景，强调从采集到解释的完整链路。",
        common_business_scenario="常见于实验分析、指标监控、增长分析和经营复盘团队，需要把数据结果转成可行动建议。",
    ),
    NarrativeGroupSpec(
        group_label="平台架构与工程治理",
        titles=(
            "Software Engineering",
            "Web Development",
            "Architecture / Systems",
            "Backend Development",
            "Frontend Development",
            "Full-Stack Development",
            "Data Engineering",
            "Database Systems",
            "思辨与创新",
            "管理/领导",
        ),
        common_introduction="这组标题描述的是保障平台长期演进的工程治理能力，强调架构、稳定性、质量和边界控制。",
        common_business_scenario="常见于复杂系统、容量规划、稳定性治理和规范化开发场景，团队需要既能落地功能，也能守住系统底线。",
    ),
)


def build_merged_narratives(final_tables: dict[str, list[dict[str, object]]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    combined_rows = final_tables["combined"]
    title_meta = {
        str(row["title"]): row
        for row in combined_rows
    }

    group_rows: list[dict[str, object]] = []
    title_to_group_count: Counter[str] = Counter()
    used_titles: set[str] = set()

    for spec in NARRATIVE_GROUP_SPECS:
        present_titles = [title for title in spec.titles if title in title_meta]
        if not present_titles:
            continue
        ordered_titles = sorted(
            present_titles,
            key=lambda title: (
                -int(title_meta[title]["frequency"]),
                -int(title_meta[title]["job_count"]),
                title.casefold(),
            ),
        )
        for title in ordered_titles:
            title_to_group_count[title] += 1
            used_titles.add(title)

        focus_rows = [
            {
                "title": title,
                "bucket": title_meta[title]["bucket"],
                "focus": NARRATIVE_TITLE_FOCUS.get(title, f"强调该场景中的关键能力和实际落地方式。"),
                "frequency": int(title_meta[title]["frequency"]),
            }
            for title in ordered_titles
        ]
        group_rows.append(
            {
                "group_label": spec.group_label,
                "merged_titles_text": "、".join(ordered_titles),
                "titles": ordered_titles,
                "common_introduction": spec.common_introduction,
                "common_business_scenario": spec.common_business_scenario,
                "title_focuses": focus_rows,
                "title_focuses_text": "\n".join(f"{row['title']}：{row['focus']}" for row in focus_rows),
                "title_count": len(ordered_titles),
                "bucket_mix": {
                    bucket: sum(1 for title in ordered_titles if title_meta[title]["bucket"] == bucket)
                    for bucket in ("generalized_tech", "business_domain", "soft_skill")
                },
            }
        )

    group_rows.sort(key=lambda row: (row["group_label"], -int(row["title_count"])))
    singleton_titles = [title for title, count in title_to_group_count.items() if count == 1]
    summary_node = {
        "group_count": len(group_rows),
        "covered_title_count": len(used_titles),
        "singleton_count": len(singleton_titles),
        "singleton_titles": sorted(singleton_titles),
        "title_group_counts": dict(sorted(title_to_group_count.items(), key=lambda item: (-item[1], item[0].casefold()))),
    }
    return group_rows, summary_node


def write_merged_narratives_outputs(out_dir: Path, rows: list[dict[str, object]], summary_node: dict[str, object]) -> None:
    write_json(
        out_dir / "merged_narratives.json",
        {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "summary": summary_node,
            "groups": rows,
        },
    )
    write_csv(
        out_dir / "merged_narratives.csv",
        [
            {
                "group_label": row["group_label"],
                "merged_titles_text": row["merged_titles_text"],
                "common_introduction": row["common_introduction"],
                "common_business_scenario": row["common_business_scenario"],
                "title_focuses": row["title_focuses_text"],
                "title_count": row["title_count"],
                "bucket_mix": "、".join(
                    f"{bucket}={count}"
                    for bucket, count in row["bucket_mix"].items()
                    if count
                ),
            }
            for row in rows
        ],
        [
            "group_label",
            "merged_titles_text",
            "common_introduction",
            "common_business_scenario",
            "title_focuses",
            "title_count",
            "bucket_mix",
        ],
    )


def clean_display_phrase(raw_phrase: str) -> str:
    text = normalize_text(raw_phrase)
    text = text.replace("\u2010", "-").replace("\u2011", "-").replace("\u2012", "-").replace("\u2013", "-").replace("\u2014", "-")
    text = re.sub(r"\s*/\s*", "/", text)
    text = re.sub(r"\s*-\s*", "-", text)
    text = re.sub(r"\s+", " ", text).strip(" ,;:.")

    if not text:
        return text

    special = {
        "api": "API",
        "apis": "APIs",
        "b2b": "B2B",
        "b2c": "B2C",
        "ci/cd": "CI/CD",
        "devops": "DevOps",
        "fullstack": "Full Stack",
        "mpp": "MPP",
        "nosql": "NoSQL",
        "mlops": "MLOps",
        "qa": "QA",
        "ui": "UI",
        "ux": "UX",
        "sql": "SQL",
        "kpi": "KPI",
        "kpis": "KPIs",
    }
    if text.casefold() in special:
        return special[text.casefold()]

    parts = re.split(r"(\s+|-|/)", text)
    normalized: list[str] = []
    for part in parts:
        if not part or part.isspace() or part in {"-", "/"}:
            normalized.append(part)
            continue
        if part.casefold() in special:
            normalized.append(special[part.casefold()])
            continue
        if any(ch.isupper() for ch in part[1:]) and any(ch.islower() for ch in part):
            normalized.append(part)
            continue
        if part.isupper() or any(ch.isdigit() for ch in part):
            normalized.append(part.upper())
            continue
        normalized.append(part[:1].upper() + part[1:].lower())
    return "".join(normalized)


def iter_source_texts(job: dict[str, Any]) -> list[tuple[str, str, str]]:
    structured = job.get("full_job_json") or {}
    detail = structured.get("detailQualifications") if isinstance(structured, dict) else {}
    results: list[tuple[str, str, str]] = []

    for field in REQUIREMENT_TEXT_FIELDS:
        value = normalize_text(job.get(field))
        if value:
            results.append((field, "text", value))

    if isinstance(detail, dict):
        for section_name in ("mustHave", "preferredHave"):
            section = detail.get(section_name, {})
            if not isinstance(section, dict):
                continue
            for kind in ("hardSkill", "softSkill"):
                items = section.get(kind, [])
                if not isinstance(items, list):
                    continue
                for idx, item in enumerate(items):
                    if isinstance(item, dict):
                        phrase = normalize_text(item.get("skill"))
                    else:
                        phrase = normalize_text(item)
                    if phrase:
                        results.append((f"detailQualifications.{section_name}.{kind}", f"{section_name}.{kind}", phrase))
    return results


def extract_matches(text: str) -> list[tuple[str, str, str]]:
    """Return (rule_id, bucket, normalized_phrase) tuples for a source text."""
    if not text:
        return []
    accepted: list[tuple[int, int, PatternRule, re.Match[str]]] = []
    for rule_index, rule in enumerate(RULES):
        for match in rule.pattern.finditer(text):
            accepted.append((match.start(), match.end(), rule, match))

    accepted.sort(key=lambda item: (-(item[1] - item[0]), item[0], item[2].rule_id))
    chosen: list[tuple[int, int, PatternRule, re.Match[str]]] = []
    occupied: list[tuple[int, int]] = []
    for start, end, rule, match in accepted:
        overlap = any(not (end <= used_start or start >= used_end) for used_start, used_end in occupied)
        if overlap:
            continue
        occupied.append((start, end))
        chosen.append((start, end, rule, match))

    chosen.sort(key=lambda item: (item[0], item[2].rule_id))
    results: list[tuple[str, str, str]] = []
    for _, _, rule, match in chosen:
        phrase = clean_display_phrase(match.group(0))
        if rule.bucket == "generalized_tech" and phrase in GENERALIZED_TECH_EXCLUDED:
            continue
        results.append((rule.rule_id, rule.bucket, phrase))
    return results


def collect_phrase_rows(catalog: list[dict[str, Any]]) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, SourceStats], dict[str, int]]:
    source_stats: dict[str, SourceStats] = defaultdict(SourceStats)
    per_source_phrase_sets: dict[str, set[str]] = defaultdict(set)
    row_map: dict[tuple[str, str], dict[str, object]] = {}
    bucket_counts: Counter[str] = Counter()
    jobs_with_any_phrase = 0

    for job in catalog:
        per_job_keys: dict[tuple[str, str], dict[str, object]] = {}
        matched_any = False
        job_content_seen: set[str] = set()
        job_candidate_seen: set[str] = set()

        for source_field, source_kind, value in iter_source_texts(job):
            stats = source_stats[source_field]
            if value and source_field not in job_content_seen:
                stats.jobs_with_content += 1
                job_content_seen.add(source_field)
            matches = extract_matches(value)
            if matches:
                matched_any = True
                if source_field not in job_candidate_seen:
                    stats.jobs_with_candidate += 1
                    job_candidate_seen.add(source_field)
            for rule_id, bucket, phrase in matches:
                stats.raw_match_count += 1
                stats.unique_phrases.add(phrase)
                stats.phrase_counts[phrase] += 1
                per_source_phrase_sets[source_field].add(phrase)

                row_key = (bucket, phrase)
                row = per_job_keys.get(row_key)
                if row is None:
                    row = {
                        "job_id": job["job_id"],
                        "job_title": job["job_title"],
                        "company_name": job["company_name"],
                        "source_scope": job["source_scope"],
                        "bucket_hint": bucket,
                        "normalized_phrase": phrase,
                        "raw_variants": set(),
                        "source_fields": set(),
                        "source_kinds": set(),
                        "rule_ids": set(),
                    }
                    per_job_keys[row_key] = row
                row["raw_variants"].add(phrase)
                row["source_fields"].add(source_field)
                row["source_kinds"].add(source_kind)
                row["rule_ids"].add(rule_id)
                bucket_counts[bucket] += 1

        if matched_any:
            jobs_with_any_phrase += 1
        for row in per_job_keys.values():
            row_map[(str(row["job_id"]), str(row["bucket_hint"]), str(row["normalized_phrase"]))] = row

    phrase_rows: list[dict[str, object]] = []
    for row in row_map.values():
        phrase_rows.append(
            {
                "job_id": row["job_id"],
                "job_title": row["job_title"],
                "company_name": row["company_name"],
                "source_scope": row["source_scope"],
                "bucket_hint": row["bucket_hint"],
                "normalized_phrase": row["normalized_phrase"],
                "raw_variants": sorted(row["raw_variants"]),
                "source_fields": sorted(row["source_fields"]),
                "source_kinds": sorted(row["source_kinds"]),
                "rule_ids": sorted(row["rule_ids"]),
            }
        )

    phrase_rows.sort(key=lambda row: (str(row["bucket_hint"]), str(row["normalized_phrase"]), str(row["job_id"])))

    coverage_rows: list[dict[str, object]] = []
    for source_field in REQUIREMENT_TEXT_FIELDS + tuple(f"detailQualifications.{section}.{kind}" for section in ("mustHave", "preferredHave") for kind in ("hardSkill", "softSkill")):
        stats = source_stats.get(source_field, SourceStats())
        coverage_rows.append(
            {
                "source_field": source_field,
                "jobs_with_content": stats.jobs_with_content,
                "jobs_with_candidate": stats.jobs_with_candidate,
                "raw_match_count": stats.raw_match_count,
                "unique_phrases": len(stats.unique_phrases),
                "top_phrases": "、".join(phrase for phrase, _ in stats.phrase_counts.most_common(5)),
            }
        )

    return phrase_rows, coverage_rows, source_stats, dict(bucket_counts)


def build_summary(
    *,
    catalog: list[dict[str, Any]],
    phrase_rows: list[dict[str, object]],
    coverage_rows: list[dict[str, object]],
    bucket_counts: dict[str, int],
    source_stats: dict[str, SourceStats],
) -> dict[str, object]:
    jobs_with_any_phrase = len({row["job_id"] for row in phrase_rows})
    per_source_summary = []
    for row in coverage_rows:
        per_source_summary.append(
            {
                "source_field": row["source_field"],
                "jobs_with_content": row["jobs_with_content"],
                "jobs_with_candidate": row["jobs_with_candidate"],
                "raw_match_count": row["raw_match_count"],
                "unique_phrases": row["unique_phrases"],
            }
        )

    top_phrases = Counter()
    for row in phrase_rows:
        top_phrases[str(row["normalized_phrase"])] += 1

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "catalog_record_count": len(catalog),
        "jobs_with_any_candidate": jobs_with_any_phrase,
        "phrase_row_count": len(phrase_rows),
        "bucket_counts": bucket_counts,
        "ignored_source_fields": list(IGNORED_FIELDS),
        "source_field_coverage": per_source_summary,
        "top_phrases": [
            {"normalized_phrase": phrase, "job_count": count}
            for phrase, count in top_phrases.most_common(50)
        ],
        "source_statistics": {
            source_field: {
                "jobs_with_content": stats.jobs_with_content,
                "jobs_with_candidate": stats.jobs_with_candidate,
                "raw_match_count": stats.raw_match_count,
                "unique_phrases": len(stats.unique_phrases),
            }
            for source_field, stats in sorted(source_stats.items())
        },
    }


def write_extraction_outputs(out_dir: Path, phrase_rows: list[dict[str, object]], coverage_rows: list[dict[str, object]], summary: dict[str, object]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(out_dir / "normalized_phrase_rows.jsonl", phrase_rows)
    write_csv(
        out_dir / "section_coverage.csv",
        coverage_rows,
        ["source_field", "jobs_with_content", "jobs_with_candidate", "raw_match_count", "unique_phrases", "top_phrases"],
    )


def write_frequency_outputs(out_dir: Path, tables: dict[str, list[dict[str, object]]]) -> None:
    combined_rows = tables["combined"]
    write_csv(
        out_dir / "phrase_frequency_combined.csv",
        combined_rows,
        ["bucket", "title", "semantic_variants", "frequency", "job_count", "mention_count"],
    )
    write_csv(
        out_dir / "generalized_tech_terms.csv",
        tables["generalized_tech"],
        ["title", "semantic_variants", "frequency", "job_count", "mention_count"],
    )
    write_csv(
        out_dir / "business_domains.csv",
        tables["business_domain"],
        ["title", "semantic_variants", "frequency", "job_count", "mention_count"],
    )
    write_csv(
        out_dir / "soft_skills.csv",
        tables["soft_skill"],
        ["title", "semantic_variants", "frequency", "job_count", "mention_count"],
    )


def run(jd_catalog_path: Path, portfolio_index_path: Path, out_dir: Path) -> dict[str, object]:
    catalog = build_jd_catalog(jd_catalog_path, portfolio_index_path)
    phrase_rows, coverage_rows, source_stats, bucket_counts = collect_phrase_rows(catalog)
    extraction_summary = build_summary(
        catalog=catalog,
        phrase_rows=phrase_rows,
        coverage_rows=coverage_rows,
        bucket_counts=bucket_counts,
        source_stats=source_stats,
    )
    write_extraction_outputs(out_dir, phrase_rows, coverage_rows, extraction_summary)
    frequency_tables, aggregation_summary = build_frequency_tables(out_dir / "normalized_phrase_rows.jsonl")
    write_frequency_outputs(out_dir, frequency_tables)
    merged_narratives, merged_narratives_summary = build_merged_narratives(frequency_tables)
    write_merged_narratives_outputs(out_dir, merged_narratives, merged_narratives_summary)
    summary = {**extraction_summary, **aggregation_summary, "merged_narratives_summary": merged_narratives_summary}
    write_json(out_dir / "summary.json", summary)
    return summary


def main() -> int:
    args = parse_args()
    run(Path(args.jd_catalog_path), Path(args.portfolio_index_path), Path(args.out))
    return 0
