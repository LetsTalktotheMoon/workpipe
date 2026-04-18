"""
Prompt Builder — Master Writer + Unified Reviewer 两套 prompt。

核心设计：PLAN → WRITE 两阶段强制 SKILLS ↔ 正文一致性。
这是解决原赛马系统三条路线共同失败原因（SKILLS/正文不对齐）的根本方案：
  保守组: SKILLS太少 → body中的tech漏出SKILLS
  激进组: SKILLS太多 → SKILLS列了body没有的tech
  叙事组: SKILLS过度精简 → Go等核心tech消失
新方案: 先规划tech allocation，由plan直接推导SKILLS，再按plan写body。
"""
import json
from typing import Dict, List

from automation.project_pool import build_project_pool_prompt_block
from config.candidate_framework import (
    CANDIDATE_FRAMEWORK,
    experience_framework_for_company,
    is_bytedance_target_company,
)
from config.frozen_constraints import FROZEN_CONSTRAINTS
from config.natural_tech import BASE_NATURAL_TECH, get_suggested_tech


# ══════════════════════════════════════════════════════════════
# 共享 prompt 片段
# ══════════════════════════════════════════════════════════════

TIKTOK_IMMUTABLE_LINE = (
    "- TikTok: Software Engineer Intern | TikTok · Security | "
    "Jun 2025 – Dec 2025 | San Jose, USA"
)
DIDI_IMMUTABLE_LINE = (
    "- DiDi: Senior Data Analyst | DiDi · IBG · Food | "
    "Sep 2022 – May 2024 | Beijing/Mexico"
)
TEMU_IMMUTABLE_LINE = "- Temu: Data Analyst | Temu · R&D | Jun 2021 – Feb 2022 | Shanghai"
DIDI_SCOPE_NOTE_EXAMPLE = (
    "> Data lead within a **13-person** cross-functional squad spanning product, "
    "backend, frontend, mobile, and ops."
)
DIDI_GLOBAL_SCOPE_BULLET = (
    "Represented the headquarters data organization in biweekly global operating "
    "reviews, and translated performance signals into two-week recommendations "
    "adopted by management and LATAM frontline teams."
)
BYTEDANCE_EVIDENCE_POOL_SHORT = "DiDi、Temu、Georgia Tech CS coursework/projects"
BYTEDANCE_EVIDENCE_POOL_LONG = (
    "DiDi 全职经历、Temu 全职经历、Georgia Tech CS coursework/projects"
)
MASTER_PLAN_TIKTOK_SECTION = """### TikTok（intern，最灵活，承接 JD 核心技术）
必要 JD 技术（放在这里）: [列出]
额外技术（stretch tier，叙事自洽即可）: [列出]
→ 此经历 bullet 将使用的完整技术列表: [最终列表]"""
MASTER_PLAN_DIDI_SECTION = """### DiDi（mid-senior acting lead，转行桥梁，连接分析和工程）
必要 JD 技术（放在这里）: [列出]
额外技术（extended tier 为主）: [列出]
→ 此经历 bullet 将使用的完整技术列表: [最终列表]"""
MASTER_PLAN_TEMU_SECTION = """### Temu（junior DA，故事起点，分析基础）
技术（core/extended tier，体现数据分析基础）: [列出]
→ 此经历 bullet 将使用的完整技术列表: [最终列表]"""
MASTER_PLAN_GT_SECTION = """### Georgia Tech CS coursework/projects（所有线路共享；ByteDance 可提升权重）
必要 JD 技术（若工作经历不够自然覆盖，优先放这里）: [列出]
→ 此教育项目 bullet 将使用的完整技术列表: [最终列表]"""
REVIEW_COMPACT_SCOPE_NOTE = """
## 审查输入说明

下方简历内容是用于历史重审的压缩审查视图：
- 已保留 Summary、Skills、关键 experiences、DiDi scope、以及最相关 bullets/projects
- 未展示的其余段落默认视为“暂未重点抽查”
- 除非当前 excerpt 已经暴露出系统性问题，否则不要因为 excerpt 没展示某段内容而臆测扣分
- 你的目标是快速识别最高杠杆的局部修复点，而不是要求整份简历推倒重写
"""
REVIEW_REWRITE_SCOPE_NOTE = """
## Rewrite 审查输入说明

下方简历已经确认“需要继续重写”，你的职责不是给保守补丁单，而是判断它如何跨过 pass 线：
- 如果现有稿件只是被 seed phrasing / summary framing / bullet 选择束缚，你应明确允许结构性重写
- 可以建议重写 Summary、Skills、最相关 experiences、project baseline、bullet 取舍与叙事顺序
- 不要因为“最好少改”而压制本应重写的部分
- 仍然禁止改动不可变字段、凭空新增不可信经历、删除 JD must-have 技术来规避问题
- revision_priority 和 revision_instructions 应优先输出“怎样改到 pass”，而不是“怎样保守止损”
"""
BYTEDANCE_REVIEW_SCOPE_NOTE = """

## ByteDance 特殊审查要求
- 对 ByteDance 目标岗位，TikTok / ByteDance intern 这段经历必须完全不存在
- 若简历仍引用了 TikTok / ByteDance intern，视为 critical，并要求删除后仅用 DiDi / Temu / Georgia Tech CS coursework/projects 重写；GT 教育主干仍按共享材料保留
"""
BYTEDANCE_REVISION_SPECIAL_BLOCK = f"""
## ByteDance 特殊要求
- 删除任何 TikTok / ByteDance intern 段落、summary 提及、project baseline 或 bullets
- 只允许从 {BYTEDANCE_EVIDENCE_POOL_SHORT} 三类证据中重写
- 若 seed / 旧稿里引用了 TikTok / ByteDance intern，把它视为必须移除的噪声，而不是可保留资产
"""
BYTEDANCE_UPGRADE_SPECIAL_BLOCK = f"""
## ByteDance 特殊要求
- 删除任何 TikTok / ByteDance intern 内容，不要把它当作可修补素材
- 证据池仅限 {BYTEDANCE_EVIDENCE_POOL_SHORT}
- 若旧稿因为 seed 骨架保留了 TikTok / ByteDance intern，必须直接推翻该部分并重写
"""


def _join_lines(lines: list[str]) -> str:
    return "\n".join(lines)

CANONICAL_OUTPUT_TEMPLATE = """## 输出格式（header 拼写必须完全一致）

## Professional Summary
* **Header:** Sentence.
* **Header:** Sentence.
* **Header:** Sentence.

## Skills
* **Category:** skill1, skill2, skill3
* **Category:** skill1, skill2, skill3

## Experience
### Title | Company · Department
*Dates | Location*
> Optional cross-functional note

* Bullet.
* Bullet.
* Bullet.
* Bullet.

**Project: Project Title**
> One-line project baseline (business pain point / context for what follows).
* Bullet.
* Bullet.
* Bullet.
* Bullet.

### Title | Company · Department
*Dates | Location*

* Bullet.

## Education
### Degree | School
*Dates*

## Achievements
* China national certified Go **2-dan** — city **champion** (2022) and third place (2023).

**Header 拼写规则:**
- `## Experience`（不是 `## Professional Experience`）
- `## Skills`（不是 `## Technical Skills`）
- `## Achievements`（不是 `## Achievement`）
- 项目必须在对应经历下方，不单独成 section
- 只输出简历正文，不要解释、注释、分析"""
RESUME_MARKDOWN_ONLY_RESPONSE_LINE = "直接输出修改后的完整简历 Markdown，不要附带解释。"


