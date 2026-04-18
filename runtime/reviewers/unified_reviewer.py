"""
Unified Reviewer — 单次 LLM 调用完成全部 9 维度审查。

替代原 R0-R6 + Secretary + ChiefReviewer + CircuitBreaker 的复杂链路。
使用轻量审查模型输出结构化 JSON。

核心方法:
  review(resume_md, jd) → ReviewSummary（含评分、findings、修改指令）
"""
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from automation.resume_repair import ResumeIssue, audit_resume_markdown
from models.jd import JDProfile
from models.resume import Resume
from core.anthropic_client import get_llm_client, LLMUnavailableError
from core.prompt_builder import UNIFIED_REVIEWER_SYSTEM, build_unified_review_prompt

logger = logging.getLogger(__name__)


@dataclass
class DimensionScore:
    """单个维度的评分结果"""
    reviewer_id: str
    score: float          # 0-10
    weight: float
    verdict: str          # pass / fail
    findings: List[Dict] = field(default_factory=list)

    @property
    def weighted_contribution(self) -> float:
        return self.score * self.weight * 10


@dataclass
class ReviewSummary:
    """统一审查汇总结果"""
    dimensions: Dict[str, DimensionScore] = field(default_factory=dict)
    weighted_score: float = 0.0      # 0-100
    overall_verdict: str = "fail"    # pass / fail
    critical_count: int = 0
    high_count: int = 0
    needs_revision: bool = True
    revision_priority: List[str] = field(default_factory=list)
    revision_instructions: str = ""
    raw_response: str = ""           # 原始 LLM 响应，供调试
    calibrated: bool = False
    calibration_scores: List[float] = field(default_factory=list)
    target_company: str = ""

    @property
    def passed(self) -> bool:
        return self.overall_verdict == "pass" and self.weighted_score >= 93.0

    def to_dict(self) -> Dict:
        data = {
            "weighted_score": round(self.weighted_score, 1),
            "overall_verdict": self.overall_verdict,
            "passed": self.passed,
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "needs_revision": self.needs_revision,
            "revision_priority": self.revision_priority,
            "scores": {
                k: {
                    "score": v.score,
                    "weight": v.weight,
                    "verdict": v.verdict,
                    "findings_count": len(v.findings),
                }
                for k, v in self.dimensions.items()
            },
        }
        if self.calibrated:
            data["calibrated"] = True
            data["calibration_scores"] = self.calibration_scores
        return data

    def format_report(self) -> str:
        """生成可读的审查报告摘要"""
        lines = [
            f"综合评分: {self.weighted_score:.1f}/100 [{self.overall_verdict.upper()}]",
            f"Critical: {self.critical_count}  High: {self.high_count}",
        ]
        if self.calibrated and self.calibration_scores:
            scores = " / ".join(f"{score:.1f}" for score in self.calibration_scores)
            lines.append(f"复核校准: {scores} → {self.weighted_score:.1f}")
        lines.extend([
            "",
            "各维度评分:",
        ])
        for dim_id, dim in self.dimensions.items():
            marker = "✓" if dim.verdict == "pass" else "✗"
            lines.append(
                f"  {marker} {dim_id}: {dim.score:.1f}/10 "
                f"(×{dim.weight:.2f} → {dim.weighted_contribution:.1f}分)"
            )
        if self.revision_priority:
            lines.append("")
            lines.append("优先修改事项:")
            for i, p in enumerate(self.revision_priority, 1):
                lines.append(f"  {i}. {p}")
        return "\n".join(lines)


