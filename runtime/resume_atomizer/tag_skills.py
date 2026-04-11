#!/usr/bin/env python3
"""
tag_skills.py — Phase 4: 基于关键词的自动技能标注。

读取 atom_store.json + skill_tree.json，为每个 atom 分配 skill_ids。
使用 bold keywords + 正文关键词匹配的方式自动标注。

Usage:
    python3 tag_skills.py
"""

import json
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent
ATOM_STORE = ROOT / "atom_store.json"
SKILL_TREE = ROOT / "skill_tree.json"


def build_skill_lookup(tree: dict) -> dict:
    """构建 skill_name → (type, domain, subdomain, skill_id) 的查找表"""
    lookup = {}
    # Hard skills
    for domain in tree["hard_skill_tree"]:
        for sd in domain["sub_domains"]:
            for skill in sd["skills"]:
                skill_id = f"hard.{_slug(domain['domain'])}.{_slug(sd['name'])}.{_slug(skill)}"
                lookup[skill.lower()] = {
                    "skill_id": skill_id,
                    "skill_name": skill,
                    "type": "hard",
                    "domain": domain["domain"],
                    "subdomain": sd["name"],
                }
    # Soft skills
    for cluster in tree["soft_skill_clusters"]:
        for skill in cluster["skills"]:
            skill_id = f"soft.{_slug(cluster['cluster_name'])}.{_slug(skill)}"
            lookup[skill.lower()] = {
                "skill_id": skill_id,
                "skill_name": skill,
                "type": "soft",
                "domain": cluster["cluster_name"],
                "subdomain": "",
            }
    return lookup


def build_keyword_patterns(lookup: dict) -> list[tuple[re.Pattern, dict]]:
    """为每个技能构建匹配 pattern，按长度降序排列（长的先匹配）"""
    patterns = []
    for key, info in sorted(lookup.items(), key=lambda x: -len(x[0])):
        # 构建正则：处理特殊字符
        escaped = re.escape(key)
        # 允许一些变体
        escaped = escaped.replace(r'\ ', r'[\s/\-]?')
        # 词边界
        pat = re.compile(r'(?<![a-zA-Z])' + escaped + r'(?![a-zA-Z])', re.IGNORECASE)
        patterns.append((pat, info))
    return patterns


