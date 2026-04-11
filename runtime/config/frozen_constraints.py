"""
不可变审查约束 - 所有阈值写入代码常量，非配置文件。
任何修改必须经CEO确认。违反铁律1。

历史教训：
- Flash曾将C04上限从6改为7
- Pro曾将C04上限从6改为8
- 某员工曾将max_bullets_per_exp从6改为10
"""
import hashlib
import json

# ============================================================
# 锁死的审查阈值 - 禁止修改
# ============================================================
FROZEN_CONSTRAINTS = {
    # C02: Summary必须恰好3句话
    "summary_sentences": {"exact": 3},

    # C03: 必须恰好2个项目（至少1个来自工作经历）
    "project_count": {"exact": 2, "min_work_project": 1},

    # C04: 每个工作项目4-6条要点
    "work_project_bullets": {"min": 4, "max": 6},

    # C04b: 每个学术项目1-2条要点
    "academic_project_bullets": {"min": 1, "max": 2},

    # C06: 工作经历总要点12-22条
    "total_work_bullets": {"min": 12, "max": 22},

    # 每段工作经历4-6条要点
    "bullets_per_experience": {"min": 4, "max": 6},

    # 每条要点中1-2条包含具体数据
    "data_bullets_per_experience": {"min": 1, "max": 2},

    # C10: Skills中>=90%技术栈来自JD
    "skills_jd_match_ratio": {"min": 0.90},

    # C13: >=80%要点以强动词开头
    "strong_verb_ratio": {"min": 0.80},

    # 禁止词汇
    "forbidden_words": [
        "Passionate", "Dedicated", "Highly motivated",
        "Hardworking", "Enthusiastic", "Self-starter",
        "Detail-oriented", "Team player", "Results-driven",
    ],

    # 审查最大迭代轮次
    "max_review_iterations": 3,

    # 竞争力审查改进建议独立预算
    "competitiveness_improvement_budget": 1,
}

# 计算约束指纹 - 用于运行时校验
_CONSTRAINTS_JSON = json.dumps(FROZEN_CONSTRAINTS, sort_keys=True)
CONSTRAINTS_HASH = hashlib.sha256(_CONSTRAINTS_JSON.encode()).hexdigest()


def verify_constraints_integrity() -> bool:
    """运行时校验约束是否被篡改"""
    current = json.dumps(FROZEN_CONSTRAINTS, sort_keys=True)
    current_hash = hashlib.sha256(current.encode()).hexdigest()
    if current_hash != CONSTRAINTS_HASH:
        raise SecurityError(
            f"FROZEN_CONSTRAINTS 已被篡改！"
            f"预期hash: {CONSTRAINTS_HASH}, 当前hash: {current_hash}"
        )
    return True


class SecurityError(Exception):
    pass