class UnifiedReviewer:
    """单次调用完成全部 9 维度审查。"""

    # 默认维度权重（与 frozen_constraints 对应）
    DIMENSION_WEIGHTS = {
        "r0_authenticity": 0.20,
        "r1_writing_standard": 0.15,
        "r2_jd_fitness": 0.20,
        "r3_overqualification": 0.10,
        "r4_rationality": 0.20,
        "r5_logic": 0.10,
        "r6_competitiveness": 0.05,
    }
    BORDERLINE_CALIBRATION_FLOOR = 91.5
    CALIBRATION_DIFF_THRESHOLD = 1.0

    def review(
        self,
        resume_md: str,
        jd: JDProfile,
        *,
        mode: str = "full",
        prompt_override: str | None = None,
        system_prompt_override: str | None = None,
    ) -> ReviewSummary:
        """
        对简历进行完整审查。

        Args:
            resume_md: 简历 Markdown 文本
            jd: JD profile

        Returns:
            ReviewSummary 包含评分、findings 和修改指令
        """
        logger.info("Unified Reviewer 开始审查: %s @ %s", jd.title, jd.company)
        summary = self._single_review(
            resume_md,
            jd,
            "primary",
            mode=mode,
            prompt_override=prompt_override,
            system_prompt_override=system_prompt_override,
        )
        if mode == "full" and self._should_calibrate(summary):
            logger.info(
                "边界分数触发复核校准: %.1f（critical=%d high=%d）",
                summary.weighted_score,
                summary.critical_count,
                summary.high_count,
            )
            calibration_runs = [
                summary,
                self._single_review(
                    resume_md,
                    jd,
                    "calibration_1",
                    mode=mode,
                    prompt_override=prompt_override,
                    system_prompt_override=system_prompt_override,
                ),
            ]
            spread = abs(
                calibration_runs[0].weighted_score - calibration_runs[1].weighted_score
            )
            if spread >= self.CALIBRATION_DIFF_THRESHOLD:
                calibration_runs.append(
                    self._single_review(
                        resume_md,
                        jd,
                        "calibration_2",
                        mode=mode,
                        prompt_override=prompt_override,
                        system_prompt_override=system_prompt_override,
                    )
                )
            summary = _combine_review_summaries(calibration_runs)
        summary = _apply_deterministic_audit(summary, resume_md, jd)
        logger.info("审查结果: %s", summary.format_report())
        return summary

    def _single_review(
        self,
        resume_md: str,
        jd: JDProfile,
        cache_suffix: str,
        *,
        mode: str = "full",
        prompt_override: str | None = None,
        system_prompt_override: str | None = None,
    ) -> ReviewSummary:
        client = get_llm_client()
        prompt_resume = _build_compact_review_excerpt(resume_md, jd) if mode == "compact" else resume_md
        prompt = prompt_override or build_unified_review_prompt(prompt_resume, jd, review_scope=mode)
        cache_key = client.make_cache_key(
            jd.jd_id or "unknown",
            jd.company or "",
            jd.role_type or "",
            str(hash(prompt_resume[:200])),
            f"unified_review_v4_{mode}_{cache_suffix}",
        )

        raw = client.call_review(
            prompt,
            system=system_prompt_override or UNIFIED_REVIEWER_SYSTEM,
            cache_key=cache_key,
        )
        summary = _parse_review_response(raw)
        summary.raw_response = raw
        summary.target_company = jd.company or ""
        return summary

    def _should_calibrate(self, summary: ReviewSummary) -> bool:
        return (
            summary.critical_count == 0
            and summary.high_count == 0
            and not summary.passed
            and self.BORDERLINE_CALIBRATION_FLOOR <= summary.weighted_score < 93.0
        )


