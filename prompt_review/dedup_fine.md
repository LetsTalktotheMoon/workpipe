# 细粒度去重 Prompt 编辑文档

**统计**: 80 共享块 + 439 唯一片段。
**重叠检查**: shared-shared=28, shared-unique=13, unique-unique=0。

> **编辑规范**: 请勿删除 `<!-- UID: ... -->` 注释。修改文本后，我可以按 UID 映射回原始 JSON。

---

# 共享块

<!-- UID: shared-1085c0a5fbcff841 -->
<!-- 24 处: runtime_main::generate::writer::standard_writer::examplecorp::output_contract, runtime_main::upgrade_revision::writer::standard_upgrade::examplecorp::output_contract, runtime_seed_retarget::rewrite_writer::writer::standard_upgrade::examplecorp::output_contract, runtime_main::generate::writer::bytedance::standard_writer::bytedance::output_contract... -->
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


---

<!-- UID: shared-c907719aaef5677c -->
<!-- 24 处: runtime_main::generate::writer::standard_writer::examplecorp::output_contract, runtime_main::upgrade_revision::writer::standard_upgrade::examplecorp::output_contract, runtime_seed_retarget::rewrite_writer::writer::standard_upgrade::examplecorp::output_contract, runtime_main::generate::writer::bytedance::standard_writer::bytedance::output_contract... -->
* **Header:** Sentence.
* **Header:** Sentence.
* **Header:** Sentence.


---

<!-- UID: shared-461f67b6eca23454 -->
<!-- 24 处: runtime_main::generate::writer::standard_writer::examplecorp::output_contract, runtime_main::upgrade_revision::writer::standard_upgrade::examplecorp::output_contract, runtime_seed_retarget::rewrite_writer::writer::standard_upgrade::examplecorp::output_contract, runtime_main::generate::writer::bytedance::standard_writer::bytedance::output_contract... -->
*Dates | Location*

* Bullet.


---

<!-- UID: shared-7a32ccd4e8096d3e -->
<!-- 24 处: runtime_main::generate::writer::standard_writer::examplecorp::output_contract, runtime_main::upgrade_revision::writer::standard_upgrade::examplecorp::output_contract, runtime_seed_retarget::rewrite_writer::writer::standard_upgrade::examplecorp::output_contract, runtime_main::generate::writer::bytedance::standard_writer::bytedance::output_contract... -->
* **Category:** skill1, skill2, skill3
* **Category:** skill1, skill2, skill3


---

<!-- UID: shared-f2fb0f2f3e9d1ed7 -->
<!-- 18 处: runtime_main::generate::writer::standard_writer::examplecorp::format_constraints, runtime_main::generate::writer::bytedance::standard_writer::bytedance::format_constraints, match_pipe::no_starter::writer::format_constraints_shared_head, match_pipe::no_starter::writer::bytedance::format_constraints_shared_head... -->

**结构规则**
- Summary: 恰好 3 句，每句格式：`* **角色定位短语:** 叙述句。`

---

<!-- UID: shared-80715052e871e54a -->
<!-- 16 处: source_reference::doc::match_pipe_prompt_review::source_reference::doc::match_pipe_prompt_review::document, source_reference::doc::match_pipe_prompt_review::source_reference::doc::match_pipe_prompt_review::document, source_reference::doc::match_pipe_prompt_review::source_reference::doc::match_pipe_prompt_review::document, source_reference::doc::match_pipe_prompt_review::source_reference::doc::match_pipe_prompt_review::document... -->

正文：

第 1 段  

---

<!-- UID: shared-47de231a1d2a4b85 -->
<!-- 10 处: source_reference::design_guide::task_general_prompt::source_reference::design_guide::task_general_prompt::document, source_reference::design_guide::task_general_prompt::source_reference::design_guide::task_general_prompt::document, source_reference::design_guide::task_general_prompt::source_reference::design_guide::task_general_prompt::document, source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document... -->

例如：


---

<!-- UID: shared-42cdd36f6e360284 -->
<!-- 9 处: match_pipe::old_match_anchor::writer::retarget_project_pool, match_pipe::old_match_anchor::writer::bytedance::retarget_project_pool, match_pipe::old_match_anchor::writer::same_company::retarget_project_pool, match_pipe::old_match_anchor::writer::bytedance::same_company::retarget_project_pool... -->
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
  scope note: 通常不需要
  notes: Use for merchant incident console, exception workbench, refund-resolution workflow, or issue-routing variants.
- `didi_pricing_rules_migration`
  时间: 2023-04 -> 2023-09
  团队: Pricing and Promotion Infrastructure
  业务域: Pricing, dispatch rules, and promotion eligibility services
  目标: Move frequently changed pricing and dispatch logic from analyst-managed processes into release-managed backend services.
  scope ceiling: Service migration, rule validation, release-readiness checks, and ops tooling for pricing/dispatch workflows; not ownership of company-wide pricing strategy.
  ownership ceiling: Build backfills, rule validators, microservice modules, data parity checks, and rollout coordination with backend and ops partners.
  allowed tech surface: Java, Python, SQL, MySQL, Redis, Kafka, Airflow, REST, Microservices, Docker, Git, Jira
  allowed role lenses: analyst, backend, data, pm, swe
  scope note: 通常不需要
  notes: Use for merchant offer rules, pricing rules migration, dispatch rules service, or rule-evaluation service variants.
- `didi_supply_eta_service`
  时间: 2023-10 -> 2024-02
  团队: Supply Planning and Dispatch Analytics
  业务域: Courier ETA, supply-demand planning, and anomaly monitoring
  目标: Improve city-level planning speed and operational visibility through reusable ETA and supply monitoring services.
  scope ceiling: Internal feature services and planning workflows for ops teams, backed by ETL and event-driven updates; not a standalone customer-facing product.
  ownership ceiling: Build feature pipelines, anomaly checks, service adapters, cached reads, and planning diagnostics with partner engineering teams.
  allowed tech surface: Java, Python, SQL, MySQL, Redis, Kafka, Airflow, REST, Flask, Docker, ETL
  allowed role lenses: analyst, backend, data, pm, swe
  scope note: 通常不需要
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
  scope note: 通常不需要
  notes: Use for campaign operations console, regional promotion console, or experiment-setup workflow variants.


---

<!-- UID: shared-2c5e4a740e6e7bca -->
<!-- 9 处: match_pipe::old_match_anchor::writer::retarget_project_pool, match_pipe::old_match_anchor::writer::bytedance::retarget_project_pool, match_pipe::old_match_anchor::writer::same_company::retarget_project_pool, match_pipe::old_match_anchor::writer::bytedance::same_company::retarget_project_pool... -->
- 公司池上限: 2
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
  scope note: 需要
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
  scope note: 需要
  notes: Use for replay sandbox, release hardening, device-feed validation, or regression-gating variants without changing the underlying security-platform context.


---

<!-- UID: shared-12bbcdd65ae43bf8 -->
<!-- 9 处: match_pipe::old_match_anchor::writer::retarget_project_pool, match_pipe::old_match_anchor::writer::bytedance::retarget_project_pool, match_pipe::old_match_anchor::writer::same_company::retarget_project_pool, match_pipe::old_match_anchor::writer::bytedance::same_company::retarget_project_pool... -->
- 公司池上限: 2
- 说明: Shorter tenure. Keep Temu scoped to analytics and experimentation support rather than turning it into a large standalone engineering program.
- `temu_checkout_funnel_diagnostics`
  时间: 2021-06 -> 2021-10
  团队: Growth and Funnel Analytics
  业务域: Checkout funnel, assortment, and conversion diagnostics
  目标: Identify conversion friction and prioritize product fixes through repeatable diagnostics and experiment readouts.
  scope ceiling: Analytics workflows, readouts, and lightweight modeling for product and R&D reviews; not ownership of the core product roadmap.
  ownership ceiling: Build SQL/Hive/Spark analyses, notebooks, and experiment slices that inform product decisions and monitoring.
  allowed tech surface: SQL, Hive, Spark SQL, Python, Pandas, A/B Testing, scikit-learn
  allowed role lenses: analyst, data, pm
  scope note: 通常不需要
  notes: Use for checkout funnel, conversion diagnostics, retention slices, or experiment-readout variants.
- `temu_promo_reporting_automation`
  时间: 2021-11 -> 2022-02
  团队: Merchant and Promotion Analytics
  业务域: Merchant reporting, promotion monitoring, and recurring analytics automation
  目标: Reduce repetitive reporting and improve visibility for merchant performance and promotion operations.
  scope ceiling: Recurring analytics automation, anomaly checks, and lightweight modeling; not full-stack product development.
  ownership ceiling: Automate reports, reconcile datasets, build monitoring tables, and provide decision support for experiments and merchant reviews.
  allowed tech surface: Python, Pandas, SQL, Hive, Spark SQL, Airflow, A/B Testing, scikit-learn
  allowed role lenses: analyst, data, pm
  scope note: 通常不需要
  notes: Use for reporting automation, merchant quality reviews, promotion monitoring, or cohort-analysis variants.

---

<!-- UID: shared-85b12c5857dbfe08 -->
<!-- 9 处: match_pipe::old_match_anchor::writer::retarget_project_pool, match_pipe::old_match_anchor::writer::bytedance::retarget_project_pool, match_pipe::old_match_anchor::writer::same_company::retarget_project_pool, match_pipe::old_match_anchor::writer::bytedance::same_company::retarget_project_pool... -->
- 单篇简历最多保留 2 个项目。
- 项目只能从下面的公司主池里选，不允许发明新项目或把同一项目改写成完全不同的业务逻辑。
- 同一项目可以换强调角度，但 team / domain / scope ceiling / ownership ceiling 不可越界。


---

<!-- UID: shared-786b4b11beba3239 -->
<!-- 11 处: runtime_main::full_review::reviewer::standard_reviewer::examplecorp::full::schema, runtime_seed_retarget::rewrite_review::reviewer::standard_reviewer::examplecorp::rewrite::schema, runtime_main::full_review::reviewer::bytedance::standard_reviewer::bytedance::full::schema, runtime_seed_retarget::rewrite_review::reviewer::bytedance::standard_reviewer::bytedance::rewrite::schema... -->

请严格按以下 JSON 格式输出（不要有任何额外文字）：

```json
{
  "scores": {
    "r0_authenticity": {
      "score": <0-10>,
      "weight": 0.20,
      "verdict": "<pass|fail>",
      "findings": [
        {"severity": "<critical|high|medium|low>", "field": "<具体位置>", "issue": "<问题描述>", "fix": "<具体修改建议>"}
      ]
    },
    "r1_writing_standard": {
      "score": <0-10>,
      "weight": 0.15,
      "verdict": "<pass|fail>",
      "findings": []
    },
    "r2_jd_fitness": {
      "score": <0-10>,
      "weight": 0.20,
      "verdict": "<pass|fail>",
      "findings": []
    },
    "r3_overqualification": {
      "score": <0-10>,
      "weight": 0.10,
      "verdict": "<pass|fail>",
      "findings": []
    },
    "r4_rationality": {
      "score": <0-10>,
      "weight": 0.20,
      "verdict": "<pass|fail>",
      "findings": []
    },
    "r5_logic": {
      "score": <0-10>,
      "weight": 0.10,
      "verdict": "<pass|fail>",
      "findings": []
    },
    "r6_competitiveness": {
      "score": <0-10>,
      "weight": 0.05,
      "verdict": "<pass|fail>",
      "findings": []
    }
  },
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
}
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

只输出 JSON，不要其他内容。

---

<!-- UID: shared-0fc1533461c59c39 -->
<!-- 8 处: runtime_main::full_review::reviewer::standard_reviewer::examplecorp::full::system, runtime_seed_retarget::rewrite_review::reviewer::standard_reviewer::examplecorp::rewrite::system, runtime_main::full_review::reviewer::bytedance::standard_reviewer::bytedance::full::system, runtime_seed_retarget::rewrite_review::reviewer::bytedance::standard_reviewer::bytedance::rewrite::system... -->
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

---

<!-- UID: shared-0cb5c5994d5a7bc2 -->
<!-- 8 处: match_pipe::old_match_anchor::writer::retarget_prompt, match_pipe::old_match_anchor::writer::bytedance::retarget_prompt, match_pipe::old_match_anchor::writer::same_company::retarget_prompt, match_pipe::old_match_anchor::writer::bytedance::same_company::retarget_prompt... -->
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


---

<!-- UID: shared-a121260e437858f7 -->
<!-- 8 处: match_pipe::no_starter::writer::format_constraints_branch, match_pipe::old_match_anchor::writer::format_constraints_branch, match_pipe::old_match_anchor::writer::same_company::format_constraints_branch, match_pipe::new_dual_channel::writer::format_constraints_branch... -->
- Experience 顺序: **严格倒序** — TikTok（2025）→ DiDi（2022-2024）→ Temu（2021-2022）
**不可变字段（绝不可修改）**
- TikTok: Software Engineer Intern | TikTok · Security · Backend Infra | Jun 2025 – Dec 2025 | San Jose, USA
- DiDi: Senior Data Analyst | DiDi · IBG · Food | Sep 2022 – May 2024 | Beijing/Mexico
- Temu: Data Engineer | Temu · R&D · Recommendation Algorithms| Jun 2021 – Feb 2022 | Shanghai

**职级 Scope 规则**
- TikTok (intern, 6个月): 禁用 Led/Architected/Drove/Spearheaded/Managed；体现个人贡献，不主张架构决策
  → bullet 数量建议 **4-5 条**（6个月实习期内独立成就不超过 5 条，超出则可信度下降）
- DiDi (mid-senior acting lead): 可用 Led/Coordinated/Drove；可展示 13 人跨职能团队领导力
- DiDi 的全球汇报/管理层传导 scope 不要塞进 scope note；如目标岗位重视 senior stakeholder scope，可用单独 bullet 表达：
  `Represented the headquarters data organization in biweekly global operating reviews, and translated performance signals into two-week recommendations adopted by management and LATAM frontline teams.`
- Temu (junior): 禁用 Led/Architected/Drove/Spearheaded；仅体现 individual contributor 贡献

---

<!-- UID: shared-13538cb570413f56 -->
<!-- 8 处: match_pipe::no_starter::writer::bytedance::format_constraints_branch_bytedance, match_pipe::old_match_anchor::writer::bytedance::format_constraints_branch_bytedance, match_pipe::old_match_anchor::writer::bytedance::same_company::format_constraints_branch_bytedance, match_pipe::new_dual_channel::writer::bytedance::format_constraints_branch_bytedance... -->
- Experience 顺序: **严格倒序** — DiDi（2022-2024）→ Temu（2021-2022）
**不可变字段（绝不可修改）**
- DiDi: Senior Data Analyst | DiDi · IBG · Food | Sep 2022 – May 2024 | Beijing/Mexico
- Temu: Data Engineer | Temu · R&D · Recommendation Algorithms | Jun 2021 – Feb 2022 | Shanghai
- TikTok / ByteDance intern experience must be absent for ByteDance target roles.

**职级 Scope 规则**
- ByteDance 目标岗位: 不允许出现 TikTok / ByteDance intern；需要更多 SWE 证据时，优先写 Georgia Tech CS coursework/projects，而不是回填该实习。
- DiDi (mid-senior acting lead): 可用 Led/Coordinated/Drove；可展示 13 人跨职能团队领导力
- DiDi 的全球汇报/管理层传导 scope 不要塞进 scope note；如目标岗位重视 senior stakeholder scope，可用单独 bullet 表达：
  `Represented the headquarters data organization in biweekly global operating reviews, and translated performance signals into two-week recommendations adopted by management and LATAM frontline teams.`
- Temu (junior): 禁用 Led/Architected/Drove/Spearheaded；仅体现 individual contributor 贡献

---

<!-- UID: shared-e2ee22e3bc7408df -->
<!-- 8 处: match_pipe::old_match_anchor::writer::retarget_prompt, match_pipe::old_match_anchor::writer::bytedance::retarget_prompt, match_pipe::old_match_anchor::writer::same_company::retarget_prompt, match_pipe::old_match_anchor::writer::bytedance::same_company::retarget_prompt... -->
你正在基于一份已经通过高标准审查的 seed resume，为新的 JD 生成派生简历。

目标：尽可能少改动，在保留 seed 叙事骨架、结构质量和可信 scope 的前提下，让简历对齐目标 JD。

路由模式: retarget


---

<!-- UID: shared-0c25a43f595e8e1e -->
<!-- 8 处: match_pipe::old_match_anchor::writer::retarget_prompt, match_pipe::old_match_anchor::writer::bytedance::retarget_prompt, match_pipe::old_match_anchor::writer::same_company::retarget_prompt, match_pipe::old_match_anchor::writer::bytedance::same_company::retarget_prompt... -->
- Role type: {role_type}
- Seniority: {seniority}
- Must-have tech: {tech_required}
- Preferred tech: {tech_preferred}
- 当前路由识别的主要缺口: {missing_required}

---

<!-- UID: shared-4269a2b8c44456a2 -->
<!-- 8 处: runtime_main::generate::writer::bytedance::standard_writer::bytedance::target_specific, match_pipe::no_starter::writer::bytedance::retarget_bytedance_special, match_pipe::old_match_anchor::writer::bytedance::retarget_bytedance_special, match_pipe::old_match_anchor::writer::bytedance::same_company::retarget_bytedance_special... -->
- 对 ByteDance 目标岗位，候选人证据池中不得出现 TikTok / ByteDance intern 这段经历，也不得在 Summary、Skills、Experience、Project baseline 或 bullets 中提及它
- 只允许从以下三类材料出发构建简历：DiDi 全职经历、Temu 全职经历、Georgia Tech CS coursework/projects
- 当 JD 需要更强的软件工程或系统实现信号时，优先把 Georgia Tech CS coursework/projects 提升为主要技术证据；GT 教育主干仍是共享材料，而不是把缺口强行塞回 ByteDance/TikTok intern
- seed 若包含 TikTok / ByteDance intern，只能作为弱参考；你必须主动删掉这段经历，再按新的证据池重写

---

<!-- UID: shared-dc23fbda9d30d3ee -->
<!-- 8 处: runtime_main::generate::writer::standard_writer::examplecorp::plan_resume, runtime_main::generate::writer::bytedance::standard_writer::bytedance::plan_resume, match_pipe::no_starter::writer::writer_plan_shared_didi_temu, match_pipe::no_starter::writer::bytedance::writer_plan_shared_didi_temu... -->
必要 JD 技术（放在这里）: [列出]
额外技术（extended tier 为主）: [列出]
→ 此经历 bullet 将使用的完整技术列表: [最终列表]


---

<!-- UID: shared-905b206bc1564215 -->
<!-- 8 处: runtime_main::generate::writer::standard_writer::examplecorp::plan_resume, runtime_main::generate::writer::bytedance::standard_writer::bytedance::plan_resume, match_pipe::no_starter::writer::writer_plan_shared_tail, match_pipe::no_starter::writer::bytedance::writer_plan_shared_tail... -->
- 项目1: 属于 [哪段经历] | 主题: [业务场景]
- 项目2: 属于 [哪段经历] | 主题: [业务场景]


---

<!-- UID: shared-75ee5ec48eacfc1c -->
<!-- 7 处: runtime_main::generate::writer::standard_writer::examplecorp::candidate_context, match_pipe::no_starter::writer::candidate_context_shared_education, match_pipe::no_starter::writer::bytedance::candidate_context_shared_education, match_pipe::planner_write::writer::candidate_context_shared_education... -->
- M.S. Computer Science | Georgia Institute of Technology | Expected May 2026
  → 当 UIUC MSIM 出现时写为 M.S. Computer Science (OMSCS)；  仅出现GT时直接写 M.S. Computer Science
- M.S. Information Management (MSIM) | University of Illinois Urbana-Champaign | Expected May 2026 — 保留当: Data方向/PM方向/信息管理相关岗位 | 可省略当: 纯SWE后端且与信息管理无关
- M.S. International Business | Beijing International Studies University | Sep 2018 – Jun 2021 — 保留当: FinTech/国际业务/金融数据方向 | 可省略当: 与目标岗位完全无关且简历空间紧张
- B.A. Philosophy & Psychology | Beijing Normal University | Sep 2014 – Jun 2018 — 保留当: TechPM(认知科学角度)/NLP(语言学角度)/UX Research | 可省略当: 大多数纯技术岗位

---

<!-- UID: shared-fa65e8ec2edcf21a -->
<!-- 6 处: runtime_main::generate::writer::standard_writer::examplecorp::system, runtime_main::generate::writer::bytedance::standard_writer::bytedance::system, match_pipe::no_starter::writer::writer_system, match_pipe::no_starter::writer::bytedance::writer_system... -->
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

---

<!-- UID: shared-3826aac696c502ca -->
<!-- 8 处: runtime_main::generate::writer::standard_writer::examplecorp::jd_context, runtime_main::generate::writer::bytedance::standard_writer::bytedance::jd_context, match_pipe::no_starter::writer::writer_jd_context, match_pipe::no_starter::writer::bytedance::writer_jd_context... -->
**公司:** {company}
**岗位:** {title}
**角色类型:** {role_type}
**职级/资历:** {seniority}
**团队业务方向:** {team_direction}

**必须技术栈（SKILLS 中至少覆盖所有 JD 必须项，且必须有正文出处）:**
{tech_required}

**加分技术栈（合理选择即可，不必全部包含）:**
{tech_preferred}

**OR 组（满足其一即可）:**
  - {or_group}（至少满足其一）

**软性要求:**
  - {soft_required}

**领域桥接提示:**
- 如果团队业务方向涉及陌生行业（例如自动驾驶、物理 AI、机器人、传感器系统、空间数据系统），请优先使用“可迁移能力”桥接：
  `infrastructure-grade pipeline patterns transferable to spatial and sensor-data systems`
  这类表达优于生造直接行业 ownership。

---

<!-- UID: shared-91d55fb843bd4e3c -->
<!-- 6 处: match_pipe::no_starter::writer::candidate_context_shared_experience, match_pipe::no_starter::writer::bytedance::candidate_context_shared_experience, match_pipe::planner_write::writer::candidate_context_shared_experience, match_pipe::planner_write::writer::bytedance::candidate_context_shared_experience... -->
- ⚡公司: DiDi | ⚡部门: IBG · Food | ⚡职称: Senior Data Analyst
- ⚡时间: Sep 2022 – May 2024 | ⚡地点: Beijing/Mexico
- 时长: 20个月 | 级别: mid_senior
- 允许动词: Led, Coordinated, Represented, Drove
- Scope: data lead within a 13-person cross-functional squad; may represent the headquarters data organization in biweekly global operating reviews, with recommendations adopted by management and LATAM frontline teams，强业务型
- 领导力: 13人跨职能团队acting lead（前端, 后端, 全栈, 移动端, PM 等）
- 全球汇报: 每两周全球会议代表北京数据中台总部发言
- 决策传导: 数据决策直接进入管理层和一线
- 自然技术栈 core（几乎必然使用）: ETL, Flask, Kafka, Python, REST, SQL
- 自然技术栈 extended（合理推断可能接触）: Airflow, Docker, Java, MySQL, Pandas, React, Redis
- 自然技术栈 stretch（特定场景可能接触，需叙事支撑）: Go, Kubernetes, Microservices, MongoDB, TypeScript, gRPC...

---

<!-- UID: shared-73076ded99cca657 -->
<!-- 6 处: match_pipe::no_starter::writer::candidate_context_shared_experience, match_pipe::no_starter::writer::bytedance::candidate_context_shared_experience, match_pipe::planner_write::writer::candidate_context_shared_experience, match_pipe::planner_write::writer::bytedance::candidate_context_shared_experience... -->
- ⚡公司: Temu | ⚡部门: R&D · Recommendation Algorithms | ⚡职称: Data Engineer
- ⚡时间: Jun 2021 – Feb 2022 | ⚡地点: Shanghai
- 时长: 8个月 | 级别: junior
- 禁用动词: Led, Architected, Drove, Spearheaded, Directed
- Scope: individual contributor, 8个月短期经历，硬核研究型
- 自然技术栈 core（几乎必然使用）: Hive, Pandas, Python, SQL, Spark SQL
- 自然技术栈 extended（合理推断可能接触）: A/B Testing, Airflow, Jupyter, Matplotlib, NumPy, scikit-learn
- 自然技术栈 stretch（特定场景可能接触，需叙事支撑）: ETL, Flask, HiveQL, Kafka, Redis...


---

<!-- UID: shared-bc34fd64f1d6c60b -->
<!-- 6 处: match_pipe::no_starter::writer::writer_plan_shared_tail, match_pipe::no_starter::writer::bytedance::writer_plan_shared_tail, match_pipe::planner_write::writer::writer_plan_shared_tail, match_pipe::planner_write::writer::bytedance::writer_plan_shared_tail... -->

按照上方 PLAN 的规划，在 <RESUME> 标签内输出完整的 Markdown 简历：

<RESUME>
[完整简历内容]
</RESUME>

---

<!-- UID: shared-009eb6cb071a2ec2 -->
<!-- 6 处: runtime_main::upgrade_revision::writer::standard_upgrade::examplecorp::main, runtime_seed_retarget::rewrite_writer::writer::standard_upgrade::examplecorp::main, runtime_main::upgrade_revision::writer::bytedance::standard_upgrade::bytedance::main, runtime_seed_retarget::rewrite_writer::writer::bytedance::standard_upgrade::bytedance::main... -->
1. 提高 JD 匹配度、summary 信号密度、scope 叙事完整度和整体逻辑自洽
2. 修复 reviewer 指出的所有问题，尤其是 summary、skills、DiDi scope 与 seniority signal
3. 若当前版本对 senior 价值表达偏弱，可以重写 summary、Skills、DiDi bullets、项目 framing
4. 允许中等幅度重写，但不得改动不可变字段，不得破坏既有职业故事主线


---

<!-- UID: shared-a1a0e45244671f52 -->
<!-- 6 处: match_pipe::no_starter::writer::writer_plan_shared_intro, match_pipe::no_starter::writer::bytedance::writer_plan_shared_intro, match_pipe::planner_write::writer::writer_plan_shared_intro, match_pipe::planner_write::writer::bytedance::writer_plan_shared_intro... -->

请在 <PLAN> 标签内完成：

<PLAN>

---

<!-- UID: shared-434966972c44f554 -->
<!-- 4 处: match_pipe::reviewer::full::reviewer_context, match_pipe::reviewer::full::bytedance::reviewer_context, match_pipe::planner_direct_review::reviewer::reviewer_context, match_pipe::planner_direct_review::reviewer::bytedance::reviewer_context -->

公司: {company} | 岗位: {title} | 角色类型: {role_type} | 职级: {seniority}
必须技术栈: {tech_required}
加分技术栈: {tech_preferred}
团队方向: {team_direction}

不可变字段（必须与此完全一致）:
{immutable_block}

---

<!-- UID: shared-6c8005e7f09c0934 -->
<!-- 4 处: runtime_main::upgrade_revision::writer::standard_upgrade::examplecorp::main, runtime_seed_retarget::rewrite_writer::writer::standard_upgrade::examplecorp::main, runtime_main::upgrade_revision::writer::bytedance::standard_upgrade::bytedance::main, runtime_seed_retarget::rewrite_writer::writer::bytedance::standard_upgrade::bytedance::main -->
请把下面这份历史简历做一次面向目标 JD 的升级式重写，而不是仅做字面修补。

目标岗位: {jd_title}
当前评分: 91.5/100
历史来源: route_mode={route_mode} | seed_label={seed_label}


---

<!-- UID: shared-cb15291a75b993ab -->
<!-- 4 处: source_reference::doc::match_pipe_prompt_review::source_reference::doc::match_pipe_prompt_review::document, source_reference::doc::match_pipe_prompt_review::source_reference::doc::match_pipe_prompt_review::document, source_reference::doc::match_pipe_prompt_review::source_reference::doc::match_pipe_prompt_review::document, source_reference::doc::match_pipe_prompt_review::source_reference::doc::match_pipe_prompt_review::document -->

角色：
- Reviewer

代码位置：

---

<!-- UID: shared-2f5e065de1e49dc6 -->
<!-- 4 处: runtime_main::generate::writer::standard_writer::examplecorp::plan_resume, match_pipe::no_starter::writer::writer_plan_generic_tiktok_branch, match_pipe::planner_write::writer::writer_plan_generic_tiktok_branch, match_pipe::planner_revision::writer::writer_plan_generic_tiktok_branch -->
必要 JD 技术（放在这里）: [列出]
额外技术（stretch tier，叙事自洽即可）: [列出]
→ 此经历 bullet 将使用的完整技术列表: [最终列表]

---

<!-- UID: shared-23d8a3ccb452b50a -->
<!-- 4 处: source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document, source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document, source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document, source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document -->

满足度规则：


---

<!-- UID: shared-dbd8538ccb4cd9d8 -->
<!-- 3 处: match_pipe::no_starter::writer::candidate_context_generic_tiktok_branch, match_pipe::planner_write::writer::candidate_context_generic_tiktok_branch, match_pipe::planner_revision::writer::candidate_context_generic_tiktok_branch -->
- ⚡公司: TikTok | ⚡部门: Security · Backend Infra | ⚡职称: Software Engineer Intern
- ⚡时间: Jun 2025 – Dec 2025 | ⚡地点: San Jose, USA
- 时长: 6个月 | 级别: intern
- 禁用动词: Led, Architected, Drove, Spearheaded, Managed
- Scope: intern, 6个月, 不可声称领导/架构决策，业务/研究/基建均可
- 自然技术栈 core（几乎必然使用）: Docker, Go, Kafka, Kubernetes, PostgreSQL, Python, gRPC
- 自然技术栈 extended（合理推断可能接触）: AWS, Bedrock, CI/CD, ECS, GitHub Actions, Java, LLM, Linux, OpenAI, Prometheus, RAG, REST, Redis, S3
- 自然技术栈 stretch（特定场景可能接触，需叙事支撑）: Elasticsearch, Flink, GraphQL, LangChain, Microservices, MongoDB, React, Spring Boot, TensorFlow, Terraform, TypeScript...

---

<!-- UID: shared-5df0bb73af7a254b -->
<!-- 3 处: source_reference::doc::match_pipe_prompt_review::source_reference::doc::match_pipe_prompt_review::document, source_reference::doc::match_pipe_prompt_review::source_reference::doc::match_pipe_prompt_review::document, source_reference::doc::match_pipe_prompt_review::source_reference::doc::match_pipe_prompt_review::document -->

角色：
- Writer

代码位置：

---

<!-- UID: shared-0914890b5afc880b -->
<!-- 3 处: source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document, source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document, source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document -->

```json
{
  "job_id": "jd_001",

---

<!-- UID: shared-b73e3c45f39e3036 -->
<!-- 3 处: source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document, source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document, source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document -->
]

