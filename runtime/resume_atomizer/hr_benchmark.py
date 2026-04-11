#!/usr/bin/env python3
"""Orchestrate the 22-case resume benchmark and blind HR pair payloads."""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from generate_resume import JD_ROLE_SIGNALS, generate_resume_artifacts
from validate_resume import validate_resume_content

PARSED_RESUMES_PATH = SCRIPT_DIR / "parsed_resumes.json"
RESUME_CATALOG_PATH = PROJECT_ROOT / "classification" / "resume_catalog.json"
STORE_PATH = SCRIPT_DIR / "consolidated_atom_store.json"
TECH_PROFILE_PATH = SCRIPT_DIR / "tech_profile_matrix.json"
RESUME_DIR = PROJECT_ROOT / "resumes"
OUTPUT_DIR = SCRIPT_DIR / "output"
BENCHMARK_DIR = OUTPUT_DIR / "hr_benchmark"
GENERATED_DIR = BENCHMARK_DIR / "generated"

HR_RUBRIC = """You are an experienced HR recruiter screening software-engineering resumes.
Compare Resume A and Resume B for this JD.

Pass 1: judge competitiveness only from the JD and resume text.
Pass 2: use the evidence appendix to judge realism, exaggeration risk, and career coherence.

Score each resume 1-5 on:
1. Competitiveness for this JD
2. Realism / credibility
3. Exaggeration risk
4. Career coherence

Penalize keyword stuffing, seniority inflation, unsupported claims, and abrupt narrative shifts.
Do not prefer the longer resume by default.
Return: winner, confidence, score table, top strengths, top risks, unsupported claims, and the smallest edits needed before submission.
"""

