#!/usr/bin/env python3
"""
resume_planner.py — 全局简历策略规划器（规则驱动，零 LLM）。

Planner 回答一个问题："这份简历应该讲什么故事？"

给定 JD profile 和 329 个 catom 的矩阵，输出一个 ResumePlan，告诉 select_catoms：
- 三段经历分别该侧重什么子领域
- 两个项目应该分配给哪两个公司、什么主题
- 哪些技术是"必须出现"的、哪些是"自然附带"的
- 整体叙事弧线（career progression）

Usage:
    python3 resume_planner.py --jd path/to/jd.txt
    python3 resume_planner.py --jd-text "We are hiring..."
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONSOLIDATED_STORE = ROOT / "consolidated_atom_store.json"
TECH_PROFILE = ROOT / "tech_profile_matrix.json"


# ═══════════════════════════════════════════════════════════
# 数据结构
# ═══════════════════════════════════════════════════════════

@dataclass
class ProjectStrategy:
    """单个项目的策略"""
    exp_id: str                      # 'exp-bytedance' / 'exp-didi' / ...
    theme: str                       # 期望的子领域主题
    tech_must_include: list[str]     # 项目中必须出现的技术
    tech_nice_to_have: list[str]     # 最好出现的技术
    bullet_count: tuple[int, int]    # (min, max) bullets
    priority: int                    # 1=最重要, 2=次要


@dataclass
class ExperienceStrategy:
    """单段经历的策略"""
    exp_id: str
    narrative_role: str              # "foundation" / "growth" / "specialization" / "academic"
    theme_focus: str                 # 侧重的子领域
    tech_emphasis: list[str]         # 该经历中应突出的技术
    tech_deemphasis: list[str]       # 该经历中应淡化的技术
    seniority_level: str             # 该经历对应的 seniority key
    project_count: int               # 分配的项目数 (0, 1, or 2)
    general_bullet_count: int        # 分配的 general bullet 数
    catom_preference_tags: list[str] # 偏好的 angle_tags


@dataclass
class ResumePlan:
    """完整的简历规划"""
    jd_role_type: str
    jd_seniority: str
    narrative_arc: str               # 1-2 句话描述整体叙事弧线
    experience_strategies: dict[str, ExperienceStrategy]  # exp_id → strategy
    project_strategies: list[ProjectStrategy]              # 2 个项目策略
    tech_budget: dict                # {'must_appear': [...], 'nice_to_have': [...], 'avoid': [...]}
    summary_theme: str               # Professional Summary 应该传达的核心主题
    risk_notes: list[str]            # 规划中识别的风险点
    writer_needed: bool              # 是否预判需要 Writer 生成内容
    writer_reason: str               # 如果需要 Writer，原因是什么

    def to_dict(self) -> dict:
        return asdict(self)

    def to_text(self) -> str:
        """格式化为可读的规划报告"""
        lines = ["═" * 50]
        lines.append(f"  Resume Plan: {self.jd_role_type} ({self.jd_seniority})")
        lines.append("═" * 50)
        lines.append(f"\n📖 NARRATIVE: {self.narrative_arc}")
        lines.append(f"\n🎯 SUMMARY THEME: {self.summary_theme}")

        lines.append("\n📋 EXPERIENCE STRATEGIES:")
        for exp_id, strat in self.experience_strategies.items():
            lines.append(f"  [{exp_id}] Role: {strat.narrative_role}")
            lines.append(f"    Theme: {strat.theme_focus}")
            lines.append(f"    Tech emphasis: {', '.join(strat.tech_emphasis[:5])}")
            lines.append(f"    Projects: {strat.project_count}, General: {strat.general_bullet_count}")

        lines.append("\n🏗️ PROJECT STRATEGIES:")
        for ps in self.project_strategies:
            lines.append(f"  P{ps.priority}: {ps.exp_id} — {ps.theme}")
            lines.append(f"    Must include: {', '.join(ps.tech_must_include)}")

        lines.append(f"\n💻 TECH BUDGET:")
        lines.append(f"  Must appear: {', '.join(self.tech_budget.get('must_appear', []))}")
        lines.append(f"  Nice to have: {', '.join(self.tech_budget.get('nice_to_have', []))}")

        if self.writer_needed:
            lines.append(f"\n⚠️ WRITER NEEDED: {self.writer_reason}")

        if self.risk_notes:
            lines.append("\n⚠️ RISKS:")
            for note in self.risk_notes:
                lines.append(f"  - {note}")

        lines.append("\n" + "═" * 50)
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
# 常量：经历元数据
# ═══════════════════════════════════════════════════════════

EXPERIENCE_META = {
    'exp-bytedance': {
        'company': 'ByteDance/TikTok',
        'actual_role': 'Software Engineer Intern',
        'seniority_key': 'intern',
        'duration_months': 6,
        'natural_domains': ['security', 'compliance', 'infrastructure', 'backend', 'devops'],
        'natural_techs': ['go', 'python', 'docker', 'kubernetes', 'grpc', 'kafka'],
        'max_projects': 2,
        'budget_total': 10,
        'general_max': 4,
    },
    'exp-didi': {
        'company': 'DiDi IBG',
        'actual_role': 'Senior Data Analyst (acting Team Lead)',
        'seniority_key': 'didi_analyst_lead',
        'duration_months': 24,
        'natural_domains': ['data', 'analytics', 'backend', 'fullstack', 'geo-spatial', 'dispatch', 'cross-border'],
        'natural_techs': ['python', 'sql', 'flink', 'spark', 'react', 'typescript', 'fastapi'],
        'max_projects': 1,
        'budget_total': 7,
        'general_max': 5,
    },
    'exp-temu': {
        'company': 'Temu',
        'actual_role': 'ML Data Analyst',
        'seniority_key': 'intern',  # 8 months junior — 与 intern 同等约束
        'duration_months': 8,
        'natural_domains': ['recommendation', 'search', 'ads', 'ml', 'data'],
        'natural_techs': ['python', 'sql', 'pytorch', 'tensorflow'],
        'max_projects': 1,
        'budget_total': 5,
        'general_max': 3,
    },
    'academic': {
        'company': 'Georgia Tech',
        'actual_role': 'MSCS Student',
        'seniority_key': 'academic',
        'duration_months': 24,
        'natural_domains': ['systems', 'compiler', 'hpc', 'distributed', 'gpu', 'ml', 'web'],
        'natural_techs': ['c++', 'python', 'cuda', 'mpi'],
        'max_projects': 1,
        'budget_total': 2,
        'general_max': 0,
    },
}

# JD role → 最匹配的公司经历（优先级排序）
ROLE_EXP_AFFINITY = {
    'backend':      ['exp-bytedance', 'exp-didi', 'exp-temu'],
    'ai_genai':     ['exp-temu', 'exp-bytedance', 'exp-didi'],
    'data':         ['exp-didi', 'exp-temu', 'exp-bytedance'],
    'security':     ['exp-bytedance', 'exp-didi', 'exp-temu'],
    'devops':       ['exp-bytedance', 'exp-didi', 'exp-temu'],
    'cloud_infra':  ['exp-bytedance', 'exp-didi', 'exp-temu'],
    'frontend':     ['exp-didi', 'exp-temu', 'exp-bytedance'],
    'mobile':       ['exp-didi', 'exp-temu', 'exp-bytedance'],
    'fintech':      ['exp-didi', 'exp-bytedance', 'exp-temu'],
    'embedded':     ['exp-bytedance', 'exp-didi', 'exp-temu'],
    'hpc_compiler': ['exp-bytedance', 'exp-didi', 'exp-temu'],
    'qa_sdet':      ['exp-bytedance', 'exp-didi', 'exp-temu'],
}

# 角色 → angle_tag 映射
ROLE_TO_ANGLE = {
    'ai_genai': ['ai', 'data'], 'backend': ['backend'],
    'data': ['data', 'ai'], 'security': ['security'],
    'devops': ['devops', 'cloud'], 'frontend': ['frontend'],
    'mobile': ['mobile'], 'fintech': ['fintech', 'backend'],
    'cloud_infra': ['devops', 'cloud'], 'embedded': ['embedded', 'hpc'],
    'hpc_compiler': ['hpc', 'embedded'], 'qa_sdet': ['qa'],
}

# 角色 → 可读标签
ROLE_LABELS = {
    'backend': 'backend engineering',
    'ai_genai': 'AI/ML engineering',
    'data': 'data engineering',
    'security': 'security engineering',
    'devops': 'DevOps/platform',
    'frontend': 'frontend engineering',
    'mobile': 'mobile development',
    'fintech': 'fintech backend',
    'cloud_infra': 'cloud infrastructure',
    'embedded': 'embedded systems',
    'hpc_compiler': 'HPC/systems',
    'qa_sdet': 'QA automation',
}

# 项目主题可选池（与 generate_resume.py 的 THEME_DOMAINS 保持同步）
THEME_POOL = {
    'exp-bytedance': [
        'security compliance & policy automation',
        'threat detection & incident response',
        'security monitoring & observability',
        'vulnerability scanning & remediation',
        'access control & identity management',
        'audit logging & forensic analysis',
    ],
    'exp-didi': [
        'dispatch optimization & fleet analytics',
        'fraud detection & risk scoring',
        'cross-border data compliance & localization',
        'geo-spatial analytics & routing',
        'payment & settlement systems',
        'LatAm market analytics & operations dashboard',
        'full-stack business intelligence platform',
        'driver supply-demand modeling',
    ],
    'exp-temu': [
        'recommendation ranking & serving',
        'search relevance & query understanding',
        'user behavior modeling & cold start',
        'ads targeting & monetization',
        'content moderation & trust safety',
    ],
    'academic': [
        'systems architecture simulation',
        'compiler optimization',
        'distributed computing',
        'GPU pipeline modeling',
    ],
}

# 主题关键词得分表 — 用于 _select_best_theme
_ROLE_THEME_KEYWORDS: dict[str, list[str]] = {
    'backend':      ['services', 'api', 'systems'],
    'data':         ['analytics', 'data', 'pipeline'],
    'security':     ['security', 'compliance', 'threat', 'access'],
    'ai_genai':     ['ml', 'ai', 'recommendation', 'modeling'],
    'frontend':     ['dashboard', 'ui', 'platform', 'full-stack'],
    'devops':       ['monitoring', 'automation', 'deployment'],
    'fintech':      ['payment', 'fraud', 'settlement', 'billing'],
    'cloud_infra':  ['infrastructure', 'platform', 'monitoring'],
    'embedded':     ['sensor', 'device', 'firmware'],
    'hpc_compiler': ['compiler', 'gpu', 'hpc'],
    'qa_sdet':      ['testing', 'verification', 'quality'],
    'mobile':       ['mobile', 'app', 'ui'],
}


# ═══════════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════════

def _select_best_theme(
    themes: list[str],
    existing_themes: list[str],
    role_type: str,
    biz_domains: set[str],
    tech_required: set[str],
) -> str:
    """从可选主题中选择与 JD 最匹配且不重复的主题

    规则：
    1. 排除 existing_themes 中已选的主题
    2. 优先选包含 role_type 关键词的主题
    3. 其次选与 biz_domains 有交集的
    4. 兜底选第一个未选的
    """
    available = [t for t in themes if t not in existing_themes]
    if not available:
        return themes[0] if themes else "general"

    def theme_score(theme: str) -> float:
        score = 0.0
        theme_lower = theme.lower()
        # role_type 关键词匹配
        for kw in _ROLE_THEME_KEYWORDS.get(role_type, []):
            if kw in theme_lower:
                score += 3.0
        # biz_domains 匹配
        for domain in biz_domains:
            domain_words = domain.lower().replace('_', ' ').split()
            if any(w in theme_lower for w in domain_words):
                score += 2.0
        return score

    available.sort(key=lambda t: -theme_score(t))
    return available[0]


def _select_project_techs(
    exp_id: str,
    tech_required: set[str],
    tech_expanded: set[str],
    meta: dict,
) -> list[str]:
    """确定项目中应该包含的技术

    优先级：
    1. JD required ∩ experience natural
    2. JD expanded ∩ experience natural
    3. 纯 JD required（兜底）
    """
    natural = set(t.lower() for t in meta['natural_techs'])
    # 优先选 JD required 且 experience natural 的交集
    must = list(tech_required & natural)
    # 补充 JD expanded 且 experience natural 的
    if len(must) < 3:
        must.extend(list((tech_expanded & natural) - set(must))[:3 - len(must)])
    # 最后补充纯 JD required 的
    if len(must) < 2:
        must.extend(list(tech_required - set(must))[:2 - len(must)])
    return must


def _check_coverage(
    catoms: list[dict],
    jd_profile: dict,
    project_strategies: list[ProjectStrategy],
) -> tuple[bool, str]:
    """检查 catom 矩阵能否覆盖规划的项目，预判 Writer 需求"""
    role_type = jd_profile.get('role_type', 'backend')
    reasons: list[str] = []

    for ps in project_strategies:
        # 统计该 exp_id 下的 project catoms 数量
        proj_catoms = [
            c for c in catoms
            if c.get('parent_exp_id') == ps.exp_id
            and c.get('is_project_bullet', False)
        ]

        if len(proj_catoms) < ps.bullet_count[0]:
            reasons.append(
                f"{ps.exp_id} 项目 catom 不足: 有 {len(proj_catoms)}, 需要 {ps.bullet_count[0]}+"
            )

        # 检查 angle_tags 匹配
        role_matched = [
            c for c in proj_catoms
            if role_type in c.get('angle_tags', [])
            or any(t in c.get('angle_tags', []) for t in ['backend', role_type])
        ]
        if len(role_matched) < ps.bullet_count[0]:
            reasons.append(
                f"{ps.exp_id} 方向匹配的项目 catom 不足: "
                f"有 {len(role_matched)}, 需要 {ps.bullet_count[0]}+"
            )

    if reasons:
        return True, "; ".join(reasons)
    return False, ""


def _build_narrative_arc(
    sorted_exps: list[str],
    exp_strategies: dict[str, ExperienceStrategy],
    role_type: str,
    seniority: str,
) -> str:
    """构建叙事弧线描述"""
    company_names = {
        'exp-bytedance': 'ByteDance',
        'exp-didi': 'DiDi',
        'exp-temu': 'Temu',
    }

    arc_parts = []
    for exp_id in sorted_exps:
        strat = exp_strategies.get(exp_id)
        if strat:
            name = company_names.get(exp_id, exp_id)
            arc_parts.append(f"{name}({strat.narrative_role}: {strat.theme_focus})")

    target = ROLE_LABELS.get(role_type, role_type)
    return f"Career progression toward {target}: {' → '.join(arc_parts)} → Georgia Tech MSCS (deepening)"


def _build_summary_theme(
    role_type: str,
    tech_required: set[str],
    biz_domains: set[str],
    seniority: str,
) -> str:
    """确定 Professional Summary 应该传达的核心主题"""
    top_techs = list(tech_required)[:4]
    target = ROLE_LABELS.get(role_type, role_type)
    if top_techs:
        return f"{target} specialist with production experience in {', '.join(top_techs)}"
    return f"{target} specialist with cross-functional production experience"


def _identify_risks(
    exp_strategies: dict[str, ExperienceStrategy],
    project_strategies: list[ProjectStrategy],
    jd_profile: dict,
    catoms: list[dict],
) -> list[str]:
    """识别规划中的风险点"""
    risks: list[str] = []
    role_type = jd_profile.get('role_type', 'backend')

    # 风险1：Temu 项目 catom 为 0
    temu_proj = [
        c for c in catoms
        if c.get('parent_exp_id') == 'exp-temu' and c.get('is_project_bullet')
    ]
    if not temu_proj and any(ps.exp_id == 'exp-temu' for ps in project_strategies):
        risks.append("Temu has 0 project catoms — project must be Writer-generated")

    # 风险2：DiDi 项目 catom 极少
    didi_proj = [
        c for c in catoms
        if c.get('parent_exp_id') == 'exp-didi' and c.get('is_project_bullet')
    ]
    if len(didi_proj) < 4 and any(ps.exp_id == 'exp-didi' for ps in project_strategies):
        risks.append(f"DiDi has only {len(didi_proj)} project catoms — may need Writer supplement")

    # 风险3：niche 方向整体 catom 不足
    niche_roles = {'embedded', 'hpc_compiler', 'mobile', 'qa_sdet'}
    if role_type in niche_roles:
        matching = [c for c in catoms if role_type in c.get('angle_tags', [])]
        if len(matching) < 10:
            risks.append(
                f"Niche role '{role_type}' has only {len(matching)} matching catoms across all experiences"
            )

    # 风险4：Title-Responsibility mismatch for DiDi
    didi_strat = exp_strategies.get('exp-didi')
    if didi_strat and didi_strat.theme_focus not in ['data analytics', 'general']:
        risks.append(
            "DiDi title is 'Data Analyst' but theme suggests non-analytics work — may need HR context line"
        )

    return risks


# ═══════════════════════════════════════════════════════════
# 核心规划算法
# ═══════════════════════════════════════════════════════════

def plan_resume(jd_profile: dict, store: dict | None = None) -> ResumePlan:
    """根据 JD profile 和 catom 矩阵，规划最优的简历策略。

    算法步骤：
    1. 分析 JD 信号 → 确定核心需求
    2. 计算每段经历与 JD 的亲和度 → 决定排序和侧重
    3. 分配项目主题 → 2 个项目的公司+主题
    4. 分配技术预算 → 哪些技术放在哪段经历
    5. 检查矩阵覆盖 → 预判是否需要 Writer
    6. 生成叙事弧线
    """
    store = store or json.loads(CONSOLIDATED_STORE.read_text(encoding='utf-8'))
    catoms = store.get('catoms', [])

    role_type = jd_profile.get('role_type', 'backend')
    seniority = jd_profile.get('seniority', 'mid_1_3y')
    tech_required = set(t.lower() for t in jd_profile.get('tech_required', []))
    tech_expanded = set(t.lower() for t in jd_profile.get('tech_expanded', []))
    biz_domains = set(jd_profile.get('biz_domains', []))

    # ── Step 1: 计算每段经历的亲和度 ──
    exp_affinity: dict[str, dict] = {}
    for exp_id, meta in EXPERIENCE_META.items():
        if exp_id == 'academic':
            continue

        # 技术亲和度
        natural_lower = set(t.lower() for t in meta['natural_techs'])
        tech_score = len(natural_lower & tech_required) * 2 + len(natural_lower & tech_expanded)

        # 领域亲和度
        domain_score = len(set(meta['natural_domains']) & biz_domains)

        # 角色亲和度
        affinity_order = ROLE_EXP_AFFINITY.get(role_type, ['exp-bytedance', 'exp-didi', 'exp-temu'])
        role_score = (3 - affinity_order.index(exp_id)) if exp_id in affinity_order else 0

        exp_affinity[exp_id] = {
            'tech_score': tech_score,
            'domain_score': domain_score,
            'role_score': role_score,
            'total': tech_score * 3 + domain_score * 2 + role_score,
        }

    # 按亲和度排序
    sorted_exps = sorted(exp_affinity.keys(), key=lambda e: -exp_affinity[e]['total'])

    # ── Step 2: 分配项目 (恰好 2 个) ──
    project_strategies: list[ProjectStrategy] = []
    project_exp_count: dict[str, int] = defaultdict(int)

    for exp_id in sorted_exps:
        if len(project_strategies) >= 2:
            break
        meta = EXPERIENCE_META[exp_id]
        if project_exp_count[exp_id] >= meta['max_projects']:
            continue

        # 选择最匹配 JD 的主题
        themes = THEME_POOL.get(exp_id, [])
        existing_themes = [ps.theme for ps in project_strategies]
        best_theme = _select_best_theme(themes, existing_themes, role_type, biz_domains, tech_required)

        # 确定项目中的必需技术
        must_techs = _select_project_techs(exp_id, tech_required, tech_expanded, meta)

        min_b, max_b = (4, 6) if exp_id != 'academic' else (1, 2)
        project_strategies.append(ProjectStrategy(
            exp_id=exp_id,
            theme=best_theme,
            tech_must_include=must_techs[:4],
            tech_nice_to_have=list(tech_expanded - set(must_techs))[:3],
            bullet_count=(min_b, max_b),
            priority=len(project_strategies) + 1,
        ))
        project_exp_count[exp_id] += 1

    # 兜底：如果不够 2 个项目，ByteDance 再分一个
    if len(project_strategies) < 2:
        bt_meta = EXPERIENCE_META['exp-bytedance']
        if project_exp_count['exp-bytedance'] < bt_meta['max_projects']:
            themes = THEME_POOL.get('exp-bytedance', [])
            existing_themes = [ps.theme for ps in project_strategies]
            best_theme = _select_best_theme(themes, existing_themes, role_type, biz_domains, tech_required)
            project_strategies.append(ProjectStrategy(
                exp_id='exp-bytedance',
                theme=best_theme,
                tech_must_include=list(tech_required)[:4],
                tech_nice_to_have=[],
                bullet_count=(4, 6),
                priority=2,
            ))

    # ── Step 3: 构建 Experience Strategy ──
    pref_tags = ROLE_TO_ANGLE.get(role_type, ['backend'])

    exp_strategies: dict[str, ExperienceStrategy] = {}
    for exp_id in ['exp-bytedance', 'exp-didi', 'exp-temu']:
        meta = EXPERIENCE_META[exp_id]
        proj_count = sum(1 for ps in project_strategies if ps.exp_id == exp_id)

        # 计算 general bullet 数
        proj_bullet_budget = proj_count * 5  # 平均每项目 5 bullets
        general_count = min(meta['general_max'], meta['budget_total'] - proj_bullet_budget)
        general_count = max(0, general_count)

        # 确定叙事角色
        rank = sorted_exps.index(exp_id) if exp_id in sorted_exps else 2
        if rank == 0:
            narrative_role = "specialization"  # 最相关 → 专业化展示
        elif rank == 1:
            narrative_role = "growth"           # 次相关 → 成长经历
        else:
            narrative_role = "foundation"       # 最不相关 → 基础能力

        # 技术侧重
        natural_lower = set(t.lower() for t in meta['natural_techs'])
        tech_emph = list(natural_lower & tech_expanded)[:5]
        tech_deemph = list(natural_lower - tech_expanded)[:3]

        # 主题侧重
        theme_focus = "general"
        for ps in project_strategies:
            if ps.exp_id == exp_id:
                theme_focus = ps.theme
                break

        exp_strategies[exp_id] = ExperienceStrategy(
            exp_id=exp_id,
            narrative_role=narrative_role,
            theme_focus=theme_focus,
            tech_emphasis=tech_emph,
            tech_deemphasis=tech_deemph,
            seniority_level=meta['seniority_key'],
            project_count=proj_count,
            general_bullet_count=general_count,
            catom_preference_tags=pref_tags,
        )

    # Academic strategy
    exp_strategies['academic'] = ExperienceStrategy(
        exp_id='academic',
        narrative_role='academic',
        theme_focus=_select_best_theme(
            THEME_POOL.get('academic', []), [], role_type, biz_domains, tech_required,
        ),
        tech_emphasis=list(tech_required)[:3],
        tech_deemphasis=[],
        seniority_level='academic',
        project_count=1,
        general_bullet_count=0,
        catom_preference_tags=pref_tags,
    )

    # ── Step 4: 技术预算 ──
    tech_budget = {
        'must_appear': list(tech_required),
        'nice_to_have': list(tech_expanded - tech_required)[:10],
        'avoid': [],  # 与 JD 完全无关的技术
    }

    # ── Step 5: 矩阵覆盖检查 → 预判 Writer 需求 ──
    writer_needed, writer_reason = _check_coverage(catoms, jd_profile, project_strategies)

    # ── Step 6: 叙事弧线 ──
    narrative_arc = _build_narrative_arc(sorted_exps, exp_strategies, role_type, seniority)

    # ── Step 7: Summary 主题 ──
    summary_theme = _build_summary_theme(role_type, tech_required, biz_domains, seniority)

    # ── Step 8: 风险识别 ──
    risk_notes = _identify_risks(exp_strategies, project_strategies, jd_profile, catoms)

    return ResumePlan(
        jd_role_type=role_type,
        jd_seniority=seniority,
        narrative_arc=narrative_arc,
        experience_strategies=exp_strategies,
        project_strategies=project_strategies,
        tech_budget=tech_budget,
        summary_theme=summary_theme,
        risk_notes=risk_notes,
        writer_needed=writer_needed,
        writer_reason=writer_reason,
    )


# ═══════════════════════════════════════════════════════════
# CLI 入口
# ═══════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(description="Resume Planner — 全局简历策略规划")
    parser.add_argument("--jd", type=str, help="JD 文件路径")
    parser.add_argument("--jd-text", type=str, help="JD 文本")
    parser.add_argument("--output", type=str, help="输出规划 JSON 的路径")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    args = parser.parse_args()

    if not args.jd and not args.jd_text:
        parser.error("Must provide --jd or --jd-text")

    jd_text: str = args.jd_text or Path(args.jd).read_text(encoding='utf-8')

    # 导入 parse_jd / expand_tech_if_sparse
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from generate_resume import expand_tech_if_sparse, parse_jd

    jd_profile = expand_tech_if_sparse(parse_jd(jd_text))
    plan = plan_resume(jd_profile)

    print(plan.to_text())

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(plan.to_dict(), indent=2, ensure_ascii=False),
            encoding='utf-8',
        )
        print(f"\nPlan saved to: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
