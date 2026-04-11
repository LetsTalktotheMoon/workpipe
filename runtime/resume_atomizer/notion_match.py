#!/usr/bin/env python3
"""
notion_match.py — 从 Notion DB 读取 JD，匹配冻结简历词库，回写推荐结果。

确定性匹配算法，无 LLM 参与：
1. 用统一标准词表扫描 JD 提取技术关键词和业务方向
2. 检测 OR 关联（"X or Y"、"X/Y"）将其合并为单条需求
3. 计算覆盖率评分 = 0.7×技术覆盖 + 0.3×业务覆盖
4. 输出 MD 中文分析报告 + 更新 Notion Match Score / Match Analysis

Usage:
    python3 notion_match.py --all --report    # 匹配所有 JD 并生成报告
    python3 notion_match.py --dry-run         # 只打印不写入 Notion
    python3 notion_match.py --all             # 匹配所有 JD 并写入 Notion
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

# ── 加载 .env ──────────────────────────────────────────────
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line.startswith('export '):
            line = line[7:]
        if '=' in line and not line.startswith('#'):
            key, val = line.split('=', 1)
            os.environ[key.strip()] = val.strip().strip('"').strip("'")

ROOT = Path(__file__).parent
FROZEN_CATALOG_PATH = ROOT / "classification" / "resume_keywords_frozen.json"

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_DB_ID = os.environ.get("NOTION_DB_ID", "")
NOTION_API = "https://api.notion.com/v1"
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


# ═══════════════════════════════════════════════════════════
# 标准词表 — 全部小写，JD 扫描和简历扫描使用同一份
# ═══════════════════════════════════════════════════════════

TECH_VOCAB = [
    # ── 编程语言 ──
    # 注意: 不含 "c"（\bc\b 误匹配率高）和 "r"（同理）
    # C 语言用 "c++" 覆盖（绝大多数 JD 写 C/C++）
    'python', 'java', 'go', 'golang', 'c++', 'c#',
    'typescript', 'javascript', 'kotlin', 'swift', 'rust',
    'ruby', 'scala', 'sql', 'matlab', 'tcl', 'solidity',
    'hiveql', 'sparksql', 'hive sql', 'spark sql', 'bash',

    # ── AI / ML ──
    'llm', 'rag', 'langchain', 'langgraph', 'ai', 'ml',
    'genai', 'generative ai', 'machine learning', 'deep learning',
    'nlp', 'bert', 'gpt', 'transformer',
    'computer vision', 'reinforcement learning', 'anomaly detection',
    'prompt engineering', 'ai agents',
    'pytorch', 'tensorflow', 'scikit-learn', 'hugging face',
    'kubeflow', 'mlflow', 'vertex ai',
    'pydantic', 'pinecone', 'opencv',
    'sensor fusion', 'kalman filter',
    'model serving', 'recommender systems',

    # ── Web 框架 ──
    'react', 'angular', 'vue', 'next.js', 'node.js',
    'spring boot', 'spring', 'django', 'flask', 'fastapi',
    'express', 'gin', 'fiber', 'celery',
    'tailwindcss', 'storybook', 'd3.js', 'ant design',

    # ── 云服务 ──
    'aws', 'gcp', 'azure',
    'ecs', 'eks', 'lambda', 'ec2', 's3', 'rds', 'fargate',
    'emr', 'kinesis', 'cloudwatch', 'dynamodb', 'redshift',
    'gke', 'bigquery', 'cloud spanner', 'dataproc', 'cloud run',

    # ── 基础设施 ──
    'kubernetes', 'docker', 'terraform', 'helm', 'istio', 'envoy',
    'linux', 'nginx', 'ansible', 'mesos',

    # ── 数据 / 消息 ──
    'kafka', 'spark', 'pyspark', 'airflow', 'apache airflow',
    'redis', 'mongodb', 'postgresql', 'mysql',
    'elasticsearch', 'druid', 'cassandra',
    'snowflake', 'databricks', 'hive',
    'rocketmq', 'rabbitmq', 'flink',

    # ── DevOps / CI ──
    'ci/cd', 'github actions', 'jenkins', 'argocd', 'gitops',
    'gitlab ci', 'gradle', 'cmake',

    # ── 可观测性 ──
    'prometheus', 'grafana', 'datadog', 'opentelemetry', 'pagerduty',

    # ── 协议 ──
    'grpc', 'rest', 'restful', 'graphql',
    'protobuf', 'protocol buffers', 'thrift', 'websocket',
    'tcp/ip', 'tls', 'http/2',

    # ── 安全 ──
    'security', 'threat detection', 'dlp', 'siem',
    'vulnerability', 'oauth', 'jwt', 'encryption',
    'compliance', 'mitre att&ck', 'owasp',
    'rbac', 'abac', 'mfa', 'saml', 'oidc',
    'pci-dss', 'hsm', 'kms',
    'hashicorp vault',

    # ── 系统设计 ──
    'distributed systems', 'microservices', 'service mesh',
    'virtualization', 'hypervisor', 'cuda', 'llvm', 'compiler',
    'system design',

    # ── HPC ──
    'mpi', 'openmp', 'slurm', 'hpc',

    # ── 测试 ──
    'pytest', 'junit', 'selenium', 'cypress', 'test automation',
    'appium', 'espresso',

    # ── 方法论 ──
    'agile', 'scrum', 'sdlc',

    # ── 区块链 ──
    'blockchain', 'smart contract', 'web3', 'erc-20',

    # ── 前端 ──
    'css', 'html', 'responsive design', 'design systems',
    'accessibility', 'web components',

    # ── 移动端 ──
    'android sdk', 'jetpack', 'mvvm', 'android', 'ios',

    # ── 其他 ──
    'openapi', 'mcp',
]

BIZ_VOCAB = [
    # 真正的行业/业务领域，剔除角色描述词
    # 已移除: fullstack, frontend, backend, mobile, qa, testing, quality,
    #         devops, cloud, infrastructure, platform, reliability, compiler, virtualization
    # ── 行业垂直 ──
    'fintech', 'e-commerce', 'payments', 'payment', 'billing', 'trading',
    'social media', 'gaming', 'simulation',
    'blockchain', 'web3', 'defi', 'stablecoin',
    'embedded', 'iot', 'robotics',
    # ── 业务功能 ──
    'security', 'fraud', 'compliance', 'privacy',
    'content moderation', 'trust and safety',
    'recommendation', 'ads', 'advertising', 'search', 'ranking',
    'data engineering', 'data pipeline', 'analytics',
    'sre', 'networking', 'edge', 'hpc', 'sensor',
    # ── 技术领域（同时也是业务方向）──
    'ai', 'machine learning', 'ml', 'nlp', 'computer vision',
]

# 别名映射：不同写法 → 标准形式
ALIASES = {
    'golang': 'go',
    'hive sql': 'hiveql',
    'spark sql': 'sparksql',
    'apache airflow': 'airflow',
    'protocol buffers': 'protobuf',
    'generative ai': 'genai',
    'restful': 'rest',
    'full stack': 'fullstack',
    'pyspark': 'spark',  # PySpark 是 Spark 的 Python API
}

# 不参与 OR 拆分的复合关键词（含 / 但是整体概念）
COMPOUND_SLASH_KEYWORDS = {
    'ci/cd', 'tcp/ip', 'http/2', 'rbac', 'abac',
}


# ═══════════════════════════════════════════════════════════
# 关键词扫描
# ═══════════════════════════════════════════════════════════

def scan_keywords(text: str, vocab: list[str]) -> set[str]:
    """用标准词表扫描文本，返回标准化关键词集合"""
    text_lower = text.lower()
    found = set()
    for kw in vocab:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, text_lower):
            canonical = ALIASES.get(kw, kw)
            found.add(canonical)
    return found


# ═══════════════════════════════════════════════════════════
# JD OR 关联检测
# ═══════════════════════════════════════════════════════════

def detect_or_groups(jd_text: str, detected_tech: set[str]) -> list[frozenset]:
    """
    检测 JD 中的 OR 关联模式:
    - "Python or Java" → {python, java}
    - "Python/Java"    → {python, java}（但排除 ci/cd 等复合词）

    返回 OR 组列表，每组是 frozenset
    """
    text_lower = jd_text.lower()
    or_pairs = []

    tech_list = sorted(detected_tech)  # 排序确保确定性

    for i, kw1 in enumerate(tech_list):
        for kw2 in tech_list[i + 1:]:
            # 检查 "kw1 or kw2" 和 "kw2 or kw1"
            for a, b in [(kw1, kw2), (kw2, kw1)]:
                pat = r'\b' + re.escape(a) + r'\s+or\s+' + re.escape(b) + r'\b'
                if re.search(pat, text_lower):
                    or_pairs.append((kw1, kw2))
                    break

            # 检查 "kw1/kw2"（排除 ci/cd 等复合词）
            if kw1 not in COMPOUND_SLASH_KEYWORDS and kw2 not in COMPOUND_SLASH_KEYWORDS:
                for a, b in [(kw1, kw2), (kw2, kw1)]:
                    # 回到原始词表寻找未别名化的形式
                    a_variants = [a] + [k for k, v in ALIASES.items() if v == a]
                    b_variants = [b] + [k for k, v in ALIASES.items() if v == b]
                    found = False
                    for av in a_variants:
                        for bv in b_variants:
                            pat = re.escape(av) + r'\s*/\s*' + re.escape(bv)
                            if re.search(pat, text_lower):
                                or_pairs.append((kw1, kw2))
                                found = True
                                break
                        if found:
                            break
                    if found:
                        break

    # 合并重叠的 OR 组（union-find 简化版）
    groups = []
    for a, b in or_pairs:
        merged = False
        for g in groups:
            if a in g or b in g:
                g.add(a)
                g.add(b)
                merged = True
                break
        if not merged:
            groups.append({a, b})

    return [frozenset(g) for g in groups]


def build_requirements(
    detected_tech: set[str],
    or_groups: list[frozenset],
) -> list[frozenset]:
    """
    构建需求列表:
    - OR 组内的关键词 → 1 条需求（满足任一即可）
    - 其余关键词 → 各自独立 1 条需求

    返回 list[frozenset]，每个 frozenset 是一条需求
    """
    or_keywords = set()
    for g in or_groups:
        or_keywords.update(g)

    requirements = list(or_groups)
    for kw in sorted(detected_tech):
        if kw not in or_keywords:
            requirements.append(frozenset({kw}))

    return requirements


# ═══════════════════════════════════════════════════════════
# 匹配评分
# ═══════════════════════════════════════════════════════════

def compute_match(
    tech_requirements: list[frozenset],
    jd_biz: set[str],
    resume_tech: set[str],
    resume_biz: set[str],
) -> dict:
    """
    确定性匹配评分:
    - tech_score = 满足的需求数 / 总需求数
    - biz_score  = 匹配的业务方向数 / JD 业务方向数
    - total      = 0.7 × tech + 0.3 × biz
    """
    # 技术覆盖
    satisfied = 0
    matched_tech = set()
    missing_tech = set()
    for req in tech_requirements:
        hit = req & resume_tech
        if hit:
            satisfied += 1
            matched_tech.update(hit)
        else:
            missing_tech.update(req)  # 记录整个 OR 组中缺失的

    tech_score = satisfied / len(tech_requirements) if tech_requirements else 0.0

    # 业务方向覆盖
    biz_matched = jd_biz & resume_biz
    biz_score = len(biz_matched) / len(jd_biz) if jd_biz else 0.0

    # 自适应权重：JD 无业务词时回退为纯技术分，无技术词时回退为纯业务分
    if not tech_requirements and not jd_biz:
        total = 0.0
    elif not jd_biz:
        total = tech_score
    elif not tech_requirements:
        total = biz_score
    else:
        total = 0.7 * tech_score + 0.3 * biz_score

    return {
        'total': round(total, 3),
        'tech_score': round(tech_score, 3),
        'biz_score': round(biz_score, 3),
        'satisfied': satisfied,
        'total_requirements': len(tech_requirements),
        'matched_tech': sorted(matched_tech),
        'missing_tech': sorted(missing_tech),
        'matched_biz': sorted(biz_matched),
        'missing_biz': sorted(jd_biz - resume_biz),
    }


def match_all_resumes(jd_text: str, catalog: list[dict]) -> list[dict]:
    """
    对所有简历计算匹配分数，返回排序结果
    """
    # 1. 扫描 JD 关键词
    jd_tech = scan_keywords(jd_text, TECH_VOCAB)
    jd_biz = scan_keywords(jd_text, BIZ_VOCAB)

    # 2. 检测 OR 关联
    or_groups = detect_or_groups(jd_text, jd_tech)

    # 3. 构建需求列表
    requirements = build_requirements(jd_tech, or_groups)

    # 4. 逐份简历评分
    results = []
    for item in catalog:
        resume_tech = set(item['tech_keywords'])
        resume_biz = set(item['business_directions'])

        score = compute_match(requirements, jd_biz, resume_tech, resume_biz)

        label = item['source_file']
        label = re.sub(r'_Resume\.md$', '', label)

        results.append({
            'resume_id': item['id'],
            'resume_label': label,
            **score,
        })

    results.sort(key=lambda x: x['total'], reverse=True)

    # 附加 JD 信息供报告使用
    for r in results:
        r['jd_tech_all'] = sorted(jd_tech)
        r['jd_biz_all'] = sorted(jd_biz)
        r['or_groups'] = [sorted(g) for g in or_groups]

    return results


# ═══════════════════════════════════════════════════════════
# Notion API
# ═══════════════════════════════════════════════════════════

def query_notion_db(db_id: str, start_cursor: str | None = None) -> dict:
    url = f"{NOTION_API}/databases/{db_id}/query"
    body = {"page_size": 100}
    if start_cursor:
        body["start_cursor"] = start_cursor
    resp = requests.post(url, headers=NOTION_HEADERS, json=body, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_all_pages(db_id: str) -> list[dict]:
    pages = []
    cursor = None
    while True:
        data = query_notion_db(db_id, cursor)
        pages.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return pages


def extract_page_info(page: dict) -> dict:
    props = page.get("properties", {})

    # Job Title
    title_arr = props.get("Job Title", {}).get("title", [])
    job_title = title_arr[0]["plain_text"] if title_arr else ""

    # Company
    company_select = props.get("Company", {}).get("select")
    company = company_select["name"] if company_select else ""

    # Team
    team_arr = props.get("Team", {}).get("rich_text", [])
    team = team_arr[0]["plain_text"] if team_arr else ""

    # Cleaned JD
    jd_arr = props.get("Cleaned JD", {}).get("rich_text", [])
    cleaned_jd = "".join(t["plain_text"] for t in jd_arr) if jd_arr else ""

    # Resume
    resume_select = props.get("Resume", {}).get("select")
    resume = resume_select["name"] if resume_select else ""

    return {
        "page_id": page["id"],
        "job_title": job_title,
        "company": company,
        "team": team,
        "cleaned_jd": cleaned_jd,
        "resume": resume,
    }


def update_notion_fields(page_id: str, resume_label: str, score: float, analysis: str) -> bool:
    """更新 Notion 页面的 Resume、Match Score、Match Analysis 字段"""
    url = f"{NOTION_API}/pages/{page_id}"

    # 截断 analysis 到 Notion rich_text 限制 (2000 字符)
    if len(analysis) > 1950:
        analysis = analysis[:1950] + "…"

    body = {
        "properties": {
            "Resume": {
                "select": {"name": resume_label}
            },
            "Match Score": {
                "number": round(score * 100, 1)  # 存为百分比数值
            },
            "Match Analysis": {
                "rich_text": [{"type": "text", "text": {"content": analysis}}]
            },
        }
    }
    try:
        resp = requests.patch(url, headers=NOTION_HEADERS, json=body, timeout=30)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"    ❌ Notion 更新失败: {e}")
        return False


# ═══════════════════════════════════════════════════════════
# MD 报告生成（中文自然语言）
# ═══════════════════════════════════════════════════════════

def format_analysis_text(info: dict, best: dict, top3: list[dict]) -> str:
    """生成一条岗位的中文分析文本（用于 Notion 和 MD 报告）"""
    lines = []

    # 技术覆盖分析
    tech_pct = f"{best['tech_score']:.0%}"
    biz_pct = f"{best['biz_score']:.0%}"
    total_pct = f"{best['total']:.0%}"

    lines.append(
        f"该岗位共检测到 {best['total_requirements']} 项技术需求，"
        f"简历覆盖 {best['satisfied']} 项（技术覆盖率 {tech_pct}）。"
    )

    # OR 组说明
    if best.get('or_groups'):
        or_strs = []
        for g in best['or_groups']:
            or_strs.append(' / '.join(g))
        lines.append(f"其中 OR 关联需求（满足其一即可）：{"; ".join(or_strs)}。")

    # 匹配的关键词
    if best['matched_tech']:
        lines.append(f"匹配的技术关键词：{', '.join(best['matched_tech'])}。")

    # 缺失的关键词
    if best['missing_tech']:
        lines.append(f"缺失的技术关键词：{', '.join(best['missing_tech'])}。")

    # 业务方向
    if best.get('matched_biz'):
        lines.append(f"业务方向匹配：{', '.join(best['matched_biz'])}（覆盖率 {biz_pct}）。")
    if best.get('missing_biz'):
        lines.append(f"业务方向缺失：{', '.join(best['missing_biz'])}。")

    lines.append(f"综合得分：{total_pct}。")

    # 阈值判断
    if best['total'] >= 0.75:
        lines.append("该简历与岗位匹配度达标（≥75%），可直接投递。")
    else:
        lines.append("匹配度低于 75%，建议触发简历重写以补全缺失关键词。")

    return '\n'.join(lines)


def generate_md_report(all_job_results: list[dict], output_path: Path):
    """生成完整的中文自然语言 MD 报告"""
    lines = [
        "# Notion JD 匹配分析报告",
        "",
        f"> 生成时间：{time.strftime('%Y-%m-%d %H:%M')}",
        f"> 匹配算法：确定性关键词覆盖率（无 LLM 参与）",
        f"> 评分公式：总分 = 0.7 × 技术覆盖率 + 0.3 × 业务方向覆盖率",
        f"> OR 处理：JD 中 \"X or Y\" 或 \"X/Y\" 关联的关键词合并为一条需求，满足任一即可",
        "",
        "---",
        "",
    ]

    for idx, job in enumerate(all_job_results, 1):
        info = job['info']
        best = job['best']
        top3 = job['top3']
        analysis = job['analysis']

        company_str = info['company'] or '未知公司'
        team_str = f" · {info['team']}" if info['team'] else ""

        lines.append(f"## {idx}. {company_str}{team_str}")
        lines.append("")
        lines.append(f"**公司：** {company_str}")
        lines.append(f"**岗位：** {info['job_title']}")
        lines.append(f"**推荐简历：** {best['resume_label']}")
        lines.append(f"**匹配分数：** {best['total']:.1%}")
        lines.append("")

        lines.append("### 匹配分析")
        lines.append("")
        lines.append(analysis)
        lines.append("")

        # 候选排名
        lines.append("### 候选简历排名")
        lines.append("")
        for rank, r in enumerate(top3, 1):
            lines.append(f"{rank}. {r['resume_label']} — {r['total']:.1%}（技术 {r['tech_score']:.0%}，业务 {r['biz_score']:.0%}）")
        lines.append("")
        lines.append("---")
        lines.append("")

    content = '\n'.join(lines)
    output_path.write_text(content, encoding='utf-8')
    print(f"\n📄 MD 报告已保存: {output_path}")


# ═══════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════

def main():
    ap = argparse.ArgumentParser(description="Match Notion DB JDs to frozen resume catalog")
    ap.add_argument('--all', action='store_true', help='重新匹配所有 JD（覆盖已有推荐）')
    ap.add_argument('--dry-run', action='store_true', help='只打印结果，不写入 Notion')
    ap.add_argument('--report', action='store_true', help='生成 MD 匹配分析报告')
    ap.add_argument('--top', type=int, default=3, help='显示/记录前 N 名候选（默认 3）')
    args = ap.parse_args()

    if not NOTION_TOKEN or not NOTION_DB_ID:
        print("❌ NOTION_TOKEN 或 NOTION_DB_ID 未配置。请检查 .env 文件。")
        sys.exit(1)

    # 加载冻结简历词库
    if not FROZEN_CATALOG_PATH.exists():
        print(f"❌ 冻结词库不存在: {FROZEN_CATALOG_PATH}")
        print("   请先运行 python3 build_frozen_catalog.py")
        sys.exit(1)

    with open(FROZEN_CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    print(f"📚 加载了 {len(catalog)} 份简历冻结词库\n")

    # 获取 Notion DB 所有页面
    print("🔍 从 Notion DB 获取 Job Applications...\n")
    pages = get_all_pages(NOTION_DB_ID)
    print(f"   找到 {len(pages)} 条记录\n")

    # 逐条匹配
    matched_count = 0
    skipped_count = 0
    no_jd_count = 0
    report_data = []

    for page in pages:
        info = extract_page_info(page)

        if not info['cleaned_jd']:
            no_jd_count += 1
            continue

        # 如果已有推荐且不是 --all 模式，跳过（但 report 模式仍然计算）
        if info['resume'] and not args.all:
            if not args.report:
                skipped_count += 1
                continue

        # 匹配
        results = match_all_resumes(info['cleaned_jd'], catalog)
        if not results:
            print(f"  ⚠️  {info['company']} | {info['job_title']}: 无匹配结果")
            continue

        best = results[0]
        top_n = results[:args.top]

        company_str = info['company'] or '未知'
        team_str = f" · {info['team']}" if info['team'] else ""

        # 生成分析文本
        analysis = format_analysis_text(info, best, top_n)

        # 打印摘要
        score_pct = f"{best['total']:.0%}"
        flag = "✅" if best['total'] >= 0.75 else "⚠️"
        print(f"  {flag} {company_str}{team_str} | {info['job_title']}")
        print(f"     → {best['resume_label']} ({score_pct}, tech={best['tech_score']:.0%}, biz={best['biz_score']:.0%})")
        if best.get('or_groups'):
            print(f"     OR 需求: {['/'.join(g) for g in best['or_groups']]}")

        # 收集报告数据
        report_data.append({
            'info': info,
            'best': best,
            'top3': top_n,
            'analysis': analysis,
        })

        # 写入 Notion
        if info['resume'] and not args.all:
            skipped_count += 1
        elif not args.dry_run:
            if update_notion_fields(info['page_id'], best['resume_label'], best['total'], analysis):
                matched_count += 1
                time.sleep(0.35)  # Notion API 限流
            else:
                print(f"     ❌ 写入失败")
        else:
            matched_count += 1

    print(f"\n🎉 完成!")
    print(f"   匹配并写入: {matched_count}")
    print(f"   已有推荐（跳过）: {skipped_count}")
    print(f"   无 JD（跳过）: {no_jd_count}")

    # 统计
    if report_data:
        scores = [d['best']['total'] for d in report_data]
        above_75 = sum(1 for s in scores if s >= 0.75)
        print(f"\n📊 匹配统计:")
        print(f"   总岗位数: {len(report_data)}")
        print(f"   ≥75% 达标: {above_75} ({above_75/len(report_data):.0%})")
        print(f"   <75% 需重写: {len(report_data) - above_75}")
        print(f"   平均分: {sum(scores)/len(scores):.1%}")
        print(f"   最高分: {max(scores):.1%}")
        print(f"   最低分: {min(scores):.1%}")

    # 生成 MD 报告
    if args.report and report_data:
        report_path = ROOT / "classification" / "notion_match_report.md"
        generate_md_report(report_data, report_path)


if __name__ == "__main__":
    main()