---


---

<!-- UID: shared-bf94bdb23a077a86 -->
<!-- 3 处: runtime_main::upgrade_revision::writer::bytedance::standard_upgrade::bytedance::bytedance, runtime_seed_retarget::rewrite_writer::writer::bytedance::standard_upgrade::bytedance::bytedance, match_pipe::reviewer_followup::writer::bytedance::upgrade_bytedance_special -->
- 删除任何 TikTok / ByteDance intern 内容，不要把它当作可修补素材
- 证据池仅限 DiDi、Temu、Georgia Tech CS coursework/projects
- 若旧稿因为 seed 骨架保留了 TikTok / ByteDance intern，必须直接推翻该部分并重写

---

<!-- UID: shared-f1406634f9165d96 -->
<!-- 3 处: match_pipe::planner::planner::planner_context, match_pipe::planner_write::writer::planner_writer_context, match_pipe::planner_write::writer::bytedance::planner_writer_context -->
```md
{starter_block}
```

---

<!-- UID: shared-6a58af7252624246 -->
<!-- 71 处: runtime_main::full_review::reviewer::standard_reviewer::examplecorp::full::schema, runtime_seed_retarget::rewrite_review::reviewer::standard_reviewer::examplecorp::rewrite::schema, match_pipe::reviewer::full::reviewer_user, match_pipe::reviewer::full::bytedance::reviewer_user... -->

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


---

<!-- UID: shared-589ffef79afcf9c7 -->
<!-- 2 处: runtime_main::full_review::reviewer::bytedance::standard_reviewer::bytedance::full::schema, runtime_seed_retarget::rewrite_review::reviewer::bytedance::standard_reviewer::bytedance::rewrite::schema -->

**R0 真实性审查 (权重 0.20)**
- 不可变字段（公司/职称/时间/地点）是否与规定完全一致？
- TikTok / ByteDance intern 这段经历如果出现 = CRITICAL（ByteDance 目标岗位必须完全删掉）
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
  - 是否出现任何 TikTok / ByteDance intern 段落？若出现 = critical

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
- 是否错误地重新引入了 ByteDance / TikTok intern，以规避工作经历和课程项目证据不足？
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
- Experience 顺序是否严格倒序（DiDi（2022-2024）→ Temu（2021-2022））？
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


---

<!-- UID: shared-ea49774a31d64da3 -->
<!-- 18 处: runtime_main::generate::writer::standard_writer::examplecorp::format_constraints, runtime_main::generate::writer::bytedance::standard_writer::bytedance::format_constraints, match_pipe::no_starter::writer::format_constraints_shared_mid, match_pipe::no_starter::writer::bytedance::format_constraints_shared_mid... -->
- 每段经历: 4-6 条 bullet，至少 1 条含量化数据
- 项目: 恰好 2 个（至少1个来自工作经历），每项目 4-6 条 bullet
- 项目位置: 项目紧跟对应经历，不单独设 `## Projects` section
- 项目背景行: 每个项目标题下必须紧接一行 `> ` 开头的 blockquote（一句话说明业务痛点/背景，不是重复项目标题），然后才是 bullet 列表
- DiDi scope note 若出现，必须是简短身份说明，不承担全部 leadership/decision story；推荐写法：
  `> Data lead within a **13-person** cross-functional squad spanning product, backend, frontend, mobile, and ops.`

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

**不可变字段（绝不可修改）**

---

<!-- UID: shared-4c4b83a72ce2a809 -->
<!-- 18 处: runtime_main::generate::writer::standard_writer::examplecorp::format_constraints, runtime_main::generate::writer::bytedance::standard_writer::bytedance::format_constraints, match_pipe::no_starter::writer::format_constraints_shared_tail, match_pipe::no_starter::writer::bytedance::format_constraints_shared_tail... -->
- DiDi (mid-senior acting lead): 可用 Led/Coordinated/Drove；可展示 13 人跨职能团队领导力
- DiDi 的全球汇报/管理层传导 scope 不要塞进 scope note；如目标岗位重视 senior stakeholder scope，可用单独 bullet 表达：
  `Represented the headquarters data organization in biweekly global operating reviews, and translated performance signals into two-week recommendations adopted by management and LATAM frontline teams.`
- Temu (junior): 禁用 Led/Architected/Drove/Spearheaded；仅体现 individual contributor 贡献

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

---

<!-- UID: shared-1c446993f55f7846 -->
<!-- 2 处: runtime_main::upgrade_revision::writer::standard_upgrade::examplecorp::main, runtime_seed_retarget::rewrite_writer::writer::standard_upgrade::examplecorp::main -->
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
10. 经历顺序必须保持 TikTok（2025）→ DiDi（2022-2024）→ Temu（2021-2022）
11. 输出必须仍然满足全部格式硬约束
12. 如果 seed phrasing、旧 summary、旧 bullet 选择本身就是失分原因，可以直接替换，不要为了“保留 seed”而保留弱表达
13. rewrite 的目标是通过，而不是尽量少改；只要真实且自洽，可以换掉低质量旧表述


---

<!-- UID: shared-84037360810f5485 -->
<!-- 2 处: runtime_main::upgrade_revision::writer::bytedance::standard_upgrade::bytedance::main, runtime_seed_retarget::rewrite_writer::writer::bytedance::standard_upgrade::bytedance::main -->
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
10. 经历顺序必须保持 DiDi（2022-2024）→ Temu（2021-2022）
11. 输出必须仍然满足全部格式硬约束
12. 如果 seed phrasing、旧 summary、旧 bullet 选择本身就是失分原因，可以直接替换，不要为了“保留 seed”而保留弱表达
13. rewrite 的目标是通过，而不是尽量少改；只要真实且自洽，可以换掉低质量旧表述


---

<!-- UID: shared-644ea9a424988a40 -->
<!-- 2 处: match_pipe::reviewer_followup::writer::upgrade_prompt, match_pipe::reviewer_followup::writer::bytedance::upgrade_prompt -->
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
10. 经历顺序必须保持 {experience_order}
11. 输出必须仍然满足全部格式硬约束
12. 如果 seed phrasing、旧 summary、旧 bullet 选择本身就是失分原因，可以直接替换，不要为了“保留 seed”而保留弱表达
13. rewrite 的目标是通过，而不是尽量少改；只要真实且自洽，可以换掉低质量旧表述


---

<!-- UID: shared-6dfee6ca69e7423e -->
<!-- 2 处: runtime_main::generate::writer::standard_writer::examplecorp::candidate_context, runtime_main::generate::writer::bytedance::standard_writer::bytedance::candidate_context -->
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


---

<!-- UID: shared-9d46ed6e09fa377d -->
<!-- 2 处: runtime_main::full_review::reviewer::standard_reviewer::examplecorp::full::context, runtime_seed_retarget::rewrite_review::reviewer::standard_reviewer::examplecorp::rewrite::context -->

公司: ExampleCorp | 岗位: {title} | 角色类型: {role_type} | 职级: {seniority}
必须技术栈: {tech_required}
加分技术栈: {tech_preferred}
团队方向: {team_direction}

不可变字段（必须与此完全一致）:
- TikTok: Software Engineer Intern | TikTok · Security | Jun 2025 – Dec 2025 | San Jose, USA
- DiDi: Senior Data Analyst | DiDi · IBG · Food | Sep 2022 – May 2024 | Beijing/Mexico
- Temu: Data Analyst | Temu · R&D | Jun 2021 – Feb 2022 | Shanghai



---

<!-- UID: shared-188758ac9d427719 -->
<!-- 2 处: runtime_main::full_review::reviewer::bytedance::standard_reviewer::bytedance::full::context, runtime_seed_retarget::rewrite_review::reviewer::bytedance::standard_reviewer::bytedance::rewrite::context -->

公司: ByteDance | 岗位: {title} | 角色类型: {role_type} | 职级: {seniority}
必须技术栈: {tech_required}
加分技术栈: {tech_preferred}
团队方向: {team_direction}

不可变字段（必须与此完全一致）:
- DiDi: Senior Data Analyst | DiDi · IBG · Food | Sep 2022 – May 2024 | Beijing/Mexico
- Temu: Data Analyst | Temu · R&D | Jun 2021 – Feb 2022 | Shanghai
- TikTok / ByteDance intern experience must be absent for ByteDance target roles.



---

<!-- UID: shared-1adefc89bcc64ede -->
<!-- 24 处: runtime_main::generate::writer::standard_writer::examplecorp::output_contract, runtime_main::upgrade_revision::writer::standard_upgrade::examplecorp::output_contract, runtime_seed_retarget::rewrite_writer::writer::standard_upgrade::examplecorp::output_contract, runtime_main::generate::writer::bytedance::standard_writer::bytedance::output_contract... -->
* China national certified Go **2-dan** — city **champion** (2022) and third place (2023).

**Header 拼写规则:**
- `## Experience`（不是 `## Professional Experience`）
- `## Skills`（不是 `## Technical Skills`）
- `## Achievements`（不是 `## Achievement`）
- 项目必须在对应经历下方，不单独成 section
- 只输出简历正文，不要解释、注释、分析

直接输出修改后的完整简历 Markdown，不要附带解释。

---

<!-- UID: shared-3a4a25f88fd3435d -->
<!-- 2 处: runtime_main::generate::writer::standard_writer::examplecorp::candidate_context, runtime_main::generate::writer::bytedance::standard_writer::bytedance::candidate_context -->
- ⚡公司: Temu | ⚡部门: R&D | ⚡职称: Data Analyst
- ⚡时间: Jun 2021 – Feb 2022 | ⚡地点: Shanghai
- 时长: 8个月 | 级别: junior
- 禁用动词: Led, Architected, Drove, Spearheaded, Directed
- Scope上限: individual contributor, 8个月短期经历
- 自然技术栈 core（几乎必然使用）: Hive, Pandas, Python, SQL, Spark SQL
- 自然技术栈 extended（合理推断可能接触）: A/B Testing, Airflow, Jupyter, Matplotlib, NumPy, scikit-learn
- 自然技术栈 stretch（特定场景可能接触，需叙事支撑）: ETL, Flask, HiveQL, Kafka, Redis...


---

<!-- UID: shared-f6a84661a9723c93 -->
<!-- 2 处: runtime_seed_retarget::rewrite_review::reviewer::standard_reviewer::examplecorp::rewrite::context, runtime_seed_retarget::rewrite_review::reviewer::bytedance::standard_reviewer::bytedance::rewrite::context -->

下方简历已经确认“需要继续重写”，你的职责不是给保守补丁单，而是判断它如何跨过 pass 线：
- 如果现有稿件只是被 seed phrasing / summary framing / bullet 选择束缚，你应明确允许结构性重写
- 可以建议重写 Summary、Skills、最相关 experiences、project baseline、bullet 取舍与叙事顺序
- 不要因为“最好少改”而压制本应重写的部分
- 仍然禁止改动不可变字段、凭空新增不可信经历、删除 JD must-have 技术来规避问题
- revision_priority 和 revision_instructions 应优先输出“怎样改到 pass”，而不是“怎样保守止损”



---

<!-- UID: shared-1584e4ff89138d9a -->
<!-- 2 处: match_pipe::old_match_anchor::writer::same_company::retarget_same_company, match_pipe::new_dual_channel::writer::same_company::retarget_same_company -->
- 当前目标岗位与 seed 同属 **ExampleCorp**
- 这是该公司的公司内锚点 seed。
- seed 来源岗位: 已登记公司内来源
- 把公司内的 team / domain / 项目池视为“准不可变骨架”，不要写成完全不同的人做了完全不同的事
- 允许调整的只有：Summary 侧重点、Skills 少量技术取舍、同一项目的不同强调角度、少量 bullet 技术细节
- 不允许把业务方向改成明显不同的另一条线，不允许引入与现有公司版本完全无关的新项目池
- 同一公司家族下，全部版本合计最多保留 4 个项目；TikTok/Bytedance 实习项目最多 2 个
- 写法目标是：读者能自然感觉“同一个人在讲同一批经历，只是针对不同岗位换了强调方式”

---

<!-- UID: shared-360b8856cf15a4a4 -->
<!-- 2 处: runtime_main::generate::writer::standard_writer::examplecorp::plan_resume, runtime_main::generate::writer::bytedance::standard_writer::bytedance::plan_resume -->

按照上方 PLAN 的规划，在 <RESUME> 标签内输出完整的 Markdown 简历：

```
<RESUME>
[完整简历内容]
</RESUME>
```

---

<!-- UID: shared-5c0299ce24b58fc9 -->
<!-- 2 处: match_pipe::old_match_anchor::writer::bytedance::same_company::retarget_same_company_bytedance, match_pipe::new_dual_channel::writer::bytedance::same_company::retarget_same_company_bytedance -->
- 当前目标岗位命中了 ByteDance 同公司 seed，但该 seed 只能作为弱参考
- 这是该公司的公司内锚点 seed。
- seed 来源岗位: 已登记公司内来源
- 不得继承 seed 中的 TikTok / ByteDance intern 叙事骨架、项目或 bullet
- 只允许借用 seed 中仍然适用于 DiDi、Temu、Georgia Tech CS coursework/projects 的技术 framing
- 任何与 TikTok / ByteDance intern 绑定的内容都必须删掉，再重写成新的两段全职经历 + GT CS 项目版本

---

<!-- UID: shared-6f25f8d62a7b97db -->
<!-- 4 处: source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document, source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document, source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document, source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document -->
  }
}
```

---


---

<!-- UID: shared-8ada3b93e95f2f49 -->
<!-- 2 处: source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document, source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document -->
  ]
}
```

---


---

<!-- UID: shared-04a668d2f362bf2e -->
<!-- 2 处: match_pipe::reviewer_followup::writer::upgrade_prompt, match_pipe::reviewer_followup::writer::bytedance::upgrade_prompt -->
请把下面这份历史简历做一次面向目标 JD 的升级式重写，而不是仅做字面修补。

当前评分: 91.5/100
历史来源: route_mode={route_mode} | seed_label={seed_label}


---

<!-- UID: shared-06b456f3339eb9bb -->
<!-- 2 处: source_reference::doc::match_pipe_prompt_review::source_reference::doc::match_pipe_prompt_review::document, source_reference::doc::match_pipe_prompt_review::source_reference::doc::match_pipe_prompt_review::document -->

角色：
- Writer
- Revision Writer
- Upgrade Writer

---

<!-- UID: shared-a72ecde6f5423c79 -->
<!-- 2 处: runtime_main::generate::writer::standard_writer::examplecorp::plan_resume, runtime_main::generate::writer::bytedance::standard_writer::bytedance::plan_resume -->

请在 <PLAN> 标签内完成：

```
<PLAN>

---

<!-- UID: shared-39b918224f61f0f6 -->
<!-- 2 处: source_reference::doc::match_pipe_prompt_review::source_reference::doc::match_pipe_prompt_review::document, source_reference::doc::match_pipe_prompt_review::source_reference::doc::match_pipe_prompt_review::document -->

角色：
- Planner

代码位置：

---

<!-- UID: shared-725f916d0a95aac6 -->
<!-- 4 处: runtime_main::upgrade_revision::writer::standard_upgrade::examplecorp::main, runtime_seed_retarget::rewrite_writer::writer::standard_upgrade::examplecorp::main, runtime_main::upgrade_revision::writer::bytedance::standard_upgrade::bytedance::main, runtime_seed_retarget::rewrite_writer::writer::bytedance::standard_upgrade::bytedance::main -->
{tech_required}





---

<!-- UID: shared-5abb5c2d90cac90c -->
<!-- 2 处: source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document, source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document -->

如果岗位要求：

* 主流编程语言


---

<!-- UID: shared-07226a795d41876a -->
<!-- 2 处: match_pipe::reviewer::full::bytedance::reviewer_user_bytedance, match_pipe::planner_direct_review::reviewer::bytedance::reviewer_user_bytedance -->
R0: TikTok / ByteDance intern 这段经历如果出现 = CRITICAL（ByteDance 目标岗位必须完全删掉）
R1: 是否出现任何 TikTok / ByteDance intern 段落？若出现 = critical
R3: 是否错误地重新引入了 ByteDance / TikTok intern，以规避工作经历和课程项目证据不足？
R5: Experience 顺序是否严格倒序（DiDi（2022-2024）→ Temu（2021-2022））？

---

<!-- UID: shared-10cbc7d3907412de -->
<!-- 2 处: runtime_main::full_review::reviewer::bytedance::standard_reviewer::bytedance::full::context, runtime_seed_retarget::rewrite_review::reviewer::bytedance::standard_reviewer::bytedance::rewrite::context -->
- 对 ByteDance 目标岗位，TikTok / ByteDance intern 这段经历必须完全不存在
- 若简历仍引用了 TikTok / ByteDance intern，视为 critical，并要求删除后仅用 DiDi / Temu / Georgia Tech CS coursework/projects 重写；GT 教育主干仍按共享材料保留



---

<!-- UID: shared-db07188c53d80924 -->
<!-- 2 处: match_pipe::planner_revision::writer::planner_revision_context, match_pipe::planner_revision::writer::bytedance::planner_revision_context -->
- 当前版本评分: {weighted_score}/100
- 当前是否通过: {passed}
- 当前 reviewer 是否要求继续修改: {needs_revision}


---

<!-- UID: shared-fab22f119686283d -->
<!-- 8 处: runtime_main::generate::writer::standard_writer::examplecorp::plan_resume, runtime_main::generate::writer::bytedance::standard_writer::bytedance::plan_resume, match_pipe::no_starter::writer::writer_plan_shared_tail, match_pipe::no_starter::writer::bytedance::writer_plan_shared_tail... -->
[列出要保留的学历条目及理由]
</PLAN>
```


---

<!-- UID: shared-73ba458d0045e65a -->
<!-- 2 处: match_pipe::planner_write::writer::planner_writer_context, match_pipe::planner_write::writer::bytedance::planner_writer_context -->
```json
{planner_json}
```


---

<!-- UID: shared-f5fe240d31478f4b -->
<!-- 2 处: match_pipe::planner_write::writer::planner_writer_context, match_pipe::planner_write::writer::bytedance::planner_writer_context -->
```json
{matcher_json}
```


---

<!-- UID: shared-4cd39a94590c6fbf -->
<!-- 2 处: runtime_main::generate::writer::standard_writer::examplecorp::plan_resume, runtime_main::generate::writer::bytedance::standard_writer::bytedance::plan_resume -->
技术（core/extended tier，体现数据分析基础）: [列出]
→ 此经历 bullet 将使用的完整技术列表: [最终列表]


---

<!-- UID: shared-c62bd07a40a82f32 -->
<!-- 2 处: runtime_main::generate::writer::standard_writer::examplecorp::plan_resume, runtime_main::generate::writer::bytedance::standard_writer::bytedance::plan_resume -->
必要 JD 技术（若工作经历不够自然覆盖，优先放这里）: [列出]
→ 此教育项目 bullet 将使用的完整技术列表: [最终列表]


---

<!-- UID: shared-a52c7595b0bdd78f -->
<!-- 2 处: source_reference::doc::match_pipe_prompt_review::source_reference::doc::match_pipe_prompt_review::document, source_reference::doc::match_pipe_prompt_review::source_reference::doc::match_pipe_prompt_review::document -->
- Downstream dual-channel Writer

代码位置：

---

<!-- UID: shared-28457b32e2d27321 -->
<!-- 2 处: source_reference::doc::prompt_canonical_review::source_reference::doc::prompt_canonical_review::document, source_reference::doc::prompt_canonical_review::source_reference::doc::prompt_canonical_review::document -->
  - `B-OUTPUT-002`
  - `B-OUTPUT-001`


---

<!-- UID: shared-cc70f8732f227d3f -->
<!-- 2 处: match_pipe::planner_revision::writer::planner_revision_context, match_pipe::planner_revision::writer::bytedance::planner_revision_context -->
```md
{current_resume_md}
```

---

<!-- UID: shared-a4bdcc1b142a712f -->
<!-- 2 处: source_reference::design_guide::task_general_prompt::source_reference::design_guide::task_general_prompt::document, source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document -->
* Python
* Java
* C++

---

<!-- UID: shared-5f070f66e84305fc -->
<!-- 2 处: source_reference::design_guide::task_general_prompt::source_reference::design_guide::task_general_prompt::document, source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document -->

* 必须有 C++ 经验


---

<!-- UID: shared-05606e970ecc6f4d -->
<!-- 2 处: source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document, source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document -->

* 必须有 C++


---

<!-- UID: shared-77deae8b7fcdb887 -->
<!-- 2 处: source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document, source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document -->

* C++


---

<!-- UID: shared-efc917274b47a363 -->
<!-- 2 处: source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document, source_reference::design_guide::execution_suggestions_prompt::source_reference::design_guide::execution_suggestions_prompt::document -->

表示：


---

# 唯一片段

<!-- 上下文: runtime_main::generate::writer :: standard_writer::examplecorp::system -->

<!-- UID: frag-0b56daeed9c9a23e -->

[NO_CASCADE_TEST]

---

<!-- 上下文: runtime_main::generate::writer :: standard_writer::examplecorp::candidate_context -->
<!-- 小标题: ## 候选人经历框架（⚡=不可变字段，其余可由 Writer 决定） -->

<!-- UID: frag-86d73b1b6da5f673 -->


---

<!-- 上下文: runtime_main::generate::writer :: standard_writer::examplecorp::candidate_context -->
<!-- 小标题: ### TikTok — Software Engineer Intern (不可变) -->

<!-- UID: frag-81e4e86bbe155b44 -->
- ⚡公司: TikTok | ⚡部门: Security | ⚡职称: Software Engineer Intern
- ⚡时间: Jun 2025 – Dec 2025 | ⚡地点: San Jose, USA
- 时长: 6个月 | 级别: intern
- 禁用动词: Led, Architected, Drove, Spearheaded, Managed
- Scope上限: intern, 6个月, 不可声称领导/架构决策
- 自然技术栈 core（几乎必然使用）: Docker, Go, Kafka, Kubernetes, PostgreSQL, Python, gRPC
- 自然技术栈 extended（合理推断可能接触）: AWS, Bedrock, CI/CD, ECS, GitHub Actions, Java, LLM, Linux, OpenAI, Prometheus, RAG, REST, Redis, S3
- 自然技术栈 stretch（特定场景可能接触，需叙事支撑）: Elasticsearch, Flink, GraphQL, LangChain, Microservices, MongoDB, React, Spring Boot, TensorFlow, Terraform, TypeScript...


---

<!-- 上下文: runtime_main::generate::writer :: standard_writer::examplecorp::candidate_context -->
<!-- 小标题: ### 教育经历（可根据 JD 方向选择列哪些） -->

<!-- UID: frag-6e0578f55af52e95 -->


---

<!-- 上下文: runtime_main::generate::writer :: standard_writer::examplecorp::candidate_context -->
<!-- 小标题: ### 成就（融入 Summary 第3句） -->

<!-- UID: frag-4976aa01fcd3db00 -->
- 中国国家认证围棋二段棋手，2022年度市赛第一，2023年度市赛第三

---

<!-- 上下文: runtime_main::generate::writer :: standard_writer::examplecorp::jd_context -->
<!-- 小标题: ## 目标 JD 信息 -->

<!-- UID: frag-a4d7d8edaf63fb5a -->

**公司:** ExampleCorp

---

<!-- 上下文: runtime_main::generate::writer :: standard_writer::examplecorp::format_constraints -->
<!-- 小标题: ## 格式硬约束（违反=直接FAIL） -->

<!-- UID: frag-f2ed765204193225 -->
- Experience 顺序: **严格倒序** — TikTok（2025）→ DiDi（2022-2024）→ Temu（2021-2022）

---

<!-- UID: frag-984bba7e0f4b0f65 -->
- TikTok: Software Engineer Intern | TikTok · Security | Jun 2025 – Dec 2025 | San Jose, USA
- DiDi: Senior Data Analyst | DiDi · IBG · Food | Sep 2022 – May 2024 | Beijing/Mexico
- Temu: Data Analyst | Temu · R&D | Jun 2021 – Feb 2022 | Shanghai

**职级 Scope 规则**
- TikTok (intern, 6个月): 禁用 Led/Architected/Drove/Spearheaded/Managed；体现个人贡献，不主张架构决策
  → bullet 数量建议 **4-5 条**（6个月实习期内独立成就不超过 5 条，超出则可信度下降）

---

<!-- 上下文: runtime_main::generate::writer :: standard_writer::examplecorp::plan_resume -->
<!-- 小标题: ## 技术分配规划 -->

<!-- UID: frag-b7c5d96ba0987f84 -->


---

<!-- 上下文: runtime_main::generate::writer :: standard_writer::examplecorp::plan_resume -->
<!-- 小标题: ### TikTok（intern，最灵活，承接 JD 核心技术） -->

<!-- UID: frag-a3df536fe2abd9a9 -->


---

<!-- 上下文: runtime_main::generate::writer :: standard_writer::examplecorp::plan_resume -->
<!-- 小标题: ## SKILLS 推导（= 上述经历/项目技术列表的并集） -->

<!-- UID: frag-85400ac58e05320e -->
[按 2-4 个类别优先组织；若为满足 14 词硬上限可扩到 5 类；任何类别不得少于 4 个技术]


---

<!-- 上下文: runtime_main::generate::writer :: standard_writer::examplecorp::output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-6d9d281389629af6 -->


---

<!-- 上下文: runtime_main::generate::writer :: standard_writer::examplecorp::output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-b362ba7b68a6e3f1 -->
*Dates*


---

<!-- 上下文: runtime_main::full_review::reviewer :: standard_reviewer::examplecorp::full::context -->
<!-- 小标题: ## 目标 JD -->

<!-- UID: frag-bf57966863019f4d -->


---

<!-- 上下文: runtime_main::full_review::reviewer :: standard_reviewer::examplecorp::full::context -->
<!-- 小标题: ## 待审查简历 -->

<!-- UID: frag-2f3b8f2ada0640cd -->

{resume_md}

---

<!-- 上下文: runtime_main::full_review::reviewer :: standard_reviewer::examplecorp::full::schema -->

<!-- UID: frag-590c8f04f8dff298 -->
请对以下简历进行严格的 9 维度审查，返回 JSON 格式结果。


---

<!-- 上下文: runtime_main::upgrade_revision::writer :: standard_upgrade::examplecorp::system -->

<!-- UID: frag-5a78c2ae726f4346 -->
你是专业简历升级专家。你可以在保持不可变字段、真实性边界和核心职业叙事不变的前提下，重写 summary、skills、experience bullets、project baseline 和项目 framing，以显著提升 JD 匹配度、scope 表达完整度和整体得分。不要被 seed phrasing、旧 summary 或旧 bullet 选择束缚；如果旧稿的 framing 本身导致失分，应主动替换成更强、更清晰、但仍真实自洽的表达。直接输出修改后的完整简历 Markdown，不要附带解释。

---

<!-- 上下文: runtime_main::upgrade_revision::writer :: standard_upgrade::examplecorp::main -->
<!-- 小标题: ## 最优先修改事项 -->

<!-- UID: frag-db03bd8abe87b797 -->
  1. {priority}


---

<!-- 上下文: runtime_main::upgrade_revision::writer :: standard_upgrade::examplecorp::main -->
<!-- 小标题: ## 审查发现 -->

