"""
Pipeline Orchestrator — 简化的 5 步流程编排。

原赛马机制（3 Writer × 9 Reviewer × 3 迭代）→ 新单路线机制：
  步骤1: 解析 JD → JDProfile
  步骤2: Master Writer 生成简历（PLAN→WRITE，强制 SKILLS 一致性）
  步骤3: Unified Reviewer 进行 9 维度审查（单次 LLM 调用）
  步骤4: 若评分 < 93，执行一次精准修改（可选）
  步骤5: 保存输出并返回结果

LLM 调用次数：2-3 次（原系统：9-15 次）
"""
import json
import logging
import os
from datetime import datetime
from typing import Dict, Optional

from models.resume import Resume
from models.jd import JDProfile
from pipeline.revision_acceptance import should_adopt_revision
from writers.master_writer import MasterWriter
from reviewers.unified_reviewer import UnifiedReviewer, ReviewSummary
from core.anthropic_client import configure_llm_client, LLMUnavailableError
from core.prompt_builder import build_upgrade_revision_prompt
from config.frozen_constraints import verify_constraints_integrity
from security.audit_logger import AuditLogger

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


class PipelineOrchestrator:
    """简化版 Pipeline 编排器（单路线 + 最多2次修改）"""

    PASS_THRESHOLD = 93.0   # 综合分 >= 93 视为通过

    def __init__(
        self,
        output_dir: str = "output",
        enable_llm: bool = False,
        write_model: str = "gpt-5.4",
        review_model: str = "gpt-5.4-mini",
        llm_transport: str = "auto",
    ):
        configure_llm_client(
            enabled=enable_llm,
            write_model=write_model,
            review_model=review_model,
            transport=llm_transport,
        )
        self.writer = MasterWriter()
        self.reviewer = UnifiedReviewer()
        self.output_dir = output_dir
        self.audit = AuditLogger(output_dir)
        os.makedirs(output_dir, exist_ok=True)

    def run(
        self,
        jd_text: str,
        jd_id: str = "",
        company: str = "",
    ) -> Dict:
        """
        运行完整 pipeline。

        Returns:
            {
              "resume_markdown": str,        # 最终简历 Markdown
              "resume": Resume,              # 解析后的 Resume 对象
              "review": ReviewSummary,       # 审查结果
              "plan_text": str,              # PLAN 阶段内容（调试用）
              "revised": bool,               # 是否经过修改
              "final_score": float,          # 最终综合分
              "verdict": str,                # pass / pending / reject
              "output_path": str,            # 保存路径
            }
        """
        # ── 安全检查 ──
        verify_constraints_integrity()

        # ── 步骤1: 解析 JD ──
        print(f"\n{'='*60}")
        print(f"🎯 目标: {company or 'Unknown'} — {jd_id or 'JD'}")
        print(f"{'='*60}")
        print("\n📋 步骤1: 解析 JD...")
        jd = JDProfile.from_text(jd_text, jd_id=jd_id, company=company)
        print(f"   角色: {jd.title} | 类型: {jd.role_type} | 职级: {jd.seniority}")
        print(f"   必须技术: {', '.join(jd.tech_required[:8]) or '（无）'}")
        self.audit.log("jd_parsed", {
            "jd_id": jd_id, "company": company,
            "role_type": jd.role_type, "seniority": jd.seniority,
            "tech_required": jd.tech_required,
        })

        # ── 步骤2: Master Writer 生成 ──
        print("\n✍️  步骤2: Master Writer 生成简历（PLAN → WRITE）...")
        try:
            resume_md, plan_text = self.writer.write(jd)
        except LLMUnavailableError as e:
            print(f"   ⚠️  LLM 不可用: {e}")
            print("   请设置 ANTHROPIC_API_KEY 并传入 --enable-llm")
            return self._unavailable_result(jd_id, str(e))

        resume = Resume.from_markdown(
            resume_md,
            target_jd_id=jd.jd_id,
            target_company=jd.company,
            target_role=jd.title,
            target_seniority=jd.seniority,
        )
        print(f"   ✓ 简历生成完成 ({len(resume_md)} 字符, "
              f"{len(resume.experiences)} 段经历, "
              f"{len(resume.get_all_projects())} 个项目)")
        self.audit.log("resume_generated", {"length": len(resume_md)})

        # ── 步骤3: Unified Reviewer 审查 ──
        print("\n🔍 步骤3: 9 维度统一审查...")
        review = self.reviewer.review(resume_md, jd)
        print(f"   {review.format_report()}")
        self.audit.log("review_complete", review.to_dict())

        # ── 步骤4: 若评分 < 93，最多执行两轮精准修改 ──
        # 第一轮：任何 < 93 分触发
        # 第二轮：第一轮后仍在 88-92 分区间时触发（进一步逼近目标线）
        revised = False
        revision_round = 0
        MAX_REVISIONS = 2

        while not review.passed and review.needs_revision and revision_round < MAX_REVISIONS:
            revision_round += 1
            score_before = review.weighted_score
            in_striking_distance = 88.0 <= score_before < self.PASS_THRESHOLD

            # 第二轮仅在 88-92 分区间触发（否则分数太低，单次修改杯水车薪）
            if revision_round == 2 and not in_striking_distance:
                print(f"\n   ℹ️  评分 {score_before:.1f} 不在 88-92 区间，跳过第二轮修改")
                break

            print(f"\n🔧 步骤4（第{revision_round}轮）: 评分 {score_before:.1f} < {self.PASS_THRESHOLD}，执行精准修改...")
            try:
                rewrite_review = self.reviewer.review(resume_md, jd, mode="rewrite")
                revision_prompt = build_upgrade_revision_prompt(
                    resume_md=resume_md,
                    review_result=rewrite_review.__dict__ | {
                        "scores": {k: vars(v) for k, v in rewrite_review.dimensions.items()},
                        "weighted_score": rewrite_review.weighted_score,
                        "revision_instructions": rewrite_review.revision_instructions,
                        "revision_priority": rewrite_review.revision_priority,
                    },
                    tech_required=jd.tech_required,
                    jd_title=jd.title,
                    target_company=jd.company,
                    plan_text=plan_text,
                )
                revised_md = self.writer.revise(
                    resume_md,
                    revision_prompt,
                    jd,
                    rewrite_mode="upgrade",
                )

                # 修改后重新审查
                print("   重新审查修改后简历...")
                revised_review = self.reviewer.review(revised_md, jd)
                print(f"   修改后评分: {revised_review.weighted_score:.1f}")

                critical_before = review.critical_count
                high_before = review.high_count
                adopted = should_adopt_revision(
                    score_before=score_before,
                    critical_before=critical_before,
                    high_before=high_before,
                    score_after=revised_review.weighted_score,
                    critical_after=revised_review.critical_count,
                    high_after=revised_review.high_count,
                    passed_after=revised_review.passed,
                )

                if adopted:
                    # 仅在评分变好，或严重级别问题变少且分数几乎不回退时采纳修改。
                    resume_md = revised_md
                    resume = Resume.from_markdown(
                        resume_md,
                        target_jd_id=jd.jd_id,
                        target_company=jd.company,
                        target_role=jd.title,
                        target_seniority=jd.seniority,
                    )
                    review = revised_review
                    revised = True
                    print(f"   ✓ 第{revision_round}轮修改已采纳，当前评分: {review.weighted_score:.1f}")
                else:
                    print(
                        f"   ⚠️  修改未带来净改善（{revised_review.weighted_score:.1f} vs {score_before:.1f}，"
                        f"critical {critical_before}->{revised_review.critical_count}，"
                        f"high {high_before}->{revised_review.high_count}），保留上一版本"
                    )

                self.audit.log(f"revision_{revision_round}_complete", {
                    "adopted": adopted,
                    "score_before": score_before,
                    "score_after": revised_review.weighted_score,
                    "critical_before": critical_before,
                    "critical_after": revised_review.critical_count,
                    "high_before": high_before,
                    "high_after": revised_review.high_count,
                })

                if not adopted:
                    break

            except LLMUnavailableError as e:
                print(f"   ⚠️  修改时 LLM 不可用: {e}，保留原版本")
                break

        # ── 步骤5: 保存输出 ──
        final_score = review.weighted_score
        verdict = "pass" if review.passed else "pending"

        output_path = self._save_output(
            resume_md=resume_md,
            review=review,
            plan_text=plan_text,
            jd=jd,
            verdict=verdict,
            revised=revised,
        )

        print(f"\n{'='*60}")
        print(f"最终结果: {verdict.upper()} | 评分: {final_score:.1f}/100")
        print(f"{'修改版' if revised else '原版'} | 输出: {output_path}")
        print(f"{'='*60}\n")

        return {
            "resume_markdown": resume_md,
            "resume": resume,
            "review": review,
            "plan_text": plan_text,
            "revised": revised,
            "final_score": final_score,
            "verdict": verdict,
            "output_path": output_path,
        }

    def _save_output(
        self,
        resume_md: str,
        review: ReviewSummary,
        plan_text: str,
        jd: JDProfile,
        verdict: str,
        revised: bool,
    ) -> str:
        """保存简历和审查结果到输出目录"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = f"{jd.jd_id or 'unknown'}_{timestamp}"

        # 主简历文件
        md_path = os.path.join(self.output_dir, f"{prefix}_resume.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(resume_md)

        # 审查详情 JSON
        review_path = os.path.join(self.output_dir, f"{prefix}_review.json")
        review_data = {
            "jd_id": jd.jd_id,
            "company": jd.company,
            "title": jd.title,
            "role_type": jd.role_type,
            "verdict": verdict,
            "final_score": round(review.weighted_score, 1),
            "revised": revised,
            **review.to_dict(),
        }
        with open(review_path, "w", encoding="utf-8") as f:
            json.dump(review_data, f, indent=2, ensure_ascii=False)

        # PLAN 文本（调试用）
        if plan_text:
            plan_path = os.path.join(self.output_dir, f"{prefix}_plan.txt")
            with open(plan_path, "w", encoding="utf-8") as f:
                f.write(plan_text)

        return md_path

    @staticmethod
    def _unavailable_result(jd_id: str, error: str) -> Dict:
        """LLM 不可用时返回的占位结果"""
        return {
            "resume_markdown": "",
            "resume": None,
            "review": None,
            "plan_text": "",
            "revised": False,
            "final_score": 0.0,
            "verdict": "error",
            "output_path": "",
            "error": error,
        }
