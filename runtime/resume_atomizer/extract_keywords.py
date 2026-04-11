#!/usr/bin/env python3
"""
extract_keywords.py — 使用 LLM 从每份简历中提取 ATS 关键词和业务方向。

读取 resumes/ 下所有 MD 简历全文，调用 LLM API 做结构化提取，
输出 classification/resume_catalog.json。

可选 --renumber：按 ATS 相似度重新排序并重命名文件。

Usage:
    python3 extract_keywords.py                # 仅提取关键词
    python3 extract_keywords.py --renumber     # 提取 + 重新编号排序
"""

import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

# 加载 .env
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line.startswith('export '):
            line = line[7:]
        if '=' in line and not line.startswith('#'):
            key, val = line.split('=', 1)
            os.environ[key.strip()] = val.strip().strip('"').strip("'")

from openai import OpenAI

ROOT = Path(__file__).parent
RESUME_DIR = ROOT / "resumes"
CATALOG_PATH = ROOT / "classification" / "resume_catalog.json"

EXTRACTION_PROMPT = """你是一个专业的 ATS（Applicant Tracking System）简历分析专家。

请从以下简历全文中提取结构化信息。注意：
1. 完全基于简历内容分析，不要依赖文件名或标题
2. 提取所有出现的技术关键词，不仅限于加粗文字
3. core_stack 只保留该简历最核心、最突出的 3-5 项技术

请严格按以下 JSON 格式输出（不要包含 markdown 代码块标记）：

{
  "hard_keywords": ["所有硬技术关键词：编程语言、框架、工具、平台、协议等"],
  "core_stack": ["该简历最核心的 3-5 项技术"],
  "business_directions": ["业务方向标签，如 security infrastructure, recommendation systems 等"],
  "experience_domains": ["行业/领域，如 e-commerce, ride-hailing, fintech 等"]
}

简历全文：
"""


def call_llm(content: str, max_retries: int = 2) -> dict | None:
    """调用 LLM API 提取关键词"""
    client = OpenAI(
        api_key=os.environ.get("API_KEY", ""),
        base_url=os.environ.get("BASE_URL", ""),
    )
    model = os.environ.get("LLM_MODEL", "kimi-k2.5")

    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是 ATS 简历分析专家。只输出 JSON，不要任何额外文字。"},
                    {"role": "user", "content": EXTRACTION_PROMPT + content}
                ],
                temperature=0.1,
                max_tokens=2000,
            )
            text = response.choices[0].message.content.strip()
            # 去除可能的 markdown 代码块标记
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"    ⚠️  JSON 解析失败 (attempt {attempt+1}): {e}")
            if attempt < max_retries:
                time.sleep(2)
        except Exception as e:
            print(f"    ⚠️  API 调用失败 (attempt {attempt+1}): {e}")
            if attempt < max_retries:
                time.sleep(3)
    return None


def compute_similarity(kw1: set, kw2: set) -> float:
    """Jaccard 相似度"""
    if not kw1 and not kw2:
        return 1.0
    intersection = kw1 & kw2
    union = kw1 | kw2
    return len(intersection) / len(union) if union else 0.0


def cluster_sort(catalog: list) -> list:
    """按 ATS 关键词相似度排序，AI/GenAI 方向优先"""
    # 标记 AI/GenAI 相关简历
    ai_keywords = {'ai', 'genai', 'llm', 'machine learning', 'ml', 'deep learning',
                   'nlp', 'bert', 'gpt', 'transformer', 'neural network',
                   'responsible ai', 'ai ethics', 'generative ai'}

    for item in catalog:
        all_kw = set(k.lower() for k in item.get('hard_keywords', []))
        all_dirs = set(d.lower() for d in item.get('business_directions', []))
        item['_all_kw'] = all_kw
        item['_is_ai'] = bool((all_kw | all_dirs) & ai_keywords)

    # 分为 AI 组和非 AI 组
    ai_group = [item for item in catalog if item['_is_ai']]
    other_group = [item for item in catalog if not item['_is_ai']]

    def greedy_sort(group):
        """贪心排序：每次选择与上一个最相似的"""
        if not group:
            return []
        sorted_list = [group.pop(0)]
        while group:
            last_kw = sorted_list[-1]['_all_kw']
            best_idx = max(range(len(group)),
                          key=lambda i: compute_similarity(last_kw, group[i]['_all_kw']))
            sorted_list.append(group.pop(best_idx))
        return sorted_list

    ai_sorted = greedy_sort(ai_group)
    other_sorted = greedy_sort(other_group)

    result = ai_sorted + other_sorted

    # 清理临时字段
    for item in result:
        item.pop('_all_kw', None)
        item.pop('_is_ai', None)

    return result


