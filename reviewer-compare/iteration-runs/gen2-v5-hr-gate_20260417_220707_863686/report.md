# gen2_v5_hr_gate 结果

生成时间: 2026-04-17T22:16:38

| Case | 分数 | 结论 | 耗时(秒) | Critical | High | Medium | 主要规则 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| gen2/Discord-DBInfra | 93.9 | fail | 55.0 | 0 | 1 | 1 | P1-042, P3B-001 |
| gen2/AppliedIntuition-CloudInfra | 100.0 | pass | 32.0 | 0 | 0 | 0 | none |
| gen2/Fireblocks-SRE | 95.6 | pass | 59.0 | 0 | 0 | 3 | P2-001, P3B-003, P3D-001 |
| gen2/ChildrensHospital-Azure | 93.0 | pass | 59.0 | 0 | 2 | 3 | P1-042, P2-001, P2-010, P2-040, P3C-010 |
| gen2/CapitalOne-Manager2 | 90.9 | fail | 76.0 | 0 | 1 | 3 | P1-040, P2-001, P3B-010, P3D-001 |
| gen2/Fanduel-AnalyticsManager | 89.0 | fail | 56.0 | 0 | 1 | 4 | P2-001, P2-030, P3B-003, P3B-010, P3D-001 |
| gen2/Geico-SWE2 | 96.5 | pass | 46.0 | 0 | 0 | 4 | P1-042, P2-001, P3D-001 |
| gen2/Doordash-Backend | 97.0 | pass | 73.0 | 0 | 0 | 2 | P2-001, P3D-001 |
| gen2/Cisco-NetworkingSenior | 95.8 | pass | 63.0 | 0 | 1 | 3 | P1-042, P1-051, P2-001, P3C-010 |
| gen2/Genentech-MLInfra | 96.5 | pass | 52.0 | 0 | 0 | 4 | P1-042, P3B-003, P3C-011, P3D-001 |

## gen2/Discord-DBInfra

- 目标岗位: Software Engineer- Database Infrastructure @ Discord
- 分数/结论: 93.9 / fail
- 耗时: 55.0 秒
- 严重度计数: critical=0, high=1, medium=1, low=0
- 规则 ID: P1-042, P3B-001

### 优先修改项
- [MUST] 补出真实 Rust 使用证据到最相关的后端/基础设施经历，并同步进 Skills；如果没有真实 Rust，这版简历不算完整覆盖 Discord JD。
- [MUST] 去掉正文里对 team-maintained、internal、existing 这类修饰语的加粗，只保留技术名词和关键量化结果加粗。
- [SHOULD] 如果确有 Rust 经验，优先放在最强的 TikTok 或 DiDi bullet 中，形成与 C++ / Go / Java / Distributed Systems 的完整后端叙事。
- [NICE] 继续保持当前结构，不需要为了这份 JD 额外改 Summary 或项目数。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-discord-dbinfra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-discord-dbinfra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-discord-dbinfra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-discord-dbinfra/codex.json`

## gen2/AppliedIntuition-CloudInfra

- 目标岗位: Software Engineer - Cloud Infrastructure @ Applied Intuition
- 分数/结论: 100.0 / pass
- 耗时: 32.0 秒
- 严重度计数: critical=0, high=0, medium=0, low=0
- 规则 ID: none

### 优先修改项

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-appliedintuition-cloudinfra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-appliedintuition-cloudinfra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-appliedintuition-cloudinfra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-appliedintuition-cloudinfra/codex.json`

## gen2/Fireblocks-SRE

- 目标岗位: Site Reliability Engineer @ Fireblocks
- 分数/结论: 95.6 / pass
- 耗时: 59.0 秒
- 严重度计数: critical=0, high=0, medium=3, low=0
- 规则 ID: P2-001, P3B-003, P3D-001

### 优先修改项
- [MUST] 把 Summary 第一条改成直接的 SRE/backend/security 角色锚点，删除或后移“transitioning from data analysis”的叙事。
- [MUST] 增加一条明确桥接 Fireblocks 目标场景的句子，说明你做的是 security-sensitive / high-integrity infra、审计化发布或 incident response，而不是泛化的后台开发。
- [MUST] 在 TikTok 段补一个 Tier 1 规模或 ownership 信号，避免整段只剩百分比优化。
- [SHOULD] 如果 DiDi / Temu 里有真实 scope 数据，也用同样方式补一条，增强 senior SRE 的平台深度。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-fireblocks-sre/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-fireblocks-sre/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-fireblocks-sre/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-fireblocks-sre/codex.json`

## gen2/ChildrensHospital-Azure

- 目标岗位: Azure Software Engineer Professional @ Children's Hospital Colorado
- 分数/结论: 93.0 / pass
- 耗时: 59.0 秒
- 严重度计数: critical=0, high=2, medium=3, low=0
- 规则 ID: P1-042, P2-001, P2-010, P2-040, P3C-010

### 优先修改项
- [MUST] 把 Summary 第一句改成角色先行的 backend/software-engineer framing，弱化“transitioning from analytics”的首屏主轴。
- [MUST] 收敛 DiDi 段的前端栈叙事，避免 React/Angular/Vue 在同一角色里同时作为日常使用堆叠出现。
- [SHOULD] 去掉加粗的修饰词，只保留技术名词、系统名和量化结果加粗。
- [SHOULD] 把 Skills 里的 `APIs` 类别改成更具体的名字，提升首读信息量。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-childrenshospital-azure/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-childrenshospital-azure/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-childrenshospital-azure/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-childrenshospital-azure/codex.json`

