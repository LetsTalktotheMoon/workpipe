# Match Pipe V2 — Canonical Prompt Document

> 这是 `match_pipe_v2` 的全量 prompt 唯一文档。
> 修改方式：直接编辑本文档的对应段落，然后运行 `python sync_from_canonical_doc.py`。
> 若某段文本在多个 domain 中使用，请将其提取到下方的 **Shared Sentences** 章节，
> 并在使用处用 `{{sentences.key_name}}` 占位符替换。

---

## Shared Sentences

<!-- SENTENCE: allowed_role_lenses__analyst__backend__data__pm__s -->
allowed role lenses: analyst, backend, data, pm, swe
<!-- END_SENTENCE: allowed_role_lenses__analyst__backend__data__pm__s -->

<!-- SENTENCE: allowed_role_lenses__analyst__data__pm_1 -->
allowed role lenses: analyst, data, pm
<!-- END_SENTENCE: allowed_role_lenses__analyst__data__pm_1 -->

<!-- SENTENCE: code_fence_close -->
```
<!-- END_SENTENCE: code_fence_close -->

<!-- SENTENCE: didi_immutable -->
- DiDi: Senior Data Analyst | DiDi · IBG · Food | Sep 2022 – May 2024 | Beijing/Mexico
<!-- END_SENTENCE: didi_immutable -->

<!-- SENTENCE: didi_scope_note -->
`> Data lead within a **13-person** cross-functional squad spanning product, backend, frontend, mobile, and ops.`
<!-- END_SENTENCE: didi_scope_note -->

<!-- SENTENCE: empty -->
},
<!-- END_SENTENCE: empty -->

<!-- SENTENCE: empty_1 -->
}
<!-- END_SENTENCE: empty_1 -->

<!-- SENTENCE: findings_1 -->
"findings": []
<!-- END_SENTENCE: findings_1 -->

<!-- SENTENCE: json -->
```json
<!-- END_SENTENCE: json -->