# 额外的别名映射（简历中出现的词 → 技能树中的正式名称）
ALIASES = {
    # 编程语言
    "python": "python", "java": "java", "go": "go", "c": "c", "c++": "c++",
    "c++11": "c++", "c++14": "c++", "c++17": "c++",
    "golang": "go", "javascript": "javascript", "typescript": "typescript",
    "rust": "rust", "scala": "scala", "kotlin": "kotlin", "ruby": "ruby",
    "swift": "swift", "objective-c": "objective-c", "bash": "shell/bash",
    "shell": "shell/bash", "c#": "c#", "sql": "sql",
    "hiveql": "hiveql", "hive sql": "hiveql", "sparksql": "sparksql",
    "spark sql": "sparksql", "assembly": "assembly", "cuda": "cuda",
    "solidity": "solidity", "tcl": "tcl", "r": "r", "perl": "perl",
    "matlab": "matlab", "html/css": "html/css", "html": "html/css",

    # 框架
    "react": "react", "angular": "angular", "vue": "vue.js", "vue.js": "vue.js",
    "next.js": "next.js", "node.js": "node.js", "express": "express.js",
    "spring boot": "spring", "spring": "spring", "fastapi": "fastapi",
    "django": "django", "flask": "flask", ".net": ".net",
    "tailwindcss": "tailwindcss", "ant design": "ant design",
    "redux": "redux", "react native": "react native",
    "jetpack compose": "jetpack compose", "swiftui": "swiftui",

    # 后端/API
    "rest": "rest/restful", "restful": "rest/restful", "rest api": "rest/restful",
    "grpc": "grpc", "graphql": "graphql", "microservices": "microservices",
    "microservice": "microservices",
    "kafka": "kafka", "rabbitmq": "rabbitmq",
    "protocol buffers": "protocol buffers", "protobuf": "protocol buffers",

    # 数据库
    "postgresql": "postgresql", "postgres": "postgresql",
    "mysql": "mysql", "sqlite": "sqlite", "mongodb": "mongodb",
    "redis": "redis", "cassandra": "cassandra", "dynamodb": "dynamodb",
    "elasticsearch": "elasticsearch", "bigquery": "bigquery",
    "snowflake": "snowflake", "databricks": "databricks",
    "redshift": "redshift", "spanner": "spanner",
    "google cloud spanner": "spanner",

    # 数据处理
    "spark": "spark", "apache spark": "spark", "pyspark": "spark",
    "hadoop": "hadoop", "airflow": "airflow", "apache airflow": "airflow",
    "etl": "etl", "dbt": "dbt", "pandas": "pandas",
    "sqlalchemy": "sqlalchemy",

    # 云
    "aws": "aws", "gcp": "gcp", "azure": "azure",
    "eks": "aws", "ecs": "aws", "s3": "aws", "lambda": "aws",
    "gke": "gcp", "bigquery": "gcp",

    # 容器
    "docker": "docker", "kubernetes": "kubernetes", "k8s": "kubernetes",
    "helm": "helm", "istio": "istio", "service mesh": "service mesh",

    # IaC
    "terraform": "terraform", "ansible": "ansible",
    "infrastructure as code": "infrastructure as code",

    # CI/CD
    "ci/cd": "ci/cd", "jenkins": "jenkins",
    "github actions": "github actions", "gitlab ci": "gitlab ci",
    "argocd": "argocd", "flux cd": "flux cd",
    "git": "git",

    # 监控
    "prometheus": "prometheus", "grafana": "grafana",
    "opentelemetry": "opentelemetry", "datadog": "datadog",
    "nsight systems": "nsight systems", "nsight compute": "nsight compute",
    "monitoring": "monitoring", "observability": "observability",
    "sre": "sre",

    # OS
    "linux": "linux", "nginx": "nginx",

    # AI/ML
    "machine learning": "machine learning", "deep learning": "deep learning",
    "reinforcement learning": "reinforcement learning",
    "pytorch": "pytorch", "tensorflow": "tensorflow",
    "tensorflow lite": "tensorflow lite",
    "scikit-learn": "scikit-learn", "numpy": "numpy",
    "nlp": "nlp", "llm": "llm", "generative ai": "generative ai",
    "transformers": "transformers", "rag": "rag",
    "langchain": "langchain", "langgraph": "langgraph",
    "prompt engineering": "prompt engineering", "ai agents": "ai agents",
    "ai agent": "ai agents",
    "computer vision": "computer vision", "opencv": "opencv",
    "image processing": "image processing", "video processing": "video processing",
    "fine-tuning": "fine-tuning", "mlops": "mlops",
    "recommendation systems": "recommendation systems",
    "mcp": "mcp", "multi-model routing": "multi-model routing",
    "hooks": "hooks/middleware", "confidence scoring": "confidence scoring",
    "pydantic": "pydantic",

    # 安全
    "tls": "tls/ssl", "ssl": "tls/ssl", "mtls": "mtls",
    "oauth": "oauth/saml", "oauth 2.0": "oauth/saml",
    "iam": "iam", "zero trust": "zero trust",
    "cybersecurity": "cybersecurity", "penetration testing": "penetration testing",
    "hsm": "hsm", "cloudhsm": "hsm",
    "mpc": "mpc", "ecdsa": "ecdsa/eddsa",
    "kms": "kms", "merkle": "merkle proofs",
    "kyc": "kyc/aml", "aml": "kyc/aml",
    "sox": "sox", "pipl": "pipl", "ofac": "ofac", "cnbv": "cnbv",
    "dlp": "dlp", "content provenance": "content provenance",
    "devsecops": "devsecops", "sast": "sast", "semgrep": "semgrep",
    "hashicorp vault": "hashicorp vault",
    "mitre att&ck": "mitre att&ck", "mitre": "mitre att&ck",
    "vulnerability management": "vulnerability management",
    "incident response": "incident response",
    "threat detection": "threat detection",
    "anomaly detection": "anomaly detection",

    # 嵌入式
    "embedded systems": "embedded systems", "rtos": "rtos",
    "firmware": "firmware", "device drivers": "device drivers",
    "sensors": "sensors", "sensor fusion": "sensor fusion",
    "kalman filter": "kalman filter", "dsp": "dsp",
    "imu": "imu",
    "arm64": "arm64", "x86": "x86",
    "android os": "android os", "embedded linux": "embedded linux",
    "adb": "adb", "eda": "eda",
    "driver development": "driver development",
    "kernel": "kernel", "virtualization": "virtualization",
    "compilers": "compilers", "compiler": "compilers",
    "llvm": "llvm", "loop tiling": "loop tiling",
    "vectorization": "vectorization",
    "cmake": "cmake",
    "distributed systems": "distributed systems",
    "concurrency": "concurrency",

    # HPC
    "mpi": "mpi", "openmp": "openmp", "slurm": "slurm",
    "cuda kernel": "cuda kernel optimization",
    "roofline analysis": "roofline analysis",
    "neon simd": "neon simd", "simd": "neon simd",

    # 平台
    "ios": "ios", "android": "android",
    "mobile development": "mobile development",
    "unity": "unity engine", "unity engine": "unity engine",
    "stablecoin": "stablecoin", "erc-20": "erc-20",
    "proof-of-reserve": "proof-of-reserve",
    "wallet infrastructure": "wallet infrastructure",
    "smart contract": "smart contracts",
    "blockchain": "blockchain/crypto",
    "gpu programming": "gpu programming",

    # 测试
    "unit testing": "unit testing", "integration testing": "integration testing",
    "test automation": "test automation", "selenium": "selenium",
    "google test": "google test", "gtest": "google test",
    "gmock": "google test",
    "pytest": "pytest", "appium": "appium",
    "xcuitest": "xcuitest", "espresso": "espresso",
    "regression testing": "regression testing",
    "performance profiling": "performance profiling",
    "profiling": "performance profiling",
    "simulation": "simulation harnesses",
    "test planning": "test planning", "test plan": "test planning",
    "functional testing": "functional testing",
    "build automation": "build automation",

    # 企业工具 & 补充
    "salesforce": "salesforce", "salesforce cpq": "salesforce",
    "zuora": "zuora", "zuora billing": "zuora", "zuora revenue": "zuora",
    "netsuite": "netsuite", "mulesoft": "mulesoft", "revpro": "revpro",
    "openapi": "rest/restful",
    "slo": "monitoring", "chaos engineering": "sre",
    "canary deployment": "ci/cd", "canary deployments": "ci/cd",
    "mlflow": "mlops", "data pipeline": "etl",
    "responsive design": "html/css", "css": "html/css",
    "virtual machine": "virtualization", "virtualbox": "virtualization",
    "hypervisor": "virtualization", "virtio": "virtualization",
    "grub": "linux", "uefi": "linux",
    "wallet": "wallet infrastructure",
    "debugging": "performance profiling",
    "root cause analysis": "performance profiling",
    "quote-to-cash": "salesforce",

    # 软技能
    "agile": "agile/scrum", "scrum": "agile/scrum",
    "cross-functional": "cross-functional collaboration",
    "teamwork": "teamwork", "mentoring": "mentoring",
    "code review": "code review", "code reviews": "code review",
    "design review": "design review", "design reviews": "design review",
    "sdlc": "sdlc", "technical consulting": "technical consulting",
    "weiqi": "weiqi",
}