def _build_compact_review_excerpt(resume_md: str, jd: JDProfile) -> str:
    try:
        resume = Resume.from_markdown(resume_md)
    except Exception:
        return resume_md

    lines: list[str] = []
    lines.append("## Professional Summary")
    for sentence in resume.summary:
        lines.append(f"* {sentence}")
    lines.append("")

    lines.append("## Skills")
    for category in resume.skills:
        lines.append(f"* **{category.name}:** {', '.join(category.skills)}")
    lines.append("")

    lines.append("## Experience")
    for exp in resume.experiences:
        team_str = f" · {exp.team}" if exp.team else ""
        lines.append(f"### {exp.title} | {exp.company} · {exp.department}{team_str}")
        lines.append(f"*{exp.dates} | {exp.location}*")
        if exp.cross_functional_note:
            lines.append(f"> {resume._ensure_period(exp.cross_functional_note)}")
        lines.append("")

        for bullet in _select_key_bullets(exp.bullets, jd, exp_id=exp.id):
            lines.append(f"* {resume._ensure_period(bullet.text)}")
        lines.append("")

        if exp.project:
            project_bullets = _select_key_bullets(exp.project.bullets, jd, exp_id=exp.id, limit=2)
            if project_bullets:
                lines.append(f"**Project: {exp.project.title}**")
                if exp.project.baseline:
                    lines.append(f"> {exp.project.baseline}")
                for bullet in project_bullets:
                    lines.append(f"* {resume._ensure_period(bullet.text)}")
                lines.append("")

    if resume.education:
        lines.append("## Education")
        for edu in resume.education:
            track = f" ({edu.track})" if edu.track else ""
            lines.append(f"### {edu.degree}{track} | {edu.school}")
            lines.append(f"*{edu.dates}*")
        lines.append("")

    if resume.achievement:
        lines.append("## Achievements")
        lines.append(f"* {resume._ensure_period(resume.achievement.strip())}")

    return "\n".join(lines).strip()


def _select_key_bullets(bullets, jd: JDProfile, *, exp_id: str, limit: int | None = None):
    if not bullets:
        return []
    max_items = limit or (3 if exp_id == "didi_senior_da" else 2)
    required = [_normalize_review_token(item) for item in (jd.tech_required or []) if item]
    preferred = [_normalize_review_token(item) for item in (jd.tech_preferred or [])[:6] if item]

    scored = []
    for index, bullet in enumerate(bullets):
        lowered = _normalize_review_token(bullet.text)
        score = 0
        for item in required:
            if item and item in lowered:
                score += 100
        for item in preferred:
            if item and item in lowered:
                score += 20
        if bullet.has_data:
            score += 8
        if exp_id == "didi_senior_da" and re.search(r"(headquarters|global operating|latam|cross-functional|13-person)", lowered):
            score += 40
        if exp_id == "tiktok_intern":
            score += 4
        scored.append((score, -index, bullet))

    scored.sort(reverse=True, key=lambda item: (item[0], item[1]))
    selected = [item[2] for item in scored[:max_items] if item[0] > 0]
    if not selected:
        selected = bullets[:max_items]
    return selected


def _normalize_review_token(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower())


# ── 解析辅助函数 ──

def _parse_review_response(raw: str) -> ReviewSummary:
    """从 LLM JSON 响应解析出 ReviewSummary"""
    from core.anthropic_client import _parse_json_response

    try:
        data = _parse_json_response(raw)
    except Exception as e:
        logger.error("审查 JSON 解析失败: %s\n原始响应前500字: %s", e, raw[:500])
        repaired = _attempt_review_json_repair(raw)
        if repaired is not None:
            data = repaired
        else:
            # 返回默认失败结果
            return _default_fail_summary(f"JSON解析失败: {e}")

    summary = ReviewSummary()

    # 解析各维度
    scores_data = data.get("scores", {})
    for dim_id, dim_data in scores_data.items():
        score = float(dim_data.get("score", 0))
        weight = float(dim_data.get("weight", UnifiedReviewer.DIMENSION_WEIGHTS.get(dim_id, 0.10)))
        verdict = dim_data.get("verdict", "fail")
        findings = dim_data.get("findings", [])

        summary.dimensions[dim_id] = DimensionScore(
            reviewer_id=dim_id,
            score=score,
            weight=weight,
            verdict=verdict,
            findings=findings,
        )

    # 综合评分（使用 LLM 计算的值，若无则自行计算）
    if "weighted_score" in data:
        summary.weighted_score = float(data["weighted_score"])
    else:
        summary.weighted_score = sum(
            d.weighted_contribution for d in summary.dimensions.values()
        )

    summary.overall_verdict = data.get("overall_verdict", "fail")
    summary.critical_count = int(data.get("critical_count", 0))
    summary.high_count = int(data.get("high_count", 0))
    summary.needs_revision = bool(data.get("needs_revision", True))
    summary.revision_priority = data.get("revision_priority", [])
    summary.revision_instructions = data.get("revision_instructions", "")

    # 确保 weighted_score 与 overall_verdict 一致
    if summary.weighted_score < 93.0 and summary.overall_verdict == "pass":
        summary.overall_verdict = "fail"
        summary.needs_revision = True
    if summary.critical_count > 0:
        summary.overall_verdict = "fail"
        summary.needs_revision = True

    return summary


