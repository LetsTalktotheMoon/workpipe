# 30 Case 各版本分数总表

说明：

- 这里按你当前最终采用的 **30 个 case 最终修订标签** 来列。

- 单元格格式为 `分数/结论`。

- `未测试` 表示这个版本当时没有跑到这条 case，不代表 pass 或 fail。

- `old_pipe` 指旧的、不分阶段的 reviewer 系统；`v2` 到 `v10` 指后续迭代版本。


## 版本来源

| 版本 | 使用的最终 run | 覆盖范围 |
| --- | --- | --- |
| old_pipe | `old-pipe-codex/runs/20260417_185315_269474`<br>`old-pipe-codex/runs/20260417_222351_709578` | 20/30 |
| v2 | `iteration-runs/v2-hr-recal_20260417_193622_478749` | 10/30 |
| v3 | `iteration-runs/v3-hr-stable_20260417_195326_805428`<br>`iteration-runs/gen2-v3-hr-stable-retry_20260417_222046_433749`<br>`iteration-runs/v3-confirmation10_20260417_232542_771049` | 30/30 |
| v4 | `iteration-runs/v4-hr-converged-combined_20260417_202500_000000` | 10/30 |
| v5 | `iteration-runs/v5-hr-gate_20260417_202514_652388`<br>`iteration-runs/gen2-v5-hr-gate_20260417_220707_863686` | 20/30 |
| v6 | `iteration-runs/v6-hr-final_20260417_203626_630894`<br>`iteration-runs/gen2-v6-hr-final_20260417_220707_864016` | 20/30 |
| v7 | `iteration-runs/v7-gen2-jd-richer_20260417_223503_837943`<br>`iteration-runs/v7-gen2-jd-richer-geico-only_20260417_225504_044051`<br>`iteration-runs/v7-gen2-jd-richer-genentech-only_20260417_225504_044052`<br>`iteration-runs/v7-gen2-jd-richer-cisco-only_20260417_225504_051281`<br>`iteration-runs/v7-gen2-jd-richer-doordash-only_20260417_225504_060728` | 20/30 |
| v8 | `iteration-runs/v8-tooling-bridge-old10_20260417_225914_688788`<br>`iteration-runs/v8-tooling-bridge-gen2_20260417_225914_688602` | 20/30 |
| v9 | `iteration-runs/v9-gate-restore-old10_20260417_231136_106675`<br>`iteration-runs/v9-gate-restore-gen2_20260417_231136_106172`<br>`iteration-runs/v9-confirmation10_20260417_232542_770455` | 30/30 |
| v10 | `iteration-runs/v10-equiv-old10_20260417_234104_015942`<br>`iteration-runs/v10-equiv-gen2_20260417_234104_015941`<br>`iteration-runs/v10-equiv-conf10_20260417_234104_016175`<br>`iteration-runs/v10-equiv-old10-healthequity-only_20260417_235720_865332` | 30/30 |

## 主基准 20 Case

