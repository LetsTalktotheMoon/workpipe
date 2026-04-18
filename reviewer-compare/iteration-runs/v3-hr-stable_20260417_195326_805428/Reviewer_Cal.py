"""
Reviewer v4.0 配套聚合代码
职责：
1. 接收 reviewer LLM 的原始 JSON 输出
2. 将 findings 按维度归口
3. 基于 severity 计算每个维度分
4. 加权计算综合分
5. 判定 revision 需求和 overall verdict
6. 返回聚合结果

设计原则：
- 所有评分计算在外部代码完成，reviewer LLM 不参与数学
- 严格规则驱动，消除跨模型分差
"""

from dataclasses import dataclass, field
from typing import Literal, TypedDict

# ============================================================
# 常量配置
# ============================================================

WEIGHTS = {
    "r0_authenticity":       0.18,
    "r1_writing_standard":   0.10,
    "r2_jd_fitness":         0.28,
    "r3_overqualification":  0.06,
    "r4_rationality":        0.20,
    "r5_logic":              0.06,
    "r7_ecosystem":          0.07,
    "r8_localization":       0.05,
}

# 权重合计校验
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-6, "WEIGHTS must sum to 1.0"

SEVERITY_PENALTY = {
    "critical": 4.0,
    "high":     2.0,
    "medium":   0.8,
    "low":      0.3,
}

RULE_PENALTY_MULTIPLIER = {
    "P1-040": 0.60,
    "P1-042": 0.60,
    "P1-051": 0.60,
    "P2-010": 0.75,
    "P2-020": 0.75,
    "P2-030": 0.80,
    "P2-040": 0.85,
    "P3B-003": 0.80,
    "P3D-001": 0.60,
    "P3E-013": 0.70,
}

STRUCTURAL_FAIL_RULE_IDS = {
    "P3B-001",
    "P3B-010",
    "P3B-011",
}

# Pass 1 规则 ID 归口映射
# R0 = 不可变字段 + Experience 结构
P1_RULES_R0 = (
    "P1-001",  # 中文字符
    "P1-002",  # 不可变字段
    "P1-003",  # TikTok 职称
    "P1-010",  # Experience 倒序
    "P1-012",  # 项目数量
)

# Pass 2 规则 ID 归口映射
# R4 = 首屏信号（Summary framing + 围棋句 + 第一 bullet + Skills 首行）
P2_RULES_R4 = (
    "P2-001",  # Summary 第一句 framing
    "P2-010",  # 围棋句 header
    "P2-020",  # 第一条 bullet 信号强度
    "P2-030",  # Skills 第一行对齐
)

# R5 = Skills 类别命名
P2_RULES_R5 = (
    "P2-040",  # 类别命名
)

REVISION_THRESHOLD = 90.5  # 综合分 < 90.5 触发 revision
FAIL_THRESHOLD = 88.0      # 综合分 < 88 判定 fail
HIGH_COUNT_REVISION = 2    # high findings >= 2 触发 revision

# ============================================================
# 类型定义
# ============================================================

Severity = Literal["critical", "high", "medium", "low"]


class Finding(TypedDict, total=False):
    rule_id: str
    severity: Severity
    field: str
    issue: str
    fix: str
    sub_area: str  # 仅 Pass 3 有
    note: str      # 可选


class TranslationRecommendation(TypedDict):
    original_stack: str
    current_in_resume: str
    location: str
    recommended_translation: str
    reason: str
    confidence: Literal["high", "medium", "low"]


class ReviewerRawOutput(TypedDict):
    pass_1_structural: dict
    pass_2_attention: dict
    pass_3_substance: dict
    pass_5_localization: dict
    translation_recommendations: list[TranslationRecommendation]
    revision_priority: list[str]
    revision_instructions: str


@dataclass
class AggregatedResult:
    scores: dict[str, float]
    weighted_score: float
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    needs_revision: bool
    overall_verdict: Literal["pass", "fail"]
    translation_recommendations: list[TranslationRecommendation]
    revision_priority: list[str]
    revision_instructions: str
    reviewer_raw: ReviewerRawOutput
    per_dimension_findings: dict[str, list[Finding]] = field(default_factory=dict)


