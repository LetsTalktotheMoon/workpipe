from __future__ import annotations

import re
from dataclasses import dataclass

from config.candidate_framework import is_bytedance_target_company
from models.resume import Resume, SkillCategory


SECTION_ORDER = [
    "## Professional Summary",
    "## Skills",
    "## Experience",
    "## Education",
    "## Achievements",
]

MIN_SKILLS_PER_CATEGORY = 4
MAX_SKILLS_LINE_WORDS = 14

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
PROJECT_HEADING_RE = re.compile(r"^\*\*Project:\s*(.+?)\*\*$")
TIKTOK_TITLE_RE = re.compile(
    r"^###\s+(?!Software Engineer Intern\s+\|)(.+?Intern)\s+\|\s+TikTok\s+·\s+Security\s*$",
    re.IGNORECASE,
)
GO_KEYWORD_RE = re.compile(
    r"(围棋|go\s+2-dan|go\s+amateur\s+2-dan|second-dan|weiqi|china\s+national\s+certified\s+go|city\s+champion)",
    re.IGNORECASE,
)
BYTEDANCE_TARGET_RE = re.compile(r"\b(?:TikTok|ByteDance)\b", re.IGNORECASE)
SKILL_LINE_RE = re.compile(r"^\*+\s+\*\*(.+?)[:：]\*\*\s*(.*)$")
NON_STRUCTURAL_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9+/.-]*")
NUMBER_EXPR_RE = re.compile(
    r"(?<!\*)\b\d+(?:\.\d+)?(?:[%+]|[MK]\+?)?(?:-[A-Za-z]+)?"
    r"(?:\s+(?:seconds?|minutes?|hours?|days?|weeks?|months?|quarters?|years?|"
    r"cities?|city|markets?|people|person|stakeholders?|records?|steps?|nodes?|"
    r"releases?|workflows?|teams?))?(?!\*)",
    re.IGNORECASE,
)

CANONICAL_DIDI_SCOPE_NOTE = (
    "Data lead within a **13-person** cross-functional squad "
    "spanning product, backend, frontend, mobile, and ops."
)

CANONICAL_DIDI_GLOBAL_SCOPE_BULLET = (
    "Represented the headquarters data organization in biweekly global operating reviews, "
    "and translated performance signals into two-week recommendations adopted by management "
    "and LATAM frontline teams."
)

WEAK_GO_SUMMARY_HEADER_RE = re.compile(
    r"(collaboration|collaborative|teamwork|team player|problem solver|delivery fit|engineering collaboration)",
    re.IGNORECASE,
)

STRONG_GO_SUMMARY_HEADER_RE = re.compile(
    r"(pattern|strategic|decision|systems|analytical|judgment|reasoning|rigor)",
    re.IGNORECASE,
)

SHORT_SKILL_TITLES = {
    "programming": ["Programming", "APIs"],
    "data": ["Data", "Analytics"],
    "ai_ml": ["AI/ML", "Modeling"],
    "cloud": ["Cloud", "Systems"],
}

BODY_SKILL_VOCAB = [
    "Python", "Java", "Scala", "Go", "JavaScript", "TypeScript", "SQL", "R",
    "Matlab", "Pandas", "NumPy", "Jupyter", "Tableau", "Looker", "Matplotlib",
    "Experiment Design", "Forecasting", "KPI Measurement", "Dashboard Automation",
    "Machine Learning", "LLM", "NLP", "RAG", "AWS Bedrock", "scikit-learn",
    "A/B Testing", "ETL", "Airflow", "Hive", "Spark SQL", "PostgreSQL", "MySQL",
    "Redis", "Kafka", "Docker", "Kubernetes", "Terraform", "AWS", "GCP", "Azure",
    "S3", "Git", "GitHub Actions", "GitLab CI", "Jenkins", "CI/CD", "Linux",
    "Bash", "Shell", "Ansible", "Prometheus", "Microservices", "REST", "gRPC",
]

MERGE_TARGETS = {
    "programming": ("cloud", "data", "ai_ml"),
    "data": ("ai_ml", "programming", "cloud"),
    "ai_ml": ("data", "cloud", "programming"),
    "cloud": ("programming", "data", "ai_ml"),
}


@dataclass(frozen=True)
class ResumeIssue:
    code: str
    severity: str
    detail: str
    line_number: int = 0

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "severity": self.severity,
            "detail": self.detail,
            "line_number": self.line_number,
        }


def effective_pass(review_payload: dict) -> bool:
    try:
        score = float(review_payload.get("final_score", review_payload.get("weighted_score", 0.0)) or 0.0)
    except (TypeError, ValueError):
        score = 0.0
    return (
        bool(review_payload.get("passed", False))
        and score >= 93.0
        and int(review_payload.get("critical_count", 0) or 0) == 0
        and int(review_payload.get("high_count", 0) or 0) == 0
    )