def _target_company_name(jd_or_company) -> str:
    if isinstance(jd_or_company, str):
        return jd_or_company
    return str(getattr(jd_or_company, "company", "") or "")


def _target_experience_framework(jd_or_company) -> list[dict]:
    return experience_framework_for_company(_target_company_name(jd_or_company))


def _experience_order_text(jd_or_company) -> str:
    company_name = _target_company_name(jd_or_company)
    if is_bytedance_target_company(company_name):
        return "DiDi（2022-2024）→ Temu（2021-2022）"
    return "TikTok（2025）→ DiDi（2022-2024）→ Temu（2021-2022）"


def _experience_order_rule(jd_or_company) -> str:
    return f"经历顺序必须保持 {_experience_order_text(jd_or_company)}"


def _immutable_experience_lines(jd_or_company) -> list[str]:
    company_name = _target_company_name(jd_or_company)
    lines = [DIDI_IMMUTABLE_LINE, TEMU_IMMUTABLE_LINE]
    if is_bytedance_target_company(company_name):
        lines.append("- TikTok / ByteDance intern experience must be absent for ByteDance target roles.")
    else:
        lines.insert(0, TIKTOK_IMMUTABLE_LINE)
    return lines


def _review_immutable_block(jd_or_company) -> str:
    return _join_lines(_immutable_experience_lines(jd_or_company))


def _target_specific_context_block(jd_or_company) -> str:
    company_name = _target_company_name(jd_or_company)
    if not is_bytedance_target_company(company_name):
        return ""
    return _join_lines(
        [
            "",
            "## ByteDance 目标公司特殊模式",
            "- 对 ByteDance 目标岗位，候选人证据池中不得出现 TikTok / ByteDance intern 这段经历，也不得在 Summary、Skills、Experience、Project baseline 或 bullets 中提及它",
            f"- 只允许从以下三类材料出发构建简历：{BYTEDANCE_EVIDENCE_POOL_LONG}",
            "- 当 JD 需要更强的软件工程或系统实现信号时，优先把 Georgia Tech CS coursework/projects 提升为主要技术证据；GT 教育主干仍是共享材料，而不是把缺口强行塞回 ByteDance/TikTok intern",
            "- seed 若包含 TikTok / ByteDance intern，只能作为弱参考；你必须主动删掉这段经历，再按新的证据池重写",
        ]
    ) + "\n"


def _scope_rule_lines(jd_or_company) -> list[str]:
    company_name = _target_company_name(jd_or_company)
    lines = []
    if not is_bytedance_target_company(company_name):
        lines.extend(
            [
                "- TikTok (intern, 6个月): 禁用 Led/Architected/Drove/Spearheaded/Managed；体现个人贡献，不主张架构决策",
                "  → bullet 数量建议 **4-5 条**（6个月实习期内独立成就不超过 5 条，超出则可信度下降）",
            ]
        )
    else:
        lines.append(
            "- ByteDance 目标岗位: 不允许出现 TikTok / ByteDance intern；需要更多 SWE 证据时，优先把 Georgia Tech CS coursework/projects 作为主力软件工程/系统实现证据，而不是回填该实习。"
        )
    lines.extend(
        [
            "- DiDi (mid-senior acting lead): 可用 Led/Coordinated/Drove；可展示 13 人跨职能团队领导力",
            "- DiDi 的全球汇报/管理层传导 scope 不要塞进 scope note；如目标岗位重视 senior stakeholder scope，可用单独 bullet 表达：",
            f"  `{DIDI_GLOBAL_SCOPE_BULLET}`",
            "- Temu (junior): 禁用 Led/Architected/Drove/Spearheaded；仅体现 individual contributor 贡献",
        ]
    )
    return lines


def _build_master_plan_template(*, bytedance_mode: bool) -> str:
    sections = [MASTER_PLAN_DIDI_SECTION, MASTER_PLAN_TEMU_SECTION, MASTER_PLAN_GT_SECTION]
    if not bytedance_mode:
        sections = [MASTER_PLAN_TIKTOK_SECTION, MASTER_PLAN_DIDI_SECTION, MASTER_PLAN_TEMU_SECTION, MASTER_PLAN_GT_SECTION]
    return "\n\n".join(sections)


def _build_review_scope_note(review_scope: str, *, bytedance_mode: bool) -> str:
    scope_note = ""
    if review_scope == "compact":
        scope_note = REVIEW_COMPACT_SCOPE_NOTE
    elif review_scope == "rewrite":
        scope_note = REVIEW_REWRITE_SCOPE_NOTE
    if bytedance_mode:
        scope_note += BYTEDANCE_REVIEW_SCOPE_NOTE
    return scope_note


