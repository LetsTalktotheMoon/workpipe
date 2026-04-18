# gen2_v6_hr_final 结果

生成时间: 2026-04-17T22:18:33

| Case | 分数 | 结论 | 耗时(秒) | Critical | High | Medium | 主要规则 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| gen2/Discord-DBInfra | 92.9 | fail | 71.0 | 0 | 1 | 2 | P1-042, P3B-001, P3D-001 |
| gen2/AppliedIntuition-CloudInfra | 96.3 | pass | 81.0 | 0 | 1 | 2 | P1-042, P2-001, P3C-010 |
| gen2/Fireblocks-SRE | 96.5 | pass | 75.0 | 0 | 0 | 3 | P1-030, P1-042, P2-001 |
| gen2/ChildrensHospital-Azure | 94.3 | pass | 76.0 | 0 | 1 | 4 | P1-042, P2-001, P2-010, P2-030, P3C-010 |
| gen2/CapitalOne-Manager2 | 89.9 | fail | 72.0 | 0 | 1 | 4 | P1-042, P2-001, P2-030, P3B-010, P3D-001 |
| gen2/Fanduel-AnalyticsManager | 89.0 | fail | 52.0 | 0 | 2 | 2 | P2-001, P3B-010, P3D-001, P3E-013 |
| gen2/Geico-SWE2 | 96.3 | pass | 60.0 | 0 | 1 | 2 | P1-042, P2-001, P3C-010 |
| gen2/Doordash-Backend | 96.3 | pass | 55.0 | 0 | 1 | 2 | P1-040, P2-001, P3C-010 |
| gen2/Cisco-NetworkingSenior | 96.5 | pass | 84.0 | 0 | 0 | 3 | P1-042, P2-001, P3D-001 |
| gen2/Genentech-MLInfra | 95.7 | pass | 60.0 | 0 | 0 | 3 | P1-030, P1-042, P3B-004 |

## gen2/Discord-DBInfra

- 目标岗位: Software Engineer- Database Infrastructure @ Discord
- 分数/结论: 92.9 / fail
- 耗时: 71.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P1-042, P3B-001, P3D-001

### 优先修改项
- [MUST] Add Rust evidence if it is genuinely supported by your work, ideally in the most relevant backend or infrastructure bullet.
- [MUST] Add one concrete Tier 1 scope signal to the TikTok experience so the latest role reads as scale-aware, not only improvement-aware.
- [SHOULD] Remove bold from modifiers like team-maintained and team-owned; keep emphasis on technologies, scope, and outcomes.

### 产物
- Prompt: `gen2-discord-dbinfra/prompt.txt`
- Metadata: `gen2-discord-dbinfra/metadata.json`
- 原始输出: `gen2-discord-dbinfra/codex.raw.txt`
- JSON: `gen2-discord-dbinfra/codex.json`

## gen2/AppliedIntuition-CloudInfra

- 目标岗位: Software Engineer - Cloud Infrastructure @ Applied Intuition
- 分数/结论: 96.3 / pass
- 耗时: 81.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P1-042, P2-001, P3C-010

### 优先修改项
- [MUST] Rewrite Summary bullet 1 so it opens with the target infra/backend/security role instead of the transition narrative.
- [MUST] Compress the Skills section so each category shows only the core stack, not every supported tool at the same prominence level.
- [SHOULD] Remove bold from modifiers and scope adjectives such as `team-maintained`, `internal`, `13-person`, and `20+ city`.
- [NICE] Keep the rest of the structure; it is parseable and mostly compliant.

### 产物
- Prompt: `gen2-appliedintuition-cloudinfra/prompt.txt`
- Metadata: `gen2-appliedintuition-cloudinfra/metadata.json`
- 原始输出: `gen2-appliedintuition-cloudinfra/codex.raw.txt`
- JSON: `gen2-appliedintuition-cloudinfra/codex.json`

## gen2/Fireblocks-SRE

- 目标岗位: Site Reliability Engineer @ Fireblocks
- 分数/结论: 96.5 / pass
- 耗时: 75.0 秒
- 严重度计数: critical=0, high=0, medium=3, low=0
- 规则 ID: P1-030, P1-042, P2-001