<!-- UID: frag-576f4874f93c7b80 -->
[r0] [HIGH] {field}: {issue} → 修改建议: {fix}


---

<!-- 上下文: runtime_main::upgrade_revision::writer :: standard_upgrade::examplecorp::main -->
<!-- 小标题: ## 原审查详细修改指令 -->

<!-- UID: frag-3de0563f630638d5 -->
{revision_instructions}

---

<!-- 上下文: runtime_main::upgrade_revision::writer :: standard_upgrade::examplecorp::resume_context -->
<!-- 小标题: ## 原始简历 -->

<!-- UID: frag-6e13eb35eded9ed9 -->
{resume_md}

---

<!-- 上下文: runtime_main::upgrade_revision::writer :: standard_upgrade::examplecorp::output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-f9a7d4274562557f -->


---

<!-- 上下文: runtime_main::upgrade_revision::writer :: standard_upgrade::examplecorp::output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-cd8098c7bcf10eef -->
*Dates*


---

<!-- 上下文: runtime_seed_retarget::rewrite_review::reviewer :: standard_reviewer::examplecorp::rewrite::context -->
<!-- 小标题: ## 待审查简历 -->

<!-- UID: frag-0132ad9aa4b99c00 -->

{resume_md}

---

<!-- 上下文: runtime_seed_retarget::rewrite_review::reviewer :: standard_reviewer::examplecorp::rewrite::schema -->

<!-- UID: frag-5f596f5543d41e90 -->
请对以下简历进行严格的 9 维度审查，返回 JSON 格式结果。


---

<!-- 上下文: runtime_seed_retarget::rewrite_writer::writer :: standard_upgrade::examplecorp::system -->

<!-- UID: frag-36d41bf7340af514 -->
你是专业简历升级专家。你可以在保持不可变字段、真实性边界和核心职业叙事不变的前提下，重写 summary、skills、experience bullets、project baseline 和项目 framing，以显著提升 JD 匹配度、scope 表达完整度和整体得分。不要被 seed phrasing、旧 summary 或旧 bullet 选择束缚；如果旧稿的 framing 本身导致失分，应主动替换成更强、更清晰、但仍真实自洽的表达。直接输出修改后的完整简历 Markdown，不要附带解释。

---

<!-- 上下文: runtime_seed_retarget::rewrite_writer::writer :: standard_upgrade::examplecorp::main -->
<!-- 小标题: ## 最优先修改事项 -->

<!-- UID: frag-9736ee99aa6a5f74 -->
  1. {priority}


---

<!-- 上下文: runtime_seed_retarget::rewrite_writer::writer :: standard_upgrade::examplecorp::main -->
<!-- 小标题: ## 审查发现 -->

<!-- UID: frag-df2c0aa41c7edfbb -->
[r0] [HIGH] {field}: {issue} → 修改建议: {fix}


---

<!-- 上下文: runtime_seed_retarget::rewrite_writer::writer :: standard_upgrade::examplecorp::main -->
<!-- 小标题: ## 原审查详细修改指令 -->

<!-- UID: frag-00683317efeee1bd -->
{revision_instructions}

---

<!-- 上下文: runtime_seed_retarget::rewrite_writer::writer :: standard_upgrade::examplecorp::resume_context -->
<!-- 小标题: ## 原始简历 -->

<!-- UID: frag-d8ba6598f1d2f1e0 -->
{resume_md}

---

<!-- 上下文: runtime_seed_retarget::rewrite_writer::writer :: standard_upgrade::examplecorp::output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-54edf36e1845dd78 -->


---

<!-- 上下文: runtime_seed_retarget::rewrite_writer::writer :: standard_upgrade::examplecorp::output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-4a3d7602b8c94139 -->
*Dates*


---

<!-- 上下文: runtime_main::generate::writer::bytedance :: standard_writer::bytedance::candidate_context -->
<!-- 小标题: ## 候选人经历框架（⚡=不可变字段，其余可由 Writer 决定） -->

<!-- UID: frag-5c70a6ba7455a0d0 -->


---

<!-- 上下文: runtime_main::generate::writer::bytedance :: standard_writer::bytedance::candidate_context -->
<!-- 小标题: ### 教育经历（可根据 JD 方向选择列哪些） -->

<!-- UID: frag-1ff13cf900736101 -->
- M.S. Computer Science | Georgia Institute of Technology | Expected May 2026
  → 当 UIUC MSIM 出现时写为 M.S. Computer Science (OMSCS)；  仅出现GT时直接写 M.S. Computer Science
  → GT 教育主干对所有线路共享；ByteDance 目标岗位中，Georgia Tech CS coursework/projects 可以进一步提升为主要软件工程/系统实现证据来源。
- M.S. Information Management (MSIM) | University of Illinois Urbana-Champaign | Expected May 2026 — 保留当: Data方向/PM方向/信息管理相关岗位 | 可省略当: 纯SWE后端且与信息管理无关
- M.S. International Business | Beijing International Studies University | Sep 2018 – Jun 2021 — 保留当: FinTech/国际业务/金融数据方向 | 可省略当: 与目标岗位完全无关且简历空间紧张
- B.A. Philosophy & Psychology | Beijing Normal University | Sep 2014 – Jun 2018 — 保留当: TechPM(认知科学角度)/NLP(语言学角度)/UX Research | 可省略当: 大多数纯技术岗位


---

<!-- 上下文: runtime_main::generate::writer::bytedance :: standard_writer::bytedance::candidate_context -->
<!-- 小标题: ### 成就（融入 Summary 第3句） -->

<!-- UID: frag-273a493ffec0ff80 -->
- 中国国家认证围棋二段棋手，2022年度市赛第一，2023年度市赛第三


---

<!-- 上下文: runtime_main::generate::writer::bytedance :: standard_writer::bytedance::candidate_context -->
<!-- 小标题: ### ByteDance 特殊写作边界 -->

<!-- UID: frag-17976883674fe129 -->
- 不得写入或提及 TikTok / ByteDance intern 这段经历
- 目标岗位只能使用 DiDi、Temu 和 Georgia Tech CS coursework/projects 作为证据池；GT 教育主干仍按共享教育块保留，ByteDance 只是进一步加权 GT coursework/projects。

---

<!-- 上下文: runtime_main::generate::writer::bytedance :: standard_writer::bytedance::jd_context -->
<!-- 小标题: ## 目标 JD 信息 -->

<!-- UID: frag-5d23c8364ce5d970 -->

**公司:** ByteDance

---

<!-- 上下文: runtime_main::generate::writer::bytedance :: standard_writer::bytedance::format_constraints -->
<!-- 小标题: ## 格式硬约束（违反=直接FAIL） -->

<!-- UID: frag-358ab38a96a3641b -->
- Experience 顺序: **严格倒序** — DiDi（2022-2024）→ Temu（2021-2022）

---

<!-- UID: frag-d086813769a329e1 -->
- DiDi: Senior Data Analyst | DiDi · IBG · Food | Sep 2022 – May 2024 | Beijing/Mexico
- Temu: Data Analyst | Temu · R&D | Jun 2021 – Feb 2022 | Shanghai
- TikTok / ByteDance intern experience must be absent for ByteDance target roles.

**职级 Scope 规则**
- ByteDance 目标岗位: 不允许出现 TikTok / ByteDance intern；需要更多 SWE 证据时，优先把 Georgia Tech CS coursework/projects 作为主力软件工程/系统实现证据，而不是回填该实习。

---

<!-- 上下文: runtime_main::generate::writer::bytedance :: standard_writer::bytedance::plan_resume -->
<!-- 小标题: ## 技术分配规划 -->

<!-- UID: frag-40cfe16c7fa38a03 -->


---

<!-- 上下文: runtime_main::generate::writer::bytedance :: standard_writer::bytedance::plan_resume -->
<!-- 小标题: ## SKILLS 推导（= 上述经历/项目技术列表的并集） -->

<!-- UID: frag-0e5932a44d0ec035 -->
[按 2-4 个类别优先组织；若为满足 14 词硬上限可扩到 5 类；任何类别不得少于 4 个技术]


---

<!-- 上下文: runtime_main::generate::writer::bytedance :: standard_writer::bytedance::output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-8766431050a5095c -->


---

<!-- 上下文: runtime_main::generate::writer::bytedance :: standard_writer::bytedance::output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-55f50395a24770c3 -->
*Dates*


---

<!-- 上下文: runtime_main::full_review::reviewer::bytedance :: standard_reviewer::bytedance::full::context -->
<!-- 小标题: ## 目标 JD -->

<!-- UID: frag-a98865b421314c8c -->


---

<!-- 上下文: runtime_main::full_review::reviewer::bytedance :: standard_reviewer::bytedance::full::context -->
<!-- 小标题: ## 待审查简历 -->

<!-- UID: frag-728f004d99bf92fd -->

{resume_md}

---

<!-- 上下文: runtime_main::full_review::reviewer::bytedance :: standard_reviewer::bytedance::full::schema -->

<!-- UID: frag-3261d07da198f4ca -->
请对以下简历进行严格的 9 维度审查，返回 JSON 格式结果。


---

<!-- 上下文: runtime_main::upgrade_revision::writer::bytedance :: standard_upgrade::bytedance::system -->

<!-- UID: frag-53c3b8a94189ea3d -->
你是专业简历升级专家。你可以在保持不可变字段、真实性边界和核心职业叙事不变的前提下，重写 summary、skills、experience bullets、project baseline 和项目 framing，以显著提升 JD 匹配度、scope 表达完整度和整体得分。不要被 seed phrasing、旧 summary 或旧 bullet 选择束缚；如果旧稿的 framing 本身导致失分，应主动替换成更强、更清晰、但仍真实自洽的表达。直接输出修改后的完整简历 Markdown，不要附带解释。

---

<!-- 上下文: runtime_main::upgrade_revision::writer::bytedance :: standard_upgrade::bytedance::main -->
<!-- 小标题: ## 最优先修改事项 -->

<!-- UID: frag-c6d84cb8f89b9cf7 -->
  1. {priority}


---

<!-- 上下文: runtime_main::upgrade_revision::writer::bytedance :: standard_upgrade::bytedance::main -->
<!-- 小标题: ## 审查发现 -->

<!-- UID: frag-8fb62f79084137b8 -->
[r0] [HIGH] {field}: {issue} → 修改建议: {fix}


---

<!-- 上下文: runtime_main::upgrade_revision::writer::bytedance :: standard_upgrade::bytedance::main -->
<!-- 小标题: ## 原审查详细修改指令 -->

<!-- UID: frag-935332dbf06368a5 -->
{revision_instructions}

---

<!-- 上下文: runtime_main::upgrade_revision::writer::bytedance :: standard_upgrade::bytedance::resume_context -->
<!-- 小标题: ## 原始简历 -->

<!-- UID: frag-e7fdf9c9f3810de7 -->
{resume_md}

---

<!-- 上下文: runtime_main::upgrade_revision::writer::bytedance :: standard_upgrade::bytedance::output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-e3f6147b90064258 -->


---

<!-- 上下文: runtime_main::upgrade_revision::writer::bytedance :: standard_upgrade::bytedance::output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-de77b891d143eae9 -->
*Dates*


---

<!-- 上下文: runtime_seed_retarget::rewrite_review::reviewer::bytedance :: standard_reviewer::bytedance::rewrite::context -->
<!-- 小标题: ## 待审查简历 -->

<!-- UID: frag-ba6a346e99c488a0 -->

{resume_md}

---

<!-- 上下文: runtime_seed_retarget::rewrite_review::reviewer::bytedance :: standard_reviewer::bytedance::rewrite::schema -->

<!-- UID: frag-92328bbd941de889 -->
请对以下简历进行严格的 9 维度审查，返回 JSON 格式结果。


---

<!-- 上下文: runtime_seed_retarget::rewrite_writer::writer::bytedance :: standard_upgrade::bytedance::system -->

<!-- UID: frag-a76f3d0f07266a19 -->
你是专业简历升级专家。你可以在保持不可变字段、真实性边界和核心职业叙事不变的前提下，重写 summary、skills、experience bullets、project baseline 和项目 framing，以显著提升 JD 匹配度、scope 表达完整度和整体得分。不要被 seed phrasing、旧 summary 或旧 bullet 选择束缚；如果旧稿的 framing 本身导致失分，应主动替换成更强、更清晰、但仍真实自洽的表达。直接输出修改后的完整简历 Markdown，不要附带解释。

---

<!-- 上下文: runtime_seed_retarget::rewrite_writer::writer::bytedance :: standard_upgrade::bytedance::main -->
<!-- 小标题: ## 最优先修改事项 -->

<!-- UID: frag-6f4157ccb91bab8a -->
  1. {priority}


---

<!-- 上下文: runtime_seed_retarget::rewrite_writer::writer::bytedance :: standard_upgrade::bytedance::main -->
<!-- 小标题: ## 审查发现 -->

<!-- UID: frag-1b9ed590f0d1b51a -->
[r0] [HIGH] {field}: {issue} → 修改建议: {fix}


---

<!-- 上下文: runtime_seed_retarget::rewrite_writer::writer::bytedance :: standard_upgrade::bytedance::main -->
<!-- 小标题: ## 原审查详细修改指令 -->

<!-- UID: frag-89b7e93cdfaa753b -->
{revision_instructions}

---

<!-- 上下文: runtime_seed_retarget::rewrite_writer::writer::bytedance :: standard_upgrade::bytedance::resume_context -->
<!-- 小标题: ## 原始简历 -->

<!-- UID: frag-3d19fc04e8cac2a4 -->
{resume_md}

---

<!-- 上下文: runtime_seed_retarget::rewrite_writer::writer::bytedance :: standard_upgrade::bytedance::output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-02ec06d98691b73f -->


---

<!-- 上下文: runtime_seed_retarget::rewrite_writer::writer::bytedance :: standard_upgrade::bytedance::output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-33ba9645c75f6137 -->
*Dates*


---

<!-- 上下文: runtime_reviewer_fallback::json_repair::reviewer_repairer :: runtime_reviewer_fallback::json_repair::system -->

<!-- UID: frag-ba4f9c301cbf5107 -->
你是 JSON 修复器。输入是一段可能有少量格式错误的 JSON。输出必须是严格合法的 JSON 对象，不要附加解释，不要使用 Markdown code fence。

---

<!-- 上下文: runtime_reviewer_fallback::json_repair::reviewer_repairer :: runtime_reviewer_fallback::json_repair::user -->

<!-- UID: frag-73d5c54e4ee31cb7 -->
将下面这段 reviewer 输出修复为合法 JSON。不要改动语义，不要省略字段，不要解释，只输出 JSON 对象。

{raw_reviewer_output}

---

<!-- 上下文: match_pipe::no_starter::writer :: candidate_context_shared_experience -->
<!-- 小标题: ## 候选人经历框架（⚡=不可变字段，其余可由 Writer 决定） -->

<!-- UID: frag-254da3e517d3c96a -->


---

<!-- 上下文: match_pipe::no_starter::writer :: candidate_context_shared_achievements -->
<!-- 小标题: ### 成就（融入 Summary 第3句） -->

<!-- UID: frag-2bc84249130d7888 -->
- 中国国家认证围棋二段棋手，2022年度市赛第一，2023年度市赛第三

---

<!-- 上下文: match_pipe::no_starter::writer :: writer_plan_shared_didi_temu -->
<!-- 小标题: ### Temu（junior DE，研究型/research，硬核起点，大数据管道基建/机器学习/算法模型/亿级数据分析与训练基础，无AI接触） -->

<!-- UID: frag-111b8164e5f197b7 -->
技术（core/extended tier）: [列出]
→ 此经历 bullet 将使用的完整技术列表: [最终列表]

---

<!-- 上下文: match_pipe::no_starter::writer :: writer_plan_shared_gt_coursework -->
<!-- 小标题: ### Georgia Tech CS coursework/projects（非工业项目，最灵活，补足 SWE / systems / backend / 硬件 / 机械工程 缺口，有AI接触） -->

<!-- UID: frag-3d18d2490f12a714 -->
必要 JD 技术（若工作经历不够自然覆盖，优先放这里）: [列出]
→ 此教育项目 bullet 将使用的完整技术列表: [最终列表]

---

<!-- 上下文: match_pipe::no_starter::writer :: writer_plan_shared_tail -->
<!-- 小标题: ## SKILLS 推导（= 上述经历/项目技术列表的并集） -->

<!-- UID: frag-4c14f32cf3c733ba -->
[按 2-4 个类别优先组织；若为满足 14 词硬上限可扩到 5 类；任何类别不得少于 4 个技术]


---

<!-- 上下文: match_pipe::no_starter::writer :: output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-0d7028947a5e1215 -->


---

<!-- 上下文: match_pipe::no_starter::writer :: output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-a3e1cf1b85c411dc -->
*Dates*


---

<!-- 上下文: match_pipe::no_starter::writer::bytedance :: candidate_context_shared_experience -->
<!-- 小标题: ## 候选人经历框架（⚡=不可变字段，其余可由 Writer 决定） -->

<!-- UID: frag-640bb9ac2457dd72 -->


---

<!-- 上下文: match_pipe::no_starter::writer::bytedance :: candidate_context_bytedance_education_branch -->

<!-- UID: frag-58bc353880abbcf9 -->
→ ByteDance 目标岗位中，Georgia Tech CS coursework/projects 可以作为主要软件工程/硬件/机械工程证据来源，注意scope均为**非工业级**。

---

<!-- 上下文: match_pipe::no_starter::writer::bytedance :: candidate_context_shared_achievements -->
<!-- 小标题: ### 成就（融入 Summary 第3句） -->

<!-- UID: frag-72f4843c1e6d32d3 -->
- 中国国家认证围棋二段棋手，2022年度市赛第一，2023年度市赛第三

---

<!-- 上下文: match_pipe::no_starter::writer::bytedance :: candidate_context_bytedance_boundary -->
<!-- 小标题: ### ByteDance 特殊写作边界 -->

<!-- UID: frag-4d25b575d806f0d8 -->
- 不得写入或提及 TikTok / ByteDance intern 这段经历
- 目标岗位只能使用 DiDi、Temu 和 Georgia Tech CS coursework/projects 作为证据池；GT 教育主干仍按共享教育块保留，ByteDance 只是进一步加权 GT coursework/projects。

---

<!-- 上下文: match_pipe::no_starter::writer::bytedance :: writer_plan_shared_didi_temu -->
<!-- 小标题: ### Temu（junior DE，研究型/research，硬核起点，大数据管道基建/机器学习/算法模型/亿级数据分析与训练基础，无AI接触） -->

<!-- UID: frag-ba8578a7855ad73a -->
技术（core/extended tier）: [列出]
→ 此经历 bullet 将使用的完整技术列表: [最终列表]

---

<!-- 上下文: match_pipe::no_starter::writer::bytedance :: writer_plan_shared_gt_coursework -->
<!-- 小标题: ### Georgia Tech CS coursework/projects（非工业项目，最灵活，补足 SWE / systems / backend / 硬件 / 机械工程 缺口，有AI接触） -->

<!-- UID: frag-2ed3f76b561577a4 -->
必要 JD 技术（若工作经历不够自然覆盖，优先放这里）: [列出]
→ 此教育项目 bullet 将使用的完整技术列表: [最终列表]

---

<!-- 上下文: match_pipe::no_starter::writer::bytedance :: writer_plan_shared_tail -->
<!-- 小标题: ## SKILLS 推导（= 上述经历/项目技术列表的并集） -->

<!-- UID: frag-6e82dbb90612d025 -->
[按 2-4 个类别优先组织；若为满足 14 词硬上限可扩到 5 类；任何类别不得少于 4 个技术]


---

<!-- 上下文: match_pipe::no_starter::writer::bytedance :: output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-2187d889c93b9ed1 -->


---

<!-- 上下文: match_pipe::no_starter::writer::bytedance :: output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-d0bed065d1e7b7c4 -->
*Dates*


---

<!-- 上下文: match_pipe::old_match_anchor::writer :: strict_revision_system -->

<!-- UID: frag-77c09acec8667a58 -->
你是专业简历修改专家。严格按照修改指令执行，只改指出的问题，不做额外改动。直接输出修改后的完整简历 Markdown，不要附带解释。

---

<!-- 上下文: match_pipe::old_match_anchor::writer :: retarget_context -->
<!-- 小标题: ## Seed 简历 -->

<!-- UID: frag-34998d7e5a1857e8 -->
{seed_resume_md}

---

<!-- 上下文: match_pipe::old_match_anchor::writer :: output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-6e22b741202e5c50 -->


---

<!-- 上下文: match_pipe::old_match_anchor::writer :: output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-a3386007ee18834e -->
*Dates*


---

<!-- 上下文: match_pipe::old_match_anchor::writer::bytedance :: strict_revision_system -->

<!-- UID: frag-c872bd26b97a4086 -->
你是专业简历修改专家。严格按照修改指令执行，只改指出的问题，不做额外改动。直接输出修改后的完整简历 Markdown，不要附带解释。

---

<!-- 上下文: match_pipe::old_match_anchor::writer::bytedance :: retarget_context -->
<!-- 小标题: ## Seed 简历 -->

<!-- UID: frag-28c6c32e3907568f -->
{seed_resume_md}

---

<!-- 上下文: match_pipe::old_match_anchor::writer::bytedance :: output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-b8d7d210bc76579c -->


---

<!-- 上下文: match_pipe::old_match_anchor::writer::bytedance :: output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-839556a9d4ef2597 -->
*Dates*


---

<!-- 上下文: match_pipe::old_match_anchor::writer::same_company :: strict_revision_system -->

<!-- UID: frag-8f9b832b507e6711 -->
你是专业简历修改专家。严格按照修改指令执行，只改指出的问题，不做额外改动。直接输出修改后的完整简历 Markdown，不要附带解释。

---

<!-- 上下文: match_pipe::old_match_anchor::writer::same_company :: retarget_context -->
<!-- 小标题: ## Seed 简历 -->

<!-- UID: frag-a73a36c66d8a0152 -->
{seed_resume_md}

---

<!-- 上下文: match_pipe::old_match_anchor::writer::same_company :: output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-f7646ffce7b23403 -->


---

<!-- 上下文: match_pipe::old_match_anchor::writer::same_company :: output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-7c9f43bdf6d69fa4 -->
*Dates*


---

<!-- 上下文: match_pipe::old_match_anchor::writer::bytedance::same_company :: strict_revision_system -->

<!-- UID: frag-432adc9095de1c38 -->
你是专业简历修改专家。严格按照修改指令执行，只改指出的问题，不做额外改动。直接输出修改后的完整简历 Markdown，不要附带解释。

---

<!-- 上下文: match_pipe::old_match_anchor::writer::bytedance::same_company :: retarget_context -->
<!-- 小标题: ## Seed 简历 -->

<!-- UID: frag-f1d587db34f638f9 -->
{seed_resume_md}

---

<!-- 上下文: match_pipe::old_match_anchor::writer::bytedance::same_company :: output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-80f9cd14fd1e1715 -->


---

<!-- 上下文: match_pipe::old_match_anchor::writer::bytedance::same_company :: output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-fad9123414154d74 -->
*Dates*


---

<!-- 上下文: match_pipe::new_dual_channel::writer :: strict_revision_system -->

<!-- UID: frag-c1fc3549db50b79e -->
你是专业简历修改专家。严格按照修改指令执行，只改指出的问题，不做额外改动。直接输出修改后的完整简历 Markdown，不要附带解释。

---

<!-- 上下文: match_pipe::new_dual_channel::writer :: retarget_context -->
<!-- 小标题: ## Seed 简历 -->

<!-- UID: frag-b37bb99fe16e945a -->
{seed_resume_md}

---

<!-- 上下文: match_pipe::new_dual_channel::writer :: dual_channel_overlay -->
<!-- 小标题: ## Dual-channel continuity note -->

<!-- UID: frag-a363aaa572a495fc -->
- Use semantic anchor as the main skeleton. Apply company continuity only when it does not reintroduce hard gaps.

---

<!-- 上下文: match_pipe::new_dual_channel::writer :: output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-39a7ec95d86c1fae -->


---

<!-- 上下文: match_pipe::new_dual_channel::writer :: output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-c4204ef83c1ffbcd -->
*Dates*


---

<!-- 上下文: match_pipe::new_dual_channel::writer::bytedance :: strict_revision_system -->

<!-- UID: frag-6ab18a8fa122c5ef -->
你是专业简历修改专家。严格按照修改指令执行，只改指出的问题，不做额外改动。直接输出修改后的完整简历 Markdown，不要附带解释。

---

<!-- 上下文: match_pipe::new_dual_channel::writer::bytedance :: retarget_context -->
<!-- 小标题: ## Seed 简历 -->

<!-- UID: frag-100de0d4a01a33ad -->
{seed_resume_md}

---

<!-- 上下文: match_pipe::new_dual_channel::writer::bytedance :: dual_channel_overlay -->
<!-- 小标题: ## Dual-channel continuity note -->

<!-- UID: frag-3ef84c6feae1bfde -->
- Use semantic anchor as the main skeleton. Apply company continuity only when it does not reintroduce hard gaps.

---

<!-- 上下文: match_pipe::new_dual_channel::writer::bytedance :: output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-70702f94e0c3e7e2 -->


---

<!-- 上下文: match_pipe::new_dual_channel::writer::bytedance :: output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-f2c4720aeedb0271 -->
*Dates*


---

<!-- 上下文: match_pipe::new_dual_channel::writer::same_company :: strict_revision_system -->

<!-- UID: frag-d05444953bbb85ae -->
你是专业简历修改专家。严格按照修改指令执行，只改指出的问题，不做额外改动。直接输出修改后的完整简历 Markdown，不要附带解释。

---

<!-- 上下文: match_pipe::new_dual_channel::writer::same_company :: retarget_context -->
<!-- 小标题: ## Seed 简历 -->

<!-- UID: frag-8cfefa96ff6023c3 -->
{seed_resume_md}

---

<!-- 上下文: match_pipe::new_dual_channel::writer::same_company :: dual_channel_overlay -->
<!-- 小标题: ## Dual-channel continuity note -->

<!-- UID: frag-a82e9ec9d1bf2ce2 -->
- Use semantic anchor as the main skeleton. Apply company continuity only when it does not reintroduce hard gaps.

---

<!-- 上下文: match_pipe::new_dual_channel::writer::same_company :: output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-1b41ca34247f694e -->


---

<!-- 上下文: match_pipe::new_dual_channel::writer::same_company :: output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-8b923fb76f0e21b6 -->
*Dates*


---

<!-- 上下文: match_pipe::new_dual_channel::writer::bytedance::same_company :: strict_revision_system -->

<!-- UID: frag-95cc9d9d3707a478 -->
你是专业简历修改专家。严格按照修改指令执行，只改指出的问题，不做额外改动。直接输出修改后的完整简历 Markdown，不要附带解释。

---

<!-- 上下文: match_pipe::new_dual_channel::writer::bytedance::same_company :: retarget_context -->
<!-- 小标题: ## Seed 简历 -->

<!-- UID: frag-0441c39229c3d6fe -->
{seed_resume_md}

---

<!-- 上下文: match_pipe::new_dual_channel::writer::bytedance::same_company :: dual_channel_overlay -->
<!-- 小标题: ## Dual-channel continuity note -->

<!-- UID: frag-58e4865bc7cc1db0 -->
- Use semantic anchor as the main skeleton. Apply company continuity only when it does not reintroduce hard gaps.

---

<!-- 上下文: match_pipe::new_dual_channel::writer::bytedance::same_company :: output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-b5c3c06776375dcb -->


---

<!-- 上下文: match_pipe::new_dual_channel::writer::bytedance::same_company :: output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-6b8f25b8bff34ef2 -->
*Dates*


---

<!-- 上下文: match_pipe::reviewer::full :: reviewer_user -->

<!-- UID: frag-cfb66db93b5699e6 -->
请对以下简历进行严格的 9 维度审查，返回 JSON 格式结果。


---

<!-- 上下文: match_pipe::reviewer::full::bytedance :: reviewer_user -->

<!-- UID: frag-a62daf070664bbd0 -->
请对以下简历进行严格的 9 维度审查，返回 JSON 格式结果。


---

<!-- 上下文: match_pipe::reviewer::full::bytedance :: reviewer_context_bytedance -->
<!-- 小标题: ## ByteDance 特殊审查要求 -->

<!-- UID: frag-0cced9c090f66a0c -->
- 对 ByteDance 目标岗位，TikTok / ByteDance intern 这段经历必须完全不存在
- 若简历仍引用了 TikTok / ByteDance intern，视为 critical，并要求删除后仅用 DiDi / Temu / Georgia Tech CS coursework/projects 重写；GT 教育主干仍按共享材料保留

---

<!-- 上下文: match_pipe::reviewer_followup::writer :: upgrade_revision_system -->

