#!/usr/bin/env python3
"""
build_atom_store.py — Phase 3: 全量去重 + 构建 atom_store.json

读取 parsed_resumes.json，按"只要技术栈不同就不合并"的原则：
- 识别跨简历的 achievement clusters（pick_one）
- 保留每个 bullet 为独立 atom
- 输出 atom_store.json 和 dedup_report.md

Usage:
    python3 build_atom_store.py
"""

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
PARSED = ROOT / "parsed_resumes.json"
OUTPUT = ROOT / "atom_store.json"
REPORT = ROOT / "dedup_report.md"


def extract_fingerprint(text: str) -> set[str]:
    """提取 bullet 的 metric + 关键短语指纹，用于跨简历匹配"""
    fp = set()
    # 百分比
    for m in re.findall(r'(\d+(?:\.\d+)?)\s*%', text):
        fp.add(f'{m}%')
    # 倍数
    for m in re.findall(r'(\d+(?:\.\d+)?)×', text):
        fp.add(f'{m}×')
    # from/to 时间
    for m in re.findall(r'from\s+[~>]?(\d[\d,.]*)\s*(?:min|hour|day|second|ms|business)', text, re.I):
        fp.add(f'from_{m.replace(",", "")}')
    for m in re.findall(r'(?:to|under)\s+[~]?(\d[\d,.]*)\s*(?:min|hour|day|second|ms)', text, re.I):
        fp.add(f'to_{m.replace(",", "")}')
    # 大数
    for m in re.findall(r'(\d+[MBK]\+?)', text):
        fp.add(m)
    # 关键短语
    key_phrases = [
        'optimistic locking', 'state machine', 'dual-layer', 'dual-protocol',
        'ci/cd pipeline', 'github actions', 'gitLab ci',
        'metric library', 'canonical sql',
        'kalman filter', 'sensor fusion', 'haversine', 'cache-line', 'openmp',
        'binary caching', 'validation engine', 'precheck',
        'audit log', 'audit event', 'security event', 'security audit',
        'deployment cycle', 'test coverage', 'unit test coverage',
        'model routing', 'multi-model', 'compliance ticket',
        'approval cycle', 'ticket throughput',
        'schema data model', 'ast-based', 'transformation engine',
        'schema normalization', 'schema translation', 'schema conversion',
        'kafka consumer', 'etl pipeline', 'data pipeline',
        'anomaly detection', 'a/b test', 'a/b experiment',
        'feature-store', 'feature store',
        'binary log', 'log dump', 'log parsing',
        'event log', 'batch processing', 'batch-process',
        'rest api client', 'feature-store payload',
        'kpi framework', 'kpi definition', 'kpi reporting',
        'anomaly flag', 'data poisoning', 'silent data',
        'protocol-agnostic', 'agent deployment',
        'hooks middleware', 'sync/async',
        'prompt engineering', 'pydantic',
        'rag pipeline', 'langchain', 'langgraph',
        'confidence score', 'confidence scoring',
        'opentelemetry', 'datadog', 'slo dashboard',
        'docker', 'kubernetes', 'helm',
        'terraform', 'infrastructure as code',
        'devsecopsgit', 'sast', 'semgrep',
        'hashicorp vault', 'secret', 'zero trust',
        'tls', 'mtls', 'oauth',
        'istio', 'service mesh',
        'grpc', 'protocol buffers', 'protobuf',
        'react', 'next.js', 'typescript', 'tailwindcss',
        'spring boot', 'fastapi',
        'mongodb', 'postgresql', 'redis',
        'airflow', 'spark', 'hive',
    ]
    lower = text.lower()
    for kp in key_phrases:
        if kp in lower:
            fp.add(f'kp:{kp}')
    return fp


