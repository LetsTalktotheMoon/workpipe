"""
候选人经历框架 - 不可变部分。
所有简历版本中，不可变字段必须与此框架完全一致。
可变部分在此标注，由Writer根据目标JD自由决定。
"""

from __future__ import annotations

import copy

CANDIDATE_FRAMEWORK = {
    "education": [
        {
            "id": "gt_mscs",
            "degree": "M.S. Computer Science",
            "degree_variant_omscs": "M.S. Computer Science (OMSCS)",
            "school": "Georgia Institute of Technology",
            "dates": "Expected May 2026",
            "immutable_fields": ["school", "dates"],
            "rules": {
                "write_as_mscs_when": "UIUC MSIM不出现在简历中",
                "write_as_omscs_when": "UIUC MSIM出现在简历中",
                "can_add_projects": True,
                "project_scope": "研究生课程scope的课堂项目",
                "use_for": "当JD要求的技术栈无法从工作经历中cover时（特别是硬件/系统相关）",
            },
        },
        {
            "id": "uiuc_msim",
            "degree": "M.S. Information Management (MSIM)",
            "school": "University of Illinois Urbana-Champaign",
            "dates": "Expected May 2026",
            "immutable_fields": ["school", "degree", "dates"],
            "rules": {
                "keep_when": "Data方向/PM方向/信息管理相关岗位",
                "drop_when": "纯SWE后端且与信息管理无关",
            },
        },
        {
            "id": "bisu_mib",
            "degree": "M.S. International Business",
            "school": "Beijing International Studies University",
            "dates": "Sep 2018 – Jun 2021",
            "track": "Finance",
            "immutable_fields": ["school", "degree", "dates"],
            "rules": {
                "track_is_mutable": True,
                "track_options": "Finance/Analytics/Marketing等，需联网验证BISU实际提供的track",
                "keep_when": "FinTech/国际业务/金融数据方向",
                "drop_when": "与目标岗位完全无关且简历空间紧张",
            },
        },
        {
            "id": "bnu_ba",
            "degree": "B.A. Philosophy & Psychology",
            "school": "Beijing Normal University",
            "dates": "Sep 2014 – Jun 2018",
            "immutable_fields": ["school", "degree", "dates"],
            "rules": {
                "keep_when": "TechPM(认知科学角度)/NLP(语言学角度)/UX Research",
                "drop_when": "大多数纯技术岗位",
            },
        },
    ],
    "experience": [
        {
            "id": "temu_da",
            "company": "Temu",
            "department": "R&D",
            "title": "Data Analyst",
            "dates": "Jun 2021 – Feb 2022",
            "location": "Shanghai",
            "duration_months": 8,
            "immutable_fields": ["company", "department", "title", "dates", "location"],
            "seniority": "junior",
            "rules": {
                "can_add_team": True,
                "team_examples": [
                    "Machine Learning Engineering", "Recommendation", "Ads",
                    "Search", "Growth", "User Acquisition", "Infra", "Cloud",
                    "Algorithm", "Ops",
                ],
                "forbidden_verbs": ["Led", "Architected", "Drove", "Spearheaded", "Directed"],
                "scope_ceiling": "individual contributor, 8个月短期经历",
                "max_projects": 2,
                "notes": "初级岗位，不可出现领导/决策类要点",
            },
        },
        {
            "id": "didi_senior_da",
            "company": "DiDi",
            "department": "IBG · Food",
            "title": "Senior Data Analyst",
            "dates": "Sep 2022 – May 2024",
            "location": "Beijing/Mexico",
            "duration_months": 20,
            "immutable_fields": ["company", "department", "title", "dates", "location"],
            "seniority": "mid_senior",
            "rules": {
                "can_add_team": True,
                "leadership": {
                    "team_size": 13,
                    "team_composition": [
                        "前端", "后端", "全栈", "移动端", "PM",
                        "数据中台", "一线业务人员",
                    ],
                    "cross_functional": True,
                    "global_meetings": "每两周全球会议代表北京数据中台总部发言",
                    "decision_scope": "数据决策直接进入管理层和一线",
                },
                "career_bridge": "跨职能接触不同项目，为转行提供桥梁",
                "allowed_verbs": ["Led", "Coordinated", "Represented", "Drove"],
                "scope_ceiling": (
                    "data lead within a 13-person cross-functional squad; may represent the "
                    "headquarters data organization in biweekly global operating reviews, with "
                    "recommendations adopted by management and LATAM frontline teams"
                ),
                "java_context": (
                    "Java 可出现在 DiDi 经历中：DiDi 内部工具链（数据中台 API、"
                    "运营管理后台）普遍使用 Java。作为跨职能团队 lead，"
                    "候选人可合理声称参与了 Java 服务的接口规范对接、"
                    "跨系统 schema 设计或集成测试协调。"
                    "建议在 DiDi 某个 bullet 或 Project 中加入 1 条 Java 使用证据。"
                ),
                "notes": "这是转行叙事的核心桥梁经历",
            },
        },
        {
            "id": "tiktok_intern",
            "company": "TikTok",
            "department": "Security",
            "title": "Software Engineer Intern",
            "dates": "Jun 2025 – Dec 2025",
            "location": "San Jose, USA",
            "duration_months": 6,
            "immutable_fields": ["company", "department", "title", "dates", "location"],
            "seniority": "intern",
            "rules": {
                "can_add_team": False,
                "forbidden_verbs": ["Led", "Architected", "Drove", "Spearheaded", "Managed"],
                "scope_ceiling": "intern, 6个月, 不可声称领导/架构决策",
                "max_projects": 2,
                "notes": "实习生级别，所有要点必须体现个人贡献而非团队领导",
                "same_company_constraint": "如该公司已投递过，team名/项目框架必须一致",
            },
        },
    ],
    "achievement": {
        "id": "go_chess",
        "description": "中国国家认证围棋二段棋手",
        "competitions": "2022年度市赛第一，2023年度市赛第三",
        "immutable_fields": ["description", "competitions"],
        "rules": {
            "optional_display": True,
            "usage": "融入Summary第三句，衔接目标岗位某种必要特质",
            "narrative": "将'兴趣'升华为'职业生产力'，如战略思维/模式识别/复杂系统决策",
        },
    },
}

# 不可变字段索引 - 审查时快速查找
IMMUTABLE_FIELDS = {}
for edu in CANDIDATE_FRAMEWORK["education"]:
    IMMUTABLE_FIELDS[edu["id"]] = {
        field: edu[field] for field in edu["immutable_fields"]
    }
for exp in CANDIDATE_FRAMEWORK["experience"]:
    IMMUTABLE_FIELDS[exp["id"]] = {
        field: exp[field] for field in exp["immutable_fields"]
    }
ach = CANDIDATE_FRAMEWORK["achievement"]
IMMUTABLE_FIELDS[ach["id"]] = {
    field: ach[field] for field in ach["immutable_fields"]
}


def is_bytedance_target_company(company_name: str) -> bool:
    return "bytedance" in str(company_name or "").strip().lower()


def candidate_framework_for_company(company_name: str) -> dict:
    framework = copy.deepcopy(CANDIDATE_FRAMEWORK)
    if is_bytedance_target_company(company_name):
        framework["experience"] = [
            exp for exp in framework.get("experience", [])
            if str(exp.get("id", "") or "") != "tiktok_intern"
        ]
    return framework


def experience_framework_for_company(company_name: str) -> list[dict]:
    return candidate_framework_for_company(company_name).get("experience", [])
