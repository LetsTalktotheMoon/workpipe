#!/usr/bin/env python3
"""
generate_resume.py — Phase B: JD → 自动生成 tailored resume。

Pipeline:
  1. JD Parser → 提取 tech, domain, role, seniority
  2. Tech Profile 补全 → 稀疏 JD 自动扩展技术栈
  3. Atom Selector → 从 332 catoms 中选 15-20 最相关条目
  4. Assembler → 组装为 Markdown 格式简历
  5. LLM Polish → 生成 Summary + 微调语气（可选）
  6. PDF Builder → MD → LaTeX → PDF（可选）

Usage:
    python3 generate_resume.py --jd jd.txt --profile A
    python3 generate_resume.py --jd-text "We are looking for..." -p B
    python3 generate_resume.py --jd jd.txt --dry-run
"""

from __future__ import annotations

import argparse
import json
import subprocess
import glob
import os
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
PROJECT_ROOT = ROOT.parent

CONSOLIDATED_STORE = ROOT / "consolidated_atom_store.json"
PROFILES_PATH = PROJECT_ROOT / "profiles.json"
TECH_PROFILE = ROOT / "tech_profile_matrix.json"
DOMAIN_TAXONOMY = ROOT / "domain_taxonomy.json"
PROJECT_MAPPING = ROOT / "project_mapping.json"
OUTPUT_DIR = ROOT / "output"
STAGING_DIR = Path(__file__).parent / 'staging'
STAGING_FILE = STAGING_DIR / 'pending_review.json'
_PROJECT_TITLE_LOOKUP = None

REGISTRY_DIR = Path(__file__).parent / 'registry'
TARGET_COMPANY_LOCKS_FILE = REGISTRY_DIR / 'target_company_locks.json'


# ═══════════════════════════════════════════════════════════
# 复用的词表和常量（来自 transplant_resume.py / notion_match.py）
# ═══════════════════════════════════════════════════════════

# JD 角色信号（简化版，来自 transplant_resume.py）
JD_ROLE_SIGNALS = {
    'mobile':       ['mobile', 'android', 'ios', 'swift', 'kotlin', 'jetpack', 'react native', 'flutter'],
    'frontend':     ['frontend', 'ui engineer', 'web engineer', 'design system', 'react', 'angular', 'vue'],
    'qa_sdet':      ['qa', 'sdet', 'test engineer', 'quality', 'test automation', 'selenium', 'appium'],
    'hpc_compiler': ['hpc', 'compiler', 'cuda', 'gpu', 'llvm', 'mpi', 'openmp'],
    'security':     ['security engineer', 'threat', 'vulnerability', 'siem', 'dlp', 'penetration', 'soc'],
    'ai_genai':     ['genai', 'generative ai', 'llm', 'rag', 'ai agent', 'prompt engineering', 'langchain',
                     'machine learning', 'ml engineer', 'ai/ml', 'deep learning', 'pytorch', 'tensorflow'],
    'backend':      ['backend', 'distributed systems', 'microservices', 'grpc', 'system design'],
    'cloud_infra':  ['infrastructure', 'platform engineer', 'cloud engineer', 'terraform', 'kubernetes'],
    'devops':       ['devops', 'sre', 'site reliability', 'ci/cd'],
    'data':         ['data engineer', 'big data', 'spark', 'airflow', 'etl', 'data pipeline', 'analytics'],
    'embedded':     ['embedded', 'firmware', 'iot', 'sensor', 'rtos'],
    'fintech':      ['fintech', 'payment', 'blockchain', 'web3', 'smart contract', 'billing'],
}

# 技术词标准化别名
TECH_ALIASES = {
    'k8s': 'kubernetes', 'kube': 'kubernetes', 'tf': 'terraform',
    'py': 'python', 'js': 'javascript', 'ts': 'typescript',
    'pg': 'postgresql', 'postgres': 'postgresql', 'mongo': 'mongodb',
    'gha': 'github actions', 'gh actions': 'github actions',
    'ml': 'machine learning', 'dl': 'deep learning',
    'llms': 'llm', 'genai': 'generative ai',
    'rest api': 'rest', 'restful': 'rest',
    'ci/cd': 'CI/CD', 'cicd': 'CI/CD',
    'android sdk': 'android',
    'jetpack compose': 'jetpack',
    'xcuitest': 'ios',
    'espresso': 'android',
}

SENIORITY_BLOCKLIST = {
    'exp-bytedance': [
        'led the architecture', 'owned the entire', 'drove cross-org',
        'drove company-wide', 'spearheaded org-level', 'managed a team of',
        'as tech lead', 'as architect', 'reporting to vp',
    ],
    'exp-temu': [
        'led team', 'drove business strategy', 'spearheaded',
        'managed a team', 'as tech lead', 'as architect',
    ],
    'academic': [
        'production traffic', 'million daily active users', 'enterprise revenue',
        'company-wide adoption', 'served millions', '商业量产',
        '千万级真实流量', '创造企业营收',
    ],
}

KEEP_BOLD = {
    'bytedance/tiktok', 'didi', 'temu', 'agile', 'scrum', 'sdlc',
    'security', 'authentication', 'authorization', 'compliance',
    'risk analytics', 'transaction', 'payment', 'database',
    'data structures', 'algorithms', 'multi-threaded',
    'object-oriented design', 'business requirements',
    'data provenance', 'anomaly', 'http', 'saas',
    'synthetic data generation', 'ai/ml', 'responsive design',
    'component library', 'design-engineering bridge',
    'backend', 'frontend', 'mobile', 'reliability', 'scalability',
    'large-scale', 'distributed',
}

LEAD_VERB_NORMALIZATION = {
    'Enforced': 'Standardized',
    'Executed': 'Computed',
    'Extracted': 'Curated',
    'Performed': 'Diagnosed',
    'Profiled': 'Diagnosed',
    'Provisioned': 'Configured',
    'Wrote': 'Authored',
    'Conducted': 'Diagnosed',
    'Defined': 'Designed',
    'Redesigned': 'Refactored',
    'Validated': 'Achieved',
}


# ═══════════════════════════════════════════════════════════
# 1. JD Parser
# ═══════════════════════════════════════════════════════════

def parse_jd(jd_text: str) -> dict:
    jd_lower = jd_text.lower()
    role_scores = {}
    for role, signals in JD_ROLE_SIGNALS.items():
        role_scores[role] = sum(1 for s in signals if s in jd_lower)
    best_role = max(role_scores, key=role_scores.get)
    role_type = best_role if role_scores[best_role] >= 2 else 'backend'

    seniority = detect_seniority(jd_text)

    req_markers = ['required', 'must have', 'you will use', 'qualifications']
    n2h_markers = ['nice to have', 'bonus', 'plus', 'preferred', 'ideally']
    idx_n2h = len(jd_lower)
    for m in n2h_markers:
        idx = jd_lower.find(m)
        if idx != -1 and idx < idx_n2h:
            idx_n2h = idx
            
    req_text = jd_text[:idx_n2h]
    n2h_text = jd_text[idx_n2h:] if idx_n2h < len(jd_text) else ""
    
    tech_all_req = extract_tech_from_jd(req_text)
    tech_nice_to_have = extract_tech_from_jd(n2h_text)
    
    tech_or_groups = []
    import re as regex
    or_matches = regex.findall(r'(\b\w[\w\s+#.]*?)\s+or\s+(\w[\w\s+#.]*?\b)', req_text, regex.IGNORECASE)
    slash_matches = regex.findall(r'(\b\w+)/(\w+\b)', req_text)
    
    for m1, m2 in or_matches + slash_matches:
        t1, t2 = m1.strip(), m2.strip()
        t1_norm = TECH_ALIASES.get(t1.lower(), t1)
        t2_norm = TECH_ALIASES.get(t2.lower(), t2)
        if t1_norm in tech_all_req and t2_norm in tech_all_req:
            tech_or_groups.append({t1_norm, t2_norm})
            tech_all_req.discard(t1_norm)
            tech_all_req.discard(t2_norm)

    domain_taxonomy = json.loads(DOMAIN_TAXONOMY.read_text(encoding='utf-8'))
    biz_domains = []
    for domain_id, info in domain_taxonomy['domains'].items():
        score = sum(1 for kw in info['keywords'] if kw in jd_lower)
        if score >= 2:
            biz_domains.append(domain_id)
    if not biz_domains:
        biz_domains = ['backend_distributed']

    return {
        'role_type': role_type,
        'seniority': seniority,
        'tech_required': tech_all_req,
        'tech_or_groups': tech_or_groups,
        'tech_nice_to_have': tech_nice_to_have,
        'biz_domains': biz_domains,
        'raw_text': jd_text,
    }


def detect_seniority(jd_text: str) -> str:
    """从 JD 提取职级"""
    text = jd_text.lower()

    # 检查明确的职级词
    if any(w in text for w in ['intern', 'internship', 'co-op']):
        return 'intern'
    if any(w in text for w in ['new grad', 'new graduate', 'entry level', 'entry-level', 'junior']):
        return 'new_grad'
    if any(w in text for w in ['staff', 'principal', 'lead', 'architect']):
        return 'senior_5y_plus'
    if any(w in text for w in ['senior', 'sr.']):
        return 'senior_5y_plus'

    # 检查 YOE 要求
    yoe_match = re.search(r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)', text)
    if yoe_match:
        yoe = int(yoe_match.group(1))
        if yoe <= 1:
            return 'new_grad'
        elif yoe <= 3:
            return 'mid_1_3y'
        else:
            return 'senior_5y_plus'

    return 'mid_1_3y'  # 默认


def extract_tech_from_jd(jd_text: str) -> set[str]:
    """从 JD 中提取技术关键词"""
    # 常见技术名称模式
    tech_patterns = [
        r'\b(Python|Java|Go|Golang|C\+\+|C#|C|Rust|Ruby|Scala|Kotlin|Swift|PHP)\b',
        r'\b(TypeScript|JavaScript|SQL|HiveQL|SparkSQL|Bash|Shell)\b',
        r'\b(React|Vue|Angular|Next\.js|Svelte|Node\.js)\b',
        r'\b(Spring Boot|FastAPI|Django|Flask|Express|Rails)\b',
        r'\b(Docker|Kubernetes|Terraform|Helm|Ansible|ArgoCD|Istio)\b',
        r'\b(Kafka|Redis|PostgreSQL|MySQL|MongoDB|DynamoDB|Cassandra|Elasticsearch)\b',
        r'\b(AWS|GCP|Azure|S3|EC2|Lambda|BigQuery|Redshift)\b',
        r'\b(PyTorch|TensorFlow|LLM|BERT|GPT|RAG|LangChain|LangGraph|Hugging Face)\b',
        r'\b(gRPC|REST|GraphQL|Protobuf|WebSocket)\b',
        r'\b(Prometheus|Grafana|Datadog|OpenTelemetry|Splunk|ELK)\b',
        r'\b(GitHub Actions|GitLab CI|Jenkins|CircleCI)\b',
        r'\b(Spark|Airflow|Hive|Flink|dbt|Presto|Trino)\b',
        r'\b(CUDA|MPI|OpenMP|LLVM)\b',
        r'\b(Selenium|Appium|Cypress|Playwright|pytest|JUnit|Jest)\b',
        r'\b(TLS|mTLS|OAuth|OIDC|SAML|JWT)\b',
        r'\b(Microservices|CI/CD|ETL|MLOps|DevOps|SRE)\b',
        r'\b(Android|iOS|Jetpack|MVVM|Fastlane|SQLite|Android Studio|Xcode|Gradle|Jenkins)\b',
        r'\b(Linux|Git|ARM|RTOS|CMake|CUDA|MPI|OpenMP|LLVM)\b',
        r'\b(Embedded Linux|Device Drivers|Sensor Fusion|Firmware Design|System Architecture|Performance Optimization)\b',
        r'\b(Security Architecture|Threat Modeling|Zero Trust|Compliance|Incident Response|Security Operations|Risk Assessment|SOC|Red Team|SIEM)\b',
        r'\b(Payment Architecture|Distributed Systems|Settlement Systems|Risk Management|Real-Time Processing|Blockchain|Payment Rails)\b',
        r'\b(Test Architecture|Automation Strategy|Performance Testing|Quality Metrics|Contract Testing|Chaos Testing|Test Infrastructure)\b',
        r'\b(Mobile Architecture|Build Systems|Performance Profiling)\b',
    ]

    techs = set()
    for pattern in tech_patterns:
        for m in re.finditer(pattern, jd_text, re.I):
            tech = m.group(0)
            # 标准化
            normalized = TECH_ALIASES.get(tech.lower(), tech)
            techs.add(normalized)

    return techs


# ═══════════════════════════════════════════════════════════
# 2. Tech Profile 补全
# ═══════════════════════════════════════════════════════════

def expand_tech_if_sparse(jd_profile: dict) -> dict:
    profiles = json.loads(TECH_PROFILE.read_text(encoding='utf-8'))['profiles']
    role = jd_profile['role_type']
    seniority = jd_profile['seniority']
    jd_tech = set(jd_profile['tech_required'])
    for group in jd_profile.get('tech_or_groups', []):
        jd_tech.update(group)

    profile = profiles.get(role, profiles.get('backend', {}))
    level = profile.get(seniority, profile.get('mid_1_3y', {}))

    core_set = set(t.lower() for t in level.get('core', []))
    auxiliary_set = set(t.lower() for t in level.get('auxiliary', []))
    jd_tech_lower = set(t.lower() for t in jd_tech)

    core_coverage = len(jd_tech_lower & core_set) / max(len(core_set), 1)

    expanded_tech = set(jd_tech)
    expanded_markers = set()

    if core_coverage < 0.5:
        for t in level.get('core', []):
            if t.lower() not in jd_tech_lower:
                expanded_tech.add(t)
                expanded_markers.add(t)
        for t in level.get('auxiliary', []):
            if t.lower() not in jd_tech_lower:
                expanded_tech.add(t)
                expanded_markers.add(t)

    jd_profile['tech_expanded'] = expanded_tech
    jd_profile['tech_expansion_markers'] = expanded_markers
    jd_profile['tech_core_coverage'] = core_coverage

    return jd_profile


