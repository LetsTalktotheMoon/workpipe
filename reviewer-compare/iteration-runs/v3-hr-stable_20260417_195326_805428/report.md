# v3_hr_stable 结果

生成时间: 2026-04-17T20:02:54

| Case | 分数 | 结论 | 耗时(秒) | Critical | High | Medium | 主要规则 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| same/Microsoft | 90.3 | fail | 72.0 | 0 | 1 | 5 | P1-042, P2-001, P3B-001, P3C-011, P3D-001 |
| same/Google | 94.1 | pass | 65.0 | 0 | 1 | 2 | P2-001, P3A-002, P3E-013 |
| same/Amazon | 95.0 | pass | 60.0 | 0 | 1 | 4 | P1-040, P2-001, P2-030, P3C-010, P3E-013 |
| same/AWS | 97.5 | pass | 49.0 | 0 | 0 | 2 | P1-042, P2-001 |
| extra/Dataminr-Infra | 99.0 | pass | 40.0 | 0 | 0 | 1 | P2-010 |
| extra/Zoox-LLM | 96.8 | pass | 66.0 | 0 | 1 | 2 | P1-030, P3C-010, P3D-001 |
| extra/Synechron-Backend | 99.2 | pass | 51.0 | 0 | 0 | 2 | P1-040, P2-040 |
| extra/CapitalOne-AI | 87.9 | fail | 48.0 | 0 | 2 | 3 | P1-042, P2-001, P2-020, P3B-010, P3D-001 |
| extra/Ramp-Platform | 97.1 | pass | 51.0 | 0 | 0 | 3 | P1-040, P3B-003, P3D-001 |
| extra/HealthEquity-DotNet | 89.6 | fail | 66.0 | 0 | 1 | 2 | P2-001, P3B-001, P3B-004 |

## same/Microsoft

- 目标岗位: Software Engineer II - Azure Storage @ Microsoft
- 分数/结论: 90.3 / fail
- 耗时: 72.0 秒
- 严重度计数: critical=0, high=1, medium=5, low=0
- 规则 ID: P1-042, P2-001, P3B-001, P3C-011, P3D-001

### 优先修改项
- [MUST] 把 Summary 第一句改成直接的 backend / distributed systems 定位，删除或后移“transitioning from data analytics”这类转向叙事。
- [MUST] 在 Skills 中显式写出 `Distributed Systems`，并在最相关的 TikTok bullet 里保留一条能证明分布式服务边界的证据。
- [MUST] 给 TikTok 和 DiDi 的最关键 bullet 各补一个可追问的 scope 指标，让百分比结果退居次位。
- [SHOULD] 收敛实习段的语言栈表述，只保留 2-3 门主语言，其余语言放到具体集成场景里；同时去掉 `team-maintained`、`existing`、`internal` 等限定词的加粗。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/same-microsoft/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/same-microsoft/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/same-microsoft/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/same-microsoft/codex.json`

## same/Google

- 目标岗位: Software Engineer III, Full Stack, Google Cloud Platforms @ Google
- 分数/结论: 94.1 / pass
- 耗时: 65.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P2-001, P3A-002, P3E-013

### 优先修改项
- [MUST] 在 `Skills > Cloud` 中补上 `AWS Bedrock`，让 TikTok 项目里出现的具体平台名有技能栏支撑。
- [SHOULD] 给 TikTok 的知识检索项目补一条数据边界限定语，明确是 internal docs / no user data / no production data。
- [SHOULD] 重写 Summary 第一句，先落到 full-stack / security / platform 角色锚点，再写从 data analysis 的迁移背景。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/same-google/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/same-google/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/same-google/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/same-google/codex.json`

## same/Amazon

- 目标岗位: Machine Learning Engineer II , AGI Customization @ Amazon
- 分数/结论: 95.0 / pass
- 耗时: 60.0 秒
- 严重度计数: critical=0, high=1, medium=4, low=0
- 规则 ID: P1-040, P2-001, P2-030, P3C-010, P3E-013

### 优先修改项
- [MUST] Add explicit boundary language to the TikTok Bedrock / RAG bullets so the Security-team work is clearly internal and non-user-data-facing.
- [MUST] Tighten TikTok bullets to one primary stack per bullet and remove nonessential tech names to avoid a stack-dumping read.
- [SHOULD] Reorder Summary and Skills so ML customization is front-loaded before the analytics transition and generic programming line.
- [NICE] Bold the main scope and impact numbers so the strongest signals pop on first scan.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/same-amazon/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/same-amazon/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/same-amazon/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/same-amazon/codex.json`

## same/AWS

- 目标岗位: Software Development Engineer II - Builder Experience, GenAI, GenAI, Codex @ Amazon Web Services (AWS)
- 分数/结论: 97.5 / pass
- 耗时: 49.0 秒
- 严重度计数: critical=0, high=0, medium=2, low=0
- 规则 ID: P1-042, P2-001

### 优先修改项
- [SHOULD] Rewrite the first Summary chunk to lead with a direct backend/security role identity instead of `transitioning from analytics`.
- [SHOULD] Unbold qualifier words like `team-maintained`; keep bolding for technologies and metrics only.
- [NICE] If you want a stronger AWS Builder Experience fit, add one explicit scope signal in the latest role or project (team size, event volume, SLA, or review/rollout scope).
- [NICE] Keep the rest of the structure unchanged; the experience ordering and immutable fields are already consistent.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/same-aws/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/same-aws/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/same-aws/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/same-aws/codex.json`