CASE_BLUEPRINTS = [
    {
        "case_id": "01",
        "source_file": "01_AI_Application_GenAI_Integration_Engineer_Resume.md",
        "role_type": "ai_genai",
        "seniority": "mid_1_3y",
        "jd_title": "Applied GenAI Engineer",
        "direction_label": "Applied GenAI / Backend",
    },
    {
        "case_id": "02",
        "source_file": "02_Enterprise_Cloud_Big_Data_Engineering_Resume.md",
        "role_type": "data",
        "seniority": "mid_1_3y",
        "jd_title": "Data Platform Engineer",
        "direction_label": "Data Platform Engineering",
    },
    {
        "case_id": "03",
        "source_file": "03_Cloud_Security_Threat_Engineering_Resume.md",
        "role_type": "security",
        "seniority": "mid_1_3y",
        "jd_title": "Cloud Security Engineer",
        "direction_label": "Cloud Security Engineering",
    },
    {
        "case_id": "04",
        "source_file": "04_ML_AI_Research_Infrastructure_Engineer_Resume.md",
        "role_type": "ai_genai",
        "seniority": "mid_1_3y",
        "jd_title": "ML Platform Engineer",
        "direction_label": "ML Platform / MLOps",
    },
    {
        "case_id": "05",
        "source_file": "05_Responsible_AI_Engineer_Resume.md",
        "role_type": "ai_genai",
        "seniority": "mid_1_3y",
        "jd_title": "Responsible AI Engineer",
        "direction_label": "Responsible AI / AI Safety Infra",
    },
    {
        "case_id": "06",
        "source_file": "06_Full-Stack_Web_Application_Engineer_Resume.md",
        "role_type": "frontend",
        "seniority": "mid_1_3y",
        "jd_title": "Full-Stack Web Engineer",
        "direction_label": "Full-Stack Web Engineering",
    },
    {
        "case_id": "07",
        "source_file": "07_Early-Career_Generalist_SDE_Resume.md",
        "role_type": "backend",
        "seniority": "new_grad",
        "jd_title": "Generalist Software Engineer",
        "direction_label": "Generalist SWE",
    },
    {
        "case_id": "08",
        "source_file": "08_Cloud-Native_Platform_Infrastructure_Engineer_Resume.md",
        "role_type": "cloud_infra",
        "seniority": "mid_1_3y",
        "jd_title": "Cloud Platform Engineer",
        "direction_label": "Platform / Cloud Infrastructure",
    },
    {
        "case_id": "09",
        "source_file": "09_Backend_Distributed_Systems_Generalist_Resume.md",
        "role_type": "backend",
        "seniority": "mid_1_3y",
        "jd_title": "Backend Distributed Systems Engineer",
        "direction_label": "Distributed Backend Engineering",
    },
    {
        "case_id": "10",
        "source_file": "10_DevOps_Platform_Automation_Engineer_Resume.md",
        "role_type": "devops",
        "seniority": "mid_1_3y",
        "jd_title": "DevOps Platform Engineer",
        "direction_label": "DevOps / Platform Automation",
    },
    {
        "case_id": "11",
        "source_file": "11_AI_Field_Solutions_Engineer_Resume.md",
        "role_type": "ai_genai",
        "seniority": "mid_1_3y",
        "jd_title": "AI Solutions Engineer",
        "direction_label": "AI Solutions / Field Engineering",
    },
    {
        "case_id": "12",
        "source_file": "12_Stablecoin_Blockchain_Infrastructure_Resume.md",
        "role_type": "fintech",
        "seniority": "mid_1_3y",
        "jd_title": "Blockchain Infrastructure Engineer",
        "direction_label": "Blockchain / Payments Infrastructure",
    },
    {
        "case_id": "13",
        "source_file": "13_Edge_Infrastructure_Networking_Engineer_Resume.md",
        "role_type": "cloud_infra",
        "seniority": "mid_1_3y",
        "jd_title": "Edge Infrastructure Engineer",
        "direction_label": "Edge / Networking Platform",
    },
    {
        "case_id": "14",
        "source_file": "14_Platform_Reliability_Resilience_Engineer_Resume.md",
        "role_type": "devops",
        "seniority": "mid_1_3y",
        "jd_title": "Site Reliability Engineer",
        "direction_label": "SRE / Reliability",
    },
    {
        "case_id": "15",
        "source_file": "15_Python_Backend_Engineer_FinTech_Resume.md",
        "role_type": "fintech",
        "seniority": "mid_1_3y",
        "jd_title": "Python FinTech Backend Engineer",
        "direction_label": "Python FinTech Backend",
    },
    {
        "case_id": "16",
        "source_file": "16_Frontend_Design_Systems_Engineer_Resume.md",
        "role_type": "frontend",
        "seniority": "mid_1_3y",
        "jd_title": "Frontend Design Systems Engineer",
        "direction_label": "Frontend / Design Systems",
    },
    {
        "case_id": "17",
        "source_file": "17_Embedded_Sensor_Software_Engineer_Resume.md",
        "role_type": "embedded",
        "seniority": "mid_1_3y",
        "jd_title": "Embedded Software Engineer",
        "direction_label": "Embedded / Sensor Systems",
    },
    {
        "case_id": "18",
        "source_file": "18_HPC_Compiler_Engineer_Resume.md",
        "role_type": "hpc_compiler",
        "seniority": "mid_1_3y",
        "jd_title": "HPC Compiler Engineer",
        "direction_label": "HPC / Compiler / GPU",
    },
    {
        "case_id": "19",
        "source_file": "19_Systems_Software_Virtualization_Engineer_Resume.md",
        "role_type": "embedded",
        "seniority": "mid_1_3y",
        "jd_title": "Systems Software Engineer",
        "direction_label": "Systems / Virtualization",
    },
    {
        "case_id": "20",
        "source_file": "20_Zuora_Billing_Developer_Resume.md",
        "role_type": "fintech",
        "seniority": "mid_1_3y",
        "jd_title": "Billing Systems Engineer",
        "direction_label": "Billing / Revenue Systems",
    },
    {
        "case_id": "21",
        "source_file": "21_QA_SDET_Production_Verification_Engineer_Resume.md",
        "role_type": "qa_sdet",
        "seniority": "mid_1_3y",
        "jd_title": "QA SDET Engineer",
        "direction_label": "QA / SDET",
    },
    {
        "case_id": "22",
        "source_file": "22_Mobile_Platform_Engineer_Resume.md",
        "role_type": "mobile",
        "seniority": "mid_1_3y",
        "jd_title": "Mobile Platform Engineer",
        "direction_label": "Mobile Platform",
    },
]