# ═══════════════════════════════════════════════════════════
# 3. Atom Selector
# ═══════════════════════════════════════════════════════════

# 角色兼容性矩阵（简化版）
ROLE_COMPATIBILITY = {
    ('ai_genai', 'backend'): 0.6, ('ai_genai', 'data'): 0.6,
    ('backend', 'cloud_infra'): 0.7, ('backend', 'devops'): 0.5,
    ('backend', 'data'): 0.5, ('backend', 'fintech'): 0.7,
    ('cloud_infra', 'devops'): 0.85, ('devops', 'backend'): 0.5,
    ('data', 'backend'): 0.5, ('data', 'ai_genai'): 0.5,
    ('security', 'backend'): 0.5, ('security', 'devops'): 0.5,
    ('frontend', 'backend'): 0.3, ('mobile', 'frontend'): 0.4,
    ('qa_sdet', 'devops'): 0.4, ('qa_sdet', 'backend'): 0.3,
    ('fintech', 'backend'): 0.7, ('embedded', 'hpc_compiler'): 0.6,
}


def get_role_compat(role_a: str, role_b: str) -> float:
    """查角色兼容性"""
    if role_a == role_b:
        return 1.0
    pair = (role_a, role_b)
    if pair in ROLE_COMPATIBILITY:
        return ROLE_COMPATIBILITY[pair]
    pair_rev = (role_b, role_a)
    if pair_rev in ROLE_COMPATIBILITY:
        return ROLE_COMPATIBILITY[pair_rev]
    return 0.3  # 默认低兼容


def score_catom(catom: dict, jd_profile: dict) -> float:
    """给一个 catom 打分（0-1）"""
    tech_pool = jd_profile['tech_expanded']
    tech_pool_lower = set(t.lower() for t in tech_pool)

    # 技术栈重叠度
    catom_skills = set()
    for sid in catom.get('skill_pool', []):
        # 从 skill_id 提取末尾的技术名称
        parts = sid.split('.')
        if parts:
            catom_skills.add(parts[-1].lower().replace('-', ' ').replace('_', ' '))

    # 也从 text_variants 的文本中提取技术词
    for v in catom.get('text_variants', []):
        text = v.get('text', '').lower()
        for tech in tech_pool_lower:
            if tech in text:
                catom_skills.add(tech)

    tech_overlap = len(catom_skills & tech_pool_lower) / max(len(catom_skills), 1) if catom_skills else 0

    # 业务域重叠度
    catom_domains = set(catom.get('domain_options', []))
    jd_domains = set(jd_profile.get('biz_domains', []))
    domain_overlap = len(catom_domains & jd_domains) / max(len(catom_domains), 1) if catom_domains else 0

    # 角色兼容度
    catom_angles = catom.get('angle_tags', [])
    role_compat = 0.3
    jd_role = jd_profile['role_type']
    # angle_tags 用的是简短标签（ai, backend, devops...），需要映射
    angle_to_role = {
        'ai': 'ai_genai', 'backend': 'backend', 'devops': 'devops',
        'data': 'data', 'security': 'security', 'frontend': 'frontend',
        'mobile': 'mobile', 'qa': 'qa_sdet', 'hpc': 'hpc_compiler',
        'embedded': 'embedded', 'fintech': 'fintech', 'platform': 'cloud_infra',
    }
    for angle in catom_angles:
        mapped = angle_to_role.get(angle, angle)
        compat = get_role_compat(jd_role, mapped)
        if compat > role_compat:
            role_compat = compat

    # 综合评分
    score = 0.5 * tech_overlap + 0.2 * domain_overlap + 0.3 * role_compat
    
    # soft_required 加分
    soft_req = set(t.lower() for t in jd_profile.get('soft_required', set()))
    for sp in catom.get('skill_pool', []):
        parts = sp.split('.')
        if parts and parts[-1].lower().replace('-', ' ').replace('_', ' ') in soft_req:
            score += 0.3
            break  # 只加一次
            
    return score


def _find_claude_bin() -> str | None:
    patterns = [
        os.path.expanduser('~/Library/Application Support/Claude/claude-code/*/claude.app/Contents/MacOS/claude'),
        os.path.expanduser('~/Library/Application Support/Claude/claude-code-vm/*/claude'),
    ]
    for pattern in patterns:
        candidates = sorted(glob.glob(pattern), reverse=True)
        if candidates:
            return candidates[0]
    return None

_RATE_LIMIT_FILE = Path(__file__).parent / 'staging' / '.rate_limited'

def _is_rate_limited() -> bool:
    if not _RATE_LIMIT_FILE.exists():
        return False
    try:
        info = json.loads(_RATE_LIMIT_FILE.read_text(encoding='utf-8'))
        print(f"[Writer] ⏸️ 限额暂停中 (触发时间: {info.get('timestamp', '?')}, 类型: {info.get('limit_type', '?')})")
        print(f"[Writer] 请等待额度恢复后删除 {_RATE_LIMIT_FILE} 并重新运行")
        return True
    except Exception:
        return True

