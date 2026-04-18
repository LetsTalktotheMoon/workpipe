# v9_gate_restore_old10 结果

生成时间: 2026-04-17T23:22:16

| Case | 分数 | 结论 | 耗时(秒) | Critical | High | Medium | 主要规则 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| same/Microsoft | 87.7 | fail | 62.0 | 0 | 3 | 2 | P1-042, P2-001, P3B-012, P3C-010, P3D-001 |
| same/Google | 98.0 | pass | 55.0 | 0 | 0 | 1 | P2-001 |
| same/Amazon | 91.2 | fail | 55.0 | 0 | 2 | 1 | P2-001, P3B-010, P3C-010 |
| same/AWS | 97.5 | pass | 55.0 | 0 | 0 | 2 | P1-042, P2-001 |
| extra/Dataminr-Infra | 92.9 | fail | 81.0 | 0 | 1 | 3 | P1-042, P3B-010, P3D-001 |
| extra/Zoox-LLM | 93.8 | fail | 52.0 | 0 | 1 | 1 | P3B-001, P3C-010 |
| extra/Synechron-Backend | 98.5 | pass | 66.0 | 0 | 0 | 2 | P1-030, P1-042 |
| extra/CapitalOne-AI | 85.3 | fail | 87.0 | 0 | 2 | 3 | P1-040, P2-001, P2-020, P3B-001, P3B-010, P3D-001 |
| extra/Ramp-Platform | 99.2 | pass | 56.0 | 0 | 0 | 2 | P1-042, P3E-013 |
| extra/HealthEquity-DotNet | 84.0 | fail | 71.0 | 0 | 3 | 2 | P1-042, P2-001, P2-040, P3B-010, P3B-011 |

## same/Microsoft

- 目标岗位: Software Engineer II - Azure Storage @ Microsoft
- 分数/结论: 87.7 / fail
- 耗时: 62.0 秒
- 严重度计数: critical=0, high=3, medium=2, low=0
- 规则 ID: P1-042, P2-001, P3B-012, P3C-010, P3D-001

### 优先修改项
- [MUST] 把 Summary 首句改成直接的 backend / distributed / security 角色定位，移除“transitioning from data analytics”式开场。
- [MUST] 如果没有直接 storage / substrate 证据，这份简历对 Azure Storage 属于结构性错配；若有相关经历，必须前置到最相关经历首条 bullet。
- [MUST] 收敛 TikTok 段的多语言铺陈，保留真正主责的 1–2 个核心语言，并补一个可追问的 Tier 1 规模指标。
- [SHOULD] 去掉 team-maintained / existing / internal 这类限定词的加粗，只保留技术名词和关键结果加粗。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/same-microsoft/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/same-microsoft/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/same-microsoft/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/same-microsoft/codex.json`

## same/Google

- 目标岗位: Software Engineer III, Full Stack, Google Cloud Platforms @ Google
- 分数/结论: 98.0 / pass
- 耗时: 55.0 秒
- 严重度计数: critical=0, high=0, medium=1, low=0
- 规则 ID: P2-001

### 优先修改项
- [SHOULD] 将 Summary 第一条改成目标角色先行，再补“从数据分析转向全栈”的背景。
- [NICE] 保持其余经历不变；当前项目与经历的技术证据已足够支撑 JD 的核心要求。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/same-google/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/same-google/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/same-google/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/same-google/codex.json`

## same/Amazon

- 目标岗位: Machine Learning Engineer II , AGI Customization @ Amazon
- 分数/结论: 91.2 / fail
- 耗时: 55.0 秒
- 严重度计数: critical=0, high=2, medium=1, low=0
- 规则 ID: P2-001, P3B-010, P3C-010

### 优先修改项
- [MUST] 直面 3+ years non-internship 门槛：当前可见经历只有约 2.5 年，这份简历对该 JD 是结构性错配。
- [MUST] 把 Summary 第一行改成直接的 ML/LLM 角色锚点，去掉“transitioning”式首屏叙事。
- [SHOULD] 收敛 TikTok 段的编程语言密度，突出最核心的 1-2 门语言，避免堆砌感。
- [NICE] 保持其余 ML / RAG / Bedrock 证据不变，但减少同类技术重复出现的频率。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/same-amazon/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/same-amazon/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/same-amazon/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/same-amazon/codex.json`

## same/AWS

- 目标岗位: Software Development Engineer II - Builder Experience, GenAI, GenAI, Codex @ Amazon Web Services (AWS)
- 分数/结论: 97.5 / pass
- 耗时: 55.0 秒
- 严重度计数: critical=0, high=0, medium=2, low=0
- 规则 ID: P1-042, P2-001

### 优先修改项
- [SHOULD] Rewrite the first Summary sentence to lead with a backend/security identity instead of a transition frame.
- [SHOULD] Unbold modifiers like team-maintained and existing so emphasis stays on technical nouns and scope.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/same-aws/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/same-aws/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/same-aws/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/same-aws/codex.json`

## extra/Dataminr-Infra

- 目标岗位: Senior Software Engineer, Backend @ Dataminr
- 分数/结论: 92.9 / fail
- 耗时: 81.0 秒
- 严重度计数: critical=0, high=1, medium=3, low=0
- 规则 ID: P1-042, P3B-010, P3D-001

