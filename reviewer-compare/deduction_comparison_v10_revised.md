# 扣分项对照表

## 主基准（20 case, revised labels）

| 版本 | 常见高/致命规则 | 代表性误判 |
| --- | --- | --- |
| old_pipe | none | same/Google, same/Amazon, same/AWS, extra/HealthEquity-DotNet, extra/Zoox-LLM, extra/Synechron-Backend, gen2/Fanduel-AnalyticsManager, gen2/Geico-SWE2 |
| v3_hr_stable | P3C-010x5, P3B-001x3, P3B-010x2, P2-001x1, P3A-002x1 | same/Amazon, same/AWS, extra/Dataminr-Infra, extra/Zoox-LLM, gen2/ChildrensHospital-Azure, gen2/Fanduel-AnalyticsManager, gen2/Cisco-NetworkingSenior |
| v5_hr_gate | P3C-010x5, P3B-010x3, P3A-002x1, P3B-001x1, P2-010x1 | same/Amazon, same/AWS, same/Microsoft, extra/Dataminr-Infra, extra/HealthEquity-DotNet, extra/Zoox-LLM, gen2/ChildrensHospital-Azure, gen2/Cisco-NetworkingSenior |
| v6_hr_final | P3C-010x7, P3B-001x2, P2-001x2, P3B-010x2, P3A-002x1 | same/Amazon, same/AWS, extra/CapitalOne-AI, extra/Dataminr-Infra, extra/HealthEquity-DotNet, extra/Zoox-LLM, gen2/ChildrensHospital-Azure, gen2/Cisco-NetworkingSenior |
| v7_gen2_jd_richer | P3B-010x6, P3C-010x6, P3B-001x6, P3B-012x4, P2-001x2, P3A-002x1 | same/AWS, gen2/Fireblocks-SRE, gen2/Geico-SWE2 |
| v8_tooling_bridge | P3B-001x5, P3B-010x4, P3B-012x4, P3C-010x3, P2-001x2, P3A-002x2 | same/Amazon, same/AWS, extra/Dataminr-Infra, gen2/AppliedIntuition-CloudInfra |
| v9_gate_restore | P3B-010x6, P3B-012x4, P3C-010x4, P3B-001x3, P2-001x2, P3B-011x1 | same/AWS |
| v10_equiv_evidence | P3B-010x7, P3B-001x4, P3B-012x4, P3C-010x3, P2-001x2, P3A-001x1 | none |

## 外部确认集（10 case, revised labels）

| 版本 | 常见高/致命规则 | 代表性误判 |
| --- | --- | --- |
| v3_hr_stable | P3C-010x3, P2-010x1, P3B-001x1, P2-001x1 | conf/FlexTrade-SoftwareDeveloper, conf/Whoop-SensorIntelligence, conf/8451-ResearchAI, conf/Photon-AIEngineer, conf/Clarivate-NLP |
| v9_gate_restore | P3B-001x6, P2-001x3, P3B-002x1, P3C-010x1, P3B-010x1, P3A-002x1 | conf/Phantom-SDET, conf/VeteransUnited-AssociateSE |
| v10_equiv_evidence | P3C-010x5, P3B-001x5, P3B-002x1, P3B-010x1 | conf/Phantom-SDET |