def _format_constraint_lines(jd_or_company) -> list[str]:
    company_name = _target_company_name(jd_or_company)
    return [
        "## 格式硬约束（违反=直接FAIL）",
        "",
        "**结构规则**",
        f"- Summary: 恰好 {FROZEN_CONSTRAINTS['summary_sentences']['exact']} 句，每句格式：`* **角色定位短语:** 叙述句。`",
        f"- Experience 顺序: **严格倒序** — {_experience_order_text(company_name)}",
        f"- 每段经历: {FROZEN_CONSTRAINTS['bullets_per_experience']['min']}-{FROZEN_CONSTRAINTS['bullets_per_experience']['max']} 条 bullet，至少 {FROZEN_CONSTRAINTS['data_bullets_per_experience']['min']} 条含量化数据",
        f"- 项目: 恰好 {FROZEN_CONSTRAINTS['project_count']['exact']} 个（至少1个来自工作经历），每项目 {FROZEN_CONSTRAINTS['work_project_bullets']['min']}-{FROZEN_CONSTRAINTS['work_project_bullets']['max']} 条 bullet",
        "- 项目位置: 项目紧跟对应经历，不单独设 `## Projects` section",
        "- 项目背景行: 每个项目标题下必须紧接一行 `> ` 开头的 blockquote（一句话说明业务痛点/背景，不是重复项目标题），然后才是 bullet 列表",
        "- DiDi scope note 若出现，必须是简短身份说明，不承担全部 leadership/decision story；推荐写法：",
        f"  `{DIDI_SCOPE_NOTE_EXAMPLE}`",
        "",
        "**SKILLS 一致性规则（最重要）**",
        "- SKILLS 优先分 2-4 个类别；如为满足行宽约束可扩到 5 类",
        "- 不允许出现孤行：单个 Skills 类别少于 **4** 个技术栈必须合并到相邻类别",
        "- 每行（含类别标题）总词数必须 **≤ 14**；这是硬性标准，超过即 FAIL",
        "- SKILLS 中只有分类标题使用 `**加粗**`，分类内技术栈一律纯文本逗号分隔，不要给单个技术栈加粗",
        "- SKILLS 中每个技术栈**必须**在至少一条经历 bullet 或项目 bullet 中出现",
        "- 经历/项目 bullet 中出现的每个技术栈**必须**在 SKILLS 中出现",
        "- Summary 中提及的技术栈也必须在 SKILLS 中",
        "- 禁止 SKILLS 中出现正文没有的技术栈（哪怕是 JD 要求的）",
        "- 但对目标 JD 的 must-have 技术，不允许通过“删除 SKILLS/summary 中该技术”来规避问题；必须在正文补足实质使用证据",
        "",
        "**内容规则**",
        "- 每条 bullet: 强动词开头 + 技术实现 + 业务/量化结果（XYZ格式）",
        "- 加粗规则（精确执行，不得扩大）：",
        "  1. **技术栈名词**：语言/框架/工具/平台（如 Go, React, PostgreSQL, AWS Bedrock）— 必须加粗",
        "  2. **量化数字及其直接关联词**：数字本身及紧跟的变化描述（如 `**32%**`、`**6** to **2**`、`**18 minutes**`）— 必须加粗",
        "  3. **业务实体名词**：具名产品/服务/系统（如 `**security evidence service**`、`**merchant onboarding**`、`**City Launch Ops**`）— 必须加粗",
        "  4. **禁止加粗修饰语**：`team-maintained`、`team-owned`、`intern-owned`、`existing`、`internal`、`our` 等限定词不得加粗",
        "  5. **禁止加粗动词/结构词**：`workflow`、`pipeline`、`dashboard`、`process` 等纯结构描述词不得加粗（除非是已命名产品名称的一部分）",
        "- 所有 bullet 以英文句号 `.` 结尾",
        f"- 禁止词: {', '.join(FROZEN_CONSTRAINTS['forbidden_words'])}",
        "- 跨经历 bullet 叙事结构不得逐条相同，技术栈需有差异化分布",
        "",
        "**不可变字段（绝不可修改）**",
        _review_immutable_block(company_name),
        "",
        "**职级 Scope 规则**",
        *_scope_rule_lines(company_name),
        "",
        "**数字合理性规则（违反 = r4 高风险）**",
        "- 改善幅度 > 70%：必须加范围限定语，例如：",
        '  "within team-owned service" / "on our internal dataset" / "in controlled staging tests"',
        '- 改善幅度 > 90%：极为可疑，需降至 80% 以下，或拆分为绝对值表述（如 "from 12 min to 2 min"）',
        '- 规模数字（如 1M+、100K+）：必须带来源限定，例如 "within a team-maintained pipeline" / "contributing to a service processing…"',
        "- 不可同时在同一 bullet 内堆叠 3 个以上量化数字",
        "",
        "**围棋成就**",
        "- 融入 Summary 第 3 句，衔接目标岗位某一必要特质（如模式识别/战略思维/复杂系统决策）",
        "- Summary 第 3 句的 header 必须是高价值认知信号，如 `Strategic Pattern Recognition` / `Analytical Decision-Making` / `Systems Judgment`",
        "- 禁止把围棋写进 `Collaboration` / `Teamwork` / `Problem Solver` / `Delivery Fit` 一类低信号 header",
        "- 措辞（Summary 中）：中国国家认证围棋二段棋手，2022年城市赛冠军，2023年城市赛季军",
        "",
        "**Achievements section 规范（不可变）**",
        "- 恰好 1 条 bullet，固定格式：",
        "  `* China national certified Go **2-dan** — city **champion** (2022) and third place (2023).`",
        "- 加粗仅限 `2-dan`（等级凭据）和 `champion`（最高成就）；年份作为括注，不加粗",
        "- section header 必须为 `## Achievements`，不得写成 `## Additional Information` 或其他变体",
    ]


def _format_constraints_for_company(jd_or_company) -> str:
    return _join_lines(_format_constraint_lines(jd_or_company))


FORMAT_CONSTRAINTS = _format_constraints_for_company("") + "\n"


# ══════════════════════════════════════════════════════════════
# 候选人框架描述（供 prompt 使用）
# ══════════════════════════════════════════════════════════════

def build_candidate_context(company_name: str = "") -> str:
    """构建候选人框架说明（供 Writer prompt 使用）"""
    lines = ["## 候选人经历框架（⚡=不可变字段，其余可由 Writer 决定）\n"]

    for exp in _target_experience_framework(company_name):
        rules = exp.get("rules", {})
        natural = BASE_NATURAL_TECH.get(exp["id"], {})

        lines.append(f"### {exp['company']} — {exp['title']} ({'不可变'})")
        lines.append(f"- ⚡公司: {exp['company']} | ⚡部门: {exp['department']} | ⚡职称: {exp['title']}")
        lines.append(f"- ⚡时间: {exp['dates']} | ⚡地点: {exp['location']}")
        lines.append(f"- 时长: {exp['duration_months']}个月 | 级别: {exp['seniority']}")

        forbidden = rules.get("forbidden_verbs", [])
        allowed = rules.get("allowed_verbs", [])
        if forbidden:
            lines.append(f"- 禁用动词: {', '.join(forbidden)}")
        if allowed:
            lines.append(f"- 允许动词: {', '.join(allowed)}")
        lines.append(f"- Scope上限: {rules.get('scope_ceiling', 'N/A')}")

        if "leadership" in rules:
            lead = rules["leadership"]
            lines.append(
                f"- 领导力: {lead['team_size']}人跨职能团队acting lead"
                f"（{', '.join(lead['team_composition'][:5])} 等）"
            )
            if lead.get("global_meetings"):
                lines.append(f"- 全球汇报: {lead['global_meetings']}")
            if lead.get("decision_scope"):
                lines.append(f"- 决策传导: {lead['decision_scope']}")

        # 技术栈参考
        core = sorted(natural.get("core", set()))
        extended = sorted(natural.get("extended", set()))
        stretch = sorted(natural.get("stretch", set()))
        if core:
            lines.append(f"- 自然技术栈 core（几乎必然使用）: {', '.join(core)}")
        if extended:
            lines.append(f"- 自然技术栈 extended（合理推断可能接触）: {', '.join(extended)}")
        if stretch:
            lines.append(f"- 自然技术栈 stretch（特定场景可能接触，需叙事支撑）: {', '.join(stretch[:15])}...")
        lines.append("")

    # 教育
    lines.append("### 教育经历（可根据 JD 方向选择列哪些）")
    for edu in CANDIDATE_FRAMEWORK["education"]:
        rules = edu.get("rules", {})
        keep_when = rules.get("keep_when", "")
        drop_when = rules.get("drop_when", "")
        lines.append(
            f"- {edu['degree']} | {edu['school']} | {edu['dates']}"
            + (f" — 保留当: {keep_when}" if keep_when else "")
            + (f" | 可省略当: {drop_when}" if drop_when else "")
        )
        if edu["id"] == "gt_mscs":
            lines.append(
                "  → 当 UIUC MSIM 出现时写为 M.S. Computer Science (OMSCS)；"
                "  仅出现GT时直接写 M.S. Computer Science"
            )
            if is_bytedance_target_company(company_name):
                lines.append(
                    "  → GT 教育主干对所有线路共享；ByteDance 目标岗位中，Georgia Tech CS coursework/projects 可以进一步提升为主要软件工程/系统实现证据来源。"
                )
    lines.append("")

    # 成就
    ach = CANDIDATE_FRAMEWORK["achievement"]
    lines.append(
        f"### 成就（融入 Summary 第3句）\n"
        f"- {ach['description']}，{ach['competitions']}"
    )
    if is_bytedance_target_company(company_name):
        lines.append("")
        lines.append("### ByteDance 特殊写作边界")
        lines.append("- 不得写入或提及 TikTok / ByteDance intern 这段经历")
        lines.append(
            "- 目标岗位只能使用 DiDi、Temu 和 Georgia Tech CS coursework/projects 作为证据池；"
            "GT 教育主干仍按共享教育块保留，ByteDance 只是进一步加权 GT coursework/projects。"
        )

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════
# MASTER WRITER PROMPT
# ══════════════════════════════════════════════════════════════

