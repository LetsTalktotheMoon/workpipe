"""
审查结果数据模型 - Reviewer和Writer之间的通信协议。
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum


class Severity(Enum):
    """审查问题严重程度"""
    CRITICAL = "critical"       # 必须修复，否则不通过
    HIGH = "high"               # 应当修复
    MEDIUM = "medium"           # 建议修复
    LOW = "low"                 # 可选改进


class ReviewVerdict(Enum):
    """审查裁决"""
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL_PASS = "conditional_pass"   # 有条件通过（熔断时使用）


@dataclass
class ReviewFinding:
    """单条审查发现"""
    reviewer_id: str             # 哪个审查官发现的 (r0-r6)
    rule_id: str                 # 规则编号
    severity: Severity
    field: str                   # 涉及的简历字段/位置
    message: str                 # 问题描述
    suggestion: str = ""         # 修改建议
    target_writer: str = ""      # 应由哪个Writer角色处理 (w0-w6)
    requires_collaboration: List[str] = field(default_factory=list)  # 需要与哪些角色协作


@dataclass
class ReviewResult:
    """单个审查官的审查结果"""
    reviewer_id: str
    reviewer_name: str
    priority: int                # 优先级（0最高）
    verdict: ReviewVerdict = ReviewVerdict.PASS
    findings: List[ReviewFinding] = field(default_factory=list)
    score: float = 100.0         # 0-100
    notes: str = ""

    @property
    def has_critical(self) -> bool:
        return any(f.severity == Severity.CRITICAL for f in self.findings)

    @property
    def fail_count(self) -> int:
        return len([f for f in self.findings if f.severity in (Severity.CRITICAL, Severity.HIGH)])


@dataclass
class SecretaryReport:
    """总审查官秘书汇总报告"""
    all_results: List[ReviewResult] = field(default_factory=list)
    conflicts: List[Dict] = field(default_factory=list)
    consolidated_findings: List[ReviewFinding] = field(default_factory=list)
    final_recommendation: ReviewVerdict = ReviewVerdict.FAIL
    notes: str = ""


@dataclass
class ChiefDecision:
    """总审查官最终裁决"""
    verdict: ReviewVerdict = ReviewVerdict.FAIL
    approved_findings: List[ReviewFinding] = field(default_factory=list)
    overruled_findings: List[ReviewFinding] = field(default_factory=list)
    notes: str = ""
    iteration: int = 0


@dataclass
class WriterRevisionRequest:
    """Writer收到的修改请求 - 审查官→Writer的通信"""
    target_writer: str           # w0-w6
    from_reviewer: str           # r0-r6
    findings: List[ReviewFinding] = field(default_factory=list)
    priority: int = 0            # 来自审查官的优先级
    iteration: int = 0           # 第几轮修改


@dataclass
class WriterQuery:
    """Writer向审查官的查询 - Writer→审查官的通信"""
    from_writer: str             # w0-w6
    to_reviewer: str             # r0-r6
    question: str = ""           # 具体问题
    context: str = ""            # 上下文
    options: List[str] = field(default_factory=list)  # 候选方案


@dataclass
class ReviewerResponse:
    """审查官对Writer查询的回复"""
    from_reviewer: str
    to_writer: str
    answer: str = ""
    preferred_option: int = -1   # 推荐的候选方案编号
    constraints: List[str] = field(default_factory=list)  # 额外约束
