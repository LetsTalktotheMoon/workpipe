# gen2_v5_hr_gate 对照 HR 标签

| Case | 目标 | 实际 | 分数 | 是否命中 | 主要高/致命项 | 标签理由 |
| --- | --- | --- | --- | --- | --- | --- |
| gen2/Discord-DBInfra | fail | fail | 93.9 | 是 | P3B-001:high:Skills / 全文 | 数据库基础设施/高可用存储/底层服务 owner 叙事不足，属于 specialized infra domain gap；失败原因不应简化成缺 Rust 单 token。 |
| gen2/AppliedIntuition-CloudInfra | pass | pass | 100.0 | 是 | none | 云基础设施、容器、部署和平台运营信号充分，能通过真实 HR 首筛。 |
| gen2/Fireblocks-SRE | pass | pass | 95.6 | 是 | none | 安全、可观测性、容器与平台运维叙事足够贴近 SRE，虽非完美但应进入下一轮。 |
| gen2/ChildrensHospital-Azure | fail | pass | 93.0 | 否 | P2-010:high:Professional Summary 第三句<br>P3C-010:high:DiDi · IBG · Food Experience（尤其 bullets 1, 4, 5；Project: Merchant Ops Control Tower bullets 1, 4） | 岗位是 Azure Software Engineer，但简历只有泛后端与少量 Azure 相邻信号，缺少可自证的 Azure 主体交付经历。 |
| gen2/CapitalOne-Manager2 | fail | fail | 90.9 | 是 | P3B-010:high:Target role vs. overall experience scope | Manager title 需要明确的人管理/团队管理/正式 owner scope，当前简历主要是 IC 交付。 |
| gen2/Fanduel-AnalyticsManager | fail | fail | 89.0 | 是 | P3B-010:high:Professional Summary + Experience sections | JD 明确要求管理分析师团队，当前简历没有直接 people-management 证据，真实 HR 会直接追问并大概率卡掉。 |
| gen2/Geico-SWE2 | pass | pass | 96.5 | 是 | none | 语言、分布式系统、API、code review 和云相关信号整体够用，首筛可过。 |
| gen2/Doordash-Backend | pass | pass | 97.0 | 是 | none | 后端、REST、微服务、SQL/NoSQL 与服务发布叙事贴近岗位，真实 HR 应通过。 |
| gen2/Cisco-NetworkingSenior | fail | pass | 95.8 | 否 | P3C-010:high:Summary and TikTok Experience | Networking Technologies 岗位需要明确网络系统/路由/协议/系统级深度与年限支撑，当前简历只有相邻后端与验证信号，差距仍偏大。 |
| gen2/Genentech-MLInfra | pass | pass | 96.5 | 是 | none | ML infra、AWS、Python/Go/C++、评估与部署叙事形成可接受闭环，应通过首筛。 |

## 汇总

- 命中: `8/10`
- 错判: `2`
- 错判列表: `gen2/ChildrensHospital-Azure, gen2/Cisco-NetworkingSenior`