# ============================================================
# 核心评分函数
# ============================================================

def score_dimension(findings: list[Finding]) -> float:
    """
    基于 findings 计算单个维度分数
    
    规则：
    - 起点 10 分
    - 基础扣分：critical -4, high -2, medium -0.8, low -0.3
    - calibration-sensitive 规则可按 multiplier 降权
    - 同一 rule_id 在同一维度重复出现时，第二条按 50%，第三条起按 25% 计
    - 若存在任一 critical, 该维度分 ≤ 6
    - 若存在任一 high, 该维度分 ≤ 8.5
    - 四舍五入到 0.5
    - 下限 0
    """
    score = 10.0
    has_critical = False
    has_high = False
    seen_rule_counts: dict[str, int] = {}
    
    for f in findings:
        sev = f.get("severity")
        if sev not in SEVERITY_PENALTY:
            continue
        rule_id = str(f.get("rule_id", "") or "")
        seen_rule_counts[rule_id] = seen_rule_counts.get(rule_id, 0) + 1
        duplicate_index = seen_rule_counts[rule_id]
        duplicate_multiplier = 1.0 if duplicate_index == 1 else 0.5 if duplicate_index == 2 else 0.25
        rule_multiplier = RULE_PENALTY_MULTIPLIER.get(rule_id, 1.0)
        score -= SEVERITY_PENALTY[sev] * rule_multiplier * duplicate_multiplier
        if sev == "critical":
            has_critical = True
        elif sev == "high":
            has_high = True
    
    if has_critical:
        score = min(score, 6.0)
    elif has_high:
        score = min(score, 8.5)
    
    score = max(0.0, score)
    # 四舍五入到 0.5
    return round(score * 2) / 2


def split_p1_findings(p1_findings: list[Finding]) -> tuple[list[Finding], list[Finding]]:
    """
    将 Pass 1 findings 拆分为 R0（不可变字段+结构）和 R1（格式）
    """
    r0_findings = [f for f in p1_findings 
                   if f.get("rule_id", "").startswith(P1_RULES_R0)]
    r1_findings = [f for f in p1_findings 
                   if not f.get("rule_id", "").startswith(P1_RULES_R0)]
    return r0_findings, r1_findings


def split_p2_findings(p2_findings: list[Finding]) -> tuple[list[Finding], list[Finding]]:
    """
    将 Pass 2 findings 拆分为 R4（首屏）和 R5（Skills 命名）
    """
    r4_findings = [f for f in p2_findings 
                   if f.get("rule_id", "").startswith(P2_RULES_R4)]
    r5_findings = [f for f in p2_findings 
                   if f.get("rule_id", "").startswith(P2_RULES_R5)]
    return r4_findings, r5_findings


def split_p3_findings(p3_findings: list[Finding]) -> dict[str, list[Finding]]:
    """
    将 Pass 3 findings 按 sub_area 分组
    """
    buckets: dict[str, list[Finding]] = {"3A": [], "3B": [], "3C": [], "3D": [], "3E": []}
    for f in p3_findings:
        sub = f.get("sub_area", "")
        if sub in buckets:
            buckets[sub].append(f)
    return buckets


def has_structural_fail(findings: list[Finding]) -> bool:
    for finding in findings:
        if finding.get("rule_id") in STRUCTURAL_FAIL_RULE_IDS and finding.get("severity") in {"high", "critical"}:
            return True
    return False


# ============================================================
# 主聚合函数
# ============================================================

