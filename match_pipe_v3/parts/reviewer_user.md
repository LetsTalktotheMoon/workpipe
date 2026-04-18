请对以下简历进行严格的 9 维度审查，返回 JSON 格式结果。

## 审查维度与权重

**R0 真实性审查 (权重 0.20)**
- 不可变字段（公司/职称/时间/地点）是否与规定完全一致？
- TikTok 职称必须为 `Software Engineer Intern`，出现 `Backend Development Engineer Intern` 或任何其他变体 = CRITICAL
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
  - TikTok 职称是否为 `Software Engineer Intern`（不得含 "Backend Development"）？违反 = critical

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
- TikTok intern 是否使用了过于高级的动词（Led/Architected/Drove）？
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
- Experience 顺序是否严格倒序（TikTok（2025）→ DiDi（2022-2024）→ Temu（2021-2022））？
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