### 优先修改项
- [MUST] Resolve the senior-backend tenure gap by surfacing truthful backend ownership evidence in the most relevant roles, or treat this as a structural mismatch for Dataminr Senior Backend.
- [MUST] Add one concrete scope anchor to the newest backend-relevant bullets so the resume is not read as percent-lift heavy and scope-light.
- [SHOULD] Remove bold from qualifiers like team-maintained/internal/existing/team-owned and keep emphasis on technologies and measurable signals.
- [NICE] If you want a stronger first impression, make the Summary's third sentence more cognition-forward and less generic.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-dataminr-infra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-dataminr-infra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-dataminr-infra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-dataminr-infra/codex.json`

## extra/Zoox-LLM

- 目标岗位: Machine Learning Engineer, 3D Simulation @ Zoox
- 分数/结论: 93.8 / fail
- 耗时: 52.0 秒
- 严重度计数: critical=0, high=1, medium=1, low=0
- 规则 ID: P3B-001, P3C-010

### 优先修改项
- [MUST] 补出一条真实的 3D simulation / radiance field / 3D reconstruction 证据，否则这份简历对 Zoox 的结构性匹配不足。
- [MUST] 收敛 TikTok intern 段的语言与工具密度，避免 4 种编程语言并列造成堆栈炫技感。
- [SHOULD] 如果有真实的数学建模或概率方法经历，把它用 1 条可核验 bullet 写出来。
- [NICE] 让 Summary 第一行更贴近目标岗位的 3D ML 方向，而不是只强调 backend 交付。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-zoox-llm/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-zoox-llm/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-zoox-llm/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-zoox-llm/codex.json`

## extra/Synechron-Backend

- 目标岗位: Python Fullstack Engineer @ Synechron
- 分数/结论: 98.5 / pass
- 耗时: 66.0 秒
- 严重度计数: critical=0, high=0, medium=2, low=0
- 规则 ID: P1-030, P1-042

### 优先修改项
- [MUST] Rewrite the 3 Summary bullets so each starts with a strong action verb or role anchor while preserving the same evidence and the 3-sentence structure.
- [MUST] Remove bold from descriptive qualifiers like `internal` and `team-maintained`; reserve emphasis for technologies, scope, and metrics.
- [SHOULD] Normalize Skills token casing for cleaner ATS parsing, especially `GitLab CI` and `RESTful APIs`.
- [NICE] Keep the current project and experience evidence density; no extra stack breadth is needed.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-synechron-backend/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-synechron-backend/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-synechron-backend/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-synechron-backend/codex.json`

## extra/CapitalOne-AI

- 目标岗位: Manager, Data Analysis - Card Services @ Capital One
- 分数/结论: 85.3 / fail
- 耗时: 87.0 秒
- 严重度计数: critical=0, high=2, medium=3, low=1
- 规则 ID: P1-040, P2-001, P2-020, P3B-001, P3B-010, P3D-001

### 优先修改项
- [MUST] 补齐 `R` 的真实使用证据，否则这份简历对该 JD 的核心技能覆盖不成立。
- [MUST] 处理 Manager 门槛与可见年限/people-management 的结构性错配；如果没有真实管理经历，优先换目标岗位。
- [SHOULD] 把 TikTok 段首条 bullet 的 scope 信号前置，别让百分比结果承担全部首屏说服力。
- [NICE] 统一加粗正文里的核心技术词，尤其是 `Bedrock` 这类已经出现但没被视觉强调的词。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-capitalone-ai/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-capitalone-ai/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-capitalone-ai/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-capitalone-ai/codex.json`

## extra/Ramp-Platform

- 目标岗位: Software Engineer, Infrastructure @ Ramp
- 分数/结论: 99.2 / pass
- 耗时: 56.0 秒
- 严重度计数: critical=0, high=0, medium=2, low=0
- 规则 ID: P1-042, P3E-013

### 优先修改项
- [SHOULD] 取消正文里对限定词/修饰语的加粗，只保留技术栈、关键 scope 和量化结果的加粗。
- [SHOULD] 给 TikTok 的 RAG / Bedrock bullet 补一条明确的数据边界说明，避免敏感团队场景下的合规追问。
- [NICE] 其余结构基本合规，不需要改动职业主线；保持现有的 infra/backend 叙事即可。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-ramp-platform/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-ramp-platform/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-ramp-platform/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-ramp-platform/codex.json`

## extra/HealthEquity-DotNet

- 目标岗位: Software Engineer II @ HealthEquity
- 分数/结论: 84.0 / fail
- 耗时: 71.0 秒
- 严重度计数: critical=0, high=3, medium=2, low=0
- 规则 ID: P1-042, P2-001, P2-040, P3B-010, P3B-011

### 优先修改项
- [MUST] Resolve the structural mismatch with this JD: the resume currently shows only ~3 years of experience versus the JD's 6+ year requirement, so this is not a good-fit target unless there is truthful missing experience.
- [MUST] Add explicit Azure service-level and Azure DevOps evidence in the most relevant DiDi bullet if those facts are real; generic `Azure` is not enough for this posting.
- [SHOULD] Rewrite Summary sentence 1 to lead with a direct backend/platform/security role anchor instead of a transition narrative.
- [NICE] Remove bold from qualifiers like `team-maintained` and rename the vague `APIs` Skills category.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-healthequity-dotnet/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-healthequity-dotnet/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-healthequity-dotnet/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-old10_20260417_231136_106675/extra-healthequity-dotnet/codex.json`