def renumber_resumes(catalog: list) -> list:
    """重新编号和重命名简历文件"""
    print("\n🔢 Renumbering resumes...\n")

    # 先把所有文件移到临时名以避免冲突
    temp_dir = RESUME_DIR / "_temp_rename"
    temp_dir.mkdir(exist_ok=True)

    for item in catalog:
        src = RESUME_DIR / item['source_file']
        if src.exists():
            shutil.copy2(src, temp_dir / item['source_file'])

    # 生成新文件名并重命名
    for i, item in enumerate(catalog, 1):
        old_name = item['source_file']
        # 从旧文件名提取描述部分（去掉编号前缀）
        desc_match = re.match(r'^\d+_(.+)$', old_name)
        desc = desc_match.group(1) if desc_match else old_name
        new_name = f"{i:02d}_{desc}"

        src = temp_dir / old_name
        dst = RESUME_DIR / new_name
        if src.exists():
            shutil.copy2(src, dst)
            # 如果旧文件还在 resumes/ 且与新文件名不同，删除旧文件
            old_path = RESUME_DIR / old_name
            if old_path.exists() and old_name != new_name:
                old_path.unlink()

        item['source_file'] = new_name
        item['id'] = i
        print(f"  {old_name} → {new_name}")

    # 清理临时目录
    shutil.rmtree(temp_dir)
    return catalog


def main():
    ap = argparse.ArgumentParser(description="Extract ATS keywords from resumes using LLM")
    ap.add_argument('--renumber', action='store_true', help='Renumber and reorder resumes by ATS similarity')
    ap.add_argument('--dry-run', action='store_true', help='Print extraction results without saving')
    args = ap.parse_args()

    md_files = sorted(RESUME_DIR.glob("*.md"))
    if not md_files:
        print("❌ No .md files found in resumes/")
        sys.exit(1)

    print(f"📝 Extracting ATS keywords from {len(md_files)} resumes via LLM...\n")
    print(f"   Model: {os.environ.get('LLM_MODEL', 'kimi-k2.5')}")
    print(f"   API: {os.environ.get('BASE_URL', 'N/A')}\n")

    catalog = []
    for md_file in md_files:
        md_text = md_file.read_text(encoding='utf-8')
        print(f"  🔍 {md_file.name}...", end="", flush=True)
        result = call_llm(md_text)
        if result:
            entry = {
                'id': len(catalog) + 1,
                'source_file': md_file.name,
                'hard_keywords': result.get('hard_keywords', []),
                'core_stack': result.get('core_stack', []),
                'business_directions': result.get('business_directions', []),
                'experience_domains': result.get('experience_domains', []),
            }
            catalog.append(entry)
            print(f" ✅ ({len(entry['hard_keywords'])} keywords, core: {entry['core_stack']})")
        else:
            print(" ❌ Failed")

    if not catalog:
        print("❌ No keywords extracted.")
        sys.exit(1)

    # 按 ATS 相似度排序（AI/GenAI 优先）
    catalog = cluster_sort(catalog)

    # 重新编号
    for i, item in enumerate(catalog, 1):
        item['id'] = i

    if args.renumber:
        catalog = renumber_resumes(catalog)

    if args.dry_run:
        print(json.dumps(catalog, indent=2, ensure_ascii=False))
        return

    # 保存 catalog
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"\n🎉 Done. Catalog saved to {CATALOG_PATH}")
    print(f"   Total: {len(catalog)} resumes")
    print(f"   AI/GenAI resumes sorted first")

    if args.renumber:
        print(f"   Files renumbered 01-{len(catalog):02d}")


if __name__ == "__main__":
    main()