def _attempt_review_json_repair(raw: str) -> Optional[Dict[str, Any]]:
    """
    当 reviewer 返回的 JSON 轻微损坏时，用一次轻量 repair 调用恢复结构，
    避免把本来有效的审查结果记成 0 分。
    """
    try:
        client = get_llm_client()
        repaired = client.call_review(
            (
                "将下面这段 reviewer 输出修复为合法 JSON。"
                "不要改动语义，不要省略字段，不要解释，只输出 JSON 对象。\n\n"
                f"{raw}"
            ),
            system=(
                "你是 JSON 修复器。输入是一段可能有少量格式错误的 JSON。"
                "输出必须是严格合法的 JSON 对象，不要附加解释，不要使用 Markdown code fence。"
            ),
        )
        from core.anthropic_client import _parse_json_response

        data = _parse_json_response(repaired)
        if isinstance(data, dict):
            logger.info("审查 JSON 修复成功，继续使用修复后的结构化结果")
            return data
    except Exception as exc:
        logger.error("审查 JSON repair 失败: %s", exc)
    return None


def _combine_review_summaries(summaries: List[ReviewSummary]) -> ReviewSummary:
    """合并近阈值复核结果，降低单次评分抖动。"""
    if len(summaries) == 1:
        return summaries[0]

    strictest = min(summaries, key=lambda item: item.weighted_score)
    merged = ReviewSummary()
    merged.calibrated = True
    merged.calibration_scores = [round(item.weighted_score, 1) for item in summaries]

    for dim_id, weight in UnifiedReviewer.DIMENSION_WEIGHTS.items():
        dim_samples = [
            item.dimensions[dim_id]
            for item in summaries
            if dim_id in item.dimensions
        ]
        if not dim_samples:
            continue
        avg_score = round(
            sum(dim.score for dim in dim_samples) / len(dim_samples),
            1,
        )
        merged.dimensions[dim_id] = DimensionScore(
            reviewer_id=dim_id,
            score=avg_score,
            weight=weight,
            verdict="pass" if all(dim.verdict == "pass" for dim in dim_samples) else "fail",
            findings=_merge_findings(dim_samples),
        )

    merged.weighted_score = round(
        sum(dim.weighted_contribution for dim in merged.dimensions.values()),
        1,
    )
    merged.critical_count = max(item.critical_count for item in summaries)
    merged.high_count = max(item.high_count for item in summaries)
    merged.raw_response = strictest.raw_response

    no_severe = merged.critical_count == 0 and merged.high_count == 0
    if no_severe and merged.weighted_score >= 93.0:
        merged.overall_verdict = "pass"
        merged.needs_revision = False
        merged.revision_priority = []
        merged.revision_instructions = ""
    else:
        merged.overall_verdict = "fail"
        merged.needs_revision = True
        merged.revision_priority = _merge_revision_priority(summaries)
        merged.revision_instructions = strictest.revision_instructions

    return merged


def _merge_findings(dimensions: List[DimensionScore], limit: int = 2) -> List[Dict]:
    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    merged: List[Dict] = []
    seen = set()

    for dim in sorted(
        dimensions,
        key=lambda item: sum(
            severity_rank.get(finding.get("severity", "low"), 9)
            for finding in item.findings
        ),
    ):
        for finding in dim.findings:
            key = (finding.get("field", ""), finding.get("issue", ""))
            if key in seen:
                continue
            seen.add(key)
            merged.append(finding)
            if len(merged) >= limit:
                return merged
    return merged


