#!/usr/bin/env python3
"""
consolidate_atoms.py — 将 410 个 atoms 压缩为 ~100 个 consolidated atoms (catoms)。

两层合并策略：
  第一层：同一"成就"（metrics + 核心动作相同）合并为 1 个 catom
  第二层：catom 内部按文本相似度分 text_variants，相似的做 OR-slot 替换

输入：atom_store.json, project_mapping.json, domain_taxonomy.json
输出：consolidated_atom_store.json, consolidation_report.md

Usage:
    python3 consolidate_atoms.py
"""

import json
import re
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).parent
ATOM_STORE = ROOT / "atom_store.json"
PROJECT_MAPPING = ROOT / "project_mapping.json"
DOMAIN_TAXONOMY = ROOT / "domain_taxonomy.json"
OUTPUT = ROOT / "consolidated_atom_store.json"
REPORT = ROOT / "consolidation_report.md"

# 复用 build_atom_store 的 fingerprint 提取
from build_atom_store import extract_fingerprint, union_find_cluster

# ═══════════════════════════════════════════════════════════
# OR 框架常量
# ═══════════════════════════════════════════════════════════

CANDIDATE_CONTEXT = {
    'exp-bytedance': {
        'title': 'Software Engineer Intern',
        'department': 'Security Infra',
        'duration': '6 months',
        'team_context': 'Security/compliance/infrastructure tooling team',
        'plausible_tech_domains': [
            'security compliance', 'threat detection', 'monitoring',
            'access control', 'audit', 'CI/CD', 'microservices',
            'backend services', 'API development', 'data pipelines',
        ],
    },
    'exp-didi': {
        'title': 'Senior Data Analyst (acting Team Lead)',
        'department': 'IBG Food Business',
        'duration': '2 years',
        'team_context': '13-person cross-functional team (backend, frontend, fullstack, PM, data analysts, LatAm sales/ops). Acted as global spokesperson for Beijing data team. Covered Mexico, Brazil, Chile, Colombia, Costa Rica, Dominican Republic.',
        'plausible_tech_domains': [
            'data analytics', 'ETL pipelines', 'backend services',
            'frontend dashboards', 'API development', 'recommendation',
            'dispatch optimization', 'fraud detection', 'geo-spatial',
            'payment systems', 'cross-border compliance', 'agile/scrum',
            'full-stack development', 'ML/AI integration',
        ],
    },
    'exp-temu': {
        'title': 'ML Data Analyst',
        'department': 'R&D Recommendation Infra',
        'duration': '8 months',
        'team_context': 'Recommendation/search/ads infrastructure team',
        'plausible_tech_domains': [
            'recommendation systems', 'search relevance', 'ads targeting',
            'content moderation', 'ML pipelines', 'data processing',
            'RAG', 'LLM', 'NLP', 'feature engineering',
        ],
    },
    'academic': {
        'title': 'MSCS Student',
        'department': 'Georgia Tech CS',
        'plausible_tech_domains': [
            'systems programming', 'compiler optimization', 'HPC',
            'distributed computing', 'GPU computing', 'ML/AI',
            'web development', 'database systems', 'networking',
        ],
    },
}

TECH_EQUIVALENTS = {
    'kafka': ['rabbitmq', 'pulsar', 'kinesis', 'nats'],
    'postgresql': ['mysql', 'cockroachdb', 'tidb'],
    'redis': ['memcached', 'dragonfly'],
    'kubernetes': ['docker swarm', 'nomad', 'ecs'],
    'react': ['vue', 'angular', 'svelte'],
    'pytorch': ['tensorflow', 'jax'],
    'grpc': ['rest', 'graphql', 'thrift'],
    'prometheus': ['datadog', 'grafana', 'new relic'],
    'github actions': ['gitlab ci', 'jenkins', 'circleci'],
    'terraform': ['pulumi', 'cloudformation', 'cdktf'],
    'spark': ['flink', 'beam', 'dbt'],
    'airflow': ['dagster', 'prefect', 'luigi'],
    'fastapi': ['django', 'flask', 'express'],
    'aws': ['gcp', 'azure'],
    'elasticsearch': ['solr', 'opensearch', 'meilisearch'],
    'selenium': ['cypress', 'playwright', 'puppeteer'],
    'c++': ['c', 'rust'],
    'langchain': ['llamaindex', 'haystack'],
}

