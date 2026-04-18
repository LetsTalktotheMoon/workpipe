# v7_gen2_jd_richer_doordash_only 结果

生成时间: 2026-04-17T22:56:08

| Case | 分数 | 结论 | 耗时(秒) | Critical | High | Medium | 主要规则 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| gen2/Doordash-Backend | 95.8 | pass | 64.0 | 0 | 1 | 3 | P2-001, P3C-010, P3D-001 |

## gen2/Doordash-Backend

- 目标岗位: Software Engineer, Backend (All Teams) @ DoorDash
- 分数/结论: 95.8 / pass
- 耗时: 64.0 秒
- 严重度计数: critical=0, high=1, medium=3, low=0
- 规则 ID: P2-001, P3C-010, P3D-001

### 优先修改项
- [MUST] Rewrite the Summary opening to foreground backend scope and domain, not transition narrative.
- [MUST] Reduce the core language stack in Summary and Skills to 2 primary backend languages, and keep the others only in the bullets where they are proven.
- [SHOULD] Add one explicit scope anchor to the latest quantified bullets, especially TikTok and Temu, so impact is not just percentage or time deltas.
- [NICE] Bold the strongest result numbers in the lead bullets of each experience for faster human scanning.

### 产物
- Prompt: `gen2-doordash-backend/prompt.txt`
- Metadata: `gen2-doordash-backend/metadata.json`
- 原始输出: `gen2-doordash-backend/codex.raw.txt`
- JSON: `gen2-doordash-backend/codex.json`
