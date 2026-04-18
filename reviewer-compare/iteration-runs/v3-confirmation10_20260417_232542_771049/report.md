# v3_confirmation10 结果

生成时间: 2026-04-17T23:36:15

| Case | 分数 | 结论 | 耗时(秒) | Critical | High | Medium | 主要规则 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| conf/FlexTrade-SoftwareDeveloper | 90.6 | fail | 65.0 | 0 | 1 | 3 | P2-001, P3B-001, P3B-003, P3E-013 |
| conf/Whoop-SensorIntelligence | 94.0 | pass | 46.0 | 0 | 1 | 2 | P2-001, P3B-004, P3C-010 |
| conf/Hopper-CustomerPlatform | 97.5 | pass | 67.0 | 0 | 0 | 2 | P1-040, P2-001 |
| conf/Nuro-OffboardInfra | 94.6 | pass | 50.0 | 0 | 1 | 2 | P2-010, P3B-003, P3D-001 |
| conf/AMH-EnterpriseDataAnalyst | 98.0 | pass | 65.0 | 0 | 0 | 3 | P1-040, P1-042, P3D-001 |
| conf/Phantom-SDET | 95.5 | pass | 85.0 | 0 | 0 | 5 | P1-042, P2-001, P2-040, P3B-003, P3E-013 |
| conf/VeteransUnited-AssociateSE | 95.8 | pass | 76.0 | 0 | 0 | 4 | P1-042, P2-001, P2-040, P3B-003 |
| conf/8451-ResearchAI | 95.8 | pass | 54.0 | 0 | 1 | 2 | P2-001, P2-010, P3C-010 |
| conf/Photon-AIEngineer | 93.3 | pass | 78.0 | 0 | 2 | 2 | P1-042, P2-001, P3C-010, P3D-001 |
| conf/Clarivate-NLP | 99.7 | pass | 47.0 | 0 | 0 | 1 | P3E-013 |

## conf/FlexTrade-SoftwareDeveloper

- 目标岗位: Software Developer @ FlexTrade
- 分数/结论: 90.6 / fail
- 耗时: 65.0 秒
- 严重度计数: critical=0, high=1, medium=3, low=0
- 规则 ID: P2-001, P3B-001, P3B-003, P3E-013

### 优先修改项
- [MUST] 在 Skills 和最相关的后端 bullet 中显式补出 `Distributed Systems`，不要只靠 `Microservices` / `distributed service environment` 近义覆盖。
- [MUST] 重写 Summary 第一行，改成角色先行的后端定位，去掉过重的 `analytics-to-engineering` 转型开场。
- [SHOULD] 补一条面向 FlexTrade 的桥接句，把你的经历明确映射到 `latency-sensitive`, `release-controlled`, `distributed` 后端场景。
- [SHOULD] 视真实情况为 TikTok 的 Bedrock/RAG bullet 加上 `internal evaluation` / `sandbox` / `no user data` 之类边界限定。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-flextrade-softwaredeveloper/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-flextrade-softwaredeveloper/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-flextrade-softwaredeveloper/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-flextrade-softwaredeveloper/codex.json`

## conf/Whoop-SensorIntelligence

- 目标岗位: Sensor Intelligence Engineer II (Tools & Validation) @ WHOOP
- 分数/结论: 94.0 / pass
- 耗时: 46.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P2-001, P3B-004, P3C-010

### 优先修改项
- [MUST] Reframe the first Summary sentence to anchor on the target engineering identity first, and move the transition language behind that anchor.
- [MUST] Split the TikTok ML-evaluation bullet so the frameworks are supported by a single workflow instead of being stacked in one line.
- [SHOULD] Add one explicit bridge to WHOOP-relevant work, such as validation tooling, signal quality, or time-series/data QA, so the domain fit is legible on first scan.
- [NICE] Tighten the top-of-page narrative so the resume reads as sensor/validation-adjacent rather than broadly cross-domain.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-whoop-sensorintelligence/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-whoop-sensorintelligence/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-whoop-sensorintelligence/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-whoop-sensorintelligence/codex.json`

## conf/Hopper-CustomerPlatform

- 目标岗位: Senior Software Engineer - Customer Experience Platform @ Hopper
- 分数/结论: 97.5 / pass
- 耗时: 67.0 秒
- 严重度计数: critical=0, high=0, medium=2, low=0
- 规则 ID: P1-040, P2-001

### 优先修改项
- [SHOULD] 把 Summary 第一句改成先锚定 `Backend engineer`，不要让 `transitioning from analytics` 站在首位。
- [SHOULD] 给最关键的结果数字和 scope 词加粗，提升首屏扫读效率。
- [NICE] 如需更贴 Hopper 的 post-booking/customer-experience 方向，可以在首段或 DiDi 段补一句更明确的 support / operations / customer workflow bridge。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-hopper-customerplatform/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-hopper-customerplatform/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-hopper-customerplatform/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-hopper-customerplatform/codex.json`

## conf/Nuro-OffboardInfra

- 目标岗位: Software Engineer, Offboard Infrastructure @ Nuro
- 分数/结论: 94.6 / pass
- 耗时: 50.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P2-010, P3B-003, P3D-001

### 优先修改项
- [MUST] 把 Summary 第 3 句改成能力导向标题，避免“Collaborator”式弱 framing。
- [MUST] 在 Summary 或 TikTok 首条 bullet 里补一条明确的迁移桥接，说明为什么这份 backend / infra 经验适合 Nuro 的 offboard infrastructure。
- [SHOULD] 给 TikTok 最新经历补 1 个 Tier 1 规模或边界信号，降低整段对百分比结果的依赖。
- [NICE] 如果版面允许，继续把最相关经历的首条 bullet 写得更像“范围 + 责任 + 结果”，少一点泛化成效描述。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-nuro-offboardinfra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-nuro-offboardinfra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-nuro-offboardinfra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-nuro-offboardinfra/codex.json`