def tag_atom(atom: dict, lookup: dict) -> list[str]:
    """为单个 atom 标注 skill_ids"""
    text = atom['text']
    keywords = atom.get('keywords', [])
    matched_skills = set()

    # 1. 先匹配 bold keywords（高权重）
    for kw in keywords:
        kw_lower = kw.lower().strip()
        if kw_lower in ALIASES:
            canonical = ALIASES[kw_lower]
            if canonical in lookup:
                matched_skills.add(lookup[canonical]['skill_id'])

    # 2. 正文全文匹配 ALIASES（带词边界检查）
    text_lower = text.lower()
    # 只通过 bold keyword 匹配、不做全文扫描的别名（太短，全文匹配误报率极高）
    KEYWORD_ONLY_ALIASES = {'c'}
    # 需要词边界保护的短别名（≤3字符或容易误匹配的词）
    SHORT_ALIASES_NEEDING_BOUNDARY = {
        'r', 'go', 'c#', 'sql', 'git', 'dbt', 'dsp', 'imu', 'eda', 'mpi',
        'dlp', 'iam', 'kms', 'hsm', 'mpc', 'ios', 'sre', 'etl', 'hpc',
        'adb', 'tls', 'ssl', 'qa', 'slo', 'css', 'api',
    }
    for alias, canonical in sorted(ALIASES.items(), key=lambda x: -len(x[0])):
        if alias in KEYWORD_ONLY_ALIASES:
            continue  # 只通过 bold keyword 匹配
        if alias in SHORT_ALIASES_NEEDING_BOUNDARY:
            # 使用正则词边界，避免 "r" 匹配 "process"、"go" 匹配 "going"
            pat = re.compile(r'(?<![a-zA-Z])' + re.escape(alias) + r'(?![a-zA-Z])', re.IGNORECASE)
            if pat.search(text_lower):
                if canonical in lookup:
                    matched_skills.add(lookup[canonical]['skill_id'])
        else:
            if alias in text_lower:
                if canonical in lookup:
                    matched_skills.add(lookup[canonical]['skill_id'])

    return sorted(matched_skills)