ROLE_FALLBACK_TECH = {
    "ai_genai": ["Python", "LLM", "RAG", "LangChain", "LangGraph", "Prompt Engineering", "PyTorch"],
    "data": ["Python", "SQL", "Spark", "Airflow", "Hive", "Kafka", "PostgreSQL"],
    "security": ["Go", "Python", "Kafka", "TLS/mTLS", "OAuth", "SIEM", "Docker", "Kubernetes", "gRPC", "REST", "DLP"],
    "frontend": ["React", "TypeScript", "JavaScript", "Next.js", "HTML", "CSS", "Component Library", "Responsive Design"],
    "backend": ["Go", "Python", "Java", "Kafka", "PostgreSQL", "Redis", "gRPC", "REST", "Docker", "Kubernetes", "Microservices", "CI/CD"],
    "cloud_infra": ["AWS", "Kubernetes", "Terraform", "Docker", "Helm", "GitHub Actions"],
    "devops": ["Docker", "Kubernetes", "Terraform", "GitHub Actions", "CI/CD", "Jenkins", "ArgoCD"],
    "fintech": ["Go", "Python", "Kafka", "PostgreSQL", "Redis", "gRPC", "REST", "Docker", "Microservices"],
    "embedded": ["C", "C++", "Linux", "ARM", "RTOS", "Device Drivers", "Firmware", "UART", "SPI", "I2C"],
    "hpc_compiler": ["C++", "CUDA", "LLVM", "MPI", "OpenMP", "GPU"],
    "qa_sdet": ["Python", "Selenium", "Appium", "pytest", "Docker", "Kubernetes", "CI/CD", "REST API"],
    "mobile": ["Kotlin", "Swift", "Android", "iOS", "Jetpack", "REST API", "CI/CD", "Jenkins", "Gradle"],
}

ROLE_LABELS = {
    "backend": "Backend Software Engineer",
    "ai_genai": "AI/ML Engineer",
    "data": "Data Engineer",
    "devops": "DevOps Engineer",
    "frontend": "Frontend Engineer",
    "security": "Security Engineer",
    "mobile": "Mobile Engineer",
    "cloud_infra": "Cloud Platform Engineer",
    "fintech": "FinTech Backend Engineer",
    "hpc_compiler": "Systems and HPC Engineer",
    "embedded": "Embedded Software Engineer",
    "qa_sdet": "QA Automation Engineer",
}

