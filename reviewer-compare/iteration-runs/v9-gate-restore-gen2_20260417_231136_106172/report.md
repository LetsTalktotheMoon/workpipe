# v9_gate_restore_gen2 结果

生成时间: 2026-04-17T23:22:56

| Case | 分数 | 结论 | 耗时(秒) | Critical | High | Medium | 主要规则 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| gen2/Discord-DBInfra | 93.3 | fail | 69.0 | 0 | 1 | 2 | P1-042, P3B-012, P3C-011 |
| gen2/AppliedIntuition-CloudInfra | 96.2 | pass | 70.0 | 0 | 0 | 2 | P3B-001, P3D-001 |
| gen2/Fireblocks-SRE | 96.6 | pass | 85.0 | 0 | 0 | 2 | P2-001, P3B-013 |
| gen2/ChildrensHospital-Azure | 88.6 | fail | 66.0 | 0 | 2 | 3 | P1-040, P2-001, P2-010, P2-040, P3B-012 |
| gen2/CapitalOne-Manager2 | 90.9 | fail | 75.0 | 0 | 1 | 3 | P1-042, P2-001, P3B-010, P3D-001 |
| gen2/Fanduel-AnalyticsManager | 85.3 | fail | 58.0 | 0 | 2 | 3 | P1-042, P2-001, P3B-001, P3B-010, P3D-001 |
| gen2/Geico-SWE2 | 93.9 | pass | 75.0 | 0 | 1 | 4 | P1-042, P2-001, P3B-013, P3C-010, P3D-001 |
| gen2/Doordash-Backend | 98.0 | pass | 65.0 | 0 | 0 | 1 | P2-001 |
| gen2/Cisco-NetworkingSenior | 90.7 | fail | 73.0 | 0 | 2 | 2 | P1-040, P2-001, P3B-012, P3C-010 |
| gen2/Genentech-MLInfra | 96.5 | pass | 44.0 | 0 | 0 | 4 | P1-042, P3B-003, P3C-011, P3D-001 |

## gen2/Discord-DBInfra

- 目标岗位: Software Engineer- Database Infrastructure @ Discord
- 分数/结论: 93.3 / fail
- 耗时: 69.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P1-042, P3B-012, P3C-011

### 优先修改项
- [MUST] Add one explicit database-infrastructure bullet to the most relevant experience so the resume matches a Database Infrastructure role instead of only generic backend/data work.
- [MUST] Narrow or reframe the TikTok language stack so Go, Python, C++, and Java do not read like four equally primary languages in one internship.
- [SHOULD] Remove bolding from qualifier words such as `team-maintained`.
- [NICE] If available, add one concrete database-operation metric tied to HA, failover, replication, or query latency.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-discord-dbinfra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-discord-dbinfra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-discord-dbinfra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-discord-dbinfra/codex.json`

## gen2/AppliedIntuition-CloudInfra

- 目标岗位: Software Engineer - Cloud Infrastructure @ Applied Intuition
- 分数/结论: 96.2 / pass
- 耗时: 70.0 秒
- 严重度计数: critical=0, high=0, medium=2, low=0
- 规则 ID: P3B-001, P3D-001

### 优先修改项
- [SHOULD] Close the GCP gap in the Cloud skill story by adding a truthful GCP deployment/ops bullet if it exists.
- [SHOULD] Add one concrete scope metric to the TikTok first bullet so the newest experience reads as infrastructure at scale, not just percentage improvement.
- [NICE] Keep the rest of the structure, summary framing, and immutable fields unchanged.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-appliedintuition-cloudinfra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-appliedintuition-cloudinfra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-appliedintuition-cloudinfra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-appliedintuition-cloudinfra/codex.json`

## gen2/Fireblocks-SRE

- 目标岗位: Site Reliability Engineer @ Fireblocks
- 分数/结论: 96.6 / pass
- 耗时: 85.0 秒
- 严重度计数: critical=0, high=0, medium=2, low=0
- 规则 ID: P2-001, P3B-013

### 优先修改项
- [SHOULD] Rewrite the Summary opening so it leads with "Reliability-focused backend/SRE engineer" instead of the transition narrative.
- [SHOULD] Add explicit config-management / GitOps evidence (ArgoCD or Ansible equivalent) in the most relevant infra-heavy experience bullet.
- [SHOULD] If true, add one concrete reliability scale anchor to the newest experience so the SRE story reads as operating at material scope, not only local optimization.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-fireblocks-sre/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-fireblocks-sre/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-fireblocks-sre/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-fireblocks-sre/codex.json`

## gen2/ChildrensHospital-Azure

- 目标岗位: Azure Software Engineer Professional @ Children's Hospital Colorado
- 分数/结论: 88.6 / fail
- 耗时: 66.0 秒
- 严重度计数: critical=0, high=2, medium=3, low=0
- 规则 ID: P1-040, P2-001, P2-010, P2-040, P3B-012

### 优先修改项
- [MUST] Add concrete Azure and C# evidence to the most relevant experience bullet, or treat this JD as a structural mismatch.
- [MUST] Reframe Summary sentence 1 so it starts with backend/platform direction instead of the transition story.
- [SHOULD] Replace the generic Summary sentence 3 header and the vague 'APIs' skill bucket with higher-signal labels.
- [NICE] Bold the main metric figures in bullets for faster ATS/manual scan.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-childrenshospital-azure/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-childrenshospital-azure/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-childrenshospital-azure/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-childrenshospital-azure/codex.json`

## gen2/CapitalOne-Manager2