<!-- SENTENCE: md -->
```md
<!-- END_SENTENCE: md -->

<!-- SENTENCE: output_bullet -->
* Bullet.
<!-- END_SENTENCE: output_bullet -->

<!-- SENTENCE: output_dates_line -->
*Dates | Location*
<!-- END_SENTENCE: output_dates_line -->

<!-- SENTENCE: output_header_bullet -->
* **Header:** Sentence.
<!-- END_SENTENCE: output_header_bullet -->

<!-- SENTENCE: output_skill_line -->
* **Category:** skill1, skill2, skill3
<!-- END_SENTENCE: output_skill_line -->

<!-- SENTENCE: output_title_line -->
### Title | Company · Department
<!-- END_SENTENCE: output_title_line -->

<!-- SENTENCE: represented_the_headquarters_data_organization_in -->
`Represented the headquarters data organization in biweekly global operating reviews, and translated performance signals into two-week recommendations adopted by management and LATAM frontline teams.`
<!-- END_SENTENCE: represented_the_headquarters_data_organization_in -->

<!-- SENTENCE: scope_note__通常不需要_1 -->
scope note: 通常不需要
<!-- END_SENTENCE: scope_note__通常不需要_1 -->

<!-- SENTENCE: scope_note__需要_1 -->
scope note: 需要
<!-- END_SENTENCE: scope_note__需要_1 -->

<!-- SENTENCE: score____0_10_1 -->
"score": <0-10>,
<!-- END_SENTENCE: score____0_10_1 -->

<!-- SENTENCE: seed_来源岗位__已登记公司内来源 -->
- seed 来源岗位: 已登记公司内来源
<!-- END_SENTENCE: seed_来源岗位__已登记公司内来源 -->

<!-- SENTENCE: temu_immutable -->
- Temu: Data Analyst | Temu · R&D | Jun 2021 – Feb 2022 | Shanghai
<!-- END_SENTENCE: temu_immutable -->

<!-- SENTENCE: verdict_____pass_fail_1 -->
"verdict": "<pass|fail>",
<!-- END_SENTENCE: verdict_____pass_fail_1 -->

<!-- SENTENCE: weight___0_10_1 -->
"weight": 0.10,
<!-- END_SENTENCE: weight___0_10_1 -->

<!-- SENTENCE: weight___0_20_1 -->
"weight": 0.20,
<!-- END_SENTENCE: weight___0_20_1 -->

<!-- SENTENCE: writer_plan_jd_tech -->
必要 JD 技术（放在这里）: [列出]
<!-- END_SENTENCE: writer_plan_jd_tech -->

<!-- SENTENCE: writer_plan_tech_list -->
→ 此经历 bullet 将使用的完整技术列表: [最终列表]
<!-- END_SENTENCE: writer_plan_tech_list -->

<!-- SENTENCE: 公司池上限__2 -->
- 公司池上限: 2
<!-- END_SENTENCE: 公司池上限__2 -->

<!-- SENTENCE: 这是该公司的公司内锚点_seed -->
- 这是该公司的公司内锚点 seed。
<!-- END_SENTENCE: 这是该公司的公司内锚点_seed -->

---

## ByteDance Rules

<!-- DOMAIN: bytedance_rules -->

<!-- ATOM: boundary -->

<!-- SUB_ATOM: writer -->

  <!-- SUB_SUB_ATOM: heading --> ### ByteDance 特殊写作边界 <!-- END_SUB_SUB_ATOM: heading -->

  <!-- SUB_SUB_ATOM: rules -->
- 不得写入或提及 TikTok / ByteDance intern 这段经历
- 目标岗位只能使用 DiDi、Temu 和 Georgia Tech CS coursework/projects 作为证据池；GT 教育主干仍按共享教育块保留，ByteDance 只是进一步加权 GT coursework/projects。
  <!-- END_SUB_SUB_ATOM: rules -->

<!-- END_SUB_ATOM: writer -->

<!-- SUB_ATOM: retarget -->

  <!-- SUB_SUB_ATOM: heading --> ## ByteDance 目标公司特殊模式 <!-- END_SUB_SUB_ATOM: heading -->

  <!-- SUB_SUB_ATOM: rules -->
- 对 ByteDance 目标岗位，候选人证据池中不得出现 TikTok / ByteDance intern 这段经历，也不得在 Summary、Skills、Experience、Project baseline 或 bullets 中提及它
- 只允许从以下三类材料出发构建简历：DiDi 全职经历、Temu 全职经历、Georgia Tech CS coursework/projects
- 当 JD 需要更强的软件工程或系统实现信号时，优先把 Georgia Tech CS coursework/projects 提升为主要技术证据；GT 教育主干仍是共享材料，而不是把缺口强行塞回 ByteDance/TikTok intern
- seed 若包含 TikTok / ByteDance intern，只能作为弱参考；你必须主动删掉这段经历，再按新的证据池重写
  <!-- END_SUB_SUB_ATOM: rules -->

<!-- END_SUB_ATOM: retarget -->

<!-- SUB_ATOM: upgrade -->

  <!-- SUB_SUB_ATOM: heading --> ## ByteDance 特殊要求 <!-- END_SUB_SUB_ATOM: heading -->

  <!-- SUB_SUB_ATOM: rules -->
- 删除任何 TikTok / ByteDance intern 内容，不要把它当作可修补素材
- 证据池仅限 DiDi、Temu、Georgia Tech CS coursework/projects
- 若旧稿因为 seed 骨架保留了 TikTok / ByteDance intern，必须直接推翻该部分并重写
  <!-- END_SUB_SUB_ATOM: rules -->

<!-- END_SUB_ATOM: upgrade -->

<!-- SUB_ATOM: reviewer -->

  <!-- SUB_SUB_ATOM: heading --> ## ByteDance 特殊审查要求 <!-- END_SUB_SUB_ATOM: heading -->

  <!-- SUB_SUB_ATOM: rules -->
- 对 ByteDance 目标岗位，TikTok / ByteDance intern 这段经历必须完全不存在
- 若简历仍引用了 TikTok / ByteDance intern，视为 critical，并要求删除后仅用 DiDi / Temu / Georgia Tech CS coursework/projects 重写；GT 教育主干仍按共享材料保留
  <!-- END_SUB_SUB_ATOM: rules -->

<!-- END_SUB_ATOM: reviewer -->

<!-- END_ATOM: boundary -->

<!-- ATOM: reviewer_user -->
R0: TikTok / ByteDance intern 这段经历如果出现 = CRITICAL（ByteDance 目标岗位必须完全删掉）
R1: 是否出现任何 TikTok / ByteDance intern 段落？若出现 = critical
R3: 是否错误地重新引入了 ByteDance / TikTok intern，以规避工作经历和课程项目证据不足？
R5: Experience 顺序是否严格倒序（DiDi（2022-2024）→ Temu（2021-2022））？

<!-- END_ATOM: reviewer_user -->

<!-- END_DOMAIN: bytedance_rules -->

---

## Candidate Context

<!-- DOMAIN: candidate_context -->

<!-- ATOM: shared_experience -->
## 候选人经历框架（⚡=不可变字段，其余可由 Writer 决定）

### Temu — Data Analyst (不可变)
- ⚡公司: Temu | ⚡部门: R&D | ⚡职称: Data Analyst
- ⚡时间: Jun 2021 – Feb 2022 | ⚡地点: Shanghai
- 时长: 8个月 | 级别: junior
- 禁用动词: Led, Architected, Drove, Spearheaded, Directed
- Scope上限: individual contributor, 8个月短期经历
- 自然技术栈 core（几乎必然使用）: Hive, Pandas, Python, SQL, Spark SQL
- 自然技术栈 extended（合理推断可能接触）: A/B Testing, Airflow, Jupyter, Matplotlib, NumPy, scikit-learn
- 自然技术栈 stretch（特定场景可能接触，需叙事支撑）: ETL, Flask, HiveQL, Kafka, Redis...

### DiDi — Senior Data Analyst (不可变)
- ⚡公司: DiDi | ⚡部门: IBG · Food | ⚡职称: Senior Data Analyst
- ⚡时间: Sep 2022 – May 2024 | ⚡地点: Beijing/Mexico
- 时长: 20个月 | 级别: mid_senior
- 允许动词: Led, Coordinated, Represented, Drove
- Scope上限: data lead within a 13-person cross-functional squad; may represent the headquarters data organization in biweekly global operating reviews, with recommendations adopted by management and LATAM frontline teams
- 领导力: 13人跨职能团队acting lead（前端, 后端, 全栈, 移动端, PM 等）
- 全球汇报: 每两周全球会议代表北京数据中台总部发言
- 决策传导: 数据决策直接进入管理层和一线
- 自然技术栈 core（几乎必然使用）: ETL, Flask, Kafka, Python, REST, SQL
- 自然技术栈 extended（合理推断可能接触）: Airflow, Docker, Java, MySQL, Pandas, React, Redis
- 自然技术栈 stretch（特定场景可能接触，需叙事支撑）: Go, Kubernetes, Microservices, MongoDB, TypeScript, gRPC...

<!-- END_ATOM: shared_experience -->

<!-- ATOM: shared_education -->
### 教育经历（可根据 JD 方向选择列哪些）
- M.S. Computer Science | Georgia Institute of Technology | Expected May 2026
  → 当 UIUC MSIM 出现时写为 M.S. Computer Science (OMSCS)；  仅出现GT时直接写 M.S. Computer Science
- M.S. Information Management (MSIM) | University of Illinois Urbana-Champaign | Expected May 2026 — 保留当: Data方向/PM方向/信息管理相关岗位 | 可省略当: 纯SWE后端且与信息管理无关
- M.S. International Business | Beijing International Studies University | Sep 2018 – Jun 2021 — 保留当: FinTech/国际业务/金融数据方向 | 可省略当: 与目标岗位完全无关且简历空间紧张
- B.A. Philosophy & Psychology | Beijing Normal University | Sep 2014 – Jun 2018 — 保留当: TechPM(认知科学角度)/NLP(语言学角度)/UX Research | 可省略当: 大多数纯技术岗位

<!-- END_ATOM: shared_education -->

<!-- ATOM: shared_achievements -->
### 成就（融入 Summary 第3句）
- 中国国家认证围棋二段棋手，2022年度市赛第一，2023年度市赛第三

<!-- END_ATOM: shared_achievements -->

<!-- ATOM: generic_tiktok_branch -->
### TikTok — Software Engineer Intern (不可变)
- ⚡公司: TikTok | ⚡部门: Security | ⚡职称: Software Engineer Intern
- ⚡时间: Jun 2025 – Dec 2025 | ⚡地点: San Jose, USA
- 时长: 6个月 | 级别: intern
- 禁用动词: Led, Architected, Drove, Spearheaded, Managed
- Scope上限: intern, 6个月, 不可声称领导/架构决策
- 自然技术栈 core（几乎必然使用）: Docker, Go, Kafka, Kubernetes, PostgreSQL, Python, gRPC
- 自然技术栈 extended（合理推断可能接触）: AWS, Bedrock, CI/CD, ECS, GitHub Actions, Java, LLM, Linux, OpenAI, Prometheus, RAG, REST, Redis, S3
- 自然技术栈 stretch（特定场景可能接触，需叙事支撑）: Elasticsearch, Flink, GraphQL, LangChain, Microservices, MongoDB, React, Spring Boot, TensorFlow, Terraform, TypeScript...

<!-- END_ATOM: generic_tiktok_branch -->

<!-- ATOM: bytedance_education_branch -->
→ GT 教育主干对所有线路共享；ByteDance 目标岗位中，Georgia Tech CS coursework/projects 可以进一步提升为主要软件工程/系统实现证据来源。

<!-- END_ATOM: bytedance_education_branch -->

<!-- END_DOMAIN: candidate_context -->

---

## Context Blocks

<!-- DOMAIN: context_blocks -->

<!-- ATOM: sources -->

<!-- SUB_ATOM: seed -->

  <!-- SUB_SUB_ATOM: heading --> ## Seed 简历 <!-- END_SUB_SUB_ATOM: heading -->

  <!-- SUB_SUB_ATOM: template --> {{ seed_resume_md }} <!-- END_SUB_SUB_ATOM: template -->

<!-- END_SUB_ATOM: seed -->

<!-- SUB_ATOM: original -->

  <!-- SUB_SUB_ATOM: heading --> ## 原始简历 <!-- END_SUB_SUB_ATOM: heading -->

  <!-- SUB_SUB_ATOM: template --> {{ resume_md }} <!-- END_SUB_SUB_ATOM: template -->

<!-- END_SUB_ATOM: original -->

<!-- SUB_ATOM: jd -->

  <!-- SUB_SUB_ATOM: heading -->
## 目标 JD

  <!-- END_SUB_SUB_ATOM: heading -->

  <!-- SUB_SUB_ATOM: template -->
公司: {{ company }} | 岗位: {{ title }} | 角色类型: {{ role_type }} | 职级: {{ seniority }}
必须技术栈: {{ tech_required }}
加分技术栈: {{ tech_preferred }}
团队方向: {{ team_direction }}

不可变字段（必须与此完全一致）:
{{ immutable_block }}

  <!-- END_SUB_SUB_ATOM: template -->

<!-- END_SUB_ATOM: jd -->

<!-- SUB_ATOM: planner -->

  <!-- SUB_SUB_ATOM: heading --> ## Planner 输入 <!-- END_SUB_SUB_ATOM: heading -->

  <!-- SUB_SUB_ATOM: template -->
- 目标模式: {{ mode }}
- 公司: {{ company }}
- 职位: {{ title }}
- role_type: {{ role_type }}
- seniority: {{ seniority }}
- must-have 技术: {{ tech_required }}
- preferred 技术: {{ tech_preferred }}

## Matcher Packet
{{ data.sentences.json }}
{{ matcher_block }}
{{ data.sentences.code_fence_close }}

## Starter Resume
{{ data.sentences.md }}
{{ starter_block }}
{{ data.sentences.code_fence_close }}

  <!-- END_SUB_SUB_ATOM: template -->

<!-- END_SUB_ATOM: planner -->

<!-- SUB_ATOM: planner_writer -->

  <!-- SUB_SUB_ATOM: heading --> ## Planner Decision <!-- END_SUB_SUB_ATOM: heading -->

  <!-- SUB_SUB_ATOM: template -->
{{ data.sentences.json }}
{{ planner_json }}
{{ data.sentences.code_fence_close }}

## Matcher Evidence
{{ data.sentences.json }}
{{ matcher_json }}
{{ data.sentences.code_fence_close }}

## Historical Starter Resume
{{ data.sentences.md }}
{{ starter_block }}
{{ data.sentences.code_fence_close }}

  <!-- END_SUB_SUB_ATOM: template -->

<!-- END_SUB_ATOM: planner_writer -->

<!-- SUB_ATOM: planner_revision -->

  <!-- SUB_SUB_ATOM: heading --> ## Planner-first Revision Context <!-- END_SUB_SUB_ATOM: heading -->

  <!-- SUB_SUB_ATOM: template -->
- 当前版本评分: {{ weighted_score }}/100
- 当前是否通过: {{ passed }}
- 当前 reviewer 是否要求继续修改: {{ needs_revision }}

## Planner Carry-over
{{ planner_notes }}

## Planner Risks
{{ risk_notes }}

## Reviewer Priority
{{ priority }}

## Reviewer Findings
{{ findings_block }}

## Must-have Tech
- {{ must_have }}

## Existing Resume Draft To Revise
{{ data.sentences.md }}
{{ current_resume_md }}
{{ data.sentences.code_fence_close }}

  <!-- END_SUB_SUB_ATOM: template -->

<!-- END_SUB_ATOM: planner_revision -->

<!-- END_ATOM: sources -->

<!-- END_DOMAIN: context_blocks -->

---

## Format Constraints

<!-- DOMAIN: format_constraints -->

<!-- ATOM: shared_head -->
## 格式硬约束（违反=直接FAIL）

**结构规则**
- Summary: 恰好 3 句，每句格式：`* **角色定位短语:** 叙述句。`

<!-- END_ATOM: shared_head -->

<!-- ATOM: experience_order -->

<!-- SUB_ATOM: tiktok -->
- Experience 顺序: **严格倒序** — TikTok（2025）→ DiDi（2022-2024）→ Temu（2021-2022）
<!-- END_SUB_ATOM: tiktok -->

<!-- SUB_ATOM: bytedance -->
- Experience 顺序: **严格倒序** — DiDi（2022-2024）→ Temu（2021-2022）
<!-- END_SUB_ATOM: bytedance -->

<!-- END_ATOM: experience_order -->

<!-- ATOM: immutable_fields -->

<!-- SUB_ATOM: heading -->
**不可变字段（绝不可修改）**
<!-- END_SUB_ATOM: heading -->

<!-- SUB_ATOM: tiktok -->
- TikTok: Software Engineer Intern | TikTok · Security | Jun 2025 – Dec 2025 | San Jose, USA
{{ data.sentences.didi_immutable }}
{{ data.sentences.temu_immutable }}
<!-- END_SUB_ATOM: tiktok -->

<!-- SUB_ATOM: bytedance -->
{{ data.sentences.didi_immutable }}
{{ data.sentences.temu_immutable }}
- TikTok / ByteDance intern experience must be absent for ByteDance target roles.
<!-- END_SUB_ATOM: bytedance -->

<!-- END_ATOM: immutable_fields -->

<!-- ATOM: scope_rules -->

<!-- SUB_ATOM: heading -->
**职级 Scope 规则**
<!-- END_SUB_ATOM: heading -->

<!-- SUB_ATOM: tiktok -->
- TikTok (intern, 6个月): 禁用 Led/Architected/Drove/Spearheaded/Managed；体现个人贡献，不主张架构决策
  → bullet 数量建议 **4-5 条**（6个月实习期内独立成就不超过 5 条，超出则可信度下降）
<!-- END_SUB_ATOM: tiktok -->

<!-- SUB_ATOM: bytedance -->
- ByteDance 目标岗位: 不允许出现 TikTok / ByteDance intern；需要更多 SWE 证据时，优先把 Georgia Tech CS coursework/projects 作为主力软件工程/系统实现证据，而不是回填该实习。
<!-- END_SUB_ATOM: bytedance -->

<!-- SUB_ATOM: didi -->
- DiDi (mid-senior acting lead): 可用 Led/Coordinated/Drove；可展示 13 人跨职能团队领导力
<!-- END_SUB_ATOM: didi -->

<!-- SUB_ATOM: didi_global_bullet -->   {{ data.sentences.represented_the_headquarters_data_organization_in }} <!-- END_SUB_ATOM: didi_global_bullet -->

<!-- SUB_ATOM: temu -->
- Temu (junior): 禁用 Led/Architected/Drove/Spearheaded；仅体现 individual contributor 贡献
<!-- END_SUB_ATOM: temu -->

<!-- END_ATOM: scope_rules -->

<!-- ATOM: shared_mid -->
- 每段经历: 4-6 条 bullet，至少 1 条含量化数据
- 项目: 恰好 2 个（至少1个来自工作经历），每项目 4-6 条 bullet
- 项目位置: 项目紧跟对应经历，不单独设 `## Projects` section
- 项目背景行: 每个项目标题下必须紧接一行 `> ` 开头的 blockquote（一句话说明业务痛点/背景，不是重复项目标题），然后才是 bullet 列表
- DiDi scope note 若出现，必须是简短身份说明，不承担全部 leadership/decision story；推荐写法：
  {{ data.sentences.didi_scope_note }}

