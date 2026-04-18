# v3_conf_partial4 对照 HR 标签

| Case | 目标 | 实际 | 分数 | 是否命中 | 主要高/致命项 | 标签理由 |
| --- | --- | --- | --- | --- | --- | --- |
| conf/FlexTrade-SoftwareDeveloper | pass | fail | 90.6 | 否 | P3B-001:high:Skills - Cloud / Summary | Golang、AWS、Docker、Linux、Shell 与当前后端/基础设施经历高度贴合，真实 HR 首筛应通过。 |
| conf/Whoop-SensorIntelligence | fail | pass | 94.0 | 否 | P3C-010:high:Experience > Software Engineer Intern | TikTok · Security > bullet 3 | 岗位核心是 signal processing、time-series biosignals、C 与 wearable domain，当前简历缺少对应信号处理和领域证据链，真实 HR 应直接保留。 |
| conf/Hopper-CustomerPlatform | pass | pass | 97.5 | 是 | none | 大规模分布式系统、前后端协同与客户平台方向整体可桥接，虽 senior 表达还可加强，但首筛可过。 |
| conf/Nuro-OffboardInfra | pass | pass | 94.6 | 是 | P2-010:high:Professional Summary, sentence 3 | Python/C++/Go、distributed systems 与 data/infrastructure 叙事形成较强闭环，真实 HR 应通过。 |

## 汇总

- 命中: `2/4`
- 错判: `2`
- 错判列表: `conf/FlexTrade-SoftwareDeveloper, conf/Whoop-SensorIntelligence`