### 优先修改项
- [SHOULD] Rework Professional Summary bullet 1 so it opens with a direct backend/SRE/security identity instead of the career-transition clause.
- [SHOULD] Make the three Summary bullets more action-led for faster scanability.
- [SHOULD] Remove bold from qualifier phrases like `team-maintained` and keep emphasis only on technologies and key metrics.
- [NICE] If you want a stronger Fireblocks fit, add one bridge phrase connecting security ops, auditability, or release hardening to secure infrastructure.

### 产物
- Prompt: `gen2-fireblocks-sre/prompt.txt`
- Metadata: `gen2-fireblocks-sre/metadata.json`
- 原始输出: `gen2-fireblocks-sre/codex.raw.txt`
- JSON: `gen2-fireblocks-sre/codex.json`

## gen2/ChildrensHospital-Azure

- 目标岗位: Azure Software Engineer Professional @ Children's Hospital Colorado
- 分数/结论: 94.3 / pass
- 耗时: 76.0 秒
- 严重度计数: critical=0, high=1, medium=4, low=0
- 规则 ID: P1-042, P2-001, P2-010, P2-030, P3C-010

### 优先修改项
- [MUST] 重写 Summary 的首句和第三句标题：首句先给 backend/SWE 角色锚点，第三句把 `Team Fit` 换成认知型标题。
- [MUST] 去掉正文里对修饰语/限定语的加粗，只保留技术名词、数字和少量真正的结果信号加粗。
- [MUST] 收敛 DiDi 段的前端框架呈现方式，避免 React/Angular/Vue 作为并列堆叠信号出现。
- [SHOULD] 重新组织 Skills 首行，让它更直接地服务 Azure/backend 首筛，而不是停留在泛化的 `Programming`。

### 产物
- Prompt: `gen2-childrenshospital-azure/prompt.txt`
- Metadata: `gen2-childrenshospital-azure/metadata.json`
- 原始输出: `gen2-childrenshospital-azure/codex.raw.txt`
- JSON: `gen2-childrenshospital-azure/codex.json`

## gen2/CapitalOne-Manager2

- 目标岗位: Manager, Data Analysis - Card Services @ Capital One
- 分数/结论: 89.9 / fail
- 耗时: 72.0 秒
- 严重度计数: critical=0, high=1, medium=4, low=0
- 规则 ID: P1-042, P2-001, P2-030, P3B-010, P3D-001

### 优先修改项
- [MUST] Add explicit manager/leadership scope evidence, or acknowledge that the profile is currently closer to an IC data-analysis target than a Manager role.
- [MUST] Rewrite Summary sentence 1 to remove `Candidate` and lead with a clearer `Data Analyst` / `Data/Platform Analyst` framing.
- [MUST] Move `Data` / `Analytics` ahead of `Programming` in Skills so the first scan hit aligns with the JD.
- [SHOULD] Add one concrete scope metric to the TikTok first bullet and remove bold from descriptive qualifiers like `team-maintained` and `existing`.

### 产物
- Prompt: `gen2-capitalone-manager2/prompt.txt`
- Metadata: `gen2-capitalone-manager2/metadata.json`
- 原始输出: `gen2-capitalone-manager2/codex.raw.txt`
- JSON: `gen2-capitalone-manager2/codex.json`

## gen2/Fanduel-AnalyticsManager

- 目标岗位: Analytics Manager @ FanDuel
- 分数/结论: 89.0 / fail
- 耗时: 52.0 秒
- 严重度计数: critical=0, high=2, medium=2, low=0
- 规则 ID: P2-001, P3B-010, P3D-001, P3E-013

### 优先修改项
- [MUST] 把 Summary 首句改成直接的岗位/领域定位，去掉“Transitioning”式转型叙事。
- [MUST] 补出 Analytics Manager 级别的 leadership/ownership 证据；如果没有这类事实，当前版本更像 senior IC。
- [SHOULD] 在最新的 TikTok 经历里补 1 个可验证的 scope 锚点，替代纯百分比叙事。
- [SHOULD] 给 TikTok 的 Bedrock/RAG 项目补上明确的数据边界限定语，降低安全场景追问风险。

### 产物
- Prompt: `gen2-fanduel-analyticsmanager/prompt.txt`
- Metadata: `gen2-fanduel-analyticsmanager/metadata.json`
- 原始输出: `gen2-fanduel-analyticsmanager/codex.raw.txt`
- JSON: `gen2-fanduel-analyticsmanager/codex.json`

## gen2/Geico-SWE2

