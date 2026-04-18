# v8_full_raw_jd 对照 HR 标签

| Case | 目标 | 实际 | 分数 | 是否命中 | 主要高/致命项 | 标签理由 |
| --- | --- | --- | --- | --- | --- | --- |
| same/Google | pass | pass | 94.4 | 是 | P3A-002:high:TikTok Experience > Project: Security Knowledge Retrieval Assistant, bullet 1 | 后端/分布式系统与搜索/平台能力桥接充分，虽有表达可优化点，但真实 HR 首筛应通过。 |
| same/Amazon | fail | pass | 96.9 | 否 | none | 原始 JD 明写 `3+ years of non-internship professional software development experience`，而简历显式写 `2.5+ years of non-internship experience`，属于真实 HR 会追问并可能直接卡掉的边界硬门槛。 |
| same/AWS | pass | pass | 96.0 | 是 | P2-001:high:Professional Summary, 第一句 | 云与后端平台方向匹配度高，虽需更强 scope 呈现，但不构成首轮淘汰。 |
| same/Microsoft | fail | fail | 84.7 | 是 | P3B-001:high:Minimum qualifications / Experience overall<br>P3B-012:high:Summary + Experience overall, Azure Storage fit | 目标岗位所需技术栈和经历主轴存在结构性缺口，真实 HR 会在首轮产生明确保留。 |
| extra/CapitalOne-AI | fail | fail | 92.4 | 是 | P3B-010:high:Professional Summary / Experience / Education | AI/ML 方向与当前主经历的匹配度不足，缺少足够直接的模型/平台交付证据。 |
| extra/Dataminr-Infra | fail | pass | 95.8 | 否 | P3C-010:high:TikTok · Security, bullets 1-4 | 原始 JD 明写 `4+ years of experience building back end services and applications`，当前简历表面时间线仅约 3 年且含 internship，不足以稳过真实 HR 首筛。 |
| extra/HealthEquity-DotNet | fail | fail | 86.8 | 是 | P3B-010:high:Experience timeline / Professional Summary<br>P3B-011:high:Summary / Skills / TikTok & DiDi bullets | .NET/C# 主栈缺口明显，属于真实招聘中的岗位定义级错配。 |
| extra/Zoox-LLM | fail | fail | 91.4 | 是 | P3B-001:high:Professional Summary / Experience | 原始 JD 的核心门槛是 3D vision / 3D reconstruction / radiance field / style transfer / human-centric 3D 方向，当前简历只有通用 ML/backend 证据，没有对应 3D 证据链。 |
| extra/Synechron-Backend | pass | pass | 100.0 | 是 | none | 泛后端岗位对当前简历的接受度高，技术栈与经历覆盖足够。 |
| extra/Ramp-Platform | pass | pass | 99.5 | 是 | none | 平台与后端运营能力叙事较稳，真实 HR 没有明显一眼淘汰点。 |
| gen2/Discord-DBInfra | fail | fail | 94.4 | 是 | P3B-012:high:## Professional Summary / TikTok Experience | 数据库基础设施/高可用存储/底层服务 owner 叙事不足，属于 specialized infra domain gap；失败原因不应简化成缺 Rust 单 token。 |
| gen2/AppliedIntuition-CloudInfra | pass | fail | 90.9 | 否 | P3B-001:high:Skills > Cloud; TikTok / DiDi experience | 云基础设施、容器、部署和平台运营信号充分，能通过真实 HR 首筛。 |
| gen2/Fireblocks-SRE | pass | pass | 92.8 | 是 | none | 安全、可观测性、容器与平台运维叙事足够贴近 SRE，虽非完美但应进入下一轮。 |
| gen2/ChildrensHospital-Azure | fail | fail | 89.4 | 是 | P3B-012:high:JD core skills vs Summary/Skills/Experience<br>P3C-010:high:DiDi Experience | 岗位是 Azure Software Engineer，但简历只有泛后端与少量 Azure 相邻信号，缺少可自证的 Azure 主体交付经历。 |
| gen2/CapitalOne-Manager2 | fail | fail | 85.8 | 是 | P3B-010:high:Overall experience level vs JD Manager scope<br>P3B-001:high:Skills / Experience | Manager title 需要明确的人管理/团队管理/正式 owner scope，当前简历主要是 IC 交付。 |
| gen2/Fanduel-AnalyticsManager | fail | fail | 85.8 | 是 | P3B-001:high:Skills / Experience<br>P3B-010:high:DiDi Experience | JD 明确要求管理分析师团队，当前简历没有直接 people-management 证据，真实 HR 会直接追问并大概率卡掉。 |
| gen2/Geico-SWE2 | pass | pass | 96.6 | 是 | none | 语言、分布式系统、API、code review 和云相关信号整体够用，首筛可过。 |
| gen2/Doordash-Backend | pass | pass | 97.0 | 是 | none | 后端、REST、微服务、SQL/NoSQL 与服务发布叙事贴近岗位，真实 HR 应通过。 |
| gen2/Cisco-NetworkingSenior | fail | fail | 85.8 | 是 | P2-001:high:Professional Summary, sentence 1<br>P3A-002:high:TikTok Experience bullet 4<br>P3B-012:high:整份简历的 Cisco 目标匹配 | Networking Technologies 岗位需要明确网络系统/路由/协议/系统级深度与年限支撑，当前简历只有相邻后端与验证信号，差距仍偏大。 |
| gen2/Genentech-MLInfra | pass | pass | 96.8 | 是 | P3C-010:high:Software Engineer Intern | TikTok · Security | ML infra、AWS、Python/Go/C++、评估与部署叙事形成可接受闭环，应通过首筛。 |

## 汇总

- 命中: `17/20`
- 错判: `3`
- 错判列表: `same/Amazon, extra/Dataminr-Infra, gen2/AppliedIntuition-CloudInfra`