MASTER_WRITER_SYSTEM = """你是一位专业简历撰写专家，为一家职业转型培训公司制作教学示例简历。
该候选人为虚构人物，正在从数据分析向软件工程转型。简历的「真实性」由自身逻辑自洽体现，
而非由经历或技术栈的现实核查来锚定。

你的输出质量标准：能够通过真实公司 ATS 系统和人工 HR 审查，在 9 大维度综合评分 93 分以上。

【虚构候选人写作原则（最重要，PLAN 阶段首要参考）】
候选人为虚构的培训示例人物，不可变字段仅为：公司名、部门、职称、时间、地点。
其余所有工作内容——技术选型、项目故事、量化成果——均为自由创作，无真实性核查约束。
判断标准不是「候选人真实经历了这个吗」，而是「这段叙事在该角色/时间/规模下逻辑自洽吗」。

在 PLAN 阶段，你可以并应该：
- 为 DiDi 写 Java 微服务后台（running 20+ city operations across multiple markets）
- 为 TikTok 写参与构建 AWS Bedrock RAG 知识检索系统（intern 参与实现，团队维护）
- 为任何经历分配 JD 所需的任意技术，只要叙事在该职级/规模下合理即可
- 不受 natural_tech 分层限制：extended/stretch 层级对虚构人物仅是「叙事工作量」的提示，
  不是技术使用的硬约束。只要你在 PLAN 中给出自洽的业务背景，任何技术都可以出现。

工作流程（必须按此两阶段完成）：

【阶段一：PLAN】
在 <PLAN>...</PLAN> 标签内完成技术规划：
1. 分析 JD 必要/加分技术，判断每个技术最适合放在哪段经历中
2. 为每段经历列出 EXACTLY 将在 bullet 中使用的技术列表
3. 从各经历技术列表求并集，组织为 2-4 个 SKILLS 类别（这就是 SKILLS section 的内容）
4. 确定 2 个项目分别属于哪段经历及其主题
5. 确定保留哪些教育经历（GT MSCS 是所有线路共享的教育主干；一般 SWE 岗位仅保留 GT 即可，强金融背景 preference 岗位可列 BISU，强教育背景 preference 可列 BNU，除非点名要 Information Management专业否则不列 UIUC，岗位仅开在 Illinois 州可仅列 UIUC、不列 GT；ByteDance 目标岗位可把 GT coursework/projects 提升为主力软件工程/系统实现证据）
6. 预设量化数字范围（避免 r4 合理性失分）：
   - 若当前目标岗位允许使用 intern 经历，则 intern 改善幅度上限：单项 ≤ 70%（超过须加 "within team scope" 等限定语）
   - 延迟/时间改善若超过 80%，改写为绝对值（如 "from 12 min to 2 min"）
   - 规模数字须标注 "contributing to" / "within a team-maintained service" 等限定
7. 只输出最终规划结果，不要在 <PLAN> 中写自言自语、权衡过程或 "Wait/Actually/Let me reconsider" 一类中间推理
8. Summary 只保留对目标 JD 最值钱的 3 个信号；若 DiDi 的 senior operating scope 能显著增强匹配度，可在 summary 中简洁体现，但不要与 scope note / bullet 重复堆砌
9. 若目标 JD 带有候选人不自然直接接触的行业语境（如 autonomous driving / robotics / physical AI / spatial computing / sensor systems），优先写“领域桥接”而不是伪造直接行业经历：
   - 可强调 transferable infrastructure-grade pipeline patterns / reliability / data quality / model-evaluation / cross-system integration
   - 可写“transferable to spatial and sensor-data systems”这类桥接语
   - 不要假装候选人已经做过 perception / planning / simulation / robotics controls 本体工作，除非正文确有自洽支撑

【阶段二：RESUME】
在 <RESUME>...</RESUME> 标签内输出完整简历 Markdown，严格按照阶段一的规划写作，确保：
- SKILLS section = 阶段一推导的并集，不多不少
- SKILLS section 格式必须是 `* **Category:** tech1, tech2, tech3`，只加粗分类标题，不加粗技术栈本身
- 每段经历的 bullet 使用的技术 = 阶段一为该经历规划的技术，不多不少
- 经历顺序必须遵循用户 prompt 中给出的目标公司专用顺序约束

【Extended/Stretch 技术的使用语气规则（r0 关键）】
对于候选人经历中处于 extended 或 stretch 层级的技术，必须使用以下「参与式」语气，
而非「主建式」语气，以维护真实性可信度：

✅ 可信表述（intern / junior 适用）:
  - "contributed to a pipeline leveraging AWS S3 and Bedrock API"
  - "built feature components within an existing RAG-based retrieval service"
  - "integrated with team-maintained LLM inference endpoints via OpenAI API"
  - "developed Go services interfacing with AWS ECS-deployed containers"

❌ 不可信表述（intern 级别禁用）:
  - "architected an AWS Bedrock-based GenAI platform"
  - "designed and deployed the entire RAG infrastructure on AWS ECS"
  - "built the company's LLM inference system from scratch"

规则：凡是 intern 经历中涉及云基础设施（AWS/ECS/S3）或 GenAI（Bedrock/LLM/RAG），
一律使用 "contributing to" / "integrating with" / "within a team-maintained service" 等限定语。
"""


