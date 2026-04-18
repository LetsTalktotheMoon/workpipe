# v8_tooling_bridge_old10 结果

生成时间: 2026-04-17T23:09:26

| Case | 分数 | 结论 | 耗时(秒) | Critical | High | Medium | 主要规则 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| same/Microsoft | 84.7 | fail | 106.0 | 0 | 2 | 4 | P1-042, P2-001, P3B-001, P3B-012, P3C-011, P3D-001 |
| same/Google | 94.4 | pass | 56.0 | 0 | 1 | 1 | P2-001, P3A-002 |
| same/Amazon | 96.9 | pass | 50.0 | 0 | 0 | 3 | P1-042, P2-001, P3C-011 |
| same/AWS | 96.0 | pass | 42.0 | 0 | 1 | 0 | P2-001 |
| extra/Dataminr-Infra | 95.8 | pass | 50.0 | 0 | 1 | 3 | P2-010, P2-020, P3C-010, P3D-001 |
| extra/Zoox-LLM | 91.4 | fail | 64.0 | 0 | 1 | 3 | P3B-001, P3B-003, P3C-011, P3D-001 |
| extra/Synechron-Backend | 100.0 | pass | 47.0 | 0 | 0 | 0 | none |
| extra/CapitalOne-AI | 92.4 | fail | 50.0 | 0 | 1 | 1 | P2-001, P3B-010 |
| extra/Ramp-Platform | 99.5 | pass | 45.0 | 0 | 0 | 1 | P1-042 |
| extra/HealthEquity-DotNet | 86.8 | fail | 102.0 | 0 | 2 | 1 | P2-001, P3B-010, P3B-011 |

## same/Microsoft

- 目标岗位: Software Engineer II - Azure Storage @ Microsoft
- 分数/结论: 84.7 / fail
- 耗时: 106.0 秒
- 严重度计数: critical=0, high=2, medium=4, low=0
- 规则 ID: P1-042, P2-001, P3B-001, P3B-012, P3C-011, P3D-001

### 优先修改项
- [MUST] 把 Summary 首句和最相关经历改成明确的 backend/distributed-systems 锚点，不要先讲“转型中”。
- [MUST] 如果真实有 storage-substrate 经验，立刻在 TikTok 或 DiDi 的最相关 bullet 里补出直接证据；如果没有，这个 JD 本身就是结构性错配。
- [SHOULD] 补一条 first-person on-call / incident-response 证据，因为这是 JD 的最低门槛之一。
- [NICE] 收敛 TikTok 的多语言叙事，并补一个可追问的 scope 数字，提升首屏可信度。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/same-microsoft/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/same-microsoft/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/same-microsoft/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/same-microsoft/codex.json`

## same/Google

- 目标岗位: Software Engineer III, Full Stack, Google Cloud Platforms @ Google
- 分数/结论: 94.4 / pass
- 耗时: 56.0 秒
- 严重度计数: critical=0, high=1, medium=1, low=0
- 规则 ID: P2-001, P3A-002

### 优先修改项
- [MUST] 把 Summary 第一条改成角色先行的 full-stack framing，弱化或后移“transitioning from data analysis”的表述。
- [MUST] 处理 TikTok 项目里 `Bedrock` 的技能出处不一致：要么补进 Skills，要么重写该 bullet 只保留已列出的技术。
- [SHOULD] 如果目标继续对准 Google Cloud Platforms，补一条更明确的云平台/部署/监控/权限相关正文证据，而不是只在 Skills 里泛列云技术。
- [NICE] 精简 Summary 第三句的 Go 成就表述，保留 cognition signal，但让首屏更快扫读。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/same-google/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/same-google/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/same-google/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/same-google/codex.json`

## same/Amazon

- 目标岗位: Machine Learning Engineer II , AGI Customization @ Amazon
- 分数/结论: 96.9 / pass
- 耗时: 50.0 秒
- 严重度计数: critical=0, high=0, medium=3, low=0
- 规则 ID: P1-042, P2-001, P3C-011

### 优先修改项
- [MUST] 把 Summary 第一条改成角色方向先行，去掉“transitioning from analytics”的首屏弱化感。
- [MUST] 收敛 TikTok 实习段的语言堆叠感，明确 1-2 门主语言，其余语言降级为辅助集成上下文。
- [MUST] 取消正文里 `team-maintained` / `team-owned` / `intern-owned` 这类限定语的加粗。
- [SHOULD] 继续保留 LLM customization / RAG / evaluation 的桥接，但让它更贴近实际训练或评测贡献。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/same-amazon/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/same-amazon/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/same-amazon/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/same-amazon/codex.json`

## same/AWS

- 目标岗位: Software Development Engineer II - Builder Experience, GenAI, GenAI, Codex @ Amazon Web Services (AWS)
- 分数/结论: 96.0 / pass
- 耗时: 42.0 秒
- 严重度计数: critical=0, high=1, medium=0, low=0
- 规则 ID: P2-001

### 优先修改项
- [MUST] 重写 Summary 第一句，去掉“transitioning from analytics / candidate”这类转场开场，改为直接的 backend / distributed / security 角色锚点，并保留 Java、C++、Embedded 和 code review readiness 的核心信号。
- [SHOULD] 如果版面允许，把首段最前面的经历/项目再向 code review infrastructure、release safety、internal tooling 靠拢一点，让首屏更贴近 AWS CRUX 方向。
- [NICE] 将 Summary 里的“GenAI Systems Context”保持为辅助信号，不要让它盖过 backend 与 builder experience 主线。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/same-aws/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/same-aws/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/same-aws/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/same-aws/codex.json`