<!-- UID: frag-7298ad0dc975bcb4 -->
你是专业简历升级专家。你可以在保持不可变字段、真实性边界和核心职业叙事不变的前提下，重写 summary、skills、experience bullets、project baseline 和项目 framing，以显著提升 JD 匹配度、scope 表达完整度和整体得分。不要被 seed phrasing、旧 summary 或旧 bullet 选择束缚；如果旧稿的 framing 本身导致失分，应主动替换成更强、更清晰、但仍真实自洽的表达。直接输出修改后的完整简历 Markdown，不要附带解释。

---

<!-- 上下文: match_pipe::reviewer_followup::writer :: upgrade_prompt -->
<!-- 小标题: ## 最优先修改事项 -->

<!-- UID: frag-a479664249ddd631 -->
  1. {priority}


---

<!-- 上下文: match_pipe::reviewer_followup::writer :: upgrade_prompt -->
<!-- 小标题: ## 审查发现 -->

<!-- UID: frag-45e5e3e195ca2ddb -->
[r0] [HIGH] {field}: {issue} → 修改建议: {fix}


---

<!-- 上下文: match_pipe::reviewer_followup::writer :: upgrade_prompt -->
<!-- 小标题: ## 必须技术 -->

<!-- UID: frag-837c6a00db36f565 -->
{tech_required}


---

<!-- 上下文: match_pipe::reviewer_followup::writer :: upgrade_prompt -->
<!-- 小标题: ## 原审查详细修改指令 -->

<!-- UID: frag-9aea3a1be69b7e5b -->
{revision_instructions}

---

<!-- 上下文: match_pipe::reviewer_followup::writer :: upgrade_context -->
<!-- 小标题: ## 原始简历 -->

<!-- UID: frag-b9aca79aaa9e8ec9 -->
{resume_md}

---

<!-- 上下文: match_pipe::reviewer_followup::writer :: output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-27efda23d778e2bc -->


---

<!-- 上下文: match_pipe::reviewer_followup::writer :: output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-4ca4ddce49cf295d -->
*Dates*


---

<!-- 上下文: match_pipe::reviewer_followup::writer::bytedance :: upgrade_revision_system -->

<!-- UID: frag-7a5110e4cf8bd3b8 -->
你是专业简历升级专家。你可以在保持不可变字段、真实性边界和核心职业叙事不变的前提下，重写 summary、skills、experience bullets、project baseline 和项目 framing，以显著提升 JD 匹配度、scope 表达完整度和整体得分。不要被 seed phrasing、旧 summary 或旧 bullet 选择束缚；如果旧稿的 framing 本身导致失分，应主动替换成更强、更清晰、但仍真实自洽的表达。直接输出修改后的完整简历 Markdown，不要附带解释。

---

<!-- 上下文: match_pipe::reviewer_followup::writer::bytedance :: upgrade_prompt -->
<!-- 小标题: ## 最优先修改事项 -->

<!-- UID: frag-4b7e96e2841fa553 -->
  1. {priority}


---

<!-- 上下文: match_pipe::reviewer_followup::writer::bytedance :: upgrade_prompt -->
<!-- 小标题: ## 审查发现 -->

<!-- UID: frag-e3ab7944767a00c9 -->
[r0] [HIGH] {field}: {issue} → 修改建议: {fix}


---

<!-- 上下文: match_pipe::reviewer_followup::writer::bytedance :: upgrade_prompt -->
<!-- 小标题: ## 必须技术 -->

<!-- UID: frag-ecf649316c180b23 -->
{tech_required}


---

<!-- 上下文: match_pipe::reviewer_followup::writer::bytedance :: upgrade_prompt -->
<!-- 小标题: ## 原审查详细修改指令 -->

<!-- UID: frag-6b6efaa8ba420007 -->
{revision_instructions}

---

<!-- 上下文: match_pipe::reviewer_followup::writer::bytedance :: upgrade_context -->
<!-- 小标题: ## 原始简历 -->

<!-- UID: frag-9c4d12fabfeef5d6 -->
{resume_md}

---

<!-- 上下文: match_pipe::reviewer_followup::writer::bytedance :: output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-399563d03798fc56 -->


---

<!-- 上下文: match_pipe::reviewer_followup::writer::bytedance :: output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-c0588df012103257 -->
*Dates*


---

<!-- 上下文: match_pipe::planner::planner :: planner_system -->

<!-- UID: frag-0f5fcbebc1bfc27c -->
你是简历流程里的 Planner。你的职责不是直接写简历，而是基于 JD、matcher 证据和可选历史简历 starter，判断：这份 starter 是否适合作为起点；是否可以直接送 Reviewer；如果需要写作，哪些内容已覆盖、哪些缺失、哪些存在真实性/ownership/scope 风险；Writer 应如何改写，优先级如何排序。

必须输出 JSON，不要输出解释性文字。不要复述 schema。

---

<!-- 上下文: match_pipe::planner::planner :: planner_user -->

<!-- UID: frag-f53346c888b1b494 -->
请作为 Planner，基于以下信息做流程决策：目标模式、目标 JD、Matcher Packet、Starter Resume。

返回 JSON，schema 必须包含 decision、fit_label、reuse_ratio_estimate、already_covered、missing_or_weak、risk_flags、role_seniority_guidance、planner_summary、writer_plan、direct_review_rationale。

规则：no_starter 模式下 decision 只能是 write；starter 高度贴合且 scope/真实性风险低时可以 direct_review；starter 语义相近但仍需改写时选择 write；starter 虽相似但会明显误导 summary、ownership、项目骨架或 scope 时选择 reject_starter；不要把 matcher 的相似度直接等同于可写作适配度。

---

<!-- 上下文: match_pipe::planner::planner :: planner_context -->
<!-- 小标题: ## Planner 输入 -->

<!-- UID: frag-00a87a2f3e15fc3e -->
- 目标模式: {mode}
- 公司: {company}
- 职位: {title}
- role_type: {role_type}
- seniority: {seniority}
- must-have 技术: {tech_required}
- preferred 技术: {tech_preferred}


---

<!-- 上下文: match_pipe::planner::planner :: planner_context -->
<!-- 小标题: ## Matcher Packet -->

<!-- UID: frag-3f181aadf5ad3327 -->
```json
{matcher_block}
```


---

<!-- 上下文: match_pipe::planner_write::writer :: candidate_context_shared_experience -->
<!-- 小标题: ## 候选人经历框架（⚡=不可变字段，其余可由 Writer 决定） -->

<!-- UID: frag-2abe0b7839a8144d -->


---

<!-- 上下文: match_pipe::planner_write::writer :: candidate_context_shared_achievements -->
<!-- 小标题: ### 成就（融入 Summary 第3句） -->

<!-- UID: frag-2b21693bb2345998 -->
- 中国国家认证围棋二段棋手，2022年度市赛第一，2023年度市赛第三

---

<!-- 上下文: match_pipe::planner_write::writer :: writer_plan_shared_didi_temu -->
<!-- 小标题: ### Temu（junior DE，研究型/research，硬核起点，大数据管道基建/机器学习/算法模型/亿级数据分析与训练基础，无AI接触） -->

<!-- UID: frag-ac1593813f9c5c19 -->
技术（core/extended tier）: [列出]
→ 此经历 bullet 将使用的完整技术列表: [最终列表]

---

<!-- 上下文: match_pipe::planner_write::writer :: writer_plan_shared_gt_coursework -->
<!-- 小标题: ### Georgia Tech CS coursework/projects（非工业项目，最灵活，补足 SWE / systems / backend / 硬件 / 机械工程 缺口，有AI接触） -->

<!-- UID: frag-ab5dcc1555e18385 -->
必要 JD 技术（若工作经历不够自然覆盖，优先放这里）: [列出]
→ 此教育项目 bullet 将使用的完整技术列表: [最终列表]

---

<!-- 上下文: match_pipe::planner_write::writer :: writer_plan_shared_tail -->
<!-- 小标题: ## SKILLS 推导（= 上述经历/项目技术列表的并集） -->

<!-- UID: frag-9774727faaa682da -->
[按 2-4 个类别优先组织；若为满足 14 词硬上限可扩到 5 类；任何类别不得少于 4 个技术]


---

<!-- 上下文: match_pipe::planner_write::writer :: output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-2bd52cacf45c8bcb -->


---

<!-- 上下文: match_pipe::planner_write::writer :: output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-542f3ce66aff5f72 -->
*Dates*


---

<!-- 上下文: match_pipe::planner_write::writer :: planner_writer_overlay -->

<!-- UID: frag-2c509080c6a7f087 -->
Planner-first Rules：如果给了 starter resume，把它视为可复用参考骨架，而不是必须保留的模板；优先遵循 planner 对 coverage、missing、risk、role-seniority framing 的判断；如果 planner 指出了 scope 或真实性风险，必须主动改写 summary、ownership 和项目 framing；如果 planner 认为 starter 可高比例复用，可保留高价值证据，但仍以目标 JD 为准。

---

<!-- 上下文: match_pipe::planner_write::writer::bytedance :: candidate_context_shared_experience -->
<!-- 小标题: ## 候选人经历框架（⚡=不可变字段，其余可由 Writer 决定） -->

<!-- UID: frag-7b35094f40fddaa8 -->


---

<!-- 上下文: match_pipe::planner_write::writer::bytedance :: candidate_context_bytedance_education_branch -->

<!-- UID: frag-4c16649848c72449 -->
→ ByteDance 目标岗位中，Georgia Tech CS coursework/projects 可以作为主要软件工程/硬件/机械工程证据来源，注意scope均为**非工业级**。

---

<!-- 上下文: match_pipe::planner_write::writer::bytedance :: candidate_context_shared_achievements -->
<!-- 小标题: ### 成就（融入 Summary 第3句） -->

<!-- UID: frag-a37f0a0028f37197 -->
- 中国国家认证围棋二段棋手，2022年度市赛第一，2023年度市赛第三

---

<!-- 上下文: match_pipe::planner_write::writer::bytedance :: candidate_context_bytedance_boundary -->
<!-- 小标题: ### ByteDance 特殊写作边界 -->

<!-- UID: frag-8cf8c9bce129c702 -->
- 不得写入或提及 TikTok / ByteDance intern 这段经历
- 目标岗位只能使用 DiDi、Temu 和 Georgia Tech CS coursework/projects 作为证据池；GT 教育主干仍按共享教育块保留，ByteDance 只是进一步加权 GT coursework/projects。

---

<!-- 上下文: match_pipe::planner_write::writer::bytedance :: writer_plan_shared_didi_temu -->
<!-- 小标题: ### Temu（junior DE，研究型/research，硬核起点，大数据管道基建/机器学习/算法模型/亿级数据分析与训练基础，无AI接触） -->

<!-- UID: frag-2410f0d7a5fe8c44 -->
技术（core/extended tier）: [列出]
→ 此经历 bullet 将使用的完整技术列表: [最终列表]

---

<!-- 上下文: match_pipe::planner_write::writer::bytedance :: writer_plan_shared_gt_coursework -->
<!-- 小标题: ### Georgia Tech CS coursework/projects（非工业项目，最灵活，补足 SWE / systems / backend / 硬件 / 机械工程 缺口，有AI接触） -->

<!-- UID: frag-1cc8f1d3e633d804 -->
必要 JD 技术（若工作经历不够自然覆盖，优先放这里）: [列出]
→ 此教育项目 bullet 将使用的完整技术列表: [最终列表]

---

<!-- 上下文: match_pipe::planner_write::writer::bytedance :: writer_plan_shared_tail -->
<!-- 小标题: ## SKILLS 推导（= 上述经历/项目技术列表的并集） -->

<!-- UID: frag-ec4646f3f3737335 -->
[按 2-4 个类别优先组织；若为满足 14 词硬上限可扩到 5 类；任何类别不得少于 4 个技术]


---

<!-- 上下文: match_pipe::planner_write::writer::bytedance :: output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-2a69e144c3c434f5 -->


---

<!-- 上下文: match_pipe::planner_write::writer::bytedance :: output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-f964e0ac1a353a2e -->
*Dates*


---

<!-- 上下文: match_pipe::planner_write::writer::bytedance :: planner_writer_overlay -->

<!-- UID: frag-e49db20fe50b4fcd -->
Planner-first Rules：如果给了 starter resume，把它视为可复用参考骨架，而不是必须保留的模板；优先遵循 planner 对 coverage、missing、risk、role-seniority framing 的判断；如果 planner 指出了 scope 或真实性风险，必须主动改写 summary、ownership 和项目 framing；如果 planner 认为 starter 可高比例复用，可保留高价值证据，但仍以目标 JD 为准。

---

<!-- 上下文: match_pipe::planner_direct_review::reviewer :: reviewer_user -->

<!-- UID: frag-5631b2eec108d700 -->
请对以下简历进行严格的 9 维度审查，返回 JSON 格式结果。


---

<!-- 上下文: match_pipe::planner_direct_review::reviewer::bytedance :: reviewer_user -->

<!-- UID: frag-9469e71256bf2497 -->
请对以下简历进行严格的 9 维度审查，返回 JSON 格式结果。


---

<!-- 上下文: match_pipe::planner_direct_review::reviewer::bytedance :: reviewer_context_bytedance -->
<!-- 小标题: ## ByteDance 特殊审查要求 -->

<!-- UID: frag-43d8de1ad65d30b2 -->
- 对 ByteDance 目标岗位，TikTok / ByteDance intern 这段经历必须完全不存在
- 若简历仍引用了 TikTok / ByteDance intern，视为 critical，并要求删除后仅用 DiDi / Temu / Georgia Tech CS coursework/projects 重写；GT 教育主干仍按共享材料保留

---

<!-- 上下文: match_pipe::planner_revision::writer :: upgrade_revision_system -->

<!-- UID: frag-c97c7788333a4c51 -->
你是专业简历升级专家。你可以在保持不可变字段、真实性边界和核心职业叙事不变的前提下，重写 summary、skills、experience bullets、project baseline 和项目 framing，以显著提升 JD 匹配度、scope 表达完整度和整体得分。不要被 seed phrasing、旧 summary 或旧 bullet 选择束缚；如果旧稿的 framing 本身导致失分，应主动替换成更强、更清晰、但仍真实自洽的表达。直接输出修改后的完整简历 Markdown，不要附带解释。

---

<!-- 上下文: match_pipe::planner_revision::writer :: candidate_context_shared_experience -->
<!-- 小标题: ## 候选人经历框架（⚡=不可变字段，其余可由 Writer 决定） -->

<!-- UID: frag-9b168ba94067ab03 -->


---

<!-- 上下文: match_pipe::planner_revision::writer :: candidate_context_shared_achievements -->
<!-- 小标题: ### 成就（融入 Summary 第3句） -->

<!-- UID: frag-45814bf6244f7bdc -->
- 中国国家认证围棋二段棋手，2022年度市赛第一，2023年度市赛第三

---

<!-- 上下文: match_pipe::planner_revision::writer :: writer_plan_shared_didi_temu -->
<!-- 小标题: ### Temu（junior DE，研究型/research，硬核起点，大数据管道基建/机器学习/算法模型/亿级数据分析与训练基础，无AI接触） -->

<!-- UID: frag-ba811a043b8565ae -->
技术（core/extended tier）: [列出]
→ 此经历 bullet 将使用的完整技术列表: [最终列表]

---

<!-- 上下文: match_pipe::planner_revision::writer :: writer_plan_shared_gt_coursework -->
<!-- 小标题: ### Georgia Tech CS coursework/projects（非工业项目，最灵活，补足 SWE / systems / backend / 硬件 / 机械工程 缺口，有AI接触） -->

<!-- UID: frag-c36637f3ce6a6a31 -->
必要 JD 技术（若工作经历不够自然覆盖，优先放这里）: [列出]
→ 此教育项目 bullet 将使用的完整技术列表: [最终列表]

---

<!-- 上下文: match_pipe::planner_revision::writer :: writer_plan_shared_tail -->
<!-- 小标题: ## SKILLS 推导（= 上述经历/项目技术列表的并集） -->

<!-- UID: frag-3dbfe5998505d17e -->
[按 2-4 个类别优先组织；若为满足 14 词硬上限可扩到 5 类；任何类别不得少于 4 个技术]


---

<!-- 上下文: match_pipe::planner_revision::writer :: output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-569a87f0e9f97580 -->


---

<!-- 上下文: match_pipe::planner_revision::writer :: output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-dd0f7d9f1eb23d97 -->
*Dates*


---

<!-- 上下文: match_pipe::planner_revision::writer :: planner_revision_context -->
<!-- 小标题: ## Planner Carry-over -->

<!-- UID: frag-ba5422b35db6bcf4 -->
{planner_notes}


---

<!-- 上下文: match_pipe::planner_revision::writer :: planner_revision_context -->
<!-- 小标题: ## Planner Risks -->

<!-- UID: frag-660467255c3b9eb7 -->
{risk_notes}


---

<!-- 上下文: match_pipe::planner_revision::writer :: planner_revision_context -->
<!-- 小标题: ## Reviewer Priority -->

<!-- UID: frag-6c1f584d695a2c95 -->
{priority}


---

<!-- 上下文: match_pipe::planner_revision::writer :: planner_revision_context -->
<!-- 小标题: ## Reviewer Findings -->

<!-- UID: frag-fe37788f3f86bbe6 -->
{findings_block}


---

<!-- 上下文: match_pipe::planner_revision::writer :: planner_revision_context -->
<!-- 小标题: ## Must-have Tech -->

<!-- UID: frag-13f5106d63060113 -->
- {must_have}


---

<!-- 上下文: match_pipe::planner_revision::writer :: planner_revision_overlay -->

<!-- UID: frag-0ccd8706b304b430 -->
Revision Rules：不要保留任何只是因为旧稿已经存在、但不再服务目标 JD 的 summary framing、ownership framing 或 bullet 结构；如果 planner 指出了 starter 的 scope、真实性、角色定位或 seniority 风险，必须优先修正；如果 reviewer 指出了 JD 缺口，优先补正文证据，而不是删除 must-have 技术；允许重写 summary、skills 分组、bullet 取舍、project baseline 和经历 framing，但不得破坏不可变字段与职业主线真实性；输出完整简历 Markdown，不要解释。

---

<!-- 上下文: match_pipe::planner_revision::writer::bytedance :: upgrade_revision_system -->

<!-- UID: frag-efbecc0ef663d263 -->
你是专业简历升级专家。你可以在保持不可变字段、真实性边界和核心职业叙事不变的前提下，重写 summary、skills、experience bullets、project baseline 和项目 framing，以显著提升 JD 匹配度、scope 表达完整度和整体得分。不要被 seed phrasing、旧 summary 或旧 bullet 选择束缚；如果旧稿的 framing 本身导致失分，应主动替换成更强、更清晰、但仍真实自洽的表达。直接输出修改后的完整简历 Markdown，不要附带解释。

---

<!-- 上下文: match_pipe::planner_revision::writer::bytedance :: candidate_context_shared_experience -->
<!-- 小标题: ## 候选人经历框架（⚡=不可变字段，其余可由 Writer 决定） -->

<!-- UID: frag-6206e5a1440cb0c4 -->


---

<!-- 上下文: match_pipe::planner_revision::writer::bytedance :: candidate_context_bytedance_education_branch -->

<!-- UID: frag-66a1286d149c23bb -->
→ ByteDance 目标岗位中，Georgia Tech CS coursework/projects 可以作为主要软件工程/硬件/机械工程证据来源，注意scope均为**非工业级**。

---

<!-- 上下文: match_pipe::planner_revision::writer::bytedance :: candidate_context_shared_achievements -->
<!-- 小标题: ### 成就（融入 Summary 第3句） -->

<!-- UID: frag-4d8faecd26b48d65 -->
- 中国国家认证围棋二段棋手，2022年度市赛第一，2023年度市赛第三

---

<!-- 上下文: match_pipe::planner_revision::writer::bytedance :: candidate_context_bytedance_boundary -->
<!-- 小标题: ### ByteDance 特殊写作边界 -->

<!-- UID: frag-91fa5768819e9e11 -->
- 不得写入或提及 TikTok / ByteDance intern 这段经历
- 目标岗位只能使用 DiDi、Temu 和 Georgia Tech CS coursework/projects 作为证据池；GT 教育主干仍按共享教育块保留，ByteDance 只是进一步加权 GT coursework/projects。

---

<!-- 上下文: match_pipe::planner_revision::writer::bytedance :: writer_plan_shared_didi_temu -->
<!-- 小标题: ### Temu（junior DE，研究型/research，硬核起点，大数据管道基建/机器学习/算法模型/亿级数据分析与训练基础，无AI接触） -->

<!-- UID: frag-d9a4748ea35cab18 -->
技术（core/extended tier）: [列出]
→ 此经历 bullet 将使用的完整技术列表: [最终列表]

---

<!-- 上下文: match_pipe::planner_revision::writer::bytedance :: writer_plan_shared_gt_coursework -->
<!-- 小标题: ### Georgia Tech CS coursework/projects（非工业项目，最灵活，补足 SWE / systems / backend / 硬件 / 机械工程 缺口，有AI接触） -->

<!-- UID: frag-c2b8d6c393553e73 -->
必要 JD 技术（若工作经历不够自然覆盖，优先放这里）: [列出]
→ 此教育项目 bullet 将使用的完整技术列表: [最终列表]

---

<!-- 上下文: match_pipe::planner_revision::writer::bytedance :: writer_plan_shared_tail -->
<!-- 小标题: ## SKILLS 推导（= 上述经历/项目技术列表的并集） -->

<!-- UID: frag-03ba1fe5c9f84632 -->
[按 2-4 个类别优先组织；若为满足 14 词硬上限可扩到 5 类；任何类别不得少于 4 个技术]


---

<!-- 上下文: match_pipe::planner_revision::writer::bytedance :: output_contract -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-9cf88d71c66060e0 -->


---

<!-- 上下文: match_pipe::planner_revision::writer::bytedance :: output_contract -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-c8eed022a105ead7 -->
*Dates*


---

<!-- 上下文: match_pipe::planner_revision::writer::bytedance :: planner_revision_context -->
<!-- 小标题: ## Planner Carry-over -->

<!-- UID: frag-48a120ca943144ca -->
{planner_notes}


---

<!-- 上下文: match_pipe::planner_revision::writer::bytedance :: planner_revision_context -->
<!-- 小标题: ## Planner Risks -->

<!-- UID: frag-e4d4129b5091929d -->
{risk_notes}


---

<!-- 上下文: match_pipe::planner_revision::writer::bytedance :: planner_revision_context -->
<!-- 小标题: ## Reviewer Priority -->

<!-- UID: frag-0760bd766d523b62 -->
{priority}


---

<!-- 上下文: match_pipe::planner_revision::writer::bytedance :: planner_revision_context -->
<!-- 小标题: ## Reviewer Findings -->

<!-- UID: frag-36da8794b35c8d8c -->
{findings_block}


---

<!-- 上下文: match_pipe::planner_revision::writer::bytedance :: planner_revision_context -->
<!-- 小标题: ## Must-have Tech -->

<!-- UID: frag-f99341c8fd2b1e9c -->
- {must_have}


---

<!-- 上下文: match_pipe::planner_revision::writer::bytedance :: planner_revision_overlay -->

<!-- UID: frag-90d1249db596bde4 -->
Revision Rules：不要保留任何只是因为旧稿已经存在、但不再服务目标 JD 的 summary framing、ownership framing 或 bullet 结构；如果 planner 指出了 starter 的 scope、真实性、角色定位或 seniority 风险，必须优先修正；如果 reviewer 指出了 JD 缺口，优先补正文证据，而不是删除 must-have 技术；允许重写 summary、skills 分组、bullet 取舍、project baseline 和经历 framing，但不得破坏不可变字段与职业主线真实性；输出完整简历 Markdown，不要解释。

---

<!-- 上下文: source_reference::inactive_builder::revision_writer :: source_reference::inactive_builder::revision_writer::user -->

<!-- UID: frag-52d1f73a533841a3 -->
请按照以下审查结果，对简历进行精准修改。
目标岗位: {title}


---

<!-- 上下文: source_reference::inactive_builder::revision_writer :: source_reference::inactive_builder::revision_writer::user -->
<!-- 小标题: ## 当前评分: 88.4/100（目标: 93 分以上） -->

<!-- UID: frag-585e3d7ce32ec9a4 -->


---

<!-- 上下文: source_reference::inactive_builder::revision_writer :: source_reference::inactive_builder::revision_writer::user -->
<!-- 小标题: ## 原始技术分配 PLAN（revision 必须遵守此规划，不得凭空引入计划外技术） -->

<!-- UID: frag-b2aac204936c4ed4 -->


---

<!-- 上下文: source_reference::inactive_builder::revision_writer :: source_reference::inactive_builder::revision_writer::user -->
<!-- 小标题: ## 最终 PLAN -->

<!-- UID: frag-828c8bfb2ed7491f -->
- 把 Python/backend 证据优先放在最相关经历中。

---

<!-- 上下文: source_reference::inactive_builder::revision_writer :: source_reference::inactive_builder::revision_writer::user -->
<!-- 小标题: ## JD 必须技术（所有必须技术均需在正文有实质使用出处） -->

<!-- UID: frag-e76552e220c2e784 -->
Python, REST APIs

---

<!-- 上下文: source_reference::inactive_builder::revision_writer :: source_reference::inactive_builder::revision_writer::user -->
<!-- 小标题: ## 最优先修改事项 -->

<!-- UID: frag-91745ac7fdcb39b9 -->
  1. 补全 Python / backend 相关正文证据
  2. 压缩泛化措辞，提升 JD 对齐度


---

<!-- 上下文: source_reference::inactive_builder::revision_writer :: source_reference::inactive_builder::revision_writer::user -->
<!-- 小标题: ## 所有 CRITICAL/HIGH 问题（必须全部修复） -->

<!-- UID: frag-0fb4e4aac866f2f5 -->
[coverage] [HIGH] Experience bullets: 缺少对 must-have 技术的直接证据 → 修改建议: 在已有经历中补出 Python / backend 实战证据


---

<!-- 上下文: source_reference::inactive_builder::revision_writer :: source_reference::inactive_builder::revision_writer::user -->
<!-- 小标题: ## 详细修改指令 -->

<!-- UID: frag-37a42f614f5a7b8a -->
补齐 JD 必须技术的正文证据，并把 summary 对齐到目标岗位。


---

<!-- 上下文: source_reference::inactive_builder::revision_writer :: source_reference::inactive_builder::revision_writer::user -->
<!-- 小标题: ## 修改原则 -->

<!-- UID: frag-bcdf059a819e2b4c -->
1. 只修改上方指出的问题，其他内容保持不变
2. 若 PLAN 已提供，技术分配须遵循 PLAN；若需在正文补充某技术，选择 PLAN 中已规划该技术的经历
3. 修复 SKILLS ↔ 正文不一致时：优先调整正文 bullet，不随意增删 SKILLS 条目
4. 对 JD must-have 技术，绝不允许通过删除来过关；必须补正文证据。仅非必须技术在确实无法自然嵌入时才可删除
5. 保持所有不可变字段（公司/职称/时间/地点）完全不变
6. 经历顺序必须保持 TikTok（2025）→ DiDi（2022-2024）→ Temu（2021-2022）
7. 修复后的简历必须满足所有格式硬约束
8. 若目标 JD 属于候选人不自然直连的行业域，优先补充 1 句 summary bridge 或 1 条 project baseline bridge，而不是硬改整段经历去假装已有该行业本体经历


---

<!-- 上下文: source_reference::inactive_builder::revision_writer :: source_reference::inactive_builder::revision_writer::user -->
<!-- 小标题: ## 原始简历 -->

<!-- UID: frag-42ab92bb0175d586 -->
{resume_md}


---

<!-- 上下文: source_reference::inactive_builder::revision_writer :: source_reference::inactive_builder::revision_writer::user -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-72bf53c7903b64eb -->


---

<!-- 上下文: source_reference::inactive_builder::revision_writer :: source_reference::inactive_builder::revision_writer::user -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-228a544dacd94769 -->
*Dates*


---

<!-- 上下文: source_reference::indirect_runtime::seed_retarget_writer :: source_reference::indirect_runtime::seed_retarget_writer::system -->

<!-- UID: frag-89696647141b8901 -->
你是专业简历修改专家。严格按照修改指令执行，只改指出的问题，不做额外改动。直接输出修改后的完整简历 Markdown，不要附带解释。

---

<!-- 上下文: source_reference::indirect_runtime::seed_retarget_writer :: source_reference::indirect_runtime::seed_retarget_writer::user -->

<!-- UID: frag-a09de24bcbe13f90 -->
你正在基于一份已经通过高标准审查的 seed resume，为新的 JD 生成派生简历。

目标：尽可能少改动，在保留 seed 叙事骨架、结构质量和可信 scope 的前提下，让简历对齐目标 JD。

当前命中的 seed: seed-placeholder
路由模式: retarget
目标岗位: {title} @ ExampleCorp

---

<!-- 上下文: source_reference::indirect_runtime::seed_retarget_writer :: source_reference::indirect_runtime::seed_retarget_writer::user -->
<!-- 小标题: ## Retarget 原则 -->

