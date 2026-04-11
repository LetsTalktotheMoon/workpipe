#!/usr/bin/env python3
"""
build_frozen_catalog.py — 一次性构建冻结的简历关键词词库。

用 notion_match.py 中的统一标准词表扫描所有简历 MD 文件，
输出 classification/resume_keywords_frozen.json。

此文件确认完美后可删除，词库不再修改。

Usage:
    python3 build_frozen_catalog.py
    python3 build_frozen_catalog.py --verbose   # 打印每份简历的详细关键词
"""

import argparse
import json
import re
from pathlib import Path

# 从 notion_match 导入共享的词表和扫描函数
from notion_match import TECH_VOCAB, BIZ_VOCAB, scan_keywords

ROOT = Path(__file__).parent
RESUME_DIR = ROOT / "resumes"
OUTPUT = ROOT / "classification" / "resume_keywords_frozen.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--verbose', '-v', action='store_true', help='打印详细关键词')
    args = ap.parse_args()

    resume_files = sorted(RESUME_DIR.glob('*_Resume.md'))
    if not resume_files:
        print("❌ 没有找到简历文件")
        return

    catalog = []

    for i, f in enumerate(resume_files, 1):
        text = f.read_text(encoding='utf-8')
        # 去掉 "Go (Weiqi)" 引用，避免与 Go 编程语言误匹配
        text = re.sub(r'\bGo\s*\(Weiqi\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\d-Dan\s+Go\b', '', text)
        # 去掉 Additional Information 部分
        text = re.sub(r'##\s*Additional Information.*', '', text, flags=re.DOTALL)
        tech = scan_keywords(text, TECH_VOCAB)
        biz = scan_keywords(text, BIZ_VOCAB)

        entry = {
            'id': i,
            'source_file': f.name,
            'tech_keywords': sorted(tech),
            'business_directions': sorted(biz),
        }
        catalog.append(entry)

        count_str = f"{len(tech)} tech, {len(biz)} biz"
        print(f"  {i:02d} {f.stem}: {count_str}")

        if args.verbose:
            print(f"      tech: {', '.join(sorted(tech))}")
            print(f"      biz:  {', '.join(sorted(biz))}")
            print()

    OUTPUT.parent.mkdir(exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as out:
        json.dump(catalog, out, ensure_ascii=False, indent=2)

    print(f"\n✅ 冻结词库已保存: {OUTPUT}")
    print(f"   共 {len(catalog)} 份简历")

    # 汇总统计
    all_tech = set()
    all_biz = set()
    for item in catalog:
        all_tech.update(item['tech_keywords'])
        all_biz.update(item['business_directions'])
    print(f"   词表覆盖: {len(all_tech)} 种技术关键词, {len(all_biz)} 种业务方向")


if __name__ == '__main__':
    main()