def _mark_rate_limited(stderr_text: str):
    limit_type = 'unknown'
    if '5 hour' in stderr_text.lower() or '5h' in stderr_text.lower():
        limit_type = '5_hour'
    elif 'week' in stderr_text.lower() or '7 day' in stderr_text.lower():
        limit_type = 'weekly'
    
    from datetime import datetime
    _RATE_LIMIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    _RATE_LIMIT_FILE.write_text(json.dumps({
        'timestamp': datetime.now().isoformat(),
        'limit_type': limit_type,
        'raw_error': stderr_text[:500],
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"[Writer] ⏸️ 触发流量限额 ({limit_type})")
    print(f"[Writer] 已暂停。所有待处理项目已 stage。")
    print(f"[Writer] 恢复后删除 {_RATE_LIMIT_FILE} 并重新运行。")

def _call_claude(prompt: str, model: str = "claude-sonnet-4-6") -> str | None:
    if _is_rate_limited():
        return None
    claude_bin = _find_claude_bin()
    if not claude_bin:
        print("[Writer] ❌ Claude Code CLI 未找到")
        return None
    
    env = os.environ.copy()
    if "CLAUDECODE" in env:
        del env["CLAUDECODE"]
    
    cmd = [claude_bin, "-p", "--model", model]
    try:
        process = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, env=env
        )
        stdout, stderr = process.communicate(input=prompt, timeout=180)
        if process.returncode != 0:
            all_output = (stdout + stderr).lower()
            keywords = [
                'rate limit', 'quota', 'resource_exhausted', 'overloaded', 
                'capacity', 'hit your limit', 'resets'
            ]
            if any(kw in all_output for kw in keywords):
                _mark_rate_limited(stdout + stderr)
                return None
            print(f"[Writer] ❌ CLI 错误 (exit {process.returncode}): {stderr[:300]}")
            return None
        return stdout.strip()
    except subprocess.TimeoutExpired:
        process.kill()
        print("[Writer] ❌ CLI 超时 (180s)")
        return None
    except Exception as e:
        print(f"[Writer] ❌ 异常: {e}")
        return None

def _writer_rewrite_project(project_catoms: list[tuple[float, dict]], jd_profile: dict, exp_id: str,
                            avoid_themes: list[str] | None = None,
                            project_index: int = 1,
                            total_projects: int = 1) -> dict | None:
    original_bullets = []
    original_techs = set()
    project_group = None
    for _, catom in project_catoms:
        text = catom.get('_resolved_text', '')
        original_bullets.append(text)
        original_techs.update(re.findall(r'\*\*([^*]+)\*\*', text))
        if not project_group:
            project_group = catom.get('_project_group') or catom.get('project_group')
    
    role_type = jd_profile.get('role_type', 'backend')
    biz_domains = jd_profile.get('biz_domains', ['backend_distributed'])
    seniority = jd_profile.get('seniority', 'mid_1_3y')
    
    COMPANY_CONTEXT = {
        'exp-bytedance': 'ByteDance (TikTok) Security Infra team, San Jose. 6-month internship. Builds security/compliance/infrastructure tools. Title: Software Engineer Intern.',
        'exp-didi': 'DiDi IBG Food Business, Beijing/Mexico City. Senior Data Analyst (acting Team Lead), Sep 2022-May 2024. Led 13-person cross-functional team (backend, frontend, fullstack, PM, data analysts, LatAm ops). Global spokesperson for Beijing data team. Covered 6 LatAm countries. Tech transition: data analytics → backend/fullstack development. Plausible scope: data pipelines, backend services, dashboards, cross-border compliance, dispatch analytics.',
        'exp-temu': 'Temu R&D, Shanghai. ML Data Analyst. Recommendation/search/ads infrastructure.',
        'academic': 'Georgia Tech MSCS course project.',
    }
    SENIORITY_RULES = {
        'intern': 'INTERN: use "implemented/built/developed/designed". NEVER "led team/drove org-wide/managed/spearheaded".',
        'new_grad': 'NEW GRAD: avoid overly senior language.',
        'mid_1_3y': 'MID-LEVEL (1-3y): can use "designed/architected/optimized".',
        'senior_5y_plus': 'SENIOR (5y+): can use "led/architected/drove/mentored".',
        'didi_analyst_lead': 'DiDi ANALYST (acting Team Lead): can use "coordinated/designed/built/led" for team-scoped work. Can say "led cross-functional" for the 13-person team. May also credibly represent the headquarters data organization in biweekly global operating reviews, with recommendations adopted by management and LATAM frontline teams. Do NOT claim undefined company-wide executive ownership beyond that operating-review chain.',
    }
    
    # 主题差异化约束
    theme_instruction = ""
    available_themes = THEME_DOMAINS.get(exp_id, [])
    if avoid_themes and total_projects > 1:
        theme_instruction = f"""
THEME CONSTRAINT (CRITICAL):
- This is Project {project_index} of {total_projects} for this company.
- The OTHER project(s) focus on: {', '.join(avoid_themes)}
- You MUST pick a DIFFERENT sub-domain. Do NOT repeat their theme.
- Available sub-domains: {', '.join(available_themes)}
- Tech stacks may share 30-50% overlap with the other project (natural for same company), but this project needs 2-3 DISTINCT focus technologies that the other project does NOT use.
"""
    elif total_projects > 1:
        theme_instruction = f"""
THEME CONSTRAINT:
- This is Project {project_index} of {total_projects} for this company.
- Available sub-domains: {', '.join(available_themes)}
- Pick a focused sub-domain from the list above.
"""

    prompt = f"""Rewrite the business narrative of these project bullets. KEEP ALL **bold** technical terms EXACTLY as-is.

COMPANY: {COMPANY_CONTEXT.get(exp_id, 'Software company')}
TARGET DOMAIN: {role_type} / {', '.join(biz_domains)}
SENIORITY: {SENIORITY_RULES.get(seniority, SENIORITY_RULES['mid_1_3y'])}
{theme_instruction}
ORIGINAL BULLETS:
{chr(10).join(f'- {b}' for b in original_bullets)}

RULES:
1. Keep ALL **bold** terms identical (same casing, same words)
2. Keep quantitative metrics in realistic range (don't inflate)
3. REWRITE business narrative to match target domain
4. XYZ format: Action verb + technical method + quantified result
5. New project title fitting the target domain
6. EXACTLY {len(original_bullets)} bullets, each 120-180 characters
7. Every bullet MUST start with a strong action verb. NEVER start with Assisted/Helped/Supported/Participated/Contributed.
8. Do NOT add technical terms not in the original
9. Include a "theme" field describing the sub-domain focus (1-3 words)

Output ONLY this JSON:
{{"project_title": "...", "theme": "...", "bullets": ["...", "..."]}}"""

    result = _call_claude(prompt)
    if not result:
        return None
    
    try:
        cleaned = result.strip()
        match = re.search(r'(\{.*\})', cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1)
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        Path('/tmp/failed.json').write_text(result, encoding='utf-8')
        print(f"[Writer] ❌ JSON 解析失败 ({e}), 原始输出: {result[:300]}")
        return None
    
    new_pg = f"gen-{role_type}-{exp_id.replace('exp-', '')}-p{project_index}"
    theme = data.get('theme', '')
    generated_catoms = []
    for i, text in enumerate(data.get('bullets', [])):
        generated_catoms.append({
            'catom_id': f"{new_pg}-{i+1:03d}",
            'parent_exp_id': exp_id,
            'is_project_bullet': True,
            'project_group': new_pg,
            'achievement': data.get('project_title', 'Rewritten Project'),
            'text_variants': [{'variant_id': 'v1', 'text': text, 'best_for': [role_type]}],
            'skill_pool': [f"hard.{t.lower()}" for t in original_techs],
            'domain_options': list(biz_domains),
            'angle_tags': [role_type],
            'source_resumes': [], 'source_atom_ids': [],
        })
    
    return {
        'target_direction': role_type, 'target_company': exp_id,
        'project_group': new_pg, 'theme': theme,
        'project_title': data.get('project_title', 'Rewritten Project'),
        'generated_catoms': generated_catoms, 'source_project': project_group,
    }

THEME_DOMAINS = {
    'exp-bytedance': [
        'security compliance & policy automation',
        'threat detection & incident response',
        'security monitoring & observability',
        'vulnerability scanning & remediation',
        'access control & identity management',
        'audit logging & forensic analysis',
    ],
    'exp-didi': [
        'dispatch optimization & fleet analytics',
        'fraud detection & risk scoring',
        'cross-border data compliance & localization',
        'geo-spatial analytics & routing',
        'payment & settlement systems',
        'LatAm market analytics & operations dashboard',
        'full-stack business intelligence platform',
        'driver supply-demand modeling',
    ],
    'exp-temu': [
        'recommendation ranking & serving',
        'search relevance & query understanding',
        'user behavior modeling & cold start',
        'ads targeting & monetization',
        'content moderation & trust safety',
    ],
    'academic': [
        'systems architecture simulation',
        'compiler optimization',
        'distributed computing',
        'GPU pipeline modeling',
    ],
}


def _writer_generate_project(jd_profile: dict, exp_id: str, num_bullets: int = 5,
                             avoid_themes: list[str] | None = None,
                             project_index: int = 1,
                             total_projects: int = 1) -> dict | None:
    role_type = jd_profile.get('role_type', 'backend')
    biz_domains = jd_profile.get('biz_domains', ['backend_distributed'])
    seniority = jd_profile.get('seniority', 'mid_1_3y')
    tech_required = list(jd_profile.get('tech_required', set()))[:8]
    tech_expanded = list(jd_profile.get('tech_expanded', set()))
    tech_list = tech_required[:]
    if len(tech_list) < 5:
        tech_list.extend([t for t in tech_expanded if t not in tech_required][:5 - len(tech_list)])

    COMPANY_CONTEXT = {
        'exp-bytedance': 'ByteDance (TikTok) Security Infra, San Jose. 6-month intern. Security/compliance/infrastructure tools. Title: Software Engineer Intern.',
        'exp-didi': 'DiDi IBG Food Business, Beijing/Mexico City. Senior Data Analyst (acting Team Lead), Sep 2022-May 2024. Led 13-person cross-functional team (backend, frontend, fullstack, PM, data analysts, LatAm ops). Global spokesperson for Beijing data team. Covered 6 LatAm countries. Tech transition: data analytics → backend/fullstack development. Plausible scope: data pipelines, backend services, dashboards, cross-border compliance, dispatch analytics.',
        'exp-temu': 'Temu R&D, Shanghai. ML Data Analyst (Jun 2021-Feb 2022). Recommendation/search/ads.',
        'academic': 'Georgia Tech MSCS course project (Expected May 2026).',
    }
    SENIORITY_RULES = {
        'intern': 'INTERN: use "implemented/built/developed/designed". NEVER "led team/drove org-wide/managed/spearheaded".',
        'new_grad': 'NEW GRAD: avoid senior language.',
        'mid_1_3y': 'MID-LEVEL (1-3y): can use "designed/architected/optimized".',
        'senior_5y_plus': 'SENIOR (5y+): can use "led/architected/drove".',
        'didi_analyst_lead': 'DiDi ANALYST (acting Team Lead): can use "coordinated/designed/built/led" for team-scoped work. Can say "led cross-functional" for the 13-person team. May also credibly represent the headquarters data organization in biweekly global operating reviews, with recommendations adopted by management and LATAM frontline teams. Do NOT claim undefined company-wide executive ownership beyond that operating-review chain.',
    }

    # 主题差异化约束
    theme_instruction = ""
    available_themes = THEME_DOMAINS.get(exp_id, [])
    if avoid_themes and total_projects > 1:
        theme_instruction = f"""
THEME CONSTRAINT (CRITICAL):
- This is Project {project_index} of {total_projects} for this company.
- The OTHER project(s) focus on: {', '.join(avoid_themes)}
- You MUST pick a DIFFERENT sub-domain. Do NOT repeat their theme.
- Available sub-domains: {', '.join(available_themes)}
- Tech stacks may share 30-50% overlap with the other project (natural for same company), but this project needs 2-3 DISTINCT focus technologies that the other project does NOT use.
"""
    elif total_projects > 1:
        theme_instruction = f"""
THEME CONSTRAINT:
- This is Project {project_index} of {total_projects} for this company.
- Available sub-domains: {', '.join(available_themes)}
- Pick a focused sub-domain from the list above.
"""

    prompt = f"""Generate {num_bullets} resume bullet points for a NEW project.

COMPANY: {COMPANY_CONTEXT.get(exp_id, 'Software company')}
TARGET DIRECTION: {role_type} / {', '.join(biz_domains)}
REQUIRED TECH (must use): {', '.join(tech_list)}
SENIORITY: {SENIORITY_RULES.get(seniority, SENIORITY_RULES['mid_1_3y'])}
{theme_instruction}
RULES:
1. XYZ format: Action verb + technical method + quantified result
2. At least 3 bullets with specific metrics (%, time, throughput)
3. Metrics must be REALISTIC (e.g. "31% reduction" not "99.9%")
4. Mark technical terms with **bold**
5. Each bullet 120-180 characters
6. Every bullet MUST start with a strong action verb. NEVER start with Assisted/Helped/Supported/Participated/Contributed.
7. Business narrative must match the company context
8. ONLY use tech from: {', '.join(tech_list)}
9. Project must feel real for this company/department
10. Include a "theme" field describing the sub-domain focus (1-3 words)

Output ONLY this JSON:
{{"project_title": "...", "theme": "...", "bullets": ["...", "..."]}}"""

    result = _call_claude(prompt)
    if not result:
        return None

    try:
        cleaned = result.strip()
        match = re.search(r'(\{.*\})', cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1)
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        Path('/tmp/failed.json').write_text(result, encoding='utf-8')
        print(f"[Writer] ❌ JSON 解析失败 ({e}), 原始输出: {result[:300]}")
        return None

    new_pg = f"gen-{role_type}-{exp_id.replace('exp-', '')}-p{project_index}"
    theme = data.get('theme', '')
    generated_catoms = []
    for i, text in enumerate(data.get('bullets', [])):
        generated_catoms.append({
            'catom_id': f"{new_pg}-{i+1:03d}",
            'parent_exp_id': exp_id,
            'is_project_bullet': True,
            'project_group': new_pg,
            'achievement': data.get('project_title', 'Generated Project'),
            'text_variants': [{'variant_id': 'v1', 'text': text, 'best_for': [role_type]}],
            'skill_pool': [f"hard.{t.lower()}" for t in tech_list],
            'domain_options': list(biz_domains),
            'angle_tags': [role_type],
            'source_resumes': [], 'source_atom_ids': [],
        })

    return {
        'target_direction': role_type, 'target_company': exp_id,
        'project_group': new_pg, 'theme': theme,
        'project_title': data.get('project_title', 'Generated Project'),
        'generated_catoms': generated_catoms, 'source_project': None,
    }


def _validate_project_selection(chosen_groups, jd_profile):
    """验证选中的项目是否与 JD 方向有合理关联，返回 (valid_groups, fallback_actions)"""
    valid_groups = []
    fallback_actions = []
    
    for pg, exp_id, items in chosen_groups:
        proj_techs = set()
        proj_domains = set()
        for _, c in items:
            for sp in c.get('skill_pool', []):
                parts = sp.split('.')
                if parts:
                    proj_techs.add(parts[-1].lower().replace('-', ' ').replace('_', ' '))
            for d in c.get('domain_options', []):
                proj_domains.add(d)
        
        jd_techs = set(t.lower() for t in jd_profile.get('tech_expanded', []))
        jd_domains = set(jd_profile.get('biz_domains', []))
        
        tech_overlap = len(proj_techs & jd_techs) / max(len(proj_techs), 1)
        domain_overlap = len(proj_domains & jd_domains) > 0
        
        jd_required_lower = set(t.lower() for t in jd_profile.get('tech_required', set()))
        core_in_project = len(proj_techs & jd_required_lower)
        
        tech_fit = tech_overlap >= 0.15 and core_in_project >= 1
        domain_fit = domain_overlap
        
        if tech_fit and domain_fit:
            valid_groups.append((pg, exp_id, items))
        elif tech_fit and not domain_fit:
            valid_groups.append((pg, exp_id, items))
            fallback_actions.append({
                'project_group': pg,
                'exp_id': exp_id,
                'action': 'rewrite_domain',
                'reason': f'tech_fit={tech_overlap:.2f} but domain_mismatch',
                'proj_techs': list(proj_techs),
                'proj_domains': list(proj_domains),
            })
        else:
            fallback_actions.append({
                'project_group': pg,
                'exp_id': exp_id,
                'action': 'generate_new',
                'reason': f'tech_fit={tech_overlap:.2f}, core_match={core_in_project}, domain_fit={domain_fit}',
                'proj_techs': list(proj_techs),
                'proj_domains': list(proj_domains),
            })
    
    return valid_groups, fallback_actions

def _load_staging_project(direction: str, exp_id: str,
                          exclude_groups: list[str] | None = None,
                          exclude_themes: list[str] | None = None) -> dict | None:
    """从 staging 中查找已 approved 的同方向项目"""
    if not STAGING_FILE.exists():
        return None
    
    staging = json.loads(STAGING_FILE.read_text(encoding='utf-8'))
    for item in staging.get('approved', []):
        if item.get('target_direction') == direction and item.get('target_company') == exp_id:
            # 排除已使用的 project group
            if exclude_groups and item.get('project_group') in exclude_groups:
                continue
            # 排除已使用的 theme
            if exclude_themes and item.get('theme', '') in exclude_themes:
                continue
            return item
    return None

def _staged_to_catom_items(staged: dict, jd_profile: dict) -> list[tuple[float, dict]]:
    """将 staging 项目转换为 select_catoms 可用的 (score, catom) 列表"""
    items = []
    for catom_data in staged.get('generated_catoms', []):
        catom = {
            'catom_id': catom_data.get('catom_id', f"staged-{staged.get('staging_id', 'unknown')}"),
            'parent_exp_id': staged.get('target_company', ''),
            'is_project_bullet': True,
            'project_group': catom_data.get('project_group', staged.get('staging_id', '')),
            'text_variants': catom_data.get('text_variants', []),
            'skill_pool': catom_data.get('skill_pool', []),
            'domain_options': catom_data.get('domains', []),
            'angle_tags': catom_data.get('angle_tags', []),
            'achievement': catom_data.get('achievement', staged.get('project_title', '')),
        }
        resolved = _resolve_variant(catom, jd_profile)
        resolved['_project_group'] = catom['project_group']
        resolved['achievement'] = catom.get('achievement', '')
        score = score_catom(catom, jd_profile)
        items.append((score, resolved))
    return items

def _auto_review_staging(project_data: dict) -> str:
    """自动审核 staging 项目质量。

    返回: 'approved' | 'rejected' | 'pending'

    自动批准条件（全部满足）:
    1. 有 >= 4 个 generated_catoms（项目 bullet 数足够）
    2. 每个 bullet 的文本长度在 80-300 字符之间
    3. 每个 bullet 以大写字母开头（动词开头）
    4. 有 project_title 且非空
    5. 有 theme 且非空

    自动拒绝条件（任一满足）:
    1. generated_catoms 为空或 < 3 个
    2. 任何 bullet 超过 400 字符
    3. 任何 bullet 包含 JSON 残留（如 {, }, "bullets":）
    """
    catoms = project_data.get('generated_catoms', [])

    # 拒绝条件
    if not catoms or len(catoms) < 3:
        return 'rejected'

    for catom in catoms:
        variants = catom.get('text_variants', [])
        if not variants:
            return 'rejected'
        text = variants[0].get('text', '')
        if len(text) > 400:
            return 'rejected'
        if any(marker in text for marker in ['"bullets":', '"project_title":', '{"', '}']):
            return 'rejected'

    # 批准条件
    if len(catoms) < 4:
        return 'pending'  # 3 个 bullet 不够确定，人工审

    title = project_data.get('project_title', '').strip()
    theme = project_data.get('theme', '').strip()
    if not title or not theme:
        return 'pending'

    all_good = True
    for catom in catoms:
        text = catom.get('text_variants', [{}])[0].get('text', '')
        if len(text) < 80 or len(text) > 300:
            all_good = False
            break
        # 检查是否以大写字母开头（动词）
        clean = text.replace('**', '').strip()
        if not clean or not clean[0].isupper():
            all_good = False
            break

    return 'approved' if all_good else 'pending'


def _save_to_staging(project_data: dict, trigger: str, source_project: str = None):
    """保存新生成的项目到 staging，带去重和自动审核"""
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    if STAGING_FILE.exists():
        staging = json.loads(STAGING_FILE.read_text(encoding='utf-8'))
    else:
        staging = {'pending': [], 'approved': []}

    # ── 去重：同 direction + company + theme 的条目只保留最新的 ──
    new_dir = project_data.get('target_direction', '')
    new_company = project_data.get('target_company', '')
    new_theme = project_data.get('theme', '').lower().strip()

    staging['pending'] = [
        item for item in staging['pending']
        if not (item.get('target_direction') == new_dir
                and item.get('target_company') == new_company
                and item.get('theme', '').lower().strip() == new_theme)
    ]

    # ── 生成 staging_id ──
    existing_ids = [item.get('staging_id', '') for item in staging['pending'] + staging['approved']]
    max_num = 0
    for sid in existing_ids:
        if sid.startswith('stg-'):
            try:
                max_num = max(max_num, int(sid.split('-')[1]))
            except (ValueError, IndexError):
                pass
    new_id = f"stg-{max_num + 1:03d}"

    from datetime import datetime
    project_data['staging_id'] = new_id
    project_data['created'] = datetime.now().isoformat()
    project_data['trigger'] = trigger
    project_data['source_project'] = source_project
    project_data.setdefault('theme', '')

    # ── 自动审核：检查生成质量 ──
    auto_status = _auto_review_staging(project_data)
    project_data['review_status'] = auto_status
    project_data['reviewer_notes'] = 'auto-reviewed' if auto_status != 'pending' else ''

    if auto_status == 'approved':
        staging['approved'].append(project_data)
        print(f"[Staging] ✅ 自动批准: {new_id} (theme: {project_data.get('theme', 'N/A')})")
    elif auto_status == 'rejected':
        # 被拒绝的不保存（避免垃圾堆积）
        print(f"[Staging] ❌ 自动拒绝: {new_id} — 质量不达标")
    else:
        staging['pending'].append(project_data)
        print(f"[Staging] 💾 待审核: {new_id}")

    STAGING_FILE.write_text(json.dumps(staging, ensure_ascii=False, indent=2), encoding='utf-8')
    return new_id

def _approve_staging(staging_id: str):
    """批准 staging 中的项目，写入 catom 池"""
    if not STAGING_FILE.exists():
        print(f"[Staging] ❌ staging 文件不存在")
        return False
    
    staging = json.loads(STAGING_FILE.read_text(encoding='utf-8'))
    target = None
    for i, item in enumerate(staging['pending']):
        if item.get('staging_id') == staging_id:
            target = staging['pending'].pop(i)
            break
    
    if not target:
        print(f"[Staging] ❌ 未找到 {staging_id}")
        return False
    
    target['review_status'] = 'approved'
    staging['approved'].append(target)
    STAGING_FILE.write_text(json.dumps(staging, ensure_ascii=False, indent=2), encoding='utf-8')
    
    store = load_store()
    for catom_data in target.get('generated_catoms', []):
        store['catoms'].append(catom_data)
    store['_meta']['total_catom_count'] = len(store['catoms'])
    
    store_path = Path(__file__).parent / 'consolidated_atom_store.json'
    store_path.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding='utf-8')
    
    print(f"[Staging] ✅ {staging_id} 已批准，{len(target.get('generated_catoms', []))} catoms 写入池")
    return True


