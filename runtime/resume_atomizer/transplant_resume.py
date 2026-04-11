#!/usr/bin/env python3
"""
transplant_resume.py — 确定性简历段落移植 + LLM 最后防线微调系统。

三层策略:
  Layer 1: 确定性段落移植（集群内工作经历互换）
  Layer 2: Skills 最小增量追加（≤3 个关键词）
  Layer 3: LLM 微创手术（仅当 Layer 1+2 仍 <75% 时触发，逐 bullet 注入缺失关键词）

Usage:
    python3 transplant_resume.py --dry-run          # 只打印结果，不生成文件
    python3 transplant_resume.py --all              # 处理所有 JD（含达标判断）
    python3 transplant_resume.py --all --update-notion  # 处理并回写 Notion
    python3 transplant_resume.py --jd jd.txt        # 输入 JD 文件，返回匹配推荐
    python3 transplant_resume.py --jd-text "..."    # 直接输入 JD 文本
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from openai import OpenAI

# 导入共享模块
from notion_match import (
    TECH_VOCAB, BIZ_VOCAB, ALIASES,
    scan_keywords, detect_or_groups, build_requirements, compute_match,
    match_all_resumes, format_analysis_text,
    get_all_pages, extract_page_info, update_notion_fields,
    FROZEN_CATALOG_PATH, NOTION_DB_ID,
)
from build_resumes import build_one, build_progressive, TEX_DIR, PDF_DIR

ROOT = Path(__file__).parent
RESUME_DIR = ROOT / "resumes"
TUNED_DIR = ROOT / "output" / "tuned"
TUNED_MD = TUNED_DIR / "md"
TUNED_TEX = TUNED_DIR / "tex"
TUNED_PDF = TUNED_DIR / "pdf"
TUNED_META = TUNED_DIR / "metadata"


# ═══════════════════════════════════════════════════════════
# 人设集群定义
# ═══════════════════════════════════════════════════════════

CLUSTERS = {
    'backend':  [6, 7, 9, 15, 22],
    'cloud':    [8, 10, 11, 13, 14],
    'ai':       [1, 4, 5],
    'data':     [2, 3],
    'security': [3, 5],
}

# isolated 集群不参与移植
ISOLATED_IDS = {12, 16, 17, 18, 19, 20, 21}


# ═══════════════════════════════════════════════════════════
# 人设方向标签 — 用于 base 选择时的角色亲和度惩罚
# ═══════════════════════════════════════════════════════════

# 每份简历的主要角色人设
RESUME_PERSONA = {
    1:  'ai_genai',        # AI Application & GenAI Integration
    2:  'cloud_data',      # Enterprise Cloud & Big Data
    3:  'security',        # Cloud Security & Threat Engineering
    4:  'ml_research',     # ML/AI Research & Infrastructure
    5:  'responsible_ai',  # Responsible AI
    6:  'fullstack',       # Full-Stack Web & Application
    7:  'generalist_sde',  # Early-Career Generalist SDE
    8:  'cloud_infra',     # Cloud-Native Platform & Infrastructure
    9:  'backend',         # Backend & Distributed Systems
    10: 'devops',          # DevOps & Platform Automation
    11: 'solutions',       # AI Field & Solutions Engineer
    12: 'blockchain',      # Stablecoin & Blockchain
    13: 'edge_networking', # Edge Infrastructure & Networking
    14: 'reliability',     # Platform Reliability & Resilience
    15: 'python_fintech',  # Python Backend FinTech
    16: 'frontend',        # Frontend & Design Systems
    17: 'embedded',        # Embedded & Sensor Software
    18: 'hpc_compiler',    # HPC & Compiler
    19: 'systems',         # Systems Software & Virtualization
    20: 'billing',         # Zuora Billing Developer
    21: 'qa_sdet',         # QA / SDET / Production Verification
    22: 'mobile',          # Mobile Platform Engineer
}

# JD 角色类型检测关键词 → 人设标签
# 用于从 JD 文本推断期望的角色类型
JD_ROLE_SIGNALS = {
    'mobile':          ['mobile', 'android', 'ios', 'swift', 'kotlin', 'jetpack',
                        'react native', 'flutter'],
    'frontend':        ['frontend', 'ui engineer', 'web engineer', 'design system',
                        'react', 'angular', 'vue', 'css', 'html', 'accessibility'],
    'qa_sdet':         ['qa', 'sdet', 'test engineer', 'quality', 'test automation',
                        'selenium', 'appium'],
    'hpc_compiler':    ['hpc', 'compiler', 'cuda', 'gpu', 'llvm', 'mpi', 'openmp'],
    'security':        ['security engineer', 'threat', 'vulnerability', 'siem',
                        'dlp', 'penetration', 'soc'],
    'ml_research':     ['machine learning', 'ml engineer', 'ai/ml', 'deep learning',
                        'model training', 'pytorch', 'tensorflow'],
    'ai_genai':        ['genai', 'generative ai', 'llm', 'rag', 'ai agent',
                        'prompt engineering', 'langchain'],
    'backend':         ['backend', 'distributed systems', 'microservices', 'grpc',
                        'system design'],
    'cloud_infra':     ['infrastructure', 'platform engineer', 'cloud engineer',
                        'terraform', 'kubernetes'],
    'devops':          ['devops', 'sre', 'site reliability', 'ci/cd', 'infrastructure'],
    'reliability':     ['reliability', 'resilience', 'sre', 'incident'],
    'cloud_data':      ['data engineer', 'big data', 'spark', 'airflow', 'etl',
                        'data pipeline', 'redshift', 'emr'],
    'embedded':        ['embedded', 'firmware', 'iot', 'sensor', 'rtos'],
    'blockchain':      ['blockchain', 'web3', 'smart contract', 'solidity', 'defi'],
    'fullstack':       ['full stack', 'fullstack', 'full-stack'],
}

# 人设兼容性矩阵 — 值越高表示越兼容（1.0 = 完全匹配）
# 未列出的配对默认 0.5（中性）
PERSONA_COMPATIBILITY = {
    # 同族高兼容
    ('ai_genai', 'ml_research'): 0.85,
    ('ai_genai', 'responsible_ai'): 0.80,
    ('ml_research', 'responsible_ai'): 0.80,
    ('backend', 'fullstack'): 0.80,
    ('backend', 'cloud_infra'): 0.75,
    ('backend', 'cloud_data'): 0.70,
    ('fullstack', 'frontend'): 0.75,
    ('cloud_infra', 'devops'): 0.85,
    ('cloud_infra', 'reliability'): 0.80,
    ('devops', 'reliability'): 0.80,
    ('cloud_data', 'cloud_infra'): 0.70,
    ('security', 'reliability'): 0.65,
    ('qa_sdet', 'reliability'): 0.60,
    ('generalist_sde', 'backend'): 0.75,
    ('generalist_sde', 'fullstack'): 0.75,
    ('python_fintech', 'backend'): 0.80,
    ('solutions', 'cloud_infra'): 0.70,
    # 跨族低兼容
    ('ai_genai', 'mobile'): 0.25,
    ('ai_genai', 'frontend'): 0.30,
    ('ai_genai', 'qa_sdet'): 0.25,
    ('ai_genai', 'hpc_compiler'): 0.35,
    ('ai_genai', 'embedded'): 0.25,
    ('ml_research', 'mobile'): 0.25,
    ('ml_research', 'frontend'): 0.25,
    ('ml_research', 'qa_sdet'): 0.25,
    ('backend', 'mobile'): 0.40,
    ('backend', 'frontend'): 0.45,
    ('backend', 'qa_sdet'): 0.35,
    ('backend', 'hpc_compiler'): 0.30,
    ('frontend', 'security'): 0.25,
    ('frontend', 'hpc_compiler'): 0.15,
    ('mobile', 'hpc_compiler'): 0.15,
    ('mobile', 'security'): 0.30,
    ('qa_sdet', 'hpc_compiler'): 0.20,
    ('qa_sdet', 'security'): 0.50,
    ('hpc_compiler', 'security'): 0.25,
    ('embedded', 'hpc_compiler'): 0.65,
}


def detect_jd_role(jd_text: str) -> str | None:
    """从 JD 文本推断期望的角色类型"""
    jd_lower = jd_text.lower()
    scores = {}
    for role, signals in JD_ROLE_SIGNALS.items():
        scores[role] = sum(1 for s in signals if s in jd_lower)
    best_role = max(scores, key=scores.get)
    return best_role if scores[best_role] >= 2 else None


def get_persona_compatibility(resume_id: int, jd_role: str | None) -> float:
    """
    计算简历人设与 JD 角色类型的兼容度。
    返回 0.0-1.0，1.0 = 完美匹配。
    """
    if jd_role is None:
        return 0.7  # JD 角色不明确时给中性分
    resume_persona = RESUME_PERSONA.get(resume_id)
    if resume_persona is None:
        return 0.5

    if resume_persona == jd_role:
        return 1.0

    # 查兼容性矩阵（双向查找）
    pair = (resume_persona, jd_role)
    if pair in PERSONA_COMPATIBILITY:
        return PERSONA_COMPATIBILITY[pair]
    pair_rev = (jd_role, resume_persona)
    if pair_rev in PERSONA_COMPATIBILITY:
        return PERSONA_COMPATIBILITY[pair_rev]

    return 0.5  # 默认中性


# ═══════════════════════════════════════════════════════════
# 场景-技术栈亲和表：判断关键词在 bullet 业务场景中是否合理
# ═══════════════════════════════════════════════════════════

SCENE_TECH_AFFINITY = {
    "backend_service": {
        "python", "go", "java", "kotlin", "redis", "kafka", "rabbitmq", "grpc",
        "docker", "kubernetes", "postgresql", "mysql", "mongodb", "dynamodb",
        "nginx", "graphql",
        "spring boot", "node.js", "c++", "c#", ".net", "rust", "django", "fastapi",
        "elasticsearch", "cassandra", "sqlite", "rest", "microservices", "memcached",
    },
    "data_pipeline": {
        "spark", "flink", "airflow", "hive", "presto", "kafka", "kinesis", "emr",
        "hdfs", "parquet", "python", "scala",
        "hadoop", "snowflake", "databricks", "bigquery", "redshift", "dbt", "trino",
        "athena", "hbase", "sql", "nosql", "fivetran", "clickhouse",
    },
    "ml_training": {
        "pytorch", "tensorflow", "cuda", "ray", "mlflow", "python", "numpy",
        "pandas", "huggingface", "wandb",
        "scikit-learn", "keras", "xgboost", "lightgbm", "opencv", "onnx",
        "tensorrt", "langchain", "jupyter", "matplotlib", "scipy", "vllm",
        "reinforcement learning", "deep learning", "machine learning",
        "computer vision", "nlp", "genai", "llm", "rag",
    },
    "frontend_app": {
        "react", "vue", "angular", "typescript", "javascript", "nextjs",
        "webpack", "tailwind", "graphql", "redux",
        "html", "css", "sass", "vite", "svelte", "nuxtjs", "zustand",
        "jest", "cypress", "material-ui", "ant design", "storybook",
    },
    "devops_infra": {
        "terraform", "ansible", "jenkins", "github actions", "docker",
        "kubernetes", "prometheus", "grafana", "aws", "gcp", "azure", "linux", "nginx",
        "gitlab ci", "argocd", "helm", "istio", "datadog", "elk", "splunk",
        "bash", "shell", "vault", "packer", "ci/cd",
    },
    "mobile": {
        "kotlin", "swift", "react native", "flutter", "android", "ios",
        "jetpack", "firebase",
        "objective-c", "java", "dart", "swiftui", "uikit", "coredata",
        "room", "sqlite", "fastlane", "gradle", "cocoapods",
    },
    "qa_automation": {
        "selenium", "appium", "cypress", "playwright", "pytest", "junit",
        "testng", "cucumber", "postman", "jmeter", "k6",
    },
}

# 场景识别关键词（用于从 bullet 文本推断业务场景）
SCENE_SIGNALS = {
    "backend_service": ["service", "api", "endpoint", "backend", "server", "request",
                        "microservice", "rest", "grpc", "handler", "route", "middleware"],
    "data_pipeline":   ["pipeline", "etl", "data", "warehouse", "batch", "stream",
                        "ingest", "transform", "table", "query", "schema", "lake"],
    "ml_training":     ["model", "train", "neural", "inference", "predict", "feature",
                        "embedding", "accuracy", "loss", "epoch", "dataset", "ml", "ai"],
    "frontend_app":    ["frontend", "ui", "portal", "dashboard", "page", "component",
                        "render", "browser", "dom", "layout", "responsive", "ux"],
    "devops_infra":    ["deploy", "infrastructure", "provision", "monitor", "alert",
                        "pipeline", "ci", "cd", "cluster", "node", "uptime", "sre"],
    "mobile":          ["mobile", "app", "android", "ios", "device", "screen",
                        "notification", "gesture", "native"],
    "qa_automation":   ["test", "automat", "coverage", "regression", "e2e", "qa",
                        "assert", "fixture", "mock", "integration test"],
}


def classify_bullet_scene(bullet: str) -> str:
    """根据 bullet 已有关键词判断业务场景"""
    bullet_lower = bullet.lower()
    scores = {}
    for scene, signals in SCENE_SIGNALS.items():
        scores[scene] = sum(1 for s in signals if s in bullet_lower)
    best = max(scores, key=scores.get)
    # 如果最高分为 0，回退到 backend_service（最宽泛的场景）
    return best if scores[best] > 0 else "backend_service"


def is_injectable(keyword: str, bullet: str) -> bool:
    """关键词是否可以合理注入到这条 bullet 的业务场景中"""
    scene = classify_bullet_scene(bullet)
    return keyword.lower() in SCENE_TECH_AFFINITY.get(scene, set())


# LLM 微创手术可恢复的最大缺失关键词数
MAX_RECOVERABLE = 6


def get_cluster(resume_id: int) -> str | None:
    """返回简历所属的集群名称；isolated 返回 None"""
    if resume_id in ISOLATED_IDS:
        return None
    for name, ids in CLUSTERS.items():
        if resume_id in ids:
            return name
    return None


def get_best_cluster_for_jd(resume_id: int, jd_biz: set[str]) -> str | None:
    """当简历属于多个集群时（如 03 在 data + security），选与 JD 业务方向更匹配的集群"""
    if resume_id in ISOLATED_IDS:
        return None
    matching_clusters = [name for name, ids in CLUSTERS.items() if resume_id in ids]
    if len(matching_clusters) == 1:
        return matching_clusters[0]
    if not matching_clusters:
        return None
    # 对多集群简历，选集群内简历数更多的（覆盖更广）
    # 如果 JD 含 security 相关词，优先 security 集群
    security_words = {'security', 'fraud', 'compliance', 'privacy', 'threat detection'}
    if 'security' in matching_clusters and jd_biz & security_words:
        return 'security'
    return max(matching_clusters, key=lambda c: len(CLUSTERS[c]))


# ═══════════════════════════════════════════════════════════
# LLM 微创手术（Layer 3 — 最后防线）
# ═══════════════════════════════════════════════════════════

def get_llm_client():
    return OpenAI(
        api_key=os.environ.get("API_KEY", ""),
        base_url=os.environ.get("BASE_URL", ""),
    )


def call_llm(prompt: str, system: str = "", max_retries: int = 2) -> str | None:
    """调用 LLM API，复用 match_resume.py 的模式"""
    client = get_llm_client()
    model = os.environ.get("LLM_MODEL", "kimi-k2.5")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,
                max_tokens=1000,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"    ⚠️ LLM API 调用失败 (attempt {attempt+1}): {e}")
            if attempt < max_retries:
                time.sleep(3)
    return None


# 关键词的标准显示格式
DISPLAY_KW = {
    'python': 'Python', 'java': 'Java', 'go': 'Go', 'golang': 'Go',
    'c++': 'C++', 'c#': 'C#', 'rust': 'Rust', 'ruby': 'Ruby',
    'scala': 'Scala', 'kotlin': 'Kotlin', 'swift': 'Swift',
    'typescript': 'TypeScript', 'javascript': 'JavaScript',
    'sql': 'SQL', 'bash': 'Bash', 'matlab': 'MATLAB',
    'django': 'Django', 'flask': 'Flask', 'fastapi': 'FastAPI',
    'react': 'React', 'angular': 'Angular', 'vue': 'Vue',
    'node.js': 'Node.js', 'next.js': 'Next.js',
    'spring boot': 'Spring Boot', 'spring': 'Spring',
    'kubernetes': 'Kubernetes', 'docker': 'Docker',
    'terraform': 'Terraform', 'helm': 'Helm', 'istio': 'Istio',
    'kafka': 'Kafka', 'redis': 'Redis', 'mongodb': 'MongoDB',
    'postgresql': 'PostgreSQL', 'mysql': 'MySQL',
    'elasticsearch': 'Elasticsearch', 'snowflake': 'Snowflake',
    'cassandra': 'Cassandra', 'rabbitmq': 'RabbitMQ',
    'pytorch': 'PyTorch', 'tensorflow': 'TensorFlow',
    'langchain': 'LangChain', 'langgraph': 'LangGraph',
    'llm': 'LLM', 'rag': 'RAG', 'genai': 'GenAI',
    'nlp': 'NLP', 'ml': 'ML', 'ai': 'AI',
    'aws': 'AWS', 'gcp': 'GCP', 'azure': 'Azure',
    'grpc': 'gRPC', 'graphql': 'GraphQL', 'rest': 'REST',
    'ci/cd': 'CI/CD', 'github actions': 'GitHub Actions',
    'jenkins': 'Jenkins', 'argocd': 'ArgoCD', 'gitops': 'GitOps',
    'prometheus': 'Prometheus', 'grafana': 'Grafana',
    'datadog': 'Datadog', 'opentelemetry': 'OpenTelemetry',
    'machine learning': 'Machine Learning',
    'deep learning': 'Deep Learning',
    'computer vision': 'Computer Vision',
    'distributed systems': 'distributed systems',
    'microservices': 'microservices', 'system design': 'system design',
    'hiveql': 'HiveQL', 'sparksql': 'SparkSQL',
    'solidity': 'Solidity', 'protobuf': 'Protobuf',
    'airflow': 'Airflow', 'flink': 'Flink',
    'dynamodb': 'DynamoDB', 'bigquery': 'BigQuery',
    'eks': 'EKS', 'ecs': 'ECS', 'gke': 'GKE',
    's3': 'S3', 'rds': 'RDS', 'ec2': 'EC2',
    'lambda': 'Lambda', 'fargate': 'Fargate',
    'emr': 'EMR', 'kinesis': 'Kinesis',
    'redshift': 'Redshift', 'cloudwatch': 'CloudWatch',
    'owasp': 'OWASP', 'jwt': 'JWT', 'oauth': 'OAuth',
    'rbac': 'RBAC', 'abac': 'ABAC', 'saml': 'SAML',
    'oidc': 'OIDC', 'mfa': 'MFA', 'hsm': 'HSM', 'kms': 'KMS',
    'pci-dss': 'PCI-DSS', 'siem': 'SIEM', 'dlp': 'DLP',
    'threat detection': 'threat detection',
    'vulnerability': 'vulnerability',
    'encryption': 'encryption', 'compliance': 'compliance',
    'agile': 'Agile', 'scrum': 'Scrum', 'sdlc': 'SDLC',
    'linux': 'Linux', 'nginx': 'Nginx',
    'mpi': 'MPI', 'openmp': 'OpenMP', 'cuda': 'CUDA',
    'llvm': 'LLVM', 'hpc': 'HPC',
    'pytest': 'pytest', 'junit': 'JUnit',
    'selenium': 'Selenium', 'cypress': 'Cypress',
    'appium': 'Appium', 'espresso': 'Espresso',
    'android': 'Android', 'ios': 'iOS',
    'css': 'CSS', 'html': 'HTML',
    'blockchain': 'blockchain', 'smart contract': 'smart contract',
    'web3': 'Web3', 'erc-20': 'ERC-20',
    'mcp': 'MCP', 'openapi': 'OpenAPI',
}


def format_kw_display(kw: str) -> str:
    """获取关键词的标准显示格式"""
    return DISPLAY_KW.get(kw, kw.title() if len(kw) > 3 else kw.upper())


def extract_bullets(md_text: str) -> list[tuple[int, str]]:
    """
    提取 MD 文本中所有 bullet points（以 * 开头的行）。
    返回 [(行号, 原始行文本), ...]
    """
    bullets = []
    lines = md_text.split('\n')
    for i, line in enumerate(lines):
        if re.match(r'^\s*\*\s+', line):
            bullets.append((i, line))
    return bullets


def find_best_bullet_for_keyword(
    bullets: list[tuple[int, str]],
    keyword: str,
    already_modified: set[int],
) -> tuple[int, str] | None:
    """
    为一个缺失关键词找到最佳候选 bullet（场景兼容 + 语义最相关）。
    已修改过的 bullet 不再选取。

    两层筛选：
    1. 场景兼容性（SCENE_TECH_AFFINITY）：关键词必须属于 bullet 场景的合理技术栈
    2. 领域亲和度：在兼容 bullets 中选语义最相关的
    """
    # 关键词的领域亲和词（用于在兼容 bullets 中排序）
    domain_affinity = {
        # 编程语言
        'python': ['python', 'script', 'automat', 'develop', 'implement', 'built', 'engineer'],
        'java': ['java', 'service', 'backend', 'develop', 'module', 'implement', 'spring'],
        'go': ['go', 'golang', 'service', 'microservice', 'backend', 'develop'],
        'c++': ['c++', 'performance', 'parser', 'engine', 'optimize', 'memory'],
        'c#': ['c#', '.net', 'service', 'backend', 'develop', 'application'],
        'typescript': ['typescript', 'frontend', 'react', 'web', 'ui', 'portal'],
        'javascript': ['javascript', 'frontend', 'react', 'web', 'ui', 'node'],
        'rust': ['rust', 'performance', 'system', 'memory', 'safe'],
        'ruby': ['ruby', 'rails', 'web', 'api', 'backend'],
        'scala': ['scala', 'spark', 'data', 'pipeline', 'stream'],
        'kotlin': ['kotlin', 'android', 'mobile', 'app', 'service'],
        'swift': ['swift', 'ios', 'mobile', 'app'],
        # 框架
        'spring boot': ['java', 'service', 'api', 'backend', 'microservice'],
        'spring': ['java', 'service', 'api', 'backend'],
        'django': ['python', 'web', 'api', 'backend'],
        'flask': ['python', 'api', 'lightweight', 'internal'],
        'fastapi': ['python', 'api', 'backend', 'async'],
        'react': ['frontend', 'ui', 'web', 'portal', 'dashboard'],
        'angular': ['frontend', 'ui', 'web', 'portal'],
        'vue': ['frontend', 'ui', 'web'],
        'node.js': ['node', 'javascript', 'backend', 'api', 'server'],
        # 云 & 基础设施
        'kubernetes': ['deploy', 'cluster', 'container', 'orchestrat', 'helm', 'pod'],
        'docker': ['container', 'deploy', 'image', 'build'],
        'terraform': ['infrastructure', 'provision', 'cloud', 'deploy'],
        'aws': ['aws', 'cloud', 'deploy', 's3', 'ec2', 'ecs', 'lambda'],
        'gcp': ['gcp', 'google', 'cloud', 'gke', 'bigquery'],
        'azure': ['azure', 'microsoft', 'cloud', 'deploy'],
        # 数据
        'kafka': ['kafka', 'stream', 'event', 'message', 'pipeline', 'async'],
        'redis': ['redis', 'cache', 'session', 'store', 'distributed'],
        'mongodb': ['mongo', 'document', 'store', 'database', 'collection'],
        'postgresql': ['postgres', 'database', 'sql', 'schema', 'query'],
        'mysql': ['mysql', 'database', 'sql', 'query'],
        'dynamodb': ['dynamo', 'database', 'nosql', 'aws', 'store'],
        'flink': ['flink', 'stream', 'real-time', 'pipeline', 'processing'],
        'elasticsearch': ['elastic', 'search', 'index', 'query', 'log'],
        'snowflake': ['snowflake', 'data', 'warehouse', 'query', 'analytics'],
        'cassandra': ['cassandra', 'nosql', 'distributed', 'store', 'wide-column'],
        # AI/ML
        'pytorch': ['pytorch', 'model', 'train', 'neural', 'deep learning', 'ml'],
        'tensorflow': ['tensorflow', 'model', 'train', 'neural', 'deep learning', 'ml'],
        'langchain': ['langchain', 'llm', 'chain', 'ai', 'rag', 'prompt'],
        'genai': ['ai', 'llm', 'generat', 'model', 'prompt'],
        'scikit-learn': ['model', 'train', 'predict', 'feature', 'classif'],
        'reinforcement learning': ['reinforcement', 'reward', 'agent', 'policy', 'model', 'train', 'ml', 'ai'],
        'deep learning': ['deep', 'neural', 'model', 'train', 'layer', 'ml'],
        'machine learning': ['machine', 'model', 'train', 'predict', 'ml', 'ai', 'feature'],
        'computer vision': ['vision', 'image', 'detect', 'segment', 'opencv', 'visual'],
        # 安全
        'owasp': ['security', 'vulnerab', 'compliance', 'scan', 'penetrat'],
        'jwt': ['jwt', 'token', 'auth', 'session', 'identity'],
        'threat detection': ['threat', 'security', 'detect', 'alert', 'incident'],
        'vulnerability': ['vulnerab', 'security', 'scan', 'patch', 'remediat'],
        # 系统设计
        'distributed systems': ['distribut', 'system', 'scale', 'fault', 'replicat'],
        'system design': ['design', 'architect', 'system', 'scale', 'pattern'],
        'microservices': ['microservice', 'service', 'api', 'endpoint', 'module'],
        # 业务方向（biz keywords）
        'ads': ['ads', 'advertis', 'campaign', 'click', 'impression', 'revenue', 'conversion'],
        'advertising': ['advertis', 'ads', 'campaign', 'click', 'impression', 'revenue'],
        'gaming': ['game', 'player', 'session', 'event', 'real-time', 'latency'],
        'payments': ['payment', 'transact', 'settle', 'billing', 'money', 'charge'],
        'payment': ['payment', 'transact', 'settle', 'billing', 'money'],
        'billing': ['billing', 'invoice', 'charge', 'subscript', 'revenue'],
        'fraud': ['fraud', 'risk', 'anomal', 'detect', 'suspicious', 'security'],
        'networking': ['network', 'tcp', 'protocol', 'routing', 'packet', 'latency', 'throughput'],
        'embedded': ['embedded', 'device', 'firmware', 'sensor', 'hardware', 'iot'],
        'iot': ['iot', 'device', 'sensor', 'embedded', 'connect'],
        'analytics': ['analytic', 'metric', 'dashboard', 'kpi', 'report', 'data'],
        # 测试
        'selenium': ['test', 'automat', 'browser', 'e2e', 'ui'],
        'cypress': ['test', 'e2e', 'frontend', 'browser', 'automat'],
        'pytest': ['test', 'python', 'automat', 'unit', 'assert'],
        'junit': ['test', 'java', 'unit', 'assert'],
    }

    # 默认亲和词
    default_affinity = [keyword.split()[0] if ' ' in keyword else keyword[:4]]
    affinity_words = domain_affinity.get(keyword, default_affinity)

    best_idx = None
    best_line = None
    best_score = -1

    for line_idx, line in bullets:
        if line_idx in already_modified:
            continue

        # 第一层：场景兼容性检查
        # 软件技术栈必须属于 bullet 场景的合理技术栈
        if not is_injectable(keyword, line):
            # biz 关键词（ads, gaming 等）不受场景限制，只看亲和度
            if keyword not in BIZ_VOCAB:
                continue

        # 第二层：亲和度评分
        line_lower = line.lower()
        score = sum(1 for w in affinity_words if w in line_lower)
        if score > best_score:
            best_score = score
            best_idx = line_idx
            best_line = line

    if best_idx is not None:
        return (best_idx, best_line)
    return None


LLM_SURGERY_SYSTEM = """你现在不是一个简历撰写者，而是一个执行"微创手术"的 ATS 简历优化插件。
你的唯一任务是将缺失的【目标关键词】极度克制地、无缝且符合逻辑地融入到我提供的【原简历要点】中。"""

LLM_SURGERY_PROMPT = """【输入数据】
- 目标关键词：[{missing_keywords}]
- 业务场景：[{scene}]
- 目标岗位基调：[{job_title}]
- 原简历要点 (仅限此句，不改变上下文)：
{bullet}

