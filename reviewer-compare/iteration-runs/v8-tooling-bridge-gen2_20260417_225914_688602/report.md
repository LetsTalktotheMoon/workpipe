# v8_tooling_bridge_gen2 结果

生成时间: 2026-04-17T23:09:31

| Case | 分数 | 结论 | 耗时(秒) | Critical | High | Medium | 主要规则 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| gen2/Discord-DBInfra | 94.4 | fail | 52.0 | 0 | 1 | 0 | P3B-012 |
| gen2/AppliedIntuition-CloudInfra | 90.9 | fail | 76.0 | 0 | 1 | 3 | P1-042, P2-001, P3B-001, P3D-001 |
| gen2/Fireblocks-SRE | 92.8 | pass | 52.0 | 0 | 0 | 4 | P2-001, P3B-003, P3B-013, P3D-001 |
| gen2/ChildrensHospital-Azure | 89.4 | fail | 66.0 | 0 | 2 | 4 | P1-051, P2-001, P2-010, P2-040, P3B-012, P3C-010 |
| gen2/CapitalOne-Manager2 | 85.8 | fail | 70.0 | 0 | 2 | 2 | P2-001, P3B-001, P3B-010, P3D-001 |
| gen2/Fanduel-AnalyticsManager | 85.8 | fail | 69.0 | 0 | 2 | 2 | P2-001, P3B-001, P3B-010, P3D-001 |
| gen2/Geico-SWE2 | 96.6 | pass | 65.0 | 0 | 0 | 2 | P2-001, P2-020, P3B-013 |
| gen2/Doordash-Backend | 97.0 | pass | 45.0 | 0 | 0 | 2 | P2-001, P3D-001 |
| gen2/Cisco-NetworkingSenior | 85.8 | fail | 71.0 | 0 | 3 | 1 | P2-001, P3A-002, P3B-012, P3D-001 |
| gen2/Genentech-MLInfra | 96.8 | pass | 51.0 | 0 | 1 | 3 | P1-040, P1-042, P3C-010, P3D-001 |

## gen2/Discord-DBInfra

- 目标岗位: Software Engineer- Database Infrastructure @ Discord
- 分数/结论: 94.4 / fail
- 耗时: 52.0 秒
- 严重度计数: critical=0, high=1, medium=0, low=0
- 规则 ID: P3B-012

### 优先修改项
- [MUST] In the most relevant experience, add one explicit database-infrastructure ownership bullet so the resume proves Database Infrastructure fit instead of only adjacent backend/platform work.
- [MUST] Reframe the summary to foreground database infrastructure and operational reliability, not just general backend/data experience.
- [SHOULD] If Rust or PostgreSQL HA/replication work is real, surface it once in the same most-relevant bullet rather than leaving it implicit.
- [NICE] Keep the existing stack breadth, but reduce reliance on inference by naming the exact DB surface, operational action, and measured result in one place.

### 产物
- Prompt: `gen2-discord-dbinfra/prompt.txt`
- Metadata: `gen2-discord-dbinfra/metadata.json`
- 原始输出: `gen2-discord-dbinfra/codex.raw.txt`
- JSON: `gen2-discord-dbinfra/codex.json`

## gen2/AppliedIntuition-CloudInfra

- 目标岗位: Software Engineer - Cloud Infrastructure @ Applied Intuition
- 分数/结论: 90.9 / fail
- 耗时: 76.0 秒
- 严重度计数: critical=0, high=1, medium=3, low=0
- 规则 ID: P1-042, P2-001, P3B-001, P3D-001

### 优先修改项
- [MUST] 补齐或显式承认 GCP 证据缺口；这是这个云基础设施 JD 的主要多云门槛。
- [MUST] 把 Summary 首句改成直接的 cloud / platform / infrastructure SWE 定位，别以“Transitioning”开头。
- [SHOULD] 去掉 `team-maintained`、`internal` 这类限定词的加粗，只保留技术名词和量化结果加粗。
- [SHOULD] 在 TikTok 最新经历里补一个更硬的规模锚点，避免只剩局部效率提升。

### 产物
- Prompt: `gen2-appliedintuition-cloudinfra/prompt.txt`
- Metadata: `gen2-appliedintuition-cloudinfra/metadata.json`
- 原始输出: `gen2-appliedintuition-cloudinfra/codex.raw.txt`
- JSON: `gen2-appliedintuition-cloudinfra/codex.json`

## gen2/Fireblocks-SRE