SENIORITY_VERB_MAP = {
    'intern': ['Built', 'Implemented', 'Developed', 'Designed', 'Created', 'Configured'],
    'mid': ['Designed', 'Architected', 'Optimized', 'Refactored', 'Streamlined'],
    'senior': ['Led', 'Architected', 'Drove', 'Spearheaded', 'Mentored'],
}


# ═══════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════

def text_similarity(a: str, b: str) -> float:
    """计算两段文本的相似度（SequenceMatcher ratio）"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def extract_tech_terms(text: str) -> set[str]:
    """从 bullet 文本中提取加粗的技术关键词"""
    return set(re.findall(r'\*\*([^*]+)\*\*', text))


def extract_all_tech_mentions(text: str) -> set[str]:
    """从文本中提取所有可能的技术词（加粗 + 常见技术名称）"""
    techs = extract_tech_terms(text)
    # 常见技术名称正则匹配
    tech_patterns = [
        r'\b(Python|Java|Go|C\+\+|Rust|TypeScript|JavaScript|Kotlin|Swift|Scala|SQL)\b',
        r'\b(React|Vue|Angular|Next\.js|FastAPI|Spring Boot|Django|Flask)\b',
        r'\b(Docker|Kubernetes|Terraform|Helm|Istio|ArgoCD)\b',
        r'\b(Kafka|Redis|PostgreSQL|MongoDB|MySQL|DynamoDB|Cassandra|Elasticsearch)\b',
        r'\b(AWS|GCP|Azure)\b',
        r'\b(PyTorch|TensorFlow|LLM|BERT|GPT|RAG|LangChain|LangGraph)\b',
        r'\b(gRPC|REST|GraphQL|Protobuf)\b',
        r'\b(Prometheus|Grafana|Datadog|OpenTelemetry)\b',
        r'\b(GitHub Actions|GitLab CI|Jenkins|CI/CD)\b',
        r'\b(Spark|Airflow|Hive|HiveQL|SparkSQL|Flink|BigQuery)\b',
        r'\b(CUDA|MPI|OpenMP|LLVM)\b',
        r'\b(Selenium|Appium|pytest|JUnit|Cypress)\b',
    ]
    for pattern in tech_patterns:
        for m in re.finditer(pattern, text, re.I):
            techs.add(m.group(0))
    return techs


def diff_two_texts(text_a: str, text_b: str) -> list[dict]:
    """找出两段文本中不同的片段，返回 slot 候选"""
    slots = []
    sm = SequenceMatcher(None, text_a.split(), text_b.split())
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'replace':
            a_segment = ' '.join(text_a.split()[i1:i2])
            b_segment = ' '.join(text_b.split()[j1:j2])
            # 只处理短片段替换（≤ 5 个词），避免大段落差异
            if i2 - i1 <= 5 and j2 - j1 <= 5:
                slots.append({
                    'position': i1,
                    'options': [a_segment, b_segment],
                })
    return slots


def create_or_slots_from_group(texts: list[str]) -> tuple[str, dict]:
    """
    从一组相似文本中提取 OR-slots。
    返回 (base_text_with_placeholders, slots_dict)
    """
    if len(texts) <= 1:
        return texts[0] if texts else "", {}

    # 选最长的作为 base
    base = max(texts, key=len)
    all_slots = {}
    slot_counter = 0

    # 对每个 variant 与 base 做 diff，收集所有差异位置的选项
    position_options = defaultdict(set)
    for t in texts:
        if t == base:
            continue
        diffs = diff_two_texts(base, t)
        for d in diffs:
            pos_key = d['position']
            for opt in d['options']:
                position_options[pos_key].add(opt)

    # 也把 base 自己在这些位置的词加进去
    base_words = base.split()
    for pos_key, opts in position_options.items():
        # 找到 base 在该位置的原始词
        # 从所有 diff 中找到 base 的对应词
        pass  # base 的词已经在 opts 里了（来自 diff_two_texts 的 text_a = base 的情况）

    # 构建 slots
    # 即使差异位置 > 5，也保留前 5 个最有意义的（优先替换技术词）
    if len(position_options) > 5:
        tech_positions = {}
        for pos, opts in position_options.items():
            if any(extract_tech_terms(opt) for opt in opts):
                tech_positions[pos] = opts
        if tech_positions:
            position_options = dict(list(tech_positions.items())[:5])
        else:
            position_options = dict(list(position_options.items())[:3])

    result_text = base
    for pos_key in sorted(position_options.keys(), reverse=True):
        opts = list(position_options[pos_key])
        if len(opts) >= 2:
            slot_name = f"slot_{slot_counter}"
            slot_counter += 1
            # 在 base 文本中替换
            words = result_text.split()
            if pos_key < len(words):
                original_word = words[pos_key]
                if original_word not in opts:
                    opts.insert(0, original_word)
                placeholder = "{" + slot_name + "}"
                words[pos_key] = placeholder
                result_text = ' '.join(words)
                all_slots[slot_name] = {
                    "options": opts,
                    "default": opts[0],
                }

    return result_text, all_slots


def _inject_tech_or_slots(text: str, existing_slots: dict) -> tuple[str, dict]:
    """
    从文本中的加粗技术词生成 OR-slots（基于 TECH_EQUIVALENTS）。
    独立于 text-diff 机制——即使只有 1 个 source atom 也能生成 slots。
    """
    bold_terms = extract_tech_terms(text)  # **xxx** 格式的词
    if not bold_terms:
        return text, existing_slots

    slots = dict(existing_slots)
    slot_counter = len(slots)
    result_text = text

    for term in sorted(bold_terms):  # 排序保证确定性
        term_lower = term.lower()
        equivalents = TECH_EQUIVALENTS.get(term_lower, [])
        if not equivalents:
            continue

        slot_name = f"tech_slot_{slot_counter}"
        slot_counter += 1

        # 在文本中标记该 bold 词为可替换
        # 注意：不替换文本本身，只在 slots 中记录
        slots[slot_name] = {
            "options": [term] + equivalents,
            "default": term,
            "position_hint": f"**{term}**",  # 告诉下游在哪里替换
            "type": "tech_equivalent",
        }

    return result_text, slots


def assign_domains(text: str, keywords: list[str], domain_taxonomy: dict) -> list[str]:
    """根据文本内容和关键词，匹配适用的业务域"""
    combined = (text + " " + " ".join(keywords)).lower()
    matched = []
    for domain_id, domain_info in domain_taxonomy['domains'].items():
        score = sum(1 for kw in domain_info['keywords'] if kw in combined)
        if score >= 2:
            matched.append(domain_id)
        elif score == 1 and len(domain_info['keywords']) <= 5:
            matched.append(domain_id)
    return matched if matched else ['backend_distributed']  # 默认


def infer_best_for(text: str, angle_tags: list[str]) -> list[str]:
    """推断 variant 最适合的方向"""
    if angle_tags:
        return angle_tags[:3]
    # 基于文本内容推断
    text_lower = text.lower()
    directions = []
    if any(w in text_lower for w in ['llm', 'ai', 'model', 'neural', 'rag', 'agent']):
        directions.append('ai')
    if any(w in text_lower for w in ['kubernetes', 'docker', 'terraform', 'ci/cd', 'deploy']):
        directions.append('devops')
    if any(w in text_lower for w in ['api', 'grpc', 'microservice', 'backend', 'service']):
        directions.append('backend')
    if any(w in text_lower for w in ['security', 'compliance', 'audit', 'threat']):
        directions.append('security')
    if any(w in text_lower for w in ['data', 'spark', 'pipeline', 'etl', 'hive', 'sql']):
        directions.append('data')
    if any(w in text_lower for w in ['react', 'frontend', 'ui', 'portal', 'dashboard']):
        directions.append('frontend')
    if any(w in text_lower for w in ['mobile', 'android', 'ios']):
        directions.append('mobile')
    if any(w in text_lower for w in ['test', 'qa', 'selenium', 'coverage']):
        directions.append('qa')
    return directions[:3] if directions else ['backend']


# ═══════════════════════════════════════════════════════════
# 主合并逻辑
# ═══════════════════════════════════════════════════════════

def consolidate():
    store = json.loads(ATOM_STORE.read_text(encoding='utf-8'))
    proj_mapping = json.loads(PROJECT_MAPPING.read_text(encoding='utf-8'))
    domain_tax = json.loads(DOMAIN_TAXONOMY.read_text(encoding='utf-8'))

    atom_map = {a['atom_id']: a for a in store['atoms']}
    report = ["# Atom 压缩报告 (Consolidation Report)\n"]
    report.append(f"原始 atom 数量: {len(store['atoms'])}\n")

    catom_counter = {"bt": 0, "dd": 0, "tm": 0, "ac": 0, "sm": 0}
    prefix_map = {"exp-bytedance": "bt", "exp-didi": "dd", "exp-temu": "tm"}

    def next_catom_id(exp_id: str) -> str:
        prefix = prefix_map.get(exp_id, "bt")
        catom_counter[prefix] += 1
        return f"C-{prefix.upper()}-{catom_counter[prefix]:03d}"

    # 建立 group_id → atoms 映射
    group_atoms = defaultdict(list)
    for a in store['atoms']:
        group_atoms[a['parent_group_id']].append(a)

    # 建立 group_id → group_info 映射
    group_info = {}
    for exp in store['experiences']:
        for cg in exp['contribution_groups']:
            group_info[cg['group_id']] = {
                'exp_id': exp['exp_id'],
                'type': cg['type'],
                'title': cg['canonical_title'],
                'source_resumes': cg.get('source_resumes', []),
                'pick_mode': cg.get('pick_mode', 'pick_all'),
            }

    # 建立 project_mapping 的反向索引：group_id → canonical_project_id
    group_to_canonical = {}
    for proj_id, proj_info in proj_mapping['canonical_projects'].items():
        for gid in proj_info['group_ids']:
            group_to_canonical[gid] = proj_id

    all_catoms = []
    all_catom_groups = []  # 用于 consolidated store 的 contribution_groups

    # ──────────────────────────────────────────
    # Step 1: 处理 achievement_clusters
    # ──────────────────────────────────────────
    report.append("\n## Step 1: Achievement Clusters 合并\n")

    for exp in store['experiences']:
        for cg in exp['contribution_groups']:
            if cg['type'] != 'achievement_cluster':
                continue

            atoms_in_cluster = [atom_map[aid] for aid in cg['atom_ids'] if aid in atom_map]
            if not atoms_in_cluster:
                continue

            catom = _merge_atoms_to_catom(
                atoms_in_cluster,
                catom_id=next_catom_id(exp['exp_id']),
                exp_id=exp['exp_id'],
                achievement_name=cg['canonical_title'],
                domain_tax=domain_tax,
            )
            catom['is_project_bullet'] = False
            catom['original_group_type'] = 'achievement_cluster'
            all_catoms.append(catom)

            report.append(f"- **{cg['canonical_title']}**: {len(atoms_in_cluster)} atoms → 1 catom ({len(catom['text_variants'])} variants)")
            report.append(f"  Source: {cg.get('source_resumes', [])}\n")

    # ──────────────────────────────────────────
    # Step 2: 处理 named_projects (按 canonical mapping 分组)
    # ──────────────────────────────────────────
    report.append("\n## Step 2: Named Projects 合并（按 canonical mapping）\n")

    # 按 canonical project 收集所有 atoms
    canonical_project_atoms = defaultdict(list)
    unmapped_project_atoms = defaultdict(list)  # 未映射的 project group

    for exp in store['experiences']:
        for cg in exp['contribution_groups']:
            if cg['type'] != 'named_project':
                continue
            gid = cg['group_id']
            atoms_in_group = [atom_map[aid] for aid in cg['atom_ids'] if aid in atom_map]

            if gid in group_to_canonical:
                canonical_id = group_to_canonical[gid]
                canonical_project_atoms[canonical_id].extend(atoms_in_group)
            else:
                unmapped_project_atoms[gid].extend(atoms_in_group)

    # 对每个 canonical project，内部再用 fingerprint 聚类
    for proj_id, proj_info in proj_mapping['canonical_projects'].items():
        atoms = canonical_project_atoms.get(proj_id, [])
        if not atoms:
            continue

        # 获取 exp_id（从第一个 atom）
        exp_id = atoms[0]['parent_exp_id']

        # 给每个 atom 加 fingerprint + keywords
        for a in atoms:
            a['fp'] = extract_fingerprint(a['text'])
            a['rid'] = a['source_resumes'][0] if a['source_resumes'] else 0
            a['_bold_kw'] = set(kw.lower() for kw in a.get('keywords', []))
            a['_tech'] = set(t.lower() for t in extract_all_tech_mentions(a['text']))

        # 多策略聚类
        clusters = _aggressive_cluster(atoms)

        report.append(f"\n### Canonical Project: {proj_info['title']}")
        report.append(f"  Groups: {proj_info['group_ids']}")
        report.append(f"  Total atoms: {len(atoms)} → {len(clusters)} clusters\n")

        for cluster_key, cluster_atoms in clusters.items():
            catom = _merge_atoms_to_catom(
                cluster_atoms,
                catom_id=next_catom_id(exp_id),
                exp_id=exp_id,
                achievement_name=proj_info['title'],
                domain_tax=domain_tax,
            )
            catom['is_project_bullet'] = True
            catom['project_group'] = proj_id
            catom['original_group_type'] = 'named_project'
            all_catoms.append(catom)

            report.append(f"  - Cluster ({len(cluster_atoms)} atoms) → 1 catom ({len(catom['text_variants'])} variants)")

    # 处理未映射的 project groups（DiDi/Temu 的项目）
    for gid, atoms in unmapped_project_atoms.items():
        if not atoms:
            continue
        info = group_info.get(gid, {})
        exp_id = info.get('exp_id', atoms[0]['parent_exp_id'])

        catom = _merge_atoms_to_catom(
            atoms,
            catom_id=next_catom_id(exp_id),
            exp_id=exp_id,
            achievement_name=info.get('title', gid),
            domain_tax=domain_tax,
        )
        catom['is_project_bullet'] = True
        catom['project_group'] = gid
        catom['original_group_type'] = 'named_project'
        all_catoms.append(catom)

        report.append(f"\n### Unmapped Project: {info.get('title', gid)}")
        report.append(f"  {len(atoms)} atoms → 1 catom ({len(catom['text_variants'])} variants)\n")

    # ──────────────────────────────────────────
    # Step 3: 处理 core/general/themed 贡献
    # ──────────────────────────────────────────
    report.append("\n## Step 3: Core/General/Themed 贡献合并\n")

    for exp in store['experiences']:
        exp_id = exp['exp_id']

        # 收集所有非 achievement_cluster 且非 named_project 的 atoms
        general_atoms = []
        for cg in exp['contribution_groups']:
            if cg['type'] in ('achievement_cluster', 'named_project'):
                continue
            atoms_in_group = [atom_map[aid] for aid in cg['atom_ids'] if aid in atom_map]
            for a in atoms_in_group:
                a['_group_title'] = cg['canonical_title']
                a['_group_type'] = cg['type']
            general_atoms.extend(atoms_in_group)

        if not general_atoms:
            continue

        report.append(f"\n### {exp['company']}: {len(general_atoms)} general atoms")

        # 多策略聚类：fingerprint + 关键词 + 文本相似度
        for a in general_atoms:
            a['fp'] = extract_fingerprint(a['text'])
            a['rid'] = a['source_resumes'][0] if a['source_resumes'] else 0
            a['_bold_kw'] = set(kw.lower() for kw in a.get('keywords', []))
            a['_tech'] = set(t.lower() for t in extract_all_tech_mentions(a['text']))

        clusters = _aggressive_cluster(general_atoms)

        report.append(f"  → {len(clusters)} clusters\n")

        for cluster_key, cluster_atoms in clusters.items():
            achievement_name = _infer_achievement_name(cluster_atoms)
            catom = _merge_atoms_to_catom(
                cluster_atoms,
                catom_id=next_catom_id(exp_id),
                exp_id=exp_id,
                achievement_name=achievement_name,
                domain_tax=domain_tax,
            )
            catom['is_project_bullet'] = False
            catom['original_group_type'] = cluster_atoms[0].get('_group_type', 'general')
            all_catoms.append(catom)

    # ──────────────────────────────────────────
    # Step 4: 处理 academic projects
    # ──────────────────────────────────────────
    report.append("\n## Step 4: Academic Projects (保持不变)\n")

    for proj in store.get('academic_projects', []):
        atoms = [atom_map[aid] for aid in proj.get('atom_ids', []) if aid in atom_map]
        if not atoms:
            continue
        catom = _merge_atoms_to_catom(
            atoms,
            catom_id=f"C-AC-{catom_counter['ac'] + 1:03d}",
            exp_id="academic",
            achievement_name=proj.get('canonical_title', 'Academic Project'),
            domain_tax=domain_tax,
        )
        catom_counter['ac'] += 1
        catom['is_project_bullet'] = True
        catom['project_group'] = 'academic'
        catom['original_group_type'] = 'academic_project'
        all_catoms.append(catom)
        report.append(f"- {proj.get('canonical_title', 'Academic')}: {len(atoms)} atoms → 1 catom\n")

    # ──────────────────────────────────────────
    # Step 5: 处理 summary atoms
    # ──────────────────────────────────────────
    report.append("\n## Step 5: Summary Atoms\n")

    summary_catoms = []
    for sa in store.get('summary_atoms', []):
        variants = sa.get('variants', [])
        catom_counter['sm'] += 1
        summary_catom = {
            "catom_id": f"C-SM-{catom_counter['sm']:03d}",
            "parent_exp_id": "summary",
            "achievement": f"summary-{sa.get('role', 'slot')}",
            "text_variants": [],
            "domain_options": [],
            "scene": "summary",
            "skill_pool": [],
            "angle_tags": [],
            "metrics": {},
            "source_atom_ids": [sa['atom_id']],
            "is_project_bullet": False,
            "original_group_type": "summary",
            "summary_role": sa.get('role', ''),
            "summary_position": sa.get('position', 0),
        }

        # 按文本相似度分组 variants
        variant_groups = _group_by_similarity([v['text'] for v in variants], threshold=0.7)

        for vg_idx, vg_indices in enumerate(variant_groups):
            vg_texts = [variants[i]['text'] for i in vg_indices]
            vg_resumes = [variants[i]['rid'] for i in vg_indices]

            base_text, slots = create_or_slots_from_group(vg_texts)
            best_for = []
            # 从文本推断方向
            for t in vg_texts[:1]:
                best_for = infer_best_for(t, [])

            summary_catom['text_variants'].append({
                "variant_id": f"v{vg_idx + 1}",
                "text": base_text,
                "slots": slots,
                "best_for": best_for,
                "source_resumes": vg_resumes,
            })

        summary_catoms.append(summary_catom)
        report.append(f"- Summary {sa.get('role', '?')}: {len(variants)} variants → {len(summary_catom['text_variants'])} grouped variants\n")

    # ──────────────────────────────────────────
    # 组装输出
    # ──────────────────────────────────────────
    consolidated_store = {
        "_meta": {
            "version": "2.0",
            "created_at": "2026-03-24",
            "source_atom_count": len(store['atoms']),
            "consolidated_catom_count": len(all_catoms),
            "summary_catom_count": len(summary_catoms),
            "total_catom_count": len(all_catoms) + len(summary_catoms),
            "compression_ratio": f"{len(store['atoms'])} → {len(all_catoms) + len(summary_catoms)}",
            "strategy": "两层合并: 同成就→catom, 内部按句式→variants, 相似variants→OR-slots",
        },
        "identity": store['identity'],
        "experiences": store['experiences'],  # 保留原始 experience 结构
        "academic_projects": store.get('academic_projects', []),
        "summary_catoms": summary_catoms,
        "catoms": all_catoms,
    }

    # 写入
    OUTPUT.write_text(json.dumps(consolidated_store, ensure_ascii=False, indent=2), encoding='utf-8')
    REPORT.write_text('\n'.join(report), encoding='utf-8')

    # 统计
    total = len(all_catoms) + len(summary_catoms)
    total_variants = sum(len(c['text_variants']) for c in all_catoms) + sum(len(c['text_variants']) for c in summary_catoms)

    print(f"✅ consolidated_atom_store.json: {total} catoms (from {len(store['atoms'])} atoms)")
    print(f"   Work/Academic catoms: {len(all_catoms)}")
    print(f"   Summary catoms: {len(summary_catoms)}")
    print(f"   Total text variants: {total_variants}")
    print(f"   Compression: {len(store['atoms'])} → {total} ({100 - total / len(store['atoms']) * 100:.1f}% reduction)")
    print(f"✅ consolidation_report.md: {len(report)} lines")

    # 按公司统计
    by_exp = defaultdict(int)
    for c in all_catoms:
        by_exp[c['parent_exp_id']] += 1
    for exp_id, count in by_exp.items():
        print(f"   {exp_id}: {count} catoms")


def _aggressive_cluster(atoms: list[dict]) -> dict[int, list[dict]]:
    """
    多策略聚类：fingerprint + 关键词 + 文本相似度。
    策略优先级（需要满足至少一条）：
    1. 共享 2+ metric fingerprints 或 1 metric + 1 key phrase
    2. 共享 2+ 非泛化 bold keywords + 文本相似度 > 0.35
    3. 文本相似度 > 0.55（足够高时直接合并）
    """
    n = len(atoms)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[a] = b

    # 泛化关键词/技术 — 太常见不能作为聚类信号
    GENERIC_KW = {'python', 'sql', 'api', 'data', 'c++', 'go', 'java', 'javascript',
                  'typescript', 'linux', 'git', 'aws', 'docker', 'kubernetes', 'rest'}

    for i in range(n):
        for j in range(i + 1, n):
            if atoms[i]['rid'] == atoms[j]['rid']:
                continue

            merged = False

            # 策略1: fingerprint 匹配（最可靠）
            shared_fp = atoms[i]['fp'] & atoms[j]['fp']
            metric_shared = {s for s in shared_fp if not s.startswith('kp:')}
            phrase_shared = {s for s in shared_fp if s.startswith('kp:')}
            if len(metric_shared) >= 2 or (len(metric_shared) >= 1 and len(phrase_shared) >= 1):
                merged = True

            # 策略2: 共享 2+ 非泛化 bold keywords + 最低相似度保障
            if not merged:
                shared_kw = atoms[i]['_bold_kw'] & atoms[j]['_bold_kw']
                specific_shared = shared_kw - GENERIC_KW
                if len(specific_shared) >= 2:
                    sim = text_similarity(atoms[i]['text'], atoms[j]['text'])
                    if sim > 0.35:
                        merged = True

            # 策略3: 高文本相似度（直接合并）
            if not merged:
                sim = text_similarity(atoms[i]['text'], atoms[j]['text'])
                if sim > 0.55:
                    merged = True

            if merged:
                union(i, j)

    clusters = defaultdict(list)
    for i, a in enumerate(atoms):
        clusters[find(i)].append(a)
    return clusters


def _merge_atoms_to_catom(
    atoms: list[dict],
    catom_id: str,
    exp_id: str,
    achievement_name: str,
    domain_tax: dict,
) -> dict:
    """将一组 atoms 合并为一个 consolidated atom (catom)"""

    # 收集所有文本
    texts = [a['text'] for a in atoms]
    all_keywords = []
    all_skill_ids = set()
    all_angle_tags = set()
    all_source_resumes = set()
    all_source_atom_ids = []
    all_metrics = {}

    for a in atoms:
        all_keywords.extend(a.get('keywords', []))
        all_skill_ids.update(a.get('skill_ids', []))
        all_angle_tags.update(a.get('angle_tags', []))
        all_source_resumes.update(a.get('source_resumes', []))
        all_source_atom_ids.append(a['atom_id'])
        # 提取 metrics
        fp = extract_fingerprint(a['text'])
        for f in fp:
            if not f.startswith('kp:'):
                all_metrics[f] = True

    # 第二层：按文本相似度分组 → variants
    variant_groups = _group_by_similarity(texts, threshold=0.7)

    text_variants = []
    for vg_idx, vg_indices in enumerate(variant_groups):
        vg_texts = [texts[i] for i in vg_indices]
        vg_atoms = [atoms[i] for i in vg_indices]
        vg_resumes = []
        for a in vg_atoms:
            vg_resumes.extend(a.get('source_resumes', []))

        # 尝试 OR-slot 合并
        base_text, slots = create_or_slots_from_group(vg_texts)

        # 如果 diff 没产生 slots，从 bold 技术词生成 tech-equivalent slots
        if not slots:
            base_text, slots = _inject_tech_or_slots(base_text, slots)

        # 推断 best_for
        vg_angle_tags = set()
        for a in vg_atoms:
            vg_angle_tags.update(a.get('angle_tags', []))
        best_for = infer_best_for(base_text, list(vg_angle_tags))

        text_variants.append({
            "variant_id": f"v{vg_idx + 1}",
            "text": base_text,
            "slots": slots,
            "best_for": best_for,
            "source_resumes": sorted(set(vg_resumes)),
            "source_atom_ids": [a['atom_id'] for a in vg_atoms],
        })

    # 推断 scene
    scene = _classify_scene(texts[0]) if texts else "backend_service"

    # 分配 domains
    combined_text = " ".join(texts[:3])
    combined_kw = " ".join(list(set(all_keywords))[:10])
    domains = assign_domains(combined_text, list(set(all_keywords)), domain_tax)

    # ── OR 框架扩展 ──

    # a) tech_or_pool: 从所有 source atoms 收集技术词并扩展等价替换
    all_tech_mentions = set()
    for a in atoms:
        all_tech_mentions.update(extract_all_tech_mentions(a['text']))
    tech_or_pool = {}
    for tech in all_tech_mentions:
        tech_lower = tech.lower()
        equivalents = TECH_EQUIVALENTS.get(tech_lower, [])
        if equivalents:
            tech_or_pool[tech_lower] = equivalents
        else:
            tech_or_pool[tech_lower] = []

    # b) domain_or_pool: 从 angle_tags 收集并基于候选人经历扩展
    all_domains = set(all_angle_tags)
    all_domains.update(domains)  # 包含 domain_taxonomy 匹配结果
    if exp_id in CANDIDATE_CONTEXT:
        plausible = CANDIDATE_CONTEXT[exp_id]['plausible_tech_domains']
        for domain in plausible:
            all_domains.add(domain)

    # c) seniority_variants: 推断当前职级，为各级别推荐动词
    first_text = atoms[0]['text']
    first_verb = first_text.split()[0].rstrip(',').rstrip(':')
    current_seniority = 'mid'  # 默认
    for level, verbs in SENIORITY_VERB_MAP.items():
        if first_verb in verbs:
            current_seniority = level
            break
    seniority_variants = {}
    for level, verbs in SENIORITY_VERB_MAP.items():
        seniority_variants[level] = verbs[0]  # 推荐首选动词
    seniority_variants['_detected'] = current_seniority

    # d) source_resume_ids: 记录方向来源
    source_resume_ids = sorted(all_source_resumes)

    return {
        "catom_id": catom_id,
        "parent_exp_id": exp_id,
        "achievement": achievement_name,
        "text_variants": text_variants,
        "domain_options": domains,
        "tech_or_pool": tech_or_pool,
        "domain_or_pool": sorted(all_domains),
        "seniority_variants": seniority_variants,
        "scene": scene,
        "skill_pool": sorted(all_skill_ids),
        "angle_tags": sorted(all_angle_tags),
        "metrics": all_metrics,
        "source_atom_ids": all_source_atom_ids,
        "source_resumes": sorted(all_source_resumes),
        "source_resume_ids": source_resume_ids,
        "is_project_bullet": False,
    }


def _group_by_similarity(texts: list[str], threshold: float = 0.7) -> list[list[int]]:
    """
    按文本相似度分组。相似度 > threshold 的归为一组。
    返回: [[idx1, idx2], [idx3], ...]
    """
    n = len(texts)
    if n == 0:
        return []
    if n == 1:
        return [[0]]

    # Union-Find
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[a] = b

    for i in range(n):
        for j in range(i + 1, n):
            if text_similarity(texts[i], texts[j]) > threshold:
                union(i, j)

    groups = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(i)
    return list(groups.values())


def _classify_scene(text: str) -> str:
    """基于文本内容推断业务场景（复用 transplant_resume.py 的逻辑）"""
    text_lower = text.lower()
    scene_signals = {
        "backend_service": ["service", "api", "endpoint", "backend", "server", "microservice", "grpc", "handler"],
        "data_pipeline": ["pipeline", "etl", "data", "warehouse", "batch", "stream", "query", "schema", "sql"],
        "ml_training": ["model", "train", "neural", "inference", "predict", "ml", "ai", "llm", "rag"],
        "frontend_app": ["frontend", "ui", "portal", "dashboard", "component", "react", "browser"],
        "devops_infra": ["deploy", "infrastructure", "monitor", "ci", "cd", "cluster", "kubernetes", "terraform"],
        "mobile": ["mobile", "app", "android", "ios", "device"],
        "qa_automation": ["test", "coverage", "regression", "e2e", "qa", "selenium", "appium"],
    }
    scores = {}
    for scene, signals in scene_signals.items():
        scores[scene] = sum(1 for s in signals if s in text_lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "backend_service"


def _infer_achievement_name(atoms: list[dict]) -> str:
    """从一组 atoms 推断成就名称"""
    if len(atoms) == 1:
        # 单个 atom，用前 60 个字符
        text = atoms[0]['text']
        # 去掉 markdown 格式
        clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        return clean[:60].strip() + ("..." if len(clean) > 60 else "")

    # 多个 atoms，尝试用 fingerprint 中的关键短语
    fps = set()
    for a in atoms:
        fp = extract_fingerprint(a['text'])
        fps.update(f for f in fp if f.startswith('kp:'))

    if fps:
        # 用最具描述性的 key phrase
        phrases = [f[3:].title() for f in sorted(fps)]
        return " & ".join(phrases[:2])

    # 回退：第一个 atom 的缩写
    text = atoms[0]['text']
    clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    return clean[:60].strip() + ("..." if len(clean) > 60 else "")


if __name__ == "__main__":
    consolidate()