- 目标岗位: Manager, Data Analysis - Card Services @ Capital One
- 分数/结论: 90.9 / fail
- 耗时: 75.0 秒
- 严重度计数: critical=0, high=1, medium=3, low=0
- 规则 ID: P1-042, P2-001, P3B-010, P3D-001

### 优先修改项
- [MUST] 先处理 Capital One 这个 Manager / 4+ years 门槛的结构性不匹配：当前可见 full-time 数据分析经验不足，且 people-management 证据不明确。
- [MUST] 把 Summary 第一句改成角色导向的首屏表述，不要用 `Candidate` 作为主标题。
- [SHOULD] 给 TikTok 最前面的 bullet 补一个真实的 scope 数字，降低纯百分比叙事的弱抓手问题。
- [SHOULD] 取消修饰语加粗，只保留技术名、规模数字和明确实体的加粗。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-capitalone-manager2/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-capitalone-manager2/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-capitalone-manager2/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-capitalone-manager2/codex.json`

## gen2/Fanduel-AnalyticsManager

- 目标岗位: Analytics Manager @ FanDuel
- 分数/结论: 85.3 / fail
- 耗时: 58.0 秒
- 严重度计数: critical=0, high=2, medium=3, low=0
- 规则 ID: P1-042, P2-001, P3B-001, P3B-010, P3D-001

### 优先修改项
- [MUST] 在最相关经历里补出 Excel 和明确的数据可视化软件证据，JD 的必需项现在缺少正文支撑。
- [MUST] 在 DiDi 段补出真实 people-management / coaching / task-prioritization 证据，当前不够支撑 Manager 职责。
- [SHOULD] 把 Summary 第一句从“转型中”改成直接的 analytics / risk / SQL-Python-Spark 角色锚点，提升首屏命中率。
- [SHOULD] 给 TikTok 最新经历补一个 Tier1 规模锚点，避免整段只剩百分比提升。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-fanduel-analyticsmanager/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-fanduel-analyticsmanager/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-fanduel-analyticsmanager/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-fanduel-analyticsmanager/codex.json`

## gen2/Geico-SWE2

- 目标岗位: Software Engineer II @ GEICO
- 分数/结论: 93.9 / pass
- 耗时: 75.0 秒
- 严重度计数: critical=0, high=1, medium=4, low=0
- 规则 ID: P1-042, P2-001, P3B-013, P3C-010, P3D-001

### 优先修改项
- [MUST] Add explicit PowerShell evidence in the most relevant backend/tooling experience.
- [MUST] Tighten the TikTok language-stack story so it does not read as broad stack padding.
- [SHOULD] Add one Tier 1 scope metric to the latest experience or project.
- [NICE] Reframe the summary opener around a direct backend/security pitch and bold scope qualifiers consistently.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-geico-swe2/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-geico-swe2/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-geico-swe2/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-geico-swe2/codex.json`

## gen2/Doordash-Backend

- 目标岗位: Software Engineer, Backend (All Teams) @ DoorDash
- 分数/结论: 98.0 / pass
- 耗时: 65.0 秒
- 严重度计数: critical=0, high=0, medium=1, low=0
- 规则 ID: P2-001

### 优先修改项
- [SHOULD] 将 Summary 第一句改成直接的 `Backend Engineer` framing，弱化“transitioning from analytics”的首屏占位。
- [NICE] 进一步压缩 Summary 的表述密度，保留 1-2 个最强后端信号，避免首屏信息过载。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-doordash-backend/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-doordash-backend/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-doordash-backend/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-doordash-backend/codex.json`

## gen2/Cisco-NetworkingSenior

- 目标岗位: Senior Software Engineer- Networking Technologies @ Cisco
- 分数/结论: 90.7 / fail
- 耗时: 73.0 秒
- 严重度计数: critical=0, high=2, medium=2, low=0
- 规则 ID: P1-040, P2-001, P3B-012, P3C-010

### 优先修改项
- [MUST] Rewrite the Summary opening to lead with a direct role/domain headline instead of 'transitioning from analytics'.
- [MUST] Add direct networking-substrate evidence to the most relevant experience if true; otherwise accept that this is a structural mismatch for Cisco Networking Technologies.
- [MUST] Reduce the appearance of four-primary-language pile-up in the TikTok internship by making one language primary and the rest supporting.
- [SHOULD] Bold the most important numbers and scope tokens in Summary and Experience for faster scanability.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-cisco-networkingsenior/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-cisco-networkingsenior/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-cisco-networkingsenior/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-cisco-networkingsenior/codex.json`

## gen2/Genentech-MLInfra

- 目标岗位: Machine Learning Engineer/Senior Machine Learning Engineer - Infra @ Genentech
- 分数/结论: 96.5 / pass
- 耗时: 44.0 秒
- 严重度计数: critical=0, high=0, medium=4, low=0
- 规则 ID: P1-042, P3B-003, P3C-011, P3D-001

### 优先修改项
- [SHOULD] 在最相关经历里补一条可量化的 scope 指标，提升 ML infra 岗位的首屏抓手。
- [SHOULD] 收敛 TikTok 段的编程语言密度，明确主责语言与集成语言的边界。
- [SHOULD] 在 Summary 增加一层面向 Genentech 的行业迁移桥接，强调 regulated / privacy-sensitive infra 经验。
- [NICE] 去掉限定词加粗，保留技术名词、系统名和量化数字的加粗即可。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-genentech-mlinfra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-genentech-mlinfra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-genentech-mlinfra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v9-gate-restore-gen2_20260417_231136_106172/gen2-genentech-mlinfra/codex.json`