def _load_target_company_locks() -> dict:
    """加载目标公司锁定记录"""
    if not TARGET_COMPANY_LOCKS_FILE.exists():
        return {}
    return json.loads(TARGET_COMPANY_LOCKS_FILE.read_text(encoding='utf-8'))


def _save_target_company_locks(locks: dict):
    """保存目标公司锁定记录"""
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    TARGET_COMPANY_LOCKS_FILE.write_text(
        json.dumps(locks, ensure_ascii=False, indent=2), encoding='utf-8'
    )


def _check_and_lock_target_company(
    target_company: str,
    store: dict,
    selected: dict,
    jd_profile: dict,
    output_file: str = '',
) -> list[str]:
    """
    检查跨简历一致性。返回 warning 列表。
    
    规则：
    - 首次向该公司投递 → 锁定当前的部门名称和项目名称
    - 再次向该公司投递 → 检查是否与锁定记录一致
    - 不一致 → 强制使用锁定内容 + 输出 Warning
    """
    warnings = []
    locks = _load_target_company_locks()
    company_key = target_company.lower().strip()
    
    # 收集当前简历的部门和项目信息
    current_departments = {}
    for exp in store.get('experiences', []):
        exp_id = exp['exp_id']
        if exp_id in selected:
            current_departments[exp_id] = exp.get('division', '')
    
    current_projects = {}
    for exp_id, items in selected.items():
        for _, catom in items:
            pg = catom.get('_project_group') or catom.get('project_group')
            if pg and pg not in current_projects:
                current_projects[pg] = {
                    'title': _get_project_title(catom),
                    'company': exp_id,
                }
    
    if company_key not in locks:
        # 首次投递 → 锁定
        from datetime import datetime
        locks[company_key] = {
            'first_submitted': datetime.now().strftime('%Y-%m-%d'),
            'locked_departments': current_departments,
            'locked_projects': current_projects,
            'resumes_submitted': [{
                'role': jd_profile.get('role_type', 'unknown'),
                'file': output_file,
                'date': datetime.now().strftime('%Y-%m-%d'),
            }],
        }
        _save_target_company_locks(locks)
        print(f"[Registry] 🔒 首次投递 {target_company}，已锁定部门和项目信息")
    else:
        # 再次投递 → 检查一致性
        lock = locks[company_key]
        
        # 检查部门一致性
        for exp_id, current_dept in current_departments.items():
            locked_dept = lock['locked_departments'].get(exp_id, '')
            if locked_dept and current_dept != locked_dept:
                warnings.append(
                    f"⚠️ {exp_id} 部门不一致: 当前='{current_dept}', "
                    f"锁定='{locked_dept}' (首次投递 {lock['first_submitted']})"
                )
                # 强制使用锁定的部门名
                for exp in store.get('experiences', []):
                    if exp['exp_id'] == exp_id:
                        exp['division'] = locked_dept
                        print(f"[Registry] 强制使用锁定部门: {exp_id} → {locked_dept}")
        
        # 检查项目名一致性
        for pg, current_info in current_projects.items():
            locked_info = lock['locked_projects'].get(pg)
            if locked_info and current_info['title'] != locked_info['title']:
                warnings.append(
                    f"⚠️ 项目 '{pg}' 名称不一致: 当前='{current_info['title']}', "
                    f"锁定='{locked_info['title']}'"
                )
        
        # 记录本次投递
        from datetime import datetime
        lock['resumes_submitted'].append({
            'role': jd_profile.get('role_type', 'unknown'),
            'file': output_file,
            'date': datetime.now().strftime('%Y-%m-%d'),
        })
        # 更新锁定（可能有新的部门/项目是首次出现的）
        for exp_id, dept in current_departments.items():
            if exp_id not in lock['locked_departments']:
                lock['locked_departments'][exp_id] = dept
        for pg, info in current_projects.items():
            if pg not in lock['locked_projects']:
                lock['locked_projects'][pg] = info
        
        _save_target_company_locks(locks)
        
        if warnings:
            for w in warnings:
                print(f"[Registry] {w}")
        else:
            print(f"[Registry] ✅ 与 {target_company} 历史记录一致")
    
    return warnings


def _direction_penalty(catom, jd_profile):
    """计算 catom 与 JD 方向的一致性 penalty"""
    jd_role = jd_profile['role_type']
    angle_tags = set(catom.get('angle_tags', []))
    
    OPPOSING = {
        'frontend': {'embedded', 'hpc_compiler'},
        'mobile': {'hpc_compiler', 'embedded'},
        'embedded': {'frontend', 'mobile', 'fintech'},
        'hpc_compiler': {'frontend', 'mobile', 'fintech'},
        'qa_sdet': {'hpc_compiler', 'embedded'},
    }
    
    opposing = OPPOSING.get(jd_role, set())
    if angle_tags and angle_tags.issubset(opposing):
        return 0.2
    
    role_to_angle = {
        'ai_genai': {'ai', 'data', 'backend'},
        'backend': {'backend', 'devops', 'data'},
        'frontend': {'frontend', 'backend'},
        'mobile': {'mobile', 'frontend'},
        'devops': {'devops', 'backend', 'cloud'},
        'data': {'data', 'ai', 'backend'},
        'security': {'security', 'backend', 'devops'},
        'fintech': {'fintech', 'backend', 'data'},
        'cloud_infra': {'devops', 'cloud', 'backend'},
        'hpc_compiler': {'hpc', 'embedded', 'backend'},
        'embedded': {'embedded', 'hpc', 'backend'},
        'qa_sdet': {'qa', 'backend', 'devops'},
    }
    
    compatible_angles = role_to_angle.get(jd_role, {'backend'})
    if angle_tags and not angle_tags & compatible_angles:
        return 0.5
    
    return 1.0


def select_catoms(store: dict, jd_profile: dict) -> dict:
    """
    从 consolidated store 中选择最相关的 catoms。
    返回按 experience 分组的选中 catoms。
    """
    catoms = store['catoms']

    # Budget 分配
    BUDGET = {
        'exp-bytedance': {'total': 10, 'max_project_groups': 2, 'bullets_per_project': (4, 6), 'general_max': 4},
        'exp-didi': {'total': 7, 'max_project_groups': 1, 'bullets_per_project': (4, 6), 'general_max': 5},
        'exp-temu': {'total': 5, 'max_project_groups': 1, 'bullets_per_project': (4, 6), 'general_max': 3},
        'academic': {'total': 2, 'max_project_groups': 1, 'bullets_per_project': (1, 2), 'general_max': 0},
    }
    GLOBAL_PROJECT_LIMIT = 2  # 整份简历恰好 2 个 Project

    # 打分
    scored = []
    for c in catoms:
        s = score_catom(c, jd_profile)
        scored.append((s, c))

    scored.sort(key=lambda x: -x[0])

    # 第一阶段：全局选 top-2 project_group
    selected = defaultdict(list)
    selected_ids = set()
    all_project_groups = defaultdict(list)
    for s, c in scored:
        pg = c.get('project_group')
        if not c.get('is_project_bullet') or not pg:
            continue

        exp_id = c['parent_exp_id']
        budget = BUDGET.get(exp_id)
        if not budget or budget['max_project_groups'] <= 0:
            continue

        c_resolved = _resolve_variant(c, jd_profile)
        c_resolved['_project_group'] = pg
        c_resolved['_project_title'] = _get_project_title(c_resolved)
        if _check_seniority_compat(c_resolved, exp_id):
            all_project_groups[pg].append((s, c_resolved))

    group_scores = []
    for pg, items in all_project_groups.items():
        exp_id = items[0][1]['parent_exp_id']
        budget = BUDGET.get(exp_id, {})
        min_b, max_b = budget.get('bullets_per_project', (0, 0))
        eligible_items = sorted(items, key=lambda x: -x[0])
        effective_min = min(len(eligible_items), min_b)
        avg_score = sum(s for s, _ in eligible_items[:max_b]) / max(effective_min, 1)
        group_scores.append((avg_score, pg, exp_id, eligible_items))

    group_scores.sort(key=lambda x: -x[0])

    chosen_groups = []
    exp_pg_count = defaultdict(int)
    for avg_score, pg, exp_id, items in group_scores:
        del avg_score
        if len(chosen_groups) >= GLOBAL_PROJECT_LIMIT:
            break
        if exp_pg_count[exp_id] >= BUDGET[exp_id]['max_project_groups']:
            continue
        chosen_groups.append((pg, exp_id, items))
        exp_pg_count[exp_id] += 1

    original_chosen_groups = list(chosen_groups)
    chosen_groups, fallback_actions = _validate_project_selection(chosen_groups, jd_profile)

    if fallback_actions:
        generated_context = defaultdict(list)  # exp_id -> [{'project_group': ..., 'theme': ...}]

        # 预计算每个 exp_id 需要生成的 generate_new 总数
        exp_gen_counts = defaultdict(int)
        for action in fallback_actions:
            if action['action'] == 'generate_new':
                exp_gen_counts[action['exp_id']] += 1

        for action in fallback_actions:
            exp_id_key = action['exp_id']
            existing = generated_context[exp_id_key]
            exclude_pgs = [e['project_group'] for e in existing]
            exclude_themes = [e['theme'] for e in existing if e.get('theme')]
            project_index = len(existing) + 1

            if action['action'] == 'generate_new':
                total_for_exp = exp_gen_counts[exp_id_key]

                # 1. 尝试 staging（带排除）
                staged = _load_staging_project(
                    jd_profile.get('role_type', 'backend'), action['exp_id'],
                    exclude_groups=exclude_pgs,
                    exclude_themes=exclude_themes,
                )
                if staged:
                    staged_items = _staged_to_catom_items(staged, jd_profile)
                    if staged_items:
                        chosen_groups.append((staged['project_group'], action['exp_id'], staged_items))
                        generated_context[exp_id_key].append({
                            'project_group': staged['project_group'],
                            'theme': staged.get('theme', ''),
                        })
                        print(f"[Fallback] ✅ 使用 staging: {staged['project_group']} (theme: {staged.get('theme', 'N/A')})")
                        continue

                # 2. Writer 生成新项目（传入 avoid_themes）
                print(f"[Writer] 🔄 为 {action['exp_id']} 生成项目 {project_index}/{total_for_exp}...")
                new_project = _writer_generate_project(
                    jd_profile, action['exp_id'],
                    avoid_themes=exclude_themes,
                    project_index=project_index,
                    total_projects=total_for_exp,
                )
                if new_project and new_project.get('generated_catoms'):
                    _save_to_staging(new_project, 'checkpoint_tech_mismatch')
                    new_items = _staged_to_catom_items(new_project, jd_profile)
                    if new_items:
                        chosen_groups.append((new_project['project_group'], action['exp_id'], new_items))
                        generated_context[exp_id_key].append({
                            'project_group': new_project['project_group'],
                            'theme': new_project.get('theme', ''),
                        })
                        print(f"[Writer] ✅ 生成成功: {new_project['project_title']} (theme: {new_project.get('theme', 'N/A')}, {len(new_items)} bullets)")
                        continue

                # 3. 最终 fallback: 不保留原始不合格项目，只记录失败
                print(f"[Writer] ⚠️ 生成失败: {action['project_group']} — 不保留原始不合格项目")
                jd_profile.setdefault('_fallback_needed', []).append(action)

            elif action['action'] == 'rewrite_domain':
                # 1. 尝试 staging（带排除）
                staged = _load_staging_project(
                    jd_profile.get('role_type', 'backend'), action['exp_id'],
                    exclude_groups=exclude_pgs,
                    exclude_themes=exclude_themes,
                )
                if staged:
                    staged_items = _staged_to_catom_items(staged, jd_profile)
                    if staged_items:
                        chosen_groups = [g for g in chosen_groups if g[0] != action['project_group']]
                        chosen_groups.append((staged['project_group'], action['exp_id'], staged_items))
                        generated_context[exp_id_key].append({
                            'project_group': staged['project_group'],
                            'theme': staged.get('theme', ''),
                        })
                        print(f"[Fallback] ✅ 使用 staging 重写: {staged['project_group']} (theme: {staged.get('theme', 'N/A')})")
                        continue

                # 2. Writer 重写
                rewritten = None
                for pg, eid, items in list(chosen_groups):
                    if pg == action['project_group']:
                        print(f"[Writer] 🔄 重写项目: {pg}...")
                        rewritten = _writer_rewrite_project(
                            items, jd_profile, eid,
                            avoid_themes=exclude_themes,
                            project_index=project_index,
                            total_projects=max(1, len([a for a in fallback_actions if a['exp_id'] == exp_id_key])),
                        )
                        if rewritten and rewritten.get('generated_catoms'):
                            _save_to_staging(rewritten, 'checkpoint_domain_mismatch', pg)
                            new_items = _staged_to_catom_items(rewritten, jd_profile)
                            if new_items:
                                chosen_groups = [g for g in chosen_groups if g[0] != pg]
                                chosen_groups.append((rewritten['project_group'], eid, new_items))
                                generated_context[exp_id_key].append({
                                    'project_group': rewritten['project_group'],
                                    'theme': rewritten.get('theme', ''),
                                })
                                print(f"[Writer] ✅ 重写成功: {rewritten['project_title']} (theme: {rewritten.get('theme', 'N/A')})")
                        break

                if not rewritten or not rewritten.get('generated_catoms'):
                    # 不保留原始不合格项目
                    chosen_groups = [g for g in chosen_groups if g[0] != action['project_group']]
                    print(f"[Writer] ⚠️ 重写失败: {action['project_group']} — 移除不合格项目")
                    jd_profile.setdefault('_fallback_needed', []).append(action)

    chosen_by_exp = defaultdict(list)
    for pg, exp_id, items in chosen_groups:
        chosen_by_exp[exp_id].append((pg, items))

    for exp_id, groups in chosen_by_exp.items():
        budget = BUDGET[exp_id]
        min_b, max_b = budget['bullets_per_project']
        counts = {pg: min_b for pg, _ in groups}
        max_project_total = min(
            budget['total'],
            sum(min(len(items), max_b) for _, items in groups),
        )
        remaining_slots = max_project_total - sum(counts.values())

        while remaining_slots > 0:
            best_pg = None
            best_score = -1.0
            for pg, items in groups:
                current_count = counts[pg]
                if current_count >= max_b or current_count >= len(items):
                    continue
                next_score = items[current_count][0]
                if next_score > best_score:
                    best_score = next_score
                    best_pg = pg
            if best_pg is None:
                break
            counts[best_pg] += 1
            remaining_slots -= 1

        for pg, items in groups:
            for s, c in items[:counts[pg]]:
                selected[exp_id].append((s, c))
                selected_ids.add(c['catom_id'])

    # ── Academic 项目专选（不参与全局 top-2 竞争）──
    if 'academic' not in selected or not selected['academic']:
        acad_budget = BUDGET.get('academic', {})
        acad_project_candidates = []
        for s, c in scored:
            if c.get('parent_exp_id') != 'academic':
                continue
            if not c.get('is_project_bullet', False):
                continue
            if c['catom_id'] in selected_ids:
                continue
            c_resolved = _resolve_variant(c, jd_profile)
            c_resolved['_project_group'] = c.get('project_group')
            c_resolved['_project_title'] = _get_project_title(c_resolved)
            acad_project_candidates.append((s, c_resolved))

        # 按分数排序，选 top bullets（最多 2 个）
        acad_project_candidates.sort(key=lambda x: -x[0])
        min_b, max_b = acad_budget.get('bullets_per_project', (1, 2))
        for s, c in acad_project_candidates[:max_b]:
            selected['academic'].append((s, c))
            selected_ids.add(c['catom_id'])

    # 第三阶段：用 general bullets 填满剩余配额
    for exp_id, budget in BUDGET.items():
        general_added = 0
        general_candidates = [
            (s, c) for s, c in scored
            if c['parent_exp_id'] == exp_id
            and not c.get('is_project_bullet', False)
            and c['catom_id'] not in selected_ids
        ]

        def _try_add(candidates_list):
            nonlocal general_added
            for s, c in candidates_list:
                if len(selected[exp_id]) >= budget['total'] or general_added >= budget['general_max']:
                    break
                if c['catom_id'] in selected_ids:
                    continue
                c_resolved = _resolve_variant(c, jd_profile)
                c_resolved['_project_group'] = None
                if not _check_seniority_compat(c_resolved, exp_id):
                    continue
                selected[exp_id].append((s, c_resolved))
                selected_ids.add(c['catom_id'])
                general_added += 1

        pass1 = [(s, c) for s, c in general_candidates if _direction_penalty(c, jd_profile) == 1.0]
        _try_add(pass1)
        
        if len(selected[exp_id]) < budget['total'] and general_added < budget['general_max']:
            pass2 = [(s, c) for s, c in general_candidates if _direction_penalty(c, jd_profile) != 1.0]
            _try_add(pass2)

    # ── Fix 3: 项目 bullet 最低保证（不足 4 个时从 general pool 补充） ──
    MIN_PROJECT_BULLETS = 4
    for exp_id in ['exp-bytedance', 'exp-didi', 'exp-temu']:
        items = selected.get(exp_id, [])
        if not items:
            continue
        # 找所有 project_group
        pg_set = set()
        for _, c in items:
            pg = c.get('_project_group')
            if pg and c.get('is_project_bullet', False):
                pg_set.add(pg)
        for pg in pg_set:
            pg_bullets = [(s, c) for s, c in items if c.get('_project_group') == pg and c.get('is_project_bullet', False)]
            deficit = MIN_PROJECT_BULLETS - len(pg_bullets)
            if deficit <= 0:
                continue
            # 按分数排序同 exp_id 的 general catoms 补充
            for s, c in scored:
                if deficit <= 0:
                    break
                if c.get('parent_exp_id') != exp_id:
                    continue
                if c['catom_id'] in selected_ids:
                    continue
                if c.get('is_project_bullet'):
                    continue
                c_resolved = _resolve_variant(c, jd_profile)
                c_resolved['_project_group'] = pg
                c_resolved['is_project_bullet'] = True
                # 设定 project title 与已有 bullets 一致
                if pg_bullets:
                    c_resolved['_project_title'] = pg_bullets[0][1].get('_project_title', pg)
                selected[exp_id].append((s, c_resolved))
                selected_ids.add(c['catom_id'])
                deficit -= 1

    return selected