def _merge_revision_priority(summaries: List[ReviewSummary], limit: int = 3) -> List[str]:
    merged: List[str] = []
    seen = set()
    for summary in summaries:
        for item in summary.revision_priority:
            key = item.strip()
            if not key or key in seen:
                continue
            seen.add(key)
            merged.append(key)
            if len(merged) >= limit:
                return merged
    return merged


def _default_fail_summary(reason: str) -> ReviewSummary:
    """在解析失败时返回默认的失败结果"""
    summary = ReviewSummary()
    summary.weighted_score = 0.0
    summary.overall_verdict = "fail"
    summary.needs_revision = True
    summary.revision_priority = [reason]
    summary.revision_instructions = f"审查解析失败（{reason}），请重新生成简历。"
    return summary


def _apply_deterministic_audit(summary: ReviewSummary, resume_md: str, jd: JDProfile | None = None) -> ReviewSummary:
    target_company = ""
    if getattr(summary, "target_company", ""):
        target_company = str(getattr(summary, "target_company", "") or "")
    target_seniority = str(getattr(jd, "seniority", "") or "") if jd is not None else ""
    target_title = str(getattr(jd, "title", "") or "") if jd is not None else ""
    target_role_type = str(getattr(jd, "role_type", "") or "") if jd is not None else ""
    tech_required = list(getattr(jd, "tech_required", []) or []) if jd is not None else []
    issues = audit_resume_markdown(
        resume_md,
        target_company=target_company,
        target_seniority=target_seniority,
        target_title=target_title,
        target_role_type=target_role_type,
        tech_required=tech_required,
    )
    if not issues:
        return summary

    severity_caps = {
        "critical": 6.0,
        "high": 7.6,
        "medium": 8.8,
        "low": 9.2,
    }
    seen_findings = set()
    added_critical = 0
    added_high = 0

    for issue in issues:
        dim_id = _dimension_for_issue(issue)
        if dim_id not in summary.dimensions:
            summary.dimensions[dim_id] = DimensionScore(
                reviewer_id=dim_id,
                score=10.0,
                weight=UnifiedReviewer.DIMENSION_WEIGHTS.get(dim_id, 0.10),
                verdict="pass",
                findings=[],
            )

        dimension = summary.dimensions[dim_id]
        key = (dim_id, issue.code, issue.line_number)
        if key not in seen_findings:
            dimension.findings.append(
                {
                    "severity": issue.severity,
                    "field": f"{issue.code}@line {issue.line_number}" if issue.line_number else issue.code,
                    "issue": issue.detail,
                    "fix": _fix_hint_for_issue(issue),
                }
            )
            seen_findings.add(key)

        cap = severity_caps.get(issue.severity, 9.0)
        dimension.score = min(dimension.score, cap)
        if issue.severity in {"critical", "high"}:
            dimension.verdict = "fail"
            if issue.severity == "critical":
                added_critical += 1
            else:
                added_high += 1

    summary.critical_count += added_critical
    summary.high_count += added_high
    summary.weighted_score = round(
        sum(dim.weighted_contribution for dim in summary.dimensions.values()),
        1,
    )

    if summary.critical_count > 0 or summary.high_count > 0 or summary.weighted_score < 93.0:
        summary.overall_verdict = "fail"
        summary.needs_revision = True
        summary.revision_priority = _merge_issue_priorities(summary.revision_priority, issues)
        if not summary.revision_instructions:
            summary.revision_instructions = _build_issue_revision_instructions(issues)
    else:
        summary.overall_verdict = "pass"
        summary.needs_revision = False

    return summary


def _dimension_for_issue(issue: ResumeIssue) -> str:
    if issue.code in {"cjk_characters", "tiktok_title_variant", "bytedance_intern_present"}:
        return "r0_authenticity"
    if issue.code in {"jd_must_have_body_evidence_missing"}:
        return "r2_jd_fitness"
    if issue.code in {"summary_weak_framing", "didi_scope_note_jargon"}:
        return "r4_rationality"
    if issue.code in {"section_order", "skills_after_experience"}:
        return "r5_logic"
    if issue.code in {"skills_category_weak_label"}:
        return "r5_logic"
    if issue.code.startswith("didi_scope_note"):
        return "r4_rationality"
    return "r1_writing_standard"


