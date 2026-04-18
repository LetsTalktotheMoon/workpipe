# v3_conf_revised 对照 HR 标签

| Case | 目标 | 实际 | 分数 | 是否命中 | 主要高/致命项 | 标签理由 |
| --- | --- | --- | --- | --- | --- | --- |
| conf/FlexTrade-SoftwareDeveloper | pass | fail | 90.6 | 否 | P3B-001:high:Skills - Cloud / Summary | Golang、AWS、Docker、Linux、Shell 与当前后端/基础设施经历高度贴合，真实 HR 首筛应通过。 |
| conf/Whoop-SensorIntelligence | fail | pass | 94.0 | 否 | P3C-010:high:Experience > Software Engineer Intern | TikTok · Security > bullet 3 | 岗位核心是 signal processing、time-series biosignals、C 与 wearable domain，当前简历缺少对应信号处理和领域证据链，真实 HR 应直接保留。 |
| conf/Hopper-CustomerPlatform | pass | pass | 97.5 | 是 | none | 大规模分布式系统、前后端协同与客户平台方向整体可桥接，虽 senior 表达还可加强，但首筛可过。 |
| conf/Nuro-OffboardInfra | pass | pass | 94.6 | 是 | P2-010:high:Professional Summary, sentence 3 | Python/C++/Go、distributed systems 与 data/infrastructure 叙事形成较强闭环，真实 HR 应通过。 |
| conf/AMH-EnterpriseDataAnalyst | pass | pass | 98.0 | 是 | none | Business Intelligence、financial reporting、data warehousing、SQL 与当前数据分析主轴高度一致，首筛应通过。 |
| conf/Phantom-SDET | pass | pass | 95.5 | 是 | none | 虽然 raw JD 很强调 framework ownership，但当前简历已给出 reusable validation pack、pytest/Playwright、CI 集成、flakiness 控制与 API testing 证据，真实 HR 首筛应允许进入下一轮。 |
| conf/VeteransUnited-AssociateSE | pass | pass | 95.8 | 是 | none | Associate 级岗位对 .NET/C#/Angular/TypeScript、CI/CD、数据库与服务层经验的要求已经被正文和技能区较充分覆盖，未写 AI coding assistant 具体产品不应直接卡死首筛。 |
| conf/8451-ResearchAI | fail | pass | 95.8 | 否 | P3C-010:high:TikTok Experience, bullets 2 and 4 | 岗位强调 agentic systems、research agents、multi-step reasoning、RLHF，当前简历只有通用 LLM/ML 工程与评估证据，没有研究型 agent/RLHF 证据链。 |
| conf/Photon-AIEngineer | fail | pass | 93.3 | 否 | P2-001:high:Professional Summary 第一句<br>P3C-010:high:TikTok Experience / DiDi Experience | 岗位要求 production GenAI、LangChain/LlamaIndex、vector search、advanced retrieval 和 local LLM 能力，当前简历只有泛 RAG/LLM/Bedrock 证据，缺少命名框架与检索架构深度。 |
| conf/Clarivate-NLP | fail | pass | 99.7 | 否 | none | raw JD 明写 5+ 年 NLP/Python 与 LangChain/LangGraph 经验，且带 senior/technical leadership 责任；当前简历只有 3+ 年 transferable NLP/ML 叙事，不足以稳过真实 HR 首筛。 |

## 汇总

- 命中: `5/10`
- 错判: `5`
- 错判列表: `conf/FlexTrade-SoftwareDeveloper, conf/Whoop-SensorIntelligence, conf/8451-ResearchAI, conf/Photon-AIEngineer, conf/Clarivate-NLP`