**SKILLS 一致性规则（最重要）**
- SKILLS 优先分 2-4 个类别；如为满足行宽约束可扩到 5 类
- 不允许出现孤行：单个 Skills 类别少于 **4** 个技术栈必须合并到相邻类别
- 每行（含类别标题）总词数必须 **≤ 14**；这是硬性标准，超过即 FAIL
- SKILLS 中只有分类标题使用 `**加粗**`，分类内技术栈一律纯文本逗号分隔，不要给单个技术栈加粗
- SKILLS 中每个技术栈**必须**在至少一条经历 bullet 或项目 bullet 中出现
- 经历/项目 bullet 中出现的每个技术栈**必须**在 SKILLS 中出现
- Summary 中提及的技术栈也必须在 SKILLS 中
- 禁止 SKILLS 中出现正文没有的技术栈（哪怕是 JD 要求的）
- 但对目标 JD 的 must-have 技术，不允许通过“删除 SKILLS/summary 中该技术”来规避问题；必须在正文补足实质使用证据

**内容规则**
- 每条 bullet: 强动词开头 + 技术实现 + 业务/量化结果（XYZ格式）
- 加粗规则（精确执行，不得扩大）：
  1. **技术栈名词**：语言/框架/工具/平台（如 Go, React, PostgreSQL, AWS Bedrock）— 必须加粗
  2. **量化数字及其直接关联词**：数字本身及紧跟的变化描述（如 `**32%**`、`**6** to **2**`、`**18 minutes**`）— 必须加粗
  3. **业务实体名词**：具名产品/服务/系统（如 `**security evidence service**`、`**merchant onboarding**`、`**City Launch Ops**`）— 必须加粗
  4. **禁止加粗修饰语**：`team-maintained`、`team-owned`、`intern-owned`、`existing`、`internal`、`our` 等限定词不得加粗
  5. **禁止加粗动词/结构词**：`workflow`、`pipeline`、`dashboard`、`process` 等纯结构描述词不得加粗（除非是已命名产品名称的一部分）