<!-- UID: frag-1325aeb82c702bbf -->
1. 这是在现有 seed 上微调，不是从零重写
2. 总改动预算控制在约 35%
3. 优先保留已成熟的 summary phrasing、经历骨架、项目结构和量化风格
4. 先改 Summary、Skills、最相关经历与对应项目，再考虑其余段落
5. 所有不可变字段（公司/部门/职称/时间/地点）必须完全不变
6. 经历顺序必须保持 TikTok（2025）→ DiDi（2022-2024）→ Temu（2021-2022）
7. 必须把 JD 必需技术写到正文里有真实使用出处，不能只堆在 SKILLS
8. 不要为了补技术而把 scope 夸大；intern/junior 一律保持 team-contributed framing
9. 若 route_mode = reuse，默认只做轻改；若 route_mode = retarget，可做中等幅度改动，但仍不得改写候选人的核心职业叙事
10. 如果目标 JD 带有行业语境（如 fintech / healthcare / security / devops），优先通过 summary 和项目业务 framing 对齐，而不是凭空新增不可信 ownership
11. 如果进入同公司一致性模式，优先复用现有 team/domain/project 骨架；把变化理解为“同项目换一种表述”，而不是“换了一套完全不同的工作内容”
12. 保留合法的 DiDi senior scope，不要把它机械压缩成 generic collaboration phrasing；是否把该 scope 提到 summary/bullet，由目标 JD 决定
13. 如果目标 JD 属于自动驾驶 / physical AI / robotics / spatial-sensor systems 等陌生行业，优先在 Summary 或项目 baseline 中写“transferable infrastructure / pipeline / reliability patterns”，不要假装已有 perception、planning、simulation 或 robotics 本体 ownership


---

<!-- 上下文: source_reference::indirect_runtime::seed_retarget_writer :: source_reference::indirect_runtime::seed_retarget_writer::user -->
<!-- 小标题: ## 目标 JD 关键信息 -->

<!-- UID: frag-00d3b0a9d4a22494 -->
- Role type: {role_type}
- Seniority: {seniority}
- Must-have tech: {tech_required}
- Preferred tech: {tech_preferred}
- 当前路由识别的主要缺口: Python



---

<!-- 上下文: source_reference::indirect_runtime::seed_retarget_writer :: source_reference::indirect_runtime::seed_retarget_writer::user -->
<!-- 小标题: ### Temu R&D -->

<!-- UID: frag-8979d02c56f0862c -->


---

<!-- 上下文: source_reference::indirect_runtime::seed_retarget_writer :: source_reference::indirect_runtime::seed_retarget_writer::user -->
<!-- 小标题: ## Professional Summary -->

<!-- UID: frag-e08f7dbf35dd1906 -->
Seed resume placeholder.


---

<!-- 上下文: source_reference::indirect_runtime::seed_retarget_writer :: source_reference::indirect_runtime::seed_retarget_writer::user -->
<!-- 小标题: ## 输出格式（header 拼写必须完全一致） -->

<!-- UID: frag-8f278e8a1d74c729 -->


---

<!-- 上下文: source_reference::indirect_runtime::seed_retarget_writer :: source_reference::indirect_runtime::seed_retarget_writer::user -->
<!-- 小标题: ### Degree | School -->

<!-- UID: frag-c935037938f150de -->
*Dates*


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->

<!-- UID: frag-5d9538cb4608483c -->
# Prompt Canonical Review

这份文档是当前运行时 prompt 的单一审阅入口。

目标：
- 让你只看一份文档就能审阅当前 prompt 体系
- 尽量把重复文本折叠成共享块
- 保留“这段/这句落到哪些 prompt、哪些文件”的映射关系
- 按接收 prompt 的角色相近度排序：`Writer -> Reviewer -> Planner -> match_pipe overlay`

边界：
- 这里覆盖“会实际喂给模型的稳定文字块”
- 数据驱动展开项不逐行内联：`build_candidate_context()`、`_format_constraints_for_company()`、`build_project_pool_prompt_block()`
- 上述数据驱动块仍在运行时进入 prompt，但其内容来自配置/索引，不是单一静态字符串


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: ## How To Use -->

<!-- UID: frag-49b66707f27e3d68 -->

如果你要改 prompt，优先只改这里的块描述与块正文，然后让我按块号回写。

推荐沟通格式：
- “改 `B-WRITER-SYS-001` 第 `S03-S06`”
- “改 `B-RETARGET-002` 的第 7 条规则”
- “把 `B-OUTPUT-002` 同时作用到所有 Writer family prompt”

---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: ## Prompt Assembly Index -->

<!-- UID: frag-e207be59ee4d1a08 -->


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: ### Writer Family -->

<!-- UID: frag-0117209293ce2d1a -->


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `P-WRITER-SYS-MAIN` -->

<!-- UID: frag-4c034691d52bd653 -->
- 角色：`Writer / 主生成`
- 运行位置：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:410)
  - [runtime/writers/master_writer.py](../runtime/writers/master_writer.py:87)
- 组装：
  - `B-WRITER-SYS-001`


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `P-WRITER-USER-MAIN` -->

<!-- UID: frag-cc45412f37c97a64 -->
- 角色：`Writer / 主生成`
- 运行位置：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:475)
- 组装：
  - `G-DATA-001` candidate context
  - `B-BYTEDANCE-CTX-001`
  - `B-WRITER-USER-001` JD header + bridge rule
  - `G-DATA-002` format constraints
  - `B-WRITER-USER-002` PLAN skeleton
  - `B-WRITER-USER-003` RESUME skeleton
  - `B-OUTPUT-002`


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `P-WRITER-SYS-REV-STRICT` -->

<!-- UID: frag-e0ca96df026192b4 -->
- 角色：`Writer / 严格修补`
- 运行位置：
  - [runtime/writers/master_writer.py](../runtime/writers/master_writer.py:38)
- 组装：
  - `B-WRITER-SYS-REV-STRICT-001`
  - `B-OUTPUT-001`


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `P-WRITER-SYS-REV-UPGRADE` -->

<!-- UID: frag-699a5d15d2a9ebda -->
- 角色：`Writer / 升级重写`
- 运行位置：
  - [runtime/writers/master_writer.py](../runtime/writers/master_writer.py:42)
- 组装：
  - `B-WRITER-SYS-REV-UPGRADE-001`
  - `B-OUTPUT-001`


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `P-WRITER-USER-REV-STRICT` -->

<!-- UID: frag-16147f4fe2ae2cfb -->
- 角色：`Writer / 严格修补`
- 运行位置：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:789)
- 组装：
  - `B-REVISION-001`
  - `B-BYTEDANCE-REV-001`
  - `B-REVISION-002`

---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `P-WRITER-USER-RETARGET` -->

<!-- UID: frag-063febaf6cf894a4 -->
- 角色：`Writer / seed retarget`
- 运行位置：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:878)
- 组装：
  - `B-RETARGET-001`
  - `B-BYTEDANCE-CTX-001`
  - `B-RETARGET-002`
  - `B-RETARGET-003`
  - `G-DATA-003` project pool block

---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `P-WRITER-USER-UPGRADE` -->

<!-- UID: frag-4ee25fc8076036e7 -->
- 角色：`Writer / 升级重写`
- 运行位置：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:973)
- 组装：
  - `B-UPGRADE-001`
  - `B-BYTEDANCE-UPGRADE-001`
  - `B-UPGRADE-002`
  - `B-OUTPUT-002`
  - `B-OUTPUT-001` 的同义收口句变体


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: ### Reviewer Family -->

<!-- UID: frag-38c20ce6e2bba23e -->


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `P-REVIEWER-SYS-MAIN` -->

<!-- UID: frag-c852d4029364a581 -->
- 角色：`Reviewer / 主审查`
- 运行位置：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:568)
  - [runtime/reviewers/unified_reviewer.py](../runtime/reviewers/unified_reviewer.py:182)
- 组装：
  - `B-REVIEWER-SYS-001`


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `P-REVIEWER-USER-MAIN` -->

<!-- UID: frag-70d8a48fc87d8f6d -->
- 角色：`Reviewer / 主审查`
- 运行位置：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:592)
- 组装：
  - `B-REVIEWER-USER-001`
  - `B-IMMUTABLE-001`
  - `B-REVIEW-SCOPE-001`
  - `B-REVIEWER-USER-002`
  - `B-REVIEWER-USER-003`


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: ### Planner Family -->

<!-- UID: frag-d922b630ce3ca49d -->


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `P-PLANNER-SYS-MAIN` -->

<!-- UID: frag-c6f9f589c2ff477f -->
- 角色：`Planner / planner-first`
- 运行位置：
  - [match_pipe/planner_validation_runner.py](../match_pipe/planner_validation_runner.py:32)
- 组装：
  - `B-PLANNER-SYS-001`


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `P-PLANNER-USER-MAIN` -->

<!-- UID: frag-afd2fb456c309825 -->
- 角色：`Planner / planner-first`
- 运行位置：
  - [match_pipe/planner_validation_runner.py](../match_pipe/planner_validation_runner.py:121)
- 组装：
  - `B-PLANNER-USER-001`


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `P-PLANNER-WRITER-OVERLAY` -->

<!-- UID: frag-a9f803c787e71928 -->
- 角色：`Writer / planner-first write`
- 运行位置：
  - [match_pipe/planner_validation_runner.py](../match_pipe/planner_validation_runner.py:194)
- 组装：
  - `P-WRITER-USER-MAIN`
  - `B-PLANNER-WRITER-OVERLAY-001`


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `P-PLANNER-REVISION-OVERLAY` -->

<!-- UID: frag-ba6d9c78f2ea8728 -->
- 角色：`Writer / planner-first revision`
- 运行位置：
  - [match_pipe/planner_validation_runner.py](../match_pipe/planner_validation_runner.py:230)
- 组装：
  - `P-WRITER-USER-MAIN`
  - `B-PLANNER-REVISION-OVERLAY-001`


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: ### match_pipe Overlay Family -->

<!-- UID: frag-f511f8e65cc6063a -->


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `P-MATCH-DUAL-CHANNEL-OVERLAY` -->

<!-- UID: frag-334515750e89b163 -->
- 角色：`Writer / dual-channel retarget`
- 运行位置：
  - [match_pipe/downstream_validation_runner.py](../match_pipe/downstream_validation_runner.py:276)
- 组装：
  - `P-WRITER-USER-RETARGET`
  - `B-MATCH-OVERLAY-001`


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: ### Test Anchor -->

<!-- UID: frag-d28c8408b4193990 -->


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `P-TEST-PROMPT-HASH-ANCHOR` -->

<!-- UID: frag-199d4202e8f1bd23 -->
- 角色：`测试，不下发模型`
- 运行位置：
  - [tests/test_prompt_merge_equivalence.py](../tests/test_prompt_merge_equivalence.py:22)
- 作用：
  - 锚定 `build_revision_prompt`
  - 锚定 `build_seed_retarget_prompt`
  - 锚定 `build_upgrade_revision_prompt`
  - 锚定 strict/upgrade revision system prompt

---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: ## Canonical Block Library -->

<!-- UID: frag-37d44dea84fb47a6 -->


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: ### Shared Output Contract -->

<!-- UID: frag-4e3d32502a8c9c39 -->


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-OUTPUT-001` -->

<!-- UID: frag-3f11942e7f80b1c9 -->
- 类型：共享单句
- 作用：所有要求“只返回 Markdown 正文”的收口句
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:152)
  - [runtime/writers/master_writer.py](../runtime/writers/master_writer.py:38)
  - [runtime/writers/master_writer.py](../runtime/writers/master_writer.py:42)
- 句子：
  - `S01` 直接输出修改后的完整简历 Markdown，不要附带解释。


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-OUTPUT-002` -->

<!-- UID: frag-bd4c2ea2a7593cf1 -->
- 类型：共享模板
- 作用：Writer family 的统一输出结构合同
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:106)
  - 被插入 `P-WRITER-USER-MAIN`
  - 被插入 `P-WRITER-USER-REV-STRICT`
  - 被插入 `P-WRITER-USER-RETARGET`
  - 被插入 `P-WRITER-USER-UPGRADE`
- 句子/条目：
  - `S01` ## 输出格式（header 拼写必须完全一致）
  - `S02` `## Professional Summary`
  - `S03` `## Skills`
  - `S04` `## Experience`
  - `S05` `## Education`
  - `S06` `## Achievements`
  - `S07` `## Experience` 不能写成 `## Professional Experience`
  - `S08` `## Skills` 不能写成 `## Technical Skills`
  - `S09` `## Achievements` 不能写成 `## Achievement`
  - `S10` 项目必须挂在对应经历下，不单独成 section
  - `S11` 只输出简历正文，不要解释、注释、分析


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: ### Shared Context Blocks -->

<!-- UID: frag-e52f9c1895eb3807 -->


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-IMMUTABLE-001` -->

<!-- UID: frag-00ba73281d5a889f -->
- 类型：共享约束块
- 作用：Reviewer prompt 的不可变字段区
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:177)
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:600)
- 说明：
  - 正文由 `TIKTOK_IMMUTABLE_LINE` / `DIDI_IMMUTABLE_LINE` / `TEMU_IMMUTABLE_LINE` 与 ByteDance 特例共同组成
  - 这里不逐字内联三条经历行；它们是单源常量


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-BYTEDANCE-CTX-001` -->

<!-- UID: frag-fb69055fe134c4c5 -->
- 类型：共享 ByteDance 特例块
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:181)
  - 插入 `P-WRITER-USER-MAIN`
  - 插入 `P-WRITER-USER-RETARGET`
- 句子：
  - `S01` ByteDance 目标岗位不得出现 TikTok / ByteDance intern
  - `S02` 证据池只允许 DiDi、Temu、Georgia Tech CS coursework/projects
  - `S03` 需要更强 SWE/system 信号时，优先抬高 GT CS 证据
  - `S04` seed 里的 TikTok / ByteDance intern 只能作弱参考，不得继承


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-BYTEDANCE-REV-001` -->

<!-- UID: frag-2557733f9e94b8ba -->
- 类型：共享 ByteDance revision 特例
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:86)
  - 插入 `P-WRITER-USER-REV-STRICT`
- 句子：
  - `S01` 删除任何 TikTok / ByteDance intern 段落、summary 提及、project baseline 或 bullets
  - `S02` 只允许从 DiDi、Temu、Georgia Tech CS coursework/projects 三类证据中重写
  - `S03` seed/旧稿中的 TikTok / ByteDance intern 是噪声，不是资产


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-BYTEDANCE-UPGRADE-001` -->

<!-- UID: frag-216856f170641841 -->
- 类型：共享 ByteDance upgrade 特例
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:91)
  - 插入 `P-WRITER-USER-UPGRADE`
- 句子：
  - `S01` 删除任何 TikTok / ByteDance intern 内容，不要把它当作可修补素材
  - `S02` 证据池仅限 DiDi、Temu、Georgia Tech CS coursework/projects
  - `S03` 若旧稿保留了 TikTok / ByteDance intern，必须推翻并重写


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: ### Writer System Blocks -->

<!-- UID: frag-5dbab64018776a99 -->


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-WRITER-SYS-001` -->

<!-- UID: frag-64f70b868e671bde -->
- 类型：Writer system
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:410)
- 段落：
  - `P01` 你是一位专业简历撰写专家，为职业转型培训公司制作教学示例简历。
  - `P02` 候选人为虚构人物，真实性只要求叙事自洽，不做现实核查。
  - `P03` 质量标准：能通过 ATS 和人工 HR 审查，综合分 93+。
  - `P04` 虚构候选人写作原则：除不可变字段外，其余工作内容可自由创作，但必须逻辑自洽。
  - `P05` PLAN 阶段允许给各段经历分配目标 JD 所需技术，不受 natural_tech 分层硬约束。
  - `P06` 工作流程必须按 `PLAN -> WRITE` 两阶段执行。
  - `P07` PLAN 阶段需完成技术分配、skills 并集、项目归属、教育保留、量化范围控制、summary 优先级控制、陌生行业桥接。
  - `P08` RESUME 阶段必须严格按 PLAN 落地，确保 SKILLS 与正文技术完全一致。
  - `P09` extended/stretch 技术在 intern/junior 里必须用参与式、受限式语气。


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-WRITER-SYS-REV-STRICT-001` -->

<!-- UID: frag-8809f2fc473ed1d6 -->
- 类型：Writer strict revision system
- 全局映射：
  - [runtime/writers/master_writer.py](../runtime/writers/master_writer.py:38)
- 句子：
  - `S01` 你是专业简历修改专家。
  - `S02` 严格按照修改指令执行，只改指出的问题，不做额外改动。
  - `S03` 复用 `B-OUTPUT-001.S01`


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-WRITER-SYS-REV-UPGRADE-001` -->

<!-- UID: frag-2dd0842d680278ea -->
- 类型：Writer upgrade revision system
- 全局映射：
  - [runtime/writers/master_writer.py](../runtime/writers/master_writer.py:42)
- 句子：
  - `S01` 你是专业简历升级专家。
  - `S02` 可在保持不可变字段、真实性边界和核心职业叙事不变前提下重写 summary、skills、experience bullets、project baseline、project framing。
  - `S03` 目标是显著提升 JD 匹配度、scope 表达完整度和整体得分。
  - `S04` 不要被 seed phrasing、旧 summary、旧 bullet 选择束缚。
  - `S05` 如果旧稿 framing 本身导致失分，应主动替换成更强但仍真实自洽的表达。
  - `S06` 复用 `B-OUTPUT-001.S01`


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: ### Writer User Blocks -->

<!-- UID: frag-69c95d46660bbc2b -->


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-WRITER-USER-001` -->

<!-- UID: frag-187b1b2b33b8bb3e -->
- 类型：主生成 prompt 的静态头部
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:493)
- 句子：
  - `S01` 输出目标 JD 的公司、岗位、角色类型、职级/资历、团队业务方向
  - `S02` 必须技术栈：SKILLS 至少覆盖所有 must-have，且必须有正文出处
  - `S03` 加分技术栈：合理选择即可，不必全含
  - `S04` OR 组：满足其一即可
  - `S05` 软性要求：列出 soft required
  - `S06` 陌生行业优先写可迁移能力桥接，不要生造直接行业 ownership


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-WRITER-USER-002` -->

<!-- UID: frag-a50aa639990806af -->
- 类型：主生成 prompt 的 PLAN 骨架
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:524)
- 条目：
  - `S01` 在 `<PLAN>` 内完成技术分配规划
  - `S02` 为各经历指定最终技术列表
  - `S03` 从经历/项目技术并集反推 skills 分类
  - `S04` 规划两个项目归属和主题
  - `S05` 规划保留哪些教育经历


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-WRITER-USER-003` -->

<!-- UID: frag-813d52d423ab3fa2 -->
- 类型：主生成 prompt 的 RESUME 骨架
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:542)
- 条目：
  - `S01` 在 `<RESUME>` 内输出完整 Markdown 简历
  - `S02` 最终结构必须满足 `B-OUTPUT-002`


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-REVISION-001` -->

<!-- UID: frag-5a82f4b6c3da0a1b -->
- 类型：strict revision 主体
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:824)
- 条目：
  - `S01` 按审查结果进行精准修改
  - `S02` 若有原始 PLAN，revision 必须遵守它，不得引入计划外技术
  - `S03` 列出最优先修改事项
  - `S04` 列出所有 critical/high 问题，必须全部修复
  - `S05` 列出详细修改指令


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-REVISION-002` -->

<!-- UID: frag-40343faee44093c9 -->
- 类型：strict revision 规则尾部
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:845)
- 规则：
  - `R01` 只修改指出的问题，其他内容保持不变
  - `R02` 若需补技术，优先去 PLAN 已规划的经历中补
  - `R03` 修复 SKILLS ↔ 正文不一致时，优先调正文，不随意删加 skills
  - `R04` 对 must-have 技术，不能通过删除过关
  - `R05` 所有不可变字段完全不变
  - `R06` 经历顺序必须保持目标公司要求
  - `R07` 修后简历必须继续满足格式硬约束
  - `R08` 陌生行业优先补 summary bridge 或 project baseline bridge


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-RETARGET-001` -->

<!-- UID: frag-d5d73b3500938f5d -->
- 类型：seed retarget 头部
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:922)
- 条目：
  - `S01` 基于已通过高标准审查的 seed resume，为新的 JD 生成派生简历
  - `S02` 目标是在保留 seed 叙事骨架、结构质量、可信 scope 的前提下最小改动对齐 JD
  - `S03` 显示命中的 seed label、route mode、目标岗位


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-RETARGET-002` -->

<!-- UID: frag-31794ab91cba45fc -->
- 类型：seed retarget 核心规则
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:932)
- 规则：
  - `R01` 这是在现有 seed 上微调，不是从零重写
  - `R02` 控制总改动预算
  - `R03` 优先保留成熟的 summary phrasing、经历骨架、项目结构、量化风格
  - `R04` 优先修改 Summary、Skills、最相关经历和对应项目
  - `R05` 不可变字段完全不变
  - `R06` 经历顺序保持目标公司规则
  - `R07` must-have 技术必须在正文有出处
  - `R08` 不要为补技术夸大 scope
  - `R09` `reuse` 默认轻改，`retarget` 可中等幅度改
  - `R10` 陌生行业优先改 summary 和项目业务 framing
  - `R11` 进入同公司一致性模式后，优先复用 team/domain/project 骨架
  - `R12` 合法的 DiDi senior scope 可以保留，不要机械压缩
  - `R13` 自动驾驶/physical AI/robotics 等陌生行业优先写 transferable infrastructure patterns


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-RETARGET-003` -->

<!-- UID: frag-4ec3baa33482fd12 -->
- 类型：同公司/同公司 ByteDance 特例块
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:900)
- 变体：
  - `V01` ByteDance 同公司 seed：只能弱参考，不得继承 TikTok/ByteDance intern 骨架
  - `V02` 非 ByteDance 同公司 seed：team/domain/project pool 视为准不可变骨架


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-UPGRADE-001` -->

<!-- UID: frag-29d8be9dca165e73 -->
- 类型：upgrade revision 头部
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:1002)
- 条目：
  - `S01` 把历史简历做成面向目标 JD 的升级式重写，而不是字面修补
  - `S02` 给出目标岗位、当前评分、历史来源
  - `S03` 升级目标是提升 JD 匹配度、summary 信号密度、scope 叙事完整度和整体逻辑自洽
  - `S04` 可以中等幅度重写，但不得破坏不可变字段和职业主线


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-UPGRADE-002` -->

<!-- UID: frag-92978ea5e63d4a2b -->
- 类型：upgrade revision 关键规则
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:1023)
- 规则：
  - `R01` Summary 必须重新评估，不默认沿用旧 phrasing
  - `R02` DiDi senior operating scope 如能增强匹配度，可提炼进 summary，但不要与 bullet 重复
  - `R03` 陌生行业优先补一条领域桥接语句
  - `R04` DiDi scope note 若保留，统一用标准句式
  - `R05` 面向 senior/stakeholder JD 时可使用全局经营评审那条 DiDi bullet
  - `R06` 上面那条 senior bullet 只在确有帮助时使用
  - `R07` Skills 既要满足格式硬约束，也要补齐正文/JD 技术
  - `R08` must-have 技术只能补正文证据，不能删除
  - `R09` 围棋 summary 句必须是高价值认知信号
  - `R10` 不可变字段完全不变
  - `R11` 经历顺序保持目标公司规则
  - `R12` 输出仍需满足全部格式硬约束
  - `R13` 如果 seed phrasing/旧 summary/旧 bullet 选择本身是失分原因，可以直接替换


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: ### Reviewer Blocks -->

<!-- UID: frag-d51ad671b1947823 -->


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-REVIEWER-SYS-001` -->

<!-- UID: frag-a080df35904dcddb -->
- 类型：Reviewer system
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:568)
- 段落：
  - `P01` 你是一位严格的简历质量审查专家，负责 9 维度综合评分
  - `P02` 审查是最终裁决，直接决定能否作为教学示例发布
  - `P03` 反馈必须具体、可操作
  - `P04` 综合加权分 < 93 必须修改
  - `P05` 审查目标不是现实核验，而是模拟 ATS + 招聘方人工初筛
  - `P06` 虚构候选人的真实性只锚定不可变字段、技能出处一致性、时间线自洽、scope 与量化可信度
  - `P07` 不要因“现实里这个职称通常不做该技术”直接扣分
  - `P08` 只有叙事自证不足、HR 很可能质疑时才提出问题
  - `P09` 跨领域接触技术本身允许，重点审查“是否讲圆”
  - `P10` 只保留真正影响 ATS 或 HR 信任的高信号发现
  - `P11` 每个维度最多 2 条 finding，不写“无需修改”
  - `P12` 无 critical/high 时，综合分通常应落在 93-97，而不是机械打低
  - `P13` 默认 fix 尽量局部、低扰动
  - `P14` 但当 seed phrasing/旧骨架束缚了 JD 信号时，必须允许结构性重写
  - `P15` 对 must-have 技术，fix 方向只能是补正文证据，不是删除


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-REVIEW-SCOPE-001` -->

<!-- UID: frag-bfb838a01583958f -->
- 类型：review scope note 族
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:61)
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:69)
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:81)
- 变体：
  - `V01` compact 审查：只保留 summary / skills / 关键经历 / 关键 bullets / projects，不因未展示内容臆测扣分
  - `V02` rewrite 审查：职责是判断如何跨过 pass 线，而不是给保守补丁单
  - `V03` ByteDance 审查：若出现 TikTok / ByteDance intern，直接 critical


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-REVIEWER-USER-001` -->

<!-- UID: frag-97d2ff74fab507b6 -->
- 类型：Reviewer user 头部
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:603)
- 条目：
  - `S01` 对以下简历进行严格 9 维度审查，返回 JSON
  - `S02` 列出目标 JD 的公司、岗位、角色类型、职级、must-have、preferred、team direction
  - `S03` 列出不可变字段块
  - `S04` 插入 scope note
  - `S05` 插入待审查简历正文


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-REVIEWER-USER-002` -->

<!-- UID: frag-4387e455e43a87eb -->
- 类型：Reviewer rubric 主体
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:619)
- 维度：
  - `R0` 真实性：不可变字段、中文字符、SKILLS ↔ 正文一致性、Summary 一致性、DiDi 特例、ByteDance/TikTok 特例
  - `R1` 撰写规范：summary 句数/标题格式、围棋句 header、bullet 格式、加粗规则、skills 行密度、project baseline、achievements section
  - `R2` JD 适配：must-have 技术覆盖、正文实质使用、team direction 对齐、局部补强优先、领域桥接允许
  - `R3` 炫技：ownership/动词强度、TikTok intern 夸大、Temu junior 夸大、stretch 技术可信度
  - `R4` 合理性：转行故事、项目合理性、数字可信、跨职能 scope 自证、Summary framing、陌生行业桥接
  - `R5` 逻辑：经历顺序、skills 分类、技术栈差异化、经历内逻辑、Summary 归纳准确性
  - `R6` 竞争力：量化数据、项目亮点、Summary 转岗叙事竞争力


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-REVIEWER-USER-003` -->

<!-- UID: frag-b6cb8e423a396a67 -->
- 类型：Reviewer JSON schema + calibration
- 全局映射：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:721)
- 条目：
  - `S01` 严格输出 JSON，不得额外文字
  - `S02` schema 必须包含各维度分数、加权分、overall verdict、critical/high 计数、needs_revision、revision_priority、revision_instructions
  - `S03` 给出 9.5-10 / 9.0-9.4 / 8.0-8.9 / 7.0-7.9 / <7 的评分档
  - `S04` 说明高分校准：无 critical/high 且 JD 必需技术完整覆盖时，应优先落在 93+


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: ### Planner Blocks -->

<!-- UID: frag-01157b8cf26885c1 -->


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-PLANNER-SYS-001` -->

<!-- UID: frag-2b2eb1228c3392ac -->
- 类型：Planner system
- 全局映射：
  - [match_pipe/planner_validation_runner.py](../match_pipe/planner_validation_runner.py:32)
- 句子：
  - `S01` 你是简历流程里的 Planner，不直接写简历
  - `S02` 基于 JD、matcher 证据和可选 starter 判断 starter 是否合适
  - `S03` 判断是否可直接送 reviewer
  - `S04` 判断 coverage、缺口、真实性/ownership/scope 风险
  - `S05` 判断 Writer 应如何改写、优先级如何排序
  - `S06` 必须输出 JSON，不要解释性文字，不要复述 schema


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-PLANNER-USER-001` -->

<!-- UID: frag-bab5603c64af15a3 -->
- 类型：Planner user
- 全局映射：
  - [match_pipe/planner_validation_runner.py](../match_pipe/planner_validation_runner.py:121)
