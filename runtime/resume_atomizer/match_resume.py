#!/usr/bin/env python3
"""
match_resume.py — JD 匹配 + LLM 微调简历。

从 JD 中提取核心技术栈和业务方向，匹配最适配的简历。
如核心技术栈缺失或业务方向不一致，调用 LLM 微调后生成新简历 PDF。

Usage:
    python3 match_resume.py --jd path/to/jd.md
    python3 match_resume.py --jd path/to/jd.md --auto-tune   # 自动微调
"""

import argparse
import json
import os
import re
import subprocess
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
TEX_DIR = ROOT / "output" / "tex"
PDF_DIR = ROOT / "output" / "pdf"

JD_EXTRACTION_PROMPT = """你是一个专业的 ATS（Applicant Tracking System）JD 分析专家。

请从以下 Job Description 中提取结构化信息。请严格按以下 JSON 格式输出（不要包含 markdown 代码块标记）：

{
  "job_title": "职位名称",
  "required_stack": ["必须的核心技术栈，3-8 项"],
  "preferred_stack": ["加分项技术"],
  "business_direction": "业务方向描述",
  "seniority": "junior/mid/senior"
}

JD 全文：
"""

TUNE_PROMPT = """你是一个简历微调专家。请基于以下简历和 JD，对简历做最小幅度的调整，使其更好地匹配 JD 的核心技术栈和业务方向。

规则：
1. 只做「微微调」—— 调整措辞、突出已有技能、调整顺序
2. 绝不编造不存在的经历或技能
3. 可以调整 Professional Summary 中的业务方向表述
4. 可以在 Skills 中重新排列已有技能的顺序
5. 可以微调 bullet point 中的关键词以更贴合 JD
6. 保持完全相同的 Markdown 格式结构
7. 保持姓名、联系方式、教育经历、Additional Information 完全不变

JD 核心需求：
- 核心技术栈: {required_stack}
- 业务方向: {business_direction}

请直接输出完整的微调后 Markdown 简历（不要解释，不要代码块标记）：

原始简历：
{resume_content}
"""


def get_llm_client():
    return OpenAI(
        api_key=os.environ.get("API_KEY", ""),
        base_url=os.environ.get("BASE_URL", ""),
    )


def call_llm(prompt: str, system: str = "", max_retries: int = 2) -> str | None:
    """调用 LLM API"""
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
                max_tokens=4000,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"  ⚠️  API 调用失败 (attempt {attempt+1}): {e}")
            if attempt < max_retries:
                time.sleep(3)
    return None


def extract_jd_keywords(jd_text: str) -> dict | None:
    """从 JD 中提取技术栈和业务方向"""
    text = call_llm(
        JD_EXTRACTION_PROMPT + jd_text,
        system="你是 ATS JD 分析专家。只输出 JSON，不要任何额外文字。"
    )
    if not text:
        return None
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"  ❌ JD JSON 解析失败: {e}")
        return None