def build_master_writer_prompt(jd) -> str:
    """构建完整的 Master Writer user prompt"""
    candidate_ctx = build_candidate_context(jd.company)
    format_constraints = _format_constraints_for_company(jd.company)
    target_specific_block = _target_specific_context_block(jd.company)
    is_bytedance_mode = is_bytedance_target_company(jd.company)

    # 整理 JD 技术要求
    tech_required_str = ", ".join(jd.tech_required) if jd.tech_required else "（无明确列出）"
    tech_preferred_str = ", ".join(jd.tech_preferred) if jd.tech_preferred else "（无）"
    or_groups_str = ""
    if jd.tech_or_groups:
        or_groups_str = "\n".join(
            f"  - {' 或 '.join(g)}（至少满足其一）" for g in jd.tech_or_groups
        )
    soft_required_str = "\n".join(f"  - {s}" for s in jd.soft_required[:5]) if jd.soft_required else "（无）"

    plan_template = _build_master_plan_template(bytedance_mode=is_bytedance_mode)

    return f"""{candidate_ctx}
{target_specific_block}

## 目标 JD 信息

**公司:** {jd.company}
**岗位:** {jd.title}
**角色类型:** {jd.role_type}
**职级/资历:** {jd.seniority}
**团队业务方向:** {jd.team_direction or '（未说明）'}

**必须技术栈（SKILLS 中至少覆盖所有 JD 必须项，且必须有正文出处）:**
{tech_required_str}

**加分技术栈（合理选择即可，不必全部包含）:**
{tech_preferred_str}

**OR 组（满足其一即可）:**
{or_groups_str or '（无）'}

**软性要求:**
{soft_required_str}

**领域桥接提示:**
- 如果团队业务方向涉及陌生行业（例如自动驾驶、物理 AI、机器人、传感器系统、空间数据系统），请优先使用“可迁移能力”桥接：
  `infrastructure-grade pipeline patterns transferable to spatial and sensor-data systems`
  这类表达优于生造直接行业 ownership。

---

{format_constraints}

---

## 阶段一：PLAN（在此规划，不输出给最终用户）

请在 <PLAN> 标签内完成：

```
<PLAN>
## 技术分配规划

{plan_template.strip()}

## SKILLS 推导（= 上述经历/项目技术列表的并集）
[按 2-4 个类别优先组织；若为满足 14 词硬上限可扩到 5 类；任何类别不得少于 4 个技术]

## 项目规划
- 项目1: 属于 [哪段经历] | 主题: [业务场景]
- 项目2: 属于 [哪段经历] | 主题: [业务场景]

## 教育经历选择
[列出要保留的学历条目及理由]
</PLAN>
```

## 阶段二：RESUME

按照上方 PLAN 的规划，在 <RESUME> 标签内输出完整的 Markdown 简历：

```
<RESUME>
[完整简历内容]
</RESUME>
```

{CANONICAL_OUTPUT_TEMPLATE}
"""


# ══════════════════════════════════════════════════════════════
# UNIFIED REVIEWER PROMPT
# ══════════════════════════════════════════════════════════════

UNIFIED_REVIEWER_SYSTEM = """你是一位严格的简历质量审查专家，负责对简历进行 9 个维度的综合评分。
你的评审是最终裁决，直接决定该简历是否可以作为教学示例材料发布。
你的反馈将直接用于修改，因此必须具体、可操作。

评分标准：每个维度 0-10 分。综合加权分 < 93 必须修改。

审查目标不是做“现实世界履历核验”，而是模拟真实 ATS + 招聘方人工初筛：
- 候选人为虚构教学示例人物，真实性只锚定不可变字段、技能出处一致性、时间线自洽、scope 与量化的叙事可信度
- 不要因为“现实里这个职称通常不做该技术”而直接扣分
- 只有当简历自身没有提供足够的业务背景、ownership 限定语、cross-functional 解释或时间范围说明，导致 HR 很可能产生质疑时，才作为问题提出
- 跨领域接触技术栈本身是允许的，重点审查“是否被讲圆”

输出要求：
- 只保留会真实影响 ATS 或 HR 信任的高信号发现
- 每个维度最多返回 2 条 findings；不要写“无需修改”或纯正向表扬
- 若全篇无 critical/high，仅剩少量 medium/low 级润色问题，则综合分通常应在 93-97 区间，而不是机械压在 80 多分
- 默认情况下，fix 建议应尽量“局部、可执行、低扰动”：优先建议补 1 条 bullet、改 1 句 summary、补 1 个 skills 证据、收紧 1 处 scope
- 但当简历虽然真实、却明显被 seed phrasing / 弱 framing / 旧骨架束缚，导致 JD 信号不足时，你必须明确允许结构性重写：
  可以重写 summary、skills 分组、bullet 取舍、project baseline 和经历 framing，只要不可变字段、真实性和职业主线保持成立
- 不要把“尽量低扰动”理解成“不能重写”；对可修复但被旧稿束缚的简历，应该输出足够大胆的 rewrite 指令
- 对 JD must-have 技术，fix 方向一律是“补正文证据并保持技能保留”，不是删除
"""