WEAK_SKILL_CATEGORY_TITLES = {
    "api",
    "apis",
    "other",
    "others",
    "misc",
    "miscellaneous",
    "tools",
    "technology",
    "technologies",
}

GENERIC_BODY_EVIDENCE_EXEMPT_TECH = {
    "python", "java", "javascript", "typescript", "c#", "c++", "go", "golang", "rust",
    "ruby", "swift", "kotlin", "scala", "php", "r", "matlab", "sql", "bash", "shell",
    "aws", "gcp", "azure", "docker", "kubernetes", "k8s", "terraform", "git", "linux",
    "mysql", "postgres", "postgresql", "redis", "mongodb", "snowflake", "databricks",
    "react", "node.js", "html", "css",
}

SUMMARY_STRONG_SIGNALS = (
    "lead", "led", "leading", "architect", "architected", "ownership", "owner",
    "platform", "distributed", "scalable", "scale", "reliability", "performance",
    "stakeholder", "cross-functional", "operating review", "systems", "backend",
    "infrastructure", "infra", "technical strategy", "code review", "design review",
)

SUMMARY_WEAK_SIGNALS = (
    "collaboration", "collaborative", "teamwork", "problem-solving", "problem solving",
    "transitioning from data analytics", "transitioning from analytics",
    "data analytics", "data analyst", "analyst background", "team player",
)


