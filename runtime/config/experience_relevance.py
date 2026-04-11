"""
Experience Relevance — 经历与目标JD的动态适配度计算。

核心理念：
- 滚雪球权重按经历与JD的业务领域匹配度动态调整
- 非机械按职级/时长分配
- 算法岗→Temu权重高; 平台岗→DiDi权重高; 后端岗→TikTok权重高
"""
from typing import Dict, List, Set

# 避免循环import，运行时按需导入JDProfile
# from models.jd import JDProfile


# ── 每段经历的业务领域标签 ──
EXPERIENCE_DOMAINS: Dict[str, Dict] = {
    "temu_da": {
        "primary_domains": [
            "algorithm", "recommendation", "search", "ml",
            "data_pipeline", "ab_testing", "data_science",
        ],
        "secondary_domains": [
            "ecommerce", "growth", "user_acquisition", "ads",
        ],
        "department_signal": "R&D, algorithm/recommendation/search/growth team",
        # 灵活度：0-1，越高越容易承接不相关JD的tech
        "flexibility": 0.3,
    },
    "didi_senior_da": {
        "primary_domains": [
            "platform", "ops", "data_governance", "cross_market",
            "etl", "fullstack", "data_engineering", "international",
        ],
        "secondary_domains": [
            "transportation", "food_delivery", "logistics",
            "leadership", "cross_functional", "product_analytics",
        ],
        "department_signal": "IBG Food, 13-person cross-functional team lead, 6 markets",
        "flexibility": 0.5,
    },
    "tiktok_intern": {
        "primary_domains": [
            "backend", "security", "microservices", "cloud",
            "devops", "infrastructure", "distributed_systems",
        ],
        "secondary_domains": [
            "monitoring", "ci_cd", "swe", "api_design",
            "log_processing", "automation",
        ],
        "department_signal": "Security backend intern, Go/Python microservices",
        "flexibility": 0.8,
    },
}

# ── JD特征到领域的映射 ──
ROLE_TYPE_DOMAINS = {
    "swe_backend": ["backend", "api_design", "microservices", "distributed_systems"],
    "swe_frontend": ["frontend", "ui", "web"],
    "swe_fullstack": ["fullstack", "backend", "frontend", "api_design", "cross_functional", "platform"],
    "swe_devops": ["devops", "cloud", "infrastructure", "ci_cd"],
    "data_analyst": ["data_pipeline", "data_science", "ab_testing", "product_analytics"],
    "data_engineer": ["data_pipeline", "etl", "data_engineering", "platform"],
    "data_scientist": ["ml", "data_science", "algorithm", "ab_testing"],
    "mle": ["ml", "algorithm", "data_pipeline", "infrastructure", "distributed_systems"],
    "tech_pm": ["product_analytics", "cross_functional", "leadership"],
}

TECH_DOMAIN_HINTS = {
    # tech名 → 关联领域
    "algorithm": ["algorithm", "ml"],
    "machine learning": ["ml", "algorithm", "data_science"],
    "ml infrastructure": ["ml", "infrastructure", "data_pipeline"],
    "model deployment": ["ml", "infrastructure", "devops"],
    "recommendation": ["recommendation", "algorithm"],
    "data structures": ["algorithm", "swe", "backend"],
    "c++": ["backend", "infrastructure", "distributed_systems"],
    "go": ["backend", "microservices", "infrastructure"],
    "java": ["backend", "fullstack", "platform"],
    "typescript": ["fullstack", "frontend"],
    "react": ["frontend", "fullstack"],
    "kafka": ["data_pipeline", "backend", "platform"],
    "docker": ["devops", "cloud", "backend"],
    "kubernetes": ["devops", "cloud", "infrastructure"],
    "aws": ["cloud", "infrastructure", "devops"],
    "generative ai": ["ml", "algorithm", "backend"],
    "llm": ["ml", "algorithm"],
    "rag": ["ml", "algorithm", "backend"],
    "spark": ["data_pipeline", "data_engineering"],
    "flask": ["backend", "api_design", "platform"],
    "grpc": ["backend", "microservices", "distributed_systems"],
    "postgresql": ["backend", "data_engineering"],
    "network protocol": ["infrastructure", "distributed_systems", "backend"],
    "embedded": ["infrastructure", "backend"],
    "large-scale systems": ["distributed_systems", "backend", "infrastructure"],
    "software test engineering": ["swe", "backend", "devops"],
    "sql": ["data_pipeline", "data_engineering", "backend"],
    "python": ["data_pipeline", "backend", "ml"],
}


def compute_relevance_weights(jd) -> Dict[str, float]:
    """
    根据JD动态计算各经历的适配度权重。

    Args:
        jd: JDProfile实例（含role_type, business_domain, tech_required, tech_preferred）

    Returns:
        {exp_id: weight} where 0.0 <= weight <= 1.0, 所有weight之和 = 1.0
        weight越高 = 该经历与JD越匹配 = 应分配更多tech深度和bullet篇幅
    """
    # 收集JD关联的领域标签
    jd_domains: Set[str] = set()

    # 从role_type推断
    role_domains = ROLE_TYPE_DOMAINS.get(getattr(jd, 'role_type', ''), [])
    jd_domains.update(role_domains)

    # 从business_domain推断
    biz_domain = getattr(jd, 'business_domain', '')
    if biz_domain:
        jd_domains.add(biz_domain)

    # 从tech_required/preferred推断
    all_tech = getattr(jd, 'tech_required', []) + getattr(jd, 'tech_preferred', [])
    for tech in all_tech:
        hints = TECH_DOMAIN_HINTS.get(tech.lower(), [])
        jd_domains.update(hints)

    # 计算每段经历的原始分数
    raw_scores: Dict[str, float] = {}
    for exp_id, exp_info in EXPERIENCE_DOMAINS.items():
        primary = set(exp_info["primary_domains"])
        secondary = set(exp_info["secondary_domains"])
        flexibility = exp_info["flexibility"]

        # primary匹配: 每个 +3分; secondary匹配: 每个 +1分
        primary_hits = len(primary & jd_domains)
        secondary_hits = len(secondary & jd_domains)
        score = primary_hits * 3.0 + secondary_hits * 1.0

        # 基础分 = flexibility（保证每段经历至少有一定权重）
        score += flexibility

        raw_scores[exp_id] = score

    # 归一化到0-1，和为1.0
    total = sum(raw_scores.values())
    if total == 0:
        # 无匹配时均分
        n = len(raw_scores)
        return {exp_id: 1.0 / n for exp_id in raw_scores}

    weights = {exp_id: score / total for exp_id, score in raw_scores.items()}

    # 保底：每段经历至少0.05（5%），避免完全忽略某段经历
    min_weight = 0.05
    for exp_id in weights:
        if weights[exp_id] < min_weight:
            weights[exp_id] = min_weight
    # 重新归一化
    total = sum(weights.values())
    weights = {exp_id: w / total for exp_id, w in weights.items()}

    return weights


def get_experience_context(exp_id: str) -> str:
    """获取经历的业务描述，供LLM prompt使用"""
    info = EXPERIENCE_DOMAINS.get(exp_id, {})
    return info.get("department_signal", "")
