# v9_conf_revised 对照 HR 标签

| Case | 目标 | 实际 | 分数 | 是否命中 | 主要高/致命项 | 标签理由 |
| --- | --- | --- | --- | --- | --- | --- |
| conf/FlexTrade-SoftwareDeveloper | pass | pass | 94.1 | 是 | none | Golang、AWS、Docker、Linux、Shell 与当前后端/基础设施经历高度贴合，真实 HR 首筛应通过。 |
| conf/Whoop-SensorIntelligence | fail | fail | 90.4 | 是 | P2-001:high:Professional Summary bullet 1<br>P3B-001:high:Professional Summary / 全部 Experience | 岗位核心是 signal processing、time-series biosignals、C 与 wearable domain，当前简历缺少对应信号处理和领域证据链，真实 HR 应直接保留。 |
| conf/Hopper-CustomerPlatform | pass | pass | 97.0 | 是 | none | 大规模分布式系统、前后端协同与客户平台方向整体可桥接，虽 senior 表达还可加强，但首筛可过。 |
| conf/Nuro-OffboardInfra | pass | pass | 97.5 | 是 | none | Python/C++/Go、distributed systems 与 data/infrastructure 叙事形成较强闭环，真实 HR 应通过。 |
| conf/AMH-EnterpriseDataAnalyst | pass | pass | 93.5 | 是 | P3C-010:high:TikTok Experience, overall section | Business Intelligence、financial reporting、data warehousing、SQL 与当前数据分析主轴高度一致，首筛应通过。 |
| conf/Phantom-SDET | pass | fail | 91.6 | 否 | P3B-001:high:JD minimum qualifications vs. Professional Summary and TikTok Experience / project bullets | 虽然 raw JD 很强调 framework ownership，但当前简历已给出 reusable validation pack、pytest/Playwright、CI 集成、flakiness 控制与 API testing 证据，真实 HR 首筛应允许进入下一轮。 |
| conf/VeteransUnited-AssociateSE | pass | fail | 82.3 | 否 | P2-001:high:Summary sentence 1<br>P3B-001:high:Skills / recent backend experience<br>P3B-002:high:Summary / TikTok Experience / DiDi Experience | Associate 级岗位对 .NET/C#/Angular/TypeScript、CI/CD、数据库与服务层经验的要求已经被正文和技能区较充分覆盖，未写 AI coding assistant 具体产品不应直接卡死首筛。 |
| conf/8451-ResearchAI | fail | fail | 87.3 | 是 | P3A-002:high:Experience > TikTok · Security bullet 2/5<br>P3B-001:high:JD Core Skills / Minimum qualifications vs Resume Summary + Experience | 岗位强调 agentic systems、research agents、multi-step reasoning、RLHF，当前简历只有通用 LLM/ML 工程与评估证据，没有研究型 agent/RLHF 证据链。 |
| conf/Photon-AIEngineer | fail | fail | 89.4 | 是 | P2-001:high:Professional Summary 第1句<br>P3B-001:high:Skills + TikTok · Security / Threat Knowledge Retrieval Assistant | 岗位要求 production GenAI、LangChain/LlamaIndex、vector search、advanced retrieval 和 local LLM 能力，当前简历只有泛 RAG/LLM/Bedrock 证据，缺少命名框架与检索架构深度。 |
| conf/Clarivate-NLP | fail | fail | 85.8 | 是 | P3B-001:high:Skills > AI/ML; overall body<br>P3B-010:high:Professional Summary / overall experience timeline | raw JD 明写 5+ 年 NLP/Python 与 LangChain/LangGraph 经验，且带 senior/technical leadership 责任；当前简历只有 3+ 年 transferable NLP/ML 叙事，不足以稳过真实 HR 首筛。 |

## 汇总

- 命中: `8/10`
- 错判: `2`
- 错判列表: `conf/Phantom-SDET, conf/VeteransUnited-AssociateSE`