def audit_resume_markdown(
    text: str,
    *,
    target_company: str = "",
    target_seniority: str = "",
    target_title: str = "",
    target_role_type: str = "",
    tech_required: list[str] | None = None,
) -> list[ResumeIssue]:
    lines = text.splitlines()
    issues: list[ResumeIssue] = []
    bytedance_mode = is_bytedance_target_company(target_company)

    headers = [line.strip() for line in lines if line.startswith("## ")]
    canonical_headers = [header for header in headers if header in SECTION_ORDER]
    if canonical_headers and canonical_headers != SECTION_ORDER[: len(canonical_headers)]:
        issues.append(
            ResumeIssue(
                code="section_order",
                severity="high",
                detail=f"Unexpected section order: {' > '.join(canonical_headers)}",
            )
        )

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if CJK_RE.search(line):
            issues.append(
                ResumeIssue(
                    code="cjk_characters",
                    severity="critical",
                    detail="English resume contains Chinese characters.",
                    line_number=idx,
                )
            )
        if TIKTOK_TITLE_RE.search(stripped):
            issues.append(
                ResumeIssue(
                    code="tiktok_title_variant",
                    severity="critical",
                    detail="TikTok title must be `Software Engineer Intern`.",
                    line_number=idx,
                )
            )
        if bytedance_mode and BYTEDANCE_TARGET_RE.search(stripped):
            issues.append(
                ResumeIssue(
                    code="bytedance_intern_present",
                    severity="critical",
                    detail="ByteDance target resumes must not mention TikTok / ByteDance intern experience.",
                    line_number=idx,
                )
            )
        if stripped == "## Additional Information":
            issues.append(
                ResumeIssue(
                    code="achievements_header_alias",
                    severity="medium",
                    detail="Use `## Achievements`, not `## Additional Information`.",
                    line_number=idx,
                )
            )
        if stripped == "## Achievement":
            issues.append(
                ResumeIssue(
                    code="achievements_header_singular",
                    severity="medium",
                    detail="Use `## Achievements`, not `## Achievement`.",
                    line_number=idx,
                )
            )
        if PROJECT_HEADING_RE.match(stripped):
            next_nonempty = ""
            next_line_no = 0
            for j in range(idx, len(lines)):
                candidate = lines[j].strip()
                if candidate:
                    next_nonempty = candidate
                    next_line_no = j + 1
                    break
            if not next_nonempty.startswith("> "):
                code = "project_baseline_missing"
                detail = "Project heading must be followed by a `> ` context line."
                if next_nonempty.startswith("*") and next_nonempty.endswith("*") and not next_nonempty.startswith("* "):
                    code = "project_baseline_legacy_italic"
                    detail = "Project baseline still uses legacy italic formatting."
                issues.append(
                    ResumeIssue(
                        code=code,
                        severity="medium",
                        detail=detail,
                        line_number=next_line_no or idx,
                    )
                )

    if "## Skills" in headers and "## Experience" in headers and headers.index("## Skills") > headers.index("## Experience"):
        issues.append(
            ResumeIssue(
                code="skills_after_experience",
                severity="high",
                detail="Skills must appear before Experience.",
            )
        )

    summary_count = len(_extract_summary_candidates(text))
    if summary_count != 3:
        issues.append(
            ResumeIssue(
                code="summary_count",
                severity="high",
                detail=f"Professional Summary must contain exactly 3 bullets; found {summary_count}.",
                line_number=1,
            )
        )

    if _count_non_structural_bolds(lines) == 0:
        issues.append(
            ResumeIssue(
                code="keyword_bold_missing",
                severity="high",
                detail="Resume body must contain bolded keywords beyond headers and skills category titles.",
            )
        )

    summary_candidates = _extract_summary_candidates(text)
    if len(summary_candidates) >= 3 and _is_weak_go_summary_header(summary_candidates[2]):
        issues.append(
            ResumeIssue(
                code="go_summary_weak_header",
                severity="high",
                detail=(
                    "The Go / weiqi summary line must emphasize strategic judgment or pattern recognition, "
                    "not collaboration/teamwork/problem-solver phrasing."
                ),
                line_number=_summary_line_number(lines, 3),
            )
        )

    for line_number, category_name, skills, word_count, _raw in _iter_skill_lines(lines):
        if len(skills) < MIN_SKILLS_PER_CATEGORY:
            issues.append(
                ResumeIssue(
                    code="skills_category_too_short",
                    severity="high",
                    detail=(
                        f"Skills category `{category_name}` has {len(skills)} items; "
                        f"categories with fewer than {MIN_SKILLS_PER_CATEGORY} items must be merged."
                    ),
                    line_number=line_number,
                )
            )
        if word_count > MAX_SKILLS_LINE_WORDS:
            issues.append(
                ResumeIssue(
                    code="skills_line_word_overflow",
                    severity="high",
                    detail=(
                        f"Skills line `{category_name}` has {word_count} words including the title; "
                        f"the hard limit is {MAX_SKILLS_LINE_WORDS}."
                    ),
                    line_number=line_number,
                )
            )
        if _is_weak_skill_category_title(category_name):
            issues.append(
                ResumeIssue(
                    code="skills_category_weak_label",
                    severity="medium",
                    detail=(
                        f"Skills category `{category_name}` is too vague to signal a clear taxonomy. "
                        "Use a functional group label such as Programming, Data, AI/ML, Cloud/Infra, or Developer Tools."
                    ),
                    line_number=line_number,
                )
            )

    if "## Skills" in headers and not _iter_skill_lines(lines):
        issues.append(
            ResumeIssue(
                code="skills_section_empty",
                severity="high",
                detail="Skills section is present but contains no parseable skill categories.",
            )
        )

    didi_scope = _find_didi_scope_line(lines)
    if didi_scope is not None:
        raw_line, line_number = didi_scope
        stripped = raw_line.strip()
        if not stripped.startswith("> "):
            issues.append(
                ResumeIssue(
                    code="didi_scope_note_legacy_format",
                    severity="high",
                    detail="DiDi cross-functional scope note must use `> ` blockquote formatting.",
                    line_number=line_number,
                )
            )
        if stripped and stripped[-1] not in ".!?":
            issues.append(
                ResumeIssue(
                    code="didi_scope_note_missing_period",
                    severity="medium",
                    detail="DiDi cross-functional scope note must end with a period.",
                    line_number=line_number,
                )
            )
        if "embedded analytics partner" in stripped.lower():
            issues.append(
                ResumeIssue(
                    code="didi_scope_note_jargon",
                    severity="medium",
                    detail="Replace `Embedded analytics partner` with plain-English leadership framing.",
                    line_number=line_number,
                )
            )

    required_tech = [item for item in (tech_required or []) if str(item or "").strip()]
    missing_body_tech = [
        tech for tech in required_tech
        if _requires_body_evidence_gate(tech) and not _tech_has_body_evidence(lines, tech)
    ]
    if missing_body_tech:
        issues.append(
            ResumeIssue(
                code="jd_must_have_body_evidence_missing",
                severity="medium",
                detail=(
                    "JD must-have technology lacks body evidence: "
                    + ", ".join(missing_body_tech[:4])
                    + ". Keep the skill, but add concrete usage evidence in experience/project bullets."
                ),
            )
        )

    if _needs_summary_reframe(lines, target_title, target_role_type, tech_required or []):
        issues.append(
            ResumeIssue(
                code="summary_weak_framing",
                severity="medium",
                detail=(
                    "The opening summary uses a weaker narrative anchor than the resume body supports. "
                    "Page one should explain the career line clearly, stay within body-supported claims, and foreground the strongest role-aligned signal instead of transition-first, collaboration-first, or generic-safe framing."
                ),
                line_number=_summary_line_number(lines, 1),
            )
        )

    achievement_section = _extract_achievement_section(lines)
    if achievement_section is not None:
        bullet_line, line_number = achievement_section
        bullet_text = bullet_line[2:].strip() if bullet_line.startswith(("* ", "- ")) else bullet_line.strip()
        if bullet_text and bullet_text[-1] not in ".!?":
            issues.append(
                ResumeIssue(
                    code="achievement_missing_period",
                    severity="medium",
                    detail="Achievements bullet must end with a period.",
                    line_number=line_number,
                )
            )

    return issues