【场景上下文】
这条 bullet 描述的是 {scene} 场景。【{missing_keywords}】属于候选人在该场景下真实接触过的技术栈（已通过场景亲和表验证），可以作为实现细节自然融入。

【极度克制的微调纪律 (Strict Surgical Constraints)】
为了保持工业级简历的真实感，你必须遵守以下最高优先级纪律：
1. 最小化变动 (Minimal Mutation)：禁止重写整个句子结构！你只能在"技术手段/工具链"出现的地方进行"平替"或"并列插入"。（例如：如果原句是基于 MySQL 实现的，而缺失词是 PostgreSQL，请自然替换或扩展为兼顾两者的表述，禁止改变原句的业务逻辑）。
2. 绝对禁止越权与幻觉 (No Scope Inflation)：严格维持原要点的职级深度和动作范围。如果原句的动词是"参与/开发"，绝对不能为了迎合关键词而改写成"主导/架构"。绝对不能为了该关键词生造一段宏大的业务背景。
3. 冻结核心指标 (Freeze Metrics & Results)：原句中的所有量化数据（如 60%+、5M+ calls、<100ms 等）以及业务收益，全部视为**只读常量，绝对禁止修改、删除或新增**。
4. 继承反过度包装法则 (Anti-Over-engineering)：禁止添加任何"企业级废话"（如 manually orchestrated），禁止深入到代码颗粒度（如传参或类名）。
5. 🚨 关键词必须有技术动作支撑 (No Dangling Keywords)：关键词必须作为一个具体技术动作的工具/手段/对象出现，而非仅仅括号提及或作为标签罗列。
   - ✅ 正确示例："...deployed on **Azure** Kubernetes Service via Helm chart..." — Azure 是部署目标
   - ✅ 正确示例："...consuming **Flink**-processed event streams for real-time feature updates..." — Flink 是数据处理手段
   - ❌ 错误示例："...deployed on Kubernetes (**Azure**)..." — 括号标注无技术动作
   - ❌ 错误示例："...pipeline processing events (**Flink**)..." — 仅括号提及
   - ❌ 错误示例：在句末追加 "including reinforcement learning" — 无具体动作
   如果无法在原句中为该关键词找到合理的技术动作位置，请原样返回原句不做修改。

