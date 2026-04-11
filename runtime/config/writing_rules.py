"""
简历撰写规范 - Writer部门和润色部门共享。
所有规则来自原始prompt的简历教具模块规范。
"""

WRITING_RULES = {
    # ========================================
    # 模块一：Professional Summary
    # ========================================
    "summary": {
        "sentence_count": 3,
        "guidelines": [
            "第1句：统一底层能力主线，将跨度极大的背景提炼为一条连贯叙事",
            "第2句：核心技术/业务能力与目标岗位的价值对接",
            "第3句：围棋→职业生产力升华，衔接目标岗位必要特质（如战略思维/模式识别）",
        ],
        "forbidden_words": [
            "Passionate", "Dedicated", "Highly motivated",
            "Hardworking", "Enthusiastic", "Self-starter",
        ],
        "line_length": "每句1.5-2行，字数紧凑",
        "tone": "去情感化，每一行都要有实质性的技术或业务信号",
        "self_check": [
            "如果出现候选人公司/职位/职级/部门/team/年限，是否与简历正文一致？",
            "如果出现目标岗位信息，是否与目标JD一致？",
        ],
    },

    # ========================================
    # 模块二：SKILLS
    # ========================================
    "skills": {
        "ordering_priority": [
            "目标岗位JD重视程度/基础程度",
            "技术栈自身难度/深度",
            "简历全篇提及频次",
        ],
        "rules": [
            "技术基础岗位重点强调硬技术栈",
            "高级岗位或PM岗位适当增加软技术",
            "不出现'孤独分类'（一个分类下只有1-2个技术栈，应合并到其他分类）",
            "每个SKILLS分类至少保留4个技术栈，少于4个必须合并",
            "每个SKILLS行（含分类标题）总词数必须控制在14个以内",
            "检查大小写/缩写与全称/同义词不同表述是否被误识别为不同技术栈",
            "SKILLS中出现的每个技术栈，必须在简历正文中有出处（不可凭空出现）",
        ],
    },

    # ========================================
    # 模块三：工作经历
    # ========================================
    "experience_bullets": {
        "count_per_experience": {"min": 4, "max": 6},
        "data_bullets_per_experience": {"min": 1, "max": 2},
        "format": "动词开头 + 业务价值 + 技术手段 (XYZ格式)",
        "rules": [
            "剔除所有代词（I, We）和无意义的过渡词",
            "不要盲目塞入孤立的关键词，确保关键词与真实工程成就'语义级对齐'",
            "同经历下所有要点逻辑层层递进，最核心数字成就放最后1-2条",
            "不同工作经历下的要点不得重复（如都涉及A/B test需结合不同业务事务）",
            "动词必须匹配职级scope（intern不可用Led/Architected/Drove）",
        ],
    },

    # ========================================
    # 模块四：教育经历
    # ========================================
    "education": {
        "rules": [
            "有选择性呈现教育经历",
            "选择性呈现或rewrite各自track",
            "呈现出来的部分一律不可变",
            "默认不含项目和课程",
            "仅当JD技术栈无法从工作经历cover时启用教育项目（特别是GT MSCS）",
        ],
    },

    # ========================================
    # 流动模块：项目
    # ========================================
    "projects": {
        "count": 2,
        "bullets_per_project": {"min": 4, "max": 6},
        "naming": "必须有专业务实符合对应经历业务背景的项目名称",
        "structure": {
            "baseline": (
                "一句话斜体，高度概括项目解决了什么日常痛点，交代业务上下文；"
                "如果项目与工作title差距大，此处自然解释（回答HR疑虑）"
            ),
            "bullets": (
                "STAR法则，自然融入核心技术栈，达成量化业务指标；"
                "教育项目不可能出现工业规模指标；"
                "每个分配给项目的技术栈都必须'长'在具体描述里"
            ),
        },
        "rules": [
            "项目要点不得与对应骨架经历要点重合",
            "可以是骨架经历要点中1-2点的具体纵深延伸",
            "项目时长和内容需在岗位骨架范围内",
            "有1-2条包含业务数据成就",
        ],
    },

    # ========================================
    # 全篇约束
    # ========================================
    "global": {
        "tech_distribution": "技术栈与能力在各经历中合理分配，不机械重复",
        "generation_order": [
            "1. 根据目标JD决定框架中可变部分",
            "2. 根据可变部分设计项目归属",
            "3. 决定技术栈和软技能的全篇分布",
            "4. 撰写具体要点",
            "5. 最后总结SKILLS和Summary模块",
        ],
        "cross_industry_narrative": (
            "不存在100%对口的工作！转行候选人看中合理的能力迁移与"
            "在自己职责范围内利用公司资源进行跨行业工作尝试的能力，"
            "只要能自圆其说、讲一个完整的故事、在同一职级内即可视作合理发散"
        ),
        "divergence_example": (
            "如身为数据分析师，顺手开发了一个内部使用的数据分析平台，"
            "此为数据分析岗位内部对开发工作的尝试，没有夸大；"
            "但身为初级岗位出现领导团队/决策类要点，为不合理夸大"
        ),
    },
}

# 强动词列表（用于C13检查）
STRONG_VERBS = [
    "Developed", "Built", "Designed", "Implemented", "Engineered",
    "Architected", "Optimized", "Automated", "Deployed", "Integrated",
    "Migrated", "Refactored", "Streamlined", "Orchestrated", "Scaled",
    "Reduced", "Improved", "Increased", "Accelerated", "Enhanced",
    "Led", "Coordinated", "Represented", "Drove", "Mentored",
    "Spearheaded", "Established", "Launched", "Created", "Constructed",
    "Configured", "Transformed", "Consolidated", "Pioneered", "Initiated",
    "Delivered", "Executed", "Maintained", "Monitored", "Analyzed",
    "Diagnosed", "Resolved", "Investigated", "Evaluated", "Assessed",
    "Collaborated", "Facilitated", "Presented", "Communicated", "Proposed",
    "Hardened", "Translated", "Converted", "Exposed", "Clustered",
    "Codified", "Wired", "Shipped", "Grounded", "Unified",
]

# 弱动词列表（需要被替换）
WEAK_VERBS = [
    "Helped", "Assisted", "Worked on", "Was responsible for",
    "Participated in", "Contributed to", "Involved in", "Handled",
    "Did", "Made", "Used", "Supported", "Managed",
]
