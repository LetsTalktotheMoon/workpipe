# v2_hr_recal 结果

生成时间: 2026-04-17T19:46:10

| Case | 分数 | 结论 | 耗时(秒) | Critical | High | Medium | 主要规则 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| same/Microsoft | 90.4 | pass | 63.0 | 0 | 2 | 3 | P1-042, P2-001, P3B-001, P3C-010, P3D-001 |
| same/Google | 92.8 | pass | 71.0 | 0 | 1 | 3 | P1-040, P1-042, P2-001, P2-020, P3A-002 |
| same/Amazon | 97.8 | pass | 55.0 | 0 | 0 | 3 | P1-042, P3C-011, P3D-001 |
| same/AWS | 94.4 | fail | 65.0 | 1 | 0 | 3 | P1-040, P2-001, P3D-001, P3E-010 |
| extra/Dataminr-Infra | 97.4 | pass | 56.0 | 0 | 0 | 3 | P1-040, P2-010, P3D-001 |
| extra/Zoox-LLM | 96.8 | pass | 44.0 | 0 | 1 | 2 | P2-010, P3C-010, P3D-001 |
| extra/Synechron-Backend | 95.0 | pass | 51.0 | 0 | 0 | 5 | P1-040, P1-042, P2-001, P2-040, P3D-001 |
| extra/CapitalOne-AI | 95.2 | pass | 51.0 | 0 | 0 | 4 | P1-042, P2-001, P3B-003, P3D-001 |
| extra/Ramp-Platform | 95.8 | fail | 60.0 | 1 | 0 | 3 | P1-040, P1-042, P3D-001, P3E-010 |
| extra/HealthEquity-DotNet | 88.8 | pass | 72.0 | 0 | 1 | 5 | P1-040, P2-001, P2-040, P3B-001, P3B-004, P3C-011 |

## same/Microsoft

- 目标岗位: Software Engineer II - Azure Storage @ Microsoft
- 分数/结论: 90.4 / pass
- 耗时: 63.0 秒
- 严重度计数: critical=0, high=2, medium=3, low=0
- 规则 ID: P1-042, P2-001, P3B-001, P3C-010, P3D-001

### 优先修改项
- [MUST] 把 TikTok 首条 bullet 改成真正的后端/分布式系统抓手，前置一个具体 scale 或 ownership 指标，别让首屏先看到一串百分比。
- [MUST] 显式写出 `Distributed Systems`，并在最相关的后端经历里补足可追问的系统边界证据，确保 Azure Storage 的 JD 匹配一眼可见。
- [MUST] 收敛 TikTok 段的语言栈表述，每段只保留 1-2 个主语言，其余语言只作为集成或调用背景出现。
- [SHOULD] 去掉 `team-maintained`、`existing` 这类描述词的加粗，只保留技术名词和量化结果加粗。

### 产物
- Prompt: `same-microsoft/prompt.txt`
- Metadata: `same-microsoft/metadata.json`
- 原始输出: `same-microsoft/codex.raw.txt`
- JSON: `same-microsoft/codex.json`

## same/Google

- 目标岗位: Software Engineer III, Full Stack, Google Cloud Platforms @ Google
- 分数/结论: 92.8 / pass
- 耗时: 71.0 秒
- 严重度计数: critical=0, high=1, medium=3, low=1
- 规则 ID: P1-040, P1-042, P2-001, P2-020, P3A-002

### 优先修改项
- [MUST] Rewrite Summary sentence 1 to lead with a direct role/domain anchor instead of `transitioning from data analysis to full-stack development`.
- [MUST] Add `AWS Bedrock` to Skills, or remove the named platform from the TikTok retrieval project bullet.
- [SHOULD] Move the clearest scope signal into the first TikTok bullet and surface the best quantitative evidence earlier.
- [NICE] Normalize bolding so qualifiers like `team-maintained` are unbolded and only technologies or key scale/result tokens are emphasized.

### 产物
- Prompt: `same-google/prompt.txt`
- Metadata: `same-google/metadata.json`
- 原始输出: `same-google/codex.raw.txt`
- JSON: `same-google/codex.json`

## same/Amazon

- 目标岗位: Machine Learning Engineer II , AGI Customization @ Amazon
- 分数/结论: 97.8 / pass
- 耗时: 55.0 秒
- 严重度计数: critical=0, high=0, medium=3, low=0
- 规则 ID: P1-042, P3C-011, P3D-001