def union_find_cluster(bullets: list[dict], threshold_metrics=2, threshold_mixed=1) -> dict[str, list[dict]]:
    """Union-Find 聚类：共享足够多 fingerprint 的 bullets 归为同一 cluster"""
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[a] = b

    for i, b in enumerate(bullets):
        b['_idx'] = i
        parent[i] = i

    for i in range(len(bullets)):
        for j in range(i + 1, len(bullets)):
            if bullets[i]['rid'] == bullets[j]['rid']:
                continue
            shared = bullets[i]['fp'] & bullets[j]['fp']
            metric_shared = {s for s in shared if not s.startswith('kp:')}
            phrase_shared = {s for s in shared if s.startswith('kp:')}
            # 至少2个 metric 重合，或 1个 metric + 1个关键短语
            if (len(metric_shared) >= threshold_metrics or
                (len(metric_shared) >= threshold_mixed and len(phrase_shared) >= 1)):
                union(i, j)

    clusters = defaultdict(list)
    for b in bullets:
        clusters[find(b['_idx'])].append(b)
    return clusters


def build_atom_store():
    data = json.loads(PARSED.read_text(encoding='utf-8'))

    atom_store = {
        "_meta": {
            "version": "1.0",
            "created_at": "2026-03-23",
            "source_resume_count": 22,
            "dedup_strategy": "技术栈不同则不合并，归入 achievement_cluster (pick_one)",
        },
        "identity": {
            "name": "PLACEHOLDER",
            "contact": "PLACEHOLDER",
            "education": [
                {"degree": "M.S. Computer Science (OMSCS)", "institution": "Georgia Institute of Technology", "period": "Expected May 2026"},
                {"degree": "M.S. Information Management (MSIM)", "institution": "University of Illinois Urbana-Champaign", "period": "Expected May 2026"},
                {"degree": "M.A. International Business (Finance)", "institution": "Beijing International Studies University", "period": "Sep 2018 – Jun 2021"},
                {"degree": "B.A. Philosophy & Psychology", "institution": "Beijing Normal University", "period": "Sep 2014 – Jun 2018"},
            ],
            "additional": [
                {"category": "weiqi", "text": "National 2-Dan (China Weiqi Association); 1st Place, 2022 Municipal Open Championship; 3rd Place, 2023 Municipal Open Championship."}
            ]
        },
        "experiences": [],
        "academic_projects": [],
        "summary_atoms": [],
        "atoms": [],
    }

    dedup_report_lines = [
        "# 去重审计报告 (Dedup Report)\n",
        f"生成时间: 2026-03-23\n",
        f"去重策略: 只要硬性技术栈不同，就不合并 → 归入 achievement_cluster (pick_one)\n",
        "---\n",
    ]

    atom_id_counter = {"bt": 0, "dd": 0, "tm": 0, "ac": 0, "sm": 0}
    company_map = {0: "bt", 1: "dd", 2: "tm"}

    def next_atom_id(prefix: str) -> str:
        atom_id_counter[prefix] += 1
        return f"{prefix.upper()}-{atom_id_counter[prefix]:03d}"

    # === 处理 Summary ===
    summary_variants = defaultdict(list)  # position → [(rid, text, keywords)]
    for r in data:
        for pos_idx, s in enumerate(r['summary']):
            summary_variants[pos_idx].append({
                'rid': r['resume_id'],
                'text': s['text'],
                'keywords': s['keywords'],
            })

    role_names = ["profile", "technical_delivery", "collaboration"]
    for pos_idx in range(3):
        variants = summary_variants.get(pos_idx, [])
        atom_id = next_atom_id("sm")
        atom_store["summary_atoms"].append({
            "atom_id": atom_id,
            "position": pos_idx + 1,
            "role": role_names[pos_idx] if pos_idx < len(role_names) else f"slot_{pos_idx}",
            "variants": [{"rid": v['rid'], "text": v['text'], "keywords": v['keywords']} for v in variants],
            "note": "Summary 每份简历都不同，全部作为 variants 保留，下游按目标岗位选取",
        })

    # === 处理 Work Experience ===
    company_info = [
        {
            "exp_id": "exp-bytedance",
            "company": "ByteDance (TikTok)",
            "division": "Security Infra",
            "title": "Software Engineer Intern",
            "location": "San Jose, CA",
            "period": "Jun 2025 – Dec 2025",
        },
        {
            "exp_id": "exp-didi",
            "company": "DiDi IBG",
            "division": "Food Business",
            "title": "Senior Data Analyst",
            "location": "Beijing / Mexico City",
            "period": "Sep 2022 – May 2024",
        },
        {
            "exp_id": "exp-temu",
            "company": "Temu",
            "division": "R&D · Recommendation Infra",
            "title": "Machine Learning Data Analyst",
            "location": "Shanghai",
            "period": "Jun 2021 – Feb 2022",
        },
    ]

    for ci, comp in enumerate(company_info):
        prefix = company_map[ci]
        exp = {**comp, "contribution_groups": []}

        # 收集该公司的所有 bullets，附带来源信息
        all_bullets = []
        group_title_map = defaultdict(list)  # group_title → [(rid, group_type)]

        for r in data:
            rid = r['resume_id']
            if ci >= len(r['work_experience']):
                continue
            pos = r['work_experience'][ci]
            for g in pos.get('contribution_groups', []):
                group_title_map[g['raw_title']].append((rid, g['type']))
                for b in g['bullets']:
                    bullet = {
                        'rid': rid,
                        'text': b['text'],
                        'keywords': b['keywords'],
                        'group_title': g['raw_title'],
                        'group_type': g['type'],
                    }
                    bullet['fp'] = extract_fingerprint(b['text'])
                    all_bullets.append(bullet)

        # 聚类
        clusters = union_find_cluster(all_bullets)

        # 分类：multi-resume clusters vs single-resume bullets
        multi_clusters = {}
        single_bullets = []
        for cid, members in clusters.items():
            rids = set(b['rid'] for b in members)
            if len(rids) > 1:
                multi_clusters[cid] = members
            else:
                single_bullets.extend(members)

        # 记录聚类结果到 dedup report
        dedup_report_lines.append(f"\n## {comp['company']}\n")
        dedup_report_lines.append(f"总 bullets: {len(all_bullets)}, 跨简历 clusters: {len(multi_clusters)}, 独立 bullets: {len(single_bullets)}\n")

        # === 处理 multi-resume clusters → achievement_cluster (pick_one) ===
        cluster_idx = 0
        for cid, members in sorted(multi_clusters.items(), key=lambda x: -len(x[1])):
            cluster_idx += 1
            rids = sorted(set(b['rid'] for b in members))
            shared_fps = set.intersection(*[b['fp'] for b in members]) if members else set()

            # 生成 cluster title
            cluster_title = _generate_cluster_title(members, shared_fps)

            group = {
                "group_id": f"cg-{prefix}-cluster-{cluster_idx:02d}",
                "type": "achievement_cluster",
                "pick_mode": "pick_one",
                "canonical_title": cluster_title,
                "source_resumes": rids,
                "shared_fingerprints": sorted(shared_fps),
                "atom_ids": [],
            }

            dedup_report_lines.append(f"\n### Cluster {cluster_idx}: {cluster_title}\n")
            dedup_report_lines.append(f"来源简历: {rids}\n")
            dedup_report_lines.append(f"共享指纹: {sorted(shared_fps)}\n")

            for b in members:
                aid = next_atom_id(prefix)
                atom = {
                    "atom_id": aid,
                    "parent_exp_id": comp['exp_id'],
                    "parent_group_id": group['group_id'],
                    "text": b['text'],
                    "keywords": b['keywords'],
                    "source_resumes": [b['rid']],
                    "original_group_title": b['group_title'],
                    "original_group_type": b['group_type'],
                    "skill_ids": [],  # Phase 4 填充
                    "universal": False,
                    "angle_tags": [],
                }
                atom_store["atoms"].append(atom)
                group["atom_ids"].append(aid)
                dedup_report_lines.append(f"- `{aid}` (R{b['rid']:02d}): {b['text'][:100]}...\n")

            exp["contribution_groups"].append(group)

        # === 处理 single-resume bullets ===
        # 按 (rid, group_title) 分组
        singles_by_group = defaultdict(list)
        for b in single_bullets:
            singles_by_group[(b['rid'], b['group_title'], b['group_type'])].append(b)

        # 收集所有 group_title 变体
        all_group_titles = defaultdict(list)  # canonical_form → [(rid, raw_title, type)]
        for (rid, title, gtype), bullets in singles_by_group.items():
            all_group_titles[title].append((rid, gtype, bullets))

        for title, entries in all_group_titles.items():
            group_types = set(gt for _, gt, _ in entries)
            primary_type = "core_contributions" if any("core" in t.lower() or "contribution" in t.lower() for t in [title]) else \
                           "named_project" if any("project" in t.lower() for t in [title]) else \
                           "themed_section"

            # 检查是否有多份简历使用相同 title（但 bullets 不重叠）
            all_rids = [rid for rid, _, _ in entries]

            if len(all_rids) > 1:
                # 多份简历使用相同 title，但 bullets 不同 → 也是 pick_all（独立成就）
                pick_mode = "pick_all"
            else:
                pick_mode = "pick_all"

            group = {
                "group_id": f"cg-{prefix}-{_slugify(title)[:30]}",
                "type": primary_type,
                "pick_mode": pick_mode,
                "canonical_title": title,
                "source_resumes": sorted(set(all_rids)),
                "atom_ids": [],
            }

            for rid, gtype, bullets in entries:
                for b in bullets:
                    aid = next_atom_id(prefix)
                    atom = {
                        "atom_id": aid,
                        "parent_exp_id": comp['exp_id'],
                        "parent_group_id": group['group_id'],
                        "text": b['text'],
                        "keywords": b['keywords'],
                        "source_resumes": [b['rid']],
                        "original_group_title": b['group_title'],
                        "original_group_type": b['group_type'],
                        "skill_ids": [],
                        "universal": False,
                        "angle_tags": [],
                    }
                    atom_store["atoms"].append(atom)
                    group["atom_ids"].append(aid)

            exp["contribution_groups"].append(group)

        atom_store["experiences"].append(exp)

    # === 处理 Academic Projects ===
    for r in data:
        for proj in r.get('academic_projects', []):
            acad = {
                "project_id": f"acad-{_slugify(proj['canonical_title'])[:20]}",
                "canonical_title": proj['canonical_title'],
                "course": proj.get('course', ''),
                "institution": "Georgia Tech",
                "source_resumes": [r['resume_id']],
                "atom_ids": [],
            }
            for b in proj['bullets']:
                aid = next_atom_id("ac")
                atom = {
                    "atom_id": aid,
                    "parent_exp_id": "acad",
                    "parent_group_id": acad['project_id'],
                    "text": b['text'],
                    "keywords": b['keywords'],
                    "source_resumes": [r['resume_id']],
                    "original_group_title": proj['canonical_title'],
                    "original_group_type": "academic_project",
                    "skill_ids": [],
                    "universal": False,
                    "angle_tags": ["hpc", "compiler"],
                }
                atom_store["atoms"].append(atom)
                acad["atom_ids"].append(aid)

            atom_store["academic_projects"].append(acad)

    # === 处理 Skills Section ===
    skills_by_resume = {}
    for r in data:
        skills_by_resume[r['resume_id']] = r.get('skills_section', [])

    atom_store["_meta"]["atom_count"] = len(atom_store["atoms"])
    atom_store["_meta"]["cluster_count"] = sum(
        1 for exp in atom_store["experiences"]
        for g in exp["contribution_groups"]
        if g["type"] == "achievement_cluster"
    )
    atom_store["_meta"]["skills_by_resume"] = {
        str(rid): [s['text'] for s in skills]
        for rid, skills in skills_by_resume.items()
    }

    # 写出
    OUTPUT.write_text(json.dumps(atom_store, indent=2, ensure_ascii=False), encoding='utf-8')
    REPORT.write_text('\n'.join(dedup_report_lines), encoding='utf-8')

    print(f"✅ atom_store.json: {len(atom_store['atoms'])} atoms, "
          f"{atom_store['_meta']['cluster_count']} achievement clusters")
    print(f"✅ dedup_report.md 已生成")

    # 统计
    for exp in atom_store['experiences']:
        n_groups = len(exp['contribution_groups'])
        n_atoms = sum(len(g['atom_ids']) for g in exp['contribution_groups'])
        n_clusters = sum(1 for g in exp['contribution_groups'] if g['type'] == 'achievement_cluster')
        print(f"  {exp['company']}: {n_groups} groups ({n_clusters} clusters), {n_atoms} atoms")

    print(f"  Academic: {len(atom_store['academic_projects'])} projects, "
          f"{sum(len(p['atom_ids']) for p in atom_store['academic_projects'])} atoms")
    print(f"  Summary: {len(atom_store['summary_atoms'])} slots")


