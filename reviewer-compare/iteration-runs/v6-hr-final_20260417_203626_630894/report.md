# v6_hr_final 结果

生成时间: 2026-04-17T20:46:32

| Case | 分数 | 结论 | 耗时(秒) | Critical | High | Medium | 主要规则 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| same/Microsoft | 91.8 | fail | 63.0 | 0 | 1 | 2 | P2-001, P3B-001, P3C-011 |
| same/Google | 91.2 | pass | 75.0 | 0 | 2 | 4 | P1-040, P1-042, P2-001, P3A-002, P3C-010, P3D-001 |
| same/Amazon | 95.8 | pass | 76.0 | 0 | 1 | 3 | P1-040, P1-042, P2-001, P3C-010 |
| same/AWS | 96.5 | pass | 60.0 | 0 | 0 | 3 | P1-042, P2-001, P2-010 |
| extra/Dataminr-Infra | 98.5 | pass | 48.0 | 0 | 0 | 2 | P1-042, P2-010 |
| extra/Zoox-LLM | 98.6 | pass | 48.0 | 0 | 0 | 1 | P3B-003 |
| extra/Synechron-Backend | 99.7 | pass | 78.0 | 0 | 0 | 1 | P2-040 |
| extra/CapitalOne-AI | 96.2 | pass | 55.0 | 0 | 0 | 4 | P1-040, P2-001, P3D-001, P3E-013 |
| extra/Ramp-Platform | 97.3 | pass | 39.0 | 0 | 1 | 2 | P1-042, P3C-010, P3D-001 |
| extra/HealthEquity-DotNet | 94.5 | pass | 64.0 | 0 | 1 | 2 | P1-040, P2-001, P3D-001 |

## same/Microsoft

- 目标岗位: Software Engineer II - Azure Storage @ Microsoft
- 分数/结论: 91.8 / fail
- 耗时: 63.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P2-001, P3B-001, P3C-011

### 优先修改项
- [MUST] 在最相关的后端经历里补出“Distributed Systems”这个命名信号，并让它和 C++/gRPC/Kafka 的证据同框出现。
- [MUST] 把 Summary 第一句改成直接的后端/分布式系统定位，把“从数据分析转向后端”放到后半句。
- [SHOULD] 收敛 TikTok 实习段的语言栈叙事，避免 5 门语言看起来都像主工作栈。
- [NICE] 其余量化保持即可，优先让首屏更快读出“Azure Storage 相关的分布式后端工程师”信号。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/same-microsoft/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/same-microsoft/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/same-microsoft/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/same-microsoft/codex.json`

## same/Google

- 目标岗位: Software Engineer III, Full Stack, Google Cloud Platforms @ Google
- 分数/结论: 91.2 / pass
- 耗时: 75.0 秒
- 严重度计数: critical=0, high=2, medium=4, low=0
- 规则 ID: P1-040, P1-042, P2-001, P3A-002, P3C-010, P3D-001

### 优先修改项
- [MUST] 把 Summary 第一条改成目标角色锚点，而不是转向叙事开场。
- [MUST] 处理 TikTok 项目里的 AWS Bedrock：要么补进 Skills，要么改成更抽象的 AWS-hosted retrieval 表述。
- [MUST] 收敛 TikTok 段的语言栈呈现，明确主语言与支持性技术，避免一段里同时像在用 5-6 门语言。
- [SHOULD] 给 TikTok 的关键结果补 scope 数字，并把最重要的量化信号加粗；同时去掉对 modifiers 的加粗。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/same-google/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/same-google/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/same-google/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/same-google/codex.json`

## same/Amazon

- 目标岗位: Machine Learning Engineer II , AGI Customization @ Amazon
- 分数/结论: 95.8 / pass
- 耗时: 76.0 秒
- 严重度计数: critical=0, high=1, medium=3, low=0
- 规则 ID: P1-040, P1-042, P2-001, P3C-010

### 优先修改项
- [MUST] Rewrite Summary sentence 1 to lead with the target ML/backend role, then mention the analytics transition later.
- [MUST] Narrow the apparent primary stack in the TikTok internship so it does not read like one broad daily-use language/tool pile-up.
- [SHOULD] Remove bold from modifier phrases like `team-maintained` and `team-owned`, and reserve bold for tech nouns plus the strongest metrics.
- [NICE] Standardize metric emphasis so each bullet highlights one headline result clearly.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/same-amazon/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/same-amazon/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/same-amazon/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/same-amazon/codex.json`

## same/AWS

- 目标岗位: Software Development Engineer II - Builder Experience, GenAI, GenAI, Codex @ Amazon Web Services (AWS)
- 分数/结论: 96.5 / pass
- 耗时: 60.0 秒
- 严重度计数: critical=0, high=0, medium=3, low=0
- 规则 ID: P1-042, P2-001, P2-010

### 优先修改项
- [SHOULD] 把 Summary 第一句改成直接的后端/安全角色锚点，弱化 `transitioning from analytics` 的首屏存在感。
- [SHOULD] 把第三句的 `GenAI Systems Context` 换成 cognition 型 header，例如 `Pattern recognition:`，让围棋经历更像能力证据而不是背景说明。
- [NICE] 取消修饰语的加粗，只保留技术栈名词、规模和结果数字加粗，避免视觉权重失衡。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/same-aws/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/same-aws/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/same-aws/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/same-aws/codex.json`