### 优先修改项
- [MUST] Add one concrete tier-1 scope anchor to the TikTok Security internship, ideally in the first bullet or project baseline, so the MLE narrative is not carried only by percentage improvements.
- [MUST] Recast the TikTok experience so Go, Java, Python, and C++ are clearly mapped to specific tasks instead of reading like one broad daily stack.
- [SHOULD] Remove bold from ownership qualifiers such as team-maintained, team-owned, and intern-owned; reserve emphasis for technologies and metrics.
- [NICE] Keep the rest of the content, but make the most relevant scope signal visible earlier in the TikTok section.

### 产物
- Prompt: `same-amazon/prompt.txt`
- Metadata: `same-amazon/metadata.json`
- 原始输出: `same-amazon/codex.raw.txt`
- JSON: `same-amazon/codex.json`

## same/AWS

- 目标岗位: Software Development Engineer II - Builder Experience, GenAI, GenAI, Codex @ Amazon Web Services (AWS)
- 分数/结论: 94.4 / fail
- 耗时: 65.0 秒
- 严重度计数: critical=1, high=0, medium=3, low=0
- 规则 ID: P1-040, P2-001, P3D-001, P3E-010

### 优先修改项
- [MUST] Clarify the TikTok Security / AWS Bedrock bullet with an explicit data boundary, or remove the external-LLM claim if it touched protected data.
- [MUST] Reframe the Summary opening as a direct backend/security identity instead of a transition story.
- [SHOULD] Add one concrete Tier 1 scope metric to the TikTok intern section so the latest experience reads as owned impact, not only percentage deltas.
- [NICE] Bold the key scope numbers and headline metrics consistently across the experience bullets.

### 产物
- Prompt: `same-aws/prompt.txt`
- Metadata: `same-aws/metadata.json`
- 原始输出: `same-aws/codex.raw.txt`
- JSON: `same-aws/codex.json`

## extra/Dataminr-Infra

- 目标岗位: Senior Software Engineer, Backend @ Dataminr
- 分数/结论: 97.4 / pass
- 耗时: 56.0 秒
- 严重度计数: critical=0, high=0, medium=3, low=0
- 规则 ID: P1-040, P2-010, P3D-001

### 优先修改项
- [SHOULD] Add one Tier 1 scope anchor to the TikTok internship section so the latest experience reads as backend-scale work, not only a set of percentage deltas.
- [SHOULD] Replace the generic Summary header `Structured Problem Solver` with a stronger cognition frame such as `Systems judgment` or `Pattern recognition`.
- [NICE] Bold `Bedrock` in the TikTok bullet so technical emphasis is consistent with the rest of the resume.

### 产物
- Prompt: `extra-dataminr-infra/prompt.txt`
- Metadata: `extra-dataminr-infra/metadata.json`
- 原始输出: `extra-dataminr-infra/codex.raw.txt`
- JSON: `extra-dataminr-infra/codex.json`

## extra/Zoox-LLM

- 目标岗位: Machine Learning Engineer, 3D Simulation @ Zoox
- 分数/结论: 96.8 / pass
- 耗时: 44.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P2-010, P3C-010, P3D-001

### 优先修改项
- [MUST] 收敛 TikTok intern 段的技术栈展示，避免 4 种编程语言 + 多个基础设施/ML 框架同时铺开，改成更清晰的主责叙事。
- [MUST] 给 TikTok 最新经历补一个可追问的规模/scope 锚点，让最上方经验不只是百分比结果，而是系统边界 + 结果一起成立。
- [SHOULD] 把 Summary 第三句的 `Technical Range` 换成更具体的系统判断类标题。
- [NICE] 如果要更贴 Zoox 的 3D simulation 方向，可以在 replay sandbox 项目里再强化“simulation / evaluation infrastructure”的表述。

### 产物
- Prompt: `extra-zoox-llm/prompt.txt`
- Metadata: `extra-zoox-llm/metadata.json`
- 原始输出: `extra-zoox-llm/codex.raw.txt`
- JSON: `extra-zoox-llm/codex.json`

## extra/Synechron-Backend

- 目标岗位: Python Fullstack Engineer @ Synechron
- 分数/结论: 95.0 / pass
- 耗时: 51.0 秒
- 严重度计数: critical=0, high=0, medium=5, low=0
- 规则 ID: P1-040, P1-042, P2-001, P2-040, P3D-001