- 条目：
  - `S01` 基于 mode、JD、matcher packet、starter resume 做流程决策
  - `S02` 返回 schema 必须包含 `decision / fit_label / reuse_ratio_estimate / already_covered / missing_or_weak / risk_flags / role_seniority_guidance / planner_summary / writer_plan / direct_review_rationale`
  - `S03` `no_starter` 模式下 decision 只能是 `write`
  - `S04` starter 高度贴合且风险低可 `direct_review`
  - `S05` starter 语义相近但需改写则 `write`
  - `S06` starter 虽相似但会误导 summary / ownership / 项目骨架 / scope 时 `reject_starter`
  - `S07` 不要把 matcher 相似度直接等同于可写作适配度


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-PLANNER-WRITER-OVERLAY-001` -->

<!-- UID: frag-b69aab63b7da507f -->
- 类型：planner-first writer overlay
- 全局映射：
  - [match_pipe/planner_validation_runner.py](../match_pipe/planner_validation_runner.py:194)
- 条目：
  - `S01` 在 `P-WRITER-USER-MAIN` 之后追加 planner decision JSON
  - `S02` 追加 matcher evidence JSON
  - `S03` 追加 historical starter resume
  - `S04` 若给了 starter，把它视为可复用骨架，不是必须保留的模板
  - `S05` 优先遵循 planner 对 coverage / missing / risk / role-seniority framing 的判断
  - `S06` planner 指出 scope/真实性风险时，必须主动改写 summary、ownership、project framing
  - `S07` planner 认为 starter 可高比例复用时，可保留高价值证据，但仍以目标 JD 为准


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-PLANNER-REVISION-OVERLAY-001` -->

<!-- UID: frag-75455111791044c1 -->
- 类型：planner-first revision overlay
- 全局映射：
  - [match_pipe/planner_validation_runner.py](../match_pipe/planner_validation_runner.py:230)
- 条目：
  - `S01` 在 `P-WRITER-USER-MAIN` 之后追加 planner carry-over、planner risks、reviewer priority、reviewer findings、must-have tech、当前草稿
  - `S02` 当前目标不是保留旧稿，而是基于 reviewer 与 planner 判断把简历提到更稳的 pass
  - `S03` 不要保留任何只是因为旧稿已存在、但不再服务目标 JD 的 summary framing、ownership framing、bullet 结构
  - `S04` planner 指出了 scope / 真实性 / 角色定位 / seniority 风险时必须优先修正
  - `S05` reviewer 指出 JD 缺口时，优先补正文证据，而不是删除 must-have 技术
  - `S06` 允许重写 summary、skills 分组、bullet 取舍、project baseline、经历 framing，但不得破坏不可变字段与职业主线真实性
  - `S07` 输出完整 Markdown，不要解释


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: ### match_pipe Overlay Blocks -->

<!-- UID: frag-3a353b759b741644 -->


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `B-MATCH-OVERLAY-001` -->

<!-- UID: frag-028137a43223d4ab -->
- 类型：dual-channel continuity overlay
- 全局映射：
  - [match_pipe/downstream_validation_runner.py](../match_pipe/downstream_validation_runner.py:276)
- 句子：
  - `S01` `## Dual-channel continuity note`
  - `S02` 逐行插入 `delta_summary`
  - `S03` 若 continuity anchor 存在，插入其公司、标题与 `reuse_readiness`
  - `S04` `Use semantic anchor as the main skeleton. Apply company continuity only when it does not reintroduce hard gaps.`


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: ### Generated Source-Owned Blocks -->

<!-- UID: frag-d5ba308bf04b9962 -->


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `G-DATA-001` -->

<!-- UID: frag-5ef817f4a28d9305 -->
- 类型：数据驱动 candidate context
- 来源：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:326)
- 说明：
  - 文字框架在这里，但公司、部门、自然技术栈、教育条目由配置展开
  - 如果你要统一改“候选人经历框架”这层文案，改这里


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `G-DATA-002` -->

<!-- UID: frag-1aa8e4b30dd6b73b -->
- 类型：数据驱动 format constraints
- 来源：
  - [runtime/core/prompt_builder.py](../runtime/core/prompt_builder.py:228)
- 说明：
  - 是 Writer/Revision/Upgrade 的大块硬约束来源
  - 当前仍是单源，无重复文本问题


---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: #### `G-DATA-003` -->

<!-- UID: frag-978efb3489a8cfe5 -->
- 类型：数据驱动 project pool block
- 来源：
  - [runtime/automation/project_pool.py](../runtime/automation/project_pool.py:174)
- 说明：
  - 只进入 `P-WRITER-USER-RETARGET`
  - 若你要统一改项目池提示语，只改这里

---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: ## Short Edit Rules -->

<!-- UID: frag-55d81fa18d33aa81 -->

- 改 Writer 主生成气质：先看 `B-WRITER-SYS-001`，再看 `B-WRITER-USER-001/002/003`
- 改 strict/upgrade 修稿行为边界：先看 `B-WRITER-SYS-REV-STRICT-001` / `B-WRITER-SYS-REV-UPGRADE-001`，再看 `B-REVISION-002` / `B-UPGRADE-002`
- 改 retarget/reuse 行为：先看 `B-RETARGET-002`，再看 `B-RETARGET-003` 和 `G-DATA-003`
- 改审查标准：先看 `B-REVIEWER-SYS-001`，再看 `B-REVIEWER-USER-002/003`
- 改 planner-first 行为：先看 `B-PLANNER-SYS-001`，再看 `B-PLANNER-USER-001` / `B-PLANNER-WRITER-OVERLAY-001` / `B-PLANNER-REVISION-OVERLAY-001`
- 改所有 Writer 结尾输出要求：只改 `B-OUTPUT-001` 或 `B-OUTPUT-002`

---

<!-- 上下文: source_reference::doc::prompt_canonical_review :: source_reference::doc::prompt_canonical_review::document -->
<!-- 小标题: ## Test Guardrail -->

<!-- UID: frag-b1a74df882aa33d8 -->

修改以下块后，必须同步复核：
- `B-WRITER-SYS-REV-STRICT-001`
- `B-WRITER-SYS-REV-UPGRADE-001`
- `B-REVISION-001`
- `B-RETARGET-001`
- `B-UPGRADE-001`

对应测试：
- [tests/test_prompt_merge_equivalence.py](../tests/test_prompt_merge_equivalence.py:22)

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->

<!-- UID: frag-ef04dc9b63343f1c -->
# Match Pipe Prompt Review

这份文档只服务 `match_pipe`，并且从现在开始把它当成唯一人工审阅入口。

目标：
- 让你用“改自然语言段落”的方式审稿
- 每段都能映射回正确代码位置
- 优先展开 `match_pipe` 真正会吃到的 prompt
- 不再用抽象块号隐藏正文
- 你之后只改这一份，我负责映射回所有正确代码位置

怎么提修改：
- “改 `MP-03` 第 2 段”
- “改 `MP-06` 的规则 7-9”
- “删掉 `MP-08` 最后一段”

我收到后会负责把这些修改回写到所有正确位置。

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## Scope -->

<!-- UID: frag-0760e3b7e2f63446 -->

`match_pipe` 当前实际会吃到的 prompt，分成六类：
- 上游共享 candidate context / format constraints
- 上游共享 Writer prompt
- 上游共享 Reviewer prompt
- 上游共享 retarget / upgrade prompt
- `match_pipe` 自己的 Planner prompt
- `match_pipe` 自己追加的 overlay prompt

其中：
- `build_master_writer_prompt()` 是 `match_pipe` 的上游 Writer user prompt
- `build_candidate_context()` 和 `_format_constraints_for_company()` 会被拼进 `build_master_writer_prompt()`
- `MASTER_WRITER_SYSTEM` 是 `match_pipe` 的上游 Writer system prompt
- `build_unified_review_prompt()` / `UNIFIED_REVIEWER_SYSTEM` 是 `match_pipe` 的上游 Reviewer prompt
- `build_seed_retarget_prompt()` / `build_upgrade_revision_prompt()` 会被 `downstream_validation_runner.py` 直接复用
- `PLANNER_SYSTEM` / `_planner_prompt()` / `_writer_prompt_from_planner()` / `_writer_revision_prompt()` 是 `match_pipe` 自己的 prompt
- `Dual-channel continuity note` 是 `match_pipe` 自己的 downstream overlay

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## MP-01 Writer System Prompt -->

<!-- UID: frag-b17a9b8e4378e98f -->
- [runtime/core/prompt_builder.py:410](../runtime/core/prompt_builder.py:410)

---

<!-- UID: frag-afc1c071fa19bc99 -->
你是一位专业简历撰写专家，为一家职业转型培训公司制作教学示例简历。该候选人为虚构人物，正在从数据分析向软件工程转型。简历的「真实性」由自身逻辑自洽体现，而非由经历或技术栈的现实核查来锚定。

第 2 段  
你的输出质量标准：能够通过真实公司 ATS 系统和人工 HR 审查，在 9 大维度综合评分 93 分以上。

第 3 段  
虚构候选人写作原则（最重要）：候选人为虚构的培训示例人物，不可变字段仅为公司名、部门、职称、时间、地点。其余所有工作内容，包括技术选型、项目故事、量化成果，均可自由创作；判断标准不是“候选人真实经历了这个吗”，而是“这段叙事在该角色/时间/规模下逻辑自洽吗”。

第 4 段  
在 PLAN 阶段，可以并且应该为不同经历分配目标 JD 所需的任意技术，只要叙事在该职级和业务规模下合理即可；extended/stretch 层级只是叙事工作量提示，不是硬约束。

第 5 段  
工作流程必须按两阶段完成：先 PLAN，再 WRITE。

第 6 段  
PLAN 阶段必须完成技术分配、Skills 并集推导、项目归属、教育选择、量化数字范围控制、summary 信号排序、陌生行业桥接策略。

第 7 段  
RESUME 阶段必须严格按 PLAN 输出，确保 SKILLS 与正文技术完全一致。

第 8 段  
对 extended/stretch 技术，尤其是 intern/junior 经历中的云基础设施和 GenAI 技术，必须使用参与式、受限式语气，例如 contributing to / integrating with / within a team-maintained service；禁止写成 architected / built from scratch 这种主建式口吻。

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## MP-02 Writer User Prompt: JD Header + PLAN / RESUME Skeleton -->

<!-- UID: frag-f817bde4053bfb7a -->
- [runtime/core/prompt_builder.py:475](../runtime/core/prompt_builder.py:475)

---

<!-- UID: frag-9a154ae68743a292 -->
先给出目标 JD 信息：公司、岗位、角色类型、职级/资历、团队业务方向。

第 2 段  
必须技术栈：SKILLS 中至少覆盖所有 JD 必须项，且必须有正文出处。

第 3 段  
加分技术栈：合理选择即可，不必全部包含。

第 4 段  
OR 组：满足其一即可。

第 5 段  
软性要求：列出 soft required。

第 6 段  
领域桥接提示：如果团队业务方向涉及陌生行业，如自动驾驶、物理 AI、机器人、传感器系统、空间数据系统，优先使用“可迁移能力”桥接，例如 infrastructure-grade pipeline patterns transferable to spatial and sensor-data systems，不要生造直接行业 ownership。

第 7 段  
阶段一是 PLAN，只在 `<PLAN>` 标签内完成技术分配规划、SKILLS 推导、项目规划、教育经历选择。

第 8 段  
阶段二是 RESUME，只在 `<RESUME>` 标签内输出完整 Markdown 简历。

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## MP-02A Candidate Context Template -->

<!-- UID: frag-1a5db63c48be1746 -->
- [runtime/core/prompt_builder.py:326](../runtime/core/prompt_builder.py:326)

说明：
- 这是 `build_master_writer_prompt()` 的前置大块
- 它按目标公司动态展开，但自然语言结构是固定的

正文模板：

第 1 段  
标题固定为：`## 候选人经历框架（⚡=不可变字段，其余可由 Writer 决定）`

第 2 段  
对每段经历，都会列出：公司、部门、职称、时间、地点、时长、级别。

第 3 段  
对每段经历，都会列出：禁用动词、允许动词、scope 上限。

第 4 段  
如果该经历存在 leadership 设定，会额外列出：团队规模、跨职能构成、全球汇报、决策传导。

第 5 段  
对每段经历，都会列出自然技术栈分层：core、extended、stretch。

第 6 段  
教育经历模板会列出：学位、学校、时间，以及“保留当/可省略当”的条件。

第 7 段  
最后会列出成就模块，要求围棋成就融入 Summary 第 3 句。

第 8 段  
如果目标公司是 ByteDance，还会额外插入：不得写入 TikTok / ByteDance intern，只能使用 DiDi、Temu、Georgia Tech CS coursework/projects 作为证据池。

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## MP-03 Shared Format Constraints -->

<!-- UID: frag-2d367089b52849cc -->
- `match_pipe` 中所有复用 `build_master_writer_prompt()` 的路径

代码位置：
- [runtime/core/prompt_builder.py:248](../runtime/core/prompt_builder.py:248)

这是你刚才指出被我折叠掉、但实际非常重要的一块。

---

<!-- UID: frag-a9b8e5a82b2cc316 -->
格式硬约束：违反直接 FAIL。

第 2 段  
结构规则：Summary 必须恰好 3 句；Experience 必须严格倒序；每段经历必须满足 bullet 数和量化要求；项目数量固定；项目必须跟在对应经历下；项目标题下必须有 blockquote 背景行。

第 3 段  
DiDi scope note 若出现，必须是简短身份说明，不承担全部 leadership/decision story；推荐统一写法为：  
`> Data lead within a **13-person** cross-functional squad spanning product, backend, frontend, mobile, and ops.`

第 4 段  
`SKILLS 一致性规则（最重要）`：SKILLS 优先分 2-4 个类别；如为满足行宽约束可扩到 5 类。

第 5 段  
不允许出现孤行：单个 Skills 类别少于 4 个技术栈必须合并到相邻类别。

第 6 段  
每行（含类别标题）总词数必须小于等于 14；这是硬性标准，超过即 FAIL。

第 7 段  
SKILLS 中只有分类标题使用加粗，分类内技术栈一律纯文本逗号分隔，不要给单个技术栈加粗。

第 8 段  
SKILLS 中每个技术栈必须在至少一条经历 bullet 或项目 bullet 中出现；正文 bullet 中出现的每个技术栈也必须在 SKILLS 中出现；Summary 中提及的技术栈也必须在 SKILLS 中。

第 9 段  
禁止 SKILLS 中出现正文没有的技术栈；即便是 JD 要求的技术，也不能只堆在 SKILLS 里。

第 10 段  
对目标 JD 的 must-have 技术，不允许通过删除 SKILLS 或 Summary 中该技术来规避问题；必须在正文补足实质使用证据。

第 11 段  
内容规则：每条 bullet 都要满足强动词开头 + 技术实现 + 业务/量化结果（XYZ 格式）。

第 12 段  
加粗规则必须精确执行：技术栈名词、量化数字、业务实体名词要加粗；修饰语、限定词、纯结构词不能乱加粗。

第 13 段  
所有 bullet 以英文句号结尾；禁止词必须回避；跨经历 bullet 结构不能机械重复。

第 14 段  
不可变字段绝不可修改。

第 15 段  
职级 scope 规则：TikTok intern 禁用 Led/Architected/Drove/Spearheaded/Managed；DiDi 可以使用 Led/Coordinated/Drove 并展示 13 人跨职能团队领导力；Temu junior 仅体现 individual contributor 贡献。

第 16 段  
数字合理性规则：改善幅度过高时必须加范围限定语；规模数字必须带来源限定；单条 bullet 中不要堆叠过多量化数字。

第 17 段  
围棋成就必须进入 Summary 第 3 句，且 header 必须是高价值认知信号，不能写成 Collaboration、Teamwork、Problem Solver 一类低信号标题。

第 18 段  
Achievements section 必须固定格式，且 header 必须是 `## Achievements`。

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## MP-03A Output Contract -->

<!-- UID: frag-9e1418328c85a0e7 -->

代码位置：
- [runtime/core/prompt_builder.py:106](../runtime/core/prompt_builder.py:106)
- [runtime/core/prompt_builder.py:152](../runtime/core/prompt_builder.py:152)

---

<!-- UID: frag-86a556b8752abeaa -->
输出格式固定包含：Professional Summary、Skills、Experience、Education、Achievements。

第 2 段  
Header 拼写必须完全一致：`## Experience` 不能写成 `## Professional Experience`，`## Skills` 不能写成 `## Technical Skills`，`## Achievements` 不能写成别的变体。

第 3 段  
项目必须挂在对应经历下，不单独成 section。

第 4 段  
只输出简历正文，不要解释、注释、分析。

第 5 段  
修稿类 prompt 的统一收口句是：直接输出修改后的完整简历 Markdown，不要附带解释。

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## MP-04 Reviewer System Prompt -->

<!-- UID: frag-0c3e69395b2ba19e -->
- [runtime/core/prompt_builder.py:568](../runtime/core/prompt_builder.py:568)

---

<!-- UID: frag-335efec346d2642f -->
你是一位严格的简历质量审查专家，负责对简历进行 9 个维度的综合评分。你的评审是最终裁决，直接决定该简历是否可以作为教学示例材料发布。你的反馈将直接用于修改，因此必须具体、可操作。

第 2 段  
评分标准：每个维度 0-10 分。综合加权分小于 93 必须修改。

第 3 段  
审查目标不是做现实世界履历核验，而是模拟 ATS + 招聘方人工初筛：候选人为虚构教学示例人物，真实性只锚定不可变字段、技能出处一致性、时间线自洽、scope 与量化的叙事可信度。

第 4 段  
不要因为“现实里这个职称通常不做该技术”而直接扣分。只有当简历自身没有提供足够的业务背景、ownership 限定语、cross-functional 解释或时间范围说明，导致 HR 很可能产生质疑时，才作为问题提出。

第 5 段  
跨领域接触技术栈本身是允许的，重点审查“是否被讲圆”。

第 6 段  
只保留会真实影响 ATS 或 HR 信任的高信号发现；每个维度最多返回 2 条 findings；不要写“无需修改”或纯正向表扬。

第 7 段  
若全篇无 critical/high，仅剩少量 medium/low 级润色问题，则综合分通常应在 93-97 区间，而不是机械压在 80 多分。

第 8 段  
默认 fix 建议应尽量局部、可执行、低扰动。

第 9 段  
但当简历虽然真实、却明显被 seed phrasing、弱 framing 或旧骨架束缚，导致 JD 信号不足时，必须明确允许结构性重写。

第 10 段  
对 JD must-have 技术，fix 方向一律是补正文证据并保持技能保留，不是删除。

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## MP-05 Reviewer User Prompt -->

<!-- UID: frag-1c785833a2427fee -->
- [runtime/core/prompt_builder.py:592](../runtime/core/prompt_builder.py:592)

---

<!-- UID: frag-e69196b034e9d549 -->
请对以下简历进行严格的 9 维度审查，返回 JSON 格式结果。

第 2 段  
先给出目标 JD：公司、岗位、角色类型、职级、必须技术栈、加分技术栈、团队方向。

第 3 段  
再给出不可变字段块，要求与之完全一致。

第 4 段  
根据模式插入 scope note：compact、rewrite、ByteDance 特例。

第 5 段  
然后插入待审查简历正文。

第 6 段  
后面是一整套评分 rubric，覆盖真实性、撰写规范、JD 适配、炫技、合理性、逻辑、竞争力，以及严格 JSON 输出 schema。

如果你后面要直接改 reviewer 评分口径，我建议先只改：
- 第 1-5 段的 framing
- rubric 中你最关心的那一维
- 最后的 JSON 输出约束

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## MP-05A Reviewer Rubric -->

<!-- UID: frag-22cd10df77ff796e -->
- [runtime/core/prompt_builder.py:620](../runtime/core/prompt_builder.py:620)

---

<!-- UID: frag-732a9a72cce14f2a -->
`R0 真实性审查`：检查不可变字段、TikTok/ByteDance 特例、中文字符、SKILLS ↔ 正文一致性、Summary 与正文一致性，以及 DiDi senior scope 是否被误判。

第 2 段  
`R1 撰写规范审查`：检查 Summary 句数和 header、围棋句位置、经历和项目 bullet 数、XYZ 格式、加粗规则、SKILLS 行密度、project baseline、Achievements section。

第 3 段  
`R2 JD 适配审查`：检查 must-have 技术是否都进入 SKILLS，且是否在正文有实质使用；必须优先建议补正文证据，而不是删除技术；允许通过领域桥接语言满足陌生行业适配。

第 4 段  
`R3 炫技审查`：检查 ownership 和动词强度是否超出经历可解释范围；TikTok intern 是否过度 senior；Temu junior 是否越级；stretch 技术是否被合理限定。

第 5 段  
`R4 合理性审查`：检查转行故事、项目合理性、量化数字可信度、跨职能 scope 是否完成自证、Summary 是否先给出高价值信号，以及陌生行业桥接是否成立。

第 6 段  
`R5 逻辑审查`：检查经历倒序、SKILLS 分类逻辑、标题信息量、技术分布是否差异化、经历内 bullet 是否连贯、Summary 是否准确归纳。

第 7 段  
`R6 竞争力审查`：检查量化数据区分度、项目亮点、Summary 的转岗叙事竞争力。

第 8 段  
输出格式必须是严格 JSON，包含各维度 score、weight、verdict、findings，以及 weighted_score、overall_verdict、critical_count、high_count、needs_revision、revision_priority、revision_instructions。

第 9 段  
评分校准要求：如果 0 critical 且 0 high，并且 JD 必需技术完整覆盖、转岗叙事自洽，综合分应优先落在 93+，除非存在会显著影响 HR 信任的中等级结构问题。

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## MP-05B Reviewer Scope Notes -->

<!-- UID: frag-c2e0def983e31e34 -->
- [runtime/core/prompt_builder.py:61](../runtime/core/prompt_builder.py:61)
- [runtime/core/prompt_builder.py:69](../runtime/core/prompt_builder.py:69)
- [runtime/core/prompt_builder.py:81](../runtime/core/prompt_builder.py:81)

---

<!-- UID: frag-e920f1d08c00092f -->
`compact` 审查模式：只保留 Summary、Skills、关键 experiences、DiDi scope、以及最相关 bullets/projects；除非 excerpt 已暴露系统性问题，否则不要因为没展示某段就臆测扣分。

第 2 段  
`rewrite` 审查模式：职责不是给保守补丁单，而是判断怎样跨过 pass 线；可以建议重写 Summary、Skills、最相关 experiences、project baseline、bullet 取舍与叙事顺序。

第 3 段  
ByteDance 特例：ByteDance 目标岗位中，TikTok / ByteDance intern 必须完全不存在；若仍出现，视为 critical。

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## MP-05C Strict Revision Prompt -->

<!-- UID: frag-b4ac5aa07b5189ac -->

角色：
- Revision Writer

代码位置：
- [runtime/core/prompt_builder.py:789](../runtime/core/prompt_builder.py:789)

说明：
- `match_pipe` 目前主流程里更常用 upgrade revision，但 strict revision 仍属于同一族共享 prompt

---

<!-- UID: frag-f12fa8df1c84f769 -->
按审查结果对简历进行精准修改。

第 2 段  
如果提供了原始技术分配 PLAN，revision 必须遵守它，不得引入计划外技术。

第 3 段  
列出当前评分、最优先修改事项、所有 critical/high 问题、详细修改指令。

第 4 段  
修改原则：只修改指出的问题；补技术时优先去 PLAN 已规划的经历；修复 SKILLS ↔ 正文不一致时优先调整正文；对 must-have 技术绝不允许通过删除过关；所有不可变字段不变；输出仍需满足全部格式硬约束。

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## MP-05D Retarget Prompt -->

<!-- UID: frag-3b060870f85e97a2 -->

角色：
- Retarget Writer

---

<!-- UID: frag-464376f8ff0af8a6 -->
- [runtime/core/prompt_builder.py:878](../runtime/core/prompt_builder.py:878)

---

<!-- UID: frag-0fdc5c44d7500c69 -->
你正在基于一份已经通过高标准审查的 seed resume，为新的 JD 生成派生简历。

第 2 段  
目标是在保留 seed 叙事骨架、结构质量和可信 scope 的前提下尽可能少改动，让简历对齐目标 JD。

第 3 段  
会显示当前命中的 seed、路由模式、目标岗位。

第 4 段  
Retarget 原则：这是在现有 seed 上微调，不是从零重写；控制总改动预算；优先保留成熟的 summary phrasing、经历骨架、项目结构和量化风格；先改 Summary、Skills、最相关经历与对应项目。

第 5 段  
所有不可变字段必须完全不变；经历顺序必须保持；JD 必需技术必须写到正文里有真实使用出处；不要为了补技术夸大 scope。

第 6 段  
`reuse` 默认轻改，`retarget` 可做中等幅度改动，但仍不得改写候选人的核心职业叙事。

第 7 段  
如果目标 JD 带有行业语境，优先通过 summary 和项目业务 framing 对齐，而不是凭空新增不可信 ownership。

第 8 段  
如果进入同公司一致性模式，优先复用现有 team/domain/project 骨架，把变化理解为“同项目换一种表述”，而不是“换了一套完全不同的工作内容”。

第 9 段  
保留合法的 DiDi senior scope，不要机械压缩成 generic collaboration phrasing。

第 10 段  
如果目标 JD 属于自动驾驶、physical AI、robotics、spatial-sensor systems 等陌生行业，优先在 Summary 或项目 baseline 中写 transferable infrastructure / pipeline / reliability patterns，不要假装已有 perception、planning、simulation 或 robotics 本体 ownership。

第 11 段  
后面会给出目标 JD 关键信息、同公司模式块、project pool block、seed 简历，以及统一输出结构合同。

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## MP-05E Upgrade Revision Prompt -->

<!-- UID: frag-15dfbf80dea2c2f7 -->

角色：
- Upgrade Revision Writer
- `match_pipe` reviewer 后续重写

代码位置：
- [runtime/core/prompt_builder.py:973](../runtime/core/prompt_builder.py:973)

---

<!-- UID: frag-e86bcfde671729dd -->
请把下面这份历史简历做一次面向目标 JD 的升级式重写，而不是仅做字面修补。

第 2 段  
会显示目标岗位、当前评分、历史来源。

第 3 段  
升级目标：提高 JD 匹配度、summary 信号密度、scope 叙事完整度和整体逻辑自洽；修复 reviewer 指出的所有问题；如果当前版本对 senior 价值表达偏弱，可以重写 summary、Skills、DiDi bullets、项目 framing；允许中等幅度重写，但不得破坏不可变字段和职业故事主线。

第 4 段  
会列出最优先修改事项、审查发现、必须技术，以及历史 PLAN / 技术分配参考。

第 5 段  
关键升级规则：Summary 必须重新评估；DiDi senior operating scope 如确有帮助可提炼进 summary；陌生行业优先补一条领域桥接句；scope note 和那条全球经营评审 bullet 只有在确实提高匹配度时才使用。

第 6 段  
Skills 既要满足格式硬约束，也要确保没有遗漏正文/JD 关键技术；不要靠暴力删减过关。

第 7 段  
对 must-have 技术，只能补正文证据、扩写项目或重写相关 bullet，不能删除。

第 8 段  
围棋 Summary 句必须是高价值认知信号，不要写成 collaboration/teamwork 论据。

第 9 段  
保留所有不可变字段完全不变；经历顺序保持；输出仍然满足全部格式硬约束。

第 10 段  
如果 seed phrasing、旧 Summary、旧 bullet 选择本身就是失分原因，可以直接替换；rewrite 的目标是通过，而不是尽量少改。

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## MP-06 Planner System Prompt -->

<!-- UID: frag-473a56967fbb4804 -->
- [match_pipe/planner_validation_runner.py:32](../match_pipe/planner_validation_runner.py:32)

---

<!-- UID: frag-7a743cb1208ae3f9 -->
你是简历流程里的 Planner。你的职责不是直接写简历，而是基于 JD、matcher 证据和可选历史简历 starter，判断：这份 starter 是否适合作为起点；是否可以直接送 Reviewer；如果需要写作，哪些内容已覆盖、哪些缺失、哪些存在真实性/ownership/scope 风险；Writer 应如何改写，优先级如何排序。

第 2 段  
必须输出 JSON，不要输出解释性文字。不要复述 schema。

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## MP-07 Planner User Prompt -->

<!-- UID: frag-52b67eb04cf3cd66 -->
- [match_pipe/planner_validation_runner.py:121](../match_pipe/planner_validation_runner.py:121)

---

<!-- UID: frag-c43e08ec6ab8574a -->
请作为 Planner，基于以下信息做流程决策。

第 2 段  
先给出目标模式。

第 3 段  
再给出目标 JD：公司、职位、role_type、seniority、must-have 技术、preferred 技术。

第 4 段  
再给出 Matcher Packet JSON。

第 5 段  
再给出 Starter Resume Markdown；如果没有 starter，就写“无 starter resume”。

第 6 段  
返回 JSON，schema 必须包含：decision、fit_label、reuse_ratio_estimate、already_covered、missing_or_weak、risk_flags、role_seniority_guidance、planner_summary、writer_plan、direct_review_rationale。

第 7 段  
规则 1：`no_starter` 模式下 decision 只能是 `write`。

