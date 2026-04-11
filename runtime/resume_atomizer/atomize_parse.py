#!/usr/bin/env python3
"""
atomize_parse.py — Phase 1: 机械解析 22 份简历 Markdown 文件。

读取 auto-cv/resumes/*.md，输出 parsed_resumes.json，
包含每份简历的结构化拆解（Summary / Work / Academic Projects / Skills / Education / Additional）。

Usage:
    python3 atomize_parse.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
RESUME_DIR = ROOT.parent / "resumes"
OUTPUT = ROOT / "parsed_resumes.json"


def extract_bold_keywords(text: str) -> list[str]:
    """提取 **加粗** 关键词"""
    return re.findall(r'\*\*([^*]+)\*\*', text)


def strip_bold(text: str) -> str:
    """去掉 markdown 加粗标记，保留内容"""
    return re.sub(r'\*\*([^*]+)\*\*', r'\1', text)


def parse_resume(filepath: Path) -> dict:
    """解析单份简历 MD 文件，返回结构化 dict"""
    text = filepath.read_text(encoding='utf-8')
    lines = text.split('\n')

    resume_id = int(filepath.name.split('_')[0])
    resume_label = filepath.stem  # 去掉 .md

    result = {
        "resume_id": resume_id,
        "source_file": filepath.name,
        "label": resume_label,
        "identity": {"name": "", "contact": ""},
        "summary": [],
        "work_experience": [],
        "academic_projects": [],
        "skills_section": [],
        "education": [],
        "additional": [],
    }

    # 状态机解析
    current_section = None  # summary / work / academic_projects / skills / education / additional
    current_position = None  # 当前工作经历
    current_group = None     # 当前 contribution_group（项目或Core标题）
    current_bullets = []     # 当前正在收集的 bullets

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # --- 识别 H1 (# Name) ---
        if line.startswith('# ') and not line.startswith('## '):
            # 第一个 H1 是名字
            if not result["identity"]["name"]:
                result["identity"]["name"] = line[2:].strip()
                # 下一行通常是 contact
                if i + 1 < len(lines) and not lines[i + 1].startswith('#'):
                    contact_line = lines[i + 1].strip()
                    if contact_line and contact_line != '---':
                        result["identity"]["contact"] = contact_line
            i += 1
            continue

        # --- 识别 H2 (## Section) ---
        if line.startswith('## ') and not line.startswith('### '):
            # 先保存之前的状态
            # 如果当前在 academic_projects 且有未 flush 的 group
            if current_group and current_group.get("type") == "academic_project":
                current_group["bullets"] = current_bullets[:]
                result["academic_projects"].append(current_group)
            else:
                _flush_group(current_position, current_group, current_bullets)
            current_group = None
            current_bullets = []

            section_title = line[3:].strip()

            if 'summary' in section_title.lower():
                current_section = 'summary'
                _flush_position(result, current_position)
                current_position = None
            elif 'work experience' in section_title.lower():
                current_section = 'work'
                _flush_position(result, current_position)
                current_position = None
            elif 'academic project' in section_title.lower():
                current_section = 'academic_projects'
                _flush_position(result, current_position)
                current_position = None
            elif 'skill' in section_title.lower():
                current_section = 'skills'
                _flush_position(result, current_position)
                current_position = None
            elif 'education' in section_title.lower():
                current_section = 'education'
                _flush_position(result, current_position)
                current_position = None
            elif 'additional' in section_title.lower():
                current_section = 'additional'
                _flush_position(result, current_position)
                current_position = None
            else:
                current_section = section_title.lower()
                _flush_position(result, current_position)
                current_position = None

            i += 1
            continue

        # --- 识别 H3 (### Position 或 Academic Project) ---
        if line.startswith('### ') and not line.startswith('#### '):
            h3_text = line[4:].strip()

            if current_section == 'academic_projects':
                # H3 = 学术项目标题
                # 先 flush 之前的学术项目 group（在清空前！）
                if current_group and current_group.get("type") == "academic_project":
                    current_group["bullets"] = current_bullets[:]
                    result["academic_projects"].append(current_group)
                current_bullets = []
                _flush_position(result, current_position)
                current_position = None
                # 创建新的学术项目 group
                proj_title, course = _parse_academic_project_header(h3_text)
                current_group = {
                    "type": "academic_project",
                    "raw_title": h3_text,
                    "canonical_title": proj_title,
                    "course": course,
                    "bullets": [],
                }
            elif current_section == 'work':
                _flush_group(current_position, current_group, current_bullets)
                current_group = None
                current_bullets = []
                # H3 = 工作经历标题（如 "Software Engineer Intern | ByteDance..."）
                _flush_position(result, current_position)
                current_position = _parse_position_header(h3_text)
                current_position["contribution_groups"] = []
            else:
                # 其他 section 的 H3，视情况处理
                _flush_group(current_position, current_group, current_bullets)
                current_group = None
                current_bullets = []

            i += 1
            continue

        # --- 识别子标题（项目/贡献组）---
        # 模式1: **_Project: XXX_**  或  **Sub-project: XXX**  或  **_Core XXX:_**
        sub_match = re.match(
            r'^\*\*[_\s]*((?:Sub-)?[Pp]roject|Core\s.+?(?:Contributions|Engineering).*)[\s:：]*(.+?)\s*[_\s]*\*\*\s*$',
            line
        )
        if not sub_match:
            # 模式2: **_XXX Contributions:_** 或 **_XXX Contributions_**
            sub_match2 = re.match(
                r'^\*\*[_\s]*(.+?(?:Contributions|Engineering|Infrastructure|Treasury|Compliance).+?)\s*[_:：]*\s*[_\s]*\*\*\s*$',
                line
            )
            if sub_match2:
                sub_match = sub_match2

        if not sub_match and re.match(r'^\*\*[_\s]*.+?[_\s]*\*\*\s*$', line):
            # 模式3: 任何独立的加粗行（非 bullet），可能是子标题
            inner = re.match(r'^\*\*[_\s]*(.+?)\s*[_:：]*\s*[_\s]*\*\*\s*$', line)
            if inner:
                inner_text = inner.group(1).strip().rstrip(':').rstrip('：')
                # 排除日期行（如 **Jun 2025 – Dec 2025**）
                if not re.match(r'^[A-Z][a-z]{2}\s+\d{4}', inner_text) and len(inner_text) > 10:
                    sub_match = inner

        if sub_match and current_section in ('work', 'academic_projects') and current_position is not None:
            # 保存之前的 group
            _flush_group(current_position, current_group, current_bullets)
            current_bullets = []

            raw_title = strip_bold(line).strip().strip('_').strip(':').strip('：').strip()

            # 判断类型
            group_type = _classify_group_type(raw_title)

            current_group = {
                "type": group_type,
                "raw_title": raw_title,
                "bullets": [],
            }
            i += 1
            continue

        # --- 收集 bullet points ---
        if line.startswith('* ') or line.startswith('- '):
            bullet_text = line[2:].strip()
            # 处理多行 bullet（续行）
            j = i + 1
            while j < len(lines):
                next_line = lines[j].rstrip()
                if next_line and not next_line.startswith('* ') and not next_line.startswith('- ') \
                   and not next_line.startswith('#') and not next_line.startswith('**') \
                   and next_line != '---' and not next_line.startswith('|'):
                    bullet_text += ' ' + next_line.strip()
                    j += 1
                else:
                    break
            i = j

            bullet_obj = {
                "text": bullet_text,
                "keywords": extract_bold_keywords(bullet_text),
            }

            if current_section == 'summary':
                result["summary"].append(bullet_obj)
            elif current_section == 'skills':
                result["skills_section"].append(bullet_obj)
            elif current_section == 'additional':
                result["additional"].append(bullet_obj)
            elif current_section in ('work', 'academic_projects'):
                current_bullets.append(bullet_obj)
            elif current_section == 'education':
                result["education"].append(bullet_obj)
            continue

        # --- 教育表格行 ---
        if line.startswith('|') and current_section == 'education':
            # 跳过表头分隔符
            if re.match(r'^\|\s*-', line):
                i += 1
                continue
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if len(cells) >= 3 and cells[0] and not cells[0].startswith('Degree'):
                result["education"].append({
                    "degree": strip_bold(cells[0]),
                    "institution": strip_bold(cells[1]),
                    "period": strip_bold(cells[2]),
                })
            i += 1
            continue

        # --- Skills section: 非 bullet 的加粗行 (如 **Languages:** Python, Java, ...) ---
        if current_section == 'skills' and line.startswith('**') and ':' in line:
            skill_line = line.strip()
            result["skills_section"].append({
                "text": skill_line,
                "keywords": extract_bold_keywords(skill_line),
            })
            i += 1
            continue

        # --- 日期行 ---
        if line.startswith('**') and current_position is not None:
            date_match = re.match(r'^\*\*(.+?)\*\*\s*$', line)
            if date_match:
                date_text = date_match.group(1).strip()
                if re.match(r'^[A-Z][a-z]{2}\s+\d{4}', date_text):
                    current_position["period"] = date_text
                    i += 1
                    continue

        # --- 课程行 ---
        if current_section == 'education' and 'coursework' in line.lower():
            result["education"].append({
                "type": "coursework",
                "text": strip_bold(line.strip()),
            })
            i += 1
            continue

        i += 1

    # 最终 flush
    if current_group and current_group.get("type") == "academic_project":
        current_group["bullets"] = current_bullets[:]
        result["academic_projects"].append(current_group)
    else:
        _flush_group(current_position, current_group, current_bullets)
    _flush_position(result, current_position)

    return result


def _flush_group(position: dict | None, group: dict | None, bullets: list):
    """将收集的 bullets 保存到 group，将 group 保存到 position"""
    if group is not None:
        group["bullets"] = bullets[:]
        if position is not None:
            position["contribution_groups"].append(group)
    elif position is not None and bullets:
        # 没有 group 标题的散落 bullets → 创建一个 "general" group
        general_group = {
            "type": "general",
            "raw_title": "General Contributions",
            "bullets": bullets[:],
        }
        position["contribution_groups"].append(general_group)


def _flush_position(result: dict, position: dict | None):
    """将 position 保存到 result 的对应 section"""
    if position is not None:
        result["work_experience"].append(position)


def _parse_position_header(text: str) -> dict:
    """解析工作经历标题行，如 'Software Engineer Intern | ByteDance (TikTok) · Security Infra | San Jose, CA'"""
    parts = [p.strip() for p in text.split('|')]
    position = {
        "raw_header": text,
        "title": parts[0] if len(parts) > 0 else text,
        "company_full": parts[1] if len(parts) > 1 else "",
        "location": parts[2] if len(parts) > 2 else "",
        "period": "",
        "contribution_groups": [],
    }
    return position


def _parse_academic_project_header(text: str) -> tuple[str, str]:
    """解析学术项目标题，如 'GPU Pipeline Functional Simulator — CS 6290 HPCA'"""
    parts = re.split(r'\s*[—–-]\s*', text, maxsplit=1)
    title = parts[0].strip()
    course = parts[1].strip() if len(parts) > 1 else ""
    return title, course


def _classify_group_type(raw_title: str) -> str:
    """根据标题文本判断 group 类型"""
    lower = raw_title.lower()
    if 'project' in lower or 'sub-project' in lower:
        return "named_project"
    elif 'contribution' in lower or 'core ' in lower:
        return "core_contributions"
    elif any(kw in lower for kw in ['payment', 'treasury', 'compliance', 'infrastructure',
                                      'blockchain', 'security', 'sensor', 'gpu']):
        return "themed_section"
    else:
        return "themed_section"


def main():
    resume_files = sorted(RESUME_DIR.glob('*_Resume.md'))
    if not resume_files:
        print("❌ 没有找到简历文件")
        return

    print(f"找到 {len(resume_files)} 份简历，开始解析...\n")

    all_resumes = []
    for f in resume_files:
        parsed = parse_resume(f)
        resume_id = parsed["resume_id"]
        n_summary = len(parsed["summary"])
        n_work = len(parsed["work_experience"])
        total_bullets = sum(
            len(g["bullets"])
            for pos in parsed["work_experience"]
            for g in pos.get("contribution_groups", [])
        )
        n_groups = sum(
            len(pos.get("contribution_groups", []))
            for pos in parsed["work_experience"]
        )
        n_acad = len(parsed["academic_projects"])
        n_skills = len(parsed["skills_section"])

        print(f"  {resume_id:02d} {f.stem[:50]:50s} | "
              f"summary={n_summary} work_pos={n_work} groups={n_groups} "
              f"bullets={total_bullets} acad={n_acad} skills={n_skills}")

        all_resumes.append(parsed)

    # 写出
    OUTPUT.write_text(json.dumps(all_resumes, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"\n✅ 解析完成，输出到 {OUTPUT}")
    print(f"   共 {len(all_resumes)} 份简历")

    # 汇总统计
    total_all_bullets = sum(
        sum(len(g["bullets"]) for pos in r["work_experience"] for g in pos.get("contribution_groups", []))
        for r in all_resumes
    )
    print(f"   工作经历 bullets 总数: {total_all_bullets}")


if __name__ == "__main__":
    main()
