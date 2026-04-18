# v9_confirmation10 结果

生成时间: 2026-04-17T23:37:32

| Case | 分数 | 结论 | 耗时(秒) | Critical | High | Medium | 主要规则 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| conf/FlexTrade-SoftwareDeveloper | 94.1 | pass | 95.0 | 0 | 0 | 5 | P1-030, P1-042, P2-001, P2-010, P3B-003 |
| conf/Whoop-SensorIntelligence | 90.4 | fail | 64.0 | 0 | 2 | 0 | P2-001, P3B-001 |
| conf/Hopper-CustomerPlatform | 97.0 | pass | 53.0 | 0 | 0 | 2 | P1-030, P2-001 |
| conf/Nuro-OffboardInfra | 97.5 | pass | 65.0 | 0 | 0 | 3 | P1-040, P2-010, P3D-001 |
| conf/AMH-EnterpriseDataAnalyst | 93.5 | pass | 60.0 | 0 | 1 | 4 | P1-030, P1-042, P3B-004, P3C-010, P3D-001 |
| conf/Phantom-SDET | 91.6 | fail | 75.0 | 0 | 1 | 3 | P1-042, P2-001, P2-040, P3B-001 |
| conf/VeteransUnited-AssociateSE | 82.3 | fail | 86.0 | 0 | 3 | 3 | P1-042, P2-001, P2-020, P3B-001, P3B-002, P3D-001 |
| conf/8451-ResearchAI | 87.3 | fail | 83.0 | 0 | 2 | 3 | P1-040, P2-001, P2-010, P3A-002, P3B-001 |
| conf/Photon-AIEngineer | 89.4 | fail | 56.0 | 0 | 2 | 1 | P2-001, P3B-001, P3D-001 |
| conf/Clarivate-NLP | 85.8 | fail | 73.0 | 0 | 2 | 2 | P2-001, P3B-001, P3B-010, P3D-001 |

## conf/FlexTrade-SoftwareDeveloper

- 目标岗位: Software Developer @ FlexTrade
- 分数/结论: 94.1 / pass
- 耗时: 95.0 秒
- 严重度计数: critical=0, high=0, medium=5, low=0
- 规则 ID: P1-030, P1-042, P2-001, P2-010, P3B-003

### 优先修改项
- [SHOULD] Rewrite Summary sentence 1 to lead with backend/distributed systems rather than the analytics-to-engineering transition.
- [SHOULD] Add one explicit bridge to FlexTrade's latency-sensitive, event-driven backend domain.
- [SHOULD] Rename the third Summary header to a stronger cognition label.
- [NICE] Clean up bullet openers and emphasis rules: replace weak openers like `Participated`/`Supported` and remove bold from modifier words like `team-maintained`.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-flextrade-softwaredeveloper/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-flextrade-softwaredeveloper/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-flextrade-softwaredeveloper/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-flextrade-softwaredeveloper/codex.json`

## conf/Whoop-SensorIntelligence

- 目标岗位: Sensor Intelligence Engineer II (Tools & Validation) @ WHOOP
- 分数/结论: 90.4 / fail
- 耗时: 64.0 秒
- 严重度计数: critical=0, high=2, medium=0, low=0
- 规则 ID: P2-001, P3B-001

### 优先修改项
- [MUST] 把 Professional Summary 第一句改成目标岗位 framing，删除或后置“Transitioning from data analytics to software engineering”的转型叙事。
- [MUST] 在最相关经历里补一条明确的 signal processing / time-series / wearable biosignals 证据；如果没有真实经历，WHOOP 这条线应重新评估。
- [SHOULD] 继续保留现有 ML 与 validation 叙事，但把表述收敛到具体问题和方法，避免看起来像泛化的工具堆叠。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-whoop-sensorintelligence/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-whoop-sensorintelligence/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-whoop-sensorintelligence/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-whoop-sensorintelligence/codex.json`

## conf/Hopper-CustomerPlatform