第 8 段  
规则 2：如果 starter 已经高度贴合且 scope/真实性风险低，可以 `direct_review`。

第 9 段  
规则 3：如果 starter 语义相近但需要改写，选 `write`。

第 10 段  
规则 4：如果 starter 虽相似但会明显误导 summary、ownership、项目骨架或 scope，选 `reject_starter`。

第 11 段  
规则 5：不要把 matcher 的相似度直接等同于可写作适配度。

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## MP-08 Planner Writer Overlay -->

<!-- UID: frag-be4dffa32d8bb387 -->

角色：
- Planner-first Writer

代码位置：
- [match_pipe/planner_validation_runner.py:194](../match_pipe/planner_validation_runner.py:194)

---

<!-- UID: frag-43b7b375f521a3e1 -->
这不是一个独立完整 prompt，而是在 `build_master_writer_prompt()` 后面追加的 overlay。

第 2 段  
追加 Planner Decision JSON。

第 3 段  
追加 Matcher Evidence JSON。

第 4 段  
追加 Historical Starter Resume。

第 5 段  
Planner-first Rules：如果给了 starter resume，把它视为可复用参考骨架，而不是必须保留的模板。

第 6 段  
优先遵循 planner 对 coverage、missing、risk、role-seniority framing 的判断。

第 7 段  
如果 planner 指出了 scope 或真实性风险，必须主动改写 summary、ownership 和项目 framing。

第 8 段  
如果 planner 认为 starter 可高比例复用，可保留高价值证据，但仍以目标 JD 为准。

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## MP-09 Planner Revision Overlay -->

<!-- UID: frag-6f8353370af3bb5d -->

角色：
- Planner-first Revision Writer

代码位置：
- [match_pipe/planner_validation_runner.py:230](../match_pipe/planner_validation_runner.py:230)

---

<!-- UID: frag-c505a5d4d622de38 -->
这也是一个 overlay：它先完整复用 `build_master_writer_prompt()`，再追加 planner/reviewer carry-over。

第 2 段  
追加 Planner-first Revision Context：当前评分、是否通过、reviewer 是否要求继续修改、当前目标不是保留旧稿，而是把简历提升到更稳的 pass。

第 3 段  
追加 Planner Carry-over。

第 4 段  
追加 Planner Risks。

第 5 段  
追加 Reviewer Priority。

第 6 段  
追加 Reviewer Findings。

第 7 段  
追加 Must-have Tech。

第 8 段  
追加 Existing Resume Draft To Revise。

第 9 段  
Revision Rules：不要保留任何只是因为旧稿已经存在、但不再服务目标 JD 的 summary framing、ownership framing 或 bullet 结构。

第 10 段  
如果 planner 指出了 starter 的 scope、真实性、角色定位或 seniority 风险，必须优先修正。

第 11 段  
如果 reviewer 指出了 JD 缺口，优先补正文证据，而不是删除 must-have 技术。

第 12 段  
允许重写 summary、skills 分组、bullet 取舍、project baseline 和经历 framing，但不得破坏不可变字段与职业主线真实性。

第 13 段  
输出完整简历 Markdown，不要解释。

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## MP-10 Downstream Dual-Channel Overlay -->

<!-- UID: frag-86170c276b1c7982 -->

角色：

---

<!-- UID: frag-4b0df3838ea8d9e5 -->
- [match_pipe/downstream_validation_runner.py:276](../match_pipe/downstream_validation_runner.py:276)

---

<!-- UID: frag-a2f38399bd26ebd8 -->
这也是 overlay：它先复用 `build_seed_retarget_prompt()`，然后再追加双通道连续性说明。

第 2 段  
标题固定为：`## Dual-channel continuity note`

第 3 段  
逐行插入 `delta_summary`。

第 4 段  
如果 continuity anchor 存在，追加它的公司、标题和 `reuse_readiness`。

第 5 段  
最后一条固定结论句：Use semantic anchor as the main skeleton. Apply company continuity only when it does not reintroduce hard gaps.

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## What You Can Edit Safely First -->

<!-- UID: frag-65a63662e2b9ceb9 -->

如果你想先做低风险、高收益的审稿，我建议优先看：
- `MP-06` 和 `MP-07`
  原因：这是 `match_pipe` 自己的 Planner prompt，改它不会直接波及主链路。
- `MP-08` 和 `MP-09`
  原因：这是 `match_pipe` 自己的 overlay，最适合先按段落改。
- `MP-10`
  原因：这是 `match_pipe` 双通道实验特有说明，改动边界最清晰。

如果你要改共享上游 prompt，再看：
- `MP-01` / `MP-02` / `MP-03`
- `MP-04` / `MP-05`

---

<!-- 上下文: source_reference::doc::match_pipe_prompt_review :: source_reference::doc::match_pipe_prompt_review::document -->
<!-- 小标题: ## Important Note -->

<!-- UID: frag-2c3fb826c9544708 -->

你刚才指出的问题是成立的：
- 之前那份 `prompt_canonical_review.md` 是“工程映射表”
- 它不是“给人直接逐段审稿”的最终文档
- 所以它故意折叠了像 `SKILLS 一致性规则（最重要）` 这种上游动态拼装正文

这份 `match_pipe_prompt_review.md` 才是给你直接改自然语言段落用的版本。

---

<!-- 上下文: source_reference::design_guide::task_general_prompt :: source_reference::design_guide::task_general_prompt::document -->

<!-- UID: frag-7a4fe1228f671fbd -->
可以。你现在卡住的点很正常，因为一旦把“层级关系、OR 关系、父类/子类要求、硬软要求的多轴结构”引入进来，原来那种简单的：

* 抽 A/B/C/D/E
* 直接算命中多少
* 再排序

就不够了。

现在正确的迁移方式是：

> **把原来的“元素匹配”升级成“要求单元匹配”**。
> 原来 A/B/C/D/E 是直接比元素；
> 现在要先把岗位描述拆成“要求单元（requirement unit）”，然后每个要求单元内部再去匹配它所包含的元素、层级、逻辑和强弱。

也就是说，新的匹配逻辑不是废掉原来的 A/B/C/D/E，而是：

* **A/B/C/D/E 仍然存在**
* 但它们现在不再直接平铺比较
* 而是被装进一个个“要求单元”里，再进行更高一层的匹配

下面我先给你一版**正式改写后的完整 prompt**，然后再单独详细讲清楚：

1. 新模型里到底怎么召回
2. 怎么打分
3. 怎么处理 OR
4. 怎么处理父类/子类
5. 怎么做权重评估
6. 原来 ABCDE 规则怎么迁移到新模型

---

<!-- UID: frag-39f61a57a3f6eaaf -->
你的任务是：在**不修改原有程序**的前提下，基于当前已有的 **1000 多份原始岗位描述（Job Descriptions）**，独立开发一个全新的“岗位描述匹配系统”。

这个系统的第一目标，不是直接生成简历，而是先把岗位描述本身做成一个**可计算、可索引、可比较、可扩展、可解释**的结构化匹配系统。这个系统后续将用于：

1. 新岗位进入时，尽可能快地匹配到历史上最相似的旧岗位；
2. 判断是否存在“完全一致”或“几乎完全一致”的旧岗位；
3. 在无法完全一致时，找到“技术栈、业务方向、职级、岗位职责、硬要求、软要求、约束条件”等维度最接近的旧岗位；
4. 为后续复用已有简历、减少重写轮次、提高达标率提供高质量输入；
5. 最终与旧匹配模型做对比，评估哪种模型更快、更准、更稳定、更能减少简历重写轮次。

注意：当前已有的 800 多份简历可以暂时忽略，因为它们是基于旧匹配模型生成的，不适合作为新系统的结构基准。新系统可以完全不依赖旧程序、不读取旧程序逻辑、不改动旧程序，而是以这 1000 多份岗位描述为训练池 / 建模池，自行建立一套新的岗位匹配程序。

整个新系统必须优先实现并做扎实 **策略4**，把它作为教师系统（teacher system）/ 基准系统（gold system）。在策略4没有做扎实之前，不允许为了速度而偷工减料做简化版。只有策略4稳定后，才允许从策略4蒸馏（distill）出策略3，再进一步寻找最终可部署的高性价比版本。

最终程序上线后，必须依靠**程序自身自治运行**，不依赖大模型（large model）在线参与。也就是说，你现在开发时可以利用代码、数据、规则、统计、聚类、相似度、索引、状态机等程序机制，但最终系统运行时，不能把“抽取岗位要素、语义归一、权重判断、岗位匹配”这些核心能力依赖给大模型在线完成。

---

<!-- 上下文: source_reference::design_guide::task_general_prompt :: source_reference::design_guide::task_general_prompt::document -->
<!-- 小标题: ## 一、系统要解决的真实业务问题 -->

<!-- UID: frag-b58df1b0d5ee837e -->

当前你拥有的是 1000 多份原始岗位描述。每天还会持续新增约 100 到 200 个岗位，其中有一部分是噪声岗位，也就是被错误筛选进来的不相关岗位。

你的目标是：

当一个新的岗位描述进入系统时，系统能够自动完成以下事情：

1. 从岗位描述中抽取关键要素；
2. 将不同表述方式但语义相同的要素归一到统一字典表；
3. 判断这些要素中哪些是硬要求，哪些是软要求，哪些是强偏好，哪些只是背景信息；
4. 将新岗位与历史岗位进行快速匹配；
5. 优先寻找“完全一致”或“几乎完全一致”的旧岗位；
6. 如果找不到完全一致的旧岗位，则寻找在以下维度最接近的旧岗位：

   * 技术栈
   * 业务方向
   * 职级要求
   * 岗位职责
   * 领域要求
   * 必备要求（must have）
   * 优先要求（preferred / nice to have）
   * 约束条件
   * 其他可能存在但当前尚未显式定义的维度
7. 输出最相似的旧岗位列表及其解释；
8. 为后续简历生成与重写提供最佳复用起点。

系统最终追求的理想状态是：

如果新岗位和历史岗位在业务方向、技术栈、核心职责、硬要求、职级要求等关键维度上完全一致，那么它们应当被匹配到同一个岗位模式，后续也应尽量复用同一种简历生成路径，或者只需极少轮次重写即可达标。

---

<!-- 上下文: source_reference::design_guide::task_general_prompt :: source_reference::design_guide::task_general_prompt::document -->
<!-- 小标题: ## 二、岗位描述不应只拆成平铺要素，而应拆成要求单元 -->

<!-- UID: frag-1a0a20ff815f5239 -->

系统不能把岗位描述简单表示成一个平铺的元素集合，例如：
岗位 = {A, B, C, D}

这种表达过于粗糙，无法正确处理：

* “Python or Java 有其一即可”
* “熟悉一门主流编程语言即可”与“必须有 C++ 经验”的区别
* 泛技术栈 Y 与细分技术栈 Y1/Y2/Y3 的层级关系
* 技术栈 / 业务方向 / 岗位职责 与 硬要求 / 软要求 之间不是同一层级分类的问题

因此，岗位描述必须先被解析成一组“要求单元（requirement units）”。

每个要求单元至少包含以下四个维度：

1. 内容维度
   表示该要求属于什么内容类别，例如：

* 技术栈
* 业务方向
* 岗位职责
* 行业经验
* 学历要求
* 地点限制
* 工作授权
* 年限要求
* 语言能力
* 工具或平台要求

2. 约束维度
   表示该要求的强弱程度，例如：

* 硬要求（must have）
* 强偏好（strong preference）
* 软要求（preferred / nice to have）
* 背景信息（background / context）

注意：
“技术栈 / 业务方向 / 岗位职责”是内容维度；
“硬要求 / 软要求 / 强偏好”是约束维度。
它们不是平级并列分类，而是两条不同轴。

3. 逻辑维度
   表示该要求内部的逻辑关系，至少必须支持：

* 单项必须
* 多项同时满足（AND）
* 多项任选其一（OR）
* 多项中至少满足 K 项
* 主项满足即可，子项命中可加分
* 主项满足且某个子项优先

系统必须显式建模 OR 关系，不能把“Python or Java”误拆成两个并列 must have。

4. 层级维度
   表示该要求处于抽象父类层，还是具体子类层。

---

<!-- UID: frag-3d06a85a75924ba6 -->
* “主流编程语言”属于父类层
* “Python / Java / C++”属于子类层
* “C++17 / C++20”可能属于更细层

系统必须支持父类要求与子类要求之间的单向满足关系：

* 命中更具体的子类，可以向上覆盖父类要求
* 命中父类泛要求，不能自动向下推定命中特定子类要求

最终，岗位匹配系统不应把岗位描述表示成简单的要素集合，而应表示成：
“一组带有内容维度、约束维度、逻辑维度、层级维度的要求单元集合”。

---

<!-- 上下文: source_reference::design_guide::task_general_prompt :: source_reference::design_guide::task_general_prompt::document -->
<!-- 小标题: ## 三、岗位要素的基础类型 -->

<!-- UID: frag-8cc1723812bf1b18 -->

虽然系统最终要使用“要求单元”作为核心结构，但要求单元内部仍然由更底层的“岗位要素（job elements）”组成。

岗位要素至少包括以下几类，但不能局限于这些：

1. 技术栈要素
   例如：
   语言、框架、数据库、云平台、工具链、中间件、基础设施、工程技术、算法方向、分析工具等。

2. 业务方向要素
   例如：
   推荐系统、风控、安全、增长、广告、电商、支付、搜索、数据治理、平台工程、机器学习基础设施等。

3. 职级要素
   例如：
   实习、初级、中级、高级、资深、应届、管理、带团队经验、独立 owner 经验等。

4. 岗位职责要素
   例如：
   后端开发、全栈开发、数据建模、实验设计、模型部署、系统设计、平台搭建、跨团队协作、指标建设等。

5. 约束条件要素
   例如：
   地点、工作授权、签证、远程/现场、毕业时间、学位要求、可实习周期等。

6. 其他隐含但重要的要素
   例如：
   岗位偏平台还是偏业务、偏研究还是偏落地、偏分析还是偏开发、团队成熟度、业务阶段等。

系统必须支持未来持续新增、细化和扩充要素类别。

---

<!-- 上下文: source_reference::design_guide::task_general_prompt :: source_reference::design_guide::task_general_prompt::document -->
<!-- 小标题: ## 四、双层表示：表面表达层 + 语义归一层 -->

<!-- UID: frag-bcfddfe8bdf4d698 -->

系统中每个实例、每个查询、每个候选，都必须采用双层表示（dual representation）：

一是表面表达层（surface layer）
记录岗位描述中的原始说法，例如：

* A1
* A2
* A3
* “熟悉一门主流编程语言”
* “Proficient in at least one modern programming language”
* “Experience with Python or Java”

二是语义归一层（canonical layer）
记录归一后的统一语义要素，例如：

* 主流编程语言

---

<!-- UID: frag-472bbffd4667eebb -->
* 后端开发
* 推荐系统
* 电商

必须同时保留：

* 表面表达层：用于细粒度差异比较、实例精排、误差分析
* 语义归一层：用于 pattern 构建、索引、召回、排序

禁止只保留其中一层。

---

<!-- 上下文: source_reference::design_guide::task_general_prompt :: source_reference::design_guide::task_general_prompt::document -->
<!-- 小标题: ## 五、技术栈与职责、业务方向的层级关系 -->

<!-- UID: frag-4075e6ada8ea02f6 -->

系统必须支持技术栈、职责、业务方向等要素内部存在层级关系，而不是把它们全部看成平面词。

---

<!-- UID: frag-90c13552e555acf6 -->
1. 主流编程语言

   * Python
   * Java
   * C++
   * Go

2. 云平台

   * AWS
   * GCP
   * Azure

3. 大数据

   * Spark
   * Flink
   * Hadoop

4. 后端开发

   * 服务端开发
   * 接口开发
   * 微服务开发
   * 分布式系统开发

5. 机器学习平台

   * 训练平台
   * 推理平台
   * 特征平台
   * 数据管道

匹配规则必须支持：

* 子类可向上满足父类要求
* 父类不能自动向下满足具体子类要求

例如：
岗位要求“熟悉一门主流编程语言”，则命中 Python/Java/C++/Go 中任一子类都可满足该要求单元。
但如果岗位要求“必须有 C++ 经验”，则不能用 Python 或 Java 来替代满足。

同理：
如果岗位要求“有 Y 方向经验即可”，则 Y1/Y2/Y3 可部分或完全满足该要求。
但如果岗位要求“必须有 Y1 经验”，则泛泛的 Y 要求不能向下替代 Y1。

---

<!-- 上下文: source_reference::design_guide::task_general_prompt :: source_reference::design_guide::task_general_prompt::document -->
<!-- 小标题: ## 六、OR / AND / 至少 K 项的逻辑关系 -->

<!-- UID: frag-358ae55145e92ad5 -->

系统必须支持要求单元内部的逻辑关系，而不能把所有元素平铺并列。

---

<!-- UID: frag-f7a17a6993b01263 -->
* Python or Java 有其一即可
* SQL and Python 都需要
* Kafka / Redis / MySQL 中至少熟悉两项
* 熟悉一门主流编程语言即可，但 C++ 优先

因此，每个要求单元必须能够表达：

1. 单项必须
2. 多项同时满足（AND）
3. 多项任选其一（OR）
4. 多项中至少满足 K 项
5. 主项满足即可，附加子项加分
6. 主项为硬要求，具体某子项为强偏好

系统必须特别注意：
“Python or Java” 不是两个并列 must have。
它应该被建模为一个 OR 型要求单元，候选项为：

* Python
* Java

满足其中任意一项即可满足该要求单元。

---

<!-- 上下文: source_reference::design_guide::task_general_prompt :: source_reference::design_guide::task_general_prompt::document -->
<!-- 小标题: ## 七、权重体系 -->

<!-- UID: frag-58fde79201d55609 -->

当前已有岗位描述中虽然已经初步提取了一些 domain、技术栈、职级要求，但：

* 没有权重；
* 要素粒度还不够细；
* 还需要根据新岗位不断补充和细化。

因此你必须自行构建一套岗位要素 / 要求单元权重体系。

这套权重体系不能是死的，必须能够从岗位描述中自动判断和学习。至少要区分：

1. 硬要求（must have）
2. 强偏好（strong preference）
3. 软要求（preferred / nice to have）
4. 背景信息（background only）

权重来源可以综合以下信号：

* 显式关键词：must、required、preferred、nice to have、bonus 等
* 描述所在段落：基本要求、优先条件、岗位职责、职位概述等
* 表达强度：明确必须、建议、有经验优先、了解即可
* 出现位置：标题、summary、requirements、responsibilities 等
* 重复出现程度
* 是否属于团队核心能力
* 是否与其他要求构成关键组合模式
* 是否在历史岗位中稳定代表某类岗位核心特征

权重既要存在于“要求单元层”，也要存在于“要求单元内部要素层”。

例如：
要求单元：“Python or Java”

* 这个单元本身可能是硬要求，权重高
* 单元内部的 Python、Java 作为候选项，满足其一即可
* 若其中某项有额外说明，例如“Java preferred”，则 Java 在单元内部可带附加权重

---

<!-- 上下文: source_reference::design_guide::task_general_prompt :: source_reference::design_guide::task_general_prompt::document -->
<!-- 小标题: ## 八、pattern 的定义：岗位模式组 -->

<!-- UID: frag-9fa20078bda1fadb -->

本系统中的 pattern，定义为：

在语义归一层和要求单元层上，“关键要求单元结构完全一致”的一组岗位描述。

注意，这里不能只看“平铺语义元素是否一致”，而应看：

* 要求单元的内容是否一致
* 要求单元的约束强度是否一致
* 要求单元的逻辑关系是否一致
* 要求单元的层级要求是否一致

例如这两个岗位不能简单视为同一个 pattern：

岗位甲：

* 熟悉一门主流编程语言（OR：Python / Java / C++）

岗位乙：

---

<!-- UID: frag-c48fcdf9fa1099a5 -->
虽然它们都涉及主流编程语言和 C++，但要求结构不同，不应直接归为完全一致 pattern。

因此，pattern 应基于“要求单元结构”构建，而不是只基于词面元素构建。

---

<!-- 上下文: source_reference::design_guide::task_general_prompt :: source_reference::design_guide::task_general_prompt::document -->
<!-- 小标题: ## 九、岗位匹配的目标层级 -->

<!-- UID: frag-f0c4bb9224552270 -->

岗位匹配应分三层目标：

第一层：完全一致
新岗位与某历史岗位在关键要求单元结构上完全一致，包括：

* 核心技术栈要求
* 业务方向
* 岗位职责
* 职级要求
* 硬要求 / 软要求结构
* 逻辑关系
* 层级要求

第二层：高度相似
如果无法完全一致，则尽量在以下维度上高度相似：

* 技术栈接近
* 业务方向接近
* 职级接近
* 岗位职责接近
* 硬要求接近
* 约束条件接近

第三层：可复用相似
即使不能完全一致，也应找到最容易通过少量重写达标的历史岗位。

---

<!-- 上下文: source_reference::design_guide::task_general_prompt :: source_reference::design_guide::task_general_prompt::document -->
<!-- 小标题: ## 十、噪声岗位处理 -->

<!-- UID: frag-eb5df773c98ebda1 -->

每天新增的 100 到 200 个岗位中，部分是噪声岗位，即被错误筛选进来的不相关岗位。

系统必须内置噪声处理机制。至少要做到：

1. 识别明显偏离目标岗位池的岗位；
2. 将可疑噪声岗位标记出来；
3. 噪声岗位不能污染主 pattern 库；
4. 噪声岗位进入隔离区单独分析；
5. 噪声识别必须是程序化机制，而不是依赖人工逐条筛。

---

<!-- 上下文: source_reference::design_guide::task_general_prompt :: source_reference::design_guide::task_general_prompt::document -->
<!-- 小标题: ## 十一、必须实现的完整模块 -->

<!-- UID: frag-42ffa18ebde73d67 -->

你必须实现以下模块：

1. 岗位来源审计模块
   审计代码库和数据结构，识别岗位描述来源、字段结构、可抽取字段、噪声字段、辅助字段。

2. 岗位要素抽取模块
   从岗位描述中抽取候选要素，包括技术栈、业务方向、职级、职责、硬要求、软要求、约束条件等。

3. 要求单元解析模块
   将抽取出的岗位要素组织成要求单元，并识别每个要求单元的：

   * 内容维度
   * 约束维度
   * 逻辑维度
   * 层级维度

4. 语义归一模块
   把不同表述归一到统一字典表中，实现 A1/A2/A3 -> A 的映射。

5. 开放世界新要素发现模块
   当新的技术栈、新的业务方向、新的职责类别出现时，系统必须能识别并逐步纳入字典表，而不是硬塞给旧类。

6. 权重建模模块
   给岗位要素和要求单元赋权，区分硬要求、强偏好、软要求、背景信息。

7. pattern 构建模块
   以“要求单元结构 + 语义要素”作为基础构建岗位模式组。

8. 索引构建模块
   建立：

   * 精确 pattern 索引
   * 要素倒排索引
   * 高价值组合索引
   * 表面层近邻索引
   * 可选关系索引

9. 多路召回模块
   对新岗位并行做：

   * 精确 pattern 命中
   * 高价值要求单元召回
   * 高价值要素召回
   * 高价值组合召回
   * 表面层近邻召回
   * 关系扩展召回

10. 两阶段排序模块
    先对 pattern 排序，再对具体岗位实例排序。

11. 解释输出模块
    解释为什么匹配到这些旧岗位，哪些要求命中，哪些缺失，哪些是硬要求，哪些是软要求，哪些是父类命中，哪些是子类精确命中，哪些是 OR 满足。

12. 评估对比模块
    将新模型与旧模型对比，重点比较：

* 匹配速度
* 匹配准确度
* 是否更快找到最优旧岗位
* 是否减少简历重写轮次
* 是否提高最终达标率

---

<!-- 上下文: source_reference::design_guide::task_general_prompt :: source_reference::design_guide::task_general_prompt::document -->
<!-- 小标题: ## 十二、开放世界 -->

<!-- UID: frag-26fdac51c5423205 -->

现有的 1000 多份岗位描述不是全集。

因此系统必须支持开放世界识别（open-world recognition）：

1. 不能假设当前字典表已经覆盖所有技术栈；
2. 不能假设当前业务方向体系已经完整；
3. 不能假设当前职级表达已经固定；
4. 不能假设当前职责表述已经穷尽。

新表达进入后，必须走四态机制：

1. 已解析别名
2. 近似已知但未决
3. 候选新要素
4. 噪声或无效项

必须维护：

* 已验证要素区
* 候选新区
* 未决表达池

---

<!-- 上下文: source_reference::design_guide::task_general_prompt :: source_reference::design_guide::task_general_prompt::document -->
<!-- 小标题: ## 十三、召回与排序必须分离 -->

<!-- UID: frag-a961c2a60d67a3f6 -->

召回（recall）与排序（ranking）必须严格分离。

召回负责缩小候选岗位池。
排序负责从候选中选出最适合复用的旧岗位。

召回阶段重点依赖：

* 高价值硬要求单元
* 高价值要素
* 高价值组合键
* 表面层近邻
* 结构相近的要求单元模式

排序阶段重点依赖：

* 硬要求单元命中情况
* 技术栈核心单元命中情况
* 业务方向单元命中情况
* 职级单元命中情况
* 岗位职责单元命中情况
* 软要求与偏好单元补充分
* 表面层近似度
* 元信息契合度

---

<!-- 上下文: source_reference::design_guide::task_general_prompt :: source_reference::design_guide::task_general_prompt::document -->
<!-- 小标题: ## 十四、策略4的地位 -->

<!-- UID: frag-7cc524b59e456411 -->

策略4是教师系统（teacher system）/ 基准系统（gold system）。
你必须优先把策略4做得扎实、做得全、做得细。

策略4必须满足：

1. 正确性优先
2. 召回完整
3. 排序可解释
4. 支持开放世界
5. 支持噪声隔离
6. 可保存中间产物
7. 可回放每次匹配轨迹
8. 可作为策略3蒸馏对照标准

---

<!-- 上下文: source_reference::design_guide::task_general_prompt :: source_reference::design_guide::task_general_prompt::document -->
<!-- 小标题: ## 十五、策略3的定位 -->

<!-- UID: frag-2d16fcfc2d6ab19c -->

策略3不是先做的，而是策略4稳定后的蒸馏目标。

策略3的目标是：

* 计算更轻
* 速度更快
* 效果尽量逼近策略4

评估策略3时，必须拿策略4逐项对比，而不是凭感觉判断。

---

<!-- 上下文: source_reference::design_guide::task_general_prompt :: source_reference::design_guide::task_general_prompt::document -->
<!-- 小标题: ## 十六、最终交付要求 -->

<!-- UID: frag-9d4de5fbe4b92cbf -->

最终必须交付：

1. 岗位来源地图
2. 岗位要素抽取清单
3. 要素字典表（含别名映射和层级关系）
4. 未决表达池与候选新区机制
5. 要求单元解析逻辑
6. pattern 构建逻辑
7. 索引构建逻辑
8. 多路召回逻辑
9. 两阶段排序逻辑
10. 噪声岗位识别机制
11. 匹配解释输出
12. 新旧模型对比评估工具
13. 策略4教师系统
14. 策略3蒸馏基线
15. 一个不依赖大模型在线参与、可独立运行的新程序

---

<!-- 上下文: source_reference::design_guide::task_general_prompt :: source_reference::design_guide::task_general_prompt::document -->
<!-- 小标题: ## 十七、执行顺序 -->

<!-- UID: frag-9222faaa30129cb5 -->

请按以下顺序推进，不要跳步：

1. 审计代码库和岗位数据结构
2. 建立岗位要素抽取清单
3. 实现岗位要素抽取
4. 实现双层表示（表面表达层 + 语义归一层）
5. 实现要求单元解析
6. 实现开放世界新要素状态机
7. 实现岗位要素与要求单元权重体系
8. 构建 pattern
9. 构建索引
10. 实现多路召回
11. 实现两阶段排序
12. 实现噪声隔离
13. 实现解释输出
14. 建立评估集
15. 固化策略4为教师系统
16. 策略4稳定后再开始蒸馏策略3

现在开始执行。
你的第一目标不是快，而是先把这个岗位描述匹配系统的策略4做成真正可靠、完整、可作为教师系统的基准程序。
只有在这个基础上，后续的简化、加速、替代，才有意义。

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->

<!-- UID: frag-536a4302f4a900ec -->
好，我直接继续往下，把这套东西再落到**可执行层**。下面给你两部分：

第一部分：**数据结构 + 伪代码 + 打分流程**
第二部分：**工程化执行 prompt 补充版**

这样你既能看懂“系统到底怎么跑”，也能直接交给程序去做。

---

<!-- UID: frag-ce51ac3b23667a8b -->
# 一、先把最终模型压成一句话

新的岗位匹配模型，不再是：

> 岗位 = 一堆平铺元素

而是：

> **岗位 = 一组要求单元（requirement units）**
> 每个要求单元内部再包含：
>
> * 要素集合
> * 逻辑关系
> * 层级关系
> * 强弱程度
> * 单元权重