def aggregate(reviewer_output: ReviewerRawOutput) -> AggregatedResult:
    """
    将 reviewer LLM 的原始输出聚合为最终评分结果
    """
    # ---- Step 1: 提取各 Pass findings ----
    p1 = reviewer_output["pass_1_structural"].get("findings", [])
    p2 = reviewer_output["pass_2_attention"].get("findings", [])
    p3 = reviewer_output["pass_3_substance"].get("findings", [])
    p5 = reviewer_output["pass_5_localization"].get("findings", [])
    
    # ---- Step 2: 拆分归口 ----
    p1_r0, p1_r1 = split_p1_findings(p1)
    p2_r4, p2_r5 = split_p2_findings(p2)
    p3_by_sub = split_p3_findings(p3)
    
    # ---- Step 3: 组装每维度 findings ----
    per_dim: dict[str, list[Finding]] = {
        "r0_authenticity":      p1_r0 + p3_by_sub["3A"],
        "r1_writing_standard":  p1_r1,
        "r2_jd_fitness":        p3_by_sub["3B"],
        "r3_overqualification": p3_by_sub["3C"],
        "r4_rationality":       p2_r4 + p3_by_sub["3D"],
        "r5_logic":             p2_r5,
        "r7_ecosystem":         p3_by_sub["3E"],
        "r8_localization":      p5,
    }
    
    # ---- Step 4: 计算维度分 ----
    scores = {dim: score_dimension(findings) for dim, findings in per_dim.items()}
    
    # ---- Step 5: 计算综合分 ----
    weighted_raw = sum(scores[dim] * WEIGHTS[dim] for dim in WEIGHTS)
    weighted_score = round(weighted_raw * 10, 1)
    
    # ---- Step 6: 统计 severity ----
    all_findings = p1 + p2 + p3 + p5
    severity_counts = {
        "critical": sum(1 for f in all_findings if f.get("severity") == "critical"),
        "high":     sum(1 for f in all_findings if f.get("severity") == "high"),
        "medium":   sum(1 for f in all_findings if f.get("severity") == "medium"),
        "low":      sum(1 for f in all_findings if f.get("severity") == "low"),
    }
    structural_fail = has_structural_fail(p3_by_sub["3B"])
    
    # ---- Step 7: 判定 revision 需求 ----
    needs_revision = (
        weighted_score < REVISION_THRESHOLD
        or severity_counts["critical"] > 0
        or severity_counts["high"] >= HIGH_COUNT_REVISION
        or structural_fail
    )
    
    # ---- Step 8: 判定 overall verdict ----
    if severity_counts["critical"] > 0 or weighted_score < FAIL_THRESHOLD or structural_fail:
        overall_verdict = "fail"
    else:
        overall_verdict = "pass"
    
    # ---- Step 9: 组装返回结果 ----
    return AggregatedResult(
        scores=scores,
        weighted_score=weighted_score,
        critical_count=severity_counts["critical"],
        high_count=severity_counts["high"],
        medium_count=severity_counts["medium"],
        low_count=severity_counts["low"],
        needs_revision=needs_revision,
        overall_verdict=overall_verdict,
        translation_recommendations=reviewer_output.get("translation_recommendations", []),
        revision_priority=reviewer_output.get("revision_priority", []),
        revision_instructions=reviewer_output.get("revision_instructions", ""),
        reviewer_raw=reviewer_output,
        per_dimension_findings=per_dim,
    )


# ============================================================
# 结果展示辅助函数
# ============================================================

def format_report(result: AggregatedResult) -> str:
    """
    将聚合结果格式化为人类可读报告
    """
    lines = []
    lines.append("=" * 60)
    lines.append(f"综合分: {result.weighted_score}  |  判定: {result.overall_verdict.upper()}")
    lines.append(f"需要修改: {'是' if result.needs_revision else '否'}")
    lines.append("=" * 60)
    
    lines.append("\n【维度分】")
    dim_names_cn = {
        "r0_authenticity":      "R0 真实性",
        "r1_writing_standard":  "R1 撰写规范",
        "r2_jd_fitness":        "R2 JD 适配",
        "r3_overqualification": "R3 炫技",
        "r4_rationality":       "R4 合理性",
        "r5_logic":             "R5 逻辑",
        "r7_ecosystem":         "R7 生态一致性",
        "r8_localization":      "R8 本土化翻译",
    }
    for dim in WEIGHTS:
        score = result.scores[dim]
        weight = WEIGHTS[dim]
        name = dim_names_cn[dim]
        contrib = round(score * weight * 10, 2)
        lines.append(f"  {name:20s} {score:4.1f} (权重 {weight:.2f} → +{contrib:.2f})")
    
    lines.append(f"\n【Severity 统计】")
    lines.append(f"  critical: {result.critical_count}")
    lines.append(f"  high:     {result.high_count}")
    lines.append(f"  medium:   {result.medium_count}")
    lines.append(f"  low:      {result.low_count}")
    
    if result.revision_priority:
        lines.append(f"\n【Revision Priority】")
        for item in result.revision_priority:
            lines.append(f"  - {item}")
    
    if result.translation_recommendations:
        lines.append(f"\n【翻译建议】({len(result.translation_recommendations)} 条)")
        for rec in result.translation_recommendations[:3]:  # 只展示前 3 条
            lines.append(f"  {rec['original_stack']} → {rec['recommended_translation']} "
                        f"(confidence: {rec['confidence']})")
    
    if result.revision_instructions:
        lines.append(f"\n【Revision Instructions】")
        lines.append(result.revision_instructions)
    
    return "\n".join(lines)