def normalize_resume_markdown(text: str, *, target_company: str = "") -> tuple[str, list[str]]:
    resume = Resume.from_markdown(text)
    changes: list[str] = []
    bytedance_mode = is_bytedance_target_company(target_company)

    raw_summary_candidates = _extract_summary_candidates(text)
    if raw_summary_candidates:
        normalized_summary = _normalize_summary_candidates(raw_summary_candidates, resume.achievement)
        if normalized_summary != resume.summary:
            resume.summary = normalized_summary
            changes.append("normalized_summary_shape")

    filtered_experiences = []
    for exp in resume.experiences:
        exp_company = (exp.company or "").strip().lower()
        exp_dept = (exp.department or "").strip().lower()
        if bytedance_mode and ("tiktok" in exp_company or "bytedance" in exp_company or exp_dept == "security"):
            changes.append("removed_bytedance_intern_experience")
            continue
        if "tiktok" in exp_company or "bytedance" in exp_company or exp_dept == "security":
            if exp.title != "Software Engineer Intern":
                exp.title = "Software Engineer Intern"
                changes.append("normalized_tiktok_title")
            if exp.company != "TikTok":
                exp.company = "TikTok"
                changes.append("normalized_tiktok_company")
            if exp.department != "Security":
                exp.department = "Security"
                changes.append("normalized_tiktok_department")
            if exp.dates != "Jun 2025 – Dec 2025":
                exp.dates = "Jun 2025 – Dec 2025"
                changes.append("normalized_tiktok_dates")
            if exp.location != "San Jose, USA":
                exp.location = "San Jose, USA"
                changes.append("normalized_tiktok_location")
        filtered_experiences.append(exp)
    resume.experiences = filtered_experiences

    if resume.summary:
        for idx, sentence in enumerate(resume.summary):
            if idx != 2:
                continue
            lowered = sentence.lower()
            if (
                CJK_RE.search(sentence)
                or "go amateur" in lowered
                or "围棋" in sentence
                or "weiqi" in lowered
                or "second-dan" in lowered
                or ("go" in lowered and "2-dan" in lowered)
                or ("china national certified" in lowered and "champion" in lowered)
            ):
                normalized = _normalize_go_summary_sentence(sentence)
                if normalized != sentence:
                    resume.summary[idx] = normalized
                    changes.append("normalized_go_summary")

    if resume.achievement:
        normalized_achievement = _normalize_go_achievement(resume.achievement)
        if normalized_achievement != resume.achievement:
            resume.achievement = normalized_achievement
            changes.append("normalized_go_achievement")

    if _rebuild_skills_from_body_if_missing(resume, text):
        changes.append("recovered_missing_skills")

    if _normalize_skills_layout(resume):
        changes.append("normalized_skills_layout")

    if _normalize_didi_scope_notes(resume):
        changes.append("normalized_didi_scope_note")

    if _normalize_didi_global_scope_bullets(resume):
        changes.append("normalized_didi_global_scope_bullet")

    if _normalize_keyword_bolding(resume):
        changes.append("normalized_keyword_bolding")

    normalized_text = resume.to_markdown()
    return normalized_text, _dedupe(changes)


def _normalize_go_summary_sentence(sentence: str) -> str:
    header_match = re.match(r"^\*\*(.+?):\*\*\s*(.+)$", sentence.strip())
    raw_header = header_match.group(1).strip() if header_match else ""
    header = _normalize_go_summary_header(raw_header)
    return (
        f"**{header}:** Apply the pattern recognition of a **China National Certified Go 2-dan player**, "
        f"**2022 city champion**, and **2023 city third-place finisher** to complex systems analysis and "
        f"high-stakes problem solving."
    )


def _normalize_go_achievement(text: str) -> str:
    if not GO_KEYWORD_RE.search(text) and not CJK_RE.search(text):
        normalized = text.strip().rstrip(".")
        return f"{normalized}." if normalized else normalized
    return "China national certified Go **2-dan** — city **champion** (2022) and third place (2023)."


def _normalize_keyword_bolding(resume: Resume) -> bool:
    skills_vocab = _collect_skill_vocab(resume)
    changed = False

    for idx, sentence in enumerate(resume.summary):
        updated = _auto_bold_text(sentence, skills_vocab)
        if updated != sentence:
            resume.summary[idx] = updated
            changed = True

    for exp in resume.experiences:
        if exp.cross_functional_note:
            updated_note = _auto_bold_text(exp.cross_functional_note, skills_vocab)
            if updated_note != exp.cross_functional_note:
                exp.cross_functional_note = updated_note
                changed = True

        for bullet in exp.bullets:
            updated_bullet = _auto_bold_text(bullet.text, skills_vocab)
            if updated_bullet != bullet.text:
                bullet.text = updated_bullet
                _refresh_bullet_metadata(bullet)
                changed = True

        if exp.project:
            if exp.project.baseline:
                updated_baseline = _auto_bold_text(exp.project.baseline, skills_vocab)
                if updated_baseline != exp.project.baseline:
                    exp.project.baseline = updated_baseline
                    changed = True
            for bullet in exp.project.bullets:
                updated_bullet = _auto_bold_text(bullet.text, skills_vocab)
                if updated_bullet != bullet.text:
                    bullet.text = updated_bullet
                    _refresh_bullet_metadata(bullet)
                    changed = True

    for edu in resume.education:
        if not edu.project:
            continue
        if edu.project.baseline:
            updated_baseline = _auto_bold_text(edu.project.baseline, skills_vocab)
            if updated_baseline != edu.project.baseline:
                edu.project.baseline = updated_baseline
                changed = True
        for bullet in edu.project.bullets:
            updated_bullet = _auto_bold_text(bullet.text, skills_vocab)
            if updated_bullet != bullet.text:
                bullet.text = updated_bullet
                _refresh_bullet_metadata(bullet)
                changed = True

    return changed


