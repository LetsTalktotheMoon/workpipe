# 版本对照总表

## 主基准（20 case, revised labels）

| 版本 | 命中 | 错判 | 高频高/致命规则 |
| --- | ---: | --- | --- |
| old_pipe | 12/20 | same/Google, same/Amazon, same/AWS, extra/HealthEquity-DotNet, extra/Zoox-LLM, extra/Synechron-Backend, gen2/Fanduel-AnalyticsManager, gen2/Geico-SWE2 | none |
| v3_hr_stable | 13/20 | same/Amazon, same/AWS, extra/Dataminr-Infra, extra/Zoox-LLM, gen2/ChildrensHospital-Azure, gen2/Fanduel-AnalyticsManager, gen2/Cisco-NetworkingSenior | P3C-010x5, P3B-001x3, P3B-010x2, P2-001x1, P3A-002x1 |
| v5_hr_gate | 12/20 | same/Amazon, same/AWS, same/Microsoft, extra/Dataminr-Infra, extra/HealthEquity-DotNet, extra/Zoox-LLM, gen2/ChildrensHospital-Azure, gen2/Cisco-NetworkingSenior | P3C-010x5, P3B-010x3, P3A-002x1, P3B-001x1, P2-010x1 |
| v6_hr_final | 12/20 | same/Amazon, same/AWS, extra/CapitalOne-AI, extra/Dataminr-Infra, extra/HealthEquity-DotNet, extra/Zoox-LLM, gen2/ChildrensHospital-Azure, gen2/Cisco-NetworkingSenior | P3C-010x7, P3B-001x2, P2-001x2, P3B-010x2, P3A-002x1 |
| v7_gen2_jd_richer | 17/20 | same/AWS, gen2/Fireblocks-SRE, gen2/Geico-SWE2 | P3B-010x6, P3C-010x6, P3B-001x6, P3B-012x4, P2-001x2, P3A-002x1 |
| v8_tooling_bridge | 16/20 | same/Amazon, same/AWS, extra/Dataminr-Infra, gen2/AppliedIntuition-CloudInfra | P3B-001x5, P3B-010x4, P3B-012x4, P3C-010x3, P2-001x2, P3A-002x2 |
| v9_gate_restore | 19/20 | same/AWS | P3B-010x6, P3B-012x4, P3C-010x4, P3B-001x3, P2-001x2, P3B-011x1 |
| v10_equiv_evidence | 20/20 | none | P3B-010x7, P3B-001x4, P3B-012x4, P3C-010x3, P2-001x2, P3A-001x1 |

## 外部确认集（10 case, revised labels）

| 版本 | 命中 | 错判 | 高频高/致命规则 |
| --- | ---: | --- | --- |
| v3_hr_stable | 5/10 | conf/FlexTrade-SoftwareDeveloper, conf/Whoop-SensorIntelligence, conf/8451-ResearchAI, conf/Photon-AIEngineer, conf/Clarivate-NLP | P3C-010x3, P2-010x1, P3B-001x1, P2-001x1 |
| v9_gate_restore | 8/10 | conf/Phantom-SDET, conf/VeteransUnited-AssociateSE | P3B-001x6, P2-001x3, P3B-002x1, P3C-010x1, P3B-010x1, P3A-002x1 |
| v10_equiv_evidence | 9/10 | conf/Phantom-SDET | P3C-010x5, P3B-001x5, P3B-002x1, P3B-010x1 |