def _resolve_variant(catom: dict, jd_profile: dict) -> dict:
    """为 catom 选择最佳 variant 并解析 OR-slots"""
    catom = dict(catom)  # 浅拷贝
    variants = catom.get('text_variants', [])
    if not variants:
        catom['_resolved_text'] = ''
        return catom

    jd_role = jd_profile['role_type']
    # 简单映射
    role_to_angle = {
        'ai_genai': 'ai', 'backend': 'backend', 'devops': 'devops',
        'data': 'data', 'security': 'security', 'frontend': 'frontend',
        'mobile': 'mobile', 'qa_sdet': 'qa', 'hpc_compiler': 'hpc',
        'embedded': 'embedded', 'fintech': 'fintech', 'cloud_infra': 'devops',
    }
    target_angle = role_to_angle.get(jd_role, 'backend')

    # 选 best_for 最匹配的 variant
    best_variant = variants[0]
    best_score = 0
    for v in variants:
        bf = v.get('best_for', [])
        score = 1.0 if target_angle in bf else 0.0
        # 也检查技术重叠
        tech_lower = set(t.lower() for t in jd_profile['tech_expanded'])
        vtext = v.get('text', '').lower()
        tech_hits = sum(1 for t in tech_lower if t in vtext)
        score += tech_hits * 0.1
        if score > best_score:
            best_score = score
            best_variant = v

    # 解析 slots
    resolved_text = best_variant.get('text', '')
    for slot_name, slot_info in best_variant.get('slots', {}).items():
        options = slot_info.get('options', [])
        if not options:
            continue
        # 选与 JD tech 匹配的 option
        chosen = options[0]  # 默认第一个
        tech_lower = set(t.lower() for t in jd_profile['tech_expanded'])
        for opt in options:
            if any(t in opt.lower() for t in tech_lower):
                chosen = opt
                break
        placeholder = "{" + slot_name + "}"
        resolved_text = resolved_text.replace(placeholder, chosen)

    catom['_resolved_text'] = resolved_text
    catom['_chosen_variant'] = best_variant.get('variant_id', 'v1')
    return catom


def _check_seniority_compat(catom: dict, exp_id: str) -> bool:
    """过滤与实际职级不匹配的越权表述。"""
    text = catom.get('_resolved_text', '').strip()
    lowered = text.lower()

    if exp_id == 'exp-temu' and lowered.startswith('architected'):
        return False

    for blocked in SENIORITY_BLOCKLIST.get(exp_id, []):
        if blocked in lowered:
            return False

    return True


# ═══════════════════════════════════════════════════════════
# 4. Assembler
# ═══════════════════════════════════════════════════════════


UNIVERSAL_TOOLS = {'python', 'docker', 'git', 'sql', 'linux', 'ci/cd'}

def _check_tech_distribution(selected: dict) -> tuple[bool, str]:
    from collections import Counter
    exp_tech_profiles = {}
    for exp_id, items in selected.items():
        if exp_id == 'academic':
            continue
        techs = Counter()
        for _, catom in items:
            text = catom.get('_resolved_text', '')
            for bold in re.findall(r'\*\*([^*]+)\*\*', text):
                b = bold.lower()
                if b not in UNIVERSAL_TOOLS:
                    techs[b] += 1
        exp_tech_profiles[exp_id] = set(t for t, _ in techs.most_common(5))

    exps = list(exp_tech_profiles.keys())
    for i in range(len(exps)):
        for j in range(i+1, len(exps)):
            s1 = exp_tech_profiles[exps[i]]
            s2 = exp_tech_profiles[exps[j]]
            if not s1 or not s2:
                continue
            overlap = s1 & s2
            overlap_ratio = len(overlap) / min(len(s1), len(s2), 5)
            if overlap_ratio >= 0.8:
                return False, f"{exps[i]} 和 {exps[j]} 技术栈重叠过高: {overlap}"
    return True, "ok"

def _align_department(store: dict, jd_profile: dict) -> dict:
    biz_domains = set(jd_profile.get('biz_domains', []))
    role = jd_profile.get('role_type', 'backend')
    
    temu_dept = 'R&D · Recommendation Infra'
    if 'ads_monetization' in biz_domains or role == 'ads':
        temu_dept = 'R&D · Ads & Monetization'
    elif any('search' in d for d in biz_domains):
        temu_dept = 'R&D · Search & Discovery'
    
    dept_overrides = {}
    for exp in store.get('experiences', []):
        if exp['exp_id'] == 'exp-temu':
            dept_overrides['exp-temu'] = temu_dept
            exp['division'] = temu_dept
    
    return dept_overrides