def match_catalog(jd_info: dict, catalog: list) -> list:
    """匹配 catalog 中的简历，返回排序后的结果"""
    required = set(k.lower() for k in jd_info.get('required_stack', []))
    preferred = set(k.lower() for k in jd_info.get('preferred_stack', []))
    biz_dir = jd_info.get('business_direction', '').lower()

    results = []
    for item in catalog:
        resume_kw = set(k.lower() for k in item.get('hard_keywords', []))
        resume_core = set(k.lower() for k in item.get('core_stack', []))
        resume_dirs = ' '.join(d.lower() for d in item.get('business_directions', []))
        resume_domains = ' '.join(d.lower() for d in item.get('experience_domains', []))

        # 核心技术栈匹配
        required_matched = required & resume_kw
        required_score = len(required_matched) / len(required) if required else 1.0

        # 加分项匹配
        preferred_matched = preferred & resume_kw
        preferred_score = len(preferred_matched) / len(preferred) if preferred else 0.0

        # 业务方向匹配（模糊）
        biz_words = set(biz_dir.split())
        dir_words = set(resume_dirs.split()) | set(resume_domains.split())
        biz_score = len(biz_words & dir_words) / len(biz_words) if biz_words else 0.0

        # 综合分
        total = 0.6 * required_score + 0.15 * preferred_score + 0.25 * biz_score

        # 核心技术栈是否全部命中
        core_full_match = required.issubset(resume_kw)

        results.append({
            'id': item['id'],
            'source_file': item['source_file'],
            'score': round(total, 3),
            'required_score': round(required_score, 3),
            'core_full_match': core_full_match,
            'matched_required': sorted(required_matched),
            'missing_required': sorted(required - resume_kw),
            'matched_preferred': sorted(preferred_matched),
            'biz_score': round(biz_score, 3),
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def tune_resume(resume_path: Path, jd_info: dict) -> Path | None:
    """微调简历并保存为新文件"""
    md_text = resume_path.read_text(encoding='utf-8')

    prompt = TUNE_PROMPT.format(
        required_stack=', '.join(jd_info.get('required_stack', [])),
        business_direction=jd_info.get('business_direction', ''),
        resume_content=md_text,
    )

    print(f"  🔧 调用 LLM 微调 {resume_path.name}...")
    result = call_llm(prompt, system="你是简历微调专家。直接输出完整的 Markdown 简历。")
    if not result:
        return None

    # 去除可能的 markdown 代码块标记
    result = re.sub(r'^```(?:markdown)?\s*\n', '', result)
    result = re.sub(r'\n\s*```$', '', result)

    # 确定新文件编号
    existing = sorted(RESUME_DIR.glob("*.md"))
    max_num = 0
    for f in existing:
        m = re.match(r'^(\d+)_', f.name)
        if m:
            max_num = max(max_num, int(m.group(1)))

    # 从 JD title 生成描述
    jd_title = jd_info.get('job_title', 'Custom')
    desc = re.sub(r'[^\w\s-]', '', jd_title).strip().replace(' ', '_')
    new_name = f"{max_num + 1:02d}_{desc}_Resume.md"
    new_path = RESUME_DIR / new_name

    new_path.write_text(result, encoding='utf-8')
    print(f"  ✅ 新简历保存: {new_name}")

    # 更新 catalog
    if CATALOG_PATH.exists():
        with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
        catalog.append({
            'id': max_num + 1,
            'source_file': new_name,
            'hard_keywords': jd_info.get('required_stack', []) + jd_info.get('preferred_stack', []),
            'core_stack': jd_info.get('required_stack', [])[:5],
            'business_directions': [jd_info.get('business_direction', '')],
            'experience_domains': [],
            'tuned_from': resume_path.name,
        })
        with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
        print(f"  ✅ Catalog 已更新")

    return new_path


def build_pdf(md_path: Path) -> Path | None:
    """构建单份简历的 PDF"""
    from md_to_tex import convert_file

    TEX_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    try:
        tex_path = convert_file(str(md_path), str(TEX_DIR))
        result = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-output-directory", str(PDF_DIR), tex_path],
            capture_output=True, text=True, timeout=60
        )
        pdf_name = Path(tex_path).with_suffix('.pdf').name
        pdf_path = PDF_DIR / pdf_name
        if pdf_path.exists():
            # 清理辅助文件
            for ext in [".aux", ".log", ".out", ".fls", ".fdb_latexmk"]:
                junk = PDF_DIR / Path(tex_path).with_suffix(ext).name
                if junk.exists():
                    junk.unlink()
            print(f"  ✅ PDF 生成: {pdf_path}")
            return pdf_path
    except Exception as e:
        print(f"  ❌ PDF 构建失败: {e}")
    return None


def main():
    ap = argparse.ArgumentParser(description="Match JD to resumes and optionally tune")
    ap.add_argument('--jd', required=True, help='Path to JD file (.md or .txt)')
    ap.add_argument('--auto-tune', action='store_true', help='Auto-tune best match if no perfect match')
    ap.add_argument('--top', type=int, default=3, help='Number of top matches to show')
    args = ap.parse_args()

    # 读取 JD
    jd_path = Path(args.jd)
    if not jd_path.exists():
        print(f"❌ JD file not found: {args.jd}")
        sys.exit(1)
    jd_text = jd_path.read_text(encoding='utf-8')

    # 加载 catalog
    if not CATALOG_PATH.exists():
        print(f"❌ Catalog not found. Run `python3 extract_keywords.py` first.")
        sys.exit(1)
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    # 提取 JD 关键词
    print("🔍 分析 JD...")
    jd_info = extract_jd_keywords(jd_text)
    if not jd_info:
        print("❌ JD 分析失败")
        sys.exit(1)

    print(f"\n📋 JD 分析结果:")
    print(f"   职位: {jd_info.get('job_title', 'N/A')}")
    print(f"   核心技术栈: {', '.join(jd_info.get('required_stack', []))}")
    print(f"   加分项: {', '.join(jd_info.get('preferred_stack', []))}")
    print(f"   业务方向: {jd_info.get('business_direction', 'N/A')}")

    # 匹配
    results = match_catalog(jd_info, catalog)
    top_results = results[:args.top]

    print(f"\n🏆 Top {args.top} 匹配结果:\n")
    for i, r in enumerate(top_results, 1):
        status = "✅ 核心全部命中" if r['core_full_match'] else "⚠️  缺失核心技术"
        print(f"  {i}. [{r['score']:.1%}] {r['source_file']}")
        print(f"     {status}")
        print(f"     Required: {r['required_score']:.0%} matched ({', '.join(r['matched_required']) or 'none'})")
        if r['missing_required']:
            print(f"     Missing: {', '.join(r['missing_required'])}")
        print(f"     Biz match: {r['biz_score']:.0%}")
        print()

    # 判断是否需要微调
    best = top_results[0] if top_results else None
    if best and best['core_full_match'] and best['biz_score'] >= 0.5:
        print(f"✅ 推荐直接使用: {best['source_file']} (score: {best['score']:.1%})")
    elif args.auto_tune and best:
        print(f"🔧 核心技术栈未完全匹配或业务方向不一致，开始微调...")
        resume_path = RESUME_DIR / best['source_file']
        if not resume_path.exists():
            print(f"❌ Resume file not found: {resume_path}")
            sys.exit(1)

        new_path = tune_resume(resume_path, jd_info)
        if new_path:
            pdf_path = build_pdf(new_path)
            if pdf_path:
                print(f"\n🎉 微调完成! PDF: {pdf_path}")
            else:
                print(f"\n⚠️  微调完成但 PDF 构建失败。MD 文件: {new_path}")
    elif best and not best['core_full_match']:
        print(f"💡 最佳匹配缺少核心技术: {', '.join(best['missing_required'])}")
        print(f"   使用 --auto-tune 自动微调")


if __name__ == "__main__":
    main()