- 目标岗位: Site Reliability Engineer @ Fireblocks
- 分数/结论: 92.8 / pass
- 耗时: 52.0 秒
- 严重度计数: critical=0, high=0, medium=4, low=0
- 规则 ID: P2-001, P3B-003, P3B-013, P3D-001

### 优先修改项
- [MUST] 重写 Summary 首句，直接以 SRE/backend + security/platform 能力开场，把“transitioning from data analysis”后移。
- [MUST] 在 Summary 或最相关经历里补一条面向 digital asset custody / regulated infra 的桥接语，说明迁移逻辑。
- [MUST] 在最相关经历里补出 ArgoCD / Ansible / Helm 或真实等价的发布配置自动化证据。
- [SHOULD] 给 TikTok 实习经历补一个更硬的 scope 指标，避免首屏被看成“百分比很多但范围不清”。

### 产物
- Prompt: `gen2-fireblocks-sre/prompt.txt`
- Metadata: `gen2-fireblocks-sre/metadata.json`
- 原始输出: `gen2-fireblocks-sre/codex.raw.txt`
- JSON: `gen2-fireblocks-sre/codex.json`

## gen2/ChildrensHospital-Azure

- 目标岗位: Azure Software Engineer Professional @ Children's Hospital Colorado
- 分数/结论: 89.4 / fail
- 耗时: 66.0 秒
- 严重度计数: critical=0, high=2, medium=4, low=0
- 规则 ID: P1-051, P2-001, P2-010, P2-040, P3B-012, P3C-010

### 优先修改项
- [MUST] Add a concrete Azure/C# proof point in the most relevant experience, or accept that this resume is structurally misaligned with the target JD.
- [MUST] Reframe Summary to lead with the target role first, not the analytics transition.
- [SHOULD] Tighten Skills so each row is compact and rename vague categories like 'APIs' to something more specific.
- [NICE] Reduce stack breadth in the DiDi section so the core technologies read as ownership, not listing.

### 产物
- Prompt: `gen2-childrenshospital-azure/prompt.txt`
- Metadata: `gen2-childrenshospital-azure/metadata.json`
- 原始输出: `gen2-childrenshospital-azure/codex.raw.txt`
- JSON: `gen2-childrenshospital-azure/codex.json`

## gen2/CapitalOne-Manager2

- 目标岗位: Manager, Data Analysis - Card Services @ Capital One
- 分数/结论: 85.8 / fail
- 耗时: 70.0 秒
- 严重度计数: critical=0, high=2, medium=2, low=0
- 规则 ID: P2-001, P3B-001, P3B-010, P3D-001

### 优先修改项
- [MUST] Surface a real R-based analytics bullet in the most relevant experience, or accept that this posting is not a full ATS match.
- [MUST] Resolve the manager-level scope gap by adding true project leadership / mentoring / cross-team ownership evidence, or retarget the resume to IC roles.
- [SHOULD] Reframe the first Summary bullet from "Data Analysis Candidate" to a direct role + domain anchor.
- [NICE] Add one concrete scope signal to the latest TikTok experience so the top of the page reads less like percentage-only impact.

### 产物
- Prompt: `gen2-capitalone-manager2/prompt.txt`
- Metadata: `gen2-capitalone-manager2/metadata.json`
- 原始输出: `gen2-capitalone-manager2/codex.raw.txt`
- JSON: `gen2-capitalone-manager2/codex.json`

## gen2/Fanduel-AnalyticsManager

- 目标岗位: Analytics Manager @ FanDuel
- 分数/结论: 85.8 / fail
- 耗时: 69.0 秒
- 严重度计数: critical=0, high=2, medium=2, low=0
- 规则 ID: P2-001, P3B-001, P3B-010, P3D-001

### 优先修改项
- [MUST] 补出 JD 要求的 Excel + 数据可视化证据，优先放在 DiDi 或 Temu 的最相关 bullet。
- [MUST] 补出管理/ coaching analysts / direct reports 的真实证据；如果无法补真经历，这份简历不应继续按 Analytics Manager 选型。
- [SHOULD] 把 Summary 第一句从“Transitioning…”改成直接岗位定位，减少首屏转型叙事。
- [NICE] 给 TikTok 段补一个更具体的规模或工作量锚点，减少纯百分比结果的堆叠感。

### 产物
- Prompt: `gen2-fanduel-analyticsmanager/prompt.txt`
- Metadata: `gen2-fanduel-analyticsmanager/metadata.json`
- 原始输出: `gen2-fanduel-analyticsmanager/codex.raw.txt`
- JSON: `gen2-fanduel-analyticsmanager/codex.json`

