# v10_main_partial 对照 HR 标签

| Case | 目标 | 实际 | 分数 | 是否命中 | 主要高/致命项 | 标签理由 |
| --- | --- | --- | --- | --- | --- | --- |
| same/Microsoft | fail | fail | 90.5 | 是 | P3B-012:high:Overall resume vs. Microsoft Azure Storage role | 目标岗位所需技术栈和经历主轴存在结构性缺口，真实 HR 会在首轮产生明确保留。 |
| gen2/Discord-DBInfra | fail | fail | 88.8 | 是 | P3B-001:high:Skills / Summary / Experience<br>P3B-012:high:Summary + TikTok/DiDi Experience | 数据库基础设施/高可用存储/底层服务 owner 叙事不足，属于 specialized infra domain gap；失败原因不应简化成缺 Rust 单 token。 |
| gen2/AppliedIntuition-CloudInfra | pass | pass | 95.3 | 是 | P3C-010:high:TikTok Experience; DiDi Experience | 云基础设施、容器、部署和平台运营信号充分，能通过真实 HR 首筛。 |

## 汇总

- 命中: `3/3`
- 错判: `0`
- 错判列表: `none`