def _normalize_didi_scope_notes(resume: Resume) -> bool:
    changed = False
    for exp in resume.experiences:
        if exp.id != "didi_senior_da" or not exp.cross_functional_note:
            continue
        normalized = CANONICAL_DIDI_SCOPE_NOTE
        if exp.cross_functional_note != normalized:
            exp.cross_functional_note = normalized
            changed = True
    return changed


def _normalize_didi_global_scope_bullets(resume: Resume) -> bool:
    changed = False
    for exp in resume.experiences:
        if exp.id != "didi_senior_da":
            continue
        for bullet in exp.bullets:
            lowered = bullet.text.lower()
            if (
                "global operating review" not in lowered
                and "global operating reviews" not in lowered
                and not ("latam" in lowered and "management" in lowered)
            ):
                continue
            if bullet.text != CANONICAL_DIDI_GLOBAL_SCOPE_BULLET:
                bullet.text = CANONICAL_DIDI_GLOBAL_SCOPE_BULLET
                _refresh_bullet_metadata(bullet)
                changed = True
    return changed


def _normalize_skills_layout(resume: Resume) -> bool:
    ordered_skills = _ordered_unique_skills(resume)
    if not ordered_skills:
        return False

    groups = {bucket: [] for bucket in SHORT_SKILL_TITLES}
    for skill in ordered_skills:
        groups[_bucket_for_skill(skill)].append(skill)

    categories = [
        {"bucket": bucket, "title": SHORT_SKILL_TITLES[bucket][0], "skills": skills[:]}
        for bucket, skills in groups.items()
        if skills
    ]
    categories = _merge_small_skill_categories(categories)
    categories = _split_overlong_skill_categories(categories)
    categories = _merge_small_skill_categories(categories)

    new_skills = [SkillCategory(name=item["title"], skills=item["skills"]) for item in categories if item["skills"]]
    before = [(item.name, item.skills) for item in resume.skills]
    after = [(item.name, item.skills) for item in new_skills]
    if before == after:
        return False
    resume.skills = new_skills
    return True


def _auto_bold_text(text: str, skills_vocab: list[str]) -> str:
    if not text:
        return text

    header_prefix = ""
    body = text
    header_match = re.match(r"^(\*\*[^*]+:\*\*\s*)(.+)$", text.strip())
    if header_match:
        header_prefix = header_match.group(1)
        body = header_match.group(2)
    body = body.replace("**", "")

    segments = re.split(r"(\*\*.+?\*\*)", body)
    updated_parts: list[str] = []
    for segment in segments:
        if not segment:
            continue
        if segment.startswith("**") and segment.endswith("**"):
            updated_parts.append(segment)
            continue

        updated = segment
        for skill in skills_vocab:
            pattern = _skill_pattern(skill)
            updated = re.sub(pattern, lambda match: f"**{match.group(0)}**", updated, flags=re.IGNORECASE)
        updated = NUMBER_EXPR_RE.sub(lambda match: f"**{match.group(0)}**", updated)
        updated_parts.append(updated)

    updated = "".join(updated_parts)
    updated = re.sub(r"\*{4,}", "**", updated)

    if header_prefix:
        return f"{header_prefix}{updated}".strip()
    return updated


def _skill_pattern(skill: str) -> str:
    escaped = re.escape(skill.strip()).replace(r"\ ", r"\s+")
    return rf"(?<![\w*]){escaped}(?![\w*])"


def _collect_skill_vocab(resume: Resume) -> list[str]:
    vocab: list[str] = []
    seen: set[str] = set()
    for category in resume.skills:
        for skill in category.skills:
            normalized = _normalize_skill_key(skill)
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            vocab.append(skill.strip())
    vocab.sort(key=lambda item: (-len(item), item.lower()))
    return vocab