SOURCE_NAME_BY_FILE = {}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def slugify(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-")
    return value.lower() or "resume"


def normalize_bullets(text: str) -> str:
    lines = text.splitlines()
    cleaned = []
    seen_summary = False
    for line in lines:
        if not seen_summary:
            if line.strip() == "## Professional Summary":
                seen_summary = True
                cleaned.append(line)
            continue
        if line.startswith("* "):
            cleaned.append("- " + line[2:])
        else:
            cleaned.append(line)
    return "\n".join(cleaned).strip() + "\n"


def anonymize_resume_markdown(text: str) -> str:
    lines = text.splitlines()
    cleaned = []
    seen_content = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## Professional Summary"):
            seen_content = True
        if not seen_content:
            continue
        if stripped.startswith("# "):
            continue
        if re.match(r"^[^|]+@[^|]+\|.*\d", stripped):
            continue
        if stripped.startswith("* "):
            cleaned.append("- " + stripped[2:])
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip() + "\n"


def load_inputs() -> tuple[dict[str, dict], dict[str, dict], dict, dict]:
    parsed_resumes = {item["source_file"]: item for item in load_json(PARSED_RESUMES_PATH)}
    catalog = {item["source_file"]: item for item in load_json(RESUME_CATALOG_PATH)}
    store = load_json(STORE_PATH)
    tech_profiles = load_json(TECH_PROFILE_PATH)["profiles"]
    return parsed_resumes, catalog, store, tech_profiles


def build_jd_text(case: dict, parsed: dict, catalog: dict, tech_profiles: dict) -> str:
    role = case["role_type"]
    seniority = case["seniority"]
    title = ROLE_LABELS[role]
    direction = case["direction_label"]
    profile = tech_profiles[role][seniority]

    catalog_dirs = catalog.get("business_directions", [])[:3]
    catalog_domains = catalog.get("experience_domains", [])[:2]
    source_keywords = []
    for field in ("hard_keywords", "core_stack"):
        source_keywords.extend(catalog.get(field, [])[:8])

    tech_candidates = []
    for bucket in (profile.get("core", []), profile.get("auxiliary", []), ROLE_FALLBACK_TECH[role], source_keywords):
        for item in bucket:
            if item not in tech_candidates:
                tech_candidates.append(item)

    forbidden_terms = ("architect", "senior", "lead", "principal", "staff", "manager", "director")
    tech_candidates = [
        item for item in tech_candidates
        if not any(term in item.lower() for term in forbidden_terms)
    ]

    tech_needed = tech_candidates[:7]
    role_signals = [signal for signal in JD_ROLE_SIGNALS[role] if signal][:3]
    if len(role_signals) < 2:
        role_signals = (role_signals + [title.lower()])[:3]

    if seniority == "new_grad":
        seniority_phrase = "We are hiring a new graduate / entry-level engineer."
    elif seniority == "intern":
        seniority_phrase = "We are hiring an intern for a 12-week internship."
    elif seniority == "senior_5y_plus":
        seniority_phrase = "We are hiring a senior engineer with 5+ years of experience."
    else:
        seniority_phrase = "We are hiring a software engineer with 2+ years of experience."

    requirements = [
        seniority_phrase,
        f"Hands-on experience with {role_signals[0]} and {role_signals[1]}.",
        f"Production delivery using {', '.join(tech_needed[:4])}.",
        f"Familiarity with {direction.lower()} workflows across {', '.join(catalog_dirs[:2])}.",
    ]
    if len(role_signals) > 2:
        requirements.insert(2, f"Comfortable working in {role_signals[2]}-heavy product environments.")

    responsibilities = [
        f"Build and ship {direction.lower()} systems that support {', '.join(catalog_domains)}.",
        f"Partner with product, analytics, and infrastructure teams to deliver {tech_needed[0]}-backed features.",
        f"Keep observability, reliability, and rollout discipline high while working across {direction.lower()} initiatives.",
    ]

    jd_lines = [
        f"We are hiring a {title} for {direction}.",
        "Requirements:",
    ]
    jd_lines.extend(f"- {req}" for req in requirements)
    jd_lines.append("Responsibilities:")
    jd_lines.extend(f"- {resp}" for resp in responsibilities)
    jd_lines.append(f"Preferred technologies: {', '.join(tech_needed)}.")
    return "\n".join(jd_lines) + "\n"


def extract_text_list(items: list[dict[str, Any]], field: str = "text") -> list[str]:
    texts = []
    for item in items:
        value = item.get(field)
        if value:
            texts.append(value)
    return texts


def build_manifest_row(
    case: dict,
    parsed: dict,
    catalog: dict,
    jd_text: str,
    artifact: dict,
    validation_report,
    original_path: Path,
    generated_md_path: Path,
    generated_meta_path: Path,
) -> dict[str, Any]:
    return {
        "case_id": case["case_id"],
        "source_file": case["source_file"],
        "original_resume_path": str(original_path),
        "generated_resume_path": str(generated_md_path),
        "generated_meta_path": str(generated_meta_path),
        "role_type": case["role_type"],
        "atomizer_role_type": artifact["meta"]["jd_profile"]["role_type"],
        "seniority": case["seniority"],
        "jd_title": case["jd_title"],
        "direction_label": case["direction_label"],
        "jd_text": jd_text,
        "jd_profile": artifact["meta"]["jd_profile"],
        "source_summary": extract_text_list(parsed.get("summary", [])),
        "source_skills": extract_text_list(parsed.get("skills_section", [])),
        "business_directions": catalog.get("business_directions", []),
        "experience_domains": catalog.get("experience_domains", []),
        "validation": {
            "status": "PASS" if validation_report.passed else "FAIL",
            "pass_count": validation_report.pass_count,
            "total": validation_report.total,
            "failed_codes": [result.code for result in validation_report.results if not result.passed],
        },
        "include_in_hr": validation_report.passed,
    }


def collect_selected_provenance(store: dict, artifact: dict) -> dict[str, Any]:
    catom_index = {catom["catom_id"]: catom for catom in store.get("catoms", [])}
    catom_index.update({catom["catom_id"]: catom for catom in store.get("summary_catoms", [])})

    selected_items = []
    selected_ids = []
    summary_source_ids = []
    source_resume_ids = set()
    source_atom_ids = set()
    metric_spans = []
    guardrail_hits = []

    for exp_id, items in artifact["selected"].items():
        for score, catom in items:
            catom_id = catom["catom_id"]
            selected_ids.append(catom_id)
            source_atom_ids.update(catom.get("source_atom_ids", []))
            source_resume_ids.update(catom.get("source_resumes", []))
            text = catom.get("_resolved_text", "")
            metric_spans.extend(re.findall(r"\b\d+(?:\.\d+)?(?:%|x|K|M|B)?\b", text))
            selected_items.append(
                {
                    "exp_id": exp_id,
                    "catom_id": catom_id,
                    "score": score,
                    "project_group": catom.get("_project_group"),
                    "achievement": catom.get("achievement"),
                    "parent_exp_id": catom.get("parent_exp_id"),
                    "resolved_text": text,
                    "source_resumes": catom.get("source_resumes", []),
                    "source_atom_ids": catom.get("source_atom_ids", []),
                    "canonical_project_id": catom.get("_project_group") or catom.get("project_group"),
                }
            )

    summary_bullets = artifact["resume_md"].split("## Professional Summary", 1)[-1].split("## Work Experience", 1)[0]
    summary_texts = [line[2:].strip() for line in summary_bullets.splitlines() if line.startswith("- ")]
    bold_terms = sorted(set(re.findall(r"\*\*([^*]+)\*\*", summary_bullets)))
    summary_source_ids = sorted(set(selected_ids))

    for exp_id, items in artifact["selected"].items():
        for _, catom in items:
            text = catom.get("_resolved_text", "").lower()
            if exp_id == "exp-bytedance":
                for blocked in [
                    "led the architecture", "owned the entire", "drove cross-org",
                    "drove company-wide", "spearheaded org-level", "managed a team of",
                    "as tech lead", "as architect", "reporting to vp",
                ]:
                    if blocked in text:
                        guardrail_hits.append({"exp_id": exp_id, "catom_id": catom["catom_id"], "phrase": blocked})
            if exp_id == "exp-temu":
                for blocked in [
                    "led team", "drove business strategy", "spearheaded",
                    "managed a team", "as tech lead", "as architect",
                ]:
                    if blocked in text:
                        guardrail_hits.append({"exp_id": exp_id, "catom_id": catom["catom_id"], "phrase": blocked})

    return {
        "selected_catoms": selected_items,
        "selected_catom_ids": selected_ids,
        "source_resume_ids": sorted(source_resume_ids),
        "source_atom_ids": sorted(source_atom_ids),
        "metric_spans": sorted(set(metric_spans)),
        "seniority_guardrail_hits": guardrail_hits,
        "summary_provenance": {
            "summary_texts": summary_texts,
            "matched_bold_terms": bold_terms,
            "selected_source_catoms": summary_source_ids,
        },
    }


def anonymize_pair_payload(text: str) -> str:
    return anonymize_resume_markdown(normalize_bullets(text))


def build_pair_payload(
    case: dict,
    jd_text: str,
    artifact: dict,
    validation_report,
    original_resume_text: str,
    generated_resume_text: str,
    provenance: dict[str, Any],
    order_rng: random.Random,
) -> tuple[dict[str, Any], dict[str, str]]:
    left_label, right_label = ("A", "B")
    left_text = original_resume_text
    right_text = generated_resume_text
    left_source = "original"
    right_source = "generated"
    if order_rng.random() < 0.5:
        left_text, right_text = right_text, left_text
        left_source, right_source = right_source, left_source

    payload = {
        "case_id": case["case_id"],
        "source_file": case["source_file"],
        "direction_label": case["direction_label"],
        "role_type": case["role_type"],
        "seniority": case["seniority"],
        "jd_title": case["jd_title"],
        "jd_text": jd_text,
        "jd_profile": artifact["meta"]["jd_profile"],
        "blind_prompt": HR_RUBRIC,
        "resume_a": {
            "label": left_label,
            "text": anonymize_pair_payload(left_text),
        },
        "resume_b": {
            "label": right_label,
            "text": anonymize_pair_payload(right_text),
        },
        "evidence_appendix": provenance,
        "validation": {
            "status": "PASS" if validation_report.passed else "FAIL",
            "pass_count": validation_report.pass_count,
            "total": validation_report.total,
            "failed_codes": [result.code for result in validation_report.results if not result.passed],
        },
    }
    return payload, {"A_source": left_source, "B_source": right_source}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _source_from_winner(pair_order: dict[str, str], winner: str) -> str:
    return pair_order.get(f"{winner}_source", "unknown")


def _score_table_line(score_table: dict[str, Any]) -> str:
    pieces = []
    for label in ("A", "B"):
        scores = score_table.get(label, {})
        pieces.append(
            f"{label}={scores.get('competitiveness', '?')}/{scores.get('realism', '?')}/"
            f"{scores.get('exaggeration_risk', '?')}/{scores.get('career_coherence', '?')}"
        )
    return " | ".join(pieces)


def compile_pairwise_report(manifest_path: Path, review_json_path: Path, report_path: Path) -> Path:
    manifest = load_json(manifest_path)
    review = load_json(review_json_path)
    case_lookup = {case["case_id"]: case for case in manifest["cases"]}

    generated_wins = 0
    original_wins = 0
    confidence_total = 0
    lines = [
        "# HR Pairwise Review Report",
        "",
        f"- Total pairs reviewed: {len(review['pair_reviews'])}",
        f"- Review seed: {manifest.get('seed', 'n/a')}",
        "",
        "## Pair Results",
        "",
    ]

    for item in review["pair_reviews"]:
        case = case_lookup[item["case_id"]]
        winner_source = _source_from_winner(case.get("pair_order", {}), item["winner"])
        if winner_source == "generated":
            generated_wins += 1
        elif winner_source == "original":
            original_wins += 1
        confidence_total += int(item.get("confidence", 0))

        lines.extend(
            [
                f"### Case {item['case_id']} — {case['jd_title']}",
                f"- Winner: Resume {item['winner']} ({winner_source})",
                f"- Confidence: {item['confidence']}/5",
                f"- Interview Recommendation: {item['interview_recommendation']}",
                f"- Score Table (competitiveness/realism/exaggeration risk/career coherence): {_score_table_line(item.get('score_table', {}))}",
                f"- Top Reasons: {'; '.join(item.get('top_reasons', []))}",
                f"- Key Concerns: {'; '.join(item.get('key_concerns', []))}",
                f"- Overclaim Flags: {'; '.join(item.get('overclaim_flags', [])) if item.get('overclaim_flags') else 'None noted'}",
                f"- Realism Assessment: {item.get('realism_assessment', '')}",
                f"- Career Trajectory Assessment: {item.get('career_trajectory_assessment', '')}",
                f"- Post-Appendix Note: {item.get('post_appendix_note', '')}",
                f"- Quoted Evidence: {' | '.join(item.get('quoted_evidence', []))}",
                "",
            ]
        )

    pair_count = len(review["pair_reviews"]) or 1
    avg_confidence = confidence_total / pair_count
    lines.extend(
        [
            "## Aggregate Summary",
            "",
            f"- Generated resume wins: {generated_wins}",
            f"- Original resume wins: {original_wins}",
            f"- Average reviewer confidence: {avg_confidence:.2f}/5",
            f"- Common Strengths: {'; '.join(review['aggregate_synthesis'].get('common_strengths', []))}",
            f"- Common Concerns: {'; '.join(review['aggregate_synthesis'].get('common_concerns', []))}",
            f"- Overclaim Patterns: {'; '.join(review['aggregate_synthesis'].get('most_common_overclaim_patterns', []))}",
            f"- Career Coherence Patterns: {'; '.join(review['aggregate_synthesis'].get('career_coherence_patterns', []))}",
            f"- Pipeline Feedback: {'; '.join(review['aggregate_synthesis'].get('five_pipeline_feedback', []))}",
            "",
        ]
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def run(seed: int, output_dir: Path) -> dict[str, Any]:
    parsed_resumes, catalog, store, tech_profiles = load_inputs()
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_dir = output_dir / "hr_benchmark" / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)

    manifest_rows = []
    pair_payloads = []
    validation_failures = []
    order_rng = random.Random(seed)

    for case in CASE_BLUEPRINTS:
        parsed = parsed_resumes[case["source_file"]]
        catalog_entry = catalog[case["source_file"]]
        jd_text = build_jd_text(case, parsed, catalog_entry, tech_profiles)
        artifact = generate_resume_artifacts(jd_text, store=store)

        expected_role = case["role_type"]
        expected_seniority = case["seniority"]
        actual_role = artifact["jd_profile"]["role_type"]
        actual_seniority = artifact["jd_profile"]["seniority"]
        if actual_role != expected_role or actual_seniority != expected_seniority:
            raise RuntimeError(
                f"{case['case_id']} JD parse mismatch: expected {expected_role}/{expected_seniority}, "
                f"got {actual_role}/{actual_seniority}"
            )

        slug = slugify(f"{case['case_id']}_{case['jd_title']}")
        generated_md_path = generated_dir / f"{slug}.md"
        generated_meta_path = generated_dir / f"{slug}.meta.json"
        generated_md_path.write_text(artifact["resume_md"], encoding="utf-8")
        write_json(generated_meta_path, artifact["meta"])

        original_resume_path = RESUME_DIR / case["source_file"]
        original_resume_text = original_resume_path.read_text(encoding="utf-8")

        validation_report = validate_resume_content(
            artifact["resume_md"],
            artifact["meta"],
            resume_name=generated_md_path.name,
            store=store,
        )
        validation_path = generated_dir / f"{slug}.validation.md"
        validation_path.write_text(validation_report.to_text(), encoding="utf-8")

        provenance = collect_selected_provenance(store, artifact)
        manifest_row = build_manifest_row(
            case=case,
            parsed=parsed,
            catalog=catalog_entry,
            jd_text=jd_text,
            artifact=artifact,
            validation_report=validation_report,
            original_path=original_resume_path,
            generated_md_path=generated_md_path,
            generated_meta_path=generated_meta_path,
        )
        manifest_row["validation_report_path"] = str(validation_path)
        manifest_row["provenance"] = provenance
        manifest_rows.append(manifest_row)

        if validation_report.passed:
            pair_payload, order_map = build_pair_payload(
                case=case,
                jd_text=jd_text,
                artifact=artifact,
                validation_report=validation_report,
                original_resume_text=original_resume_text,
                generated_resume_text=artifact["resume_md"],
                provenance=provenance,
                order_rng=order_rng,
            )
            manifest_rows[-1]["pair_order"] = order_map
            pair_payloads.append(pair_payload)
        else:
            validation_failures.append(case["case_id"])

    review_manifest = {
        "seed": seed,
        "case_count": len(CASE_BLUEPRINTS),
        "pass_count": sum(1 for row in manifest_rows if row["validation"]["status"] == "PASS"),
        "fail_count": sum(1 for row in manifest_rows if row["validation"]["status"] != "PASS"),
        "cases": manifest_rows,
    }
    pair_payload_bundle = {
        "seed": seed,
        "hr_rubric": HR_RUBRIC,
        "pair_count": len(pair_payloads),
        "pairs": pair_payloads,
    }

    write_json(output_dir / "review_manifest.json", review_manifest)
    write_json(output_dir / "hr_pair_payloads.json", pair_payload_bundle)

    return {
        "review_manifest": review_manifest,
        "pair_payloads": pair_payload_bundle,
        "validation_failures": validation_failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the HR benchmark manifest and blind pair payloads.")
    parser.add_argument("--seed", type=int, default=20260324, help="Seed for blind A/B ordering")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory for benchmark outputs (defaults to resume_atomizer/output)",
    )
    parser.add_argument(
        "--review-json",
        type=Path,
        help="Optional raw HR review JSON path. When provided, compile hr_pairwise_report.md from review_manifest.json + this file.",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        help="Optional output path for compiled hr_pairwise_report.md",
    )
    args = parser.parse_args()

    if args.review_json:
        report_path = args.report_path or (args.output_dir / "hr_pairwise_report.md")
        compiled = compile_pairwise_report(
            manifest_path=args.output_dir / "review_manifest.json",
            review_json_path=args.review_json,
            report_path=report_path,
        )
        print(f"Compiled report: {compiled}")
        return 0

    benchmark_dir = args.output_dir / "hr_benchmark"
    result = run(seed=args.seed, output_dir=args.output_dir)

    print(f"Generated {result['review_manifest']['case_count']} benchmark cases")
    print(f"Validation PASS: {result['review_manifest']['pass_count']}")
    print(f"Validation FAIL: {result['review_manifest']['fail_count']}")
    print(f"Blind pair payloads ready: {result['pair_payloads']['pair_count']}")
    print(f"Manifest: {args.output_dir / 'review_manifest.json'}")
    print(f"Pair payloads: {args.output_dir / 'hr_pair_payloads.json'}")
    print(f"Generated resumes: {benchmark_dir / 'generated'}")

    return 0 if not result["validation_failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