- 目标岗位: Senior Software Engineer - Customer Experience Platform @ Hopper
- 分数/结论: 97.0 / pass
- 耗时: 53.0 秒
- 严重度计数: critical=0, high=0, medium=2, low=0
- 规则 ID: P1-030, P2-001

### 优先修改项
- [SHOULD] Rewrite the first Summary bullet to lead with a backend/customer-experience role anchor instead of 'transitioning from analytics'.
- [SHOULD] Make all three Summary bullets verb-led so the top section reads like an engineering resume, not a profile statement.
- [NICE] Keep the current technical breadth and experience ordering; the stack coverage itself is already aligned with the JD.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-hopper-customerplatform/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-hopper-customerplatform/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-hopper-customerplatform/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-hopper-customerplatform/codex.json`

## conf/Nuro-OffboardInfra

- 目标岗位: Software Engineer, Offboard Infrastructure @ Nuro
- 分数/结论: 97.5 / pass
- 耗时: 65.0 秒
- 严重度计数: critical=0, high=0, medium=3, low=0
- 规则 ID: P1-040, P2-010, P3D-001

### 优先修改项
- [SHOULD] 给 Professional Summary 的核心技术词和量化信号加粗，恢复首屏视觉抓手。
- [SHOULD] 把第三句 Summary 改成更强的认知型 header，避免 collaborator 这种弱 framing。
- [SHOULD] 给 TikTok 最新经历补一个 Tier 1 scope 锚点，替代纯百分比叙事。
- [NICE] 其余经历结构保持不动，不要改不可变字段或经历顺序。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-nuro-offboardinfra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-nuro-offboardinfra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-nuro-offboardinfra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-nuro-offboardinfra/codex.json`

## conf/AMH-EnterpriseDataAnalyst

- 目标岗位: Senior Enterprise Data Analyst @ AMH
- 分数/结论: 93.5 / pass
- 耗时: 60.0 秒
- 严重度计数: critical=0, high=1, medium=4, low=0
- 规则 ID: P1-030, P1-042, P3B-004, P3C-010, P3D-001

### 优先修改项
- [MUST] Rewrite the first Summary bullet so it starts with a verb and stays explicitly data-analyst focused.
- [MUST] Tighten the TikTok section into a narrower core narrative and add one concrete scope anchor to the lead bullet.
- [SHOULD] Add one bridge sentence linking prior analytics/reporting work to AMH's rental/homebuilding BI and financial-reporting context.
- [NICE] Remove bold formatting from qualifier phrases like `team-owned` and `team-maintained`.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-amh-enterprisedataanalyst/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-amh-enterprisedataanalyst/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-amh-enterprisedataanalyst/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-amh-enterprisedataanalyst/codex.json`

## conf/Phantom-SDET

- 目标岗位: SDET (Wallet Platform) @ Phantom
- 分数/结论: 91.6 / fail
- 耗时: 75.0 秒
- 严重度计数: critical=0, high=1, medium=3, low=0
- 规则 ID: P1-042, P2-001, P2-040, P3B-001

### 优先修改项
- [MUST] Rewrite the first Summary sentence to lead with `SDET/backend engineer` signal, not the transition narrative.
- [MUST] Add one concrete bullet showing from-scratch test framework ownership plus API edge-case coverage (idempotency, retry, webhook, out-of-order delivery) and, if true, a post-mortem prevention action.
- [SHOULD] Rename the `APIs` skills category to `Testing & CI` or split it into clearer buckets.
- [NICE] Remove bold emphasis from qualifiers like `team-maintained` and `team-owned` so emphasis stays on technical and quantitative signals.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-phantom-sdet/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-phantom-sdet/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-phantom-sdet/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-phantom-sdet/codex.json`

## conf/VeteransUnited-AssociateSE

- 目标岗位: Associate Software Engineer (Remote/Hybrid) @ Veterans United Home Loans
- 分数/结论: 82.3 / fail
- 耗时: 86.0 秒
- 严重度计数: critical=0, high=3, medium=3, low=0
- 规则 ID: P1-042, P2-001, P2-020, P3B-001, P3B-002, P3D-001

