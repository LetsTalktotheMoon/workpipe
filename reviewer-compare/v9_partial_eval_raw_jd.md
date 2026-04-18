# v9_partial_raw_jd_19 对照 HR 标签

| Case | 目标 | 实际 | 分数 | 是否命中 | 主要高/致命项 | 标签理由 |
| --- | --- | --- | --- | --- | --- | --- |
| same/Google | pass | pass | 98.0 | 是 | none | 后端/分布式系统与搜索/平台能力桥接充分，虽有表达可优化点，但真实 HR 首筛应通过。 |
| same/Amazon | fail | fail | 91.2 | 是 | P3B-010:high:Professional Summary + Experience timeline<br>P3C-010:high:TikTok Experience | 原始 JD 明写 `3+ years of non-internship professional software development experience`，而简历显式写 `2.5+ years of non-internship experience`，属于真实 HR 会追问并可能直接卡掉的边界硬门槛。 |
| same/AWS | pass | pass | 97.5 | 是 | none | 云与后端平台方向匹配度高，虽需更强 scope 呈现，但不构成首轮淘汰。 |
| same/Microsoft | fail | fail | 87.7 | 是 | P2-001:high:Professional Summary, sentence 1<br>P3B-012:high:整体定位 / Azure Storage 目标匹配<br>P3C-010:high:TikTok · Security Experience | 目标岗位所需技术栈和经历主轴存在结构性缺口，真实 HR 会在首轮产生明确保留。 |
| extra/CapitalOne-AI | fail | fail | 85.3 | 是 | P3B-001:high:Skills / Experience<br>P3B-010:high:Education + Experience timeline / Summary | AI/ML 方向与当前主经历的匹配度不足，缺少足够直接的模型/平台交付证据。 |
| extra/Dataminr-Infra | fail | fail | 92.9 | 是 | P3B-010:high:Professional Summary + overall experience timeline | 原始 JD 明写 `4+ years of experience building back end services and applications`，当前简历表面时间线仅约 3 年且含 internship，不足以稳过真实 HR 首筛。 |
| extra/HealthEquity-DotNet | fail | fail | 84.0 | 是 | P2-001:high:Professional Summary, sentence 1<br>P3B-010:high:Professional Summary + overall Experience timeline<br>P3B-011:high:Skills section + DiDi experience | .NET/C# 主栈缺口明显，属于真实招聘中的岗位定义级错配。 |
| extra/Zoox-LLM | fail | fail | 93.8 | 是 | P3B-001:high:Professional Summary / Experience | 原始 JD 的核心门槛是 3D vision / 3D reconstruction / radiance field / style transfer / human-centric 3D 方向，当前简历只有通用 ML/backend 证据，没有对应 3D 证据链。 |
| extra/Synechron-Backend | pass | pass | 98.5 | 是 | none | 泛后端岗位对当前简历的接受度高，技术栈与经历覆盖足够。 |
| extra/Ramp-Platform | pass | pass | 99.2 | 是 | none | 平台与后端运营能力叙事较稳，真实 HR 没有明显一眼淘汰点。 |
| gen2/Discord-DBInfra | fail | fail | 93.3 | 是 | P3B-012:high:Overall resume / Discord Database Infrastructure target | 数据库基础设施/高可用存储/底层服务 owner 叙事不足，属于 specialized infra domain gap；失败原因不应简化成缺 Rust 单 token。 |
| gen2/AppliedIntuition-CloudInfra | pass | pass | 96.2 | 是 | none | 云基础设施、容器、部署和平台运营信号充分，能通过真实 HR 首筛。 |
| gen2/Fireblocks-SRE | pass | pass | 96.6 | 是 | none | 安全、可观测性、容器与平台运维叙事足够贴近 SRE，虽非完美但应进入下一轮。 |
| gen2/ChildrensHospital-Azure | fail | fail | 88.6 | 是 | P2-010:high:Professional Summary, sentence 3<br>P3B-012:high:Overall resume vs. 'Azure Software Engineer Professional' JD | 岗位是 Azure Software Engineer，但简历只有泛后端与少量 Azure 相邻信号，缺少可自证的 Azure 主体交付经历。 |
| gen2/CapitalOne-Manager2 | fail | fail | 90.9 | 是 | P3B-010:high:Overall experience timeline / seniority signal | Manager title 需要明确的人管理/团队管理/正式 owner scope，当前简历主要是 IC 交付。 |
| gen2/Fanduel-AnalyticsManager | fail | fail | 85.3 | 是 | P3B-001:high:Skills + Experience 全文<br>P3B-010:high:DiDi · Senior Data Analyst 段 | JD 明确要求管理分析师团队，当前简历没有直接 people-management 证据，真实 HR 会直接追问并大概率卡掉。 |
| gen2/Geico-SWE2 | pass | pass | 93.9 | 是 | P3C-010:high:TikTok · Security Experience | 语言、分布式系统、API、code review 和云相关信号整体够用，首筛可过。 |
| gen2/Doordash-Backend | pass | pass | 98.0 | 是 | none | 后端、REST、微服务、SQL/NoSQL 与服务发布叙事贴近岗位，真实 HR 应通过。 |
| gen2/Cisco-NetworkingSenior | fail | fail | 90.7 | 是 | P3B-012:high:Cisco fit / TikTok Intern experience<br>P3C-010:high:TikTok Intern experience | Networking Technologies 岗位需要明确网络系统/路由/协议/系统级深度与年限支撑，当前简历只有相邻后端与验证信号，差距仍偏大。 |
| gen2/Genentech-MLInfra | pass | pass | 96.5 | 是 | none | ML infra、AWS、Python/Go/C++、评估与部署叙事形成可接受闭环，应通过首筛。 |

## 汇总

- 命中: `20/20`
- 错判: `0`
- 错判列表: `none`
