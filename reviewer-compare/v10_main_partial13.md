# v10_main_partial13 对照 HR 标签

| Case | 目标 | 实际 | 分数 | 是否命中 | 主要高/致命项 | 标签理由 |
| --- | --- | --- | --- | --- | --- | --- |
| same/Google | pass | pass | 94.4 | 是 | P3A-002:high:TikTok Experience > Project: Security Knowledge Retrieval Assistant bullet 1 / Skills > Cloud | 后端/分布式系统与搜索/平台能力桥接充分，虽有表达可优化点，但真实 HR 首筛应通过。 |
| same/Amazon | fail | fail | 89.2 | 是 | P3B-010:high:Professional Summary > bullet 1; full experience timeline<br>P3C-010:high:TikTok Experience | 原始 JD 明写 `3+ years of non-internship professional software development experience`，而简历显式写 `2.5+ years of non-internship experience`，属于真实 HR 会追问并可能直接卡掉的边界硬门槛。 |
| same/AWS | pass | fail | 90.9 | 否 | P3B-010:high:Overall experience timeline + Education | 云与后端平台方向匹配度高，虽需更强 scope 呈现，但不构成首轮淘汰。 |
| same/Microsoft | fail | fail | 90.5 | 是 | P3B-012:high:Overall resume vs. Microsoft Azure Storage role | 目标岗位所需技术栈和经历主轴存在结构性缺口，真实 HR 会在首轮产生明确保留。 |
| extra/Dataminr-Infra | fail | fail | 91.3 | 是 | P3B-010:high:Professional Summary / total experience | 原始 JD 明写 `4+ years of experience building back end services and applications`，当前简历表面时间线仅约 3 年且含 internship，不足以稳过真实 HR 首筛。 |
| extra/Zoox-LLM | fail | fail | 92.8 | 是 | P3B-001:high:Summary / Skills / Experience | 原始 JD 的核心门槛是 3D vision / 3D reconstruction / radiance field / style transfer / human-centric 3D 方向，当前简历只有通用 ML/backend 证据，没有对应 3D 证据链。 |
| gen2/Discord-DBInfra | fail | fail | 88.8 | 是 | P3B-001:high:Skills / Summary / Experience<br>P3B-012:high:Summary + TikTok/DiDi Experience | 数据库基础设施/高可用存储/底层服务 owner 叙事不足，属于 specialized infra domain gap；失败原因不应简化成缺 Rust 单 token。 |
| gen2/AppliedIntuition-CloudInfra | pass | pass | 95.3 | 是 | P3C-010:high:TikTok Experience; DiDi Experience | 云基础设施、容器、部署和平台运营信号充分，能通过真实 HR 首筛。 |
| gen2/Fireblocks-SRE | pass | pass | 94.7 | 是 | none | 安全、可观测性、容器与平台运维叙事足够贴近 SRE，虽非完美但应进入下一轮。 |
| gen2/ChildrensHospital-Azure | fail | fail | 85.3 | 是 | P3B-001:high:Skills + Experience overall<br>P3B-012:high:Professional Summary + Experience | 岗位是 Azure Software Engineer，但简历只有泛后端与少量 Azure 相邻信号，缺少可自证的 Azure 主体交付经历。 |
| gen2/CapitalOne-Manager2 | fail | fail | 91.4 | 是 | P3B-010:high:Overall profile vs. JD minimum qualifications | Manager title 需要明确的人管理/团队管理/正式 owner scope，当前简历主要是 IC 交付。 |
| gen2/Fanduel-AnalyticsManager | fail | fail | 86.3 | 是 | P3B-001:high:Skills / Experience<br>P3B-010:high:Overall profile (Summary + Experience chronology) | JD 明确要求管理分析师团队，当前简历没有直接 people-management 证据，真实 HR 会直接追问并大概率卡掉。 |
| gen2/Geico-SWE2 | pass | pass | 95.1 | 是 | none | 语言、分布式系统、API、code review 和云相关信号整体够用，首筛可过。 |

## 汇总

- 命中: `12/13`
- 错判: `1`
- 错判列表: `same/AWS`