def _rebuild_skills_from_body_if_missing(resume: Resume, text: str) -> bool:
    if any(category.skills for category in resume.skills):
        return False

    found: list[tuple[int, str]] = []
    for skill in BODY_SKILL_VOCAB:
        match = re.search(_skill_pattern(skill), text, flags=re.IGNORECASE)
        if match:
            found.append((match.start(), _canonical_skill_name(skill)))

    if not found:
        return False

    found.sort(key=lambda item: item[0])
    ordered: list[str] = []
    seen: set[str] = set()
    for _position, skill in found:
        key = _normalize_skill_key(skill)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(skill)

    resume.skills = [SkillCategory(name="Recovered", skills=ordered)]
    return True


def _ordered_unique_skills(resume: Resume) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for category in resume.skills:
        for skill in category.skills:
            canonical = _canonical_skill_name(skill)
            key = _normalize_skill_key(canonical)
            if not key or key in seen:
                continue
            seen.add(key)
            ordered.append(canonical)
    return ordered


def _merge_small_skill_categories(categories: list[dict]) -> list[dict]:
    merged = [item.copy() | {"skills": item["skills"][:]} for item in categories]
    while len(merged) > 1:
        small_index = next(
            (idx for idx, item in enumerate(merged) if len(item["skills"]) < MIN_SKILLS_PER_CATEGORY),
            None,
        )
        if small_index is None:
            break

        source = merged[small_index]
        target_index = _find_merge_target_index(merged, small_index)
        merged[target_index]["skills"].extend(source["skills"])
        del merged[small_index]
    return merged


def _find_merge_target_index(categories: list[dict], source_index: int) -> int:
    source_bucket = categories[source_index]["bucket"]
    preferred = MERGE_TARGETS.get(source_bucket, ())
    for bucket in preferred:
        for idx, item in enumerate(categories):
            if idx != source_index and item["bucket"] == bucket:
                return idx
    if source_index > 0:
        return source_index - 1
    return 1


def _split_overlong_skill_categories(categories: list[dict]) -> list[dict]:
    expanded: list[dict] = []
    for item in categories:
        if _skills_line_word_count(item["title"], item["skills"]) <= MAX_SKILLS_LINE_WORDS:
            expanded.append(item)
            continue

        chunks = _chunk_skills_for_word_limit(item["skills"])
        if len(chunks) == 1:
            expanded.append(item)
            continue

        titles = SHORT_SKILL_TITLES.get(item["bucket"], [item["title"]])
        for idx, chunk in enumerate(chunks):
            title = titles[idx] if idx < len(titles) else f"{titles[-1]} {idx + 1}"
            expanded.append({"bucket": item["bucket"], "title": title, "skills": chunk})
    return expanded


def _chunk_skills_for_word_limit(skills: list[str]) -> list[list[str]]:
    if not skills:
        return []
    if len(skills) <= MIN_SKILLS_PER_CATEGORY:
        return [skills[:]]

    chunks: list[list[str]] = []
    remaining = skills[:]
    while remaining:
        chunk: list[str] = []
        for skill in remaining:
            candidate = chunk + [skill]
            if chunk and _skills_line_word_count("X", candidate) > MAX_SKILLS_LINE_WORDS and len(chunk) >= MIN_SKILLS_PER_CATEGORY:
                break
            chunk.append(skill)

        if not chunk:
            return [skills[:]]

        consumed = len(chunk)
        leftover = len(remaining) - consumed
        if chunks and 0 < leftover < MIN_SKILLS_PER_CATEGORY:
            chunks[-1].extend(remaining)
            break

        chunks.append(chunk)
        remaining = remaining[consumed:]

    if len(chunks) >= 2 and len(chunks[-1]) < MIN_SKILLS_PER_CATEGORY:
        while len(chunks[-1]) < MIN_SKILLS_PER_CATEGORY and len(chunks[-2]) > MIN_SKILLS_PER_CATEGORY:
            chunks[-1].insert(0, chunks[-2].pop())

    return [chunk for chunk in chunks if chunk]


def _bucket_for_skill(skill: str) -> str:
    key = _normalize_skill_key(skill)
    ai_ml = {
        "machine learning", "llm", "nlp", "rag", "aws bedrock", "bedrock",
        "scikit-learn", "openai", "generative ai", "ml", "model deployment",
    }
    data = {
        "sql", "pandas", "hive", "spark sql", "tableau", "looker",
        "etl", "airflow", "a/b testing", "experiment design", "forecasting",
        "kpi measurement", "matplotlib", "jupyter", "r", "matlab",
    }
    cloud = {
        "aws", "gcp", "azure", "docker", "kubernetes", "terraform",
        "ci/cd", "github actions", "s3", "postgresql", "mysql", "redis",
        "kafka", "microservices",
    }
    if key in ai_ml:
        return "ai_ml"
    if key in data:
        return "data"
    if key in cloud:
        return "cloud"
    return "programming"


def _skills_line_word_count(title: str, skills: list[str]) -> int:
    line = f"{title} " + " ".join(skills)
    return len(WORD_RE.findall(line))


