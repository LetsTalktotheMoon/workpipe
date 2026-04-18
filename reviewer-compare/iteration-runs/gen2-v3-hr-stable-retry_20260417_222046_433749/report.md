# gen2_v3_hr_stable_retry 结果

生成时间: 2026-04-17T22:31:45

| Case | 分数 | 结论 | 耗时(秒) | Critical | High | Medium | 主要规则 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| gen2/Discord-DBInfra | 92.9 | fail | 76.0 | 0 | 1 | 2 | P1-030, P1-042, P3B-001 |
| gen2/AppliedIntuition-CloudInfra | 96.5 | pass | 68.0 | 0 | 0 | 3 | P1-040, P2-001, P3D-001 |
| gen2/Fireblocks-SRE | 98.0 | pass | 56.0 | 0 | 0 | 1 | P2-001 |
| gen2/ChildrensHospital-Azure | 93.3 | pass | 54.0 | 0 | 0 | 8 | P1-042, P1-051, P2-001, P2-010, P2-040, P3B-003, P3D-001 |
| gen2/CapitalOne-Manager2 | 90.2 | fail | 88.0 | 0 | 2 | 2 | P2-001, P3B-010, P3C-010, P3D-001 |
| gen2/Fanduel-AnalyticsManager | 94.7 | pass | 69.0 | 0 | 0 | 6 | P1-040, P1-042, P2-001, P2-030, P3D-001, P3E-013 |
| gen2/Geico-SWE2 | 97.0 | pass | 55.0 | 0 | 0 | 3 | P2-001, P3D-001 |
| gen2/Doordash-Backend | 96.0 | pass | 52.0 | 0 | 0 | 4 | P1-040, P1-051, P2-001, P3D-001 |
| gen2/Cisco-NetworkingSenior | 96.8 | pass | 88.0 | 0 | 1 | 1 | P2-001, P3C-010 |
| gen2/Genentech-MLInfra | 96.4 | pass | 53.0 | 0 | 1 | 2 | P3B-003, P3C-010, P3D-001 |

## gen2/Discord-DBInfra

- 目标岗位: Software Engineer- Database Infrastructure @ Discord
- 分数/结论: 92.9 / fail
- 耗时: 76.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P1-030, P1-042, P3B-001

### 优先修改项
- [MUST] Add Rust evidence or treat the Discord JD as a structural mismatch.
- [MUST] Remove bolding from qualifiers; keep bold only for technologies and metrics.
- [SHOULD] Rework the Summary into verb-led clauses while preserving the 3-sentence structure.
- [NICE] Add one explicit database/storage ownership signal in the most relevant backend bullet to sharpen the infra story.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-discord-dbinfra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-discord-dbinfra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-discord-dbinfra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-discord-dbinfra/codex.json`

## gen2/AppliedIntuition-CloudInfra

- 目标岗位: Software Engineer - Cloud Infrastructure @ Applied Intuition
- 分数/结论: 96.5 / pass
- 耗时: 68.0 秒
- 严重度计数: critical=0, high=0, medium=3, low=0
- 规则 ID: P1-040, P2-001, P3D-001

### 优先修改项
- [MUST] Rewrite the Summary opener so it leads with backend/cloud-infra identity instead of the transition story.
- [MUST] Add one concrete Tier 1 scope anchor to the first TikTok bullet and one DiDi bullet so the senior infra narrative is not mostly percentage-based.
- [MUST] Bold the strongest quantified or scope tokens in the major bullets and baselines to surface the best evidence faster.
- [NICE] Keep the current technology set unchanged; the main issue is framing and evidence density, not stack coverage.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-appliedintuition-cloudinfra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-appliedintuition-cloudinfra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-appliedintuition-cloudinfra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-appliedintuition-cloudinfra/codex.json`

## gen2/Fireblocks-SRE

- 目标岗位: Site Reliability Engineer @ Fireblocks
- 分数/结论: 98.0 / pass
- 耗时: 56.0 秒
- 严重度计数: critical=0, high=0, medium=1, low=0
- 规则 ID: P2-001

### 优先修改项
- [SHOULD] 重写 Summary 第一句，改成角色方向和领域信号先行，避免“Transitioning from ...”抢占首屏。
- [NICE] 如果要增强 senior SRE 叙事，把一个更强的系统/规模信号前置到首屏。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-fireblocks-sre/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-fireblocks-sre/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-fireblocks-sre/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-fireblocks-sre/codex.json`

## gen2/ChildrensHospital-Azure

- 目标岗位: Azure Software Engineer Professional @ Children's Hospital Colorado
- 分数/结论: 93.3 / pass
- 耗时: 54.0 秒
- 严重度计数: critical=0, high=0, medium=8, low=0
- 规则 ID: P1-042, P1-051, P2-001, P2-010, P2-040, P3B-003, P3D-001

### 优先修改项
- [MUST] 把 Summary 改成直接的后端/系统设计定位，删掉首句的转型感和第三句的弱标题感。
- [MUST] 给 Azure 岗位补一条明确的云平台桥接证据；如果没有 Azure 经验，就把云叙事改成更中性的后端系统迁移叙事。
- [MUST] 给 TikTok 最新经历和关键项目各补一个可追问的 scope 信号，避免整段主要靠百分比结果支撑。
- [SHOULD] 压缩 Skills 行长度，并把 `APIs` 这种弱类别名改成更具体的标题。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-childrenshospital-azure/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-childrenshospital-azure/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-childrenshospital-azure/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-childrenshospital-azure/codex.json`

