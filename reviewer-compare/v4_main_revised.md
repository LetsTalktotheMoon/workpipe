# v4_main_revised 对照 HR 标签

| Case | 目标 | 实际 | 分数 | 是否命中 | 主要高/致命项 | 标签理由 |
| --- | --- | --- | --- | --- | --- | --- |
| same/Google | pass | fail | 86.2 | 否 | P3A-002:high:TikTok Project: Security Knowledge Retrieval Assistant, bullet 1<br>P3A-003:critical:Professional Summary, sentence 2 | 后端/分布式系统与搜索/平台能力桥接充分，虽有表达可优化点，但真实 HR 首筛应通过。 |
| same/Amazon | fail | pass | 95.3 | 否 | P3C-010:high:Professional Summary / Skills / Experience | 原始 JD 明写 `3+ years of non-internship professional software development experience`，而简历显式写 `2.5+ years of non-internship experience`，属于真实 HR 会追问并可能直接卡掉的边界硬门槛。 |
| same/AWS | fail | pass | 97.7 | 否 | none | raw JD 同样要求 `3+ years of non-internship professional software development experience`，而当前简历可见非实习全职时间约 30 个月，难以稳过真实 HR 的 SDE II 首筛。 |
| same/Microsoft | fail | pass | 95.8 | 否 | P3C-010:high:Professional Summary + TikTok · Security experience | 目标岗位所需技术栈和经历主轴存在结构性缺口，真实 HR 会在首轮产生明确保留。 |
| extra/CapitalOne-AI | fail | fail | 88.6 | 是 | P3B-010:high:Summary / 全文经历 | AI/ML 方向与当前主经历的匹配度不足，缺少足够直接的模型/平台交付证据。 |
| extra/Dataminr-Infra | fail | pass | 98.5 | 否 | none | 原始 JD 明写 `4+ years of experience building back end services and applications`，当前简历表面时间线仅约 3 年且含 internship，不足以稳过真实 HR 首筛。 |
| extra/HealthEquity-DotNet | fail | pass | 88.6 | 否 | P2-001:high:Professional Summary, sentence 1<br>P3B-002:high:Skills + DiDi Experience, `MongoDB` / `Merchant Incident Workbench` project | .NET/C# 主栈缺口明显，属于真实招聘中的岗位定义级错配。 |
| extra/Zoox-LLM | fail | pass | 96.4 | 否 | P3C-010:high:TikTok · Security intern bullets | 原始 JD 的核心门槛是 3D vision / 3D reconstruction / radiance field / style transfer / human-centric 3D 方向，当前简历只有通用 ML/backend 证据，没有对应 3D 证据链。 |
| extra/Synechron-Backend | pass | pass | 100.0 | 是 | none | 泛后端岗位对当前简历的接受度高，技术栈与经历覆盖足够。 |
| extra/Ramp-Platform | pass | pass | 100.0 | 是 | none | 平台与后端运营能力叙事较稳，真实 HR 没有明显一眼淘汰点。 |

## 汇总

- 命中: `3/10`
- 错判: `7`
- 错判列表: `same/Google, same/Amazon, same/AWS, same/Microsoft, extra/Dataminr-Infra, extra/HealthEquity-DotNet, extra/Zoox-LLM`