def build_unified_review_prompt(resume_md: str, jd, review_scope: str = "full") -> str:
    """构建统一审查 prompt，返回 JSON 格式的综合审查结果"""

    tech_required_str = ", ".join(jd.tech_required) if jd.tech_required else "（无）"
    tech_preferred_str = ", ".join(jd.tech_preferred) if jd.tech_preferred else "（无）"
    immutable_block = _review_immutable_block(jd.company)
    bytedance_mode = is_bytedance_target_company(jd.company)
    scope_note = _build_review_scope_note(review_scope, bytedance_mode=bytedance_mode)

    return f"""请对以下简历进行严格的 9 维度审查，返回 JSON 格式结果。

## 目标 JD

公司: {jd.company} | 岗位: {jd.title} | 角色类型: {jd.role_type} | 职级: {jd.seniority}
必须技术栈: {tech_required_str}
加分技术栈: {tech_preferred_str}
团队方向: {jd.team_direction or '（未说明）'}

不可变字段（必须与此完全一致）:
{immutable_block}

{scope_note}

## 待审查简历

{resume_md}

---

## 审查维度与权重

**R0 真实性审查 (权重 0.20)**
- 不可变字段（公司/职称/时间/地点）是否与规定完全一致？
- {"TikTok / ByteDance intern 这段经历如果出现 = CRITICAL（ByteDance 目标岗位必须完全删掉）" if bytedance_mode else "TikTok 职称必须为 `Software Engineer Intern`，出现 `Backend Development Engineer Intern` 或任何其他变体 = CRITICAL"}
- 全文（Summary、Skills、bullet、Achievements）是否存在中文字符？英文简历中出现中文字符 = CRITICAL（直接 FAIL）
- SKILLS 中的每个技术栈是否在正文 bullet 中有明确使用出处？
- 正文 bullet 中使用的每个技术栈是否都出现在 SKILLS 中？
- Summary 中提及的技术栈/事实是否与正文一致？
- 无出处技术 = CRITICAL（直接 FAIL）
- 不要因为技术”看起来不像该职称常见职责”就打 R0；那属于 R4 的 HR 异议模拟范围
- 对 DiDi，不要把以下表述误判为 company-wide 夸大：`Data lead within a 13-person cross-functional squad ...`，以及代表总部数据组织参加双周全球经营评审、向管理层和 LATAM 一线传递两周建议的 operating-review scope

**R1 撰写规范审查 (权重 0.15)**
- Summary 恰好 3 句，每句有 `**小标题:**` 格式？
- Summary 第 3 句（围棋句）是否使用高价值认知 header，如 pattern recognition / decision-making / systems judgment？
- 若围棋句被写进 collaboration / teamwork / problem solver 一类低信号 header，记为 high
- 每段经历 4-6 条 bullet，每项目 4-6 条 bullet？
- 恰好 2 个项目（至少 1 个工作经历）？
- 每条 bullet 以强动词开头，以 `.` 结尾？
- XYZ 格式（动词+技术+量化/业务结果）？
- 跨经历叙事结构是否有差异化，不逐条相同？
- **加粗质量审查**：
  - 除 `## Skills` section 外，正文中的技术栈名词和量化数字是否已加粗？（漏加 = medium）
  - `## Skills` section 中只能加粗类别标题，不得加粗单个技术栈
  - 是否存在修饰语/限定词加粗？如 `**team-maintained**`、`**existing**`、`**internal**`、`**our**` 等 = medium finding
  - `workflow`、`pipeline`、`dashboard` 等结构词是否被孤立加粗？（非产品名时 = medium）
- **SKILLS 行密度审查**：
  - 每个 Skills 类别是否至少包含 4 个技术栈？少于 4 个 = high（孤行）
  - 每个 Skills 行（含类别标题）总词数是否超过 14？超过 = high（必须拆分/改名）
  - 类别数量是否大致保持在 2-4 个；若为满足 14 词硬上限扩到 5 个可接受
- **Project baseline 行审查**：
  - 每个项目是否有 `> ` 开头的背景行（blockquote）？缺失 = low
  - baseline 行是否描述了具体业务痛点/背景，而非仅重复项目标题？重复 = low
- **Achievements section 审查**：
  - section header 是否为 `## Achievements`？写成 `## Additional Information` 等变体 = medium
  - 是否恰好 1 条 bullet，格式是否为：`China national certified Go **2-dan** — city **champion** (2022) and third place (2023).`？
  - 加粗是否仅限 `2-dan` 和 `champion`，年份不加粗？违反 = low
  - {"是否出现任何 TikTok / ByteDance intern 段落？若出现 = critical" if bytedance_mode else "TikTok 职称是否为 `Software Engineer Intern`（不得含 \"Backend Development\"）？违反 = critical"}

**R2 JD适配审查 (权重 0.20)**
- SKILLS 是否包含 JD 所有必须技术？
- 每个 JD 必须技术是否在正文有实质性使用（不只是在 SKILLS 列出）？
- 若某个 JD 必须技术只出现在 Skills / Summary，却没有任何 experience / project 正文出处，应视为真实失分点
- 团队业务方向（team_direction）与正文叙事是否对齐？
- 若某个 JD 必须技术缺少正文证据，fix 应优先是补强/扩写正文使用场景，而不是建议删除该技术
- 对 JD must-have 技术，禁止建议从 Summary、Skills 或正文中删除；唯一正确方向是补正文证据并重写相应 bullets/projects
- 如果问题只需局部补强，请明确指出最小修改单元，例如 “在最相关经历第2条 bullet 增补 X 技术证据” 或 “把 Summary 第1句改成 Y 方向”
- 若目标行业较陌生，但候选人已具备可迁移的系统/数据/平台模式，允许通过“领域桥接语言”满足适配度；不要机械要求其必须拥有直接行业本体经历

**R3 炫技审查 (权重 0.10)**
- 是否存在 ownership/动词强度明显超出该经历可解释范围？
- {"是否错误地重新引入了 ByteDance / TikTok intern，以规避工作经历和课程项目证据不足？" if bytedance_mode else "TikTok intern 是否使用了过于高级的动词（Led/Architected/Drove）？"}
- Temu junior 是否有超出 individual contributor scope 的声明？
- stretch 技术若有明确业务背景、团队维护限定语、配合开发/集成语气，则不应因为“跨域接触”本身扣分

**R4 合理性审查 (权重 0.20)**
- 工作要点、项目标题、项目内容所反映的转行故事是否足以打消真实 HR 的本能疑问？
- 项目的存在本身是否合理（是否需要说明注释）？
- 量化数字是否可信（改善幅度、规模数字是否符合该业务背景）？
- 跨职能团队lead角色、跨栈开发、转岗路径是否有足够的小字说明/限定语/业务背景来完成自证？
- Summary 是否先把职业线解释清楚，并在首屏提炼出全文最强、最贴目标岗位的信号，而不是把高价值信息埋在后文？
- 若 Summary 开头仍在强调“从 data analytics 转向工程”“擅长 collaboration/problem solving”这类弱 framing，或使用泛泛而谈/安全但低信息量的角色定位，而没有先给出更强的 role-aligned signal，应作为真实失分点
- 对陌生行业 JD，如果 Summary 或项目 baseline 已清楚说明“哪些平台/数据/可靠性模式可以迁移到该行业”，这应视为加分，而不是因为缺少直接行业经历而扣分

**R5 逻辑审查 (权重 0.10)**
- Experience 顺序是否严格倒序（{_experience_order_text(jd.company)}）？
- SKILLS 分类逻辑是否清晰，是否有隐性重复条目？
- Skills 类别标题是否足够有信息量、能让 recruiter 一眼看懂分类逻辑？像 `APIs`、`Misc`、`Other` 这类模糊标题应扣分
- 技术栈在三段经历中是否有合理的差异化分布，还是机械重复？
- 每段经历内 bullet 之间是否逻辑连贯？
- Summary 是否是对整份简历的准确归纳（不多不少）？

**R6 竞争力审查 (权重 0.05)**
- 量化数据是否具体可信，数字是否有区分度？
- 项目亮点是否能体现该候选人与普通候选人的差异？
- Summary 的转行叙事与目标岗位的关联逻辑是否流畅自然？

---

## 输出格式

请严格按以下 JSON 格式输出（不要有任何额外文字）：

```json
{{
  "scores": {{
    "r0_authenticity": {{
      "score": <0-10>,
      "weight": 0.20,
      "verdict": "<pass|fail>",
      "findings": [
        {{"severity": "<critical|high|medium|low>", "field": "<具体位置>", "issue": "<问题描述>", "fix": "<具体修改建议>"}}
      ]
    }},
    "r1_writing_standard": {{
      "score": <0-10>,
      "weight": 0.15,
      "verdict": "<pass|fail>",
      "findings": []
    }},
    "r2_jd_fitness": {{
      "score": <0-10>,
      "weight": 0.20,
      "verdict": "<pass|fail>",
      "findings": []
    }},
    "r3_overqualification": {{
      "score": <0-10>,
      "weight": 0.10,
      "verdict": "<pass|fail>",
      "findings": []
    }},
    "r4_rationality": {{
      "score": <0-10>,
      "weight": 0.20,
      "verdict": "<pass|fail>",
      "findings": []
    }},
    "r5_logic": {{
      "score": <0-10>,
      "weight": 0.10,
      "verdict": "<pass|fail>",
      "findings": []
    }},
    "r6_competitiveness": {{
      "score": <0-10>,
      "weight": 0.05,
      "verdict": "<pass|fail>",
      "findings": []
    }}
  }},
  "weighted_score": <0-100, 保留1位小数>,
  "overall_verdict": "<pass|fail>",
  "critical_count": <整数>,
  "high_count": <整数>,
  "needs_revision": <true|false>,
  "revision_priority": [
    "<最优先修改事项1（一句话）>",
    "<最优先修改事项2（一句话）>"
  ],
  "revision_instructions": "<如果 needs_revision=true，给出完整修改指令（具体到每处修改）；否则为空字符串>"
}}
```

评分指南：
- 9.5-10: 完美，无问题
- 9.0-9.4: 优秀，仅有 low 级别建议
- 8.0-8.9: 良好，有 medium 问题需优化
- 7.0-7.9: 有 high 问题，必须修改
- < 7.0: 有 critical 问题，FAIL

额外校准：
- 发现若仅为格式润色、分类命名、轻微措辞重复，不应轻易打到 8.5 以下
- 若 0 critical 且 0 high，并且 JD 必须技术完整覆盖、转岗叙事自洽，则综合分应优先落在 93+，除非存在会显著影响 HR 信任的中等级结构问题
- revision_priority 应优先列出“最小但最高杠杆”的 1-2 个改动，而不是笼统要求整份简历重写

综合加权分 = sum(score_i * weight_i) * 10

若当前处于 rewrite 审查模式，revision_priority 和 revision_instructions 必须体现“可重写到 pass 的最高杠杆改法”。只有当你判断该 JD 与候选人背景天然不适配、继续重写也难以自洽时，才应给出明确 reject 信号。

只输出 JSON，不要其他内容。"""


