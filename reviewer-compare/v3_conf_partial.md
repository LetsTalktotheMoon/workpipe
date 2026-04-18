# v3_conf_partial 对照 HR 标签

| Case | 目标 | 实际 | 分数 | 是否命中 | 主要高/致命项 | 标签理由 |
| --- | --- | --- | --- | --- | --- | --- |
| conf/FlexTrade-SoftwareDeveloper | pass | fail | 90.6 | 否 | P3B-001:high:Skills - Cloud / Summary | Golang、AWS、Docker、Linux、Shell 与当前后端/基础设施经历高度贴合，真实 HR 首筛应通过。 |
| conf/Whoop-SensorIntelligence | fail | pass | 94.0 | 否 | P3C-010:high:Experience > Software Engineer Intern | TikTok · Security > bullet 3 | 岗位核心是 signal processing、time-series biosignals、C 与 wearable domain，当前简历缺少对应信号处理和领域证据链，真实 HR 应直接保留。 |

## 汇总

- 命中: `0/2`
- 错判: `2`
- 错判列表: `conf/FlexTrade-SoftwareDeveloper, conf/Whoop-SensorIntelligence`