## conf/AMH-EnterpriseDataAnalyst

- 目标岗位: Senior Enterprise Data Analyst @ AMH
- 分数/结论: 98.0 / pass
- 耗时: 65.0 秒
- 严重度计数: critical=0, high=0, medium=3, low=0
- 规则 ID: P1-040, P1-042, P3D-001

### 优先修改项
- [SHOULD] 在 TikTok 经验补一个 Tier 1 scope 锚点，不要只靠百分比结果支撑首屏。
- [SHOULD] 收敛加粗策略，去掉限定词加粗，并把最强的量化数字突出出来。
- [NICE] 如果要更贴近 AMH，可在 Summary 或 DiDi 项目里补一句 enterprise ops / stakeholder reporting 的迁移桥接。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-amh-enterprisedataanalyst/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-amh-enterprisedataanalyst/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-amh-enterprisedataanalyst/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-amh-enterprisedataanalyst/codex.json`

## conf/Phantom-SDET

- 目标岗位: SDET (Wallet Platform) @ Phantom
- 分数/结论: 95.5 / pass
- 耗时: 85.0 秒
- 严重度计数: critical=0, high=0, medium=5, low=0
- 规则 ID: P1-042, P2-001, P2-040, P3B-003, P3E-013

### 优先修改项
- [MUST] 重写 Summary 首句和三个小标题，让开头先落在目标角色/领域，而不是 `transitioning` / trait-led 叙事。
- [MUST] 把 `Skills > APIs` 改成更具体的能力分组名，例如 `Testing & Automation`。
- [SHOULD] 在 Summary 或 TikTok 首条里补一层到 Phantom 的桥接，突出你做的是高风险、正确性敏感的验证工作，而不是泛化的自动化经验。
- [SHOULD] 给 TikTok 的 Bedrock/RAG 条目加上 internal/sandbox/synthetic/no-production-data 的边界限定。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-phantom-sdet/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-phantom-sdet/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-phantom-sdet/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-phantom-sdet/codex.json`

## conf/VeteransUnited-AssociateSE

- 目标岗位: Associate Software Engineer (Remote/Hybrid) @ Veterans United Home Loans
- 分数/结论: 95.8 / pass
- 耗时: 76.0 秒
- 严重度计数: critical=0, high=0, medium=4, low=0
- 规则 ID: P1-042, P2-001, P2-040, P3B-003

### 优先修改项
- [MUST] Rewrite the Summary opening so it is role-first and domain-first, not transition-first.
- [MUST] Remove bold emphasis from qualifier words like team-maintained; reserve bold for technologies and metrics.
- [MUST] Add one explicit transfer-bridge sentence tying prior internal workflow work to regulated, customer-facing operations.
- [SHOULD] Rename the vague Skills bucket 'APIs' to a clearer workflow-oriented category.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-veteransunited-associatese/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-veteransunited-associatese/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-veteransunited-associatese/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-veteransunited-associatese/codex.json`

## conf/8451-ResearchAI

- 目标岗位: Senior AI/ML Engineer - Research (P4368) @ 84.51˚
- 分数/结论: 95.8 / pass
- 耗时: 54.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P2-001, P2-010, P3C-010

### 优先修改项
- [MUST] 把 Summary 第一段改成直接的 AI/ML engineer / ML systems 定位，去掉首句的“transitioning from data analytics into software engineering”主叙事。
- [MUST] 把 Summary 第三句的 `Strategic Problem Solving` 改成更强的认知型 header，例如 `Pattern recognition` 或 `Structural intuition`。
- [SHOULD] 收敛 TikTok internship 里的云与平台栈，只保留主云和真正核心的部署/检索技术，避免 AWS + GCP + Azure 同段堆叠。
- [NICE] 其余 bullets 保持现状即可，重点是把首屏叙事从“转型说明”改成“AI/ML 系统能力 + 具体 scope”。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-8451-researchai/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-8451-researchai/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-8451-researchai/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-8451-researchai/codex.json`

## conf/Photon-AIEngineer

- 目标岗位: Artificial Intelligence Engineer @ Photon
- 分数/结论: 93.3 / pass
- 耗时: 78.0 秒
- 严重度计数: critical=0, high=2, medium=2, low=0
- 规则 ID: P1-042, P2-001, P3C-010, P3D-001

### 优先修改项
- [MUST] 把 Summary 第一行改成直接的 AI/Backend 角色定位，先给出岗位锚点，再写转型背景。
- [MUST] 给 TikTok 段补一个明确的 scope 锚点，优先放在第一条 bullet 或项目背景行，避免整段只剩百分比结果。
- [MUST] 收敛 TikTok / DiDi 的多栈并列写法，每条 bullet 只保留 1-2 个主技术，其他技术降级为支撑上下文。
- [SHOULD] 取消 `team-maintained` 这类限定词的加粗，只保留技术名词和关键量化信号加粗。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-photon-aiengineer/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-photon-aiengineer/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-photon-aiengineer/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-photon-aiengineer/codex.json`

## conf/Clarivate-NLP

- 目标岗位: Senior Data Scientist (NLP) @ Clarivate
- 分数/结论: 99.7 / pass
- 耗时: 47.0 秒
- 严重度计数: critical=0, high=0, medium=1, low=0
- 规则 ID: P3E-013

### 优先修改项
- [SHOULD] Add an explicit data-boundary qualifier to the TikTok AWS Bedrock bullets so the Security-context use case is unambiguous.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-clarivate-nlp/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-clarivate-nlp/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-clarivate-nlp/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-confirmation10_20260417_232542_771049/conf-clarivate-nlp/codex.json`