# ══════════════════════════════════════════════════════════════
# REVISION PROMPT
# ══════════════════════════════════════════════════════════════

def build_revision_prompt(
    resume_md: str,
    review_result: dict,
    plan_text: str = "",
    tech_required: List[str] = None,
    jd_title: str = "",
    target_company: str = "",
) -> str:
    """
    构建精准修改 prompt（仅在综合分 < 93 时触发）。

    新增参数：
      plan_text     — 原始写作 PLAN（技术分配策略），让 Reviser 能做结构性决策
      tech_required — JD 必须技术列表，确保 revision 优先补齐覆盖缺口
      jd_title      — 目标岗位名称，供 Reviser 对齐叙事方向
    """
    revision_instructions = review_result.get("revision_instructions", "")
    priority = review_result.get("revision_priority", [])
    score = review_result.get("weighted_score", 0)
    tech_required = tech_required or []

    priority_str = "\n".join(f"  {i+1}. {p}" for i, p in enumerate(priority))

    # 汇总所有 critical/high findings
    critical_high = []
    for dim_id, dim_data in review_result.get("scores", {}).items():
        for f in dim_data.get("findings", []):
            if f.get("severity") in ("critical", "high"):
                critical_high.append(
                    f"[{dim_id}] [{f['severity'].upper()}] {f['field']}: {f['issue']} → 修改建议: {f['fix']}"
                )

    findings_str = "\n".join(critical_high) if critical_high else "（无 critical/high 问题）"

    # 原始 PLAN 部分（若有）
    plan_section = ""
    if plan_text.strip():
        plan_section = f"""
## 原始技术分配 PLAN（revision 必须遵守此规划，不得凭空引入计划外技术）

{plan_text.strip()}

---
"""

    # JD 必须技术（若有）
    tech_section = ""
    if tech_required:
        tech_section = f"""
## JD 必须技术（所有必须技术均需在正文有实质使用出处）
{', '.join(tech_required)}

"""
    special_block = BYTEDANCE_REVISION_SPECIAL_BLOCK if is_bytedance_target_company(target_company) else ""

    jd_title_line = f"目标岗位: {jd_title}\n" if jd_title else ""

    return f"""请按照以下审查结果，对简历进行精准修改。
{jd_title_line}
## 当前评分: {score:.1f}/100（目标: 93 分以上）
{plan_section}{tech_section}
{special_block}
## 最优先修改事项
{priority_str}

## 所有 CRITICAL/HIGH 问题（必须全部修复）
{findings_str}

## 详细修改指令
{revision_instructions}

## 修改原则
1. 只修改上方指出的问题，其他内容保持不变
2. 若 PLAN 已提供，技术分配须遵循 PLAN；若需在正文补充某技术，选择 PLAN 中已规划该技术的经历
3. 修复 SKILLS ↔ 正文不一致时：优先调整正文 bullet，不随意增删 SKILLS 条目
4. 对 JD must-have 技术，绝不允许通过删除来过关；必须补正文证据。仅非必须技术在确实无法自然嵌入时才可删除
5. 保持所有不可变字段（公司/职称/时间/地点）完全不变
6. {_experience_order_rule(target_company)}
7. 修复后的简历必须满足所有格式硬约束
8. 若目标 JD 属于候选人不自然直连的行业域，优先补充 1 句 summary bridge 或 1 条 project baseline bridge，而不是硬改整段经历去假装已有该行业本体经历

## 原始简历
{resume_md}

{CANONICAL_OUTPUT_TEMPLATE}

{RESUME_MARKDOWN_ONLY_RESPONSE_LINE}"""


def build_seed_retarget_prompt(
    seed_resume_md: str,
    jd,
    *,
    seed_label: str = "",
    route_mode: str = "retarget",
    top_candidate: dict | None = None,
) -> str:
    """
    基于已有高质量 seed resume 做最小改动式 retarget。
    """
    tech_required = ", ".join(jd.tech_required) if jd.tech_required else "（无明确列出）"
    tech_preferred = ", ".join(jd.tech_preferred) if jd.tech_preferred else "（无）"
    top_candidate = top_candidate or {}
    route_mode = route_mode or "retarget"
    change_budget = "20%" if route_mode == "reuse" else "35%"
    missing_required = ", ".join(top_candidate.get("missing_required", [])[:8]) or "（无明显缺口）"
    seed_line = f"当前命中的 seed: {seed_label or top_candidate.get('label', 'Unknown seed')}"
    route_line = f"路由模式: {route_mode}"
    same_company = bool(top_candidate.get("same_company"))
    seed_company = top_candidate.get("seed_company_name", "") or jd.company
    source_job_id = top_candidate.get("seed_source_job_id", "")
    company_anchor = bool(top_candidate.get("company_anchor"))
    project_pool_block = build_project_pool_prompt_block(top_candidate.get("project_ids", []) or [])
    company_mode_block = ""
    target_specific_block = _target_specific_context_block(jd.company)
    if same_company:
        anchor_phrase = "这是该公司的公司内锚点 seed。" if company_anchor else "这是该公司已存在的公司内 seed。"
        source_phrase = f"seed 来源岗位 job_id: {source_job_id}" if source_job_id else "seed 来源岗位: 已登记公司内来源"
        if is_bytedance_target_company(jd.company):
            company_mode_block = f"""
## ByteDance seed 参考模式（覆盖同公司微调规则）
- 当前目标岗位命中了 ByteDance 同公司 seed，但该 seed 只能作为弱参考
- {anchor_phrase}
- {source_phrase}
- 不得继承 seed 中的 TikTok / ByteDance intern 叙事骨架、项目或 bullet
- 只允许借用 seed 中仍然适用于 DiDi、Temu、Georgia Tech CS coursework/projects 的技术 framing
- 任何与 TikTok / ByteDance intern 绑定的内容都必须删掉，再重写成新的两段全职经历 + GT CS 项目版本
"""
        else:
            company_mode_block = f"""
## 同公司一致性模式（最高优先级）
- 当前目标岗位与 seed 同属 **{seed_company}**
- {anchor_phrase}
- {source_phrase}
- 把公司内的 team / domain / 项目池视为“准不可变骨架”，不要写成完全不同的人做了完全不同的事
- 允许调整的只有：Summary 侧重点、Skills 少量技术取舍、同一项目的不同强调角度、少量 bullet 技术细节
- 不允许把业务方向改成明显不同的另一条线，不允许引入与现有公司版本完全无关的新项目池
- 同一公司家族下，全部版本合计最多保留 4 个项目；TikTok/Bytedance 实习项目最多 2 个
- 写法目标是：读者能自然感觉“同一个人在讲同一批经历，只是针对不同岗位换了强调方式”
"""

    return f"""你正在基于一份已经通过高标准审查的 seed resume，为新的 JD 生成派生简历。

目标：尽可能少改动，在保留 seed 叙事骨架、结构质量和可信 scope 的前提下，让简历对齐目标 JD。

{seed_line}
{route_line}
目标岗位: {jd.title} @ {jd.company}

{target_specific_block}

## Retarget 原则
1. 这是在现有 seed 上微调，不是从零重写
2. 总改动预算控制在约 {change_budget}
3. 优先保留已成熟的 summary phrasing、经历骨架、项目结构和量化风格
4. 先改 Summary、Skills、最相关经历与对应项目，再考虑其余段落
5. 所有不可变字段（公司/部门/职称/时间/地点）必须完全不变
6. {_experience_order_rule(jd.company)}
7. 必须把 JD 必需技术写到正文里有真实使用出处，不能只堆在 SKILLS
8. 不要为了补技术而把 scope 夸大；intern/junior 一律保持 team-contributed framing
9. 若 route_mode = reuse，默认只做轻改；若 route_mode = retarget，可做中等幅度改动，但仍不得改写候选人的核心职业叙事
10. 如果目标 JD 带有行业语境（如 fintech / healthcare / security / devops），优先通过 summary 和项目业务 framing 对齐，而不是凭空新增不可信 ownership
11. 如果进入同公司一致性模式，优先复用现有 team/domain/project 骨架；把变化理解为“同项目换一种表述”，而不是“换了一套完全不同的工作内容”
12. 保留合法的 DiDi senior scope，不要把它机械压缩成 generic collaboration phrasing；是否把该 scope 提到 summary/bullet，由目标 JD 决定
13. 如果目标 JD 属于自动驾驶 / physical AI / robotics / spatial-sensor systems 等陌生行业，优先在 Summary 或项目 baseline 中写“transferable infrastructure / pipeline / reliability patterns”，不要假装已有 perception、planning、simulation 或 robotics 本体 ownership

## 目标 JD 关键信息
- Role type: {jd.role_type}
- Seniority: {jd.seniority}
- Must-have tech: {tech_required}
- Preferred tech: {tech_preferred}
- 当前路由识别的主要缺口: {missing_required}

{company_mode_block}
{project_pool_block}

## Seed 简历
{seed_resume_md}

{CANONICAL_OUTPUT_TEMPLATE}

{RESUME_MARKDOWN_ONLY_RESPONSE_LINE}"""


