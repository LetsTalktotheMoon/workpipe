# v10_equiv_gen2 结果

生成时间: 2026-04-17T23:52:22

| Case | 分数 | 结论 | 耗时(秒) | Critical | High | Medium | 主要规则 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| gen2/Discord-DBInfra | 88.8 | fail | 79.0 | 0 | 2 | 0 | P3B-001, P3B-012 |
| gen2/AppliedIntuition-CloudInfra | 95.3 | pass | 75.0 | 0 | 1 | 3 | P1-042, P2-001, P3C-010, P3D-001 |
| gen2/Fireblocks-SRE | 94.7 | pass | 68.0 | 0 | 0 | 3 | P1-042, P2-001, P3B-004 |
| gen2/ChildrensHospital-Azure | 85.3 | fail | 58.0 | 0 | 2 | 3 | P1-042, P2-001, P2-010, P3B-001, P3B-012 |
| gen2/CapitalOne-Manager2 | 91.4 | fail | 64.0 | 0 | 1 | 2 | P2-001, P3B-010, P3D-001 |
| gen2/Fanduel-AnalyticsManager | 86.3 | fail | 66.0 | 0 | 2 | 2 | P1-042, P2-001, P3B-001, P3B-010 |
| gen2/Geico-SWE2 | 95.1 | pass | 52.0 | 0 | 0 | 4 | P1-040, P2-001, P3B-013, P3D-001 |
| gen2/Doordash-Backend | 98.0 | pass | 44.0 | 0 | 0 | 1 | P2-001 |
| gen2/Cisco-NetworkingSenior | 90.4 | fail | 100.0 | 0 | 1 | 4 | P1-040, P1-042, P2-001, P3B-012, P3D-001 |
| gen2/Genentech-MLInfra | 98.8 | pass | 72.0 | 0 | 1 | 0 | P3C-010 |

## gen2/Discord-DBInfra

- 目标岗位: Software Engineer- Database Infrastructure @ Discord
- 分数/结论: 88.8 / fail
- 耗时: 79.0 秒
- 严重度计数: critical=0, high=2, medium=0, low=0
- 规则 ID: P3B-001, P3B-012

### 优先修改项
- [MUST] Add a direct database-infrastructure bullet in the most relevant experience, not just adjacent backend/data work, and name the actual DB responsibility and outcome.
- [MUST] Surface Rust only if it was truly used; otherwise this JD remains a language-signal gap.
- [SHOULD] Shorten the Skills lines so each category stays under 14 words while keeping the same three categories.
- [NICE] Reduce the all-percentage cadence in the newest experience by adding one scope or ownership clause to the strongest bullet.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-discord-dbinfra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-discord-dbinfra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-discord-dbinfra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-discord-dbinfra/codex.json`

## gen2/AppliedIntuition-CloudInfra

- 目标岗位: Software Engineer - Cloud Infrastructure @ Applied Intuition
- 分数/结论: 95.3 / pass
- 耗时: 75.0 秒
- 严重度计数: critical=0, high=1, medium=3, low=0
- 规则 ID: P1-042, P2-001, P3C-010, P3D-001

### 优先修改项
- [MUST] 把 Summary 第一句改成直接的 cloud infrastructure / backend engineer 定位，别让“Transitioning from data analysis”占首屏。
- [MUST] 收敛 TikTok 和 DiDi 的语言栈展示，每段经历只保留 1-2 个主语言作为主线，其余语言只在必要的具体 bullet 中出现。
- [MUST] 在 TikTok 最新经历或项目里补一个 Tier 1 scope 信号，让首屏不只剩百分比提升。
- [SHOULD] 去掉修饰词的加粗，只保留技术名词、系统名和规模数字的加粗。
- [SHOULD] 如果确实有 cloud-infra / multi-cloud / simulation 相关桥接点，补一句把安全/电商/运营平台经验和目标岗位连接起来。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-appliedintuition-cloudinfra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-appliedintuition-cloudinfra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-appliedintuition-cloudinfra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-appliedintuition-cloudinfra/codex.json`

## gen2/Fireblocks-SRE

- 目标岗位: Site Reliability Engineer @ Fireblocks
- 分数/结论: 94.7 / pass
- 耗时: 68.0 秒
- 严重度计数: critical=0, high=0, medium=3, low=0
- 规则 ID: P1-042, P2-001, P3B-004

### 优先修改项
- [SHOULD] 把 Summary 首句改成目标岗位锚点优先的写法，先给出 SRE/backend + security/reliability 方向，再提转行背景。
- [SHOULD] 统一加粗策略：只强调技术名词和真正的规模/结果信号，去掉 `team-maintained` 这类修饰语的加粗。
- [SHOULD] 补一条 Fireblocks 相关的迁移桥接句，把 security / observability / incident response 经验直接连到高信任生产平台。
- [NICE] 若要进一步增强首屏，可把最强的系统边界和规模信号前置到第一条 TikTok bullet。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-fireblocks-sre/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-fireblocks-sre/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-fireblocks-sre/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-fireblocks-sre/codex.json`

## gen2/ChildrensHospital-Azure

- 目标岗位: Azure Software Engineer Professional @ Children's Hospital Colorado
- 分数/结论: 85.3 / fail
- 耗时: 58.0 秒
- 严重度计数: critical=0, high=2, medium=3, low=0
- 规则 ID: P1-042, P2-001, P2-010, P3B-001, P3B-012

### 优先修改项
- [MUST] 在最相关经历里补出明确的 Azure 和 C# 使用证据；当前简历对该 JD 的核心平台栈覆盖不成立。
- [MUST] 把 Summary 第一句改成目标角色先行的写法，先锚定 Azure/backend，再把 analytics 迁移经历作为补充。
- [SHOULD] 去掉修饰语的加粗，尤其是 "existing" 这类限定词，只保留技术名词和可核验结果的强调。
- [NICE] 把 "Team Fit" 这种泛化标题换成更有判断力的认知型标题。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-childrenshospital-azure/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-childrenshospital-azure/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-childrenshospital-azure/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-childrenshospital-azure/codex.json`

