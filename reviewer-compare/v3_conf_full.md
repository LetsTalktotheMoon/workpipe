# v3_conf_full 对照 HR 标签

| Case | 目标 | 实际 | 分数 | 是否命中 | 主要高/致命项 | 标签理由 |
| --- | --- | --- | --- | --- | --- | --- |
| conf/FlexTrade-SoftwareDeveloper | pass | fail | 90.6 | 否 | P3B-001:high:Skills - Cloud / Summary | Golang、AWS、Docker、Linux、Shell 与当前后端/基础设施经历高度贴合，真实 HR 首筛应通过。 |
| conf/Whoop-SensorIntelligence | fail | pass | 94.0 | 否 | P3C-010:high:Experience > Software Engineer Intern | TikTok · Security > bullet 3 | 岗位核心是 signal processing、time-series biosignals、C 与 wearable domain，当前简历缺少对应信号处理和领域证据链，真实 HR 应直接保留。 |
| conf/Hopper-CustomerPlatform | pass | pass | 97.5 | 是 | none | 大规模分布式系统、前后端协同与客户平台方向整体可桥接，虽 senior 表达还可加强，但首筛可过。 |
| conf/Nuro-OffboardInfra | pass | pass | 94.6 | 是 | P2-010:high:Professional Summary, sentence 3 | Python/C++/Go、distributed systems 与 data/infrastructure 叙事形成较强闭环，真实 HR 应通过。 |
| conf/AMH-EnterpriseDataAnalyst | pass | pass | 98.0 | 是 | none | Business Intelligence、financial reporting、data warehousing、SQL 与当前数据分析主轴高度一致，首筛应通过。 |
| conf/Phantom-SDET | pass | pass | 95.5 | 是 | none | 测试/验证自动化、Go/Python/TypeScript/JavaScript 与当前质量导向工程叙事较匹配，真实 HR 应允许进入下一轮。 |
| conf/VeteransUnited-AssociateSE | pass | pass | 95.8 | 是 | none | .NET/C#/ASP.NET、CI/CD、Web APIs、microservices 与岗位要求直接对齐，属于明显可过的目标岗位。 |
| conf/8451-ResearchAI | fail | pass | 95.8 | 否 | P3C-010:high:TikTok Experience, bullets 2 and 4 | 岗位强调 agentic systems、research agents、multi-step reasoning、RLHF，当前简历只有通用 LLM/ML 工程与评估证据，没有研究型 agent/RLHF 证据链。 |
| conf/Photon-AIEngineer | pass | pass | 93.3 | 是 | P2-001:high:Professional Summary 第一句<br>P3C-010:high:TikTok Experience / DiDi Experience | Generative AI、Python、LangChain/LlamaIndex/Vector Search 与当前 AI 工程叙事可形成合理桥接，真实 HR 首筛应通过。 |
| conf/Clarivate-NLP | pass | pass | 99.7 | 是 | none | NLP、Python、LangChain、LangGraph 与当前 NLP/LLM 工作流叙事高度相关，尽管 senior title 偏 ambitious，但首筛仍可过。 |

## 汇总

- 命中: `7/10`
- 错判: `3`
- 错判列表: `conf/FlexTrade-SoftwareDeveloper, conf/Whoop-SensorIntelligence, conf/8451-ResearchAI`