## extra/Dataminr-Infra

- 目标岗位: Senior Software Engineer, Backend @ Dataminr
- 分数/结论: 98.5 / pass
- 耗时: 48.0 秒
- 严重度计数: critical=0, high=0, medium=2, low=0
- 规则 ID: P1-042, P2-010

### 优先修改项
- [SHOULD] Remove bolding from qualifying modifiers in the body bullets; keep bolding limited to technical nouns and scope signals.
- [SHOULD] Rewrite Summary sentence 3 to use a stronger cognition header that reads more senior and more backend-oriented.
- [NICE] If you want slightly stronger seniority signaling, add one explicit scope or scale anchor to the most relevant backend bullet.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-dataminr-infra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-dataminr-infra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-dataminr-infra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-dataminr-infra/codex.json`

## extra/Zoox-LLM

- 目标岗位: Machine Learning Engineer, 3D Simulation @ Zoox
- 分数/结论: 98.6 / pass
- 耗时: 48.0 秒
- 严重度计数: critical=0, high=0, medium=1, low=0
- 规则 ID: P3B-003

### 优先修改项
- [SHOULD] 在 Summary 或 TikTok 最前面的 bullet 里补一条明确的 simulation/autonomy 迁移桥接，把 replayable testing、synthetic evaluation、C++/Python validation 讲成可迁移到 3D simulation 的能力。
- [NICE] 如果要继续增强首屏说服力，可以把最相关的 C++/Python 经验前置到 TikTok 段落，并用一条更明确的场景验证/回放表述收束。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-zoox-llm/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-zoox-llm/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-zoox-llm/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-zoox-llm/codex.json`

## extra/Synechron-Backend

- 目标岗位: Python Fullstack Engineer @ Synechron
- 分数/结论: 99.7 / pass
- 耗时: 78.0 秒
- 严重度计数: critical=0, high=0, medium=1, low=0
- 规则 ID: P2-040

### 优先修改项
- [SHOULD] Rename the `APIs` skills bucket to a more specific category so the first scan reads as backend/fullstack rather than miscellaneous tooling.
- [NICE] If you want cleaner ATS parsing, split `NoSQL`, `Jenkins`, `Gitlab Ci`, and `Agile` into function-based groups instead of one mixed bucket.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-synechron-backend/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-synechron-backend/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-synechron-backend/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-synechron-backend/codex.json`

## extra/CapitalOne-AI

- 目标岗位: Manager, Data Analysis - Card Services @ Capital One
- 分数/结论: 96.2 / pass
- 耗时: 55.0 秒
- 严重度计数: critical=0, high=0, medium=4, low=0
- 规则 ID: P1-040, P2-001, P3D-001, P3E-013

### 优先修改项
- [MUST] 给 TikTok Security 的 Bedrock/RAG 表述补上明确数据边界限定语（internal/sandbox/no user data/prod data），避免安全场景被误读。
- [MUST] 在最新且最相关的经历里补一个 Tier 1 规模信号，别让百分比改进单独承担叙事。
- [SHOULD] 把 Summary 第一句从 "Data Analysis Candidate" 改成直接岗位锚点，减少首屏弱化感。
- [NICE] 统一 Summary 的技术加粗颗粒度，把 Spark 也纳入同一套强调规则。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-capitalone-ai/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-capitalone-ai/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-capitalone-ai/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-capitalone-ai/codex.json`

## extra/Ramp-Platform

- 目标岗位: Software Engineer, Infrastructure @ Ramp
- 分数/结论: 97.3 / pass
- 耗时: 39.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P1-042, P3C-010, P3D-001

### 优先修改项
- [MUST] Reframe the cloud story so AWS/Azure/GCP are tied to the exact role or bullet where they were used, instead of being presented as one broad simultaneous core stack.
- [MUST] Add one Tier 1 scale/scope anchor to the latest TikTok experience so the section does not read as pure outcome-percent polish.
- [SHOULD] Remove bold from modifiers like internal/team-maintained/existing and reserve bold for technologies and quantified outcomes.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-ramp-platform/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-ramp-platform/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-ramp-platform/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-ramp-platform/codex.json`

## extra/HealthEquity-DotNet

- 目标岗位: Software Engineer II @ HealthEquity
- 分数/结论: 94.5 / pass
- 耗时: 64.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P1-040, P2-001, P3D-001

### 优先修改项
- [MUST] Rewrite the Summary opening to be role-led and domain-led instead of transition-led.
- [MUST] Add one concrete scope metric to the newest TikTok bullet so the top of the page shows scale, not just improvement percentages.
- [SHOULD] Bold the strongest quantified outcomes consistently across Experience so the main evidence is easier to scan.
- [NICE] If you keep the transition narrative, move it to a later Summary sentence rather than the opener.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-healthequity-dotnet/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-healthequity-dotnet/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-healthequity-dotnet/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v6-hr-final_20260417_203626_630894/extra-healthequity-dotnet/codex.json`