def _pre_summary_checkpoint(selected: dict, jd_profile: dict, store: dict) -> tuple[dict, dict]:
    report = {
        'missing_techs': [],
        'seniority_swaps': 0,
        'overflow_warnings': [],
        'domain_warnings': []
    }
    
    all_bold_techs = set()
    for exp_id, items in selected.items():
        for _, catom in items:
            text = catom.get('_resolved_text', '')
            all_bold_techs.update(t.lower() for t in re.findall(r'\*\*([^*]+)\*\*', text))
    
    missing_required = set()
    for tech in jd_profile.get('tech_required', set()):
        if tech.lower() not in all_bold_techs:
            missing_required.add(tech.lower())

    missing_or_groups = []
    for or_group in jd_profile.get('tech_or_groups', []):
        if not any(t.lower() in all_bold_techs for t in or_group):
            missing_or_groups.append(or_group)

    missing_techs = missing_required
    for og in missing_or_groups:
        missing_techs.add(list(og)[0])

    if missing_techs:
        report['missing_techs'] = list(missing_techs)
        lowest_item = None
        lowest_score = float('inf')
        lowest_exp = None
        lowest_idx = -1
        for exp_id, items in selected.items():
            for idx, (s, catom) in enumerate(items):
                if not catom.get('is_project_bullet', False):
                    if s < lowest_score:
                        lowest_score = s
                        lowest_item = catom
                        lowest_exp = exp_id
                        lowest_idx = idx
        
        if lowest_item:
            selected_ids = {c['catom_id'] for items in selected.values() for _, c in items}
            best_rep = None
            best_s = -1
            for c in store.get('catoms', []):
                if c['catom_id'] in selected_ids: continue
                if c.get('parent_exp_id') != lowest_exp: continue
                if c.get('is_project_bullet', False): continue
                
                has_missing = False
                for sp in c.get('skill_pool', []):
                    parts = sp.split('.')
                    if parts and parts[-1].lower().replace('-', ' ').replace('_', ' ') in missing_techs:
                        has_missing = True
                        break
                if not has_missing:
                    # fixed iteration over text_variants which may be missing
                    for v in c.get('text_variants', []): 
                        vtext = v.get('text', '').lower()
                        if any(mt in vtext for mt in missing_techs):
                            has_missing = True
                            break
                            
                if has_missing:
                    if _direction_penalty(c, jd_profile) == 1.0:
                        s = score_catom(c, jd_profile)
                        if s > best_s:
                            best_s = s
                            best_rep = c
            
            if best_rep:
                rep_resolved = _resolve_variant(best_rep, jd_profile)
                rep_resolved['_project_group'] = None
                selected[lowest_exp][lowest_idx] = (best_s, rep_resolved)
                report['repaired_c1'] = True

    TECH_ECOSYSTEM = {
        'microservices': {'kubernetes', 'docker', 'grpc', 'service mesh', 'istio'},
        'data_pipeline': {'kafka', 'flink', 'spark', 'airflow', 'dbt'},
        'ml_infra': {'kubernetes', 'docker', 'mlflow', 'kubeflow', 'gpu'},
        'cloud_native': {'terraform', 'helm', 'argocd', 'prometheus', 'grafana'},
        'backend_web': {'redis', 'postgresql', 'mongodb', 'elasticsearch', 'rabbitmq'},
        'container_orchestration': {'docker', 'kubernetes', 'helm', 'istio'},
        'observability': {'prometheus', 'grafana', 'datadog', 'opentelemetry', 'splunk'},
        'ci_cd': {'github actions', 'gitlab ci', 'jenkins', 'argocd'},
        'hpc': {'cuda', 'mpi', 'openmp', 'cmake', 'c++'},
        'security': {'tls', 'mtls', 'oauth', 'oidc', 'jwt', 'rbac'},
    }

    TITLE_DEPT_TECH_MAP = {
        'exp-didi': {
            'title_techs': {'python', 'sql', 'flink', 'spark', 'react', 'typescript', 'fastapi', 'django'},
            'dept_techs': {'gps', 'eta', 'dispatch', 'geospatial', 'i18n', 'localization', 'latam', 'cross-border'},
        },
        'exp-temu': {
            'title_techs': {'python', 'sql'},
            'dept_techs': {'recommendation', 'search', 'ranking', 'embedding', 'rag'},
        },
        'exp-bytedance': {
            'title_techs': {'go', 'python', 'docker', 'kubernetes', 'grpc'},
            'dept_techs': {'security', 'compliance', 'rbac', 'audit', 'mcp'},
        },
    }

    nice_to_have = jd_profile.get('tech_nice_to_have', set())
    seniority = jd_profile.get('seniority', 'mid_1_3y')

    for n2h_tech in nice_to_have:
        n2h_lower = n2h_tech.lower()
        if seniority not in ['intern', 'new_grad']:
            required_techs_lower = {t.lower() for t in jd_profile.get('tech_required', set())}
            for eco_name, eco_set in TECH_ECOSYSTEM.items():
                if n2h_lower in eco_set and required_techs_lower & eco_set:
                    jd_profile.setdefault('soft_required', set()).add(n2h_lower)
                    break
        
        for exp_id, tech_map in TITLE_DEPT_TECH_MAP.items():
            all_natural = tech_map['title_techs'] | tech_map['dept_techs']
            if n2h_lower in all_natural:
                jd_profile.setdefault('natural_fit', set()).add(n2h_lower)
                break

    for exp_id, items in selected.items():
        for idx, (s, catom) in enumerate(list(items)):
            text = catom.get('_resolved_text', '').lower()
            needs_replacement = False
            if seniority in ['intern', 'new_grad']:
                if any(kw in text for kw in ["led team", "managed a team", "drove org-wide", "as tech lead"]):
                    needs_replacement = True
            elif seniority.startswith('senior'):
                if any(kw in text for kw in ["assisted with", "helped", "supported the team"]):
                    needs_replacement = True
            
            if needs_replacement:
                report['seniority_swaps'] += 1
                selected_ids = {c['catom_id'] for it in selected.values() for _, c in it}
                is_proj = catom.get('is_project_bullet', False)
                pg = catom.get('_project_group')
                best_rep = None
                best_s = -1
                for c in store.get('catoms', []):
                    if c['catom_id'] in selected_ids: continue
                    if c.get('parent_exp_id') != exp_id: continue
                    if is_proj:
                        if not c.get('is_project_bullet', False) or c.get('project_group') != pg: continue
                    else:
                        if c.get('is_project_bullet', False): continue
                    
                    cand_s = score_catom(c, jd_profile)
                    cand_resolved = _resolve_variant(c, jd_profile)
                    cand_text = cand_resolved.get('_resolved_text', '').lower()
                    
                    cand_bad = False
                    if seniority in ['intern', 'new_grad']:
                        if any(kw in cand_text for kw in ["led team", "managed a team", "drove org-wide", "as tech lead"]):
                            cand_bad = True
                    elif seniority.startswith('senior'):
                        if any(kw in cand_text for kw in ["assisted with", "helped", "supported the team"]):
                            cand_bad = True
                    
                    if not cand_bad and cand_s > best_s:
                        best_s = cand_s
                        best_rep = cand_resolved
                        
                if best_rep:
                    best_rep['_project_group'] = pg
                    selected[exp_id][idx] = (best_s, best_rep)

    profiles = json.loads(TECH_PROFILE.read_text(encoding='utf-8'))['profiles']
    role = jd_profile.get('role_type', 'backend')
    profile = profiles.get(role, profiles.get('backend', {}))
    level = profile.get(seniority, profile.get('mid_1_3y', {}))
    core_aux = set(t.lower() for t in level.get('core', []) + level.get('auxiliary', []))
    
    jd_expanded_lower = set(t.lower() for t in jd_profile.get('tech_expanded', []))
    jd_required_lower = set(t.lower() for t in jd_profile.get('tech_required', []))
    natural_fit = set(t.lower() for t in jd_profile.get('natural_fit', set()))

    for exp_id, items in selected.items():
        for idx, (s, catom) in enumerate(list(items)):
            text = catom.get('_resolved_text', '')
            bold_techs = [t.lower() for t in re.findall(r'\*\*([^*]+)\*\*', text)]
            severe_overflow_techs = []
            for tech in bold_techs:
                if tech in jd_required_lower or tech in jd_expanded_lower or tech in core_aux or tech in natural_fit:
                    continue
                severe_overflow_techs.append(tech)
            
            if severe_overflow_techs:
                clean_variants = []
                for v in catom.get('text_variants', []):
                    vtext = v.get('text', '').lower()
                    if not any(t in vtext for t in severe_overflow_techs):
                        clean_variants.append(v)
                if clean_variants:
                    temp_catom = dict(catom)
                    temp_catom['text_variants'] = clean_variants
                    new_resolved = _resolve_variant(temp_catom, jd_profile)
                    new_resolved['_project_group'] = catom.get('_project_group')
                    selected[exp_id][idx] = (s, new_resolved)
                    report['overflow_warnings'].append({'catom_id': catom['catom_id'], 'fixed': True})
                else:
                    report['overflow_warnings'].append({'catom_id': catom['catom_id'], 'fixed': False})

    tech_dist_ok, tech_dist_msg = _check_tech_distribution(selected)
    if not tech_dist_ok:
        report['tech_distribution_warning'] = tech_dist_msg
        match = re.match(r'(exp-\w+) 和 (exp-\w+)', tech_dist_msg)
        if match:
            exp_a, exp_b = match.group(1), match.group(2)
            target_exp = exp_b if len(selected.get(exp_a, [])) >= len(selected.get(exp_b, [])) else exp_a
            
            items = selected.get(target_exp, [])
            worst_idx = -1
            worst_score = float('inf')
            for idx, (s, catom) in enumerate(items):
                if not catom.get('is_project_bullet', False) and not catom.get('_project_group'):
                    if s < worst_score:
                        worst_score = s
                        worst_idx = idx
            
            if worst_idx >= 0:
                selected_ids = {c['catom_id'] for it in selected.values() for _, c in it}
                overlap_techs = set()
                for _, catom in items:
                    for bold in re.findall(r'\*\*([^*]+)\*\*', catom.get('_resolved_text', '')):
                        overlap_techs.add(bold.lower())
                
                best_rep = None
                best_s = -1
                for c in store.get('catoms', []):
                    if c['catom_id'] in selected_ids: continue
                    if c.get('parent_exp_id') != target_exp: continue
                    if c.get('is_project_bullet', False): continue
                    
                    resolved = _resolve_variant(c, jd_profile)
                    cand_techs = set(t.lower() for t in re.findall(r'\*\*([^*]+)\*\*', resolved.get('_resolved_text', '')))
                    new_techs = cand_techs - overlap_techs - UNIVERSAL_TOOLS
                    
                    if new_techs:  
                        s = score_catom(c, jd_profile)
                        if s > best_s:
                            best_s = s
                            best_rep = resolved
                
                if best_rep:
                    best_rep['_project_group'] = None
                    selected[target_exp][worst_idx] = (best_s, best_rep)
                    report['tech_distribution_repaired'] = True

    print("[Checkpoint] Report:", json.dumps(report, indent=2))
    return selected, report