def infer_angle_tags(atom: dict) -> list[str]:
    """根据 skill_ids 推断 atom 的适用方向"""
    text_lower = atom['text'].lower()
    tags = set()

    skill_domain_map = {
        'ai': ['ai & machine learning', 'nlp', 'llm', 'rag', 'langchain', 'ml', 'prompt'],
        'backend': ['backend', 'microservice', 'grpc', 'rest', 'api', 'spring', 'fastapi'],
        'frontend': ['react', 'next.js', 'typescript', 'frontend', 'ui', 'tailwind', 'css'],
        'devops': ['ci/cd', 'github actions', 'docker', 'kubernetes', 'terraform', 'helm', 'argocd'],
        'security': ['security', 'threat', 'vulnerability', 'dlp', 'sast', 'zero trust', 'mtls'],
        'data': ['etl', 'pipeline', 'spark', 'hive', 'sql', 'airflow', 'data warehouse'],
        'embedded': ['embedded', 'arm64', 'sensor', 'firmware', 'driver', 'simd', 'imu'],
        'hpc': ['cuda', 'mpi', 'openmp', 'roofline', 'gpu', 'hpc', 'llvm', 'compiler'],
        'fintech': ['payment', 'stablecoin', 'blockchain', 'wallet', 'treasury', 'settlement'],
        'mobile': ['ios', 'android', 'mobile', 'unity', 'appium', 'xcuitest'],
        'qa': ['test', 'qa', 'pytest', 'regression', 'profiling', 'verification'],
        'platform': ['platform', 'sre', 'reliability', 'observability', 'prometheus'],
    }

    for tag, keywords in skill_domain_map.items():
        if any(kw in text_lower for kw in keywords):
            tags.add(tag)

    return sorted(tags)


def detect_universal(atoms: list[dict]) -> None:
    """标记 universal atoms：出现在 10+ 份简历的 cluster 中的 atoms"""
    # 按 parent_group_id 分组
    groups = defaultdict(list)
    for a in atoms:
        groups[a['parent_group_id']].append(a)

    for gid, group_atoms in groups.items():
        all_rids = set()
        for a in group_atoms:
            all_rids.update(a['source_resumes'])
        if len(all_rids) >= 10:
            for a in group_atoms:
                a['universal'] = True


def _slug(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')[:30]


def main():
    store = json.loads(ATOM_STORE.read_text(encoding='utf-8'))
    tree = json.loads(SKILL_TREE.read_text(encoding='utf-8'))

    lookup = build_skill_lookup(tree)
    print(f"技能查找表: {len(lookup)} entries")

    # 标注每个 atom
    tagged = 0
    empty = 0
    for atom in store['atoms']:
        atom['skill_ids'] = tag_atom(atom, lookup)
        atom['angle_tags'] = infer_angle_tags(atom)
        if atom['skill_ids']:
            tagged += 1
        else:
            empty += 1

    # 标注 summary atoms (对每个 variant)
    for sa in store['summary_atoms']:
        all_skill_ids = set()
        for v in sa.get('variants', []):
            temp_atom = {'text': v['text'], 'keywords': v.get('keywords', [])}
            sids = tag_atom(temp_atom, lookup)
            v['skill_ids'] = sids
            all_skill_ids.update(sids)
        sa['skill_ids'] = sorted(all_skill_ids)

    # 标记 universal
    detect_universal(store['atoms'])

    # 写回
    ATOM_STORE.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding='utf-8')

    # 统计
    universal_count = sum(1 for a in store['atoms'] if a.get('universal'))
    avg_skills = sum(len(a['skill_ids']) for a in store['atoms']) / len(store['atoms'])
    print(f"\n✅ 标注完成:")
    print(f"   有标注: {tagged}, 无标注: {empty}")
    print(f"   平均每 atom {avg_skills:.1f} 个技能")
    print(f"   Universal atoms: {universal_count}")

    # 显示无标注的 atoms
    if empty > 0:
        print(f"\n⚠️ 无标注 atoms ({empty}):")
        for a in store['atoms']:
            if not a['skill_ids']:
                print(f"  {a['atom_id']}: {a['text'][:100]}...")


if __name__ == "__main__":
    main()
