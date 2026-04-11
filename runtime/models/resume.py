"""
简历数据模型 - 所有Writer和Reviewer操作的核心数据结构。
"""
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum

from config.candidate_framework import CANDIDATE_FRAMEWORK
from config.writing_rules import STRONG_VERBS


class Seniority(Enum):
    INTERN = "intern"
    JUNIOR = "junior"
    MID_SENIOR = "mid_senior"
    SENIOR = "senior"


@dataclass
class Bullet:
    text: str
    has_data: bool = False          # 是否包含具体数据/指标
    tech_stack_used: List[str] = field(default_factory=list)
    verb: str = ""                  # 开头动词


@dataclass
class Project:
    title: str
    parent_experience_id: str       # 属于哪段经历（工作/教育）
    baseline: str = ""              # 一句话斜体概括
    bullets: List[Bullet] = field(default_factory=list)
    tech_stack: List[str] = field(default_factory=list)
    is_academic: bool = False


@dataclass
class Experience:
    id: str                         # 对应candidate_framework中的id
    company: str
    department: str
    title: str
    team: str = ""                  # 可变：新增的team名
    dates: str = ""
    location: str = ""
    seniority: Seniority = Seniority.JUNIOR
    bullets: List[Bullet] = field(default_factory=list)
    project: Optional[Project] = None  # 附属项目（如有）
    cross_functional_note: str = ""    # 如"由于跨职能小团队领导角色..."


@dataclass
class Education:
    id: str                         # 对应candidate_framework中的id
    degree: str
    school: str
    dates: str = ""
    track: str = ""                 # 可变track
    project: Optional[Project] = None  # 教育项目（如有）
    show_courses: bool = False
    courses: List[str] = field(default_factory=list)


@dataclass
class SkillCategory:
    name: str
    skills: List[str] = field(default_factory=list)


