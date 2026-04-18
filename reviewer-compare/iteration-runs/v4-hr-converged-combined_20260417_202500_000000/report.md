# v4_hr_converged 结果

生成时间: 2026-04-17T20:23:53

| Case | 分数 | 结论 | 耗时(秒) | Critical | High | Medium | 主要规则 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| same/Microsoft | 95.8 | pass | 59.0 | 0 | 1 | 2 | P2-001, P3C-010, P3D-001 |
| same/Google | 86.2 | fail | 87.0 | 1 | 1 | 3 | P1-040, P1-042, P2-001, P3A-002, P3A-003 |
| same/Amazon | 95.3 | pass | 60.0 | 0 | 1 | 3 | P1-042, P2-001, P3C-010, P3D-001 |
| same/AWS | 97.7 | pass | 59.0 | 0 | 0 | 2 | P2-001, P3E-013 |
| extra/Dataminr-Infra | 98.5 | pass | 49.0 | 0 | 0 | 2 | P1-040, P2-010 |
| extra/Zoox-LLM | 96.4 | pass | 65.0 | 0 | 1 | 3 | P1-040, P1-042, P3B-003, P3C-010 |
| extra/Synechron-Backend | 100.0 | pass | 32.0 | 0 | 0 | 0 | none |
| extra/CapitalOne-AI | 88.6 | fail | 59.0 | 0 | 1 | 3 | P2-001, P3B-004, P3B-010, P3D-001 |
| extra/Ramp-Platform | 100.0 | pass | 24.0 | 0 | 0 | 0 | none |
| extra/HealthEquity-DotNet | 88.6 | pass | 73.0 | 0 | 2 | 3 | P1-042, P2-001, P2-040, P3B-002, P3D-001 |

## same/Microsoft

- 目标岗位: Software Engineer II - Azure Storage @ Microsoft
- 分数/结论: 95.8 / pass
- 耗时: 59.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P2-001, P3C-010, P3D-001

### 优先修改项
- [MUST] Rewrite Summary sentence 1 to lead with backend/distributed systems, not the transition narrative.
- [MUST] Decompress the TikTok segment: keep a small primary stack and move supporting languages/tools into integration context.
- [SHOULD] Add one first-screen scale metric to TikTok to replace pure percentage-delta signaling.
- [NICE] Keep Skills as-is unless you need to trim secondary tools after the rewrite.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/same-microsoft/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/same-microsoft/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/same-microsoft/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/same-microsoft/codex.json`

## same/Google

- 目标岗位: Software Engineer III, Full Stack, Google Cloud Platforms @ Google
- 分数/结论: 86.2 / fail
- 耗时: 87.0 秒
- 严重度计数: critical=1, high=1, medium=3, low=0
- 规则 ID: P1-040, P1-042, P2-001, P3A-002, P3A-003

### 优先修改项
- [MUST] 把 Summary 首句改成目标角色/领域导向，去掉首屏的转型叙事。
- [MUST] 删掉或补证据支撑 `data structures` / `algorithms` 这条 Summary 主张。
- [MUST] 若真实使用过 `AWS Bedrock`，把它补进 Skills；否则把 TikTok retrieval bullet 收敛成更泛化的 AWS 内部检索表述。
- [SHOULD] 把第一屏最强的数字和 scope 信号加粗，同时去掉 `team-maintained`、`existing`、`internal` 这类修饰语的加粗。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/same-google/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/same-google/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/same-google/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/same-google/codex.json`

## same/Amazon

- 目标岗位: Machine Learning Engineer II , AGI Customization @ Amazon
- 分数/结论: 95.3 / pass
- 耗时: 60.0 秒
- 严重度计数: critical=0, high=1, medium=3, low=0
- 规则 ID: P1-042, P2-001, P3C-010, P3D-001

### 优先修改项
- [MUST] 收敛 Summary 和 Skills 里的主语言表述，不要把 Java/C++/Python/Go 都写成同一层级的核心主栈。
- [MUST] 去掉 `team-maintained`、`intern-owned`、`team-owned` 这类限定词的加粗，只保留技术名词和关键规模数字加粗。
- [SHOULD] 把 Summary 第一段的转型叙事后置，首屏先讲当前 ML/LLM customization 方向。
- [SHOULD] 给 TikTok 最新经历补一个 Tier1 规模锚点，提升量化可信度。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/same-amazon/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/same-amazon/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/same-amazon/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/same-amazon/codex.json`

## same/AWS

- 目标岗位: Software Development Engineer II - Builder Experience, GenAI, GenAI, Codex @ Amazon Web Services (AWS)
- 分数/结论: 97.7 / pass
- 耗时: 59.0 秒
- 严重度计数: critical=0, high=0, medium=2, low=0
- 规则 ID: P2-001, P3E-013

### 优先修改项
- [SHOULD] Rewrite Summary sentence 1 to lead with backend role and domain signal instead of transition framing.
- [SHOULD] Add an explicit data-boundary qualifier to the TikTok Bedrock/RAG project bullet.
- [NICE] Keep the rest of the structure; it already maps well to the AWS backend brief.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/same-aws/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/same-aws/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/same-aws/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/same-aws/codex.json`