- 所有 bullet 以英文句号 `.` 结尾
- 禁止词: Passionate, Dedicated, Highly motivated, Hardworking, Enthusiastic, Self-starter, Detail-oriented, Team player, Results-driven
- 跨经历 bullet 叙事结构不得逐条相同，技术栈需有差异化分布

<!-- END_ATOM: shared_mid -->

<!-- ATOM: shared_tail -->
**数字合理性规则（违反 = r4 高风险）**
- 改善幅度 > 70%：必须加范围限定语，例如：
  "within team-owned service" / "on our internal dataset" / "in controlled staging tests"
- 改善幅度 > 90%：极为可疑，需降至 80% 以下，或拆分为绝对值表述（如 "from 12 min to 2 min"）
- 规模数字（如 1M+、100K+）：必须带来源限定，例如 "within a team-maintained pipeline" / "contributing to a service processing…"
- 不可同时在同一 bullet 内堆叠 3 个以上量化数字

**围棋成就**
- 融入 Summary 第 3 句，衔接目标岗位某一必要特质（如模式识别/战略思维/复杂系统决策）
- Summary 第 3 句的 header 必须是高价值认知信号，如 `Strategic Pattern Recognition` / `Analytical Decision-Making` / `Systems Judgment`
- 禁止把围棋写进 `Collaboration` / `Teamwork` / `Problem Solver` / `Delivery Fit` 一类低信号 header
- 措辞（Summary 中）：中国国家认证围棋二段棋手，2022年城市赛冠军，2023年城市赛季军

**Achievements section 规范（不可变）**
- 恰好 1 条 bullet，固定格式：
  `* China national certified Go **2-dan** — city **champion** (2022) and third place (2023).`
- 加粗仅限 `2-dan`（等级凭据）和 `champion`（最高成就）；年份作为括注，不加粗
- section header 必须为 `## Achievements`，不得写成 `## Additional Information` 或其他变体

<!-- END_ATOM: shared_tail -->

<!-- END_DOMAIN: format_constraints -->

---

## JD Context

<!-- DOMAIN: jd_context -->

<!-- ATOM: writer_jd_context -->
## 目标 JD 信息
**公司:** {{ company }}
**岗位:** {{ title }}
**角色类型:** {{ role_type }}
**职级/资历:** {{ seniority }}
**团队业务方向:** {{ team_direction }}

**必须技术栈（SKILLS 中至少覆盖所有 JD 必须项，且必须有正文出处）:**
{{ tech_required }}

**加分技术栈（合理选择即可，不必全部包含）:**
{{ tech_preferred }}

**OR 组（满足其一即可）:**
  - {{ or_group }}（至少满足其一）

**软性要求:**
  - {{ soft_required }}