def _generate_cluster_title(members: list[dict], shared_fps: set) -> str:
    """根据 cluster 成员和共享指纹生成一个描述性 title"""
    texts = [m['text'][:300].lower() for m in members]
    all_text = ' '.join(texts)

    # 基于共享短语推断
    if 'kp:state machine' in shared_fps and 'kp:optimistic locking' in shared_fps:
        return "Distributed Compliance Workflow State Machine"
    if 'kp:validation engine' in shared_fps or 'kp:precheck' in shared_fps or 'kp:dual-layer' in shared_fps:
        return "Dual-Layer Compliance Validation Engine"
    if 'kp:github actions' in shared_fps and ('kp:test coverage' in shared_fps or 'kp:deployment cycle' in shared_fps or 'kp:ci/cd pipeline' in shared_fps):
        if '85%' in shared_fps or 'kp:test coverage' in shared_fps:
            return "GitHub Actions CI/CD Pipeline (Build→SAST→Deploy)"
        if 'to_30' in shared_fps:
            return "GitHub Actions CI/CD & Container Deployment"
        return "GitHub Actions CI/CD Pipeline"
    if 'kp:audit event' in shared_fps or 'kp:security audit' in shared_fps or 'kp:audit log' in shared_fps:
        return "Security Audit Event Ingestion Service"
    if 'kp:transformation engine' in shared_fps or 'kp:schema normalization' in shared_fps or 'kp:schema translation' in shared_fps or 'kp:schema conversion' in shared_fps:
        return "Schema Normalization & Transformation Engine"
    if 'kp:dual-protocol' in shared_fps:
        return "Dual-Protocol API Layer (REST + gRPC)"
    if 'kp:model routing' in shared_fps or 'kp:multi-model' in shared_fps:
        return "Multi-Model LLM Routing Layer"
    if 'kp:metric library' in shared_fps or 'kp:canonical sql' in shared_fps:
        return "Canonical SQL Metric Library"
    if 'kp:anomaly detection' in shared_fps:
        return "Operational Anomaly Detection System"
    if 'kp:haversine' in shared_fps or 'kp:cache-line' in shared_fps or ('14×' in shared_fps and 'from_22' in shared_fps):
        return "C++ Native Performance Extension (ETA Prediction)"
    if 'kp:feature-store' in shared_fps or 'kp:feature store' in shared_fps:
        return "Feature-Store REST API Client"
    if 'kp:a/b test' in shared_fps or 'kp:a/b experiment' in shared_fps:
        if '1B+' in shared_fps:
            return "Large-Scale A/B Experiment Analytics (1B+ Events)"
        return "A/B Experiment Analytics Pipeline"
    if '1B+' in shared_fps and ('kp:spark' in shared_fps or 'kp:hive' in shared_fps):
        return "Large-Scale Data Analytics (HiveQL/SparkSQL, 1B+ Events)"
    # C++ native extension 变体匹配
    if 'c++' in all_text and ('ctypes' in all_text or 'native extension' in all_text) and ('14' in all_text or 'throughput' in all_text):
        return "C++ Native Performance Extension (ETA Prediction)"
    if 'kp:binary log' in shared_fps or 'kp:log parsing' in shared_fps or ('kp:log dump' in shared_fps):
        return "Binary Log Parsing Utility"
    if 'kp:batch processing' in shared_fps or 'kp:batch-process' in shared_fps or 'kp:event log' in shared_fps:
        return "Event Log Batch Processing & Preprocessing"
    if 'kp:etl pipeline' in shared_fps or 'kp:data pipeline' in shared_fps:
        return "ETL / Data Pipeline Engineering"
    if 'kp:kafka consumer' in shared_fps:
        return "Kafka Event Consumer Service"
    if 'kp:docker' in shared_fps and 'kp:kubernetes' in shared_fps:
        return "Container Deployment & Orchestration"
    if 'kp:opentelemetry' in shared_fps or 'kp:slo dashboard' in shared_fps:
        return "Observability & SLO Instrumentation"
    if 'kp:terraform' in shared_fps:
        return "Terraform Infrastructure as Code"
    if 'kp:rag pipeline' in shared_fps:
        return "RAG Pipeline & Policy Classification"
    if 'kp:react' in shared_fps or 'kp:next.js' in shared_fps:
        return "Frontend Portal (React/Next.js)"
    if 'kp:protocol-agnostic' in shared_fps or 'kp:agent deployment' in shared_fps:
        return "Protocol-Agnostic Agent Deployment"
    if 'kp:hooks middleware' in shared_fps or 'kp:sync/async' in shared_fps:
        return "Sync/Async Hooks Middleware"

    # 更多模式匹配
    if 'dual-layer' in all_text and ('validation' in all_text or 'precheck' in all_text):
        return "Dual-Layer Compliance Validation Engine"
    if 'ci/cd' in all_text and 'github actions' in all_text and ('sast' in all_text or 'test coverage' in all_text or '85%' in all_text):
        return "GitHub Actions CI/CD Pipeline (Build→SAST→Deploy)"
    if 'ci/cd' in all_text and 'github actions' in all_text and 'deployment' in all_text:
        return "GitHub Actions CI/CD & Container Deployment"
    if 'containeriz' in all_text and ('kubernetes' in all_text or 'docker' in all_text) and 'deploy' in all_text:
        return "Container Deployment & Orchestration (K8s/Docker)"
    if 'schema' in all_text and ('normalization' in all_text or 'transformation' in all_text or 'translation' in all_text or 'conversion' in all_text):
        return "Schema Normalization & Transformation Engine"
    if 'audit' in all_text and ('event' in all_text or 'log' in all_text) and 'ingest' in all_text:
        return "Security Audit Event Ingestion Service"
    if 'kafka' in all_text and 'consumer' in all_text:
        return "Kafka Event Consumer Service"
    if 'opentelemetry' in all_text or 'slo' in all_text or 'observability' in all_text:
        return "Observability & SLO Instrumentation"
    if 'llm' in all_text and ('routing' in all_text or 'multi-model' in all_text):
        return "Multi-Model LLM Routing Layer"
    if 'helm' in all_text and 'hpa' in all_text and 'kubernetes' in all_text:
        return "Kubernetes Cluster Deployment (Helm/HPA)"
    if 'event log' in all_text and ('batch' in all_text or 'processing' in all_text):
        return "Event Log Batch Processing Pipeline"
    if 'etl' in all_text or 'data pipeline' in all_text:
        return "ETL / Data Pipeline Engineering"
    if 'reporting' in all_text and ('kpi' in all_text or 'metric' in all_text):
        return "KPI Reporting & Analytics Pipeline"
    if 'gitops' in all_text or 'flux' in all_text or 'argocd' in all_text:
        return "GitOps & Continuous Deployment"
    if 'binary log' in all_text or 'log dump' in all_text or 'log parsing' in all_text:
        return "Binary Log Parsing Utility"

    # Fallback: 取第一个成员的关键动作
    first = members[0]['text']
    # 提取动词+宾语
    match = re.match(r'^(?:\*\*\w+\*\*\s+)?(\w+(?:ed|lt|ned|ted|ped|red|sed))\s+(.{20,60}?)(?:\s*[-—;,])', first)
    if match:
        return f"{match.group(1).title()} {match.group(2).strip()}"
    words = first.split()[:8]
    return ' '.join(words) + '...'


def _slugify(text: str) -> str:
    """简单 slugify"""
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')[:40]


if __name__ == "__main__":
    build_atom_store()
