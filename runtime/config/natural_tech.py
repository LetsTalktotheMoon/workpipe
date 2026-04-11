"""
NATURAL_TECH — 各段经历的自然技术栈参考。

设计理念：
- 三层结构（core/extended/stretch）作为**参考建议**，非硬约束
- Writer可自行决定使用哪些层级（作为赛马区分点）
- Reviewer参考此表评估tech-经历匹配度，但不一刀切

core: 该经历几乎必然使用的技术栈
extended: 合理推断可能接触的技术栈
stretch: 在特定业务场景下有可能接触（需叙事支撑）

【虚构候选人注意】
此分层对虚构候选人是建议而非约束。
Writer 可以突破 extended/stretch 边界，只要在 PLAN 中给出合理的业务背景。
判断标准：「这段叙事在该职级/时间/规模下逻辑自洽吗」而非「候选人真实经历了吗」。
"""
from typing import Dict, Set, Optional


BASE_NATURAL_TECH: Dict[str, Dict[str, Set[str]]] = {
    "temu_da": {
        # R&D部门, 算法/推荐/搜索/增长团队, 初级DA, 8个月
        "core": {"Python", "SQL", "Pandas", "Hive", "Spark SQL"},
        "extended": {"Airflow", "NumPy", "scikit-learn", "Jupyter", "A/B Testing", "Matplotlib"},
        "stretch": {"Redis", "Flask", "HiveQL", "Kafka", "ETL"},
    },
    "didi_senior_da": {
        # IBG Food, 跨市场运营, 13人跨职能团队lead, 20个月
        # Java：DiDi内部工具链（如数据中台API、运营管理后台）普遍使用Java；
        # acting team lead可合理声称参与/协调过Java服务的接口对接或schema设计。
        "core": {"Python", "SQL", "Kafka", "Flask", "REST", "ETL"},
        "extended": {"Redis", "Airflow", "Docker", "MySQL", "React", "Pandas", "Java"},
        "stretch": {"Kubernetes", "gRPC", "Microservices", "MongoDB", "Go", "TypeScript"},
    },
    "tiktok_intern": {
        # Security部门, 后端开发实习, 6个月, San Jose
        # TikTok安全部门现实背景：ByteDance全面上AWS（S3/ECS/Bedrock），安全工程师
        # 日常接触云存储/容器化部署/内部AI工具是合理预期。
        # Java在字节跳动后端服务中被广泛使用，安全实习生通过代码审查/集成测试接触合理。
        "core": {"Go", "Python", "Docker", "Kubernetes", "Kafka", "gRPC", "PostgreSQL"},
        "extended": {
            # 后端基础设施（TikTok intern日常接触）
            "CI/CD", "GitHub Actions", "Linux", "Redis", "REST", "Prometheus",
            # Cloud（ByteDance/TikTok在AWS上有大量基础设施，intern通过接口对接合理接触）
            "AWS", "S3", "ECS",
            # GenAI（安全团队内部AI工具，intern通过调用Bedrock/OpenAI API参与RAG管道）
            "Bedrock", "OpenAI", "LLM", "RAG",
            # 字节系Java后端广泛使用
            "Java",
        },
        "stretch": {
            "Terraform", "Flink", "Spring Boot", "TensorFlow",
            "LangChain", "Microservices", "TypeScript",
            "React", "GraphQL", "Elasticsearch", "MongoDB",
        },
    },
}

# TikTok实习是最灵活的经历 — 后端开发岗，tech选择空间最大
FLEXIBLE_EXPERIENCE = "tiktok_intern"

TECH_ALIASES = {
    "apache kafka": "kafka",
    "apache spark": "spark",
    "apache airflow": "airflow",
    "restful": "rest",
    "rest api": "rest",
    "restful api": "rest",
    "tensorflow lite": "tensorflow",
    "data pipelines": "data pipeline",
}


def _normalize_tech_name(tech: str) -> str:
    """统一技术名称，减少 reviewer 对同义词/别名的误杀。"""
    normalized = " ".join(tech.strip().lower().split())
    return TECH_ALIASES.get(normalized, normalized)


def get_all_tiers(exp_id: str) -> Set[str]:
    """获取某段经历所有层级的tech并集"""
    tiers = BASE_NATURAL_TECH.get(exp_id, {})
    return tiers.get("core", set()) | tiers.get("extended", set()) | tiers.get("stretch", set())


def get_suggested_tech(exp_id: str, tier: str = "extended") -> Set[str]:
    """
    获取某段经历建议的技术栈集合。
    tier="core" → 仅core
    tier="extended" → core + extended
    tier="stretch" → core + extended + stretch (全部)
    """
    tiers = BASE_NATURAL_TECH.get(exp_id, {})
    result = set(tiers.get("core", set()))
    if tier in ("extended", "stretch"):
        result |= tiers.get("extended", set())
    if tier == "stretch":
        result |= tiers.get("stretch", set())
    return result


def is_tech_natural(tech: str, exp_id: str) -> Optional[str]:
    """
    判断某个tech对某段经历是否自然。
    返回: "core" / "extended" / "stretch" / None（不在任何层级）

    注意：返回None不代表该tech绝对不能出现在该经历中，
    只是建议Writer在叙事上提供合理解释。
    """
    tiers = BASE_NATURAL_TECH.get(exp_id, {})
    tech_lower = _normalize_tech_name(tech)
    for tier_name in ("core", "extended", "stretch"):
        tier_set = tiers.get(tier_name, set())
        if any(_normalize_tech_name(t) == tech_lower for t in tier_set):
            return tier_name
    return None


def find_best_experience_for_tech(tech: str) -> Optional[str]:
    """
    找到最适合承载某个tech的经历。
    优先级: core > extended > stretch > None
    同层级内优先选择tiktok_intern（最灵活）
    """
    best_exp = None
    best_tier_rank = 99  # lower = better
    tier_ranks = {"core": 0, "extended": 1, "stretch": 2}

    for exp_id in BASE_NATURAL_TECH:
        tier = is_tech_natural(tech, exp_id)
        if tier and tier_ranks.get(tier, 99) < best_tier_rank:
            best_tier_rank = tier_ranks[tier]
            best_exp = exp_id
        elif tier and tier_ranks.get(tier, 99) == best_tier_rank:
            # 同层级，优先tiktok（最灵活）
            if exp_id == FLEXIBLE_EXPERIENCE:
                best_exp = exp_id

    return best_exp
