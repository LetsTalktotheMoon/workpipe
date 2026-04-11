#!/usr/bin/env python3
"""Validate generated resume markdown outputs against iteration_plan.md checks."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).parent
CONSOLIDATED_STORE = ROOT / "consolidated_atom_store.json"

KEEP_BOLD = {
    "bytedance/tiktok", "didi", "temu", "agile", "scrum", "sdlc",
    "security", "authentication", "authorization", "compliance",
    "risk analytics", "transaction", "payment", "database",
    "data structures", "algorithms", "multi-threaded",
    "object-oriented design", "business requirements",
    "data provenance", "anomaly", "http", "saas",
    "synthetic data generation", "ai/ml", "responsive design",
    "component library", "design-engineering bridge",
    "backend", "frontend", "mobile", "reliability", "scalability",
    "large-scale", "distributed",
}

STRONG_VERBS = [
    "Engineered", "Architected", "Designed", "Built", "Developed",
    "Implemented", "Delivered", "Optimized", "Led", "Authored", "Deployed",
    "Refactored", "Integrated", "Automated", "Instrumented", "Diagnosed",
    "Containerized", "Migrated", "Shipped", "Configured", "Managed",
    "Standardized", "Partnered", "Curated", "Acted", "Identified",
    "Created", "Reduced", "Streamlined", "Consolidated", "Established",
    "Executed", "Resolved", "Constructed", "Processed", "Analyzed",
    "Enhanced", "Transformed", "Provisioned", "Orchestrated", "Calibrated",
    "Traced", "Profiled", "Benchmarked", "Computed", "Extracted",
    "Aggregated", "Normalized", "Visualized", "Parsed", "Modeled",
    "Evaluated", "Prototyped", "Validated", "Simplified", "Composed",
    "Generated", "Parallelized", "Accelerated", "Compressed", "Defined",
    "Achieved", "Coordinated", "Maintained", "Published", "Secured",
    "Upgraded", "Verified", "Wrote", "Indexed", "Launched",
]

BYTE_DANCE_BLOCKLIST = [
    "led the architecture",
    "owned the entire",
    "drove cross-org",
    "drove company-wide",
    "spearheaded org-level",
    "managed a team of",
    "as tech lead",
    "as architect",
    "reporting to vp",
]

TEMU_BLOCKLIST = [
    "led team",
    "drove business strategy",
    "spearheaded",
    "managed a team",
    "as tech lead",
    "as architect",
]

DIDI_BLOCKLIST = [
    "drove company-wide",
    "spearheaded org-level",
    "as cto",
    "as vp",
    "reporting to ceo",
    "managed 50+",
    "managed 100+",
    "company-wide transformation",
]

ACADEMIC_BLOCKLIST = [
    "production traffic",
    "million daily active users",
    "enterprise revenue",
    "company-wide adoption",
    "served millions",
    "商业量产",
    "千万级真实流量",
    "创造企业营收",
]


@dataclass
class CheckResult:
    code: str
    passed: bool
    title: str
    detail: str


@dataclass
class ValidationReport:
    resume_path: Path
    results: list[CheckResult]

    @property
    def pass_count(self) -> int:
        return sum(1 for result in self.results if result.passed)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> bool:
        return self.pass_count == self.total

    def to_text(self) -> str:
        width = 39
        border = "═" * width
        name = self.resume_path.name
        lines = [
            border,
            f"  Validation Report: {name}",
            border,
            "",
        ]
        for result in self.results:
            status = "PASS" if result.passed else "FAIL"
            lines.append(f"{result.code} [{status}] {result.title} — {result.detail}")
        lines.extend(
            [
                "",
                border,
                f"  RESULT: {self.pass_count}/{self.total} PASS {'✅' if self.passed else '❌'}",
                border,
            ]
        )
        return "\n".join(lines)


def _read_resume(resume_path: Path) -> tuple[str, list[str]]:
    text = resume_path.read_text(encoding="utf-8")
    return text, text.splitlines()


def _meta_path_for(resume_path: Path) -> Path:
    return resume_path.with_suffix(".meta.json")


def _get_top_level_section(lines: list[str], header: str) -> list[str]:
    start = None
    for idx, line in enumerate(lines):
        if line.strip() == header:
            start = idx + 1
            break
    if start is None:
        return []

    end = len(lines)
    for idx in range(start, len(lines)):
        line = lines[idx].strip()
        if line == "---":
            end = idx
            break
        if idx > start and line.startswith("## "):
            end = idx
            break
    return lines[start:end]


def _extract_bullet_texts(lines: list[str]) -> list[str]:
    return [line[2:].strip() for line in lines if line.startswith("- ")]


def _extract_bold_terms(text: str) -> list[str]:
    return [match.strip() for match in re.findall(r"\*\*([^*]+)\*\*", text)]


def _normalize_token(token: str) -> str:
    token = token.strip()
    token = re.sub(r"\s+", " ", token)
    token = token.strip(" ,.;:()[]{}")
    return token.lower()


def _term_allowed(term: str, allowed_terms: set[str]) -> bool:
    normalized = _normalize_token(term)
    if not normalized:
        return False
    if normalized in allowed_terms:
        return True
    return any(candidate in normalized or normalized in candidate for candidate in allowed_terms)


def _parse_project_blocks(lines: list[str]) -> list[dict]:
    blocks = []
    academic_active = False
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "### Academic Projects":
            academic_active = True
            continue
        if stripped.startswith("## ") and stripped != "## Education":
            academic_active = False
        if not stripped.startswith("**_Project:"):
            continue

        bullets = []
        cursor = idx + 1
        bullets_started = False
        while cursor < len(lines):
            current = lines[cursor].strip()
            # 遇到结构性分隔符才停止
            if current.startswith("**_Project:") or current.startswith("### ") or current.startswith("## ") or current == "---":
                break
            if not current:
                if bullets_started:
                    break
                cursor += 1
                continue
            if lines[cursor].startswith("- "):
                bullets.append(lines[cursor][2:].strip())
                bullets_started = True
            elif bullets_started:
                break
            cursor += 1
        blocks.append(
            {
                "title": stripped,
                "line": idx + 1,
                "bullet_count": len(bullets),
                "academic": academic_active,
            }
        )
    return blocks


def _parse_work_experience_sections(lines: list[str]) -> list[dict]:
    work_lines = _get_top_level_section(lines, "## Work Experience")
    sections = []
    idx = 0
    while idx < len(work_lines):
        if not work_lines[idx].startswith("### "):
            idx += 1
            continue

        header = work_lines[idx][4:].strip()
        bullets = []
        cursor = idx + 1
        while cursor < len(work_lines) and not work_lines[cursor].startswith("### "):
            if work_lines[cursor].startswith("- "):
                bullets.append(work_lines[cursor][2:].strip())
            cursor += 1
        sections.append({"header": header, "bullets": bullets})
        idx = cursor
    return sections


def _get_academic_bullets(lines: list[str]) -> list[str]:
    bullets = []
    in_academic = False
    for line in lines:
        stripped = line.strip()
        if stripped == "### Academic Projects":
            in_academic = True
            continue
        if in_academic and (stripped == "---" or (stripped.startswith("## ") and stripped != "## Education")):
            break
        if in_academic and line.startswith("- "):
            bullets.append(line[2:].strip())
    return bullets


def _load_meta(meta_path: Path) -> dict | None:
    if not meta_path.exists():
        return None
    return json.loads(meta_path.read_text(encoding="utf-8"))


def _selected_catom_ids(meta: dict | None) -> list[str]:
    if not meta:
        return []
    selected = meta.get("selected_catoms", {})
    ids = []
    if isinstance(selected, dict):
        for items in selected.values():
            if isinstance(items, list):
                for item in items:
                    catom_id = item.get("catom_id")
                    if catom_id:
                        ids.append(catom_id)
    return ids


def _load_selected_bold_terms(catom_ids: list[str], store: dict | None = None) -> set[str]:
    if not catom_ids:
        return set()

    store = store or json.loads(CONSOLIDATED_STORE.read_text(encoding="utf-8"))
    lookup = {}
    for catom in store.get("catoms", []):
        lookup[catom.get("catom_id")] = catom
    for catom in store.get("summary_catoms", []):
        lookup[catom.get("catom_id")] = catom

    bold_terms = set()
    for catom_id in catom_ids:
        catom = lookup.get(catom_id)
        if not catom:
            continue
        for variant in catom.get("text_variants", []):
            bold_terms.update(_extract_bold_terms(variant.get("text", "")))
    return {_normalize_token(term) for term in bold_terms if _normalize_token(term)}


def _validate_c01(lines: list[str]) -> CheckResult:
    required = [
        "## Professional Summary",
        "## Work Experience",
        "## Skills",
        "## Education",
        "## Additional Information",
    ]
    found = sum(1 for header in required if header in lines)
    passed = found == len(required)
    return CheckResult("C01", passed, "结构完整性", f"{found}/5 sections found")


def _validate_c02(lines: list[str]) -> CheckResult:
    summary_lines = _get_top_level_section(lines, "## Professional Summary")
    bullet_count = sum(1 for line in summary_lines if line.startswith("- "))
    return CheckResult("C02", bullet_count == 3, "Summary 条数", f"{bullet_count} bullets")


def _validate_c03(lines: list[str]) -> CheckResult:
    # 统计 Work Experience 区域内的项目
    in_work_exp = False
    work_project_lines: list[int] = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "## Work Experience":
            in_work_exp = True
            continue
        if in_work_exp and stripped.startswith("## "):
            break
        if in_work_exp and stripped.startswith("### Academic"):
            break
        if in_work_exp and stripped.startswith("**_Project:"):
            work_project_lines.append(idx + 1)

    # 也统计 Academic Projects 区域内的项目
    in_academic = False
    academic_count = 0
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("### Academic"):
            in_academic = True
            continue
        if in_academic and stripped.startswith("## "):
            break
        if in_academic and stripped.startswith("**_Project:"):
            academic_count += 1

    total = len(work_project_lines) + academic_count
    # 允许 1-2 个 work projects + academic，总计 >= 2
    passed = total >= 2 and len(work_project_lines) >= 1
    detail = f"{len(work_project_lines)} work + {academic_count} academic = {total} total"
    return CheckResult("C03", passed, "Project 数量", detail)


def _validate_c04(lines: list[str]) -> CheckResult:
    blocks = _parse_project_blocks(lines)
    failures = []
    summaries = []
    for idx, block in enumerate(blocks, start=1):
        bullet_count = block["bullet_count"]
        is_valid = 1 <= bullet_count <= 2 if block["academic"] else 4 <= bullet_count <= 6
        label = f"Project {idx}: {bullet_count} bullets"
        summaries.append(label)
        if not is_valid:
            failures.append(f"L{block['line']} -> {bullet_count}")
    passed = bool(blocks) and not failures
    detail = ", ".join(summaries) if summaries else "0 projects parsed"
    if failures:
        detail += f" (invalid: {', '.join(failures)})"
    return CheckResult("C04", passed, "Project bullet 数", detail)


def _validate_c05(lines: list[str]) -> CheckResult:
    sections = _parse_work_experience_sections(lines)
    counts = []
    failures = []
    for section in sections:
        count = len(section["bullets"])
        counts.append(f"{section['header'].split('|')[1].strip() if '|' in section['header'] else section['header']}: {count}")
        if count < 2:
            failures.append(section["header"])
    passed = bool(sections) and not failures
    detail = ", ".join(counts) if counts else "0 sections parsed"
    if failures:
        detail += f" (below min: {', '.join(failures)})"
    return CheckResult("C05", passed, "经历 bullet 数", detail)


def _validate_c06(lines: list[str]) -> CheckResult:
    work_bullets = _extract_bullet_texts(_get_top_level_section(lines, "## Work Experience"))
    count = len(work_bullets)
    return CheckResult("C06", 12 <= count <= 22, "总 bullet 数", f"{count} (range: 12-22)")


def _validate_c07(lines: list[str]) -> CheckResult:
    hits = []
    for section in _parse_work_experience_sections(lines):
        if "ByteDance" not in section["header"]:
            continue
        for bullet in section["bullets"]:
            lower = bullet.lower()
            for phrase in BYTE_DANCE_BLOCKLIST:
                if phrase in lower:
                    hits.append(phrase)
    return CheckResult("C07", not hits, "职级-ByteDance", f"{len(hits)} blocklist hits")


def _validate_c07b(lines: list[str]) -> CheckResult:
    """DiDi 职级合理性检查"""
    hits = []
    for section in _parse_work_experience_sections(lines):
        if "DiDi" not in section["header"] and "Didi" not in section["header"]:
            continue
        for bullet in section["bullets"]:
            lower = bullet.lower()
            for phrase in DIDI_BLOCKLIST:
                if phrase in lower:
                    hits.append(phrase)
    return CheckResult("C07b", not hits, "职级-DiDi", f"{len(hits)} blocklist hits")


def _validate_c08(lines: list[str]) -> CheckResult:
    hits = []
    for section in _parse_work_experience_sections(lines):
        if "Temu" not in section["header"]:
            continue
        for bullet in section["bullets"]:
            lower = bullet.lower()
            if lower.startswith("architected"):
                hits.append("architected")
            for phrase in TEMU_BLOCKLIST:
                if phrase in lower:
                    hits.append(phrase)
    return CheckResult("C08", not hits, "职级-Temu", f"{len(hits)} blocklist hits")


def _validate_c09(lines: list[str]) -> CheckResult:
    academic_bullets = _get_academic_bullets(lines)
    if not academic_bullets:
        return CheckResult("C09", True, "职级-Academic", "no academic section")

    hits = []
    for bullet in academic_bullets:
        lower = bullet.lower()
        for phrase in ACADEMIC_BLOCKLIST:
            if phrase in lower:
                hits.append(phrase)
    return CheckResult("C09", not hits, "职级-Academic", f"{len(hits)} blocklist hits")


def _validate_c10(lines: list[str], meta: dict | None, store: dict | None = None) -> CheckResult:
    skills_lines = _get_top_level_section(lines, "## Skills")
    tech_expanded = meta.get("jd_profile", {}).get("tech_expanded", []) if meta else []
    selected_terms = _load_selected_bold_terms(_selected_catom_ids(meta), store=store)
    allowed = {_normalize_token(item) for item in tech_expanded} | selected_terms | { _normalize_token(k) for k in KEEP_BOLD }

    skill_terms = []
    for line in skills_lines:
        if not line.startswith("- "):
            continue
        # 优先提取所有 bold terms（新格式：- Category: **term1**, **term2**）
        bold_matches = re.findall(r'\*\*([^*]+)\*\*', line)
        if bold_matches:
            skill_terms.extend(bold_matches)
        else:
            # 兼容旧格式：- **Category:** term1, term2
            match = re.match(r"- \*\*[^*]+:\*\*\s*(.+)", line)
            tail = match.group(1) if match else line[2:].strip()
            skill_terms.extend(term.strip() for term in tail.split(",") if term.strip())

    # 过滤类别标签（如 "Languages:", "Infrastructure & Cloud:"）
    skill_terms = [t for t in skill_terms if not t.endswith(':')]

    matched = sum(1 for term in skill_terms if _normalize_token(term) in allowed)
    total = len(skill_terms)
    ratio = matched / total if total else 0.0
    detail = f"{matched}/{total} matched ({ratio:.0%})" if total else "0 skills parsed"
    return CheckResult("C10", total > 0 and ratio >= 0.9, "Skills ⊆ JD tech", detail)


def _validate_c11(lines: list[str], meta: dict | None) -> CheckResult:
    bold_terms = []
    for bullet in _extract_bullet_texts(_get_top_level_section(lines, "## Work Experience")):
        bold_terms.extend(_extract_bold_terms(bullet))
    tech_expanded = meta.get("jd_profile", {}).get("tech_expanded", []) if meta else []
    allowed = {_normalize_token(item) for item in tech_expanded} | KEEP_BOLD

    matched = sum(1 for term in bold_terms if _term_allowed(term, allowed))
    total = len(bold_terms)
    ratio = matched / total if total else 1.0
    detail = f"{matched}/{total} matched ({ratio:.0%})" if total else "0 bold terms"
    return CheckResult("C11", ratio >= 0.85, "Bullet bold ⊆ JD", detail)


def _validate_c12(lines: list[str], meta: dict | None, store: dict | None = None) -> CheckResult:
    summary_text = "\n".join(_get_top_level_section(lines, "## Professional Summary"))
    summary_terms = _extract_bold_terms(summary_text)
    tech_expanded = meta.get("jd_profile", {}).get("tech_expanded", []) if meta else []
    selected_terms = _load_selected_bold_terms(_selected_catom_ids(meta), store=store)
    allowed = selected_terms | {_normalize_token(item) for item in tech_expanded} | KEEP_BOLD

    matched = sum(1 for term in summary_terms if _term_allowed(term, allowed))
    total = len(summary_terms)
    ratio = matched / total if total else 1.0
    detail = f"{matched}/{total} matched ({ratio:.0%})" if total else "0 summary bold terms"
    return CheckResult("C12", ratio >= 0.9, "Summary tech ⊆ selected", detail)


def _candidate_bullets_for_quality(lines: list[str]) -> list[str]:
    bullets = _extract_bullet_texts(_get_top_level_section(lines, "## Work Experience"))
    bullets.extend(_get_academic_bullets(lines))
    return bullets


def _validate_c13(lines: list[str]) -> CheckResult:
    bullets = _candidate_bullets_for_quality(lines)
    matched = 0
    for bullet in bullets:
        cleaned = bullet.replace("**", "").strip()
        word_match = re.match(r"([A-Za-z][A-Za-z-]*)", cleaned)
        first_word = word_match.group(1) if word_match else ""
        if first_word in STRONG_VERBS:
            matched += 1
    total = len(bullets)
    ratio = matched / total if total else 0.0
    detail = f"{matched}/{total} ({ratio:.0%})" if total else "0 bullets"
    return CheckResult("C13", total > 0 and ratio >= 0.8, "强动词开头", detail)


def _validate_c14(lines: list[str]) -> CheckResult:
    bullets = _candidate_bullets_for_quality(lines)
    in_range = sum(1 for bullet in bullets if 80 <= len(bullet) <= 450)
    total = len(bullets)
    ratio = in_range / total if total else 0.0
    detail = f"{in_range}/{total} in range ({ratio:.0%})" if total else "0 bullets"
    return CheckResult("C14", total > 0 and ratio >= 0.8, "Bullet 长度", detail)


def _validate_c15(meta: dict | None, meta_path: Path) -> CheckResult:
    if meta is None:
        return CheckResult("C15", False, "meta.json 完整", f"missing file: {meta_path.name}")

    jd_profile = meta.get("jd_profile")
    selected_catoms = meta.get("selected_catoms")
    total_selected = meta.get("total_selected")

    checks = [
        isinstance(jd_profile, dict),
        isinstance(jd_profile.get("role_type"), str) if isinstance(jd_profile, dict) else False,
        isinstance(jd_profile.get("seniority"), str) if isinstance(jd_profile, dict) else False,
        isinstance(jd_profile.get("tech_required"), list) and len(jd_profile.get("tech_required", [])) >= 1 if isinstance(jd_profile, dict) else False,
        isinstance(selected_catoms, dict) and len(selected_catoms) >= 2,
        isinstance(total_selected, int) and 12 <= total_selected <= 25,
    ]
    return CheckResult("C15", all(checks), "meta.json 完整", "all fields present" if all(checks) else "missing or invalid required fields")


def validate_resume_content(
    resume_text: str,
    meta: dict | None,
    resume_name: str = "<memory>.md",
    store: dict | None = None,
) -> ValidationReport:
    lines = resume_text.splitlines()
    results = [
        _validate_c01(lines),
        _validate_c02(lines),
        _validate_c03(lines),
        _validate_c04(lines),
        _validate_c05(lines),
        _validate_c06(lines),
        _validate_c07(lines),
        _validate_c07b(lines),
        _validate_c08(lines),
        _validate_c09(lines),
        _validate_c10(lines, meta),
        _validate_c11(lines, meta),
        _validate_c12(lines, meta, store=store),
        _validate_c13(lines),
        _validate_c14(lines),
        _validate_c15(meta, Path(resume_name).with_suffix(".meta.json")),
    ]
    return ValidationReport(resume_path=Path(resume_name), results=results)


def validate_resume_file(resume_path: str | Path, store: dict | None = None) -> ValidationReport:
    resume_path = Path(resume_path)
    text, _ = _read_resume(resume_path)
    meta_path = _meta_path_for(resume_path)
    meta = _load_meta(meta_path)
    return validate_resume_content(text, meta, resume_name=resume_path.name, store=store)


def _iter_resume_files(directory: Path) -> tuple[list[Path], list[Path]]:
    candidates = sorted(directory.glob("*.md"))
    resumés = []
    skipped = []
    for path in candidates:
        if _meta_path_for(path).exists():
            resumés.append(path)
        else:
            skipped.append(path)
    return resumés, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate generated resume markdown")
    parser.add_argument("resume", nargs="?", help="Path to resume markdown file")
    parser.add_argument("--dir", dest="directory", help="Validate all resumes in a directory")
    args = parser.parse_args()

    if not args.resume and not args.directory:
        parser.error("please provide a resume path or --dir")

    reports = []
    if args.directory:
        directory = Path(args.directory)
        resume_files, skipped = _iter_resume_files(directory)
        for path in resume_files:
            reports.append(validate_resume_file(path))
        for skipped_path in skipped:
            print(f"SKIP {skipped_path.name} (missing {skipped_path.with_suffix('.meta.json').name})")
        if not resume_files:
            print("No resume markdown files with matching .meta.json found.")
            return 1
    else:
        reports.append(validate_resume_file(Path(args.resume)))

    for idx, report in enumerate(reports):
        if idx:
            print()
        print(report.to_text())

    return 0 if all(report.passed for report in reports) else 1


if __name__ == "__main__":
    sys.exit(main())