**领域桥接提示:**
- 如果团队业务方向涉及陌生行业（例如自动驾驶、物理 AI、机器人、传感器系统、空间数据系统），请优先使用“可迁移能力”桥接：
  `infrastructure-grade pipeline patterns transferable to spatial and sensor-data systems`
  这类表达优于生造直接行业 ownership。

<!-- END_ATOM: writer_jd_context -->

<!-- END_DOMAIN: jd_context -->

---

## Output Contracts

<!-- DOMAIN: output_contracts -->

<!-- ATOM: output_contract -->
## 输出格式（header 拼写必须完全一致）

## Professional Summary
{{ data.sentences.output_header_bullet }}
{{ data.sentences.output_header_bullet }}
{{ data.sentences.output_header_bullet }}

## Skills
{{ data.sentences.output_skill_line }}
{{ data.sentences.output_skill_line }}

## Experience
{{ data.sentences.output_title_line }}
{{ data.sentences.output_dates_line }}
> Optional cross-functional note

{{ data.sentences.output_bullet }}
{{ data.sentences.output_bullet }}
{{ data.sentences.output_bullet }}
{{ data.sentences.output_bullet }}

**Project: Project Title**
> One-line project baseline (business pain point / context for what follows).
{{ data.sentences.output_bullet }}
{{ data.sentences.output_bullet }}
{{ data.sentences.output_bullet }}
{{ data.sentences.output_bullet }}

{{ data.sentences.output_title_line }}
{{ data.sentences.output_dates_line }}

{{ data.sentences.output_bullet }}

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
- 只输出简历正文，不要解释、注释、分析

<!-- END_ATOM: output_contract -->

<!-- END_DOMAIN: output_contracts -->

---

## Overlays

<!-- DOMAIN: overlays -->

<!-- ATOM: dual_channel_overlay -->
## Dual-channel continuity note
- {{delta_summary_item}}
- {{continuity_anchor_if_available}}
- Use semantic anchor as the main skeleton. Apply company continuity only when it does not reintroduce hard gaps.

<!-- END_ATOM: dual_channel_overlay -->

<!-- ATOM: planner_user -->
请作为 Planner，基于以下信息做流程决策：目标模式、目标 JD、Matcher Packet、Starter Resume。

返回 JSON，schema 必须包含 decision、fit_label、reuse_ratio_estimate、already_covered、missing_or_weak、risk_flags、role_seniority_guidance、planner_summary、writer_plan、direct_review_rationale。

规则：no_starter 模式下 decision 只能是 write；starter 高度贴合且 scope/真实性风险低时可以 direct_review；starter 语义相近但仍需改写时选择 write；starter 虽相似但会明显误导 summary、ownership、项目骨架或 scope 时选择 reject_starter；不要把 matcher 的相似度直接等同于可写作适配度。

<!-- END_ATOM: planner_user -->

<!-- ATOM: planner_writer_overlay -->
Planner-first Rules：如果给了 starter resume，把它视为可复用参考骨架，而不是必须保留的模板；优先遵循 planner 对 coverage、missing、risk、role-seniority framing 的判断；如果 planner 指出了 scope 或真实性风险，必须主动改写 summary、ownership 和项目 framing；如果 planner 认为 starter 可高比例复用，可保留高价值证据，但仍以目标 JD 为准。

<!-- END_ATOM: planner_writer_overlay -->

<!-- ATOM: planner_revision_overlay -->
Revision Rules：不要保留任何只是因为旧稿已经存在、但不再服务目标 JD 的 summary framing、ownership framing 或 bullet 结构；如果 planner 指出了 starter 的 scope、真实性、角色定位或 seniority 风险，必须优先修正；如果 reviewer 指出了 JD 缺口，优先补正文证据，而不是删除 must-have 技术；允许重写 summary、skills 分组、bullet 取舍、project baseline 和经历 framing，但不得破坏不可变字段与职业主线真实性；输出完整简历 Markdown，不要解释。

<!-- END_ATOM: planner_revision_overlay -->

<!-- END_DOMAIN: overlays -->

---

## Plan Sections

<!-- DOMAIN: plan_sections -->

<!-- ATOM: shared_intro -->
## 阶段一：PLAN（在此规划，不输出给最终用户）

请在 <PLAN> 标签内完成：

{{ data.sentences.code_fence_close }}
<PLAN>
## 技术分配规划

<!-- END_ATOM: shared_intro -->

<!-- ATOM: generic_tiktok_branch -->
### TikTok（intern，最灵活，承接 JD 核心技术）
{{ data.sentences.writer_plan_jd_tech }}
额外技术（stretch tier，叙事自洽即可）: [列出]
{{ data.sentences.writer_plan_tech_list }}

<!-- END_ATOM: generic_tiktok_branch -->

<!-- ATOM: shared_didi_temu -->
### DiDi（mid-senior acting lead，转行桥梁，连接分析和工程）
{{ data.sentences.writer_plan_jd_tech }}
额外技术（extended tier 为主）: [列出]
{{ data.sentences.writer_plan_tech_list }}

### Temu（junior DA，故事起点，分析基础）
技术（core/extended tier，体现数据分析基础）: [列出]
{{ data.sentences.writer_plan_tech_list }}

<!-- END_ATOM: shared_didi_temu -->

<!-- ATOM: shared_gt_coursework -->
### Georgia Tech CS coursework/projects（所有线路共享；ByteDance 可提升权重）
{{ data.sentences.writer_plan_jd_tech }}
{{ data.sentences.writer_plan_tech_list }}

<!-- END_ATOM: shared_gt_coursework -->

<!-- ATOM: shared_tail -->
## SKILLS 推导（= 上述经历/项目技术列表的并集）
[按 2-4 个类别优先组织；若为满足 14 词硬上限可扩到 5 类；任何类别不得少于 4 个技术]

## 项目规划
- 项目1: 属于 [哪段经历] | 主题: [业务场景]
- 项目2: 属于 [哪段经历] | 主题: [业务场景]

## 教育经历选择
[列出要保留的学历条目及理由]
</PLAN>
{{ data.sentences.code_fence_close }}

## 阶段二：RESUME

按照上方 PLAN 的规划，在 <RESUME> 标签内输出完整的 Markdown 简历：

{{ data.sentences.code_fence_close }}
<RESUME>
[完整简历内容]
</RESUME>
{{ data.sentences.code_fence_close }}

<!-- END_ATOM: shared_tail -->

<!-- END_DOMAIN: plan_sections -->

---

## Retarget Rules

<!-- DOMAIN: retarget_rules -->

<!-- ATOM: retarget_prompt -->
你正在基于一份已经通过高标准审查的 seed resume，为新的 JD 生成派生简历。

目标：尽可能少改动，在保留 seed 叙事骨架、结构质量和可信 scope 的前提下，让简历对齐目标 JD。