# ============================================================
# 使用示例
# ============================================================

if __name__ == "__main__":
    # 模拟一份 reviewer 输出
    sample_output: ReviewerRawOutput = {
        "pass_1_structural": {
            "findings": [
                {"rule_id": "P1-011", "severity": "medium", 
                 "field": "Temu Experience", "issue": "bullet 数 3 少于 4", 
                 "fix": "补一条 bullet"},
                {"rule_id": "P1-042", "severity": "medium",
                 "field": "TikTok Experience bullet 2",
                 "issue": "'**internal**' 被加粗，属修饰词",
                 "fix": "去除加粗"},
            ]
        },
        "pass_2_attention": {
            "findings": [
                {"rule_id": "P2-001", "severity": "high",
                 "field": "Summary 第一句",
                 "issue": "header '**Transitioning engineer:**' 命中低信号 framing",
                 "fix": "改为 '**Backend engineer:**' 等含领域信号的 header"},
            ]
        },
        "pass_3_substance": {
            "findings": [
                {"rule_id": "P3B-001", "sub_area": "3B", "severity": "high",
                 "field": "Skills",
                 "issue": "JD must-have 'Kubernetes' 未在 Skills 出现",
                 "fix": "在 Cloud/Infra 类别补 Kubernetes"},
                {"rule_id": "P3D-001", "sub_area": "3D", "severity": "medium",
                 "field": "整体",
                 "issue": "Tier S/A 信号少于 3 条",
                 "fix": "在 DiDi 或 TikTok bullet 补规模或技术深度信号"},
            ]
        },
        "pass_5_localization": {
            "findings": [
                {"rule_id": "P8-001", "severity": "high",
                 "field": "Temu Skills 第 2 行",
                 "issue": "直接写 MaxCompute 未翻译",
                 "fix": "翻译为 BigQuery 或 Snowflake，见 translation_recommendations"},
            ]
        },
        "translation_recommendations": [
            {"original_stack": "MaxCompute", "current_in_resume": "未翻译",
             "location": "Temu Skills 第 2 行",
             "recommended_translation": "BigQuery",
             "reason": "JD 要求 BigQuery，MaxCompute 属一级对等翻译",
             "confidence": "high"}
        ],
        "revision_priority": [
            "[MUST] Summary 第一句 framing 改为含领域信号的 header",
            "[MUST] Skills 补 Kubernetes 并在 TikTok 正文补使用证据",
            "[MUST] Temu Skills 将 MaxCompute 翻译为 BigQuery",
            "[SHOULD] 全文补 2-3 条 Tier S/A 规模或技术深度信号"
        ],
        "revision_instructions": (
            "1. Summary 第一句 header 从 '**Transitioning engineer:**' 改为 "
            "'**Backend engineer with data-intensive systems experience:**'。"
            "2. Skills 'Cloud/Infra' 类别新增 Kubernetes；在 TikTok Experience "
            "第 3 条 bullet 补充 '... deploying services to K8s clusters across 3 regions'。"
            "3. Temu Skills 第 2 行将 MaxCompute 替换为 BigQuery；相关 bullet 可加 "
            "'BigQuery-equivalent columnar warehouse' 作为桥接语言。"
            "4. 在 DiDi 至少 1 条 bullet 补入规模信号（如 daily order volume）。"
        )
    }
    
    result = aggregate(sample_output)
    print(format_report(result))