### 优先修改项
- [MUST] Rewrite the Summary opening so the first impression is a direct role-direction anchor, not a generic capability label.
- [MUST] Add one concrete scope marker to the newest TikTok bullets so the top experience reads as ownership-heavy rather than only efficiency-improvement-heavy.
- [SHOULD] Normalize bolding: keep emphasis on technologies and results, remove bold from filler adjectives, and bold the key metric phrases.
- [NICE] Rename the `APIs` skills bucket to a more informative category label.

### 产物
- Prompt: `extra-synechron-backend/prompt.txt`
- Metadata: `extra-synechron-backend/metadata.json`
- 原始输出: `extra-synechron-backend/codex.raw.txt`
- JSON: `extra-synechron-backend/codex.json`

## extra/CapitalOne-AI

- 目标岗位: Manager, Data Analysis - Card Services @ Capital One
- 分数/结论: 95.2 / pass
- 耗时: 51.0 秒
- 严重度计数: critical=0, high=0, medium=4, low=0
- 规则 ID: P1-042, P2-001, P3B-003, P3D-001

### 优先修改项
- [SHOULD] Reframe the Summary opening so it leads with a direct data-analysis role anchor instead of `Data Analysis Candidate`.
- [SHOULD] Add one sentence that bridges prior security/consumer operations analytics work to card-services-style transactional or reconciliation analytics.
- [SHOULD] Add a concrete Tier 1 scale anchor to the latest TikTok experience so the opening section reads as scope-heavy, not only percent-heavy.
- [NICE] Remove bold formatting from descriptive modifiers like `team-maintained`, `existing`, and `internal`.

### 产物
- Prompt: `extra-capitalone-ai/prompt.txt`
- Metadata: `extra-capitalone-ai/metadata.json`
- 原始输出: `extra-capitalone-ai/codex.raw.txt`
- JSON: `extra-capitalone-ai/codex.json`

## extra/Ramp-Platform

- 目标岗位: Software Engineer, Infrastructure @ Ramp
- 分数/结论: 95.8 / fail
- 耗时: 60.0 秒
- 严重度计数: critical=1, high=0, medium=3, low=0
- 规则 ID: P1-040, P1-042, P3D-001, P3E-010

### 优先修改项
- [MUST] 先修 TikTok Security 的 RAG bullet：明确它只处理 sandbox / redacted / internal-only 数据，避免外部 LLM 触碰受保护数据的合规歧义。
- [MUST] 给 TikTok 段补一个 Tier-1 scope 锚点，避免整段只剩时间/百分比优化。
- [SHOULD] 统一格式：去掉 team-maintained/internal/existing 这类修饰词的加粗，只保留技术和关键指标加粗。
- [NICE] 如果要进一步增强 Ramp 匹配感，可在最相关经历里补一句“reliability-sensitive internal workflows / platform infrastructure”式桥接。

### 产物
- Prompt: `extra-ramp-platform/prompt.txt`
- Metadata: `extra-ramp-platform/metadata.json`
- 原始输出: `extra-ramp-platform/codex.raw.txt`
- JSON: `extra-ramp-platform/codex.json`

## extra/HealthEquity-DotNet

- 目标岗位: Software Engineer II @ HealthEquity
- 分数/结论: 88.8 / pass
- 耗时: 72.0 秒
- 严重度计数: critical=0, high=1, medium=5, low=0
- 规则 ID: P1-040, P2-001, P2-040, P3B-001, P3B-004, P3C-011

### 优先修改项
- [MUST] Add `Agile` explicitly to Skills so the JD match is exact and ATS-safe.
- [MUST] Reframe the Summary opening to be role-first, not transition-first, and add one direct bridge to regulated or consumer-impacting workflows.
- [SHOULD] Qualify the DiDi stack breadth so it reads as primary ownership plus adjacent collaboration, not five-plus daily languages.
- [NICE] Rename the `APIs` Skills bucket to a more informative label.

### 产物
- Prompt: `extra-healthequity-dotnet/prompt.txt`
- Metadata: `extra-healthequity-dotnet/metadata.json`
- 原始输出: `extra-healthequity-dotnet/codex.raw.txt`
- JSON: `extra-healthequity-dotnet/codex.json`