## gen2/CapitalOne-Manager2

- 目标岗位: Manager, Data Analysis - Card Services @ Capital One
- 分数/结论: 90.9 / fail
- 耗时: 76.0 秒
- 严重度计数: critical=0, high=1, medium=3, low=0
- 规则 ID: P1-040, P2-001, P3B-010, P3D-001

### 优先修改项
- [MUST] Add explicit manager/lead scope or retarget the application away from Manager roles.
- [MUST] Rewrite the Summary opener to a direct role/domain hook and remove `Candidate`.
- [SHOULD] Add at least one Tier 1 scale/ownership signal to the latest TikTok line or project.
- [NICE] Standardize bolding for key scope and ownership cues across Experience.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-capitalone-manager2/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-capitalone-manager2/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-capitalone-manager2/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-capitalone-manager2/codex.json`

## gen2/Fanduel-AnalyticsManager

- 目标岗位: Analytics Manager @ FanDuel
- 分数/结论: 89.0 / fail
- 耗时: 56.0 秒
- 严重度计数: critical=0, high=1, medium=4, low=0
- 规则 ID: P2-001, P2-030, P3B-003, P3B-010, P3D-001

### 优先修改项
- [MUST] Add truthful manager/leadership evidence, or accept that this is a structural mismatch for an Analytics Manager role.
- [MUST] Rewrite the first Summary sentence to be role-first instead of transition-first.
- [MUST] Add one concrete scale/scope metric to the newest TikTok experience or project bullet.
- [SHOULD] Add one explicit bridge from prior security/ops work to fraud/payments/compliance analytics.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-fanduel-analyticsmanager/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-fanduel-analyticsmanager/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-fanduel-analyticsmanager/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-fanduel-analyticsmanager/codex.json`

## gen2/Geico-SWE2

- 目标岗位: Software Engineer II @ GEICO
- 分数/结论: 96.5 / pass
- 耗时: 46.0 秒
- 严重度计数: critical=0, high=0, medium=4, low=0
- 规则 ID: P1-042, P2-001, P3D-001

### 优先修改项
- [MUST] Rewrite the Summary opening to be role-first rather than transition-first, so the resume reads as an immediately credible backend/security profile.
- [MUST] Add concrete Tier 1 scope anchors to the TikTok and Temu bullets to avoid a resume that is mostly percentage deltas without scale.
- [SHOULD] Remove bolding from modifier words like `team-maintained`, `existing`, and `shared`; keep emphasis on technologies and scope signals.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-geico-swe2/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-geico-swe2/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-geico-swe2/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-geico-swe2/codex.json`

## gen2/Doordash-Backend

- 目标岗位: Software Engineer, Backend (All Teams) @ DoorDash
- 分数/结论: 97.0 / pass
- 耗时: 73.0 秒
- 严重度计数: critical=0, high=0, medium=2, low=0
- 规则 ID: P2-001, P3D-001

### 优先修改项
- [SHOULD] 把 Summary 第一行改成“角色 + 领域”开场，去掉“in transition”作为首屏主叙事。
- [SHOULD] 给 TikTok 最近一段经历补一个明确 scope 锚点，让量化结果更像真实 ownership 而不是单纯优化。
- [NICE] 如果要进一步增强说服力，可以在 DiDi 或 Temu 的其中一段再补一个团队/流程边界信号，平衡整份简历的百分比叙事。

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-doordash-backend/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-doordash-backend/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-doordash-backend/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-doordash-backend/codex.json`

## gen2/Cisco-NetworkingSenior

- 目标岗位: Senior Software Engineer- Networking Technologies @ Cisco
- 分数/结论: 95.8 / pass
- 耗时: 63.0 秒
- 严重度计数: critical=0, high=1, medium=3, low=0
- 规则 ID: P1-042, P1-051, P2-001, P3C-010

### 优先修改项
- [MUST] Rewrite Summary sentence 1 to open as a direct security/backend engineer fit, not as a transition profile.
- [MUST] Narrow the TikTok language stack presentation so Go/Java are primary and C++/Python are clearly supporting in specific bullets.
- [SHOULD] Remove bold from qualifiers like `team-maintained`; reserve bold for technologies and quantitative signals.
- [SHOULD] Compress the Programming skills row or split it so it satisfies the density rule.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-cisco-networkingsenior/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-cisco-networkingsenior/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-cisco-networkingsenior/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-cisco-networkingsenior/codex.json`

## gen2/Genentech-MLInfra

- 目标岗位: Machine Learning Engineer/Senior Machine Learning Engineer - Infra @ Genentech
- 分数/结论: 96.5 / pass
- 耗时: 52.0 秒
- 严重度计数: critical=0, high=0, medium=4, low=0
- 规则 ID: P1-042, P3B-003, P3C-011, P3D-001

### 优先修改项
- [SHOULD] Add one explicit bridge sentence for Genentech that ties the security / evaluation / replay work to regulated healthcare ML infra.
- [SHOULD] Trim the apparent multi-language surface area by marking which languages were primary versus support / integration languages in each role.
- [SHOULD] Add one Tier 1 scope signal to the TikTok section so the newest experience reads senior enough on first scan.
- [NICE] Remove bold from modifiers and keep the bolding pattern reserved for technologies and high-value metrics.

### 产物
- Prompt: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-genentech-mlinfra/prompt.txt`
- Metadata: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-genentech-mlinfra/metadata.json`
- 原始输出: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-genentech-mlinfra/codex.raw.txt`
- JSON: `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/gen2-v5-hr-gate_20260417_220707_863686/gen2-genentech-mlinfra/codex.json`