- 目标岗位: Software Engineer II @ GEICO
- 分数/结论: 96.3 / pass
- 耗时: 60.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P1-042, P2-001, P3C-010

### 优先修改项
- [MUST] 重写 Summary 第一句，改成直接的 backend/security 角色锚点，把“Transitioning from Analytics”降到次级信息。
- [MUST] 去掉修饰语加粗，只保留技术栈、规模数字、真正的 ownership 词加粗。
- [MUST] 收敛程序语言叙事，Summary 只保留 2-3 个核心语言，避免被读成堆栈炫技。
- [SHOULD] 在 Summary 或最近经历里补一小句迁移桥接，让 analytics -> backend 的路径更像“有意识的转向”而不是“广泛接触过很多技术”。

### 产物
- Prompt: `gen2-geico-swe2/prompt.txt`
- Metadata: `gen2-geico-swe2/metadata.json`
- 原始输出: `gen2-geico-swe2/codex.raw.txt`
- JSON: `gen2-geico-swe2/codex.json`

## gen2/Doordash-Backend

- 目标岗位: Software Engineer, Backend (All Teams) @ DoorDash
- 分数/结论: 96.3 / pass
- 耗时: 55.0 秒
- 严重度计数: critical=0, high=1, medium=2, low=0
- 规则 ID: P1-040, P2-001, P3C-010

### 优先修改项
- [MUST] Rewrite the Summary headline to lead with 'Backend Engineer' and remove 'in transition' from the opening framing.
- [MUST] Reduce programming-language breadth in the main experience bullets by assigning a primary language per role and demoting secondary languages to supporting context.
- [SHOULD] Bold the strongest metrics and scope markers in the lead bullet of each role and project so impact is visible in a 6-8 second scan.
- [NICE] Keep the analytics-to-backend bridge explicit, but put it in sentence 2 or 3 instead of the headline.

### 产物
- Prompt: `gen2-doordash-backend/prompt.txt`
- Metadata: `gen2-doordash-backend/metadata.json`
- 原始输出: `gen2-doordash-backend/codex.raw.txt`
- JSON: `gen2-doordash-backend/codex.json`

## gen2/Cisco-NetworkingSenior

- 目标岗位: Senior Software Engineer- Networking Technologies @ Cisco
- 分数/结论: 96.5 / pass
- 耗时: 84.0 秒
- 严重度计数: critical=0, high=0, medium=3, low=0
- 规则 ID: P1-042, P2-001, P3D-001

### 优先修改项
- [MUST] Add one explicit scope anchor to the TikTok lead bullet or project baseline so the newest experience reads like senior backend/networking work, not only local percentage improvements.
- [MUST] Fix the partial bolding in the DiDi project bullet (`**140+ week**ly`) and make scope-limiting qualifiers consistent where they carry meaning.
- [SHOULD] Reword Summary sentence 1 so it starts with a direct role/domain anchor instead of a transition narrative.
- [NICE] If you want extra polish, label primary vs supporting languages/tools in TikTok to reduce the impression of a very broad multi-language primary stack.

### 产物
- Prompt: `gen2-cisco-networkingsenior/prompt.txt`
- Metadata: `gen2-cisco-networkingsenior/metadata.json`
- 原始输出: `gen2-cisco-networkingsenior/codex.raw.txt`
- JSON: `gen2-cisco-networkingsenior/codex.json`

## gen2/Genentech-MLInfra

- 目标岗位: Machine Learning Engineer/Senior Machine Learning Engineer - Infra @ Genentech
- 分数/结论: 95.7 / pass
- 耗时: 60.0 秒
- 严重度计数: critical=0, high=0, medium=3, low=0
- 规则 ID: P1-030, P1-042, P3B-004

### 优先修改项
- [SHOULD] Rewrite the three Summary bullets into verb-led predicates while preserving the current three-header structure.
- [SHOULD] Add one explicit bridge to Genentech's biotech/healthcare context, using the existing privacy-sensitive and audit-friendly infra story.
- [NICE] Remove bolding from modifiers like 'team-maintained', 'intern-owned', 'team-owned', and 'existing'; keep bold on technologies and measurable scope only.

### 产物
- Prompt: `gen2-genentech-mlinfra/prompt.txt`
- Metadata: `gen2-genentech-mlinfra/metadata.json`
- 原始输出: `gen2-genentech-mlinfra/codex.raw.txt`
- JSON: `gen2-genentech-mlinfra/codex.json`