然后匹配时：

> **先匹配要求单元，再匹配单元内部要素，最后汇总成岗位总分。**

---

<!-- UID: frag-3a82a03a04f7f4b2 -->
# 二、核心数据结构设计


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 1. 原始岗位对象 -->

<!-- UID: frag-4c76758d5fbf8177 -->
  "title": "Software Engineer - Backend",
  "company": "X",
  "location": "San Jose, CA",
  "description_raw": "...原始岗位描述文本...",
  "source_metadata": {
    "posted_at": "2026-04-10",
    "source": "scraper_a"

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 2. 抽取后的表面表达层 -->

<!-- UID: frag-f56eed0446c529da -->

这是从原始 JD 中抽出来的候选表达。

---

<!-- UID: frag-e7c30cc83f6f121e -->
  "surface_elements": [
    {
      "text": "proficient in at least one modern programming language",
      "type_hint": "tech_stack",
      "source_section": "basic_qualifications",
      "confidence": 0.93
    },
    {
      "text": "C++ experience",
      "type_hint": "tech_stack",
      "source_section": "preferred_qualifications",
      "confidence": 0.98
    },
    {
      "text": "backend development",
      "type_hint": "responsibility",
      "source_section": "responsibilities",
      "confidence": 0.96
    }

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 3. 语义归一后的要素字典项 -->

<!-- UID: frag-f66626f70ff32bfc -->
  "canonical_id": "TECH_CPP",
  "canonical_name": "C++",
  "content_type": "tech_stack",
  "parent_id": "TECH_MAINSTREAM_PROGRAMMING_LANGUAGE",
  "aliases": [
    "C++",
    "C plus plus",
    "modern C++",
    "C++ experience"
  ],
  "status": "verified"
}
```

再比如：

---

<!-- UID: frag-4445f65976474df0 -->
  "canonical_id": "TECH_MAINSTREAM_PROGRAMMING_LANGUAGE",
  "canonical_name": "主流编程语言",
  "content_type": "tech_stack",
  "parent_id": null,
  "aliases": [
    "one modern programming language",
    "mainstream programming language",
    "one major programming language"
  ],
  "status": "verified"

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 4. 要求单元结构 -->

<!-- UID: frag-e0d7eeb83157d4a7 -->

这是最关键的对象。

---

<!-- UID: frag-6c1cf8079967d46a -->
  "unit_id": "ru_001",
  "content_type": "tech_stack",
  "constraint_type": "must_have",
  "logic_type": "OR",
  "hierarchy_level": "parent",
  "unit_weight": 0.28,
  "members": [
    "TECH_PYTHON",
    "TECH_JAVA",
    "TECH_CPP",
    "TECH_GO"
  ],
  "display_name": "熟悉一门主流编程语言",
  "source_evidence": [
    "proficient in at least one modern programming language"

---

<!-- UID: frag-cc3d423f1cb8eaeb -->
再看一个单项必须：

---

<!-- UID: frag-fcca62dbb44afdbf -->
  "unit_id": "ru_002",
  "content_type": "tech_stack",
  "constraint_type": "must_have",
  "logic_type": "SINGLE",
  "hierarchy_level": "child",
  "unit_weight": 0.35,
  "members": [
    "TECH_CPP"
  ],
  "display_name": "必须具备C++经验",
  "source_evidence": [
    "must have C++ experience"

---

<!-- UID: frag-f5e142ee34c080f7 -->
再看一个软要求：

---

<!-- UID: frag-d69ca7ae2fbfdae9 -->
  "unit_id": "ru_003",
  "content_type": "business_domain",
  "constraint_type": "preferred",
  "logic_type": "SINGLE",
  "hierarchy_level": "normal",
  "unit_weight": 0.12,
  "members": [
    "DOMAIN_RECOMMENDATION_SYSTEM"
  ],
  "display_name": "推荐系统经验优先",
  "source_evidence": [
    "experience in recommendation systems is a plus"

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 5. 岗位结构化表示 -->

<!-- UID: frag-41de6872579b6c28 -->

一个岗位最终应该长这样：

---

<!-- UID: frag-cb2fb7c8097a5057 -->
  "canonical_elements": [
    "TECH_CPP",
    "RESP_BACKEND_DEVELOPMENT",
    "DOMAIN_RECOMMENDATION_SYSTEM",
    "TECH_MAINSTREAM_PROGRAMMING_LANGUAGE"
  ],
  "requirement_units": [
    "ru_001",
    "ru_002",
    "ru_003"
  ],
  "metadata": {
    "title_normalized": "backend software engineer",
    "level_hint": "mid",
    "location": "san jose",
    "employment_type": "full_time"

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 6. pattern 结构 -->

<!-- UID: frag-20af349af6537cb4 -->

这里的 pattern 不再是“平铺要素集合”，而是：

> **要求单元结构签名一致的岗位组**

---

<!-- UID: frag-8f2c6581c9c37c3d -->
  "pattern_id": "pt_087",
  "signature": {
    "must_have_units": [
      "OR(TECH_PYTHON|TECH_JAVA|TECH_CPP|TECH_GO)",
      "SINGLE(RESP_BACKEND_DEVELOPMENT)"
    ],
    "preferred_units": [
      "SINGLE(DOMAIN_RECOMMENDATION_SYSTEM)",
      "SINGLE(TECH_CPP)"
    ]
  },
  "member_job_ids": [
    "jd_001",
    "jd_019",
    "jd_104"
  ],
  "support_count": 3

---

<!-- UID: frag-24bdee1266b497fd -->
# 三、要求单元的标准逻辑类型

建议固定以下逻辑类型，不要无限发散：


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 1. `SINGLE` -->

<!-- UID: frag-d0158f28281e4c18 -->

单项要求
例：必须有 C++


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 2. `OR` -->

<!-- UID: frag-be67c6f492b4e555 -->

任选其一
例：Python or Java


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 3. `AND` -->

<!-- UID: frag-f1f59d2eab480a22 -->

必须同时满足
例：Python + SQL


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 4. `AT_LEAST_K` -->

<!-- UID: frag-c310fc2c8c5aa2e6 -->

至少 K 项
例：Kafka / Redis / MySQL 至少两项


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 5. `PARENT_ANY_CHILD` -->

<!-- UID: frag-28f4c604ce735396 -->

父类能力要求
例：熟悉一门主流编程语言


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 6. `PARENT_WITH_CHILD_BONUS` -->

<!-- UID: frag-a92b8bb90efa2dcb -->

父类满足即可，但某个子类优先
例：熟悉一门主流编程语言，C++ 优先

这 6 类已经能覆盖你现在提到的大部分真实情况。

---

<!-- UID: frag-b74a1df59d7e045e -->
# 四、层级命中规则

这是系统最容易做错的地方，必须写死。


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 规则 1：子类可以向上覆盖父类 -->

<!-- UID: frag-102470b0b30188e7 -->
候选岗位命中：

* Python / Java / C++ / Go

都可视为满足。

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 规则 2：父类不能向下覆盖子类 -->

<!-- UID: frag-09ab4bd06948f8e9 -->

如果岗位要求：

---

<!-- UID: frag-cefa7d6774fea95c -->
候选岗位只写：

* 熟悉主流编程语言

不能视为满足 C++。

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 规则 3：兄弟节点不能互相替代 -->

<!-- UID: frag-d338fdf327ec6a23 -->

如果岗位要求：

---

<!-- UID: frag-f059a29ba477af34 -->
候选岗位只有：

* Java

不能满足。

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 规则 4：父类命中可作为弱相关信号 -->

<!-- UID: frag-ffec8b54a2e7c23a -->

如果岗位要求：

---

<!-- UID: frag-7c4daa4bea21d73c -->
候选岗位只有：

* 主流编程语言

可以给极低弱相关分，或直接 0。
这个要看你的业务保守程度。
如果你追求“必须精确”，这里建议直接记 0。

---

<!-- UID: frag-677f016ec5940b1f -->
# 五、召回怎么做

现在进入最重要的工程环节。

你问的核心就是：

> 引入要求单元、OR、层级之后，到底怎么召回？

我建议做 **五路召回**。

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 召回路 1：精确 pattern 召回 -->

<!-- UID: frag-414eeae0ff7c34e2 -->


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 目标 -->

<!-- UID: frag-ccf33f903b210209 -->

先看是否存在“结构完全一致”或“结构高度相似”的历史岗位 pattern。


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 实现 -->

<!-- UID: frag-8eebb0e57dd10f2b -->

给每个岗位生成 pattern signature，例如：

```text
must:
  OR(主流编程语言)
  SINGLE(后端开发)
preferred:
  SINGLE(C++)
  SINGLE(推荐系统)
```

查询新岗位时，先去 pattern 索引中查完全相同签名。


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 作用 -->

<!-- UID: frag-45b79c01b9b5cd92 -->

一旦命中，这通常是最有价值的候选。

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 召回路 2：硬要求单元召回 -->

<!-- UID: frag-0dd2c13fc1292136 -->


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 目标 -->

<!-- UID: frag-7d445f5a888c7442 -->

用新岗位中最关键的硬要求单元召回候选岗位。


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 例子 -->

<!-- UID: frag-c0ceb7f794ff406a -->

新岗位有：

* 必须 C++
* 必须 后端开发
* 必须 分布式系统经验

那就优先用这些单元召回。


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 实现方式 -->

<!-- UID: frag-b9769d6369d15a83 -->

建立：

* 要求单元倒排索引
* 关键 canonical 元素倒排索引

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 召回路 3：高价值组合召回 -->

<!-- UID: frag-e53e48c863b20828 -->


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 目标 -->

<!-- UID: frag-e14dab3b18eb951f -->

解决高频硬要求太泛的问题。

---

<!-- UID: frag-5dc2eb447579ecd8 -->
* “主流编程语言”过于宽泛
* 但“主流编程语言 + 后端开发”
* 或“C++ + 后端开发”
  会非常有区分度


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 实现 -->

<!-- UID: frag-a121b762f0861571 -->

构造组合键，例如：

* `TECH_CPP + RESP_BACKEND_DEVELOPMENT`
* `DOMAIN_SECURITY + RESP_BACKEND_DEVELOPMENT`
* `TECH_SQL + DOMAIN_ECOMMERCE`

对这些高价值组合建索引。

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 召回路 4：表面表达近邻召回 -->

<!-- UID: frag-9f04c6432f057504 -->


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 目标 -->

<!-- UID: frag-17887e331398c50c -->

兜底处理：

* 新表达尚未完全归一
* 字典表不完整
* 语义归一暂时失败


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 实现 -->

<!-- UID: frag-87b4b4915ea4c0c1 -->

对岗位全文或关键段落建近邻索引，找到表面上很接近的旧岗位。


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 作用 -->

<!-- UID: frag-95363d407f08f34f -->

防漏召回，不让未知表达直接失联。

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 召回路 5：层级扩展召回 -->

<!-- UID: frag-5d7cd3ec663841e6 -->


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 目标 -->

<!-- UID: frag-ccd430cce7c2bad4 -->

处理“父类要求”和“子类要求”的层级命中。


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 例子 -->

<!-- UID: frag-962e26eb4e22afdb -->
那么召回时可扩展到：


---

<!-- UID: frag-67eb2ecc54c69177 -->
* Go

但如果岗位要求：

---

<!-- UID: frag-f48f4f930d014ecc -->
则不应该反向扩展到整个主流编程语言池。


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 原则 -->

<!-- UID: frag-71406d3f40bcdec2 -->

层级扩展只能：

* 从父类向下展开子类候选
* 不能从子类向上泛化并替代精确要求

---

<!-- UID: frag-de704bb05e6201d1 -->
# 六、召回键怎么选

不是所有要求单元都同等重要。

建议为每个要求单元计算一个“召回优先分”：

[
召回优先分 = 单元权重 \times 区分度 \times 稳定性
]

其中：


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 单元权重 -->

<!-- UID: frag-074671af6cefd36d -->

这个要求本身在岗位里有多重要


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 区分度 -->

<!-- UID: frag-94a2febb29a25275 -->

这个要求单元在全库中有多稀有、多能缩小候选池


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 稳定性 -->

<!-- UID: frag-f15fc30d5f21bb15 -->

这个要求单元是否是字典里成熟、边界清晰、不容易误判的单元

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 实际选择规则 -->

<!-- UID: frag-de502c06a6dea67d -->

每个查询岗位只拿：

* 前 3 到 6 个高价值要求单元
* 再加 1 到 3 个高价值组合键
  进入主召回

剩余信息留到精排阶段再用。

---

<!-- UID: frag-5ad08d482f0f4bf1 -->
# 七、打分怎么做

打分分三层。

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 第一层：要求单元满足度 -->

<!-- UID: frag-2db6c329c188b243 -->

这是新的核心。

对查询岗位里的每个要求单元 (u)，计算候选岗位对它的满足度：

[
满足度(u, 候选岗位)
\in [0,1]
]

满足度取决于：

* 逻辑类型
* 层级命中关系
* 子项命中情况
* 是否是精确命中
* 是否只是父类/泛化命中

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 1. `SINGLE` 单项要求 -->

<!-- UID: frag-5f03380a6a076fae -->

例如：

---

<!-- UID: frag-6eb2e844c8edead1 -->
满足度规则：

* 精确命中 C++：1.0
* 只命中父类“主流编程语言”：0 或很低
* 命中兄弟项 Python/Java：0

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 2. `OR` -->

<!-- UID: frag-c6eacae6ad413cca -->
* Python or Java or C++

---

<!-- UID: frag-393486c49f7de509 -->
* 命中任意一个：1.0
* 命中多个：1.0 + 小额 bonus
* 一个都没命中：0

注意：
bonus 很小，只用于排序细化，不能改变 OR 的本质。

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 3. `AND` -->

<!-- UID: frag-81a0c90afe0c736b -->
* Python + SQL

---

<!-- UID: frag-5c4ebf2fdf98aa55 -->
* 全部命中：1.0
* 命中一半：部分分
* 全缺失：0

例如可设：

[
满足度 = 已命中项数 / 总项数

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 4. `AT_LEAST_K` -->

<!-- UID: frag-d7302ff54923bec5 -->
* Kafka / Redis / MySQL 至少两项

---

<!-- UID: frag-029439b1b5f1ee1a -->
* 命中数 >= K：1.0
* 命中数 < K：按比例部分给分

---

<!-- UID: frag-2c19b586cb5d625e -->
[
满足度 = \min(命中数 / K, 1.0)

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 5. `PARENT_ANY_CHILD` -->

<!-- UID: frag-b88df15b33882062 -->
* 熟悉一门主流编程语言

---

<!-- UID: frag-ac9bf4d06a494a88 -->
* 任意一个子类命中：1.0
* 多个子类命中：1.0 + 小额 bonus
* 一个都没命中：0

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 6. `PARENT_WITH_CHILD_BONUS` -->

<!-- UID: frag-1783ac47772a147a -->
* 熟悉一门主流编程语言，C++ 优先

最稳妥的做法：
不要硬塞在一个单元里，直接拆成两个单元：


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: #### 单元 A -->

<!-- UID: frag-3e4622d1442aedff -->

* OR(主流编程语言)
* 硬要求
* 权重高


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: #### 单元 B -->

<!-- UID: frag-46f0b03348b80818 -->

* C++
* 强偏好
* 权重中高

这样最清晰，也最可控。

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 第二层：岗位级要求单元总分 -->

<!-- UID: frag-4c87f577ce4aa9b1 -->

有了每个单元的满足度后，就可以做岗位级汇总。

[
岗位要求分 = \sum (单元权重 \times 单元满足度)
]

但这里要分桶：


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 硬要求总分 -->

<!-- UID: frag-50a106001fa4373f -->

[
硬要求总分 = \sum (硬要求单元权重 \times 满足度)
]


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 软要求总分 -->

<!-- UID: frag-d64a2cd87772c63c -->

[
软要求总分 = \sum (软要求单元权重 \times 满足度)
]


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 强偏好总分 -->

<!-- UID: frag-654d9a7142f3838d -->

[
强偏好总分 = \sum (强偏好单元权重 \times 满足度)

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 第三层：最终岗位匹配总分 -->

<!-- UID: frag-b0d2a73b8f3cff75 -->

[
最终分 =
\alpha \cdot 硬要求总分
+
\beta \cdot 强偏好总分
+
\gamma \cdot 软要求总分
+
\delta \cdot 表面表达接近度
+
\epsilon \cdot 元信息接近度
]

其中一般满足：

* (\alpha) 最大
* (\beta) 次之
* (\gamma) 再次之
* (\delta, \epsilon) 主要用于候选细排

---

<!-- UID: frag-11c85bd6ea2dd87a -->
# 八、硬要求要不要设“门槛”？

建议要。

因为在真实业务里：

> 某些 must have 没命中，再高的总体相似度也没意义。

所以建议引入“门槛规则”：


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 规则 1 -->

<!-- UID: frag-f9365eb9c2a06c69 -->

如果关键硬要求单元缺失比例过高，直接降级候选。


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 规则 2 -->

<!-- UID: frag-79623e0f7f304b9a -->

如果某个特别核心的单项硬要求没命中，例如“必须 C++”，则即使其他项很像，也不能排太前。

这能保证系统不会被“看起来像，但核心硬要求不满足”的岗位干扰。

---

<!-- UID: frag-295fe534c89f1eee -->
# 九、原来的 ABCDE 怎么迁移到新模型里？

这是你最想搞清楚的地方，我再压一遍。

原来：

* A/B/C/D/E 是直接比

现在：

* A/B/C/D/E 不再直接打总分
* 它们要先被组织进要求单元里

例如原来你会说：

新岗位 = A B C D E
候选岗位 = B C D E
所以候选命中 4/5，很高

但现在可能真实结构是：


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 查询岗位 -->

<!-- UID: frag-f8f7306f4a7cfd75 -->


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 单元 1 -->

<!-- UID: frag-8a7545fc25432e35 -->

* A
* 硬要求
* 权重 0.5


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 单元 2 -->

<!-- UID: frag-e32307b233a80e8c -->

* OR(B,C,D,E)
* 硬要求
* 权重 0.3


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ### 单元 3 -->

<!-- UID: frag-826b554915ff5b78 -->

* F
* 软要求
* 权重 0.2

如果候选岗位只有 B C D E：

* 单元 1 = 0
* 单元 2 = 1
* 单元 3 = 0

最终总分不高，因为最重要的 A 没满足。

所以：

> **元素数量命中，不再直接代表高匹配。**
> **必须先看这些元素属于哪个要求单元，以及这个单元有多重要。**

---

<!-- UID: frag-3b86d265e0b48879 -->
# 十、权重怎么评估得更细？

现在权重有两层：

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 层 1：要求单元权重 -->

<!-- UID: frag-c66cd27816ffe6de -->
* 这个要求单元在岗位中有多重要

来源：

* must / preferred / nice to have
* 所在 section
* 表达强度
* 是否出现在标题/summary/basic qualifications
* 是否是核心职责
* 是否高频但关键

---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 层 2：要求单元内部成员权重 -->

<!-- UID: frag-01b891ed6f82bbfe -->
* 在这个单元里，哪个成员更关键

---

<!-- UID: frag-8a20c0fafb83f5d0 -->
* OR(Python, Java, C++)
  如果写的是：
* “Python or Java required, C++ is a plus”

那可以拆成：

* OR(Python, Java) 作为硬要求单元
* C++ 作为额外偏好单元

通常不建议在一个 OR 单元里塞太多不对称权重，
最好拆成多个单元，更稳定。

---

<!-- UID: frag-e0b04bb46b3d7464 -->
# 十一、完整流程伪代码

下面给你一版简化但够清楚的伪代码。

```python
def match_job(query_job, pattern_index, unit_index, combo_index, surface_index):
    # 1. 抽取表面表达
    surface_elements = extract_surface_elements(query_job)

    # 2. 语义归一
    canonical_elements = canonicalize(surface_elements)

    # 3. 解析要求单元
    requirement_units = build_requirement_units(canonical_elements, query_job)

    # 4. 计算每个要求单元的权重
    weighted_units = assign_unit_weights(requirement_units, query_job)

    # 5. 选择召回键
    recall_keys = select_recall_keys(weighted_units)

    # 6. 多路召回
    candidates = set()
    candidates |= exact_pattern_recall(weighted_units, pattern_index)
    candidates |= unit_recall(recall_keys, unit_index)
    candidates |= combo_recall(recall_keys, combo_index)
    candidates |= surface_recall(query_job, surface_index)
    candidates |= hierarchical_expansion_recall(weighted_units, unit_index)

    # 7. 对候选pattern打分
    scored_patterns = []
    for pattern in candidates:
        score = score_pattern(weighted_units, pattern)
        scored_patterns.append((pattern, score))

    top_patterns = top_k(scored_patterns, k=20)

    # 8. 在pattern内部做岗位实例精排
    scored_jobs = []
    for pattern, pattern_score in top_patterns:
        for job in pattern.member_jobs:
            final_score = score_job_instance(query_job, weighted_units, job, pattern_score)
            scored_jobs.append((job, final_score))

    # 9. 排序输出
    return sorted(scored_jobs, key=lambda x: x[1], reverse=True)
```

---

<!-- UID: frag-7522a9cf6fe0702c -->
# 十二、我对你下一步最建议的落地方向

现在你最该做的不是继续抽象，而是把这三件事先固定下来：


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 1. 要求单元的数据结构 -->

<!-- UID: frag-48d923fe4a167a94 -->

这是整个模型的地基。


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 2. 六类逻辑类型 -->

<!-- UID: frag-763ebbedf8d4417d -->

先不要无限扩展，先固定：

* SINGLE
* OR
* AND
* AT_LEAST_K
* PARENT_ANY_CHILD
* PARENT_WITH_CHILD_BONUS


---

<!-- 上下文: source_reference::design_guide::execution_suggestions_prompt :: source_reference::design_guide::execution_suggestions_prompt::document -->
<!-- 小标题: ## 3. 满足度函数 -->

<!-- UID: frag-cbb9007040bab466 -->

把每一类逻辑的满足度算式写死，跑起来

只要这三件事固定了，后面的召回、排序、pattern、评估都会清晰很多。

---

<!-- 上下文: source_reference::test_fixture::prompt_merge_equivalence :: source_reference::test_fixture::prompt_merge_equivalence::python_source -->

<!-- UID: frag-b44bfe9edbceac39 -->
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from core.anthropic_client import configure_llm_client, get_llm_client
from core.prompt_builder import (
    build_revision_prompt,
    build_seed_retarget_prompt,
    build_upgrade_revision_prompt,
)
from models.jd import JDProfile
from writers import master_writer as master_writer_module


EXPECTED_PROMPT_HASHES = {
    "build_revision_prompt": "1b2c27c056bc58e918336caf0362d7b07b7b871cda45394b965c25a61a73623d",
    "build_seed_retarget_prompt": "d2640f195691430867aec2526afaa7193d3328a1ec62b6d29963e2e7b8bc2de5",
    "build_upgrade_revision_prompt": "e91855093f935d3b871e5dfc89298a510a16cdbe4a87373153259838f6591aeb",
    "strict_revision_system_prompt": "6e5be20e6c84d700af09bf08c6fea6fba07587dc8639e0667f70114b7cb59c63",
    "upgrade_revision_system_prompt": "876266872c7cac3429703077309361577b211f98d6b88bf78688a507d5579907",
}


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sample_jd() -> JDProfile:
    return JDProfile(
        jd_id="jd-123",
        company="ExampleCo",
        title="Senior Backend Engineer",
        role_type="swe_backend",
        seniority="senior",
        tech_required=["Python", "Kafka", "AWS"],
        tech_preferred=["Go", "Kubernetes"],
    )


def _sample_review_result() -> dict:
    return {
        "revision_instructions": (
            "1. 强化 Summary 中的 backend ownership。\n"
            "2. 在 DiDi bullet 中补 Kafka 生产证据。"
        ),
        "revision_priority": ["补齐 Kafka 正文证据", "强化 senior backend scope"],
        "weighted_score": 91.4,
        "scores": {
            "r2_jd_fitness": {
                "findings": [
                    {
                        "severity": "high",
                        "field": "Experience",
                        "issue": "Kafka 仅出现在 Skills",
                        "fix": "在 DiDi bullet 写出生产使用场景",
                    }
                ]
            },
            "r4_rationality": {
                "findings": [
                    {
                        "severity": "medium",
                        "field": "Summary",
                        "issue": "Senior signal 偏弱",
                        "fix": "提升 owner/operator 表达",
                    }
                ]
            },
        },
    }


def _sample_resume_md() -> str:
    return (
        "## Professional Summary\n"
        "* **Backend:** Built services.\n\n"
        "## Skills\n"
        "* **Languages:** Python, SQL\n"
    )


def _sample_seed_resume_md() -> str:
    return (
        f"{_sample_resume_md()}\n"
        "## Experience\n"
        "### Engineer | ExampleCo · Platform\n"
        "*2024 | Remote*\n\n"
        "* Built pipelines.\n"
    )


def _sample_plan_text() -> str:
    return "## FINAL PLAN\n- TikTok: Python\n- DiDi: Kafka\n"


def _sample_top_candidate() -> dict:
    return {
        "missing_required": ["Kafka"],
        "label": "seed-main",
        "same_company": True,
        "seed_company_name": "ExampleCo",
        "source_job_id": "source-1",
        "company_anchor": True,
        "project_ids": [],
    }


def test_prompt_builder_hashes_remain_identical() -> None:
    jd = _sample_jd()
    review_result = _sample_review_result()
    resume_md = _sample_resume_md()
    seed_resume_md = _sample_seed_resume_md()
    plan_text = _sample_plan_text()

    samples = {
        "build_revision_prompt": build_revision_prompt(
            resume_md,
            review_result,
            plan_text=plan_text,
            tech_required=jd.tech_required,
            jd_title=jd.title,
            target_company=jd.company,
        ),
        "build_seed_retarget_prompt": build_seed_retarget_prompt(
            seed_resume_md,
            jd,
            seed_label="seed-main",
            route_mode="reuse",
            top_candidate=_sample_top_candidate(),
        ),
        "build_upgrade_revision_prompt": build_upgrade_revision_prompt(
            seed_resume_md,
            review_result,
            tech_required=jd.tech_required,
            jd_title=jd.title,
            target_company=jd.company,
            route_mode="reuse",
            seed_label="seed-main",
            plan_text=plan_text,
        ),
        "strict_revision_system_prompt": master_writer_module.STRICT_REVISION_SYSTEM_PROMPT,
        "upgrade_revision_system_prompt": master_writer_module.UPGRADE_REVISION_SYSTEM_PROMPT,
    }

    for key, value in samples.items():
        assert _sha256(value) == EXPECTED_PROMPT_HASHES[key], key


def test_master_writer_revision_prompts_stay_identical_on_kimi_path(monkeypatch) -> None:
    monkeypatch.setenv("KIMI_API_KEY", "test-kimi-key")
    configure_llm_client(
        enabled=True,
        write_model="kimi-for-coding",
        review_model="kimi-for-coding",
        transport="kimi",
    )
    client = get_llm_client()
    writer = master_writer_module.MasterWriter()
    captured: list[tuple[str, str, str]] = []

    monkeypatch.setattr(client, "is_available", lambda: True)
    monkeypatch.setattr(client, "_selected_transport", lambda: "kimi")

    def fake_run_kimi_api(prompt: str, model: str, system: str = "") -> str:
        captured.append((prompt, model, system))
        return _sample_resume_md()

    monkeypatch.setattr(client, "_run_kimi_api", fake_run_kimi_api)
    monkeypatch.setattr(master_writer_module, "get_llm_client", lambda: client)

    writer.revise(
        _sample_resume_md(),
        build_revision_prompt(
            _sample_resume_md(),
            _sample_review_result(),
            plan_text=_sample_plan_text(),
            tech_required=_sample_jd().tech_required,
            jd_title=_sample_jd().title,
            target_company=_sample_jd().company,
        ),
        rewrite_mode="strict",
    )
    writer.revise(
        _sample_seed_resume_md(),
        build_upgrade_revision_prompt(
            _sample_seed_resume_md(),
            _sample_review_result(),
            tech_required=_sample_jd().tech_required,
            jd_title=_sample_jd().title,
            target_company=_sample_jd().company,
            route_mode="reuse",
            seed_label="seed-main",
            plan_text=_sample_plan_text(),
        ),
        rewrite_mode="upgrade",
    )

    assert [item[1] for item in captured] == ["kimi-for-coding", "kimi-for-coding"]
    assert _sha256(captured[0][0]) == EXPECTED_PROMPT_HASHES["build_revision_prompt"]
    assert _sha256(captured[0][2]) == EXPECTED_PROMPT_HASHES["strict_revision_system_prompt"]
    assert _sha256(captured[1][0]) == EXPECTED_PROMPT_HASHES["build_upgrade_revision_prompt"]
    assert _sha256(captured[1][2]) == EXPECTED_PROMPT_HASHES["upgrade_revision_system_prompt"]

---