## extra/Dataminr-Infra

- 目标岗位: Senior Software Engineer, Backend @ Dataminr
- 分数/结论: 95.8 / pass
- 耗时: 50.0 秒
- 严重度计数: critical=0, high=1, medium=3, low=1
- 规则 ID: P2-010, P2-020, P3C-010, P3D-001

### 优先修改项
- [MUST] Rewrite the TikTok intern section to center one coherent ownership story instead of spreading across many language and infra families.
- [MUST] Add at least one genuine Tier 1 scope metric to the newest backend-relevant experience or project.
- [SHOULD] Replace `Structured Problem Solver` with a more specific cognition header tied to backend systems judgment.
- [NICE] Move the strongest scope/ownership clause to the first TikTok bullet before any percentage lift.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-dataminr-infra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-dataminr-infra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-dataminr-infra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-dataminr-infra/codex.json`

## extra/Zoox-LLM

- 目标岗位: Machine Learning Engineer, 3D Simulation @ Zoox
- 分数/结论: 91.4 / fail
- 耗时: 64.0 秒
- 严重度计数: critical=0, high=1, medium=3, low=0
- 规则 ID: P3B-001, P3B-003, P3C-011, P3D-001

### 优先修改项
- [MUST] 在最相关经历里补一条真实可核验的 3D / radiance-field / 3D reconstruction 证据；没有这类经历就应把该 JD 视为结构性错配。
- [MUST] 收敛 TikTok 段落的语言栈写法，避免看起来像 4 门语言的日常主栈。
- [SHOULD] 给最近一段经历补一个规模或 scope 锚点，不要只靠局部百分比和时间改进。
- [NICE] 在 Summary 里加一句明确的迁移桥接，说明 ML systems / replay / evaluation 为什么能迁移到 simulation fidelity。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-zoox-llm/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-zoox-llm/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-zoox-llm/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-zoox-llm/codex.json`

## extra/Synechron-Backend

- 目标岗位: Python Fullstack Engineer @ Synechron
- 分数/结论: 100.0 / pass
- 耗时: 47.0 秒
- 严重度计数: critical=0, high=0, medium=0, low=0
- 规则 ID: none

### 优先修改项

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-synechron-backend/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-synechron-backend/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-synechron-backend/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-synechron-backend/codex.json`

## extra/CapitalOne-AI

- 目标岗位: Manager, Data Analysis - Card Services @ Capital One
- 分数/结论: 92.4 / fail
- 耗时: 50.0 秒
- 严重度计数: critical=0, high=1, medium=1, low=0
- 规则 ID: P2-001, P3B-010

### 优先修改项
- [MUST] 解决 Manager JD 与简历纸面资历的结构性错配：当前只显式写出 3+ years，且没有可见 people-management 证据；若事实成立，应转投非 Manager 的 analytics 岗位。
- [MUST] 重写 Summary 首句，去掉“Candidate”式自我定位，改为直接的 data analytics / Python / SQL / Spark 岗位锚点。
- [SHOULD] 如果真实存在项目管理、带人、导师式协作或跨团队 owner 证据，把它补到最相关经历里，专门服务 JD 的 Manager 叙事。
- [NICE] 去掉对修饰语的加粗，把加粗保留给技术名词和量化结果，提升首屏可读性。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-capitalone-ai/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-capitalone-ai/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-capitalone-ai/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-capitalone-ai/codex.json`

## extra/Ramp-Platform

- 目标岗位: Software Engineer, Infrastructure @ Ramp
- 分数/结论: 99.5 / pass
- 耗时: 45.0 秒
- 严重度计数: critical=0, high=0, medium=1, low=0
- 规则 ID: P1-042

### 优先修改项
- [SHOULD] 去掉正文里修饰语/限定词的加粗，保留技术栈和量化结果的加粗权重。
- [NICE] 统一全篇的强调策略，让首屏更聚焦在技术栈、系统边界和量化结果上。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-ramp-platform/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-ramp-platform/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-ramp-platform/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-ramp-platform/codex.json`

## extra/HealthEquity-DotNet

- 目标岗位: Software Engineer II @ HealthEquity
- 分数/结论: 86.8 / fail
- 耗时: 102.0 秒
- 严重度计数: critical=0, high=2, medium=1, low=0
- 规则 ID: P2-001, P3B-010, P3B-011

### 优先修改项
- [MUST] 先解决 seniority 门槛问题：当前可见经历只有约 3.1 年，和 JD 的 6+ 年要求不匹配。
- [MUST] 只有在真实做过的前提下，补齐 named Azure/Microsoft service 证据；否则这份简历对该 JD 属于结构性错配。
- [MUST] 把 Summary 第一条改成 backend/Azure/Python 的目标角色 framing，删除首屏的转行感。
- [SHOULD] 收紧 TikTok 和 DiDi 的技术堆栈密度，让每条 bullet 聚焦 1 个主系统 + 1 个结果。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-healthequity-dotnet/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-healthequity-dotnet/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-healthequity-dotnet/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788/extra-healthequity-dotnet/codex.json`