## gen2/CapitalOne-Manager2

- 目标岗位: Manager, Data Analysis - Card Services @ Capital One
- 分数/结论: 90.2 / fail
- 耗时: 88.0 秒
- 严重度计数: critical=0, high=2, medium=2, low=0
- 规则 ID: P2-001, P3B-010, P3C-010, P3D-001

### 优先修改项
- [MUST] If there was no real people-management scope, do not present this as a Manager profile; if there was, add explicit leadership evidence in the most senior experience.
- [MUST] Tighten the top-level Skills stack so it reads like a focused core, not a broad inventory of every tool ever touched.
- [SHOULD] Add one concrete scale anchor to the TikTok experience so the percentage wins have visible operating context.
- [NICE] Reword the Summary opener so it starts with a role/domain anchor instead of 'Candidate' language.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-capitalone-manager2/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-capitalone-manager2/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-capitalone-manager2/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-capitalone-manager2/codex.json`

## gen2/Fanduel-AnalyticsManager

- 目标岗位: Analytics Manager @ FanDuel
- 分数/结论: 94.7 / pass
- 耗时: 69.0 秒
- 严重度计数: critical=0, high=0, medium=6, low=0
- 规则 ID: P1-040, P1-042, P2-001, P2-030, P3D-001, P3E-013

### 优先修改项
- [SHOULD] Rewrite Summary sentence 1 so it starts with a direct role/domain anchor instead of `Transitioning from...`.
- [SHOULD] Move `SQL` and the analytics stack into the first Skills row so the first scan matches the JD.
- [SHOULD] Add one concrete scope metric to the latest TikTok bullet or project opener.
- [NICE] Add an explicit internal/no-user-data qualifier to the TikTok Bedrock/RAG bullet, and bold the strongest scope/ownership markers.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-fanduel-analyticsmanager/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-fanduel-analyticsmanager/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-fanduel-analyticsmanager/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-fanduel-analyticsmanager/codex.json`

## gen2/Geico-SWE2

- 目标岗位: Software Engineer II @ GEICO
- 分数/结论: 97.0 / pass
- 耗时: 55.0 秒
- 严重度计数: critical=0, high=0, medium=3, low=0
- 规则 ID: P2-001, P3D-001

### 优先修改项
- [MUST] Rewrite Summary bullet 1 to lead with the backend role and distributed-systems domain, not the analytics-transition phrase.
- [MUST] Add a concrete scope anchor to the TikTok intern section so the latest experience is not read as percentage-only impact.
- [MUST] Add a concrete scope anchor to the Temu section so the earliest experience is not read as percentage-only impact.
- [SHOULD] Keep the current technical coverage and two-project structure; the rest is broadly aligned.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-geico-swe2/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-geico-swe2/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-geico-swe2/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-geico-swe2/codex.json`

## gen2/Doordash-Backend

- 目标岗位: Software Engineer, Backend (All Teams) @ DoorDash
- 分数/结论: 96.0 / pass
- 耗时: 52.0 秒
- 严重度计数: critical=0, high=0, medium=4, low=0
- 规则 ID: P1-040, P1-051, P2-001, P3D-001

### 优先修改项
- [SHOULD] Reframe the opening Summary line so it leads with backend specialization instead of transition language.
- [SHOULD] Add one concrete Tier 1 scope anchor to the TikTok section so the latest experience is easier to calibrate.
- [SHOULD] Compress the Skills rows to keep only the highest-signal stack items and satisfy the line-length cap.
- [NICE] Bold the main scope and impact numbers consistently across Summary and Experience for stronger scanability.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-doordash-backend/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-doordash-backend/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-doordash-backend/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-doordash-backend/codex.json`

## gen2/Cisco-NetworkingSenior

- 目标岗位: Senior Software Engineer- Networking Technologies @ Cisco
- 分数/结论: 96.8 / pass
- 耗时: 88.0 秒
- 严重度计数: critical=0, high=1, medium=1, low=0
- 规则 ID: P2-001, P3C-010

### 优先修改项
- [MUST] Narrow the TikTok internship to 2 core stacks and make support infra explicitly auxiliary.
- [SHOULD] Rewrite the opening Summary to lead with backend/security rather than transition language.
- [SHOULD] Add one Tier-1 scope metric near the top of TikTok or DiDi if available.
- [NICE] Keep the rest of the content; it already covers the Cisco must-haves.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-cisco-networkingsenior/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-cisco-networkingsenior/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-cisco-networkingsenior/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-cisco-networkingsenior/codex.json`

## gen2/Genentech-MLInfra

- 目标岗位: Machine Learning Engineer/Senior Machine Learning Engineer - Infra @ Genentech
- 分数/结论: 96.4 / pass
- 耗时: 53.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P3B-003, P3C-010, P3D-001

### 优先修改项
- [MUST] 将 TikTok 实习段从多语言堆栈清单改成 2-3 个主系统故事，避免一段里同时展示过多同类技术。
- [MUST] 为 TikTok 最新经历补一个真实可追问的 scope 事实，避免整段只剩百分比改进。
- [SHOULD] 在 Summary 或相关经历里补一条到 Genentech 的迁移桥接，明确为什么这套 privacy-sensitive retrieval/evaluation 经验适合医疗/生物技术场景。
- [NICE] 若有真实基线，把部分“improved by X%”改成带对象、窗口和 ownership 的表述。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-genentech-mlinfra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-genentech-mlinfra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-genentech-mlinfra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749/gen2-genentech-mlinfra/codex.json`