### 优先修改项
- [MUST] 在最相关的后端经历里补出 `Web APIs` / microservice 证据，并明确写一个 AI coding assistant（Windsurf / ChatGPT / Copilot / Cursor）的实际使用场景。
- [MUST] 把 Summary 第一句改成角色方向开头，去掉首屏的转型叙事主导感。
- [SHOULD] 给 TikTok 首条经历补一个具体 scope 数字，让最新经历不只剩百分比结果。
- [NICE] 去掉对 `team-maintained`、`internal` 这类限定语的加粗。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-veteransunited-associatese/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-veteransunited-associatese/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-veteransunited-associatese/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-veteransunited-associatese/codex.json`

## conf/8451-ResearchAI

- 目标岗位: Senior AI/ML Engineer - Research (P4368) @ 84.51˚
- 分数/结论: 87.3 / fail
- 耗时: 83.0 秒
- 严重度计数: critical=0, high=2, medium=3, low=0
- 规则 ID: P1-040, P2-001, P2-010, P3A-002, P3B-001

### 优先修改项
- [MUST] 把 Summary 第一条改成 AI/ML / LLM 研究工程的角色前置开场，不要以“transitioning”起手。
- [MUST] 在 TikTok 最相关经历补一条可验证的 agentic / alignment / pretraining 类证据；如果没有这类经历，这个 JD 对你就是结构性错配。
- [SHOULD] 把正文里的 `Bedrock` 补进 Skills，或把相关表述改成能被 Skills 支撑的更泛化写法。
- [NICE] 把第三条 Summary header 换成更强的认知型标签，并统一处理未加粗的核心技术名词。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-8451-researchai/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-8451-researchai/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-8451-researchai/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-8451-researchai/codex.json`

## conf/Photon-AIEngineer

- 目标岗位: Artificial Intelligence Engineer @ Photon
- 分数/结论: 89.4 / fail
- 耗时: 56.0 秒
- 严重度计数: critical=0, high=2, medium=1, low=0
- 规则 ID: P2-001, P3B-001, P3D-001

### 优先修改项
- [MUST] 把 Summary 第一句改成角色/领域先行，避免以“transitioning”开场。
- [MUST] 在最相关的 RAG bullet 里补出 LangChain / LlamaIndex / 向量库 / 检索编排的真实使用证据。
- [SHOULD] 给 TikTok 最新经历补一个 Tier1 规模或 owner scope 锚点，降低“只有百分比提升”的观感。
- [NICE] 如果确实使用了更具体的检索或评估组件，把泛化的“RAG/LLM evaluation”改写成具体组件名和责任边界。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-photon-aiengineer/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-photon-aiengineer/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-photon-aiengineer/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-photon-aiengineer/codex.json`

## conf/Clarivate-NLP

- 目标岗位: Senior Data Scientist (NLP) @ Clarivate
- 分数/结论: 85.8 / fail
- 耗时: 73.0 秒
- 严重度计数: critical=0, high=2, medium=2, low=0
- 规则 ID: P2-001, P3B-001, P3B-010, P3D-001

### 优先修改项
- [MUST] Add explicit LangChain/LangGraph evidence in the most relevant NLP/RAG project bullet if true; otherwise the JD's core tool family is unproven.
- [MUST] Fix the experience-depth gap: the resume currently self-states 3+ years while the JD asks for 5+ years of NLP/Python experience.
- [SHOULD] Reframe the summary opening to remove 'candidate/transferable' language and lead with a direct NLP/ML role hook.
- [NICE] Replace one percentage-led bullet in the TikTok section with a scope/ownership bullet.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-clarivate-nlp/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-clarivate-nlp/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-clarivate-nlp/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-confirmation10_20260417_232542_770455/conf-clarivate-nlp/codex.json`