| Case | 人工判断 | old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| same/Google | pass | 79.0/fail | 92.8/pass | 94.1/pass | 86.2/fail | 94.4/pass | 91.2/pass | 90.9/pass | 94.4/pass | 98.0/pass | 94.4/pass |
| same/Amazon | fail | 93.3/pass | 97.8/pass | 95.0/pass | 95.3/pass | 97.3/pass | 95.8/pass | 90.8/fail | 96.9/pass | 91.2/fail | 89.2/fail |
| same/AWS | fail | 94.6/pass | 94.4/fail | 97.5/pass | 97.7/pass | 96.3/pass | 96.5/pass | 96.0/pass | 96.0/pass | 97.5/pass | 90.9/fail |
| same/Microsoft | fail | 88.1/fail | 90.4/pass | 90.3/fail | 95.8/pass | 95.8/pass | 91.8/fail | 78.5/fail | 84.7/fail | 87.7/fail | 90.5/fail |
| extra/CapitalOne-AI | fail | 89.2/fail | 95.2/pass | 87.9/fail | 88.6/fail | 91.9/fail | 96.2/pass | 90.9/fail | 92.4/fail | 85.3/fail | 82.5/fail |
| extra/Dataminr-Infra | fail | 92.8/fail | 97.4/pass | 99.0/pass | 98.5/pass | 95.5/pass | 98.5/pass | 90.7/fail | 95.8/pass | 92.9/fail | 91.3/fail |
| extra/HealthEquity-DotNet | fail | 93.5/pass | 88.8/pass | 89.6/fail | 88.6/pass | 97.0/pass | 94.5/pass | 81.5/fail | 86.8/fail | 84.0/fail | 84.3/fail |
| extra/Zoox-LLM | fail | 94.4/pass | 96.8/pass | 96.8/pass | 96.4/pass | 96.5/pass | 98.6/pass | 91.5/fail | 91.4/fail | 93.8/fail | 92.8/fail |
| extra/Synechron-Backend | pass | 89.5/fail | 95.0/pass | 99.2/pass | 100.0/pass | 100.0/pass | 99.7/pass | 99.5/pass | 100.0/pass | 98.5/pass | 99.5/pass |
| extra/Ramp-Platform | pass | 97.0/pass | 95.8/fail | 97.1/pass | 100.0/pass | 100.0/pass | 97.3/pass | 98.5/pass | 99.5/pass | 99.2/pass | 99.0/pass |
| gen2/Discord-DBInfra | fail | 82.7/fail | 未测试 | 92.9/fail | 未测试 | 93.9/fail | 92.9/fail | 90.6/fail | 94.4/fail | 93.3/fail | 88.8/fail |
| gen2/AppliedIntuition-CloudInfra | pass | 93.8/pass | 未测试 | 96.5/pass | 未测试 | 100.0/pass | 96.3/pass | 97.0/pass | 90.9/fail | 96.2/pass | 95.3/pass |
| gen2/Fireblocks-SRE | pass | 96.1/pass | 未测试 | 98.0/pass | 未测试 | 95.6/pass | 96.5/pass | 91.4/fail | 92.8/pass | 96.6/pass | 94.7/pass |
| gen2/ChildrensHospital-Azure | fail | 87.7/fail | 未测试 | 93.3/pass | 未测试 | 93.0/pass | 94.3/pass | 86.4/fail | 89.4/fail | 88.6/fail | 85.3/fail |
| gen2/CapitalOne-Manager2 | fail | 92.6/fail | 未测试 | 90.2/fail | 未测试 | 90.9/fail | 89.9/fail | 86.3/fail | 85.8/fail | 90.9/fail | 91.4/fail |
| gen2/Fanduel-AnalyticsManager | fail | 93.8/pass | 未测试 | 94.7/pass | 未测试 | 89.0/fail | 89.0/fail | 83.3/fail | 85.8/fail | 85.3/fail | 86.3/fail |
| gen2/Geico-SWE2 | pass | 91.7/fail | 未测试 | 97.0/pass | 未测试 | 96.5/pass | 96.3/pass | 92.4/fail | 96.6/pass | 93.9/pass | 95.1/pass |
| gen2/Doordash-Backend | pass | 94.4/pass | 未测试 | 96.0/pass | 未测试 | 97.0/pass | 96.3/pass | 95.8/pass | 97.0/pass | 98.0/pass | 98.0/pass |
| gen2/Cisco-NetworkingSenior | fail | 91.8/fail | 未测试 | 96.8/pass | 未测试 | 95.8/pass | 96.5/pass | 92.4/fail | 85.8/fail | 90.7/fail | 90.4/fail |
| gen2/Genentech-MLInfra | pass | 95.9/pass | 未测试 | 96.4/pass | 未测试 | 96.5/pass | 95.7/pass | 98.3/pass | 96.8/pass | 96.5/pass | 98.8/pass |

## 外部确认 10 Case

| Case | 人工判断 | old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conf/FlexTrade-SoftwareDeveloper | pass | 未测试 | 未测试 | 90.6/fail | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 94.1/pass | 92.2/pass |
| conf/Whoop-SensorIntelligence | fail | 未测试 | 未测试 | 94.0/pass | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 90.4/fail | 90.7/fail |
| conf/Hopper-CustomerPlatform | pass | 未测试 | 未测试 | 97.5/pass | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 97.0/pass | 95.5/pass |
| conf/Nuro-OffboardInfra | pass | 未测试 | 未测试 | 94.6/pass | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 97.5/pass | 98.1/pass |
| conf/AMH-EnterpriseDataAnalyst | pass | 未测试 | 未测试 | 98.0/pass | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 93.5/pass | 91.0/pass |
| conf/Phantom-SDET | pass | 未测试 | 未测试 | 95.5/pass | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 91.6/fail | 89.6/fail |
| conf/VeteransUnited-AssociateSE | pass | 未测试 | 未测试 | 95.8/pass | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 82.3/fail | 95.1/pass |
| conf/8451-ResearchAI | fail | 未测试 | 未测试 | 95.8/pass | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 87.3/fail | 87.8/fail |
| conf/Photon-AIEngineer | fail | 未测试 | 未测试 | 93.3/pass | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 89.4/fail | 89.7/fail |
| conf/Clarivate-NLP | fail | 未测试 | 未测试 | 99.7/pass | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 85.8/fail | 83.2/fail |

## 读取说明

- 如果某条 case 在很多早期版本里都是 `90+` 但结论仍是 `pass`，不代表它真的适合岗位，往往说明当时版本还没把年限、specialized domain、manager 门槛等问题识别出来。
- 你会看到部分 case 在多个版本之间分数变化不大，但 `verdict` 会在 `pass / conditional_pass / fail` 之间变化，这说明当时的扣分聚合或硬门槛策略在变。
- `conditional_pass` 是中间版本里出现过的中间态，本质上比 `pass` 更保守，但还没到直接 `fail`。