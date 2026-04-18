# v5_hr_gate 结果

生成时间: 2026-04-17T20:35:00

| Case | 分数 | 结论 | 耗时(秒) | Critical | High | Medium | 主要规则 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| same/Microsoft | 95.8 | pass | 69.0 | 0 | 1 | 2 | P2-001, P3C-010, P3D-001 |
| same/Google | 94.4 | pass | 48.0 | 0 | 1 | 1 | P2-001, P3A-002 |
| same/Amazon | 97.3 | pass | 61.0 | 0 | 1 | 2 | P1-042, P2-030, P3C-010 |
| same/AWS | 96.3 | pass | 60.0 | 0 | 1 | 2 | P1-042, P2-001, P3C-010 |
| extra/Dataminr-Infra | 95.5 | pass | 58.0 | 0 | 0 | 8 | P1-030, P1-040, P1-042, P1-051, P2-010, P3D-001 |
| extra/Zoox-LLM | 96.5 | pass | 57.0 | 0 | 0 | 4 | P1-042, P3B-003, P3C-011, P3D-001 |
| extra/Synechron-Backend | 100.0 | pass | 33.0 | 0 | 0 | 0 | none |
| extra/CapitalOne-AI | 91.9 | fail | 55.0 | 0 | 1 | 2 | P1-040, P2-001, P3B-010 |
| extra/Ramp-Platform | 100.0 | pass | 60.0 | 0 | 0 | 0 | none |
| extra/HealthEquity-DotNet | 97.0 | pass | 85.0 | 0 | 0 | 3 | P1-040, P1-042, P2-001 |

## same/Microsoft

- 目标岗位: Software Engineer II - Azure Storage @ Microsoft
- 分数/结论: 95.8 / pass
- 耗时: 69.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P2-001, P3C-010, P3D-001

### 优先修改项
- [MUST] Rewrite the first Summary sentence to lead with backend/distributed-systems positioning, not the transition story.
- [MUST] Narrow the headline stack claim so the resume does not read as 6+ languages of primary expertise.
- [SHOULD] Add a tier-1 scope/scale metric to the TikTok section.
- [NICE] Keep the rest of the experience bullets as proof points; do not touch immutable titles, dates, or locations.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/same-microsoft/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/same-microsoft/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/same-microsoft/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/same-microsoft/codex.json`

## same/Google

- 目标岗位: Software Engineer III, Full Stack, Google Cloud Platforms @ Google
- 分数/结论: 94.4 / pass
- 耗时: 48.0 秒
- 严重度计数: critical=0, high=1, medium=1, low=0
- 规则 ID: P2-001, P3A-002

### 优先修改项
- [MUST] Rewrite the opening Summary sentence to lead with a clear full-stack SWE role/domain anchor instead of the transition narrative.
- [MUST] Add AWS Bedrock to Skills, or soften the project wording so the stack in the body matches the stack list.
- [SHOULD] If you have one more concrete scope cue, add it to the first bullet of the newest role to strengthen the Google Cloud platform fit.
- [NICE] Keep the current structure and quantification style; the resume is otherwise internally coherent.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/same-google/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/same-google/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/same-google/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/same-google/codex.json`

## same/Amazon

- 目标岗位: Machine Learning Engineer II , AGI Customization @ Amazon
- 分数/结论: 97.3 / pass
- 耗时: 61.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P1-042, P2-030, P3C-010

### 优先修改项
- [MUST] 收敛 TikTok 实习段的语言栈表述：保留 1-2 个主语言，把其余语言改写成支持性集成/适配工作，避免像四语言堆砌。
- [MUST] 把 Skills 的首行改成 AI/ML / Machine Learning / LLM / RAG，让首屏直接对齐 MLE II / AGI Customization。
- [SHOULD] 取消 `team-maintained`、`intern-owned`、`team-owned` 这类限定词的加粗，只保留技术和量化结果加粗。
- [NICE] 若后续重排版，再顺手检查背景行里的 scope 数字是否保持视觉一致，但不要改不可变字段。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/same-amazon/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/same-amazon/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/same-amazon/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/same-amazon/codex.json`

## same/AWS

- 目标岗位: Software Development Engineer II - Builder Experience, GenAI, GenAI, Codex @ Amazon Web Services (AWS)
- 分数/结论: 96.3 / pass
- 耗时: 60.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P1-042, P2-001, P3C-010

### 优先修改项
- [MUST] Rewrite the Summary opening to lead with a direct role anchor instead of `Transition Profile` language.
- [MUST] Recast the TikTok internship so the language/tool stack reads as two core languages plus supporting embedded/test work, not four equal primary stacks.
- [SHOULD] Remove bold styling from qualifiers like `team-maintained` and `existing` so emphasis stays on technologies and quantified outcomes.
- [NICE] Tighten the first-screen Summary so the backend/security direction is visible within the first clause.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/same-aws/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/same-aws/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/same-aws/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/same-aws/codex.json`