def _fix_hint_for_issue(issue: ResumeIssue) -> str:
    hints = {
        "keyword_bold_missing": "Bold real keywords in summary, experience, or project content rather than leaving only section/category headers bold.",
        "go_summary_weak_header": "Rewrite the Go summary line so the header signals strategic judgment or pattern recognition, not collaboration or generic problem-solving.",
        "skills_category_too_short": "Merge this category into a neighboring skills line so every category has at least four items.",
        "skills_line_word_overflow": "Split or rename this skills line until the total word count including the title is 14 or fewer.",
        "skills_category_weak_label": "Rename this skills category to a functional label that signals a clear taxonomy rather than a vague bucket like `APIs` or `Misc`.",
        "jd_must_have_body_evidence_missing": "Keep the JD must-have skill, but add concrete usage evidence in the most relevant experience or project bullet.",
        "summary_weak_framing": "Rewrite the opening summary so it explains the career line clearly and foregrounds the strongest role-aligned signal instead of transition-first, collaboration-first, or generic-safe phrasing.",
        "didi_scope_note_legacy_format": "Render the DiDi scope note as a `> ` blockquote line directly under the date line.",
        "didi_scope_note_jargon": "Replace `Embedded analytics partner` with plain-English leadership framing.",
        "bytedance_intern_present": "Delete all TikTok / ByteDance intern references and rewrite only from DiDi, Temu, and Georgia Tech CS coursework/projects.",
    }
    return hints.get(issue.code, issue.detail)


def _merge_issue_priorities(existing: List[str], issues: List[ResumeIssue], limit: int = 3) -> List[str]:
    merged = list(existing)
    seen = {item.strip() for item in merged if item.strip()}
    ordered = sorted(
        issues,
        key=lambda item: ({"critical": 0, "high": 1, "medium": 2, "low": 3}.get(item.severity, 9), item.code),
    )
    for issue in ordered:
        priority = _priority_text_for_issue(issue)
        if priority in seen:
            continue
        merged.append(priority)
        seen.add(priority)
        if len(merged) >= limit:
            break
    return merged[:limit]


def _priority_text_for_issue(issue: ResumeIssue) -> str:
    priorities = {
        "go_summary_weak_header": "Rewrite the Go summary header into a strategic cognitive signal instead of collaboration/teamwork wording.",
        "keyword_bold_missing": "Add keyword bolding to the resume body; headers alone are not enough.",
        "skills_category_too_short": "Merge under-filled skills categories so no line has fewer than four items.",
        "skills_line_word_overflow": "Shorten or split overlong skills lines to 14 words or fewer.",
        "skills_category_weak_label": "Rename vague skills buckets into functional categories that a recruiter can parse quickly.",
        "jd_must_have_body_evidence_missing": "Add body evidence for each JD must-have technology instead of leaving it only in Skills or Summary.",
        "summary_weak_framing": "Reframe the opening summary so first-scan positioning is clear, body-supported, and anchored on the strongest role-aligned signal.",
        "didi_scope_note_legacy_format": "Normalize the DiDi cross-functional note into blockquote format.",
        "didi_scope_note_jargon": "Rewrite the DiDi scope note into plain-English leadership framing.",
        "bytedance_intern_present": "Remove TikTok / ByteDance intern content and rebuild the resume only from DiDi, Temu, and Georgia Tech CS coursework/projects.",
    }
    return priorities.get(issue.code, issue.detail)


def _build_issue_revision_instructions(issues: List[ResumeIssue]) -> str:
    ordered = sorted(
        issues,
        key=lambda item: ({"critical": 0, "high": 1, "medium": 2, "low": 3}.get(item.severity, 9), item.code),
    )
    lines = []
    for issue in ordered:
        lines.append(f"- [{issue.severity.upper()}] {issue.code}: {_fix_hint_for_issue(issue)}")
    return "\n".join(lines[:8])
