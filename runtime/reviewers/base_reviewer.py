"""
审查官基类 - 所有R0-R6审查官继承此类。
定义统一的审查接口和通信协议。
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.resume import Resume
from models.jd import JDProfile
from models.review import (
    ReviewResult, ReviewFinding, ReviewVerdict,
    Severity, WriterQuery, ReviewerResponse,
)
from config.frozen_constraints import FROZEN_CONSTRAINTS, verify_constraints_integrity


class BaseReviewer(ABC):
    """审查官基类"""

    def __init__(self):
        self.reviewer_id: str = ""
        self.reviewer_name: str = ""
        self.priority: int = 99         # 数字越小优先级越高
        self.corresponding_writer: str = ""  # 对应的Writer角色

    @abstractmethod
    def review(self, resume: Resume, jd: JDProfile) -> ReviewResult:
        """
        执行审查，返回审查结果。
        每个子类实现自己的审查逻辑。
        """
        pass

    def respond_to_writer(self, query: WriterQuery) -> ReviewerResponse:
        """
        回复Writer的查询（默认实现，子类可覆盖）。
        这是Writer→Reviewer的通信接口。
        """
        return ReviewerResponse(
            from_reviewer=self.reviewer_id,
            to_writer=query.from_writer,
            answer=f"[{self.reviewer_name}] 默认回复：请遵循审查规则。",
        )

    def _make_finding(
        self,
        rule_id: str,
        severity: Severity,
        field: str,
        message: str,
        suggestion: str = "",
        collaboration: Optional[List[str]] = None,
    ) -> ReviewFinding:
        """创建一条审查发现"""
        return ReviewFinding(
            reviewer_id=self.reviewer_id,
            rule_id=rule_id,
            severity=severity,
            field=field,
            message=message,
            suggestion=suggestion,
            target_writer=self.corresponding_writer,
            requires_collaboration=collaboration or [],
        )

    def _make_result(
        self,
        findings: List[ReviewFinding],
        notes: str = "",
    ) -> ReviewResult:
        """构造审查结果"""
        # 确认约束完整性
        verify_constraints_integrity()

        has_critical = any(f.severity == Severity.CRITICAL for f in findings)
        has_high = any(f.severity == Severity.HIGH for f in findings)

        if has_critical:
            verdict = ReviewVerdict.FAIL
        elif has_high:
            verdict = ReviewVerdict.FAIL
        else:
            verdict = ReviewVerdict.PASS

        # 评分：100分起扣
        score = 100.0
        for f in findings:
            if f.severity == Severity.CRITICAL:
                score -= 25
            elif f.severity == Severity.HIGH:
                score -= 15
            elif f.severity == Severity.MEDIUM:
                score -= 5
            elif f.severity == Severity.LOW:
                score -= 2
        score = max(0, score)

        return ReviewResult(
            reviewer_id=self.reviewer_id,
            reviewer_name=self.reviewer_name,
            priority=self.priority,
            verdict=verdict,
            findings=findings,
            score=score,
            notes=notes,
        )
