#!/usr/bin/env python3
"""
hr_review.py — 模拟真人 HR 认知审核的质量关卡模块。

与 validate_resume.py（结构化合规检查）互补：
  validate_resume.py: "有没有" — 正则 + 计数 + 集合运算
  hr_review.py:       "信不信" — Claude CLI 调用 + HR 人格 prompt

8 个审核维度 (H1-H8):
  H1: Title-Responsibility Alignment
  H2: Seniority-Scope Reasonability
  H3: Cross-Experience Narrative Coherence
  H4: Project Plausibility
  H5: Tech Stack Combination Realism
  H6: Quantitative Metric Credibility
  H7: Repetition Pattern Detection
  H8: Why-This-Role Signal

Usage:
    python3 hr_review.py --resume path/to/resume.md --jd path/to/jd.txt
    python3 hr_review.py --dir path/to/generated/
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ═══════════════════════════════════════════════════════════
# 候选人背景常量 — HR 审核的 ground truth
# ═══════════════════════════════════════════════════════════

CANDIDATE_BACKGROUND = {
    'exp-bytedance': {
        'title': 'Software Engineer Intern',
        'department': 'Security Infra',
        'location': 'San Jose, CA',
        'period': 'Dec 2024 – May 2025',
        'duration': '6 months',
        'scope': 'Individual contributor on security/compliance tooling. NO management scope.',
        'constraints': 'Intern — cannot lead teams, architect systems, drive org-wide initiatives.',
    },
    'exp-didi': {
        'title': 'Senior Data Analyst (acting Team Lead)',
        'department': 'IBG Food Business',
        'location': 'Beijing / Mexico City',
        'period': 'Sep 2022 – May 2024',
        'duration': '2 years',
        'scope': (
            '13-person cross-functional team: 3 backend, 2 frontend, 1 fullstack, 2 PM, '
            '3 data analysts, 2 LatAm sales/ops. Acted as global spokesperson for Beijing data team. '
            'Covered 6 LatAm countries (Mexico, Brazil, Chile, Colombia, Costa Rica, Dominican Republic). '
            'Tech transition: initially data analytics → grew into backend/fullstack development as '
            'team needs evolved.'
        ),
        'constraints': (
            'Title is Data Analyst but actual scope includes backend dev, dashboard building, '
            'and cross-functional coordination. This is REAL and should be explained, not hidden.'
        ),
    },
    'exp-temu': {
        'title': 'ML Data Analyst',
        'department': 'R&D Recommendation Infra',
        'location': 'Shanghai',
        'period': 'Jun 2021 – Feb 2022',
        'duration': '8 months',
        'scope': 'Junior role in recommendation/search/ads infrastructure team.',
        'constraints': (
            '8-month junior — should NOT lead teams, drive strategy, or spearhead initiatives. '
            'Can: implemented, built, developed, analyzed, processed.'
        ),
    },
    'academic': {
        'title': 'MSCS Student',
        'department': 'Georgia Tech College of Computing',
        'period': 'Expected May 2026',
        'scope': 'Course projects only.',
        'constraints': 'Academic projects — no production traffic, no enterprise revenue, no company-wide adoption.',
    },
}

# 公司名检测 markers — 用于从简历文本中识别包含哪些经历
_COMPANY_MARKERS = {
    'exp-bytedance': ['ByteDance', 'TikTok'],
    'exp-didi': ['DiDi', 'Didi'],
    'exp-temu': ['Temu'],
    'academic': ['Georgia Tech', 'Academic Projects'],
}

# ═══════════════════════════════════════════════════════════
# HR Persona Prompt — 核心
# ═══════════════════════════════════════════════════════════

HR_PERSONA_PROMPT = """You are Sarah, a Senior Technical Recruiter with 8 years at top tech companies (Google, Meta, Amazon).
You're reviewing resumes that passed ATS keyword screening. Your job: decide if this person is REAL and CREDIBLE.

YOUR COGNITIVE BIASES (intentionally injected to simulate real HR behavior):
- Primacy effect: The first 3 lines shape your gut impression
- Anchoring: Company brands (ByteDance, DiDi) influence your trust baseline
- Confirmation bias: Once you spot one red flag, you look harder for others
- Halo effect: Georgia Tech CS gives goodwill, but doesn't mask logical gaps in experience

WHAT YOU DO NOT DO:
- Full-text keyword search
- Tech coverage percentage calculation
- Format/structure checking
- Count bullets or sections

WHAT YOU DO:
- 15-30 second quick scan → form gut impression
- Flag things that "feel off"
- Judge if the career story makes sense
- Assess if someone at this level would realistically do these things
- Check if the resume tells a coherent "why this role" story

CANDIDATE BACKGROUND (use this as ground truth for credibility checks):
{candidate_background}

JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}

---

Evaluate on these 8 dimensions. For each, output: category, severity (high/medium/low), description, quote (exact text from resume), fix_suggestion. Only flag issues you actually find — it's OK to have 0 issues on some dimensions.

H1 — Title-Responsibility Alignment:
Does the work described match the job title? E.g., a "Data Analyst" whose bullets are all backend engineering → flag.
Severity: HIGH if complete mismatch, MEDIUM if partial mismatch.
NOTE: The candidate had a cross-functional role at DiDi (13-person team: backend, frontend, fullstack, PM, data analysts, LatAm ops). Data Analyst doing backend/fullstack work is PLAUSIBLE for DiDi but needs explanation. If flagged, suggest a context line.

H2 — Seniority-Scope Reasonability:
Does the scope match the experience level?
- 6-month intern "led team-wide architecture" → HIGH
- 2-year analyst "designed company-wide platform" → MEDIUM
- But: DiDi analyst acting as Team Lead for 13-person cross-functional team → PLAUSIBLE (explain context)
- ByteDance INTERN should NEVER: lead teams, drive org-wide, manage, spearhead, architect
- Temu 8-month junior should NOT: led team, drove strategy, spearheaded

H3 — Cross-Experience Narrative Coherence:
Do 3 work experiences read like one person's career journey?
ByteDance intern → Temu ML analyst → DiDi data analyst/team lead → Georgia Tech MSCS
The career arc should feel logical. Random domain jumps without explanation = MEDIUM.

H4 — Project Plausibility:
Does this project make sense for this company/department?
- ByteDance Security Infra doing recommendation system → HIGH
- DiDi Food Business doing dispatch optimization → OK
- DiDi Food Business doing compiler optimization → HIGH
- Temu R&D doing security compliance → MEDIUM

H5 — Tech Stack Combination Realism:
Are the technologies used together plausible?
- CUDA on AWS Lambda → HIGH
- PyTorch for compliance audit → MEDIUM
- Kafka + Flink for real-time analytics → OK
- React + Django + PostgreSQL for dashboard → OK

H6 — Quantitative Metric Credibility:
Are the numbers believable?
- "Reduced latency by 99.9%" → HIGH (physically implausible)
- "Processed 2M+ records daily" → OK for data pipeline
- "Improved accuracy from 60% to 95%" → MEDIUM (too dramatic without context)
- "Reduced deployment time by 40%" → OK

H7 — Repetition Pattern Detection:
Does every bullet follow the same template?
- All bullets: "Implemented X using Y, reducing Z by N%" → MEDIUM
- Variety of verbs, structures, and metric types → OK

H8 — Why-This-Role Signal:
After reading, can you articulate why this person wants THIS specific role?
- Clear narrative thread → OK
- No connection between experience and target role → LOW (advisory only)

---