## gen2/Geico-SWE2

- 目标岗位: Software Engineer II @ GEICO
- 分数/结论: 96.6 / pass
- 耗时: 65.0 秒
- 严重度计数: critical=0, high=0, medium=2, low=1
- 规则 ID: P2-001, P2-020, P3B-013

### 优先修改项
- [MUST] 把 Summary 第一句改成 backend-first framing，去掉或后移“Transitioning from Analytics”的首屏权重。
- [MUST] 补一条真实的 PowerShell / CI-CD / IaC 证据到最相关的 cloud 或 deployment bullet，覆盖 JD 的 support-tool 要求。
- [SHOULD] 给 TikTok 第一条 bullet 加一个可追问的 scope 锚点，让开屏先看到规模再看到 28% 改进。
- [NICE] 轻微收敛转型叙事，减少首屏“路径变化”感。

### 产物
- Prompt: `gen2-geico-swe2/prompt.txt`
- Metadata: `gen2-geico-swe2/metadata.json`
- 原始输出: `gen2-geico-swe2/codex.raw.txt`
- JSON: `gen2-geico-swe2/codex.json`

## gen2/Doordash-Backend

- 目标岗位: Software Engineer, Backend (All Teams) @ DoorDash
- 分数/结论: 97.0 / pass
- 耗时: 45.0 秒
- 严重度计数: critical=0, high=0, medium=2, low=0
- 规则 ID: P2-001, P3D-001

### 优先修改项
- [SHOULD] 把 Summary 第一条从“转型叙事”改成“后端角色叙事”，把转型信息后移。
- [SHOULD] 在 TikTok 经历最前面的 bullet 补一个可核验的规模或 scope 锚点，提升首屏抓手。
- [NICE] 若要增强 DoorDash 匹配感，可在 Summary 或 DiDi 段补一句物流/marketplace/restaurant ops 语境桥接。

### 产物
- Prompt: `gen2-doordash-backend/prompt.txt`
- Metadata: `gen2-doordash-backend/metadata.json`
- 原始输出: `gen2-doordash-backend/codex.raw.txt`
- JSON: `gen2-doordash-backend/codex.json`

## gen2/Cisco-NetworkingSenior

- 目标岗位: Senior Software Engineer- Networking Technologies @ Cisco
- 分数/结论: 85.8 / fail
- 耗时: 71.0 秒
- 严重度计数: critical=0, high=3, medium=1, low=0
- 规则 ID: P2-001, P3A-002, P3B-012, P3D-001

### 优先修改项
- [MUST] 把 Summary 第一句从“转型叙事”改成目标角色开场，直接锚定 Security/backend 或 Linux/networking。
- [MUST] 若 TikTok 确有真实经历，就补一条直接的网络底层/平台证据；否则这份简历对 Cisco Networking Technologies 属于结构性错配。
- [MUST] 统一正文与 Skills 的工具命名，把 GitHub Actions 补入 Skills，或把相关 bullet 收敛成泛化 CI/CD。
- [SHOULD] 给最新经历补一个明确 scope 数字，让百分比结果有系统规模背景。

### 产物
- Prompt: `gen2-cisco-networkingsenior/prompt.txt`
- Metadata: `gen2-cisco-networkingsenior/metadata.json`
- 原始输出: `gen2-cisco-networkingsenior/codex.raw.txt`
- JSON: `gen2-cisco-networkingsenior/codex.json`

## gen2/Genentech-MLInfra

- 目标岗位: Machine Learning Engineer/Senior Machine Learning Engineer - Infra @ Genentech
- 分数/结论: 96.8 / pass
- 耗时: 51.0 秒
- 严重度计数: critical=0, high=1, medium=3, low=0
- 规则 ID: P1-040, P1-042, P3C-010, P3D-001

### 优先修改项
- [MUST] Tighten the TikTok intern section around 2-3 primary languages and one owned infra boundary instead of spreading the story across six languages.
- [MUST] Add one concrete scale metric to the TikTok first bullet or project block so the impact is not only percentage-based.
- [SHOULD] Remove bold from qualifier phrases like team-maintained, team-owned, and intern-owned.
- [NICE] Bold the strongest quantitative proof points consistently across Experience bullets.

### 产物
- Prompt: `gen2-genentech-mlinfra/prompt.txt`
- Metadata: `gen2-genentech-mlinfra/metadata.json`
- 原始输出: `gen2-genentech-mlinfra/codex.raw.txt`
- JSON: `gen2-genentech-mlinfra/codex.json`
