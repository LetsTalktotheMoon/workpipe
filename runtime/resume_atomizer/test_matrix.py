#!/usr/bin/env python3
"""Run the 12x4 resume generation coverage matrix."""

from __future__ import annotations

import json
from pathlib import Path

from generate_resume import JD_ROLE_SIGNALS, OUTPUT_DIR, TECH_PROFILE, extract_tech_from_jd, generate_resume_artifacts
from validate_resume import validate_resume_content

ROOT = Path(__file__).parent

ROLES = [
    "backend",
    "ai_genai",
    "data",
    "devops",
    "frontend",
    "security",
    "mobile",
    "cloud_infra",
    "fintech",
    "hpc_compiler",
    "embedded",
    "qa_sdet",
]

SENIORITIES = [
    ("intern", "intern"),
    ("new_grad", "new_grad"),
    ("mid_1_3y", "mid_1_3y"),
    ("senior_5y_plus", "senior_5y+"),
]

ROLE_TITLES = {
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

ROLE_RESPONSIBILITIES = {
    "backend": "Design and build scalable backend services for distributed systems workflows.",
    "ai_genai": "Build AI/ML services for LLM and RAG product features with production APIs.",
    "data": "Develop data pipelines and analytics systems for large-scale data processing.",
    "devops": "Own deployment automation, Kubernetes reliability, CI/CD operations, and platform tooling.",
    "frontend": "Ship customer-facing frontend features and component-driven web experiences.",
    "security": "Build security tooling for threat detection, incident response, SIEM workflows, and access control.",
    "mobile": "Develop Android and iOS mobile application features, REST API integrations, and client-platform tooling.",
    "cloud_infra": "Build infrastructure platform services for Kubernetes and cloud operations.",
    "fintech": "Develop payment architecture, settlement systems, Kafka services, and regulated transaction workflows.",
    "hpc_compiler": "Optimize compiler and HPC workloads across CUDA, LLVM, MPI, and parallel compute.",
    "embedded": "Build embedded Linux, RTOS, firmware, and low-level device driver systems for sensors and devices.",
    "qa_sdet": "Design QA automation strategy, Selenium and Appium frameworks, and release validation workflows.",
}

SENIORITY_INTROS = {
    "intern": "We are hiring a {title} Intern for a 12-week internship.",
    "new_grad": "We are hiring a New Graduate {title}.",
    "mid_1_3y": "We are hiring a {title} with 2+ years of experience.",
    "senior_5y_plus": "We are hiring a Senior {title} with 5+ years of experience.",
}

ROLE_CONCRETE_FALLBACKS = {
    "security": ["Python", "SIEM", "OAuth", "TLS/mTLS", "Incident Response"],
    "fintech": ["Python", "Kafka", "PostgreSQL", "gRPC", "Blockchain"],
    "embedded": ["C", "C++", "Embedded Linux", "RTOS", "CMake"],
    "mobile": ["Kotlin", "Swift", "Android", "iOS", "Jetpack", "REST API"],
    "qa_sdet": ["Python", "pytest", "Selenium", "Appium", "CI/CD"],
}


def load_profiles() -> dict:
    return json.loads(Path(TECH_PROFILE).read_text(encoding="utf-8"))["profiles"]


def dedupe_keep_order(items: list[str]) -> list[str]:
    seen = set()
    ordered = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def build_test_jd(role: str, seniority: str, profiles: dict) -> str:
    title = ROLE_TITLES[role]
    intro = SENIORITY_INTROS[seniority].format(title=title)
    signals = JD_ROLE_SIGNALS[role][:3]
    profile = profiles[role][seniority]
    techs = dedupe_keep_order(
        ROLE_CONCRETE_FALLBACKS.get(role, []) +
        profile.get("core", [])[:4] +
        profile.get("auxiliary", [])[:4]
    )
    if len(extract_tech_from_jd(", ".join(techs))) < 2:
        techs = dedupe_keep_order(ROLE_CONCRETE_FALLBACKS.get(role, []) + techs)
    if not techs:
        techs = ["Python", "SQL", "Docker"]

    signal_text = ", ".join(signals[:2]) if len(signals) >= 2 else signals[0]
    extra_signal = signals[2] if len(signals) > 2 else signals[0]
    tech_text = ", ".join(techs[:5])

    return (
        f"{intro}\n"
        f"We need someone with hands-on experience in {signal_text}, plus strong delivery around {extra_signal}.\n"
        "Requirements:\n"
        f"- Strong hands-on skills in {tech_text}\n"
        f"- Experience with {signal_text} in production environments\n"
        "- Strong collaboration, ownership, and clear written communication\n"
        "Responsibilities:\n"
        f"- {ROLE_RESPONSIBILITIES[role]}\n"
    )


def classify_report(pass_count: int, total: int) -> str:
    if pass_count == total:
        return "✅"
    if pass_count >= 12:
        return "⚠️"
    return "❌"


def maybe_atom_gap(result: dict) -> str:
    failed = set(result["failed_codes"])
    if result["status"] != "❌":
        return ""
    if {"C03", "C04", "C05", "C06"} & failed and result["total_selected"] < 12:
        return " [ATOM_GAP]"
    return ""


def build_report(results: dict) -> str:
    lines = [
        "# Coverage Matrix Report",
        "",
        "| Direction \\ Seniority | intern | new_grad | mid_1_3y | senior_5y+ |",
        "|----------------------|--------|----------|----------|------------|",
    ]

    accepted = 0
    for role in ROLES:
        cells = []
        for seniority, display in SENIORITIES:
            result = results[(role, seniority)]
            cells.append(f"{result['status']} {result['pass_count']}/{result['total']}")
            if result["status"] in {"✅", "⚠️"}:
                accepted += 1
        lines.append(f"| {role} | {' | '.join(cells)} |")

    total = len(ROLES) * len(SENIORITIES)
    ratio = accepted / total
    lines.extend(
        [
            "",
            f"Total: {accepted}/{total} PASS ({ratio:.0%}) {'✅' if accepted >= 38 else '❌'}",
            "",
            "## Non-green Cases",
        ]
    )

    non_green = []
    for role in ROLES:
        for seniority, _ in SENIORITIES:
            result = results[(role, seniority)]
            if result["status"] == "✅":
                continue
            failed = ", ".join(result["failed_codes"]) if result["failed_codes"] else "none"
            non_green.append(
                f"- {role} / {seniority}: {result['status']} {result['pass_count']}/{result['total']} "
                f"(failed: {failed}){maybe_atom_gap(result)}"
            )

    if non_green:
        lines.extend(non_green)
    else:
        lines.append("- None")

    return "\n".join(lines) + "\n"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    profiles = load_profiles()
    store = json.loads((ROOT / "consolidated_atom_store.json").read_text(encoding="utf-8"))
    results = {}

    for role in ROLES:
        for seniority, _ in SENIORITIES:
            jd_text = build_test_jd(role, seniority, profiles)
            artifacts = generate_resume_artifacts(jd_text, store=store)
            report = validate_resume_content(
                artifacts["resume_md"],
                artifacts["meta"],
                resume_name=f"{role}_{seniority}.md",
                store=store,
            )
            results[(role, seniority)] = {
                "status": classify_report(report.pass_count, report.total),
                "pass_count": report.pass_count,
                "total": report.total,
                "failed_codes": [item.code for item in report.results if not item.passed],
                "total_selected": artifacts["total_selected"],
            }

    report_text = build_report(results)
    output_path = OUTPUT_DIR / "coverage_matrix.md"
    output_path.write_text(report_text, encoding="utf-8")
    print(report_text, end="")

    accepted = sum(1 for result in results.values() if result["status"] in {"✅", "⚠️"})
    return 0 if accepted >= 38 else 1


if __name__ == "__main__":
    raise SystemExit(main())