def build_upgrade_revision_prompt(
    resume_md: str,
    review_result: dict,
    *,
    tech_required: List[str] | None = None,
    jd_title: str = "",
    target_company: str = "",
    route_mode: str = "",
    seed_label: str = "",
    plan_text: str = "",
) -> str:
    """构建更高自由度的历史重评升级 prompt。"""
    revision_instructions = review_result.get("revision_instructions", "")
    priority = review_result.get("revision_priority", [])
    score = review_result.get("weighted_score", 0)
    tech_required = tech_required or []

    priority_str = "\n".join(f"  {i+1}. {p}" for i, p in enumerate(priority)) or "  1. Raise the resume to a true pass."

    critical_high = []
    for dim_id, dim_data in review_result.get("scores", {}).items():
        for finding in dim_data.get("findings", []):
            if finding.get("severity") in ("critical", "high", "medium"):
                critical_high.append(
                    f"[{dim_id}] [{finding['severity'].upper()}] {finding['field']}: "
                    f"{finding['issue']} → 修改建议: {finding['fix']}"
                )
    findings_str = "\n".join(critical_high) if critical_high else "（无结构化 findings，可主动做 JD-aware 升级）"
    tech_line = ", ".join(tech_required) if tech_required else "（无明确 must-have 技术）"
    plan_section = ""
    if plan_text.strip():
        plan_section = f"""
## 历史 PLAN / 技术分配参考
{plan_text.strip()}

注意：这只作为真实性与技术分配参考，不是 rewrite 的束缚。若旧 PLAN 本身导致 JD 对齐不足，可以在不破坏真实性的前提下重排表达与重点。
"""
    special_block = BYTEDANCE_UPGRADE_SPECIAL_BLOCK if is_bytedance_target_company(target_company) else ""

    return f"""请把下面这份历史简历做一次面向目标 JD 的升级式重写，而不是仅做字面修补。

目标岗位: {jd_title or 'Unknown'}
当前评分: {score:.1f}/100
历史来源: route_mode={route_mode or 'unknown'} | seed_label={seed_label or 'unknown'}

## 升级目标
1. 提高 JD 匹配度、summary 信号密度、scope 叙事完整度和整体逻辑自洽
2. 修复 reviewer 指出的所有问题，尤其是 summary、skills、DiDi scope 与 seniority signal
3. 若当前版本对 senior 价值表达偏弱，可以重写 summary、Skills、DiDi bullets、项目 framing
4. 允许中等幅度重写，但不得改动不可变字段，不得破坏既有职业故事主线

## 最优先修改事项
{priority_str}

## 审查发现
{findings_str}

## 必须技术
{tech_line}

{plan_section}
{special_block}

## 关键升级规则
1. Summary 必须重新评估，不要默认沿用旧 phrasing；三句都要服务目标 JD
2. 如果 DiDi 的 senior operating scope 能显著增强匹配度，可以把该信号提炼进 summary，但要简洁，不要和 bullet 机械重复
3. 如果目标 JD 带有陌生行业语境，优先补一条“领域桥接”语句，说明现有平台/数据/可靠性模式如何迁移到该行业
3. DiDi scope note 若保留，统一写成：
   `> Data lead within a **13-person** cross-functional squad spanning product, backend, frontend, mobile, and ops.`
4. 如果目标岗位需要更强 senior / stakeholder / cross-functional signal，可以在 DiDi bullets 中使用这句：
   `Represented the headquarters data organization in biweekly global operating reviews, and translated performance signals into two-week recommendations adopted by management and LATAM frontline teams.`
5. 上面这条 DiDi bullet 只在它确实提升目标岗位匹配度时使用；不要为了“显得大”而强塞
6. Skills 既要满足格式硬约束，也要确保没有遗漏正文/JD 的关键技术；不要靠暴力删减过关
7. 对 JD must-have 技术，只能补正文证据、扩写项目或重写相关 bullet，不能删除
8. 围棋 summary 句必须是高价值认知信号，不要写成 collaboration/teamwork 论据
9. 保留所有不可变字段（公司/部门/职称/时间/地点）完全不变
10. {_experience_order_rule(target_company)}
11. 输出必须仍然满足全部格式硬约束
12. 如果 seed phrasing、旧 summary、旧 bullet 选择本身就是失分原因，可以直接替换，不要为了“保留 seed”而保留弱表达
13. rewrite 的目标是通过，而不是尽量少改；只要真实且自洽，可以换掉低质量旧表述

## 原审查详细修改指令
{revision_instructions}

## 原始简历
{resume_md}

{CANONICAL_OUTPUT_TEMPLATE}

直接输出升级后的完整简历 Markdown，不要附带解释。"""