def _canonical_skill_name(skill: str) -> str:
    collapsed = " ".join(re.sub(r"[*`]+", "", skill or "").split())
    normalized = collapsed.lower()
    aliases = {
        "bedrock": "AWS Bedrock",
        "aws bedrock": "AWS Bedrock",
        "ci/cd": "CI/CD",
        "github actions": "GitHub Actions",
        "grpc": "gRPC",
        "llm": "LLM",
        "nlp": "NLP",
        "rag": "RAG",
        "sql": "SQL",
        "spark sql": "Spark SQL",
    }
    return aliases.get(normalized, collapsed)


def _normalize_skill_key(skill: str) -> str:
    return " ".join(re.sub(r"[*`]+", "", skill or "").lower().split())


def _refresh_bullet_metadata(bullet) -> None:
    refreshed = Resume._parse_bullet(bullet.text)
    bullet.has_data = refreshed.has_data
    bullet.tech_stack_used = refreshed.tech_stack_used
    bullet.verb = refreshed.verb


def _count_non_structural_bolds(lines: list[str]) -> int:
    count = 0
    in_skills = False
    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped == "## Skills":
            in_skills = True
            continue
        if in_skills and stripped.startswith("## "):
            in_skills = False
        if stripped.startswith(("## ", "### ", "**Project:")):
            continue

        candidate = stripped
        if in_skills:
            candidate = SKILL_LINE_RE.sub(r"\2", candidate)
        else:
            candidate = re.sub(r"^(\*|-) \*\*[^*]+:\*\*\s*", "", candidate)
        count += len(NON_STRUCTURAL_BOLD_RE.findall(candidate))
    return count


def _iter_skill_lines(lines: list[str]) -> list[tuple[int, str, list[str], int, str]]:
    in_skills = False
    collected: list[tuple[int, str, list[str], int, str]] = []
    for line_number, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if stripped == "## Skills":
            in_skills = True
            continue
        if in_skills and stripped.startswith("## "):
            break
        if not in_skills:
            continue
        match = SKILL_LINE_RE.match(stripped)
        if not match:
            continue
        category_name = match.group(1).strip()
        skills = [item.strip() for item in match.group(2).split(",") if item.strip()]
        word_count = len(WORD_RE.findall(stripped.replace("**", "")))
        collected.append((line_number, category_name, skills, word_count, raw_line))
    return collected


def _is_weak_skill_category_title(category_name: str) -> bool:
    normalized = _normalize_skill_key(category_name)
    return normalized in WEAK_SKILL_CATEGORY_TITLES


def _requires_body_evidence_gate(tech: str) -> bool:
    normalized = _normalize_skill_key(tech)
    if not normalized or normalized in GENERIC_BODY_EVIDENCE_EXEMPT_TECH:
        return False
    return (" " in normalized) or ("/" in normalized) or ("-" in normalized)


def _needs_summary_reframe(
    lines: list[str],
    target_title: str,
    target_role_type: str,
    tech_required: list[str],
) -> bool:
    summary_candidates = _extract_summary_candidates("\n".join(lines))
    if not summary_candidates:
        return False
    opening_text = " ".join(summary_candidates[:2]).lower()
    if not opening_text:
        return False

    target_signature = " ".join(
        [
            str(target_title or "").lower(),
            str(target_role_type or "").lower(),
            " ".join(_normalize_skill_key(item) for item in tech_required[:8]),
        ]
    )
    looks_engineering_target = any(
        token in target_signature
        for token in (
            "software engineer", "swe", "backend", "infrastructure", "platform",
            "performance", "distributed", "systems", "cloud", "ml", "genai",
        )
    )

    if "data modeling focus" in opening_text:
        return True
    if any(token in opening_text for token in SUMMARY_WEAK_SIGNALS) and not any(
        token in opening_text for token in SUMMARY_STRONG_SIGNALS
    ):
        return True
    if looks_engineering_target and "data analytics" in opening_text and not any(
        token in opening_text for token in ("backend", "infrastructure", "platform", "distributed", "performance", "software engineer")
    ):
        return True
    if looks_engineering_target and not any(token in opening_text for token in SUMMARY_STRONG_SIGNALS) and any(
        token in target_signature for token in ("backend", "infrastructure", "platform", "distributed", "performance")
    ):
        return True
    return False


def _tech_has_body_evidence(lines: list[str], tech: str) -> bool:
    normalized = _normalize_skill_key(tech)
    if not normalized:
        return True

    in_summary = False
    in_skills = False
    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped == "## Professional Summary":
            in_summary = True
            in_skills = False
            continue
        if stripped == "## Skills":
            in_summary = False
            in_skills = True
            continue
        if stripped.startswith("## "):
            in_summary = False
            in_skills = False
            continue
        if in_summary or in_skills or not stripped:
            continue
        if _text_matches_tech(stripped, normalized):
            return True
    return False