当前命中的 seed: {seed_label}
路由模式: retarget
目标岗位: {title} @ {company}



## Retarget 原则
1. 这是在现有 seed 上微调，不是从零重写
2. 总改动预算控制在约 35%
3. 优先保留已成熟的 summary phrasing、经历骨架、项目结构和量化风格
4. 先改 Summary、Skills、最相关经历与对应项目，再考虑其余段落
5. 所有不可变字段（公司/部门/职称/时间/地点）必须完全不变
6. 经历顺序必须保持 {experience_order}
7. 必须把 JD 必需技术写到正文里有真实使用出处，不能只堆在 SKILLS
8. 不要为了补技术而把 scope 夸大；intern/junior 一律保持 team-contributed framing
9. 若 route_mode = reuse，默认只做轻改；若 route_mode = retarget，可做中等幅度改动，但仍不得改写候选人的核心职业叙事
10. 如果目标 JD 带有行业语境（如 fintech / healthcare / security / devops），优先通过 summary 和项目业务 framing 对齐，而不是凭空新增不可信 ownership
11. 如果进入同公司一致性模式，优先复用现有 team/domain/project 骨架；把变化理解为“同项目换一种表述”，而不是“换了一套完全不同的工作内容”
12. 保留合法的 DiDi senior scope，不要把它机械压缩成 generic collaboration phrasing；是否把该 scope 提到 summary/bullet，由目标 JD 决定
13. 如果目标 JD 属于自动驾驶 / physical AI / robotics / spatial-sensor systems 等陌生行业，优先在 Summary 或项目 baseline 中写“transferable infrastructure / pipeline / reliability patterns”，不要假装已有 perception、planning、simulation 或 robotics 本体 ownership

## 目标 JD 关键信息
- Role type: {role_type}
- Seniority: {seniority}
- Must-have tech: {tech_required}
- Preferred tech: {tech_preferred}
- 当前路由识别的主要缺口: {missing_required}

<!-- END_ATOM: retarget_prompt -->

<!-- ATOM: retarget_project_pool -->
## 经验公司项目池（硬约束）
- 单篇简历最多保留 2 个项目。
- 项目只能从下面的公司主池里选，不允许发明新项目或把同一项目改写成完全不同的业务逻辑。
- 同一项目可以换强调角度，但 team / domain / scope ceiling / ownership ceiling 不可越界。

### TikTok / ByteDance
{{ data.sentences.公司池上限__2 }}
- 说明: Internship company. Keep scope explicitly team-contributed and avoid multiplying independent project universes.
- `tiktok_security_retrieval_console`
  时间: 2025-06 -> 2025-09
  团队: Security Investigation Tooling
  业务域: Security knowledge retrieval and analyst tooling
  目标: Reduce manual context gathering for policy and incident investigations through retrieval-assisted internal tooling.
  scope ceiling: Feature delivery inside a team-maintained retrieval assistant, evaluator, or analyst console; not end-to-end ownership of a standalone platform.
  ownership ceiling: Implement handlers, evaluators, ingestion utilities, replay hooks, lightweight UI surfaces, and deployment checks for a bounded intern-owned slice.
  allowed tech surface: Go, Python, Java, JavaScript, TypeScript, PostgreSQL, Kafka, gRPC, REST, Docker, Kubernetes, AWS, S3, AWS Bedrock, RAG, LLM
  allowed role lenses: backend, data, swe, mle, analyst
  {{ data.sentences.scope_note__需要_1 }}
  notes: Use for retrieval assistant, policy search, evaluation, or analyst-console variants. The business logic stays anchored in security knowledge retrieval.
- `tiktok_security_release_hardening`
  时间: 2025-10 -> 2025-12
  团队: Security Platform Release and Replay
  业务域: Security telemetry replay, release safety, and validation
  目标: Improve release confidence and replay fidelity for security event-processing and retrieval-adjacent services.
  scope ceiling: Tooling and reliability work around existing services, replay sandboxes, CI gates, and device/parser validation; not ownership of the core product roadmap.
  ownership ceiling: Implement parsers, replay fixtures, CI/CD gates, deployment automation, Linux validation harnesses, and bounded reliability fixes with teammate guidance.
  allowed tech surface: Go, Python, Java, C++, Linux, Kafka, PostgreSQL, Docker, Kubernetes, GitHub Actions, CI/CD, Model Deployment, Network Protocol, Embedded
  allowed role lenses: backend, platform, swe, data
  {{ data.sentences.scope_note__需要_1 }}
  notes: Use for replay sandbox, release hardening, device-feed validation, or regression-gating variants without changing the underlying security-platform context.

### DiDi Food
- 公司池上限: 4
- 说明: Longer tenure allows multiple sequential projects, but their time windows must not overlap or read like unrelated parallel careers.
- `didi_merchant_incident_workbench`
  时间: 2022-09 -> 2023-03
  团队: Merchant Support and Exception Operations
  业务域: Merchant incident triage, support routing, and exception handling
  目标: Replace spreadsheet-heavy merchant support workflows with auditable services and operator tooling.
  scope ceiling: Cross-functional delivery of internal support tooling, routing APIs, and dashboards used by regional operations; not sole ownership of the full merchant platform.
  ownership ceiling: Translate analyst requirements, build validation scripts and service slices, coordinate release checks, and ship operator-facing views with backend/frontend partners.
  allowed tech surface: Java, Python, Flask, REST, SQL, MySQL, Redis, Kafka, Airflow, Docker, React, TypeScript, Jira
  allowed role lenses: analyst, backend, fullstack, pm, swe
  {{ data.sentences.scope_note__通常不需要_1 }}
  notes: Use for merchant incident console, exception workbench, refund-resolution workflow, or issue-routing variants.
- `didi_pricing_rules_migration`
  时间: 2023-04 -> 2023-09
  团队: Pricing and Promotion Infrastructure
  业务域: Pricing, dispatch rules, and promotion eligibility services
  目标: Move frequently changed pricing and dispatch logic from analyst-managed processes into release-managed backend services.
  scope ceiling: Service migration, rule validation, release-readiness checks, and ops tooling for pricing/dispatch workflows; not ownership of company-wide pricing strategy.
  ownership ceiling: Build backfills, rule validators, microservice modules, data parity checks, and rollout coordination with backend and ops partners.
  allowed tech surface: Java, Python, SQL, MySQL, Redis, Kafka, Airflow, REST, Microservices, Docker, Git, Jira
  {{ data.sentences.allowed_role_lenses__analyst__backend__data__pm__s }}
  {{ data.sentences.scope_note__通常不需要_1 }}
  notes: Use for merchant offer rules, pricing rules migration, dispatch rules service, or rule-evaluation service variants.
