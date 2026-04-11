#!/usr/bin/env python3
"""
update_contacts.py — 批量替换简历中的姓名、邮箱、电话。

读取 profiles.json 中的联系方式配置，将 resumes/ 下所有 MD 简历
替换为指定 profile 的联系方式后输出到 output/{profile_id}/resumes/。
不会覆盖原始 resumes/ 目录。

Usage:
    python3 update_contacts.py                                    # 为所有 profile 生成
    python3 update_contacts.py --profile A  # 指定 profile
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
RESUME_DIR = ROOT / "resumes"
PROFILES_PATH = ROOT.parent / "profiles.json"


def load_profiles(path: Path) -> list[dict]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_current_contact(md_text: str) -> dict:
    """从 MD 简历中提取当前的 name、email、phone"""
    lines = md_text.splitlines()
    info = {'name': '', 'email': '', 'phone': '', 'name_line': -1, 'contact_line': -1}

    for i, line in enumerate(lines):
        stripped = line.strip()
        # 姓名行: # Name
        if stripped.startswith('# ') and not stripped.startswith('## '):
            heading = stripped[2:].strip()
            if heading != 'Professional Summary':
                info['name'] = heading
                info['name_line'] = i
        # 联系方式行: email | phone 或 PLACEHOLDER
        if '@' in stripped and '|' in stripped:
            info['contact_line'] = i
            parts = [p.strip() for p in re.split(r'\s*\|\s*', stripped) if p.strip()]
            for part in parts:
                if re.match(r'^[\w\.\+\-]+@[\w\.\-]+\.\w+$', part):
                    info['email'] = part
                elif re.match(r'^\+?[\d\-\s\(\)\.]{7,}$', part):
                    info['phone'] = part
        elif stripped == 'PLACEHOLDER' and info['name_line'] >= 0 and info['contact_line'] < 0:
            # 脱敏后的联系方式行
            info['contact_line'] = i
    return info


def replace_contact(md_text: str, current: dict, profile: dict) -> str:
    """替换 MD 文本中的姓名、邮箱、电话"""
    lines = md_text.splitlines()

    # 替换姓名
    if current['name_line'] >= 0 and current['name']:
        lines[current['name_line']] = lines[current['name_line']].replace(
            current['name'], profile['name']
        )

    # 替换联系方式行
    if current['contact_line'] >= 0:
        new_contact_parts = []
        if profile.get('email'):
            new_contact_parts.append(profile['email'])
        if profile.get('phone'):
            new_contact_parts.append(profile['phone'])
        lines[current['contact_line']] = ' | '.join(new_contact_parts)

    return '\n'.join(lines)


def process_profile(profile: dict, resume_dir: Path, output_base: Path):
    """为一个 profile 处理所有简历"""
    out_dir = output_base / profile['id'] / "resumes"
    out_dir.mkdir(parents=True, exist_ok=True)

    md_files = sorted(resume_dir.glob("*.md"))
    if not md_files:
        print("❌ No .md files found in resumes/")
        return

    count = 0
    for md_file in md_files:
        md_text = md_file.read_text(encoding='utf-8')
        current = extract_current_contact(md_text)
        new_text = replace_contact(md_text, current, profile)

        out_path = out_dir / md_file.name
        out_path.write_text(new_text, encoding='utf-8')
        count += 1

    print(f"  ✅ Profile [{profile['id']}]: {count} resumes → {out_dir}")


def main():
    ap = argparse.ArgumentParser(description="Batch replace contact info in resumes")
    ap.add_argument('--profile', '-p', default=None, help='Specific profile ID to process')
    ap.add_argument('--profiles-file', default=str(PROFILES_PATH), help='Path to profiles.json')
    args = ap.parse_args()

    profiles = load_profiles(Path(args.profiles_file))
    if not profiles:
        print("❌ No profiles found in profiles.json")
        sys.exit(1)

    output_base = ROOT / "output"

    if args.profile:
        matched = [p for p in profiles if p['id'] == args.profile]
        if not matched:
            print(f"❌ Profile '{args.profile}' not found. Available: {[p['id'] for p in profiles]}")
            sys.exit(1)
        profiles = matched

    print(f"📝 Processing {len(profiles)} profile(s)...\n")
    for profile in profiles:
        process_profile(profile, RESUME_DIR, output_base)

    print(f"\n🎉 Done. Output directories under {output_base}/")


if __name__ == "__main__":
    main()
