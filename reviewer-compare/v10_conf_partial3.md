# v10_conf_partial3 对照 HR 标签

| Case | 目标 | 实际 | 分数 | 是否命中 | 主要高/致命项 | 标签理由 |
| --- | --- | --- | --- | --- | --- | --- |
| conf/FlexTrade-SoftwareDeveloper | pass | pass | 92.2 | 是 | none | Golang、AWS、Docker、Linux、Shell 与当前后端/基础设施经历高度贴合，真实 HR 首筛应通过。 |
| conf/Whoop-SensorIntelligence | fail | fail | 90.7 | 是 | P3B-001:high:Skills / Experience<br>P3C-010:high:TikTok Experience, bullet 3 | 岗位核心是 signal processing、time-series biosignals、C 与 wearable domain，当前简历缺少对应信号处理和领域证据链，真实 HR 应直接保留。 |
| conf/Hopper-CustomerPlatform | pass | pass | 95.5 | 是 | none | 大规模分布式系统、前后端协同与客户平台方向整体可桥接，虽 senior 表达还可加强，但首筛可过。 |
| conf/Nuro-OffboardInfra | pass | pass | 98.1 | 是 | none | Python/C++/Go、distributed systems 与 data/infrastructure 叙事形成较强闭环，真实 HR 应通过。 |
| conf/AMH-EnterpriseDataAnalyst | pass | pass | 91.0 | 是 | P3B-002:high:Skills; Experience | Business Intelligence、financial reporting、data warehousing、SQL 与当前数据分析主轴高度一致，首筛应通过。 |

## 汇总

- 命中: `5/5`
- 错判: `0`
- 错判列表: `none`