- `didi_supply_eta_service`
  时间: 2023-10 -> 2024-02
  团队: Supply Planning and Dispatch Analytics
  业务域: Courier ETA, supply-demand planning, and anomaly monitoring
  目标: Improve city-level planning speed and operational visibility through reusable ETA and supply monitoring services.
  scope ceiling: Internal feature services and planning workflows for ops teams, backed by ETL and event-driven updates; not a standalone customer-facing product.
  ownership ceiling: Build feature pipelines, anomaly checks, service adapters, cached reads, and planning diagnostics with partner engineering teams.
  allowed tech surface: Java, Python, SQL, MySQL, Redis, Kafka, Airflow, REST, Flask, Docker, ETL
  {{ data.sentences.allowed_role_lenses__analyst__backend__data__pm__s }}
  {{ data.sentences.scope_note__通常不需要_1 }}
  notes: Use for courier ETA feature service, capacity planning service, merchant supply exception monitoring, or outage diagnostics.
- `didi_campaign_ops_console`
  时间: 2024-03 -> 2024-05
  团队: Promotion Operations and Experimentation
  业务域: Campaign launch tooling, experimentation, and promotion audits
  目标: Give operators a shared console to configure, launch, and audit promotion campaigns with fewer errors.
  scope ceiling: Internal launch-console and experimentation workflows tied to existing backend services and data refresh jobs; not ownership of company-wide growth product strategy.
  ownership ceiling: Build validation logic, console flows, sync jobs, audit tables, and release coordination with product/frontend/backend partners.
  allowed tech surface: Java, Python, TypeScript, JavaScript, Flask, REST, SQL, Redis, Kafka, Airflow, ETL, Docker
  allowed role lenses: analyst, fullstack, pm, backend, swe
  {{ data.sentences.scope_note__通常不需要_1 }}
  notes: Use for campaign operations console, regional promotion console, or experiment-setup workflow variants.

### Temu R&D
{{ data.sentences.公司池上限__2 }}
- 说明: Shorter tenure. Keep Temu scoped to analytics and experimentation support rather than turning it into a large standalone engineering program.
- `temu_checkout_funnel_diagnostics`
  时间: 2021-06 -> 2021-10
  团队: Growth and Funnel Analytics
  业务域: Checkout funnel, assortment, and conversion diagnostics
  目标: Identify conversion friction and prioritize product fixes through repeatable diagnostics and experiment readouts.
  scope ceiling: Analytics workflows, readouts, and lightweight modeling for product and R&D reviews; not ownership of the core product roadmap.
  ownership ceiling: Build SQL/Hive/Spark analyses, notebooks, and experiment slices that inform product decisions and monitoring.
  allowed tech surface: SQL, Hive, Spark SQL, Python, Pandas, A/B Testing, scikit-learn
  {{ data.sentences.allowed_role_lenses__analyst__data__pm_1 }}
  {{ data.sentences.scope_note__通常不需要_1 }}
  notes: Use for checkout funnel, conversion diagnostics, retention slices, or experiment-readout variants.
- `temu_promo_reporting_automation`
  时间: 2021-11 -> 2022-02
  团队: Merchant and Promotion Analytics
  业务域: Merchant reporting, promotion monitoring, and recurring analytics automation
  目标: Reduce repetitive reporting and improve visibility for merchant performance and promotion operations.
  scope ceiling: Recurring analytics automation, anomaly checks, and lightweight modeling; not full-stack product development.
  ownership ceiling: Automate reports, reconcile datasets, build monitoring tables, and provide decision support for experiments and merchant reviews.
  allowed tech surface: Python, Pandas, SQL, Hive, Spark SQL, Airflow, A/B Testing, scikit-learn
  {{ data.sentences.allowed_role_lenses__analyst__data__pm_1 }}
  {{ data.sentences.scope_note__通常不需要_1 }}
  notes: Use for reporting automation, merchant quality reviews, promotion monitoring, or cohort-analysis variants.

<!-- END_ATOM: retarget_project_pool -->

<!-- ATOM: retarget_same_company -->
## 同公司一致性模式（最高优先级）
- 当前目标岗位与 seed 同属 **ExampleCorp**
{{ data.sentences.这是该公司的公司内锚点_seed }}
{{ data.sentences.seed_来源岗位__已登记公司内来源 }}
- 把公司内的 team / domain / 项目池视为“准不可变骨架”，不要写成完全不同的人做了完全不同的事
- 允许调整的只有：Summary 侧重点、Skills 少量技术取舍、同一项目的不同强调角度、少量 bullet 技术细节
- 不允许把业务方向改成明显不同的另一条线，不允许引入与现有公司版本完全无关的新项目池
- 同一公司家族下，全部版本合计最多保留 4 个项目；TikTok/Bytedance 实习项目最多 2 个
- 写法目标是：读者能自然感觉“同一个人在讲同一批经历，只是针对不同岗位换了强调方式”

<!-- END_ATOM: retarget_same_company -->

<!-- ATOM: retarget_same_company_bytedance -->
## ByteDance seed 参考模式（覆盖同公司微调规则）
- 当前目标岗位命中了 ByteDance 同公司 seed，但该 seed 只能作为弱参考
{{ data.sentences.这是该公司的公司内锚点_seed }}
{{ data.sentences.seed_来源岗位__已登记公司内来源 }}
- 不得继承 seed 中的 TikTok / ByteDance intern 叙事骨架、项目或 bullet
- 只允许借用 seed 中仍然适用于 DiDi、Temu、Georgia Tech CS coursework/projects 的技术 framing
- 任何与 TikTok / ByteDance intern 绑定的内容都必须删掉，再重写成新的两段全职经历 + GT CS 项目版本

<!-- END_ATOM: retarget_same_company_bytedance -->

<!-- END_DOMAIN: retarget_rules -->

---

## Reviewer Rules

<!-- DOMAIN: reviewer_rules -->

<!-- ATOM: reviewer_user -->
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

<!-- END_ATOM: reviewer_user -->

<!-- ATOM: reviewer_output_schema -->
## 输出格式

请严格按以下 JSON 格式输出（不要有任何额外文字）：