## extra/Dataminr-Infra

- 目标岗位: Senior Software Engineer, Backend @ Dataminr
- 分数/结论: 98.5 / pass
- 耗时: 49.0 秒
- 严重度计数: critical=0, high=0, medium=2, low=0
- 规则 ID: P1-040, P2-010

### 优先修改项
- [SHOULD] Replace the third Summary header `Structured Problem Solver` with a more role-specific cognition header tied to backend systems judgment.
- [SHOULD] Bold the most persuasive metrics and scope markers in Experience and Project bullets so the strongest evidence stands out on first scan.
- [NICE] Tighten the Summary wording to surface backend + distributed systems positioning even earlier.
- [NICE] If you want a stronger first-screen bridge to Dataminr, mention event-driven or risk/alerting context once in the Summary.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-dataminr-infra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-dataminr-infra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-dataminr-infra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-dataminr-infra/codex.json`

## extra/Zoox-LLM

- 目标岗位: Machine Learning Engineer, 3D Simulation @ Zoox
- 分数/结论: 96.4 / pass
- 耗时: 65.0 秒
- 严重度计数: critical=0, high=1, medium=3, low=0
- 规则 ID: P1-040, P1-042, P3B-003, P3C-010

### 优先修改项
- [MUST] Rework the TikTok intern section so C++ and Python are the primary story, and the other languages/tools are framed as supporting integration rather than equal-weight daily stack claims.
- [SHOULD] Add one explicit bridge sentence that maps the replay/evaluation work to simulation-adjacent validation for Zoox.
- [SHOULD] Bold the clearest scope markers such as `13-person` and `20+ city` to improve scanability.
- [NICE] Use ownership/boundary bolding consistently only where it clarifies scope.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-zoox-llm/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-zoox-llm/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-zoox-llm/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-zoox-llm/codex.json`

## extra/Synechron-Backend

- 目标岗位: Python Fullstack Engineer @ Synechron
- 分数/结论: 100.0 / pass
- 耗时: 32.0 秒
- 严重度计数: critical=0, high=0, medium=0, low=0
- 规则 ID: none

### 优先修改项

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-synechron-backend/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-synechron-backend/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-synechron-backend/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-synechron-backend/codex.json`

## extra/CapitalOne-AI

- 目标岗位: Manager, Data Analysis - Card Services @ Capital One
- 分数/结论: 88.6 / fail
- 耗时: 59.0 秒
- 严重度计数: critical=0, high=1, medium=3, low=0
- 规则 ID: P2-001, P3B-004, P3B-010, P3D-001

### 优先修改项
- [MUST] 如果没有真实 people-management 经验，不要把这份简历继续投向 Manager；若有真实经历，在最相关经历里补 1 条团队/项目 ownership 证据。
- [MUST] 把 Summary 第一句改成角色方向 + 领域信号，去掉 `Candidate` 式 framing。
- [MUST] 在 TikTok 最新经历前置一个可追问的规模/边界信号，不要只靠百分比。
- [SHOULD] 增加一条面向 Card Services 的迁移桥接，把 security / ops / reconciliation 经验翻成金融分析语境。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-capitalone-ai/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-capitalone-ai/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-capitalone-ai/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-capitalone-ai/codex.json`

## extra/Ramp-Platform

- 目标岗位: Software Engineer, Infrastructure @ Ramp
- 分数/结论: 100.0 / pass
- 耗时: 24.0 秒
- 严重度计数: critical=0, high=0, medium=0, low=0
- 规则 ID: none

### 优先修改项

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-ramp-platform/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-ramp-platform/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-ramp-platform/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-ramp-platform/codex.json`

## extra/HealthEquity-DotNet

- 目标岗位: Software Engineer II @ HealthEquity
- 分数/结论: 88.6 / pass
- 耗时: 73.0 秒
- 严重度计数: critical=0, high=2, medium=3, low=0
- 规则 ID: P1-042, P2-001, P2-040, P3B-002, P3D-001

### 优先修改项
- [MUST] 把 Summary 第一条改成岗位前置的 backend/security headline，去掉 `transitioning from data analytics` 这种转型开场。
- [MUST] 在最相关的 China-company 经历里补出 MongoDB 的直接使用证据；不要只停留在 `MongoDB-compatible` 这种间接表述。
- [SHOULD] 给 TikTok 段补一个 tier-1 scope 信号，降低纯百分比结果的观感。
- [NICE] 把 `APIs` 这种泛分类改成更具体、更适合 6-8 秒扫读的技能分组。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-healthequity-dotnet/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-healthequity-dotnet/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-healthequity-dotnet/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v4-hr-converged-combined_20260417_202500_000000/extra-healthequity-dotnet/codex.json`