## extra/Dataminr-Infra

- 目标岗位: Senior Software Engineer, Backend @ Dataminr
- 分数/结论: 95.5 / pass
- 耗时: 58.0 秒
- 严重度计数: critical=0, high=0, medium=8, low=0
- 规则 ID: P1-030, P1-040, P1-042, P1-051, P2-010, P3D-001

### 优先修改项
- [SHOULD] Compress the Skills section into 3 short category rows that stay within the line-word cap.
- [SHOULD] Add one Tier 1 scope metric to the TikTok first bullet so the latest role has a clear scale anchor.
- [SHOULD] Rewrite the third Summary header into a stronger cognition label and make the Summary bullets more verb-led.
- [NICE] Remove bold from qualifiers and reserve bold for the strongest metrics and core technologies.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-dataminr-infra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-dataminr-infra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-dataminr-infra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-dataminr-infra/codex.json`

## extra/Zoox-LLM

- 目标岗位: Machine Learning Engineer, 3D Simulation @ Zoox
- 分数/结论: 96.5 / pass
- 耗时: 57.0 秒
- 严重度计数: critical=0, high=0, medium=4, low=0
- 规则 ID: P1-042, P3B-003, P3C-011, P3D-001

### 优先修改项
- [MUST] 在 Summary 和 TikTok 项目里把 `replay sandbox` 明确写成 simulation-like validation / scenario replay 体系，直接建立与 Zoox 3D Simulation 的迁移桥接。
- [MUST] 收敛 TikTok 段的语言栈表达，标清主语言与辅助语言，避免看起来像 4 种编程语言的日常主栈。
- [SHOULD] 给最新经历补一个可追问的规模锚点，减少纯百分比叙事对首屏说服力的依赖。
- [NICE] 取消 `team-maintained`、`intern-owned` 这类限定词的加粗，只保留技术名词和量化信号加粗。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-zoox-llm/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-zoox-llm/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-zoox-llm/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-zoox-llm/codex.json`

## extra/Synechron-Backend

- 目标岗位: Python Fullstack Engineer @ Synechron
- 分数/结论: 100.0 / pass
- 耗时: 33.0 秒
- 严重度计数: critical=0, high=0, medium=0, low=0
- 规则 ID: none

### 优先修改项

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-synechron-backend/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-synechron-backend/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-synechron-backend/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-synechron-backend/codex.json`

## extra/CapitalOne-AI

- 目标岗位: Manager, Data Analysis - Card Services @ Capital One
- 分数/结论: 91.9 / fail
- 耗时: 55.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P1-040, P2-001, P3B-010

### 优先修改项
- [MUST] Resolve the manager-scope gap with truthful lead/ownership evidence in the most relevant experience, or stop positioning this resume for Manager roles.
- [MUST] Rework the first Summary sentence to be role-first rather than 'Candidate'-first, while preserving the 3+ years Python/SQL/Spark/ETL signal.
- [SHOULD] Bold the most important scope/result numbers in each experience section to improve scanability.
- [NICE] Keep the China-company stacks as-is; no localization translation changes are needed here.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-capitalone-ai/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-capitalone-ai/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-capitalone-ai/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-capitalone-ai/codex.json`

## extra/Ramp-Platform

- 目标岗位: Software Engineer, Infrastructure @ Ramp
- 分数/结论: 100.0 / pass
- 耗时: 60.0 秒
- 严重度计数: critical=0, high=0, medium=0, low=0
- 规则 ID: none

### 优先修改项

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-ramp-platform/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-ramp-platform/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-ramp-platform/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-ramp-platform/codex.json`

## extra/HealthEquity-DotNet

- 目标岗位: Software Engineer II @ HealthEquity
- 分数/结论: 97.0 / pass
- 耗时: 85.0 秒
- 严重度计数: critical=0, high=0, medium=3, low=0
- 规则 ID: P1-040, P1-042, P2-001

### 优先修改项
- [MUST] Reframe Summary sentence 1 to lead with a direct backend/security role statement instead of a transition narrative.
- [MUST] Bold the missing high-signal tokens in the body and Summary (`3+ years`, `Agile`, `Bedrock`, `team-maintained`, `internal`, `operator-facing`).
- [SHOULD] Keep the rest of the content unchanged; do not remove any technical evidence that supports JD fit.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-healthequity-dotnet/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-healthequity-dotnet/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-healthequity-dotnet/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v5-hr-gate_20260417_202514_652388/extra-healthequity-dotnet/codex.json`