## gen2/CapitalOne-Manager2

- 目标岗位: Manager, Data Analysis - Card Services @ Capital One
- 分数/结论: 91.4 / fail
- 耗时: 64.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P2-001, P3B-010, P3D-001

### 优先修改项
- [MUST] 删除 Summary 首句里的 `Candidate` framing，改成直接的 data analytics 角色锚点。
- [MUST] 这份简历目前不满足 `Manager` / `6+ years` / people management 预期；如果没有真实领导证据，就不要把它包装成管理岗匹配。
- [SHOULD] 在最新的 TikTok 段补 1-2 个真实规模信号，提升首屏可信度。
- [NICE] 如果确实有 `Tableau` / `R`，再补进 Skills 和最相关经历。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-capitalone-manager2/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-capitalone-manager2/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-capitalone-manager2/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-capitalone-manager2/codex.json`

## gen2/Fanduel-AnalyticsManager

- 目标岗位: Analytics Manager @ FanDuel
- 分数/结论: 86.3 / fail
- 耗时: 66.0 秒
- 严重度计数: critical=0, high=2, medium=2, low=0
- 规则 ID: P1-042, P2-001, P3B-001, P3B-010

### 优先修改项
- [MUST] 补出 Excel 和可视化工具的真实使用证据，最好放在 DiDi 的分析/报表/复盘相关 bullet 里，直接对齐 JD minimum qualifications。
- [MUST] 处理 Analytics Manager 的结构性缺口：当前时间线和经历内容都没有支撑 5+ 年与 people management/coaching scope。
- [SHOULD] 把 Summary 第一行改成直接的 analytics/security 角色锚点，弱化“transitioning”叙事。
- [NICE] 统一正文加粗策略，只保留技术名词和规模信号加粗，去掉修饰语加粗。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-fanduel-analyticsmanager/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-fanduel-analyticsmanager/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-fanduel-analyticsmanager/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-fanduel-analyticsmanager/codex.json`

## gen2/Geico-SWE2

- 目标岗位: Software Engineer II @ GEICO
- 分数/结论: 95.1 / pass
- 耗时: 52.0 秒
- 严重度计数: critical=0, high=0, medium=4, low=0
- 规则 ID: P1-040, P2-001, P3B-013, P3D-001

### 优先修改项
- [MUST] 给 TikTok 或 DiDi 增补 PowerShell 的真实使用证据，补齐 JD 的支持性交付工具要求。
- [MUST] 把最重要的量化数字加粗，尤其是能体现 scope 的数字和最强结果对比。
- [SHOULD] 把 Summary 第一段改成直接的 backend / security 角色锚点，弱化 'Transitioning from Analytics' 的首屏转型叙事。
- [NICE] 在 TikTok 段补一个 Tier 1 规模指标，减少整份简历对百分比结果的依赖。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-geico-swe2/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-geico-swe2/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-geico-swe2/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-geico-swe2/codex.json`

## gen2/Doordash-Backend

- 目标岗位: Software Engineer, Backend (All Teams) @ DoorDash
- 分数/结论: 98.0 / pass
- 耗时: 44.0 秒
- 严重度计数: critical=0, high=0, medium=1, low=0
- 规则 ID: P2-001

### 优先修改项
- [SHOULD] 重写 Summary 第一句，先给 backend / distributed systems / scalability 的角色锚点，再保留 analytics 到 backend 的迁移说明。
- [NICE] 若要进一步增强首屏抓手，可让 TikTok 第一条 bullet 更直接体现服务边界或 ownership，而不是先写结果数字。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-doordash-backend/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-doordash-backend/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-doordash-backend/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-doordash-backend/codex.json`

## gen2/Cisco-NetworkingSenior

- 目标岗位: Senior Software Engineer- Networking Technologies @ Cisco
- 分数/结论: 90.4 / fail
- 耗时: 100.0 秒
- 严重度计数: critical=0, high=1, medium=4, low=0
- 规则 ID: P1-040, P1-042, P2-001, P3B-012, P3D-001

### 优先修改项
- [MUST] Recast the opening Summary as role-led and domain-led, not transition-led.
- [MUST] Surface direct networking-substrate evidence in the TikTok section, or treat this Cisco role as a structural mismatch.
- [SHOULD] Add one concrete scope/ownership metric to the TikTok internship section if it is true.
- [NICE] Tighten emphasis rules by bolding key metrics and removing bold from modifiers like team-maintained.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-cisco-networkingsenior/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-cisco-networkingsenior/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-cisco-networkingsenior/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-cisco-networkingsenior/codex.json`

## gen2/Genentech-MLInfra

- 目标岗位: Machine Learning Engineer/Senior Machine Learning Engineer - Infra @ Genentech
- 分数/结论: 98.8 / pass
- 耗时: 72.0 秒
- 严重度计数: critical=0, high=1, medium=0, low=0
- 规则 ID: P3C-010

### 优先修改项
- [MUST] Narrow the TikTok sandbox project bullet so it no longer implies one intern personally owned Go + Java + Scala + Rust + C++ in a single workstream.
- [SHOULD] If you still want to reduce breadth perception, compress Summary bullet 1 to fewer languages and keep the rest distributed across the relevant experience bullets.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-genentech-mlinfra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-genentech-mlinfra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-genentech-mlinfra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v10-equiv-gen2_20260417_234104_015941/gen2-genentech-mlinfra/codex.json`
