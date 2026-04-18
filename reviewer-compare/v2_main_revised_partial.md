# v2_main_revised_partial 对照 HR 标签

| Case | 目标 | 实际 | 分数 | 是否命中 | 主要高/致命项 | 标签理由 |
| --- | --- | --- | --- | --- | --- | --- |
| same/Google | pass | pass | 92.8 | 是 | P3A-002:high:TikTok Experience, project bullet 1 | 后端/分布式系统与搜索/平台能力桥接充分，虽有表达可优化点，但真实 HR 首筛应通过。 |
| same/Amazon | fail | pass | 97.8 | 否 | none | 原始 JD 明写 `3+ years of non-internship professional software development experience`，而简历显式写 `2.5+ years of non-internship experience`，属于真实 HR 会追问并可能直接卡掉的边界硬门槛。 |
| same/AWS | fail | fail | 94.4 | 是 | P3E-010:critical:TikTok project: Security Investigation Retrieval Assistant, bullet 2 | raw JD 同样要求 `3+ years of non-internship professional software development experience`，而当前简历可见非实习全职时间约 30 个月，难以稳过真实 HR 的 SDE II 首筛。 |
| same/Microsoft | fail | pass | 90.4 | 否 | P3B-001:high:Skills; Professional Summary; TikTok Experience<br>P3C-010:high:Professional Summary; TikTok Experience | 目标岗位所需技术栈和经历主轴存在结构性缺口，真实 HR 会在首轮产生明确保留。 |
| extra/CapitalOne-AI | fail | pass | 95.2 | 否 | none | AI/ML 方向与当前主经历的匹配度不足，缺少足够直接的模型/平台交付证据。 |
| extra/Dataminr-Infra | fail | pass | 97.4 | 否 | none | 原始 JD 明写 `4+ years of experience building back end services and applications`，当前简历表面时间线仅约 3 年且含 internship，不足以稳过真实 HR 首筛。 |
| extra/HealthEquity-DotNet | fail | pass | 88.8 | 否 | P3B-001:high:Skills section | .NET/C# 主栈缺口明显，属于真实招聘中的岗位定义级错配。 |
| extra/Zoox-LLM | fail | pass | 96.8 | 否 | P3C-010:high:TikTok · Security Experience 全段 | 原始 JD 的核心门槛是 3D vision / 3D reconstruction / radiance field / style transfer / human-centric 3D 方向，当前简历只有通用 ML/backend 证据，没有对应 3D 证据链。 |
| extra/Synechron-Backend | pass | pass | 95.0 | 是 | none | 泛后端岗位对当前简历的接受度高，技术栈与经历覆盖足够。 |
| extra/Ramp-Platform | pass | fail | 95.8 | 否 | P3E-010:critical:TikTok · Security | Software Engineer Intern | Jun 2025 – Dec 2025 | Bullet 2 | 平台与后端运营能力叙事较稳，真实 HR 没有明显一眼淘汰点。 |

## 汇总

- 命中: `3/10`
- 错判: `7`
- 错判列表: `same/Amazon, same/Microsoft, extra/CapitalOne-AI, extra/Dataminr-Infra, extra/HealthEquity-DotNet, extra/Zoox-LLM, extra/Ramp-Platform`