def assemble_resume(store: dict, selected: dict, jd_profile: dict, profile: dict | None = None) -> str:
    """将选中的 catoms 组装为 Markdown 简历。profile 覆盖 identity 中的 name/contact。"""
    dept_overrides = _align_department(store, jd_profile)
    selected, checkpoint_report = _pre_summary_checkpoint(selected, jd_profile, store)
    identity = store['identity']
    lines = []

    # Header — 如果提供了 profile 则用 profile 信息，否则用 store 中的 placeholder
    if profile:
        header_name = profile['name']
        header_contact = f"{profile['email']} | {profile['phone']}"
    else:
        header_name = identity.get('name', 'PLACEHOLDER')
        header_contact = identity.get('contact', 'PLACEHOLDER')
    lines.append(f"# {header_name}")
    lines.append(f"{header_contact}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Professional Summary (placeholder — LLM 填充)
    lines.append("## Professional Summary")
    summary_bullets = _generate_deterministic_summary(store, selected, jd_profile)
    for bullet in summary_bullets:
        lines.append(f"- {_post_process_bullet(bullet, jd_profile)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Work Experience
    lines.append("## Work Experience")
    lines.append("")

    exp_scores = {}
    for exp_id in ['exp-bytedance', 'exp-didi', 'exp-temu']:
        items = selected.get(exp_id, [])
        exp_scores[exp_id] = sum(s for s, _ in items) / max(len(items), 1)
    exp_order = sorted(exp_scores.keys(), key=lambda e: -exp_scores[e])
    for exp_id in exp_order:
        exp_info = _get_exp_info(store, exp_id)
        if not exp_info:
            continue

        # Experience header
        lines.append(f"### {exp_info['title']} | {exp_info['company']} · {exp_info['division']} | {exp_info['location']}")
        lines.append(f"> {exp_info['period']}")
        lines.append("")

        catoms_for_exp = selected.get(exp_id, [])
        if not catoms_for_exp:
            continue

        project_groups_output, general_catoms = _group_catoms_for_output(catoms_for_exp)

        for _, pg_catoms in project_groups_output.items():
            proj_title = _get_project_title(pg_catoms[0])
            lines.append(f"**_Project: {proj_title}_**")
            for catom in pg_catoms:
                bullet_text = _post_process_bullet(catom['_resolved_text'], jd_profile, exp_id=exp_id)
                # 防止 bullet 内含换行导致项目块被断裂（C04 修复）
                bullet_text = bullet_text.replace('\n', ' ').strip()
                if bullet_text:
                    lines.append(f"- {bullet_text}")
            lines.append("")

        for _, catom in general_catoms:
            lines.append(f"- {_post_process_bullet(catom['_resolved_text'], jd_profile, exp_id=exp_id)}")

        if general_catoms:
            lines.append("")

    # Academic Projects（如果选中）
    if 'academic' in selected and selected['academic']:
        # 放在 Education section 下面
        pass  # 会在 Education 部分输出

    lines.append("---")
    lines.append("")

    # Skills
    lines.append("## Skills")
    skills_text = _generate_skills_section(selected, jd_profile)
    lines.append(skills_text)
    lines.append("")
    lines.append("---")
    lines.append("")

    # Education
    lines.append("## Education")
    lines.append("")
    lines.append("| Degree | Institution | Period |")
    lines.append("|--------|-------------|--------|")
    for edu in identity.get('education', []):
        # 跳过 UIUC MSIM
        if 'MSIM' in edu['degree'] and 'Illinois' in edu['institution']:
            continue
        # GT: 去掉 (OMSCS) 标注
        degree = edu['degree']
        if '(OMSCS)' in degree:
            degree = degree.replace(' (OMSCS)', '')
        lines.append(f"| {degree} | {edu['institution']} | {edu['period']} |")
    lines.append("")

    # Academic projects（在 Education 后面）
    if 'academic' in selected and selected['academic']:
        lines.append("### Academic Projects")
        lines.append("")
        project_groups_output, general_catoms = _group_catoms_for_output(selected['academic'])
        for _, pg_catoms in project_groups_output.items():
            proj_title = _get_project_title(pg_catoms[0])
            lines.append(f"**_Project: {proj_title}_**")
            for catom in pg_catoms:
                lines.append(f"- {_post_process_bullet(catom['_resolved_text'], jd_profile, exp_id='academic')}")
            if len(general_catoms) == 0:
                lines.append("")
        for _, catom in general_catoms:
            lines.append(f"- {_post_process_bullet(catom['_resolved_text'], jd_profile, exp_id='academic')}")
        
        if general_catoms:
            lines.append("")

    lines.append("---")
    lines.append("")

    # Additional Information
    lines.append("## Additional Information")
    for item in identity.get('additional', []):
        lines.append(f"- **{item['category'].title()}:** {item['text']}")
    lines.append("")


    fallback_needed = jd_profile.get('_fallback_needed', [])
    if fallback_needed:
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("> ⚠️ **NEEDS REVIEW**: 以下项目需要人工审核：")
        for action in fallback_needed:
            if action['action'] == 'rewrite_domain':
                lines.append(f"> - 项目 `{action['project_group']}` ({action['exp_id']}): 技术栈匹配但业务域不匹配，需要业务重写")
            elif action['action'] == 'generate_new':
                lines.append(f"> - 需要为 `{action['exp_id']}` 生成新项目: {action['reason']}")
        lines.append(f"> ")
        lines.append(f"> 请前往 staging/pending_review.json 审核触发生成的新项目。")

    return '\n'.join(lines)


def _get_exp_info(store: dict, exp_id: str) -> dict | None:
    """获取经历基本信息"""
    for exp in store.get('experiences', []):
        if exp['exp_id'] == exp_id:
            return exp
    return None


def _group_catoms_for_output(catoms_for_exp: list[tuple[float, dict]]) -> tuple[OrderedDict, list[tuple[float, dict]]]:
    """按 project_group 聚合，用于输出多 bullet project。"""
    project_groups_output = OrderedDict()
    general_catoms = []

    for s, catom in catoms_for_exp:
        pg = catom.get('_project_group')
        is_pj = catom.get('is_project_bullet', False)
        if pg and is_pj:
            if pg not in project_groups_output:
                project_groups_output[pg] = []
            project_groups_output[pg].append(catom)
        else:
            general_catoms.append((s, catom))

    return project_groups_output, general_catoms


def _get_project_title(catom: dict) -> str:
    """优先使用 project_mapping 中的 canonical 标题。"""
    project_group = catom.get('_project_group') or catom.get('project_group')
    
    # Writer 生成的项目：直接使用 achievement 字段
    if project_group and project_group.startswith('gen-'):
        return catom.get('achievement', project_group).strip()
    
    title_lookup = _load_project_title_lookup()
    if project_group and project_group in title_lookup:
        return title_lookup[project_group].strip()

    title = catom.get('achievement', project_group or 'Project')
    return title.replace('Project: ', '').strip()


def _load_project_title_lookup() -> dict:
    """缓存 canonical project 标题，避免反复读取 JSON。"""
    global _PROJECT_TITLE_LOOKUP
    if _PROJECT_TITLE_LOOKUP is None:
        if PROJECT_MAPPING.exists():
            mapping = json.loads(PROJECT_MAPPING.read_text(encoding='utf-8')).get('canonical_projects', {})
            _PROJECT_TITLE_LOOKUP = {
                project_group: info.get('title', project_group)
                for project_group, info in mapping.items()
            }
        else:
            _PROJECT_TITLE_LOOKUP = {}
    return _PROJECT_TITLE_LOOKUP



def _extract_role_label(jd_profile: dict) -> str:
    def fix_acronyms(s: str) -> str:
        s = re.sub(r'(?i)\bhpc\b', 'HPC', s)
        s = re.sub(r'(?i)\bfintech\b', 'FinTech', s)
        s = re.sub(r'(?i)\bai\b', 'AI', s)
        s = re.sub(r'(?i)\bml\b', 'ML', s)
        s = re.sub(r'(?i)\bqa\b', 'QA', s)
        s = re.sub(r'(?i)\bsdet\b', 'SDET', s)
        return s

    raw_text = jd_profile.get('raw_text', '').strip()
    first_line = raw_text.split('\n')[0].strip()
    first_part = first_line.split(',')[0].strip()
    if 5 <= len(first_part) <= 50 and 'engineer' in first_part.lower():
        role = first_part.title()
        role = re.sub(r'(?i)^We Are Looking For A[n]?\s+', '', role)
        return fix_acronyms(role)

    match = re.search(r'(?i)we are looking for a(?:n)?\s+([a-zA-Z0-9\s\-]+engineer)', raw_text)
    if match:
        return fix_acronyms(match.group(1).strip().title())

    role_labels = {
        'backend': 'Backend Engineer',
        'ai_genai': 'AI/ML & Backend Engineer',
        'data': 'Data Engineer',
        'devops': 'DevOps Engineer',
        'frontend': 'Frontend Engineer',
        'security': 'Security Engineer',
        'mobile': 'Mobile Engineer',
        'cloud_infra': 'Cloud Infrastructure Engineer',
        'fintech': 'FinTech Backend Engineer',
        'hpc_compiler': 'HPC & Compiler Engineer',
        'embedded': 'Embedded Systems Engineer',
        'qa_sdet': 'QA & Automation Engineer',
    }
    return role_labels.get(jd_profile.get('role_type', 'backend'), 'Software Engineer')

def _extract_delivery_keywords(selected: dict, jd_profile: dict) -> str:
    delivery_kw_set = {'docker', 'kubernetes', 'ci/cd', 'github actions', 'gitlab ci', 'jenkins', 'argo', 'terraform', 'rest', 'grpc', 'graphql', 'agile', 'scrum'}
    jd_req = set(t.lower() for t in jd_profile.get('tech_required', []))
    jd_exp = set(t.lower() for t in jd_profile.get('tech_expanded', []))
    
    found_kws = set()
    for exp_id, items in selected.items():
        for _, catom in items:
            text = catom.get('_resolved_text', '').lower()
            for kw in delivery_kw_set:
                if kw in text and (kw in jd_req or kw in jd_exp):
                    found_kws.add(kw)
    
    found_kws = sorted(list(found_kws))
    if not found_kws:
        return "**CI/CD** automation"
    
    formatted = []
    for kw in found_kws:
        if kw in {'docker', 'kubernetes'}:
            formatted.append(f"**{kw.title()}**")
        elif kw == 'ci/cd':
            formatted.append("**CI/CD**")
        elif kw in {'rest', 'grpc', 'graphql'}:
            formatted.append(f"**{kw if kw == 'graphql' else kw.upper() if kw == 'rest' else 'gRPC'}** API development")
        else:
            formatted.append(f"**{kw.title()}**")
            
    texts = []
    has_containers = [t for t in formatted if 'Docker' in t or 'Kubernetes' in t]
    if has_containers:
        texts.append('/'.join(has_containers) + " containerization")
    
    has_cicd = [t for t in formatted if 'CI/CD' in t or 'Github Actions' in t or 'Jenkins' in t]
    if has_cicd:
        texts.append(', '.join(has_cicd) + " automation")
        
    has_api = [t for t in formatted if 'API development' in t]
    if has_api:
        texts.append(', '.join(has_api))
        
    other = [t for t in formatted if t not in has_containers and t not in has_cicd and 'API' not in t]
    if other:
        texts.extend(other)
        
    if not texts:
        return "**CI/CD** automation"
    
    if len(texts) > 1:
        return ', '.join(texts[:-1]) + ", and " + texts[-1]
    return texts[0]

def _weiqi_competitive_edge(role_type: str) -> str:
    mapping = {
        'backend': "systematic thinking applied to distributed system architecture and production reliability",
        'devops': "systematic thinking applied to distributed system architecture and production reliability",
        'cloud_infra': "systematic thinking applied to distributed system architecture and production reliability",
        'ai_genai': "strategic pattern recognition and structured reasoning applied to model architecture decisions",
        'data': "strategic pattern recognition and structured reasoning applied to model architecture decisions",
        'security': "adversarial multi-step reasoning and threat scenario anticipation",
        'frontend': "holistic product thinking balancing user experience with technical constraints",
        'mobile': "holistic product thinking balancing user experience with technical constraints",
        'hpc_compiler': "deep algorithmic reasoning and resource-constrained optimization mindset",
        'embedded': "deep algorithmic reasoning and resource-constrained optimization mindset",
        'fintech': "risk-aware strategic thinking applied to financial system architecture",
        'qa_sdet': "exhaustive edge-case reasoning and systematic defect prediction",
    }
    return mapping.get(role_type, "systematic thinking and strategic problem decomposition")

def _generate_deterministic_summary(store: dict, selected: dict, jd_profile: dict) -> list[str]:
    all_bold_techs = set()
    for exp_id, items in selected.items():
        for _, catom in items:
            text = catom.get('_resolved_text', '')
            all_bold_techs.update(re.findall(r'\*\*([^*]+)\*\*', text))
    
    jd_required = set(t.lower() for t in jd_profile.get('tech_required', set()))
    jd_expanded = set(t.lower() for t in jd_profile.get('tech_expanded', set()))
    
    priority_techs = sorted([t for t in all_bold_techs if t.lower() in jd_required])
    secondary_techs = sorted([t for t in all_bold_techs if t.lower() in jd_expanded and t.lower() not in jd_required])
    tech_str = ', '.join(f'**{t}**' for t in (priority_techs + secondary_techs)[:6])
    if not tech_str:
        tech_str = "**backend systems**"
    
    role_label = _extract_role_label(jd_profile)
    b1 = (
        f"**{role_label}:** 3+ years of technical experience across high-traffic platforms "
        f"(**ByteDance/TikTok**, **DiDi**, **Temu**), with production-grade delivery of {tech_str}."
    )
    
    delivery_kws = _extract_delivery_keywords(selected, jd_profile)
    b2 = (
        f"**End-to-End Engineering Delivery:** Owns features through the complete SDLC — from "
        f"system design and API development to {delivery_kws} — with cross-functional collaboration "
        f"across product, engineering, and stakeholder teams in **Agile** environments."
    )
    
    weiqi_angle = _weiqi_competitive_edge(jd_profile.get('role_type'))
    b3 = (
        f"**Unique Edge:** National 2-Dan Go (Weiqi) competitor — {weiqi_angle}. "
        f"Pursuing M.S. Computer Science at **Georgia Tech** with interdisciplinary background "
        f"in philosophy and psychology, bringing unique perspective to technical problem-solving."
    )
    
    return [b1, b2, b3]

def _generate_skills_section(selected: dict, jd_profile: dict) -> str:
    # Fix 2: Skill noise filter logic
    SKILLS_NOISE_FILTER = {
        'ai', 'api', 'apis', 'api development', 'ml', 'iot',
        'agile', 'scrum', 'agile/scrum', 'sdlc',
        'business requirements', 'collaboration', 'leadership',
        'object-oriented design', 'data structures', 'algorithms',
        'multi-threaded', 'scalability', 'high availability',
        'android', 'appium', 'espresso', 'rest api',
        'agentic', 'sdk', 'sdks', 'llms',
        'synthetic data generation',
        'customer-facing', 'technical documentation',
        'cpu', 'gpu',
        'payment rails', 'ledger systems',
        'gcp gke',
        'javascript sdks', 'unity editor', 'unity engine',
    }
    
    all_bold_techs = set()
    for exp_id, items in selected.items():
        for _, catom in items:
            text = catom.get('_resolved_text', '')
            extracted = re.findall(r'\*\*([^*]+)\*\*', text)
            for t in extracted:
                tl = t.lower().strip()
                if tl in SKILLS_NOISE_FILTER: continue
                if re.match(r'^[\d.]+%?$', tl): continue
                if len(tl) <= 2 and tl not in {'c', 'r', 'go'}: continue
                all_bold_techs.add(t)
    
    jd_expanded = set(jd_profile.get('tech_expanded', jd_profile.get('tech_required', set())))
    tech = set()
    for jd_t in jd_expanded:
        if jd_t.lower() in [b.lower() for b in all_bold_techs]:
            tech.add(jd_t)
            
    for b in all_bold_techs:
        if not any(b.lower() == t.lower() for t in tech):
            tech.add(b)

    _skills_blocklist = {'compliance', 'sre', 'devops', 'observability', 'fintech', 'blockchain'}
    dedup = {}
    for t in tech:
        key = t.lower()
        if key in _skills_blocklist: continue
        if key not in dedup:
            dedup[key] = t
        else:
            existing = dedup[key]
            if len(t) > len(existing) or (t[0].isupper() and not existing[0].isupper()):
                dedup[key] = t
    tech_list = sorted(list(dedup.values()))

    categories = {
        'Languages': [],
        'Frameworks & Libraries': [],
        'Infrastructure & Cloud': [],
        'Data & Storage': [],
        'AI & ML': [],
        'Tools & Practices': [],
    }

    lang_kw = {'python', 'java', 'go', 'golang', 'c++', 'c#', 'rust', 'kotlin', 'swift', 'scala',
               'typescript', 'javascript', 'sql', 'hiveql', 'sparksql', 'ruby', 'php', 'bash', 'shell'}
    framework_kw = {'react', 'vue', 'angular', 'next.js', 'spring boot', 'fastapi', 'django', 'flask',
                    'express', 'langchain', 'langgraph', 'pytorch', 'tensorflow', 'hugging face'}
    infra_kw = {'docker', 'kubernetes', 'terraform', 'helm', 'ansible', 'argocd', 'istio',
                'aws', 'gcp', 'azure', 'github actions', 'gitlab ci', 'jenkins', 'ci/cd',
                'linux', 'prometheus', 'grafana', 'datadog', 'opentelemetry'}
    data_kw = {'postgresql', 'mysql', 'mongodb', 'redis', 'kafka', 'dynamodb', 'cassandra',
               'elasticsearch', 'spark', 'airflow', 'hive', 'flink', 'bigquery', 'redshift', 'dbt'}
    ai_kw = {'llm', 'rag', 'bert', 'gpt', 'machine learning', 'deep learning', 'mlflow',
             'mlops', 'pytorch', 'tensorflow', 'generative ai', 'prompt engineering'}

    for t in tech_list:
        tl = t.lower()
        if tl in lang_kw: categories['Languages'].append(t)
        elif tl in framework_kw: categories['Frameworks & Libraries'].append(t)
        elif tl in infra_kw: categories['Infrastructure & Cloud'].append(t)
        elif tl in data_kw: categories['Data & Storage'].append(t)
        elif tl in ai_kw: categories['AI & ML'].append(t)
        else: categories['Tools & Practices'].append(t)

    # Fix 3: Skills category merge logic
    MERGE_TARGET = {
        'Data & Storage': 'Infrastructure & Cloud',
        'AI & ML': 'Frameworks & Libraries',
        'Frameworks & Libraries': 'Tools & Practices',
    }

    # Step 1: Merge 1-skill categories (except Languages)
    for cat in list(categories.keys()):
        if cat == 'Languages': continue
        if len(categories[cat]) == 1:
            target = MERGE_TARGET.get(cat, 'Tools & Practices')
            categories[target].extend(categories[cat])
            categories[cat] = []

    # Step 2: Merge smallest categories if total > 4
    non_empty = {k: v for k, v in categories.items() if v}
    while len(non_empty) > 4:
        others = [k for k in non_empty.keys() if k != 'Tools & Practices']
        if not others: break
        smallest = min(others, key=lambda k: len(non_empty[k]))
        categories['Tools & Practices'].extend(categories[smallest])
        categories[smallest] = []
        non_empty = {k: v for k, v in categories.items() if v}

    lines = []
    jd_req_lower = set(t.lower() for t in jd_profile.get('tech_required', []))
    for cat in ['Languages', 'Frameworks & Libraries', 'Infrastructure & Cloud', 'Data & Storage', 'AI & ML', 'Tools & Practices']:
        if cat in non_empty and non_empty[cat]:
            # Fix 4: Local category de-duplication
            cat_dedup = {}
            for it in non_empty[cat]:
                key = it.lower()
                if key not in cat_dedup:
                    cat_dedup[key] = it
                else:
                    existing = cat_dedup[key]
                    if len(it) > len(existing) or (it[0].isupper() and not existing[0].isupper()):
                        cat_dedup[key] = it
            
            final_items = list(cat_dedup.values())
            # ── C10 修复：过滤非 JD 技术 ──
            try:
                import sys as _sys
                _atomizer_dir = str(Path(__file__).resolve().parent)
                if _atomizer_dir not in _sys.path:
                    _sys.path.insert(0, _atomizer_dir)
                from validate_resume import KEEP_BOLD as _KB
            except ImportError:
                _KB = set()
            jd_allowed_lower = {t.lower() for t in jd_expanded} | {t.lower() for t in _KB}
            final_items = [it for it in final_items if it.lower() in jd_allowed_lower]
            if not final_items:
                continue
            def sort_key(x):
                xl = x.lower()
                if xl in jd_req_lower: return 0
                if xl in [t.lower() for t in jd_expanded]: return 1
                return 2
            sorted_items = sorted(final_items, key=sort_key)
            bold_items = ', '.join(f'**{t}**' for t in sorted_items[:8])
            lines.append(f"- {cat}: {bold_items}")
            
    return '\n'.join(lines) if lines else "- **Technologies:** " + ', '.join(tech_list[:8])


def _pick_best_summary_variant(summary_catom: dict, jd_profile: dict) -> str | None:
    """从一个 summary catom 的 variants 中选最匹配 JD 的，并解析 slots。"""
    variants = summary_catom.get('text_variants', [])
    if not variants:
        return None

    tech_lower = {t.lower() for t in jd_profile.get('tech_expanded', set())}
    role_to_angle = {
        'ai_genai': 'ai', 'backend': 'backend', 'devops': 'devops',
        'data': 'data', 'security': 'security', 'frontend': 'frontend',
        'mobile': 'mobile', 'qa_sdet': 'qa', 'hpc_compiler': 'hpc',
        'embedded': 'embedded', 'fintech': 'fintech', 'cloud_infra': 'devops',
    }
    target_angle = role_to_angle.get(jd_profile.get('role_type'), 'backend')
    best_v = None
    best_score = -1
    for v in variants:
        text = v.get('text', '').lower()
        hits = sum(1 for t in tech_lower if t in text)
        score = hits * 0.1
        if target_angle in v.get('best_for', []):
            score += 1.0
        if score > best_score:
            best_score = score
            best_v = v

    if not best_v or best_score <= 0:
        return None

    text = best_v.get('text', '')
    for slot_name, slot_info in best_v.get('slots', {}).items():
        options = slot_info.get('options', [])
        chosen = options[0] if options else ''
        for opt in options:
            if any(t in opt.lower() for t in tech_lower):
                chosen = opt
                break
        text = text.replace('{' + slot_name + '}', chosen)
    return text


def _post_process_bullet(text: str, jd_profile: dict, exp_id: str | None = None) -> str:
    """后处理 bullet：只保留 JD 匹配技术词或白名单词的加粗，并清理尾部标签。"""
    # 1. 清理 bullet 尾部的全小写 metadata 标签，如 (fintech), (low-latency, data pipelines)
    # 使用较宽松的正则匹配 (lowercase_and_symbols_only) at the end of line
    text = re.sub(r'\s*\([a-z][^A-Z0-9)]*\)\s*\.?\s*$', '', text.rstrip())

    jd_tech_lower = {t.lower() for t in jd_profile.get('tech_expanded', set())}
    allowed = jd_tech_lower | KEEP_BOLD

    def debold_check(match: re.Match) -> str:
        word = match.group(1)
        normalized = word.lower()
        if normalized in allowed:
            return f'**{word}**'
        for item in allowed:
            if item in normalized or normalized in item:
                return f'**{word}**'
        return word

    text = re.sub(r'\*\*([^*]+)\*\*', debold_check, text)
    if exp_id:
        text = _normalize_bullet_lead(text)

    # 3. 清理 bullet 尾部的全小写 metadata 标签，如 (fintech), (low-latency, data pipelines)
    # 在最后一步清理，确保不被加粗逻辑影响，且清理掉可能的末尾句点。
    text = re.sub(r'\s*\([^A-Z0-9)]+\)\s*\.?\s*$', '', text.rstrip())

    return text


def _normalize_bullet_lead(text: str) -> str:
    """将少数弱开头统一为验证脚本认可的强动词。"""
    for source, target in LEAD_VERB_NORMALIZATION.items():
        if text.startswith(source + ' '):
            return target + text[len(source):]
    return text


def load_store() -> dict:
    """加载 consolidated atom store，供 CLI 和测试脚本复用。"""
    return json.loads(CONSOLIDATED_STORE.read_text(encoding='utf-8'))


def load_profile(profile_id: str) -> dict | None:
    """从 profiles.json 加载指定 profile（A/B/C），返回 {name, email, phone} 或 None。"""
    if not PROFILES_PATH.exists():
        return None
    profiles = json.loads(PROFILES_PATH.read_text(encoding='utf-8'))
    for p in profiles:
        if p['id'].upper() == profile_id.upper():
            return p
    return None


def build_meta(jd_profile: dict, selected: dict) -> dict:
    """构建输出 meta.json 结构。"""
    def _json_friendly(v):
        if isinstance(v, set): return list(v)
        if isinstance(v, list): return [_json_friendly(i) for i in v]
        if isinstance(v, dict): return {ik: _json_friendly(iv) for ik, iv in v.items()}
        return v

    total_selected = sum(len(v) for v in selected.values())
    return {
        'jd_profile': _json_friendly({k: v for k, v in jd_profile.items() if k != 'raw_text'}),
        'selected_catoms': {
            exp_id: [
                {
                    'catom_id': c['catom_id'],
                    'score': s,
                    'variant': c.get('_chosen_variant', ''),
                    'is_project': c.get('is_project_bullet', False),
                }
                for s, c in items
            ]
            for exp_id, items in selected.items()
        },
        'total_selected': total_selected,
    }


def generate_resume_artifacts(jd_text: str, store: dict | None = None) -> dict:
    """直接从 JD 文本生成 resume、selection 与 meta，供 test_matrix 复用。"""
    store = store or load_store()
    jd_profile = expand_tech_if_sparse(parse_jd(jd_text))

    # ── Phase 1: Planner — 全局策略规划 ──
    # 确保同目录模块可被 lazy import
    import sys as _sys
    _mod_dir = str(Path(__file__).resolve().parent)
    if _mod_dir not in _sys.path:
        _sys.path.insert(0, _mod_dir)

    plan = None
    plan_dict = None
    try:
        from resume_planner import plan_resume
        plan = plan_resume(jd_profile, store)
        plan_dict = plan.to_dict()
        print(f"[Planner] ✅ 规划完成: {plan.narrative_arc[:80]}")
        if plan.writer_needed:
            print(f"[Planner] ⚠️ 预判需要 Writer: {plan.writer_reason}")
        if plan.risk_notes:
            for note in plan.risk_notes:
                print(f"[Planner] ⚠️ 风险: {note}")
    except ImportError:
        print("[Planner] ⚠️ resume_planner.py 未找到，跳过规划阶段")
    except Exception as e:
        print(f"[Planner] ❌ 规划失败: {e}，继续无规划模式")

    # ── Phase 2: 选择 catoms ──
    selected = select_catoms(store, jd_profile)

    # ── Phase 3: Polisher — 逐句润色 ──
    polish_report = None
    try:
        from resume_polisher import polish_selected
        selected, polish_report = polish_selected(selected, jd_profile, plan_dict)
        print(f"[Polisher] ✅ 润色完成: {polish_report.modified_count}/{polish_report.total_bullets} 条修改")
    except ImportError:
        print("[Polisher] ⚠️ resume_polisher.py 未找到，跳过润色阶段")
    except Exception as e:
        print(f"[Polisher] ❌ 润色失败: {e}，继续使用原始文本")

    # ── Phase 4: 组装简历 ──
    resume_md = assemble_resume(store, selected, jd_profile)
    meta = build_meta(jd_profile, selected)

    # 将 plan 和 polish 信息加入 meta
    if plan_dict:
        meta['plan'] = {
            'narrative_arc': plan_dict.get('narrative_arc', ''),
            'writer_needed': plan_dict.get('writer_needed', False),
            'risk_notes': plan_dict.get('risk_notes', []),
            'project_strategies': plan_dict.get('project_strategies', []),
        }
    if polish_report:
        meta['polish'] = {
            'total_bullets': polish_report.total_bullets,
            'modified_count': polish_report.modified_count,
        }

    return {
        'resume_md': resume_md,
        'jd_profile': jd_profile,
        'selected': selected,
        'meta': meta,
        'total_selected': meta['total_selected'],
    }


# ═══════════════════════════════════════════════════════════
# 5. 主流程
# ═══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='Generate tailored resume from JD')
    parser.add_argument('--jd', type=str, help='Path to JD text file')
    parser.add_argument('--jd-text', type=str, help='JD text directly')
    parser.add_argument('--dry-run', action='store_true', help='Only show selection, no output files')
    parser.add_argument('--output', type=str, help='Output filename (default: auto-generated)')
    parser.add_argument('--approve-staging', type=str, help='Approve a staging item by ID (e.g., stg-001)')
    parser.add_argument('--target-company', type=str, help='Target company name for cross-resume consistency check')
    parser.add_argument('--profile', '-p', type=str, help='Profile ID (A/B/C) from profiles.json for name/contact injection')
    args = parser.parse_args()

    if args.approve_staging:
        success = _approve_staging(args.approve_staging)
        sys.exit(0 if success else 1)

    # 读取 JD
    if args.jd:
        jd_text = Path(args.jd).read_text(encoding='utf-8')
    elif args.jd_text:
        jd_text = args.jd_text
    else:
        print("Error: 请提供 --jd 或 --jd-text 参数")
        sys.exit(1)

    # 加载 profile（可选）
    profile = None
    if args.profile:
        profile = load_profile(args.profile)
        if not profile:
            avail = [p['id'] for p in json.loads(PROFILES_PATH.read_text(encoding='utf-8'))] if PROFILES_PATH.exists() else []
            print(f"Error: Profile '{args.profile}' not found. Available: {avail}")
            sys.exit(1)
        print(f"👤 Profile: {profile['id']} ({profile['name']})")

    # 加载 consolidated store
    store = load_store()
    print(f"📦 Loaded {store['_meta']['total_catom_count']} catoms")

    # Step 1: Parse JD
    jd_profile = parse_jd(jd_text)
    print(f"\n🔍 JD 分析:")
    print(f"   Role: {jd_profile['role_type']}")
    print(f"   Seniority: {jd_profile['seniority']}")
    print(f"   Tech ({len(jd_profile['tech_required'])}): {', '.join(sorted(jd_profile['tech_required']))}")
    print(f"   Domain: {', '.join(jd_profile['biz_domains'])}")

    # Step 2: Tech expansion
    jd_profile = expand_tech_if_sparse(jd_profile)
    if jd_profile['tech_expansion_markers']:
        print(f"\n📈 技术栈补全 (core coverage: {jd_profile['tech_core_coverage']:.0%}):")
        print(f"   补全了: {', '.join(sorted(jd_profile['tech_expansion_markers']))}")
    else:
        print(f"\n✅ JD 技术栈充分 (core coverage: {jd_profile['tech_core_coverage']:.0%})")

    # Step 3: Select catoms
    selected = select_catoms(store, jd_profile)
    total_selected = sum(len(v) for v in selected.values())
    print(f"\n🎯 选中 {total_selected} catoms:")
    for exp_id, items in selected.items():
        if items:
            proj = sum(1 for _, c in items if c.get('is_project_bullet'))
            gen = len(items) - proj
            print(f"   {exp_id}: {len(items)} ({proj} project + {gen} general)")

    if args.dry_run:
        print("\n=== DRY RUN: 选中的 catoms ===")
        for exp_id, items in selected.items():
            print(f"\n--- {exp_id} ---")
            for score, catom in items:
                label = "📁" if catom.get('is_project_bullet') else "•"
                print(f"  {label} [{score:.2f}] {catom['catom_id']}: {catom['_resolved_text'][:100]}...")
        return

    # Step 4: Assemble
    resume_md = assemble_resume(store, selected, jd_profile, profile=profile)

    # 跨简历一致性检查
    registry_warnings = []
    if args.target_company:
        output_name = args.output or f"resume_{jd_profile['role_type']}_{jd_profile['seniority']}.md"
        registry_warnings = _check_and_lock_target_company(
            args.target_company, store, selected, jd_profile, output_name
        )
        if registry_warnings:
            # 在简历末尾附加 warnings
            warning_lines = ['\n', '---', '', '> **Cross-Resume Consistency Warnings:**']
            for w in registry_warnings:
                warning_lines.append(f'> {w}')
            resume_md += '\n'.join(warning_lines) + '\n'

    # Output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if args.output:
        out_path = OUTPUT_DIR / args.output
    else:
        role_slug = jd_profile['role_type'].replace('_', '-')
        out_path = OUTPUT_DIR / f"resume_{role_slug}_{jd_profile['seniority']}.md"

    out_path.write_text(resume_md, encoding='utf-8')
    print(f"\n✅ Resume saved to: {out_path}")
    print(f"   Lines: {len(resume_md.splitlines())}")

    # 也保存选择元数据
    meta_path = out_path.with_suffix('.meta.json')
    meta = build_meta(jd_profile, selected)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"   Meta: {meta_path}")


if __name__ == '__main__':
    main()
