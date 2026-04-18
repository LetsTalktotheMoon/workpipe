# v4_hr_converged_patch 结果

生成时间: 2026-04-17T20:23:04

| Case | 分数 | 结论 | 耗时(秒) | Critical | High | Medium | 主要规则 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| extra/Ramp-Platform | 100.0 | pass | 24.0 | 0 | 0 | 0 | none |
| extra/HealthEquity-DotNet | 88.6 | pass | 73.0 | 0 | 2 | 3 | P1-042, P2-001, P2-040, P3B-002, P3D-001 |

## extra/Ramp-Platform

- 目标岗位: Software Engineer, Infrastructure @ Ramp
- 分数/结论: 100.0 / pass
- 耗时: 24.0 秒
- 严重度计数: critical=0, high=0, medium=0, low=0
- 规则 ID: none

### 优先修改项

### 产物
- Prompt: `extra-ramp-platform/prompt.txt`
- Metadata: `extra-ramp-platform/metadata.json`
- 原始输出: `extra-ramp-platform/codex.raw.txt`
- JSON: `extra-ramp-platform/codex.json`

## extra/HealthEquity-DotNet

- 目标岗位: Software Engineer II @ HealthEquity
- 分数/结论: 88.6 / pass
- 耗时: 73.0 秒
- 严重度计数: critical=0, high=2, medium=3, low=0
- 规则 ID: P1-042, P2-001, P2-040, P3B-002, P3D-001

### 优先修改项
- [MUST] 把 Summary 第一条改成岗位前置的 backend/security headline，去掉 `transitioning from data analytics` 这种转型开场。
- [MUST] 在最相关的 China-company 经历里补出 MongoDB 的直接使用证据；不要只停留在 `MongoDB-compatible` 这种间接表述。
- [SHOULD] 给 TikTok 段补一个 tier-1 scope 信号，降低纯百分比结果的观感。
- [NICE] 把 `APIs` 这种泛分类改成更具体、更适合 6-8 秒扫读的技能分组。

### 产物
- Prompt: `extra-healthequity-dotnet/prompt.txt`
- Metadata: `extra-healthequity-dotnet/metadata.json`
- 原始输出: `extra-healthequity-dotnet/codex.raw.txt`
- JSON: `extra-healthequity-dotnet/codex.json`