OUTPUT FORMAT (strict JSON):
{{
  "gut_impression": "1-2 sentence first impression",
  "risk_level": "high|medium|low|pass",
  "issues": [
    {{
      "category": "H1",
      "severity": "high|medium|low",
      "description": "...",
      "quote": "exact text from resume",
      "fix_suggestion": "..."
    }}
  ],
  "context_lines_needed": [
    {{
      "experience": "DiDi IBG",
      "line": "_Cross-functional role spanning data analytics and backend engineering within a 13-person international team_",
      "reason": "H1: Title says Data Analyst but bullets include backend work"
    }}
  ],
  "overall_suggestions": ["suggestion 1", "suggestion 2"]
}}
"""


# ═══════════════════════════════════════════════════════════
# 数据结构
# ═══════════════════════════════════════════════════════════

@dataclass
class HRIssue:
    """单个 HR 审核问题"""
    category: str       # H1-H8 或 SYSTEM
    severity: str       # "high" / "medium" / "low"
    description: str    # 问题描述
    quote: str          # 触发问题的原文引用
    fix_suggestion: str # 修复建议


@dataclass
class HRReviewResult:
    """HR 审核结果"""
    resume_name: str
    risk_level: str                   # "high" / "medium" / "low" / "pass"
    gut_impression: str               # 1-2 句 HR 第一印象
    issues: list[HRIssue] = field(default_factory=list)
    context_lines_needed: list[dict] = field(default_factory=list)  # H1 触发时需要添加的 context lines
    overall_suggestions: list[str] = field(default_factory=list)

    @property
    def high_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "high")

    @property
    def medium_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "medium")

    @property
    def low_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "low")

    @property
    def passed(self) -> bool:
        return self.high_count == 0

    def to_text(self) -> str:
        """格式化为可读报告，参照 validate_resume.py 的 ValidationReport.to_text() 风格"""
        width = 55
        border = "═" * width
        lines = [
            border,
            f"  HR Review: {self.resume_name}",
            border,
            "",
            f"GUT IMPRESSION: {self.gut_impression}",
            f"RISK LEVEL: {self.risk_level}",
            "",
        ]

        if not self.issues:
            lines.append("No issues found — clean pass. ✅")
        else:
            for issue in self.issues:
                icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue.severity, "⚪")
                lines.append(
                    f'{icon} {issue.category} [{issue.severity.upper()}] '
                    f'{issue.description} — "{issue.quote[:80]}{"..." if len(issue.quote) > 80 else ""}" '
                    f'— Suggestion: {issue.fix_suggestion}'
                )

        if self.context_lines_needed:
            lines.append("")
            lines.append("CONTEXT LINES NEEDED:")
            for ctx in self.context_lines_needed:
                lines.append(f"  📝 [{ctx.get('experience', '?')}] {ctx.get('line', '')}")
                lines.append(f"     Reason: {ctx.get('reason', '')}")

        if self.overall_suggestions:
            lines.append("")
            lines.append("OVERALL SUGGESTIONS:")
            for idx, sug in enumerate(self.overall_suggestions, 1):
                lines.append(f"  {idx}. {sug}")

        lines.extend([
            "",
            border,
            f"  RESULT: {'PASS' if self.passed else 'FAIL'} "
            f"({self.high_count} high, {self.medium_count} medium, {self.low_count} low)",
            border,
        ])
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return asdict(self)


# ═══════════════════════════════════════════════════════════
# Claude CLI 调用
# ═══════════════════════════════════════════════════════════

def _call_claude(prompt: str, timeout: int = 120) -> str | None:
    """调用 Claude CLI — 与 generate_resume.py 的 _call_claude 相同实现"""
    try:
        process = subprocess.run(
            ['claude', '-p', prompt, '--no-input'],
            capture_output=True, text=True, timeout=timeout,
        )
        if process.returncode != 0:
            print(f"[HR Review] ❌ CLI error: {process.stderr[:200]}")
            return None
        return process.stdout.strip()
    except subprocess.TimeoutExpired:
        print("[HR Review] ❌ CLI timeout")
        return None
    except FileNotFoundError:
        print("[HR Review] ❌ 'claude' CLI not found — please install Claude CLI first")
        return None
    except Exception as e:
        print(f"[HR Review] ❌ Exception: {e}")
        return None


# ═══════════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════════

def _build_candidate_background_text(resume_text: str) -> str:
    """从简历文本中检测公司名，拼接对应的背景信息"""
    sections = []
    for key, bg in CANDIDATE_BACKGROUND.items():
        if any(m in resume_text for m in _COMPANY_MARKERS.get(key, [])):
            parts = [
                f"[{bg['title']} @ {bg.get('department', '')}]",
                f"Period: {bg.get('period', 'N/A')},",
                f"Duration: {bg.get('duration', 'N/A')}.",
                f"Scope: {bg['scope']}",
                f"Constraints: {bg['constraints']}",
            ]
            sections.append(" ".join(parts))
    return "\n".join(sections) if sections else "No matching candidate background found."


def _parse_json_response(raw: str) -> dict | None:
    """从 LLM 输出中提取 JSON 对象，容错处理"""
    # 尝试直接解析
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # 尝试提取 ```json ... ``` 代码块
    code_block = re.search(r'```json\s*(\{.*?\})\s*```', raw, re.DOTALL)
    if code_block:
        try:
            return json.loads(code_block.group(1))
        except json.JSONDecodeError:
            pass

    # 尝试提取最外层 { ... }
    brace_match = re.search(r'(\{.*\})', raw, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(1))
        except json.JSONDecodeError:
            pass

    return None


# ═══════════════════════════════════════════════════════════
# 核心审核函数
# ═══════════════════════════════════════════════════════════

def review_resume(
    resume_text: str,
    jd_text: str,
    resume_name: str = "resume.md",
) -> HRReviewResult:
    """对单份简历做 HR 审核"""
    background = _build_candidate_background_text(resume_text)
    prompt = HR_PERSONA_PROMPT.format(
        candidate_background=background,
        jd_text=jd_text,
        resume_text=resume_text,
    )

    raw = _call_claude(prompt, timeout=180)
    if not raw:
        return HRReviewResult(
            resume_name=resume_name,
            risk_level="high",
            gut_impression="HR Review failed — Claude CLI error",
            issues=[HRIssue("SYSTEM", "high", "Claude CLI call failed", "", "Retry")],
        )

    # 解析 JSON
    data = _parse_json_response(raw)
    if data is None:
        return HRReviewResult(
            resume_name=resume_name,
            risk_level="high",
            gut_impression="HR Review failed — JSON parse error",
            issues=[HRIssue("SYSTEM", "high", "Could not parse LLM output", raw[:200], "Retry")],
        )

    issues = [
        HRIssue(
            category=i.get("category", "?"),
            severity=i.get("severity", "medium"),
            description=i.get("description", ""),
            quote=i.get("quote", ""),
            fix_suggestion=i.get("fix_suggestion", ""),
        )
        for i in data.get("issues", [])
    ]

    return HRReviewResult(
        resume_name=resume_name,
        risk_level=data.get("risk_level", "medium"),
        gut_impression=data.get("gut_impression", ""),
        issues=issues,
        context_lines_needed=data.get("context_lines_needed", []),
        overall_suggestions=data.get("overall_suggestions", []),
    )


# ═══════════════════════════════════════════════════════════
# 批量审核
# ═══════════════════════════════════════════════════════════

def review_all_benchmark(
    generated_dir: str | Path,
    jd_source: str = "benchmark",
) -> list[HRReviewResult]:
    """批量审核 benchmark 输出目录下的所有简历

    使用 hr_benchmark.py 的 CASE_BLUEPRINTS + build_jd_text 来重建 JD。
    """
    generated_dir = Path(generated_dir)
    results: list[HRReviewResult] = []

    # 导入 hr_benchmark 模块
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from hr_benchmark import (
        CASE_BLUEPRINTS,
        build_jd_text,
        load_inputs,
        slugify,
    )

    # 加载数据源（与 hr_benchmark.run() 相同）
    parsed_resumes, catalog, store, tech_profiles = load_inputs()

    for case in CASE_BLUEPRINTS:
        case_id = case["case_id"]
        slug = slugify(f"{case_id}_{case['jd_title']}")

        # 查找生成的简历
        resume_path = generated_dir / f"{slug}.md"
        if not resume_path.exists():
            # 尝试模糊匹配
            candidates = list(generated_dir.glob(f"{case_id}-*.md"))
            if candidates:
                resume_path = candidates[0]
            else:
                print(f"[HR] ⚠️ Case {case_id}: No resume found at {slug}.md, skipping")
                continue

        resume_text = resume_path.read_text(encoding="utf-8")

        # 重建 JD 文本（与 hr_benchmark.run() 相同逻辑）
        parsed = parsed_resumes[case["source_file"]]
        catalog_entry = catalog[case["source_file"]]
        jd_text = build_jd_text(case, parsed, catalog_entry, tech_profiles)

        print(f"[HR] 审核 Case {case_id}: {case.get('direction_label', '')}...")
        result = review_resume(resume_text, jd_text, resume_name=resume_path.name)
        results.append(result)

        # 输出简要结果
        status = "✅ PASS" if result.passed else f"❌ {result.risk_level.upper()}"
        print(f"  → {status} | {result.gut_impression}")
        if result.issues:
            for issue in result.issues:
                icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue.severity, "⚪")
                print(f"    {icon} {issue.category}: {issue.description}")

    # 汇总
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    print(f"\n{'=' * 50}")
    print(f"HR Review Summary: {passed}/{total} PASS")
    print(f"{'=' * 50}")

    # 保存结果
    output_path = generated_dir.parent / "hr_review_results.json"
    output_data = [r.to_dict() for r in results]
    output_path.write_text(
        json.dumps(output_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Results saved to: {output_path}")

    return results


# ═══════════════════════════════════════════════════════════
# CLI 入口
# ═══════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(
        description="HR Review — 模拟真人 HR 审核简历",
    )
    parser.add_argument("--resume", type=str, help="单份简历文件路径")
    parser.add_argument("--jd", type=str, help="JD 文件路径")
    parser.add_argument("--jd-text", type=str, help="JD 文本（直接传入）")
    parser.add_argument("--dir", type=str, help="批量审核目录（benchmark 输出目录）")
    parser.add_argument("--output", type=str, help="结果输出路径")
    args = parser.parse_args()

    if args.dir:
        review_all_benchmark(args.dir)
        return 0

    if not args.resume:
        parser.error("Must provide --resume or --dir")

    resume_path = Path(args.resume)
    if not resume_path.exists():
        print(f"❌ Resume file not found: {resume_path}")
        return 1

    resume_text = resume_path.read_text(encoding="utf-8")

    jd_text: str
    if args.jd:
        jd_path = Path(args.jd)
        if not jd_path.exists():
            print(f"❌ JD file not found: {jd_path}")
            return 1
        jd_text = jd_path.read_text(encoding="utf-8")
    elif args.jd_text:
        jd_text = args.jd_text
    else:
        parser.error("Must provide --jd or --jd-text when using --resume")
        return 1  # unreachable, parser.error raises

    result = review_resume(resume_text, jd_text, resume_name=resume_path.name)
    print(result.to_text())

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(result.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\nResults saved to: {out}")

    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