{{ data.sentences.json }}
{
  "scores": {
    "r0_authenticity": {
      {{ data.sentences.score____0_10_1 }}
      {{ data.sentences.weight___0_20_1 }}
      {{ data.sentences.verdict_____pass_fail_1 }}
      "findings": [
        {"severity": "<critical|high|medium|low>", "field": "<具体位置>", "issue": "<问题描述>", "fix": "<具体修改建议>"}
      ]
    {{ data.sentences.empty }}
    "r1_writing_standard": {
      {{ data.sentences.score____0_10_1 }}
      "weight": 0.15,
      {{ data.sentences.verdict_____pass_fail_1 }}
      {{ data.sentences.findings_1 }}
    {{ data.sentences.empty }}
    "r2_jd_fitness": {
      {{ data.sentences.score____0_10_1 }}
      {{ data.sentences.weight___0_20_1 }}
      {{ data.sentences.verdict_____pass_fail_1 }}
      {{ data.sentences.findings_1 }}
    {{ data.sentences.empty }}
    "r3_overqualification": {
      {{ data.sentences.score____0_10_1 }}
      {{ data.sentences.weight___0_10_1 }}
      {{ data.sentences.verdict_____pass_fail_1 }}
      {{ data.sentences.findings_1 }}
    {{ data.sentences.empty }}
    "r4_rationality": {
      {{ data.sentences.score____0_10_1 }}
      {{ data.sentences.weight___0_20_1 }}
      {{ data.sentences.verdict_____pass_fail_1 }}
      {{ data.sentences.findings_1 }}
    {{ data.sentences.empty }}
    "r5_logic": {
      {{ data.sentences.score____0_10_1 }}
      {{ data.sentences.weight___0_10_1 }}
      {{ data.sentences.verdict_____pass_fail_1 }}
      {{ data.sentences.findings_1 }}
    {{ data.sentences.empty }}
    "r6_competitiveness": {
      {{ data.sentences.score____0_10_1 }}
      "weight": 0.05,
      {{ data.sentences.verdict_____pass_fail_1 }}
      {{ data.sentences.findings_1 }}
    {{ data.sentences.empty_1 }}
  {{ data.sentences.empty }}
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
{{ data.sentences.empty_1 }}
{{ data.sentences.code_fence_close }}

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

只输出 JSON，不要其他内容。
<!-- END_ATOM: reviewer_output_schema -->

<!-- END_DOMAIN: reviewer_rules -->

---

## System Prompts

<!-- DOMAIN: system_prompts -->

<!-- ATOM: writer_system -->
你是一位专业简历撰写专家，为一家职业转型培训公司制作教学示例简历。
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
<!-- END_ATOM: writer_system -->

<!-- ATOM: strict_revision_system -->
你是专业简历修改专家。严格按照修改指令执行，只改指出的问题，不做额外改动。直接输出修改后的完整简历 Markdown，不要附带解释。
<!-- END_ATOM: strict_revision_system -->

<!-- ATOM: upgrade_revision_system -->
你是专业简历升级专家。你可以在保持不可变字段、真实性边界和核心职业叙事不变的前提下，重写 summary、skills、experience bullets、project baseline 和项目 framing，以显著提升 JD 匹配度、scope 表达完整度和整体得分。不要被 seed phrasing、旧 summary 或旧 bullet 选择束缚；如果旧稿的 framing 本身导致失分，应主动替换成更强、更清晰、但仍真实自洽的表达。直接输出修改后的完整简历 Markdown，不要附带解释。
<!-- END_ATOM: upgrade_revision_system -->

<!-- ATOM: reviewer_system -->
你是一位严格的简历质量审查专家，负责对简历进行 9 个维度的综合评分。
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
<!-- END_ATOM: reviewer_system -->

<!-- ATOM: planner_system -->
你是简历流程里的 Planner。你的职责不是直接写简历，而是基于 JD、matcher 证据和可选历史简历 starter，判断：这份 starter 是否适合作为起点；是否可以直接送 Reviewer；如果需要写作，哪些内容已覆盖、哪些缺失、哪些存在真实性/ownership/scope 风险；Writer 应如何改写，优先级如何排序。

必须输出 JSON，不要输出解释性文字。不要复述 schema。
<!-- END_ATOM: planner_system -->

<!-- END_DOMAIN: system_prompts -->

---

## Upgrade Rules

<!-- DOMAIN: upgrade_rules -->

<!-- ATOM: upgrade_prompt -->
请把下面这份历史简历做一次面向目标 JD 的升级式重写，而不是仅做字面修补。

目标岗位: {jd_title}
当前评分: 91.5/100
历史来源: route_mode={route_mode} | seed_label={seed_label}

## 升级目标
1. 提高 JD 匹配度、summary 信号密度、scope 叙事完整度和整体逻辑自洽
2. 修复 reviewer 指出的所有问题，尤其是 summary、skills、DiDi scope 与 seniority signal
3. 若当前版本对 senior 价值表达偏弱，可以重写 summary、Skills、DiDi bullets、项目 framing
4. 允许中等幅度重写，但不得改动不可变字段，不得破坏既有职业故事主线

## 最优先修改事项
  1. {priority}

## 审查发现
[r0] [HIGH] {field}: {issue} → 修改建议: {fix}

## 必须技术
{tech_required}




## 关键升级规则
1. Summary 必须重新评估，不要默认沿用旧 phrasing；三句都要服务目标 JD
2. 如果 DiDi 的 senior operating scope 能显著增强匹配度，可以把该信号提炼进 summary，但要简洁，不要和 bullet 机械重复
3. 如果目标 JD 带有陌生行业语境，优先补一条“领域桥接”语句，说明现有平台/数据/可靠性模式如何迁移到该行业
3. DiDi scope note 若保留，统一写成：
   {{ data.sentences.didi_scope_note }}
4. 如果目标岗位需要更强 senior / stakeholder / cross-functional signal，可以在 DiDi bullets 中使用这句：
     {{ data.sentences.represented_the_headquarters_data_organization_in }}
5. 上面这条 DiDi bullet 只在它确实提升目标岗位匹配度时使用；不要为了“显得大”而强塞
6. Skills 既要满足格式硬约束，也要确保没有遗漏正文/JD 的关键技术；不要靠暴力删减过关
7. 对 JD must-have 技术，只能补正文证据、扩写项目或重写相关 bullet，不能删除
8. 围棋 summary 句必须是高价值认知信号，不要写成 collaboration/teamwork 论据
9. 保留所有不可变字段（公司/部门/职称/时间/地点）完全不变
10. 经历顺序必须保持 {experience_order}
11. 输出必须仍然满足全部格式硬约束
12. 如果 seed phrasing、旧 summary、旧 bullet 选择本身就是失分原因，可以直接替换，不要为了“保留 seed”而保留弱表达
13. rewrite 的目标是通过，而不是尽量少改；只要真实且自洽，可以换掉低质量旧表述

## 原审查详细修改指令
{revision_instructions}

<!-- END_ATOM: upgrade_prompt -->

<!-- END_DOMAIN: upgrade_rules -->

---