## extra/Dataminr-Infra

- 目标岗位: Senior Software Engineer, Backend @ Dataminr
- 分数/结论: 99.0 / pass
- 耗时: 40.0 秒
- 严重度计数: critical=0, high=0, medium=1, low=0
- 规则 ID: P2-010

### 优先修改项
- [SHOULD] Replace the third Summary header with a stronger cognition label such as 'Systems judgment:' or 'Decision-making:'.
- [NICE] Keep the current TikTok and DiDi bullets as-is; they already provide the needed backend and distributed-systems bridge for Dataminr.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-dataminr-infra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-dataminr-infra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-dataminr-infra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-dataminr-infra/codex.json`

## extra/Zoox-LLM

- 目标岗位: Machine Learning Engineer, 3D Simulation @ Zoox
- 分数/结论: 96.8 / pass
- 耗时: 66.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P1-030, P3C-010, P3D-001

### 优先修改项
- [MUST] Narrow the headline stack to C++/Python and stop presenting Java/Go as co-equal core languages.
- [MUST] Add one Tier-1 scale anchor to the newest relevant experience so the impact is not only percentage deltas.
- [SHOULD] Rework the summary bullets into verb-led, Zoox-relevant framing instead of descriptor-led positioning copy.
- [NICE] Compress secondary stack words in the TikTok section so the senior MLE signal feels focused.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-zoox-llm/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-zoox-llm/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-zoox-llm/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-zoox-llm/codex.json`

## extra/Synechron-Backend

- 目标岗位: Python Fullstack Engineer @ Synechron
- 分数/结论: 99.2 / pass
- 耗时: 51.0 秒
- 严重度计数: critical=0, high=0, medium=2, low=0
- 规则 ID: P1-040, P2-040

### 优先修改项
- [SHOULD] 把 `Skills` 里的 `APIs` 类别改成更准确的 `Platform / DevOps` 或 `Workflow / DevOps`。
- [SHOULD] 统一强化 TikTok bullet 4 的视觉层级，把 `GitHub Actions` 和主结果指标加粗。
- [NICE] 保持其余结构不变，当前内容主线已经能过 ATS 和首屏扫读。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-synechron-backend/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-synechron-backend/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-synechron-backend/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-synechron-backend/codex.json`

## extra/CapitalOne-AI

- 目标岗位: Manager, Data Analysis - Card Services @ Capital One
- 分数/结论: 87.9 / fail
- 耗时: 48.0 秒
- 严重度计数: critical=0, high=2, medium=3, low=0
- 规则 ID: P1-042, P2-001, P2-020, P3B-010, P3D-001

### 优先修改项
- [MUST] 处理 Manager 角色与现有经历之间的结构性错配：如果目标真是 Manager，补 people/team ownership 证据；否则改投更匹配的 senior IC/lead analyst 岗位。
- [MUST] 把 Professional Summary 第一句改成直接角色方向，而不是 Candidate 自我标签，提升首屏抓手。
- [SHOULD] 为 TikTok 首条 bullet 补一个 tier 1 规模或 scope 锚点，避免整段只靠百分比。
- [NICE] 取消 Experience 里修饰语的加粗，只保留技术名词和量化结果加粗。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-capitalone-ai/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-capitalone-ai/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-capitalone-ai/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-capitalone-ai/codex.json`

## extra/Ramp-Platform

- 目标岗位: Software Engineer, Infrastructure @ Ramp
- 分数/结论: 97.1 / pass
- 耗时: 51.0 秒
- 严重度计数: critical=0, high=0, medium=3, low=0
- 规则 ID: P1-040, P3B-003, P3D-001

### 优先修改项
- [MUST] Add an explicit bridge to Ramp's finance-infrastructure context in the Summary or the most relevant bullet so the screener can map your backend/security experience to the role immediately.
- [MUST] Add one concrete scope anchor to the newest experience so the quantification is not mostly tier-2 deltas.
- [SHOULD] Bold the core technical nouns in the Summary for faster scanability.
- [NICE] If space allows, replace one redundant percentage-style bullet with ownership or scope detail instead of another delta.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-ramp-platform/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-ramp-platform/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-ramp-platform/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-ramp-platform/codex.json`

## extra/HealthEquity-DotNet

- 目标岗位: Software Engineer II @ HealthEquity
- 分数/结论: 89.6 / fail
- 耗时: 66.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P2-001, P3B-001, P3B-004

### 优先修改项
- [MUST] 在 Skills 里补出 JD 的 exact `Agile` 和 `Apache Spark`，不要只靠 `Scrum` / `Spark SQL` 代替，并在最相关经历里再写一次同样的 exact 词。
- [MUST] 把 Summary 第一句改成直接角色锚点，删掉或后置“transitioning from data analytics”的首屏转型叙事。
- [SHOULD] 补一条迁移桥接，把安全/审计敏感/运营工具经验明确连到 healthcare consumer / regulated workflow 场景。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-healthequity-dotnet/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-healthequity-dotnet/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-healthequity-dotnet/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428/extra-healthequity-dotnet/codex.json`
