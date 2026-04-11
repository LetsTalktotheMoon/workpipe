#!/usr/bin/env python3
"""
resume_polisher.py — 逐句适配润色器（LLM 驱动，调用 Claude CLI）。

Polisher 回答一个问题："这条 bullet 怎么微调措辞让它更贴 JD？"

原则：
- 不改含义：相同的故事、相同的指标、相同的动作
- 调术语：用 JD 的措辞替换同义词
- 调语气：根据 seniority 调整动词
- 调技术：利用 catom 的 tech_or_pool 替换为 JD 要求的等价技术
- 调领域：利用 catom 的 domain_or_pool 替换为 JD 相关的业务场景
- 规则驱动优先，LLM 仅在 domain_adapt 时触发
- bold terms 守护：任何 LLM 输出如果改了 bold terms 必须被拒绝

Usage:
    python3 resume_polisher.py --demo
    python3 resume_polisher.py --jd path/to/jd.txt
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
# 数据结构
# ═══════════════════════════════════════════════════════════

@dataclass
class PolishResult:
    """单条 bullet 的润色结果"""
    catom_id: str
    original_text: str
    polished_text: str
    changes_made: list[str]   # 描述做了什么改动
    was_modified: bool        # 是否真的改了


@dataclass
class PolishReport:
    """整份简历的润色报告"""
    total_bullets: int
    modified_count: int
    skipped_count: int
    results: list[PolishResult] = field(default_factory=list)

    def to_text(self) -> str:
        lines = ["═" * 50]
        lines.append(f"  Polish Report: {self.modified_count}/{self.total_bullets} modified")
        lines.append("═" * 50)
        for r in self.results:
            if r.was_modified:
                lines.append(f"\n  [{r.catom_id}]")
                orig_preview = r.original_text[:100] + ("..." if len(r.original_text) > 100 else "")
                pol_preview = r.polished_text[:100] + ("..." if len(r.polished_text) > 100 else "")
                lines.append(f"  BEFORE: {orig_preview}")
                lines.append(f"  AFTER:  {pol_preview}")
                lines.append(f"  CHANGES: {', '.join(r.changes_made)}")
        lines.append("\n" + "═" * 50)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return asdict(self)


# ═══════════════════════════════════════════════════════════
# 弱动词 → 强动词 映射
# ═══════════════════════════════════════════════════════════

WEAK_TO_STRONG = {
    'assisted': 'Implemented',
    'helped': 'Developed',
    'supported': 'Built',
    'participated': 'Contributed to',
    'contributed': 'Delivered',
}


# ═══════════════════════════════════════════════════════════
# Claude CLI 调用
# ═══════════════════════════════════════════════════════════

def _call_claude(prompt: str, timeout: int = 60) -> str | None:
    """调用 Claude CLI 进行微润色"""
    try:
        process = subprocess.run(
            ['claude', '-p', prompt, '--no-input'],
            capture_output=True, text=True, timeout=timeout,
        )
        if process.returncode != 0:
            print(f"[Polisher] ❌ CLI error: {process.stderr[:200]}")
            return None
        return process.stdout.strip()
    except subprocess.TimeoutExpired:
        print("[Polisher] ❌ CLI timeout")
        return None
    except FileNotFoundError:
        print("[Polisher] ❌ 'claude' CLI not found")
        return None
    except Exception as e:
        print(f"[Polisher] ❌ Exception: {e}")
        return None


# ═══════════════════════════════════════════════════════════
# 润色判断
# ═══════════════════════════════════════════════════════════

def _needs_polishing(
    catom: dict,
    jd_profile: dict,
    plan: dict | None = None,
) -> tuple[bool, list[str]]:
    """判断一条 catom 是否需要润色，返回 (需要, 原因列表)"""
    reasons: list[str] = []
    text = catom.get('_resolved_text', '')
    if not text:
        return False, []

    text_lower = text.lower()
    tech_required = set(t.lower() for t in jd_profile.get('tech_required', []))
    tech_expanded = set(t.lower() for t in jd_profile.get('tech_expanded', []))

    # 检查1：catom 有 tech_or_pool 且当前用的技术不在 JD 中，但 pool 中有 JD 的技术
    tech_or_pool = catom.get('tech_or_pool', {})
    bold_techs = set(t.lower() for t in re.findall(r'\*\*([^*]+)\*\*', text))

    for tech, alternatives in tech_or_pool.items():
        if not isinstance(alternatives, list):
            continue
        if tech.lower() in bold_techs and tech.lower() not in tech_expanded:
            # 当前技术不在 JD 中，检查替代品
            for alt in alternatives:
                if alt.lower() in tech_expanded:
                    reasons.append(f"tech_swap: {tech} → {alt}")
                    break

    # 检查2：domain_or_pool 有更匹配 JD 的领域
    domain_or_pool = catom.get('domain_or_pool', {})
    biz_domains = set(jd_profile.get('biz_domains', []))
    catom_domains = set(catom.get('domain_options', []))
    if domain_or_pool and not (catom_domains & biz_domains):
        if isinstance(domain_or_pool, dict):
            for domain, alternatives in domain_or_pool.items():
                if isinstance(alternatives, list) and any(alt in biz_domains for alt in alternatives):
                    reasons.append(f"domain_adapt: {domain} → JD domain")
                    break

    # 检查3：seniority_variants 有更合适的表达
    seniority_variants = catom.get('seniority_variants', {})
    jd_seniority = jd_profile.get('seniority', 'mid_1_3y')
    if seniority_variants and jd_seniority in seniority_variants:
        variant_text = seniority_variants[jd_seniority]
        if isinstance(variant_text, str) and variant_text.lower() != text_lower:
            reasons.append(f"seniority_adapt: → {jd_seniority}")

    # 检查4：第一个词不是强动词
    stripped = text.replace('**', '').strip()
    first_word = stripped.split()[0] if stripped else ''
    if first_word.lower() in WEAK_TO_STRONG:
        reasons.append(f"weak_verb: {first_word}")

    return bool(reasons), reasons


# ═══════════════════════════════════════════════════════════
# 核心润色函数
# ═══════════════════════════════════════════════════════════

def polish_bullet(
    catom: dict,
    jd_profile: dict,
    exp_id: str,
    plan_strategy: dict | None = None,
) -> PolishResult:
    """对单条 bullet 进行润色

    优先使用规则驱动替换（零 LLM）：
    1. tech_or_pool 直接替换 bold 技术词
    2. seniority_variants 直接使用对应级别变体
    3. 弱动词 → 强动词替换

    LLM 仅在 domain_adapt 时触发，且有 bold terms 守护。
    """
    original_text = catom.get('_resolved_text', '')
    catom_id = catom.get('catom_id', 'unknown')

    needs_polish, reasons = _needs_polishing(catom, jd_profile)

    if not needs_polish:
        return PolishResult(
            catom_id=catom_id,
            original_text=original_text,
            polished_text=original_text,
            changes_made=[],
            was_modified=False,
        )

    # ── 规则驱动替换 ──
    polished = original_text
    changes: list[str] = []

    # 规则1：tech_or_pool 直接替换
    tech_expanded = set(t.lower() for t in jd_profile.get('tech_expanded', []))
    tech_or_pool = catom.get('tech_or_pool', {})
    for tech, alternatives in tech_or_pool.items():
        if not isinstance(alternatives, list):
            continue
        if tech.lower() not in tech_expanded:
            for alt in alternatives:
                if alt.lower() in tech_expanded:
                    # 替换 **tech** → **alt**（保持 bold）
                    pattern = re.compile(r'\*\*' + re.escape(tech) + r'\*\*', re.IGNORECASE)
                    if pattern.search(polished):
                        polished = pattern.sub(f'**{alt}**', polished)
                        changes.append(f"tech: {tech} → {alt}")
                    break

    # 规则2：seniority_variants 直接使用
    seniority_variants = catom.get('seniority_variants', {})
    jd_seniority = jd_profile.get('seniority', 'mid_1_3y')
    if jd_seniority in seniority_variants:
        variant = seniority_variants[jd_seniority]
        if isinstance(variant, str) and variant and variant != original_text:
            polished = variant
            changes.append(f"seniority: → {jd_seniority} variant")

    # 规则3：弱动词替换（零 LLM）
    stripped = polished.replace('**', '').strip()
    first_word = stripped.split()[0] if stripped else ''
    if first_word.lower() in WEAK_TO_STRONG:
        replacement = WEAK_TO_STRONG[first_word.lower()]
        polished = polished.replace(first_word, replacement, 1)
        changes.append(f"verb: {first_word} → {replacement}")

    # 如果规则替换已经改了，不用调 LLM
    if changes and polished != original_text:
        return PolishResult(
            catom_id=catom_id,
            original_text=original_text,
            polished_text=polished,
            changes_made=changes,
            was_modified=True,
        )

    # ── LLM 驱动：仅 domain_adapt ──
    domain_reasons = [r for r in reasons if 'domain_adapt' in r]
    if domain_reasons:
        biz_domains = jd_profile.get('biz_domains', [])
        role_type = jd_profile.get('role_type', 'backend')

        prompt = (
            f"Adapt this resume bullet's business narrative to {role_type} / {', '.join(biz_domains)}.\n"
            f"Keep ALL **bold** technical terms EXACTLY as-is. Keep metrics. "
            f"Keep sentence structure similar.\n"
            f"Only change the business context words (not tech terms, not numbers).\n\n"
            f"Original: {polished}\n\n"
            f"Output ONLY the adapted bullet text, nothing else."
        )

        result = _call_claude(prompt)
        if result:
            # bold terms 守护：验证 bold terms 没被改
            orig_bolds = set(re.findall(r'\*\*([^*]+)\*\*', polished))
            new_bolds = set(re.findall(r'\*\*([^*]+)\*\*', result))
            if orig_bolds == new_bolds:  # bold terms 完全相同才接受
                polished = result
                changes.append("domain adapted via LLM")
            else:
                changes.append("domain LLM rejected (bold terms changed)")

    return PolishResult(
        catom_id=catom_id,
        original_text=original_text,
        polished_text=polished,
        changes_made=changes,
        was_modified=polished != original_text,
    )


def polish_selected(
    selected: dict,
    jd_profile: dict,
    plan: dict | None = None,
) -> tuple[dict, PolishReport]:
    """对 select_catoms() 的输出进行全面润色。

    参数：
        selected: exp_id → list[(score, catom)] — select_catoms() 的输出
        jd_profile: JD 解析结果
        plan: ResumePlan.to_dict() 的输出（可选）

    返回：
        polished_selected: 与 selected 结构相同，但 _resolved_text 已润色
        report: PolishReport
    """
    polished_selected: dict = {}
    all_results: list[PolishResult] = []
    total = 0
    modified = 0

    for exp_id, items in selected.items():
        polished_items: list[tuple] = []
        plan_strategy = None
        if plan and 'experience_strategies' in plan:
            strat = plan['experience_strategies'].get(exp_id)
            if strat:
                plan_strategy = strat if isinstance(strat, dict) else asdict(strat)

        for score, catom in items:
            total += 1
            result = polish_bullet(catom, jd_profile, exp_id, plan_strategy)
            all_results.append(result)

            if result.was_modified:
                modified += 1
                catom = dict(catom)  # 浅拷贝避免修改原 catom
                catom['_resolved_text'] = result.polished_text
                catom['_polished'] = True
                catom['_polish_changes'] = result.changes_made

            polished_items.append((score, catom))

        polished_selected[exp_id] = polished_items

    report = PolishReport(
        total_bullets=total,
        modified_count=modified,
        skipped_count=total - modified,
        results=all_results,
    )

    return polished_selected, report


# ═══════════════════════════════════════════════════════════
# CLI 入口
# ═══════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(description="Resume Polisher — 逐句适配润色")
    parser.add_argument("--demo", action="store_true", help="运行 demo 模式（不调 LLM）")
    parser.add_argument("--jd", type=str, help="JD 文件路径")
    parser.add_argument("--jd-text", type=str, help="JD 文本")
    parser.add_argument("--output", type=str, help="输出报告路径")
    args = parser.parse_args()

    if args.demo:
        # Demo 模式：用 mock catom 演示 tech_swap 等规则驱动替换
        mock_catom = {
            'catom_id': 'demo-001',
            '_resolved_text': (
                'Built a real-time **Kafka** ingestion pipeline for security log aggregation, '
                'processing 2M+ events daily with **Flink** stream processing'
            ),
            'tech_or_pool': {
                'Kafka': ['RabbitMQ', 'Pulsar', 'Kinesis'],
                'Flink': ['Spark', 'Beam'],
            },
            'domain_or_pool': {
                'security': ['recommendation', 'analytics', 'ads'],
            },
            'domain_options': ['security_infrastructure'],
            'seniority_variants': {
                'intern': (
                    'Implemented a real-time **Kafka** ingestion pipeline for log aggregation, '
                    'processing 2M+ events daily'
                ),
                'mid_1_3y': (
                    'Designed a real-time **Kafka** ingestion pipeline for security log aggregation, '
                    'processing 2M+ events daily with **Flink** stream processing'
                ),
            },
        }
        mock_jd = {
            'role_type': 'data',
            'seniority': 'mid_1_3y',
            'tech_required': {'spark', 'airflow', 'postgresql'},
            'tech_expanded': {'spark', 'airflow', 'postgresql', 'python', 'sql', 'kafka', 'kinesis'},
            'biz_domains': ['analytics', 'data_pipeline'],
        }

        print("═" * 50)
        print("  Resume Polisher — Demo Mode")
        print("═" * 50)
        print()

        result = polish_bullet(mock_catom, mock_jd, 'exp-bytedance')
        print(f"Original:  {result.original_text}")
        print(f"Polished:  {result.polished_text}")
        print(f"Modified:  {result.was_modified}")
        print(f"Changes:   {result.changes_made}")

        print()
        print("═" * 50)
        print("  Demo 2: Weak verb replacement")
        print("═" * 50)
        print()

        mock_catom_2 = {
            'catom_id': 'demo-002',
            '_resolved_text': 'Assisted in building **Docker** containerization for CI/CD pipeline deployment',
            'tech_or_pool': {},
            'domain_or_pool': {},
            'domain_options': [],
            'seniority_variants': {},
        }
        mock_jd_2 = {
            'role_type': 'devops',
            'seniority': 'mid_1_3y',
            'tech_required': {'docker', 'kubernetes'},
            'tech_expanded': {'docker', 'kubernetes', 'terraform', 'github actions'},
            'biz_domains': ['devops'],
        }
        result2 = polish_bullet(mock_catom_2, mock_jd_2, 'exp-bytedance')
        print(f"Original:  {result2.original_text}")
        print(f"Polished:  {result2.polished_text}")
        print(f"Modified:  {result2.was_modified}")
        print(f"Changes:   {result2.changes_made}")

        return 0

    if not args.jd and not args.jd_text:
        parser.error("Must provide --jd or --jd-text, or use --demo")

    jd_text: str = args.jd_text or Path(args.jd).read_text(encoding='utf-8')

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from generate_resume import expand_tech_if_sparse, load_store, parse_jd, select_catoms

    jd_profile = expand_tech_if_sparse(parse_jd(jd_text))
    store = load_store()
    selected = select_catoms(store, jd_profile)

    polished, report = polish_selected(selected, jd_profile)
    print(report.to_text())

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps([asdict(r) for r in report.results], indent=2, ensure_ascii=False),
            encoding='utf-8',
        )
        print(f"\nReport saved to: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