【最终输出指令】
请直接输出修改后的这条 Markdown 格式的 Bullet Point（保留原有的 `* ` 开头和 `**加粗**` 格式，你可以将新融入的关键词也加粗）。
最高警告：绝对不要输出任何解释、思考过程、前后对比或任何多余的寒暄语。只输出那句话本身。"""


def apply_llm_surgery(
    md_text: str,
    missing_keywords: list[str],
    job_title: str,
    max_surgeries: int = 5,
) -> tuple[str, list[str]]:
    """
    对 MD 文本执行 LLM 微创手术，逐个注入缺失关键词。

    返回: (modified_md_text, injected_keywords)
    """
    lines = md_text.split('\n')

    # 提取工作经历区域的 bullets（跳过 Summary 和 Skills）
    work_start = None
    skills_start = None
    for i, line in enumerate(lines):
        if re.match(r'^## Work Experience', line):
            work_start = i
        elif re.match(r'^## Skills', line):
            skills_start = i

    if work_start is None:
        return md_text, []

    # 只选工作经历区域的 bullets
    work_bullets = []
    end_line = skills_start if skills_start else len(lines)
    for i in range(work_start, end_line):
        if re.match(r'^\s*\*\s+', lines[i]):
            work_bullets.append((i, lines[i]))

    if not work_bullets:
        return md_text, []

    injected = []
    already_modified = set()
    surgeries_done = 0

    # 按关键词逐个处理（每个关键词尝试注入一个 bullet）
    for kw in missing_keywords:
        if surgeries_done >= max_surgeries:
            break

        # 检查关键词是否已经通过之前的修改被覆盖了
        current_text = '\n'.join(lines)
        if scan_keywords(current_text, [kw]) or scan_keywords(current_text, BIZ_VOCAB) & {kw}:
            injected.append(kw)
            continue

        # 找最佳候选 bullet
        target = find_best_bullet_for_keyword(work_bullets, kw, already_modified)
        if target is None:
            continue

        line_idx, original_bullet = target

        # 组装 LLM prompt — 每次只注入 1 个关键词，携带场景上下文
        display = format_kw_display(kw)
        scene = classify_bullet_scene(original_bullet)
        scene_display = scene.replace('_', ' ')
        prompt = LLM_SURGERY_PROMPT.format(
            missing_keywords=display,
            scene=scene_display,
            job_title=job_title,
            bullet=original_bullet,
        )

        print(f"    🔬 LLM 微创: 注入 [{display}] → L{line_idx+1}")

        result = call_llm(prompt, system=LLM_SURGERY_SYSTEM)
        if not result:
            continue

        # 清理 LLM 输出（去掉可能的代码块标记、多余换行）
        result = result.strip()
        result = re.sub(r'^```\w*\n?', '', result)
        result = re.sub(r'\n?```$', '', result)
        result = result.strip()

        # 验证输出是 bullet point 格式
        if not result.startswith('*'):
            result = '* ' + result

        # 验证关键词确实被注入了（检查 tech 和 biz 词表）
        found_in_tech = bool(scan_keywords(result, [kw]))
        found_in_biz = kw in scan_keywords(result, BIZ_VOCAB)
        if not found_in_tech and not found_in_biz:
            # 也用简单的子串检查作为后备
            if kw.lower() not in result.lower():
                print(f"    ⚠️ LLM 未成功注入 [{display}]，跳过")
                continue

        # 替换原行
        lines[line_idx] = result
        already_modified.add(line_idx)
        injected.append(kw)
        surgeries_done += 1

        # 短暂延迟避免 API 限流
        time.sleep(0.5)

    return '\n'.join(lines), injected


def rescore_md(md_text: str, jd_text: str) -> tuple[float, dict]:
    """
    对修改后的 MD 文本重新评分。
    返回 (score, details)
    """
    # 清理文本再扫描
    cleaned = re.sub(r'\bGo\s*\(Weiqi\)', '', md_text, flags=re.IGNORECASE)
    cleaned = re.sub(r'\d-Dan\s+Go\b', '', cleaned)
    cleaned = re.sub(r'##\s*Additional Information.*', '', cleaned, flags=re.DOTALL)

    resume_tech = scan_keywords(cleaned, TECH_VOCAB)
    resume_biz = scan_keywords(cleaned, BIZ_VOCAB)

    jd_tech = scan_keywords(jd_text, TECH_VOCAB)
    jd_biz = scan_keywords(jd_text, BIZ_VOCAB)
    or_groups = detect_or_groups(jd_text, jd_tech)
    requirements = build_requirements(jd_tech, or_groups)

    details = compute_match(requirements, jd_biz, resume_tech, resume_biz)
    return details['total'], details


# ═══════════════════════════════════════════════════════════
# 段落解析器
# ═══════════════════════════════════════════════════════════

def parse_sections(md_text: str) -> dict[str, str]:
    """
    将简历 MD 拆分为独立段落。

    返回 dict:
        header, summary, work_experience_header,
        bytedance, didi, temu,
        skills, education
    """
    lines = md_text.split('\n')
    sections = {}

    # ── 找到各段落的起止行号 ──
    # header: 开头到第一个 ---
    first_hr = None
    for i, line in enumerate(lines):
        if line.strip() == '---':
            first_hr = i
            break

    sections['header'] = '\n'.join(lines[:first_hr]) if first_hr else ''

    # 找所有 ## 和 ### 标题的位置
    headings = []  # (line_idx, level, text)
    for i, line in enumerate(lines):
        m = re.match(r'^(#{2,3})\s+(.+)', line)
        if m:
            headings.append((i, len(m.group(1)), m.group(2).strip()))

    # 找所有 --- 分隔线
    hrs = [i for i, line in enumerate(lines) if line.strip() == '---']

    # ── Professional Summary ──
    summary_start = None
    summary_end = None
    for idx, level, text in headings:
        if level == 2 and 'professional summary' in text.lower():
            summary_start = idx
            # 结束于下一个 --- 或下一个 ## 标题
            for hr in hrs:
                if hr > idx:
                    summary_end = hr
                    break
            break
    if summary_start is not None:
        sections['summary'] = '\n'.join(lines[summary_start:summary_end])
    else:
        sections['summary'] = ''

    # ── Work Experience header line ──
    work_exp_start = None
    for idx, level, text in headings:
        if level == 2 and 'work experience' in text.lower():
            work_exp_start = idx
            break

    # ── 三段工作经历：按 ### 切分 ──
    job_headings = []  # (line_idx, text)
    for idx, level, text in headings:
        if level == 3 and work_exp_start is not None and idx > work_exp_start:
            job_headings.append((idx, text))

    # 确定每段工作经历的结束行
    for i, (start_idx, title) in enumerate(job_headings):
        if i + 1 < len(job_headings):
            end_idx = job_headings[i + 1][0]
        else:
            # 最后一段工作经历，结束于下一个 ## 标题或 ---
            end_idx = len(lines)
            for idx2, level2, _ in headings:
                if level2 == 2 and idx2 > start_idx:
                    end_idx = idx2
                    break
            # 也检查 --- 分隔线
            for hr in hrs:
                if hr > start_idx and hr < end_idx:
                    end_idx = hr
                    break

        section_text = '\n'.join(lines[start_idx:end_idx]).rstrip()
        title_lower = title.lower()
        if 'bytedance' in title_lower or 'tiktok' in title_lower:
            sections['bytedance'] = section_text
        elif 'didi' in title_lower:
            sections['didi'] = section_text
        elif 'temu' in title_lower:
            sections['temu'] = section_text

    # ── Skills ──
    skills_start = None
    skills_end = None
    for idx, level, text in headings:
        if level == 2 and 'skills' in text.lower():
            skills_start = idx
            for hr in hrs:
                if hr > idx:
                    skills_end = hr
                    break
            if skills_end is None:
                skills_end = len(lines)
            break
    sections['skills'] = '\n'.join(lines[skills_start:skills_end]).rstrip() if skills_start else ''

    # ── Education + Academic Projects + Additional（固定不变）──
    # 精确捕获：只包含 Education / Academic Projects / Additional Information
    # 排除 Work Experience 和 Skills（它们由 assemble_resume 单独处理）
    TAIL_SECTIONS = {'education', 'academic projects', 'additional information',
                     'relevant coursework', 'certifications', 'publications'}
    EXCLUDE_SECTIONS = {'work experience', 'skills', 'professional summary'}

    edu_parts = []
    for idx, level, text in headings:
        if level != 2:
            continue
        section_name = text.lower().strip()
        # 判断该 section 是否属于"尾部固定段落"
        if any(t in section_name for t in TAIL_SECTIONS):
            # 找到该 section 的结束位置（下一个 ## 标题或 EOF）
            sec_end = len(lines)
            for idx2, level2, text2 in headings:
                if level2 == 2 and idx2 > idx:
                    sec_end = idx2
                    break
            # 也检查 --- 分隔线（但只在不跨越下一个 ## 的情况下）
            for hr in hrs:
                if hr > idx and hr < sec_end:
                    sec_end = hr
                    break
            edu_parts.append((idx, '\n'.join(lines[idx:sec_end]).rstrip()))

    # Additional Information 可能没有 ## 标题，而是在最后一个 --- 之后
    # 单独检查
    additional_start = None
    for idx, level, text in headings:
        if level == 2 and 'additional' in text.lower():
            additional_start = idx
            break
    if additional_start is not None:
        # 检查是否已经在 edu_parts 中
        already_captured = any(start == additional_start for start, _ in edu_parts)
        if not already_captured:
            edu_parts.append((additional_start, '\n'.join(lines[additional_start:]).rstrip()))

    # 按原始行号排序并拼接
    edu_parts.sort(key=lambda x: x[0])
    sections['education'] = '\n\n---\n\n'.join(text for _, text in edu_parts) if edu_parts else ''

    return sections


# ═══════════════════════════════════════════════════════════
# 段落级关键词预计算
# ═══════════════════════════════════════════════════════════

def precompute_section_keywords(all_parsed: dict[int, dict]) -> dict:
    """
    预计算每份简历每个段落的关键词集合。

    返回:
        {resume_id: {section_name: {'tech': set, 'biz': set}}}
    """
    result = {}
    job_sections = ['bytedance', 'didi', 'temu']

    for rid, sections in all_parsed.items():
        result[rid] = {}
        for sec_name in ['summary'] + job_sections:
            text = sections.get(sec_name, '')
            # 对工作经历段，去掉 Go (Weiqi) 引用
            cleaned = re.sub(r'\bGo\s*\(Weiqi\)', '', text, flags=re.IGNORECASE)
            cleaned = re.sub(r'\d-Dan\s+Go\b', '', cleaned)
            result[rid][sec_name] = {
                'tech': scan_keywords(cleaned, TECH_VOCAB),
                'biz': scan_keywords(cleaned, BIZ_VOCAB),
            }
    return result


# ═══════════════════════════════════════════════════════════
# 集群内组合枚举
# ═══════════════════════════════════════════════════════════

def find_best_combination(
    jd_text: str,
    base_id: int,
    cluster_name: str,
    section_kw: dict,
    catalog: list[dict],
) -> tuple[dict, float, dict]:
    """
    在集群内枚举 bytedance/didi/temu 的最优组合。
    Summary 锁定为 base 简历。

    返回: (best_sources, best_score, best_details)
        best_sources = {'bytedance': 9, 'didi': 15, 'temu': 9}
    """
    cluster_ids = CLUSTERS[cluster_name]

    # 扫描 JD
    jd_tech = scan_keywords(jd_text, TECH_VOCAB)
    jd_biz = scan_keywords(jd_text, BIZ_VOCAB)
    or_groups = detect_or_groups(jd_text, jd_tech)
    requirements = build_requirements(jd_tech, or_groups)

    # base 简历的 summary 关键词（锁定）
    base_summary_tech = section_kw[base_id]['summary']['tech']
    base_summary_biz = section_kw[base_id]['summary']['biz']

    best_score = -1.0
    best_sources = {'bytedance': base_id, 'didi': base_id, 'temu': base_id}
    best_details = {}
    best_change_count = 99  # 用于同分取最小改动

    for bt in cluster_ids:
        bt_tech = section_kw[bt]['bytedance']['tech']
        bt_biz = section_kw[bt]['bytedance']['biz']
        for dd in cluster_ids:
            dd_tech = section_kw[dd]['didi']['tech']
            dd_biz = section_kw[dd]['didi']['biz']
            for tm in cluster_ids:
                tm_tech = section_kw[tm]['temu']['tech']
                tm_biz = section_kw[tm]['temu']['biz']

                combined_tech = base_summary_tech | bt_tech | dd_tech | tm_tech
                combined_biz = base_summary_biz | bt_biz | dd_biz | tm_biz

                result = compute_match(requirements, jd_biz, combined_tech, combined_biz)
                score = result['total']

                # 计算改动段数（与 base 不同的段数）
                changes = sum(1 for x in [bt, dd, tm] if x != base_id)

                # 同分取改动最少的
                if score > best_score or (score == best_score and changes < best_change_count):
                    best_score = score
                    best_sources = {'bytedance': bt, 'didi': dd, 'temu': tm}
                    best_details = result
                    best_change_count = changes

    return best_sources, best_score, best_details


# ═══════════════════════════════════════════════════════════
# Skills 最小增量追加
# ═══════════════════════════════════════════════════════════

def patch_skills(
    base_skills_text: str,
    jd_tech: set[str],
    base_resume_tech: set[str],
    transplanted_tech: set[str],
    max_additions: int = 3,
) -> str:
    """
    在 base Skills 段基础上，追加 JD 要求且有移植段落支撑的关键词。
    最多追加 max_additions 个。

    返回修改后的 Skills 文本。
    """
    # 找出 JD 要求但 base 缺失、且移植段落支撑的关键词
    missing_in_base = jd_tech - base_resume_tech
    gained = missing_in_base & transplanted_tech

    if not gained:
        return base_skills_text

    # 只取前 max_additions 个（按字母排序确保确定性）
    additions = sorted(gained)[:max_additions]

    if not additions:
        return base_skills_text

    # 分类追加：尝试找到合适的 Skills 行追加
    lines = base_skills_text.split('\n')
    added = set()

    # 关键词到类别的映射（简化版）
    category_hints = {
        'languages': ['python', 'java', 'go', 'golang', 'c++', 'c#', 'typescript',
                       'javascript', 'kotlin', 'swift', 'rust', 'ruby', 'scala',
                       'sql', 'matlab', 'bash', 'solidity', 'hiveql', 'sparksql', 'tcl'],
        'backend': ['django', 'flask', 'fastapi', 'spring boot', 'spring', 'celery',
                     'express', 'gin', 'fiber', 'grpc', 'rest', 'graphql', 'node.js'],
        'cloud': ['aws', 'gcp', 'azure', 'ecs', 'eks', 'lambda', 'ec2', 's3', 'rds',
                   'gke', 'bigquery', 'cloud run', 'fargate', 'emr', 'kinesis'],
        'infrastructure': ['kubernetes', 'docker', 'terraform', 'helm', 'istio',
                            'linux', 'nginx', 'ansible'],
        'database': ['kafka', 'redis', 'mongodb', 'postgresql', 'mysql',
                      'elasticsearch', 'snowflake', 'cassandra', 'rabbitmq'],
        'devops': ['ci/cd', 'github actions', 'jenkins', 'argocd', 'gitops',
                    'gitlab ci', 'agile', 'scrum'],
        'observability': ['prometheus', 'grafana', 'datadog', 'opentelemetry'],
        'ai': ['llm', 'rag', 'langchain', 'pytorch', 'tensorflow', 'machine learning',
                'deep learning', 'nlp', 'genai', 'ai', 'ml', 'computer vision'],
    }

    for kw in additions:
        if kw in added:
            continue
        # 找合适的类别行
        target_category = None
        for cat, members in category_hints.items():
            if kw in members:
                target_category = cat
                break

        display_kw = format_kw_display(kw)

        # 在 Skills 行中找到匹配的类别
        appended = False
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if target_category and target_category in line_lower:
                lines[i] = lines[i].rstrip()
                if lines[i].endswith(','):
                    lines[i] += f' {display_kw},'
                else:
                    lines[i] += f', {display_kw}'
                added.add(kw)
                appended = True
                break

        if not appended:
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip().startswith('**'):
                    lines[i] = lines[i].rstrip()
                    if lines[i].endswith(','):
                        lines[i] += f' {display_kw},'
                    else:
                        lines[i] += f', {display_kw}'
                    added.add(kw)
                    break

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# 简历组装
# ═══════════════════════════════════════════════════════════

def choose_summary_source(
    base_id: int,
    sources: dict[str, int],
    all_parsed: dict[int, dict],
) -> int:
    """
    当多数工作段被移植时，自动切换 Summary 来源以保持人设连贯。

    规则:
    - 如果 ≥2 段工作经历来自同一非 base 简历，使用该简历的 Summary
    - 否则保持 base Summary
    """
    from collections import Counter
    source_counts = Counter(sources.values())
    # 找出出现次数最多的 source（排除 base 自身）
    for src_id, count in source_counts.most_common():
        if src_id != base_id and count >= 2:
            # 确认该 source 有 summary
            if all_parsed.get(src_id, {}).get('summary'):
                return src_id
    return base_id


def assemble_resume(
    base_sections: dict[str, str],
    sources: dict[str, int],
    all_parsed: dict[int, dict],
    patched_skills: str,
    base_id: int = 0,
) -> str:
    """
    组装移植后的简历 MD 文本。

    base_sections: base 简历的解析段落
    sources: {'bytedance': 9, 'didi': 15, 'temu': 9}
    all_parsed: 所有简历的解析结果
    patched_skills: 修改后的 Skills 文本
    base_id: base 简历 ID（用于 Summary 自动切换判断）
    """
    parts = []

    # 1. Header（固定）
    parts.append(base_sections['header'])
    parts.append('\n---\n')

    # 2. Summary — 当多数段移植时自动切换
    summary_source_id = choose_summary_source(base_id, sources, all_parsed)
    if summary_source_id != base_id and summary_source_id in all_parsed:
        parts.append(all_parsed[summary_source_id]['summary'])
    else:
        parts.append(base_sections['summary'])
    parts.append('\n---\n')

    # 3. Work Experience
    parts.append('## Work Experience\n')

    # ByteDance
    bt_sections = all_parsed[sources['bytedance']]
    parts.append(bt_sections.get('bytedance', ''))
    parts.append('\n')

    # DiDi
    dd_sections = all_parsed[sources['didi']]
    parts.append(dd_sections.get('didi', ''))
    parts.append('\n')

    # Temu
    tm_sections = all_parsed[sources['temu']]
    parts.append(tm_sections.get('temu', ''))
    parts.append('\n---\n')

    # 4. Skills（patched）
    parts.append(patched_skills)
    parts.append('\n---\n')

    # 5. Education + Additional（固定）
    parts.append(base_sections['education'])
    parts.append('\n')

    return '\n'.join(parts)


# ═══════════════════════════════════════════════════════════
# 端到端移植
# ═══════════════════════════════════════════════════════════

def load_all_resumes() -> dict[int, str]:
    """加载所有 22 份简历原始文本，返回 {id: md_text}"""
    resumes = {}
    for f in sorted(RESUME_DIR.glob('*_Resume.md')):
        # 从文件名提取编号
        m = re.match(r'^(\d+)_', f.name)
        if m:
            rid = int(m.group(1))
            resumes[rid] = f.read_text(encoding='utf-8')
    return resumes


def build_pdf(md_path: Path) -> tuple[bool, int, int]:
    """构建 PDF（渐进压缩）。返回 (success, pages, level)"""
    from md_to_tex import convert_file

    TUNED_TEX.mkdir(parents=True, exist_ok=True)
    TUNED_PDF.mkdir(parents=True, exist_ok=True)

    for level in range(4):
        try:
            tex_path = convert_file(str(md_path), str(TUNED_TEX), level=level)
            cmd = [
                "xelatex", "-interaction=nonstopmode",
                "-output-directory", str(TUNED_PDF),
                str(tex_path),
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True, timeout=60)
            pdf_file = TUNED_PDF / Path(tex_path).with_suffix('.pdf').name
            if pdf_file.exists():
                m = re.search(r'Output written on .+?\((\d+) pages?', result.stdout, re.DOTALL)
                pages = int(m.group(1)) if m else -1
                for ext in ['.aux', '.log', '.out', '.fls', '.fdb_latexmk', '.synctex.gz']:
                    junk = TUNED_PDF / Path(tex_path).with_suffix(ext).name
                    if junk.exists():
                        junk.unlink()
                if pages <= 2:
                    return True, pages, level
        except Exception as e:
            print(f"     ⚠️ PDF 构建失败 (L{level}): {e}")
    return False, pages if 'pages' in dir() else -1, 3


def process_job(
    jd_text: str,
    job_info: dict,
    catalog: list[dict],
    all_parsed: dict[int, dict],
    section_kw: dict,
    dry_run: bool = False,
    enable_llm: bool = True,
    threshold: float = 0.75,
) -> dict:
    """
    对单条 JD 执行完整三层优化流程。

    Layer 1: 确定性段落移植
    Layer 2: Skills 最小增量
    Layer 3: LLM 微创手术（仅当 L1+L2 仍 < threshold 时触发）

    返回结果 dict（始终返回，包含 status 字段）。
    """
    # 1. 原始匹配 — 加入人设亲和度修正
    results = match_all_resumes(jd_text, catalog)
    if not results:
        return {'status': 'no_match', 'job': f"{job_info.get('company','')} · {job_info.get('job_title','')}"}

    # 检测 JD 角色类型并用人设兼容度修正排名
    jd_role = detect_jd_role(jd_text)
    if jd_role:
        for r in results:
            compat = get_persona_compatibility(r['resume_id'], jd_role)
            # 混合分 = 0.8 × 关键词覆盖 + 0.2 × 人设亲和度
            r['persona_compat'] = compat
            r['adjusted_total'] = 0.8 * r['total'] + 0.2 * compat
        results.sort(key=lambda x: x['adjusted_total'], reverse=True)

    base = results[0]
    base_id = base['resume_id']
    original_score = base['total']

    company = job_info.get('company', '未知')
    title = job_info.get('job_title', '未知')
    label = f"{company} · {title}"

    # JD 无法解析（0 个技术词 + 0 个业务词）
    if original_score == 0:
        jd_tech_check = scan_keywords(jd_text, TECH_VOCAB)
        jd_biz_check = scan_keywords(jd_text, BIZ_VOCAB)
        if not jd_tech_check and not jd_biz_check:
            print(f"  ⏭️  {label}: JD 无可识别关键词，跳过")
            return {
                'status': 'unparseable_jd',
                'job': label,
                'resume_label': base['resume_label'],
                'score': 0,
                'page_id': job_info.get('page_id', ''),
            }

    # 已经 ≥ threshold，直接达标
    if original_score >= threshold:
        print(f"  ✅ {label}: 已达标 ({original_score:.0%})")
        return {
            'status': 'already_ok',
            'job': label,
            'resume_label': base['resume_label'],
            'score': round(original_score * 100, 1),
            'page_id': job_info.get('page_id', ''),
        }

    # ── Layer 1: 确定性段落移植 ──
    jd_biz = scan_keywords(jd_text, BIZ_VOCAB)
    jd_tech = scan_keywords(jd_text, TECH_VOCAB)
    cluster = get_best_cluster_for_jd(base_id, jd_biz)

    # 收集 base 简历的全部关键词
    base_tech_all = set()
    for sec in ['summary', 'bytedance', 'didi', 'temu']:
        base_tech_all |= section_kw[base_id][sec]['tech']

    best_sources = {'bytedance': base_id, 'didi': base_id, 'temu': base_id}
    transplant_score = original_score
    transplant_details = {}
    transplant_changes = {}

    if cluster is not None:
        best_sources, transplant_score, transplant_details = find_best_combination(
            jd_text, base_id, cluster, section_kw, catalog
        )
        transplant_changes = {k: v for k, v in best_sources.items() if v != base_id}

    # 计算移植后的关键词集合
    transplanted_tech = section_kw[base_id]['summary']['tech'].copy()
    for sec_name, src_id in best_sources.items():
        transplanted_tech |= section_kw[src_id][sec_name]['tech']

    # ── Layer 2: Skills 最小增量 ──
    patched_skills = patch_skills(
        all_parsed[base_id]['skills'],
        jd_tech,
        base_tech_all,
        transplanted_tech,
        max_additions=3,
    )
    original_skills_kw = scan_keywords(all_parsed[base_id]['skills'], TECH_VOCAB)
    patched_skills_kw = scan_keywords(patched_skills, TECH_VOCAB)
    skills_added = sorted(patched_skills_kw - original_skills_kw)

    # 组装 MD（移植 + Skills 增量）
    new_md = assemble_resume(all_parsed[base_id], best_sources, all_parsed, patched_skills, base_id=base_id)

    # 重新评分（移植 + Skills 后的真实分数）
    current_score, current_details = rescore_md(new_md, jd_text)
    missing_after_transplant = sorted(current_details.get('missing_tech', []))

    layer_reached = 'L1+L2'
    if transplant_changes:
        change_str = ', '.join(f"{k}:{base_id:02d}→{v:02d}" for k, v in transplant_changes.items())
        print(f"  🔄 {label}: {original_score:.0%} → {current_score:.0%} "
              f"(移植: {change_str})", end='')
    else:
        print(f"  📋 {label}: {original_score:.0%} → {current_score:.0%} "
              f"(无移植)", end='')

    if skills_added:
        print(f" Skills+{len(skills_added)}", end='')

    # ── Layer 3: LLM 微创手术 ──
    llm_injected = []
    # 合并 tech + biz 缺失关键词作为注入目标
    missing_biz_list = sorted(current_details.get('missing_biz', []))
    all_missing = missing_after_transplant + [b for b in missing_biz_list if b not in missing_after_transplant]

    # 路由逻辑：按缺失数量决定是否进入 LLM，而非按百分比
    # - 缺失 ≤ MAX_RECOVERABLE (6)：进入 LLM 微创（不管百分比多低）
    # - 缺失 > MAX_RECOVERABLE：标记人工审查
    missing_count = len(all_missing)
    can_recover = missing_count <= MAX_RECOVERABLE and missing_count > 0

    if current_score < threshold and enable_llm and can_recover and not dry_run:
        max_ops = missing_count  # 不再硬编码上限，由缺失数量自然约束（≤6）
        print(f" → LLM 微创...")
        new_md, llm_injected = apply_llm_surgery(
            new_md, all_missing, title, max_surgeries=max_ops,
        )
        if llm_injected:
            # 重新评分
            current_score, current_details = rescore_md(new_md, jd_text)
            missing_after_transplant = sorted(current_details.get('missing_tech', []))
            layer_reached = 'L3'
            print(f"    LLM 注入 {len(llm_injected)} 词 → {current_score:.0%}")

            # LLM 改了 bullet，也需要把对应关键词加到 Skills
            # 重新 patch Skills（允许多加几个，因为 LLM 已注入了经历支撑）
            # 重新解析 Skills 段
            new_lines = new_md.split('\n')
            skills_start_idx = None
            skills_end_idx = None
            for i, line in enumerate(new_lines):
                if re.match(r'^## Skills', line):
                    skills_start_idx = i
                elif skills_start_idx and line.strip() == '---':
                    skills_end_idx = i
                    break
            if skills_start_idx:
                skills_end_idx = skills_end_idx or len(new_lines)
                current_skills_text = '\n'.join(new_lines[skills_start_idx:skills_end_idx])
                current_resume_tech = scan_keywords(new_md, TECH_VOCAB)
                new_patched = patch_skills(
                    current_skills_text, jd_tech,
                    current_resume_tech,  # 现有的关键词
                    current_resume_tech | set(llm_injected),  # 加上 LLM 注入的
                    max_additions=3,
                )
                # 替换 Skills 段
                new_lines[skills_start_idx:skills_end_idx] = new_patched.split('\n')
                new_md = '\n'.join(new_lines)
                # 最终评分
                current_score, current_details = rescore_md(new_md, jd_text)
                missing_after_transplant = sorted(current_details.get('missing_tech', []))
                new_skills_kw = scan_keywords(new_patched, TECH_VOCAB)
                skills_added = sorted(new_skills_kw - original_skills_kw)
    elif current_score < threshold and not can_recover and all_missing:
        print(f" → ⚠️ 缺失 {missing_count} 词，超出可恢复上限 ({MAX_RECOVERABLE})，建议人工评估")
    else:
        print()  # 换行

    # 结果状态
    reached_threshold = current_score >= threshold
    if not reached_threshold and missing_count > MAX_RECOVERABLE:
        status = 'too_many_missing'
    else:
        status = 'ok' if reached_threshold else 'below_threshold'
    flag = "✅" if reached_threshold else "⚠️"

    if current_score > original_score:
        print(f"  {flag} 最终: {original_score:.0%} → {current_score:.0%} "
              f"({layer_reached}, {'达标' if reached_threshold else '未达标'})")
    else:
        print(f"  {flag} 最终: {original_score:.0%} (无提升)")

    all_still_missing = missing_after_transplant
    final_missing_biz = sorted(current_details.get('missing_biz', []))
    if final_missing_biz:
        all_still_missing = all_still_missing + [f"[biz]{b}" for b in final_missing_biz]
    if all_still_missing and not reached_threshold:
        print(f"     仍缺失: {', '.join(all_still_missing)}")

    # ── 保存文件 ──
    if not dry_run and current_score > original_score:
        safe_company = re.sub(r'[^\w\-]', '_', company)
        safe_title = re.sub(r'[^\w\-]', '_', title)[:40]
        filename_base = f"{safe_company}_{safe_title}"

        TUNED_MD.mkdir(parents=True, exist_ok=True)
        md_path = TUNED_MD / f"{filename_base}_Resume.md"
        md_path.write_text(new_md, encoding='utf-8')

        # PDF
        pdf_ok, pdf_pages, pdf_level = build_pdf(md_path)
        if pdf_ok:
            print(f"     📄 PDF ({pdf_pages}p, L{pdf_level})")

        # Metadata
        TUNED_META.mkdir(parents=True, exist_ok=True)
        metadata = {
            'job': label,
            'page_id': job_info.get('page_id', ''),
            'cluster': cluster,
            'layer': layer_reached,
            'original_resume': base['resume_label'],
            'original_score': round(original_score * 100, 1),
            'final_score': round(current_score * 100, 1),
            'sources': {
                'summary': f"{choose_summary_source(base_id, best_sources, all_parsed):02d}" + (" (locked)" if choose_summary_source(base_id, best_sources, all_parsed) == base_id else " (auto-switched)"),
                'bytedance': f"{best_sources['bytedance']:02d}",
                'didi': f"{best_sources['didi']:02d}",
                'temu': f"{best_sources['temu']:02d}",
            },
            'transplant_changes': {k: f"{v:02d}" for k, v in transplant_changes.items()},
            'skills_added': skills_added,
            'llm_injected': llm_injected,
            'keywords_still_missing': missing_after_transplant,
            'files': {
                'md': str(md_path),
                'pdf': str(TUNED_PDF / f"{filename_base}_Resume.pdf") if pdf_ok else None,
            },
        }
        meta_path = TUNED_META / f"{filename_base}.json"
        meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')

    return {
        'status': status,
        'job': label,
        'page_id': job_info.get('page_id', ''),
        'cluster': cluster,
        'layer': layer_reached,
        'resume_label': base['resume_label'],
        'original_score': round(original_score * 100, 1),
        'final_score': round(current_score * 100, 1),
        'transplant_changes': {k: f"{v:02d}" for k, v in transplant_changes.items()},
        'skills_added': skills_added,
        'llm_injected': llm_injected,
        'keywords_still_missing': missing_after_transplant,
    }


# ═══════════════════════════════════════════════════════════
# JD 单条匹配推荐
# ═══════════════════════════════════════════════════════════

def recommend_for_jd(
    jd_text: str,
    catalog: list[dict],
    all_parsed: dict[int, dict],
    section_kw: dict,
    threshold: float = 0.75,
    top_n: int = 5,
) -> list[dict]:
    """
    对输入的 JD 文本进行全量匹配，返回 Top-N 推荐结果。
    每条结果包含：编号、匹配细节、建议操作。
    """
    # 1. JD 关键词解析
    jd_tech = scan_keywords(jd_text, TECH_VOCAB)
    jd_biz = scan_keywords(jd_text, BIZ_VOCAB)
    or_groups = detect_or_groups(jd_text, jd_tech)
    requirements = build_requirements(jd_tech, or_groups)

    # 2. 全量评分
    results = match_all_resumes(jd_text, catalog)
    if not results:
        return []

    # 3. 人设亲和度修正
    jd_role = detect_jd_role(jd_text)
    for r in results:
        compat = get_persona_compatibility(r['resume_id'], jd_role)
        r['persona_compat'] = compat
        r['adjusted_total'] = 0.8 * r['total'] + 0.2 * compat
    results.sort(key=lambda x: x['adjusted_total'], reverse=True)

    # 4. 对 Top-N 做移植模拟，预估最终分数
    top_results = []
    for rank, r in enumerate(results[:top_n], 1):
        rid = r['resume_id']
        base_score = r['total']

        # 移植模拟
        cluster = get_best_cluster_for_jd(rid, jd_biz)
        transplant_gain = 0
        transplant_info = None
        if cluster is not None:
            best_sources, t_score, t_details = find_best_combination(
                jd_text, rid, cluster, section_kw, catalog
            )
            changes = {k: v for k, v in best_sources.items() if v != rid}
            if t_score > base_score and changes:
                transplant_gain = t_score - base_score
                transplant_info = changes

        # Skills 增量模拟
        base_tech_all = set()
        for sec in ['summary', 'bytedance', 'didi', 'temu']:
            base_tech_all |= section_kw[rid][sec]['tech']
        transplanted_tech = section_kw[rid]['summary']['tech'].copy()
        if transplant_info:
            for sec_name, src_id in best_sources.items():
                transplanted_tech |= section_kw[src_id][sec_name]['tech']
        else:
            for sec_name in ['bytedance', 'didi', 'temu']:
                transplanted_tech |= section_kw[rid][sec_name]['tech']

        skills_can_add = sorted(
            (jd_tech - base_tech_all) & transplanted_tech
        )[:3]

        # 预估最终分数（移植 + Skills 后重新评分）
        if transplant_info:
            sources = best_sources
        else:
            sources = {'bytedance': rid, 'didi': rid, 'temu': rid}

        patched_skills = patch_skills(
            all_parsed[rid]['skills'], jd_tech,
            base_tech_all, transplanted_tech, max_additions=3,
        )
        simulated_md = assemble_resume(
            all_parsed[rid], sources, all_parsed, patched_skills, base_id=rid,
        )
        estimated_score, est_details = rescore_md(simulated_md, jd_text)

        # 缺失分析
        missing_tech = sorted(est_details.get('missing_tech', []))
        missing_biz = sorted(est_details.get('missing_biz', []))
        missing_all = missing_tech + [f"[biz]{b}" for b in missing_biz]

        # LLM 可修复判断
        # biz 词注入难度低，按 0.5 权重计入上限
        effective_missing = len(missing_tech) + len(missing_biz) * 0.5
        llm_recoverable = effective_missing <= MAX_RECOVERABLE and len(missing_all) > 0
        estimated_final = estimated_score
        if estimated_score < threshold and llm_recoverable:
            # 保守预估：tech 词只假设 60% 能成功注入，biz 词 90%
            total_req = est_details.get('total_requirements', 1)
            tech_boost = len(missing_tech) * 0.6 * (0.7 / max(total_req, 1))
            biz_boost = len(missing_biz) * 0.9 * (0.3 / max(len(jd_biz), 1)) if jd_biz else 0
            estimated_final = min(1.0, estimated_score + tech_boost + biz_boost)

        # 建议判断
        if estimated_final >= threshold:
            if base_score >= threshold:
                advice = '直接投递'
                advice_detail = '原始匹配已达标，无需修改'
            elif estimated_score >= threshold:
                advice = '建议投递（自动优化可达标）'
                advice_detail = '移植+Skills增量即可达标'
                if transplant_info:
                    advice_detail += f'，移植: {transplant_info}'
                if skills_can_add:
                    advice_detail += f'，Skills+: {skills_can_add}'
            else:
                advice = '建议投递（LLM微调可达标）'
                advice_detail = f'需 LLM 注入 {len(missing_all)} 个关键词: {", ".join(missing_all)}'
        elif estimated_final >= threshold * 0.85:
            advice = '勉强可投（需人工微调）'
            advice_detail = f'自动优化后约 {estimated_final:.0%}，仍缺: {", ".join(missing_all)}'
        else:
            advice = '不建议投递'
            advice_detail = f'技术栈差距较大，缺失: {", ".join(missing_all[:8])}'

        persona_name = RESUME_PERSONA.get(rid, '?')
        # 综合排序分 = 0.5 × 优化后预估 + 0.3 × 人设亲和度 + 0.2 × 原始分
        composite = (0.5 * estimated_final
                     + 0.3 * r.get('persona_compat', 0.5)
                     + 0.2 * base_score)
        top_results.append({
            'rank': rank,  # 后续重排
            'composite': round(composite * 100, 1),
            'resume_id': rid,
            'resume_label': r['resume_label'],
            'persona': persona_name,
            'persona_compat': r.get('persona_compat', 0.5),
            'raw_score': round(base_score * 100, 1),
            'tech_score': round(r['tech_score'] * 100, 1),
            'biz_score': round(r['biz_score'] * 100, 1),
            'adjusted_score': round(r['adjusted_total'] * 100, 1),
            'estimated_after_optimization': round(estimated_score * 100, 1),
            'estimated_with_llm': round(estimated_final * 100, 1),
            'transplant_info': transplant_info,
            'skills_can_add': skills_can_add,
            'missing_tech': missing_tech,
            'missing_biz': missing_biz,
            'advice': advice,
            'advice_detail': advice_detail,
        })

    # 按综合排序分重排
    top_results.sort(key=lambda x: x['composite'], reverse=True)
    for i, r in enumerate(top_results, 1):
        r['rank'] = i

    return top_results


def print_jd_recommendation(jd_text: str, catalog, all_parsed, section_kw, threshold=0.75):
    """打印 JD 匹配推荐报告"""
    # JD 解析摘要
    jd_tech = scan_keywords(jd_text, TECH_VOCAB)
    jd_biz = scan_keywords(jd_text, BIZ_VOCAB)
    or_groups = detect_or_groups(jd_text, jd_tech)
    jd_role = detect_jd_role(jd_text)

    print("=" * 65)
    print("📋 JD 解析")
    print("=" * 65)
    print(f"  技术关键词 ({len(jd_tech)}): {', '.join(sorted(jd_tech))}")
    print(f"  业务方向 ({len(jd_biz)}): {', '.join(sorted(jd_biz))}")
    if or_groups:
        print(f"  OR 关联组: {[sorted(g) for g in or_groups]}")
    print(f"  检测角色类型: {jd_role or '未识别'}")
    print(f"  目标阈值: {threshold:.0%}")
    print()

    # 匹配推荐
    recs = recommend_for_jd(jd_text, catalog, all_parsed, section_kw, threshold)
    if not recs:
        print("❌ 无匹配结果")
        return recs

    print("=" * 65)
    print("🎯 Top-5 简历推荐")
    print("=" * 65)
    for r in recs:
        icon = "✅" if "投递" in r['advice'] and "不建议" not in r['advice'] else "⚠️" if "勉强" in r['advice'] else "❌"
        print(f"\n  {icon} #{r['rank']} 简历 {r['resume_id']:02d} — {r['resume_label']}")
        print(f"     人设: {r['persona']} (亲和度 {r['persona_compat']:.0%})")
        print(f"     原始分: {r['raw_score']}% (tech {r['tech_score']}% | biz {r['biz_score']}%) | 综合 {r['composite']}%")
        print(f"     优化预估: 移植+Skills → {r['estimated_after_optimization']}%"
              f" | +LLM → {r['estimated_with_llm']}%")
        if r['transplant_info']:
            print(f"     移植方案: {r['transplant_info']}")
        if r['skills_can_add']:
            print(f"     Skills 可追加: {', '.join(r['skills_can_add'])}")
        if r['missing_tech'] or r['missing_biz']:
            all_miss = r['missing_tech'] + [f"[biz]{b}" for b in r['missing_biz']]
            print(f"     仍缺失: {', '.join(all_miss)}")
        print(f"     📌 {r['advice']}")
        print(f"        {r['advice_detail']}")

    # 最终建议
    best = recs[0]
    print(f"\n{'=' * 65}")
    print(f"💡 最终建议")
    print(f"{'=' * 65}")
    print(f"  推荐简历: {best['resume_id']:02d} ({best['persona']})")
    print(f"  {best['advice']} — {best['advice_detail']}")
    print()
    return recs


# ═══════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════

def main():
    ap = argparse.ArgumentParser(description="三层简历优化系统（移植 + Skills + LLM 微创）")
    ap.add_argument('--all', action='store_true', help='处理所有 JD')
    ap.add_argument('--dry-run', action='store_true', help='只打印结果，不生成文件（也禁用 LLM）')
    ap.add_argument('--no-llm', action='store_true', help='禁用 LLM 微创手术（仅移植 + Skills）')
    ap.add_argument('--single', type=str, help='处理单条 JD (Notion page ID)')
    ap.add_argument('--jd', type=str, help='输入 JD 文本文件路径，进行匹配推荐')
    ap.add_argument('--jd-text', type=str, help='直接输入 JD 文本（短文本用）')
    ap.add_argument('--threshold', type=float, default=0.75, help='目标阈值 (默认 0.75)')
    ap.add_argument('--update-notion', action='store_true', help='更新 Notion Match Score')
    args = ap.parse_args()

    # 加载冻结词库
    if not FROZEN_CATALOG_PATH.exists():
        print(f"❌ 冻结词库不存在: {FROZEN_CATALOG_PATH}")
        sys.exit(1)
    with open(FROZEN_CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    print(f"📚 加载了 {len(catalog)} 份简历冻结词库")

    # 加载并解析所有简历
    print("📂 解析所有简历段落...")
    raw_resumes = load_all_resumes()
    all_parsed = {rid: parse_sections(text) for rid, text in raw_resumes.items()}
    print(f"   解析了 {len(all_parsed)} 份简历")

    # 预计算段落关键词
    print("🔑 预计算段落级关键词...")
    section_kw = precompute_section_keywords(all_parsed)

    # 验证解析完整性
    for rid, sections in all_parsed.items():
        missing = [k for k in ['header', 'summary', 'bytedance', 'didi', 'temu', 'skills', 'education']
                   if not sections.get(k)]
        if missing:
            print(f"   ⚠️ 简历 {rid:02d} 缺少段落: {', '.join(missing)}")

    # ── --jd / --jd-text 模式：单条 JD 匹配推荐 ──
    if args.jd or args.jd_text:
        if args.jd:
            jd_path = Path(args.jd)
            if not jd_path.exists():
                print(f"❌ JD 文件不存在: {jd_path}")
                sys.exit(1)
            jd_text = jd_path.read_text(encoding='utf-8')
        else:
            jd_text = args.jd_text
        print()
        print_jd_recommendation(jd_text, catalog, all_parsed, section_kw, args.threshold)
        return

    # 获取 Notion JD
    print("\n🔍 从 Notion DB 获取 JD...")
    pages = get_all_pages(NOTION_DB_ID)
    print(f"   找到 {len(pages)} 条记录\n")

    enable_llm = not args.dry_run and not args.no_llm
    all_results = []
    no_jd_count = 0

    for page in pages:
        info = extract_page_info(page)
        if not info['cleaned_jd']:
            no_jd_count += 1
            continue

        if args.single and info['page_id'] != args.single:
            continue

        result = process_job(
            info['cleaned_jd'], info, catalog,
            all_parsed, section_kw,
            dry_run=args.dry_run,
            enable_llm=enable_llm,
            threshold=args.threshold,
        )
        all_results.append(result)

        # 更新 Notion
        if args.update_notion and not args.dry_run:
            score = result.get('final_score', result.get('score', 0))
            resume_label = result.get('resume_label', '')
            if score and resume_label:
                # 构建分析文本
                if result.get('status') == 'already_ok':
                    analysis = f"原始匹配达标: {score}%"
                else:
                    parts = [f"优化后: {result.get('original_score',0)}% → {score}%"]
                    if result.get('layer'):
                        parts.append(f"层级: {result['layer']}")
                    if result.get('transplant_changes'):
                        parts.append(f"移植: {json.dumps(result['transplant_changes'], ensure_ascii=False)}")
                    if result.get('skills_added'):
                        parts.append(f"Skills新增: {', '.join(result['skills_added'])}")
                    if result.get('llm_injected'):
                        parts.append(f"LLM注入: {', '.join(result['llm_injected'])}")
                    if result.get('keywords_still_missing'):
                        parts.append(f"仍缺失: {', '.join(result['keywords_still_missing'])}")
                    analysis = '\n'.join(parts)

                update_notion_fields(info['page_id'], resume_label, score / 100.0, analysis)
                time.sleep(0.35)

    # ── 汇总 ──
    ok_count = sum(1 for r in all_results if r.get('status') == 'already_ok')
    improved_count = sum(1 for r in all_results if r.get('status') == 'ok' and r.get('status') != 'already_ok')
    below_count = sum(1 for r in all_results if r.get('status') == 'below_threshold')
    too_many_count = sum(1 for r in all_results if r.get('status') == 'too_many_missing')

    # 计算最终达标率
    with_jd = [r for r in all_results if r.get('status') != 'no_match']
    above_threshold = [r for r in with_jd
                       if (r.get('final_score', r.get('score', 0)) or 0) >= args.threshold * 100]

    print(f"\n{'='*60}")
    print(f"📊 全库汇总:")
    print(f"   总 JD: {len(pages)} (有JD: {len(with_jd)}, 空JD: {no_jd_count})")
    print(f"   ≥{args.threshold:.0%} 达标: {len(above_threshold)}/{len(with_jd)} "
          f"({len(above_threshold)/len(with_jd)*100:.1f}%)" if with_jd else "")
    print(f"   原始达标: {ok_count}")
    print(f"   优化达标: {improved_count}")
    print(f"   仍未达标: {below_count}")
    if too_many_count:
        print(f"   缺失过多(需人工): {too_many_count}")

    if below_count + too_many_count > 0:
        print(f"\n   ⚠️ 未达标 JD:")
        for r in all_results:
            if r.get('status') in ('below_threshold', 'too_many_missing'):
                score = r.get('final_score', r.get('original_score', 0))
                tag = " [缺失过多]" if r.get('status') == 'too_many_missing' else ""
                print(f"      - {r['job']} ({score}%, 缺: {', '.join(r.get('keywords_still_missing', [])[:5])}){tag}")

    # 生成报告
    report_path = TUNED_DIR / "transplant_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    _generate_report(all_results, report_path, args.threshold)
    print(f"\n📄 报告: {report_path}")


def _generate_report(all_results: list, output_path: Path, threshold: float):
    """生成全量汇总报告"""
    lines = [
        "# 简历优化汇总报告",
        "",
        f"> 生成时间：{time.strftime('%Y-%m-%d %H:%M')}",
        f"> 三层策略：确定性段落移植 → Skills 增量 → LLM 微创手术",
        f"> 目标阈值：{threshold:.0%}",
        "",
        "---",
        "",
    ]

    # 分类
    already_ok = [r for r in all_results if r.get('status') == 'already_ok']
    optimized_ok = [r for r in all_results if r.get('status') == 'ok' and r.get('final_score')]
    below = [r for r in all_results if r.get('status') == 'below_threshold']
    too_many = [r for r in all_results if r.get('status') == 'too_many_missing']

    lines.append(f"## 统计\n")
    lines.append(f"- 原始达标: {len(already_ok)}")
    lines.append(f"- 优化达标: {len(optimized_ok)}")
    lines.append(f"- 仍未达标: {len(below)}")
    if too_many:
        lines.append(f"- 缺失过多(需人工): {len(too_many)}")
    total_with_jd = len(already_ok) + len(optimized_ok) + len(below)
    if total_with_jd:
        pct = (len(already_ok) + len(optimized_ok)) / total_with_jd * 100
        lines.append(f"- 总达标率: {pct:.1f}%")
    lines.append("")

    if optimized_ok:
        lines.append(f"## 优化达标 ({len(optimized_ok)} 条)\n")
        for r in optimized_ok:
            lines.append(f"### {r['job']}")
            lines.append("")
            lines.append(f"- **简历**: {r.get('resume_label', '?')}")
            lines.append(f"- **分数**: {r.get('original_score', 0)}% → {r.get('final_score', 0)}%")
            lines.append(f"- **层级**: {r.get('layer', '?')}")
            if r.get('transplant_changes'):
                lines.append(f"- **移植**: {json.dumps(r['transplant_changes'], ensure_ascii=False)}")
            if r.get('skills_added'):
                lines.append(f"- **Skills新增**: {', '.join(r['skills_added'])}")
            if r.get('llm_injected'):
                lines.append(f"- **LLM注入**: {', '.join(r['llm_injected'])}")
            lines.append("")

    all_below = below + too_many
    if all_below:
        lines.append(f"## 仍未达标 ({len(all_below)} 条)\n")
        for r in all_below:
            lines.append(f"### {r['job']}")
            lines.append("")
            lines.append(f"- **简历**: {r.get('resume_label', '?')}")
            lines.append(f"- **分数**: {r.get('original_score', 0)}% → {r.get('final_score', 0)}%")
            if r.get('status') == 'too_many_missing':
                lines.append(f"- **状态**: 缺失关键词过多，建议人工评估")
            if r.get('keywords_still_missing'):
                lines.append(f"- **缺失**: {', '.join(r['keywords_still_missing'])}")
            lines.append("")

    output_path.write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()
