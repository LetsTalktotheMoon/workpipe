# v9_conf_full 对照 HR 标签

| Case | 目标 | 实际 | 分数 | 是否命中 | 主要高/致命项 | 标签理由 |
| --- | --- | --- | --- | --- | --- | --- |
| conf/FlexTrade-SoftwareDeveloper | pass | pass | 94.1 | 是 | none | Golang、AWS、Docker、Linux、Shell 与当前后端/基础设施经历高度贴合，真实 HR 首筛应通过。 |
| conf/Whoop-SensorIntelligence | fail | fail | 90.4 | 是 | P2-001:high:Professional Summary bullet 1<br>P3B-001:high:Professional Summary / 全部 Experience | 岗位核心是 signal processing、time-series biosignals、C 与 wearable domain，当前简历缺少对应信号处理和领域证据链，真实 HR 应直接保留。 |
| conf/Hopper-CustomerPlatform | pass | pass | 97.0 | 是 | none | 大规模分布式系统、前后端协同与客户平台方向整体可桥接，虽 senior 表达还可加强，但首筛可过。 |
| conf/Nuro-OffboardInfra | pass | pass | 97.5 | 是 | none | Python/C++/Go、distributed systems 与 data/infrastructure 叙事形成较强闭环，真实 HR 应通过。 |
| conf/AMH-EnterpriseDataAnalyst | pass | pass | 93.5 | 是 | P3C-010:high:TikTok Experience, overall section | Business Intelligence、financial reporting、data warehousing、SQL 与当前数据分析主轴高度一致，首筛应通过。 |
| conf/Phantom-SDET | pass | fail | 91.6 | 否 | P3B-001:high:JD minimum qualifications vs. Professional Summary and TikTok Experience / project bullets | 测试/验证自动化、Go/Python/TypeScript/JavaScript 与当前质量导向工程叙事较匹配，真实 HR 应允许进入下一轮。 |
| conf/VeteransUnited-AssociateSE | pass | fail | 82.3 | 否 | P2-001:high:Summary sentence 1<br>P3B-001:high:Skills / recent backend experience<br>P3B-002:high:Summary / TikTok Experience / DiDi Experience | .NET/C#/ASP.NET、CI/CD、Web APIs、microservices 与岗位要求直接对齐，属于明显可过的目标岗位。 |
| conf/8451-ResearchAI | fail | fail | 87.3 | 是 | P3A-002:high:Experience > TikTok · Security bullet 2/5<br>P3B-001:high:JD Core Skills / Minimum qualifications vs Resume Summary + Experience | 岗位强调 agentic systems、research agents、multi-step reasoning、RLHF，当前简历只有通用 LLM/ML 工程与评估证据，没有研究型 agent/RLHF 证据链。 |
| conf/Photon-AIEngineer | pass | fail | 89.4 | 否 | P2-001:high:Professional Summary 第1句<br>P3B-001:high:Skills + TikTok · Security / Threat Knowledge Retrieval Assistant | Generative AI、Python、LangChain/LlamaIndex/Vector Search 与当前 AI 工程叙事可形成合理桥接，真实 HR 首筛应通过。 |
| conf/Clarivate-NLP | pass | fail | 85.8 | 否 | P3B-001:high:Skills > AI/ML; overall body<br>P3B-010:high:Professional Summary / overall experience timeline | NLP、Python、LangChain、LangGraph 与当前 NLP/LLM 工作流叙事高度相关，尽管 senior title 偏 ambitious，但首筛仍可过。 |

## 汇总

- 命中: `6/10`
- 错判: `4`
- 错判列表: `conf/Phantom-SDET, conf/VeteransUnited-AssociateSE, conf/Photon-AIEngineer, conf/Clarivate-NLP`