def _text_matches_tech(text: str, normalized_tech: str) -> bool:
    for candidate in _tech_aliases(normalized_tech):
        pattern = _skill_pattern(candidate)
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True
    return False


def _tech_aliases(normalized_tech: str) -> list[str]:
    aliases = {
        "apache spark": ["Apache Spark", "Spark"],
        "spark": ["Spark", "Apache Spark"],
        "apache airflow": ["Apache Airflow", "Airflow"],
        "airflow": ["Airflow", "Apache Airflow"],
        "apache kafka": ["Apache Kafka", "Kafka"],
        "kafka": ["Kafka", "Apache Kafka"],
        "data pipelines": ["data pipelines", "data pipeline"],
        "data pipeline": ["data pipeline", "data pipelines"],
        "restful": ["RESTful", "REST"],
        "rest": ["REST", "RESTful"],
        "ci/cd": ["CI/CD", "continuous integration", "continuous delivery"],
        "k8s": ["K8s", "Kubernetes"],
        "postgres": ["Postgres", "PostgreSQL"],
        "llm": ["LLM", "large language model", "large language models"],
        "gen ai": ["Gen AI", "Generative AI"],
    }
    return aliases.get(normalized_tech, [normalized_tech])


def _find_didi_scope_line(lines: list[str]) -> tuple[str, int] | None:
    in_didi = False
    saw_dates = False
    for line_number, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if stripped.startswith("### "):
            in_didi = "Senior Data Analyst | DiDi · IBG · Food" in stripped
            saw_dates = False
            continue
        if not in_didi:
            continue
        if stripped.startswith("### ") or stripped.startswith("## "):
            return None
        if not stripped:
            continue
        if not saw_dates and stripped.startswith("*") and stripped.endswith("*") and "|" in stripped:
            saw_dates = True
            continue
        if saw_dates and (stripped.startswith("> ") or (stripped.startswith("*") and stripped.endswith("*"))):
            return raw_line, line_number
        if saw_dates and stripped.startswith("* "):
            return None
    return None


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def _extract_achievement_section(lines: list[str]) -> tuple[str, int] | None:
    in_achievements = False
    for idx, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if stripped in {"## Achievements", "## Achievement", "## Additional Information"}:
            in_achievements = True
            continue
        if in_achievements and stripped.startswith("## "):
            return None
        if in_achievements and stripped.startswith(("* ", "- ")):
            return stripped, idx
    return None


def _extract_summary_candidates(text: str) -> list[str]:
    lines = text.splitlines()
    in_summary = False
    buffer: list[str] = []
    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped == "## Professional Summary":
            in_summary = True
            continue
        if in_summary and stripped.startswith("## "):
            break
        if in_summary and stripped:
            if stripped.startswith("* ") or stripped.startswith("- "):
                buffer.append(stripped[2:].strip())
            else:
                buffer.extend(Resume._split_summary_fragments(stripped))
    return [item for item in buffer if item]


def _normalize_summary_candidates(candidates: list[str], achievement_text: str) -> list[str]:
    items = [item.strip() for item in candidates if item.strip()]
    if len(items) == 2 and achievement_text.strip():
        items.append(_normalize_go_summary_sentence(""))
        return items
    if len(items) <= 3:
        return items

    go_items = [item for item in items if GO_KEYWORD_RE.search(item) or CJK_RE.search(item)]
    non_go_items = [item for item in items if item not in go_items]
    has_achievement = bool(achievement_text.strip())
    if has_achievement and go_items and len(non_go_items) >= 2:
        return [non_go_items[0], non_go_items[1], go_items[0]]

    if len(items) > 3:
        items = items[:3]
    return items


def _normalize_go_summary_header(header: str) -> str:
    cleaned = (header or "").strip()
    if cleaned and STRONG_GO_SUMMARY_HEADER_RE.search(cleaned) and not WEAK_GO_SUMMARY_HEADER_RE.search(cleaned):
        return cleaned
    return "Strategic Pattern Recognition"


def _is_weak_go_summary_header(sentence: str) -> bool:
    lowered = sentence.lower()
    if (
        "2-dan" not in lowered
        and "weiqi" not in lowered
        and "city champion" not in lowered
        and "china national certified" not in lowered
        and "围棋" not in sentence
    ):
        return False
    header_match = re.match(r"^\*\*(.+?):\*\*\s*(.+)$", sentence.strip())
    header = header_match.group(1).strip() if header_match else ""
    if not header:
        return True
    return bool(WEAK_GO_SUMMARY_HEADER_RE.search(header) or not STRONG_GO_SUMMARY_HEADER_RE.search(header))


def _summary_line_number(lines: list[str], ordinal: int) -> int:
    in_summary = False
    count = 0
    for idx, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if stripped == "## Professional Summary":
            in_summary = True
            continue
        if in_summary and stripped.startswith("## "):
            break
        if in_summary and stripped.startswith(("* ", "- ")):
            count += 1
            if count == ordinal:
                return idx
    return 1