@dataclass
class Resume:
    # 目标信息
    target_jd_id: str = ""
    target_company: str = ""
    target_role: str = ""
    target_seniority: str = ""

    # 简历模块
    summary: List[str] = field(default_factory=list)  # 恰好3句
    skills: List[SkillCategory] = field(default_factory=list)
    experiences: List[Experience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    achievement: str = ""           # 围棋成就（可选呈现）

    # 元数据
    version: int = 1
    review_history: List[Dict] = field(default_factory=list)
    is_reviewed: bool = False
    review_passed: bool = False

    def get_all_bullets(self) -> List[Bullet]:
        """获取所有工作经历要点"""
        bullets = []
        for exp in self.experiences:
            bullets.extend(exp.bullets)
        return bullets

    def get_all_project_bullets(self) -> List[Bullet]:
        """获取所有项目要点"""
        bullets = []
        for exp in self.experiences:
            if exp.project:
                bullets.extend(exp.project.bullets)
        for edu in self.education:
            if edu.project:
                bullets.extend(edu.project.bullets)
        return bullets

    def get_all_projects(self) -> List[Project]:
        """获取所有项目"""
        projects = []
        for exp in self.experiences:
            if exp.project:
                projects.append(exp.project)
        for edu in self.education:
            if edu.project:
                projects.append(edu.project)
        return projects

    def get_all_tech_stack(self) -> set:
        """获取简历正文中提到的所有技术栈（元数据 + 文本扫描）"""
        tech = set()
        # 1. 从bullet元数据获取
        for b in self.get_all_bullets():
            tech.update(b.tech_stack_used)
        for b in self.get_all_project_bullets():
            tech.update(b.tech_stack_used)

        # 2. 从bullet文本中扫描（兜底，防止Writer未填充tech_stack_used）
        all_text = ""
        for b in self.get_all_bullets():
            all_text += " " + b.text
        for b in self.get_all_project_bullets():
            all_text += " " + b.text
        # 也扫描summary和cross_functional_note
        all_text += " " + " ".join(self.summary)
        for exp in self.experiences:
            if exp.cross_functional_note:
                all_text += " " + exp.cross_functional_note

        all_text_lower = all_text.lower()
        # 扫描skills中出现的每个技能是否在文本中有提及
        for cat in self.skills:
            for skill in cat.skills:
                if skill.lower() in all_text_lower:
                    tech.add(skill)

        return tech

    def get_skills_list(self) -> set:
        """获取SKILLS模块中的所有技术栈"""
        skills = set()
        for cat in self.skills:
            skills.update(cat.skills)
        return skills

    @staticmethod
    def _ensure_period(text: str) -> str:
        """确保文本以英文句号结尾"""
        text = text.rstrip()
        if text and text[-1] not in ".!?":
            text += "."
        return text

    def to_markdown(self) -> str:
        """输出为Markdown格式简历"""
        lines = []

        # Summary — 每句带小标题（小标题由Writer填入，格式 "**小标题:** 正文"）
        lines.append("## Professional Summary")
        for s in self.summary:
            lines.append(f"* {self._ensure_period(s)}")
        lines.append("")

        # Skills — 2-4分类，每分类4-8技能
        lines.append("## Skills")
        for cat in self.skills:
            lines.append(f"* **{cat.name}:** {', '.join(cat.skills)}")
        lines.append("")

        # Experience
        lines.append("## Experience")
        for exp in self.experiences:
            team_str = f" · {exp.team}" if exp.team else ""
            lines.append(f"### {exp.title} | {exp.company} · {exp.department}{team_str}")
            lines.append(f"*{exp.dates} | {exp.location}*")
            if exp.cross_functional_note:
                lines.append(f"> {self._ensure_period(exp.cross_functional_note)}")
            lines.append("")
            for b in exp.bullets:
                lines.append(f"* {self._ensure_period(b.text)}")
            lines.append("")

            if exp.project:
                lines.append(f"**Project: {exp.project.title}**")
                if exp.project.baseline:
                    lines.append(f"> {exp.project.baseline}")
                for b in exp.project.bullets:
                    lines.append(f"* {self._ensure_period(b.text)}")
                lines.append("")

        # Education
        lines.append("## Education")
        for edu in self.education:
            track_str = f" ({edu.track})" if edu.track else ""
            lines.append(f"### {edu.degree}{track_str} | {edu.school}")
            lines.append(f"*{edu.dates}*")
            if edu.project:
                lines.append(f"**Project: {edu.project.title}**")
                if edu.project.baseline:
                    lines.append(f"> {edu.project.baseline}")
                for b in edu.project.bullets:
                    lines.append(f"* {self._ensure_period(b.text)}")
            lines.append("")

        # Achievement
        if self.achievement:
            lines.append("## Achievements")
            lines.append(f"* {self._ensure_period(self.achievement.strip())}")

        return "\n".join(lines)

    @classmethod
    def from_markdown(cls, md: str, target_jd_id: str = "",
                      target_company: str = "", target_role: str = "",
                      target_seniority: str = "") -> "Resume":
        """
        从LLM生成的Markdown解析回Resume dataclass。
        支持to_markdown()输出的格式。
        """
        resume = cls(
            target_jd_id=target_jd_id,
            target_company=target_company,
            target_role=target_role,
            target_seniority=target_seniority,
        )

        lines = md.split("\n")
        i = 0
        current_section = None  # summary, skills, experience, education, achievements
        current_exp = None
        current_edu = None
        current_project = None  # 当前正在解析的project

        while i < len(lines):
            line = lines[i].strip()

            # 识别section header
            if line.startswith("## Professional Summary"):
                current_section = "summary"
                current_exp = current_edu = current_project = None
                i += 1
                continue
            elif line.startswith("## Skills"):
                current_section = "skills"
                current_exp = current_edu = current_project = None
                i += 1
                continue
            elif line.startswith("## Experience") or line.startswith("## Work Experience"):
                current_section = "experience"
                current_exp = current_edu = current_project = None
                i += 1
                continue
            elif line.startswith("## Education"):
                current_section = "education"
                current_exp = current_edu = current_project = None
                i += 1
                continue
            elif line.startswith("## Achievement") or line.startswith("## Additional Information"):
                current_section = "achievements"
                current_exp = current_edu = current_project = None
                i += 1
                continue
            elif line.startswith("## "):
                current_section = None
                i += 1
                continue

            if not line:
                i += 1
                continue

            # ── Summary ──
            if current_section == "summary":
                if line.startswith("* ") or line.startswith("- "):
                    resume.summary.append(line[2:].strip())
                else:
                    resume.summary.extend(cls._split_summary_fragments(line))

            # ── Skills ──
            elif current_section == "skills":
                content = ""
                if line.startswith("* ") or line.startswith("- "):
                    content = line[2:].strip()
                elif line.startswith("**"):
                    content = line
                if content:
                    # 格式: **Category:** skill1, skill2, ...
                    m = re.match(r'\*\*(.+?)[:\uff1a]\*\*\s*(.*)', content)
                    if not m:
                        m = re.match(r'([^:：]+)[:：]\s*(.*)', content)
                    if m:
                        cat_name = m.group(1).strip()
                        skills_str = m.group(2).strip()
                        skills = [s.strip() for s in skills_str.split(",") if s.strip()]
                        resume.skills.append(SkillCategory(name=cat_name, skills=skills))

            # ── Experience ──
            elif current_section == "experience":
                # ### Title | Company · Department · Team
                if line.startswith("### "):
                    current_project = None
                    header = line[4:].strip()
                    parts = [part.strip() for part in header.split("|")]
                    title = parts[0].strip() if parts else header
                    company = dept = team = dates = location = ""
                    if len(parts) > 1:
                        org_parts = parts[1].strip().split("·")
                        org_parts = [p.strip() for p in org_parts]
                        company = org_parts[0] if org_parts else ""
                        prefixed = title.split(":", 1)
                        if (
                            len(prefixed) == 2
                            and company
                            and prefixed[0].strip().lower() in company.lower()
                        ):
                            title = prefixed[1].strip()
                        exp_id = cls._infer_experience_id(company)
                        dept, team = cls._resolve_department_and_team(exp_id, org_parts[1:])
                    if len(parts) > 2:
                        third = parts[2].strip()
                        if cls._looks_like_dates(third):
                            dates = third
                            if len(parts) > 3:
                                location = parts[3].strip()
                        else:
                            location = third
                            if len(parts) > 3 and cls._looks_like_dates(parts[3].strip()):
                                dates = parts[3].strip()

                    exp_id = cls._infer_experience_id(company)
                    current_exp = Experience(
                        id=exp_id, company=company, department=dept,
                        title=title, team=team, dates=dates, location=location,
                    )
                    current_edu = None
                    resume.experiences.append(current_exp)

                # **Project: Title** （必须在italic检查之前，因为也以*开头）
                elif cls._is_project_heading(line) and current_exp:
                    proj_title = cls._strip_project_heading(line)
                    current_project = Project(
                        title=proj_title,
                        parent_experience_id=current_exp.id,
                    )
                    current_exp.project = current_project
                    # 下一行可能是 blockquote baseline（新格式）或斜体 baseline（旧格式）
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line.startswith("> "):
                            current_project.baseline = next_line[2:].strip()
                            i += 1
                        elif next_line.startswith("*") and next_line.endswith("*") and not next_line.startswith("* "):
                            current_project.baseline = next_line.strip("*").strip()
                            i += 1

                # *dates | location* 或 *cross_functional_note*
                elif line.startswith("*") and line.endswith("*") and not line.startswith("* ") and not line.startswith("**") and current_exp and not current_project:
                    inner = line.strip("*").strip()
                    if "|" in inner and not current_exp.dates:
                        date_loc = inner.split("|")
                        current_exp.dates = date_loc[0].strip()
                        current_exp.location = date_loc[1].strip() if len(date_loc) > 1 else ""
                    elif current_exp.dates:
                        current_exp.cross_functional_note = inner
                elif line.startswith("> ") and current_exp and not current_project:
                    current_exp.cross_functional_note = line[2:].strip()
                elif line.startswith("**") and line.endswith("**") and current_exp and not current_exp.dates:
                    inner = cls._strip_inline_emphasis(line)
                    if "|" in inner:
                        date_loc = inner.split("|")
                        current_exp.dates = date_loc[0].strip()
                        if len(date_loc) > 1 and not current_exp.location:
                            current_exp.location = date_loc[1].strip()
                    else:
                        current_exp.dates = inner
                elif line.startswith("> ") and current_exp and current_exp.dates and not current_project:
                    current_exp.cross_functional_note = line[2:].strip()

                # bullet
                elif (line.startswith("* ") or line.startswith("- ")) and current_exp:
                    bullet_text = line[2:].strip()
                    bullet = cls._parse_bullet(bullet_text)
                    if current_project:
                        current_project.bullets.append(bullet)
                    else:
                        current_exp.bullets.append(bullet)

            # ── Education ──
            elif current_section == "education":
                if line.startswith("|"):
                    stripped = line.strip().strip("|")
                    cells = [cell.strip() for cell in stripped.split("|")]
                    if (
                        len(cells) >= 3
                        and cells[0].lower() != "degree"
                        and not all(set(cell) <= {"-", ":", " "} for cell in cells[:3])
                    ):
                        degree_part, school, dates = cells[:3]
                        track = ""
                        track_m = re.match(r'(.+?)\s*\((.+?)\)', degree_part)
                        if track_m:
                            degree_part = track_m.group(1).strip()
                            track = track_m.group(2).strip()
                        edu_id = cls._infer_education_id(school)
                        current_edu = Education(
                            id=edu_id, degree=degree_part, school=school, track=track, dates=dates,
                        )
                        current_exp = None
                        resume.education.append(current_edu)
                        current_project = None
                elif line.startswith("### "):
                    current_project = None
                    header = line[4:].strip()
                    parts = header.split("|")
                    degree_part = parts[0].strip()
                    school = parts[1].strip() if len(parts) > 1 else ""
                    # degree可能含track: "Degree (Track)"
                    track = ""
                    track_m = re.match(r'(.+?)\s*\((.+?)\)', degree_part)
                    if track_m:
                        degree_part = track_m.group(1).strip()
                        track = track_m.group(2).strip()
                    edu_id = cls._infer_education_id(school)
                    current_edu = Education(
                        id=edu_id, degree=degree_part, school=school, track=track,
                    )
                    current_exp = None
                    resume.education.append(current_edu)

                elif line.startswith("*") and line.endswith("*") and current_edu and not current_edu.dates:
                    current_edu.dates = line.strip("*").strip()

                elif cls._is_project_heading(line) and current_edu:
                    proj_title = cls._strip_project_heading(line)
                    current_project = Project(
                        title=proj_title,
                        parent_experience_id=current_edu.id,
                        is_academic=True,
                    )
                    current_edu.project = current_project
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line.startswith("> "):
                            current_project.baseline = next_line[2:].strip()
                            i += 1
                        elif next_line.startswith("*") and next_line.endswith("*") and not next_line.startswith("* "):
                            current_project.baseline = next_line.strip("*").strip()
                            i += 1

                elif (line.startswith("* ") or line.startswith("- ")) and current_edu:
                    bullet_text = line[2:].strip()
                    bullet = cls._parse_bullet(bullet_text)
                    if current_project:
                        current_project.bullets.append(bullet)

            # ── Achievements ──
            elif current_section == "achievements":
                if line.startswith("* ") or line.startswith("- "):
                    resume.achievement = line[2:].strip().rstrip(".")

            i += 1

        return resume

    @staticmethod
    def _parse_bullet(text: str) -> "Bullet":
        """从bullet文本解析出Bullet对象"""
        # 提取开头动词
        verb = ""
        first_word_m = re.match(r'(?:\*\*)?(\w+)', text)
        if first_word_m:
            verb = first_word_m.group(1)

        # 提取bold标记的tech: **xxx**
        bold_items = re.findall(r'\*\*(.+?)\*\*', text)
        if bold_items and text.startswith("**"):
            strong_verbs = {verb.lower() for verb in STRONG_VERBS}
            if bold_items[0].strip().lower() in strong_verbs:
                bold_items = bold_items[1:]

        # 简单判断是否含量化数据
        has_data = bool(re.search(r'\d+[%+MKx]|\d+\.\d+|\d{2,}', text))

        return Bullet(
            text=text,
            has_data=has_data,
            tech_stack_used=bold_items,
            verb=verb,
        )

    @staticmethod
    def _strip_inline_emphasis(text: str) -> str:
        return re.sub(r'^[*_]+|[*_]+$', '', text.strip()).strip()

    @staticmethod
    def _looks_like_dates(text: str) -> bool:
        lowered = text.lower()
        return bool(re.search(r'\b(19|20)\d{2}\b', text) or "expected" in lowered or "present" in lowered)

    @classmethod
    def _is_project_heading(cls, line: str) -> bool:
        return cls._strip_inline_emphasis(line).lower().startswith("project:")

    @classmethod
    def _strip_project_heading(cls, line: str) -> str:
        inner = cls._strip_inline_emphasis(line)
        return inner.split(":", 1)[1].strip() if ":" in inner else inner

    @staticmethod
    def _split_summary_fragments(text: str) -> List[str]:
        stripped = text.strip()
        if not stripped:
            return []
        if stripped.startswith("* ") or stripped.startswith("- "):
            return [stripped[2:].strip()]

        header_matches = list(re.finditer(r'\*\*[^*]+?:\*\*', stripped))
        if len(header_matches) <= 1:
            return [stripped]

        fragments: List[str] = []
        for idx, match in enumerate(header_matches):
            start = match.start()
            end = header_matches[idx + 1].start() if idx + 1 < len(header_matches) else len(stripped)
            fragment = stripped[start:end].strip()
            if fragment:
                fragments.append(fragment)
        return fragments

    @staticmethod
    def _infer_experience_id(company: str) -> str:
        """从公司名推断experience id"""
        c = company.lower()
        if "temu" in c:
            return "temu_da"
        elif "didi" in c:
            return "didi_senior_da"
        elif "tiktok" in c or "bytedance" in c:
            return "tiktok_intern"
        return company.lower().replace(" ", "_")

    @staticmethod
    def _infer_education_id(school: str) -> str:
        """从学校名推断education id"""
        s = school.lower()
        if "georgia" in s or "gt" in s:
            return "gt_mscs"
        elif "illinois" in s or "uiuc" in s:
            return "uiuc_msim"
        elif "bisu" in s or "beijing international" in s:
            return "bisu_mib"
        elif "beijing normal" in s:
            return "bnu_ba"
        return school.lower().replace(" ", "_")

    @staticmethod
    def _resolve_department_and_team(exp_id: str, org_parts: List[str]) -> tuple[str, str]:
        """
        按候选人框架解析 department/team，避免把多段 department 误拆成 team。

        例如：
        - `DiDi · IBG · Food` 应解析为 department=`IBG · Food`, team=``
        - `Temu · R&D · Growth` 应解析为 department=`R&D`, team=`Growth`
        """
        if not org_parts:
            return "", ""

        expected_dept = ""
        for exp in CANDIDATE_FRAMEWORK["experience"]:
            if exp["id"] == exp_id:
                expected_dept = exp.get("department", "")
                break

        if expected_dept:
            joined = " · ".join(org_parts)
            if joined == expected_dept:
                return expected_dept, ""

            dept_segments = [seg.strip() for seg in expected_dept.split("·") if seg.strip()]
            prefix = " · ".join(org_parts[:len(dept_segments)])
            if prefix == expected_dept:
                team = " · ".join(org_parts[len(dept_segments):]).strip()
                return expected_dept, team

        dept = org_parts[0]
        team = " · ".join(org_parts[1:]).strip()
        return dept, team
