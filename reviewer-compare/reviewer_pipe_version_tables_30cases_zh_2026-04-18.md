# Reviewer Pipeline 各版本 30 Case 全量表

说明：

- 这里把 30 个 case 全部按版本展开。
- `未测试` 表示这版当时没跑到这条，不代表 pass 或 fail。
- `主要扣分点` 已尽量翻成中文大白话。
- `平均分` 是按这个版本真正跑过的 case 算的。

## 旧 reviewer pipe

| 汇总项 | 内容 |
| --- | --- |
| 本版是干嘛的 | 老版统一 reviewer，没有这轮新增的岗位原文、年限硬门槛和等价证据规则。 |
| 为什么会有这版 | 它本来就是旧链路，用来当基线看“新 pipe 到底有没有真的更像 HR”。 |
| 已测试 case 数 | 20/30 |
| 主 20 case | 命中 12/20 |
| 外部确认 10 case | 未测试 |
| 平均分（已测试） | 91.6 |
| 集中扣分点 | 无明显集中项 |
| 这版最常漏掉的点 | 年限硬门槛、岗位主方向硬门槛、管理岗硬门槛。 |

| Case | 人工判断 | 分数/结论 | 主要扣分点 | 备注 |
| --- | --- | --- | --- | --- |
| same/Google | pass | 79.0/fail | 先把 `Bedrock` 补进 `## Skills`，并确保 TikTok retrieval 项目里现有的 `AWS Bedrock` 证据保持可见、可追溯。 | 误判 |
| same/Amazon | fail | 93.3/pass | Rewrite the Professional Summary to open with the target-role signal first, and move the analytics-transition framing to the end or remove it. | 误判 |
| same/AWS | fail | 94.6/pass | 无主要硬扣分 | 误判 |
| same/Microsoft | fail | 88.1/fail | 重写 Summary 第 1 句并显式加入 Distributed Systems，让首屏先展示 C++ / Azure / 分布式后端匹配，而不是先强调转行。 | 命中 |
| extra/CapitalOne-AI | fail | 89.2/fail | Rewrite the Professional Summary so it opens as a data-analysis profile with direct business decision-support language, not a generic bridge/candidate narrative. | 命中 |
| extra/Dataminr-Infra | fail | 92.8/fail | Rewrite the third Summary sentence to use a high-value cognition header such as Systems Judgment or Decision-Making instead of Structured Problem Solver. | 命中 |
| extra/HealthEquity-DotNet | fail | 93.5/pass | 无主要硬扣分 | 误判 |
| extra/Zoox-LLM | fail | 94.4/pass | 无主要硬扣分 | 误判 |
| extra/Synechron-Backend | pass | 89.5/fail | Rewrite the Professional Summary into the exact 3-sentence labeled format and front-load the strongest platform-delivery signal. | 误判 |
| extra/Ramp-Platform | pass | 97.0/pass | 把项目段落收敛到 2 个，只保留最强的两个 project baseline，避免模板不一致。 | 命中 |
| gen2/Discord-DBInfra | fail | 82.7/fail | 补出一个真实的 Rust 证据并放进最相关的经历正文，当前这份简历对 Discord 的 must-have 栈不完整。 | 命中 |
| gen2/AppliedIntuition-CloudInfra | pass | 93.8/pass | 无主要硬扣分 | 命中 |
| gen2/Fireblocks-SRE | pass | 96.1/pass | 无主要硬扣分 | 命中 |
| gen2/ChildrensHospital-Azure | fail | 87.7/fail | Rewrite the Professional Summary to lead with backend/application engineering identity and replace the low-signal `Team Fit` / analytics-transition framing. | 命中 |
| gen2/CapitalOne-Manager2 | fail | 92.6/fail | Rewrite the summary to be role-first: open with data analysis, reporting, and decision-support language, not `Data Analysis Candidate`. | 命中 |
| gen2/Fanduel-AnalyticsManager | fail | 93.8/pass | 无主要硬扣分 | 误判 |
| gen2/Geico-SWE2 | pass | 91.7/fail | 把 `Code Review` 补进 `## Skills`，并把 Skills 重新拆成不超过 14 词/行的短分类。 | 误判 |
| gen2/Doordash-Backend | pass | 94.4/pass | 无主要硬扣分 | 命中 |
| gen2/Cisco-NetworkingSenior | fail | 91.8/fail | 把 Summary 首句改成 Cisco 目标向的 backend/networking 主叙事，先写 Linux/C++/Python/gRPC/Kafka 证据，再补充 analytics 转向背景。 | 命中 |
| gen2/Genentech-MLInfra | pass | 95.9/pass | 无主要硬扣分 | 命中 |
| conf/FlexTrade-SoftwareDeveloper | pass | 未测试 | 未测试 | 未测试 |
| conf/Whoop-SensorIntelligence | fail | 未测试 | 未测试 | 未测试 |
| conf/Hopper-CustomerPlatform | pass | 未测试 | 未测试 | 未测试 |
| conf/Nuro-OffboardInfra | pass | 未测试 | 未测试 | 未测试 |
| conf/AMH-EnterpriseDataAnalyst | pass | 未测试 | 未测试 | 未测试 |
| conf/Phantom-SDET | pass | 未测试 | 未测试 | 未测试 |
| conf/VeteransUnited-AssociateSE | pass | 未测试 | 未测试 | 未测试 |
| conf/8451-ResearchAI | fail | 未测试 | 未测试 | 未测试 |
| conf/Photon-AIEngineer | fail | 未测试 | 未测试 | 未测试 |
| conf/Clarivate-NLP | fail | 未测试 | 未测试 | 未测试 |

## v2 早期重算版

| 汇总项 | 内容 |
| --- | --- |
| 本版是干嘛的 | 开始试着把分数往“更像 HR”去调，但还没真正接入岗位原文。 |
| 为什么会有这版 | 想先把旧的新 pipe 从“纯规则扣分”拉回一点实际招聘视角。 |
| 已测试 case 数 | 10/30 |
| 主 20 case | 命中 3/10；未测试 10 |
| 外部确认 10 case | 未测试 |
| 平均分（已测试） | 94.4 |
| 集中扣分点 | P1-042 @ x3；有明显不合理/硬逻辑风险 x2；P1-040 @ x2；P3D-001 @ x2；P2-001 @ x2 |
| 这版最常漏掉的点 | 岗位原文里的年限、平台深度、岗位主方向。 |

| Case | 人工判断 | 分数/结论 | 主要扣分点 | 备注 |
| --- | --- | --- | --- | --- |
| same/Google | pass | 92.8/pass | 正文里有一条写得不稳/容易被追问 | 命中 |
| same/Amazon | fail | 97.8/pass | 格式/强调方式影响阅读；主语言写得太散；结果数字多，但规模锚点不够 | 误判 |
| same/AWS | fail | 94.4/fail | 有明显不合理/硬逻辑风险 | 命中 |
| same/Microsoft | fail | 90.4/pass | 岗位主技术或主能力没有被真正证明；技术写得太满，像堆栈炫技 | 误判 |
| extra/CapitalOne-AI | fail | 95.2/pass | 格式/强调方式影响阅读；摘要开头让 HR 第一眼误判；行业/团队方向桥接不够 | 误判 |
| extra/Dataminr-Infra | fail | 97.4/pass | 强调样式不稳；摘要第三句/团队贴合句没价值；结果数字多，但规模锚点不够 | 误判 |
| extra/HealthEquity-DotNet | fail | 88.8/pass | 岗位主技术或主能力没有被真正证明 | 误判 |
| extra/Zoox-LLM | fail | 96.8/pass | 技术写得太满，像堆栈炫技 | 误判 |
| extra/Synechron-Backend | pass | 95.0/pass | 强调样式不稳；格式/强调方式影响阅读；摘要开头让 HR 第一眼误判 | 命中 |
| extra/Ramp-Platform | pass | 95.8/fail | 有明显不合理/硬逻辑风险 | 误判 |
| gen2/Discord-DBInfra | fail | 未测试 | 未测试 | 未测试 |
| gen2/AppliedIntuition-CloudInfra | pass | 未测试 | 未测试 | 未测试 |
| gen2/Fireblocks-SRE | pass | 未测试 | 未测试 | 未测试 |
| gen2/ChildrensHospital-Azure | fail | 未测试 | 未测试 | 未测试 |
| gen2/CapitalOne-Manager2 | fail | 未测试 | 未测试 | 未测试 |
| gen2/Fanduel-AnalyticsManager | fail | 未测试 | 未测试 | 未测试 |
| gen2/Geico-SWE2 | pass | 未测试 | 未测试 | 未测试 |
| gen2/Doordash-Backend | pass | 未测试 | 未测试 | 未测试 |
| gen2/Cisco-NetworkingSenior | fail | 未测试 | 未测试 | 未测试 |
| gen2/Genentech-MLInfra | pass | 未测试 | 未测试 | 未测试 |
| conf/FlexTrade-SoftwareDeveloper | pass | 未测试 | 未测试 | 未测试 |
| conf/Whoop-SensorIntelligence | fail | 未测试 | 未测试 | 未测试 |
| conf/Hopper-CustomerPlatform | pass | 未测试 | 未测试 | 未测试 |
| conf/Nuro-OffboardInfra | pass | 未测试 | 未测试 | 未测试 |
| conf/AMH-EnterpriseDataAnalyst | pass | 未测试 | 未测试 | 未测试 |
| conf/Phantom-SDET | pass | 未测试 | 未测试 | 未测试 |
| conf/VeteransUnited-AssociateSE | pass | 未测试 | 未测试 | 未测试 |
| conf/8451-ResearchAI | fail | 未测试 | 未测试 | 未测试 |
| conf/Photon-AIEngineer | fail | 未测试 | 未测试 | 未测试 |
| conf/Clarivate-NLP | fail | 未测试 | 未测试 | 未测试 |

## v3 稳定版

| 汇总项 | 内容 |
| --- | --- |
| 本版是干嘛的 | 把格式、首屏、内容一致性和大部分基础规则先稳定下来。 |
| 为什么会有这版 | 想先做出一个“同模型同提示重复跑，结果别乱跳”的版本。 |
| 已测试 case 数 | 30/30 |
| 主 20 case | 命中 13/20 |
| 外部确认 10 case | 命中 5/10 |
| 平均分（已测试） | 95.1 |
| 集中扣分点 | P2-001 @ x10；技术写得太满，像堆栈炫技 x8；P1-040 @ x7；P1-042 @ x6；P3D-001 @ x4 |
| 这版最常漏掉的点 | 岗位原文里的年限、管理要求、特定平台/底层方向。 |

| Case | 人工判断 | 分数/结论 | 主要扣分点 | 备注 |
| --- | --- | --- | --- | --- |
| same/Google | pass | 94.1/pass | 正文里有一条写得不稳/容易被追问 | 命中 |
| same/Amazon | fail | 95.0/pass | 技术写得太满，像堆栈炫技 | 误判 |
| same/AWS | fail | 97.5/pass | 格式/强调方式影响阅读；摘要开头让 HR 第一眼误判 | 误判 |
| same/Microsoft | fail | 90.3/fail | 岗位主技术或主能力没有被真正证明 | 命中 |
| extra/CapitalOne-AI | fail | 87.9/fail | 摘要开头让 HR 第一眼误判；年限/层级/管理范围不够 | 命中 |
| extra/Dataminr-Infra | fail | 99.0/pass | 摘要第三句/团队贴合句没价值 | 误判 |
| extra/HealthEquity-DotNet | fail | 89.6/fail | 岗位主技术或主能力没有被真正证明 | 命中 |
| extra/Zoox-LLM | fail | 96.8/pass | 技术写得太满，像堆栈炫技 | 误判 |
| extra/Synechron-Backend | pass | 99.2/pass | 强调样式不稳；技能分类名不清楚 | 命中 |
| extra/Ramp-Platform | pass | 97.1/pass | 强调样式不稳；行业/团队方向桥接不够；结果数字多，但规模锚点不够 | 命中 |
| gen2/Discord-DBInfra | fail | 92.9/fail | 岗位主技术或主能力没有被真正证明 | 命中 |
| gen2/AppliedIntuition-CloudInfra | pass | 96.5/pass | 强调样式不稳；摘要开头让 HR 第一眼误判；结果数字多，但规模锚点不够 | 命中 |
| gen2/Fireblocks-SRE | pass | 98.0/pass | 摘要开头让 HR 第一眼误判 | 命中 |
| gen2/ChildrensHospital-Azure | fail | 93.3/pass | 格式/强调方式影响阅读；技能区太挤；摘要开头让 HR 第一眼误判 | 误判 |
| gen2/CapitalOne-Manager2 | fail | 90.2/fail | 年限/层级/管理范围不够；技术写得太满，像堆栈炫技 | 命中 |
| gen2/Fanduel-AnalyticsManager | fail | 94.7/pass | 强调样式不稳；格式/强调方式影响阅读；摘要开头让 HR 第一眼误判 | 误判 |
| gen2/Geico-SWE2 | pass | 97.0/pass | 摘要开头让 HR 第一眼误判；结果数字多，但规模锚点不够 | 命中 |
| gen2/Doordash-Backend | pass | 96.0/pass | 强调样式不稳；技能区太挤；摘要开头让 HR 第一眼误判 | 命中 |
| gen2/Cisco-NetworkingSenior | fail | 96.8/pass | 技术写得太满，像堆栈炫技 | 误判 |
| gen2/Genentech-MLInfra | pass | 96.4/pass | 技术写得太满，像堆栈炫技 | 命中 |
| conf/FlexTrade-SoftwareDeveloper | pass | 90.6/fail | 岗位主技术或主能力没有被真正证明 | 误判 |
| conf/Whoop-SensorIntelligence | fail | 94.0/pass | 技术写得太满，像堆栈炫技 | 误判 |
| conf/Hopper-CustomerPlatform | pass | 97.5/pass | 强调样式不稳；摘要开头让 HR 第一眼误判 | 命中 |
| conf/Nuro-OffboardInfra | pass | 94.6/pass | 摘要第三句/团队贴合句没价值 | 命中 |
| conf/AMH-EnterpriseDataAnalyst | pass | 98.0/pass | 强调样式不稳；格式/强调方式影响阅读；结果数字多，但规模锚点不够 | 命中 |
| conf/Phantom-SDET | pass | 95.5/pass | 格式/强调方式影响阅读；摘要开头让 HR 第一眼误判；技能分类名不清楚 | 命中 |
| conf/VeteransUnited-AssociateSE | pass | 95.8/pass | 格式/强调方式影响阅读；摘要开头让 HR 第一眼误判；技能分类名不清楚 | 命中 |
| conf/8451-ResearchAI | fail | 95.8/pass | 技术写得太满，像堆栈炫技 | 误判 |
| conf/Photon-AIEngineer | fail | 93.3/pass | 摘要开头让 HR 第一眼误判；技术写得太满，像堆栈炫技 | 误判 |
| conf/Clarivate-NLP | fail | 99.7/pass | 细节真实性需要更稳 | 误判 |

## v4 收敛试验版

| 汇总项 | 内容 |
| --- | --- |
| 本版是干嘛的 | 继续试图把 v3 的判断收紧一点，并减少一些乱扣。 |
| 为什么会有这版 | 想验证“再收一点”会不会更像 HR。 |
| 已测试 case 数 | 10/30 |
| 主 20 case | 命中 3/10；未测试 10 |
| 外部确认 10 case | 未测试 |
| 平均分（已测试） | 94.7 |
| 集中扣分点 | 技术写得太满，像堆栈炫技 x3；P1-040 @ x1；P2-010 @ x1；年限/层级/管理范围不够 x1；P2-001 @ x1 |
| 这版最常漏掉的点 | 岗位原文门槛，外加真实性硬扣仍不稳。 |

| Case | 人工判断 | 分数/结论 | 主要扣分点 | 备注 |
| --- | --- | --- | --- | --- |
| same/Google | pass | 86.2/fail | 正文里有一条写得不稳/容易被追问；摘要里写了，正文却没证明 | 误判 |
| same/Amazon | fail | 95.3/pass | 技术写得太满，像堆栈炫技 | 误判 |
| same/AWS | fail | 97.7/pass | 摘要开头让 HR 第一眼误判；细节真实性需要更稳 | 误判 |
| same/Microsoft | fail | 95.8/pass | 技术写得太满，像堆栈炫技 | 误判 |
| extra/CapitalOne-AI | fail | 88.6/fail | 年限/层级/管理范围不够 | 命中 |
| extra/Dataminr-Infra | fail | 98.5/pass | 强调样式不稳；摘要第三句/团队贴合句没价值 | 误判 |
| extra/HealthEquity-DotNet | fail | 88.6/pass | 摘要开头让 HR 第一眼误判；技能区写了，但正文没证据 | 误判 |
| extra/Zoox-LLM | fail | 96.4/pass | 技术写得太满，像堆栈炫技 | 误判 |
| extra/Synechron-Backend | pass | 100.0/pass | 无主要硬扣分 | 命中 |
| extra/Ramp-Platform | pass | 100.0/pass | 无主要硬扣分 | 命中 |
| gen2/Discord-DBInfra | fail | 未测试 | 未测试 | 未测试 |
| gen2/AppliedIntuition-CloudInfra | pass | 未测试 | 未测试 | 未测试 |
| gen2/Fireblocks-SRE | pass | 未测试 | 未测试 | 未测试 |
| gen2/ChildrensHospital-Azure | fail | 未测试 | 未测试 | 未测试 |
| gen2/CapitalOne-Manager2 | fail | 未测试 | 未测试 | 未测试 |
| gen2/Fanduel-AnalyticsManager | fail | 未测试 | 未测试 | 未测试 |
| gen2/Geico-SWE2 | pass | 未测试 | 未测试 | 未测试 |
| gen2/Doordash-Backend | pass | 未测试 | 未测试 | 未测试 |
| gen2/Cisco-NetworkingSenior | fail | 未测试 | 未测试 | 未测试 |
| gen2/Genentech-MLInfra | pass | 未测试 | 未测试 | 未测试 |
| conf/FlexTrade-SoftwareDeveloper | pass | 未测试 | 未测试 | 未测试 |
| conf/Whoop-SensorIntelligence | fail | 未测试 | 未测试 | 未测试 |
| conf/Hopper-CustomerPlatform | pass | 未测试 | 未测试 | 未测试 |
| conf/Nuro-OffboardInfra | pass | 未测试 | 未测试 | 未测试 |
| conf/AMH-EnterpriseDataAnalyst | pass | 未测试 | 未测试 | 未测试 |
| conf/Phantom-SDET | pass | 未测试 | 未测试 | 未测试 |
| conf/VeteransUnited-AssociateSE | pass | 未测试 | 未测试 | 未测试 |
| conf/8451-ResearchAI | fail | 未测试 | 未测试 | 未测试 |
| conf/Photon-AIEngineer | fail | 未测试 | 未测试 | 未测试 |
| conf/Clarivate-NLP | fail | 未测试 | 未测试 | 未测试 |

## v5 更像 HR gate 的版本

| 汇总项 | 内容 |
| --- | --- |
| 本版是干嘛的 | 更强调“一眼看上去像不像这个岗位”，尤其是首屏和结构。 |
| 为什么会有这版 | 希望别再让“商业案例看起来会很多技术”就轻松过。 |
| 已测试 case 数 | 20/30 |
| 主 20 case | 命中 12/20 |
| 外部确认 10 case | 未测试 |
| 平均分（已测试） | 95.6 |
| 集中扣分点 | P1-042 @ x5；技术写得太满，像堆栈炫技 x5；P2-001 @ x4；年限/层级/管理范围不够 x3；P3B-003 @ x3 |
| 这版最常漏掉的点 | 岗位原文里的年限、特定平台深度、研究型 AI 门槛。 |

| Case | 人工判断 | 分数/结论 | 主要扣分点 | 备注 |
| --- | --- | --- | --- | --- |
| same/Google | pass | 94.4/pass | 正文里有一条写得不稳/容易被追问 | 命中 |
| same/Amazon | fail | 97.3/pass | 技术写得太满，像堆栈炫技 | 误判 |
| same/AWS | fail | 96.3/pass | 技术写得太满，像堆栈炫技 | 误判 |
| same/Microsoft | fail | 95.8/pass | 技术写得太满，像堆栈炫技 | 误判 |
| extra/CapitalOne-AI | fail | 91.9/fail | 年限/层级/管理范围不够 | 命中 |
| extra/Dataminr-Infra | fail | 95.5/pass | P1-030；强调样式不稳；格式/强调方式影响阅读 | 误判 |
| extra/HealthEquity-DotNet | fail | 97.0/pass | 强调样式不稳；格式/强调方式影响阅读；摘要开头让 HR 第一眼误判 | 误判 |
| extra/Zoox-LLM | fail | 96.5/pass | 格式/强调方式影响阅读；行业/团队方向桥接不够；主语言写得太散 | 误判 |
| extra/Synechron-Backend | pass | 100.0/pass | 无主要硬扣分 | 命中 |
| extra/Ramp-Platform | pass | 100.0/pass | 无主要硬扣分 | 命中 |
| gen2/Discord-DBInfra | fail | 93.9/fail | 岗位主技术或主能力没有被真正证明 | 命中 |
| gen2/AppliedIntuition-CloudInfra | pass | 100.0/pass | 无主要硬扣分 | 命中 |
| gen2/Fireblocks-SRE | pass | 95.6/pass | 摘要开头让 HR 第一眼误判；行业/团队方向桥接不够；结果数字多，但规模锚点不够 | 命中 |
| gen2/ChildrensHospital-Azure | fail | 93.0/pass | 摘要第三句/团队贴合句没价值；技术写得太满，像堆栈炫技 | 误判 |
| gen2/CapitalOne-Manager2 | fail | 90.9/fail | 年限/层级/管理范围不够 | 命中 |
| gen2/Fanduel-AnalyticsManager | fail | 89.0/fail | 年限/层级/管理范围不够 | 命中 |
| gen2/Geico-SWE2 | pass | 96.5/pass | 格式/强调方式影响阅读；摘要开头让 HR 第一眼误判；结果数字多，但规模锚点不够 | 命中 |
| gen2/Doordash-Backend | pass | 97.0/pass | 摘要开头让 HR 第一眼误判；结果数字多，但规模锚点不够 | 命中 |
| gen2/Cisco-NetworkingSenior | fail | 95.8/pass | 技术写得太满，像堆栈炫技 | 误判 |
| gen2/Genentech-MLInfra | pass | 96.5/pass | 格式/强调方式影响阅读；行业/团队方向桥接不够；主语言写得太散 | 命中 |
| conf/FlexTrade-SoftwareDeveloper | pass | 未测试 | 未测试 | 未测试 |
| conf/Whoop-SensorIntelligence | fail | 未测试 | 未测试 | 未测试 |
| conf/Hopper-CustomerPlatform | pass | 未测试 | 未测试 | 未测试 |
| conf/Nuro-OffboardInfra | pass | 未测试 | 未测试 | 未测试 |
| conf/AMH-EnterpriseDataAnalyst | pass | 未测试 | 未测试 | 未测试 |
| conf/Phantom-SDET | pass | 未测试 | 未测试 | 未测试 |
| conf/VeteransUnited-AssociateSE | pass | 未测试 | 未测试 | 未测试 |
| conf/8451-ResearchAI | fail | 未测试 | 未测试 | 未测试 |
| conf/Photon-AIEngineer | fail | 未测试 | 未测试 | 未测试 |
| conf/Clarivate-NLP | fail | 未测试 | 未测试 | 未测试 |

## v6 再收紧版

| 汇总项 | 内容 |
| --- | --- |
| 本版是干嘛的 | 继续收紧“写得太满、太像炫技”的部分，并加强首屏判断。 |
| 为什么会有这版 | 想压住“技术名词很多就能唬过去”的问题。 |
| 已测试 case 数 | 20/30 |
| 主 20 case | 命中 12/20 |
| 外部确认 10 case | 未测试 |
| 平均分（已测试） | 95.2 |
| 集中扣分点 | 技术写得太满，像堆栈炫技 x7；P1-042 @ x5；P2-001 @ x4；P2-010 @ x2；P3D-001 @ x2 |
| 这版最常漏掉的点 | 岗位原文门槛，尤其是年限和特殊方向岗位。 |

| Case | 人工判断 | 分数/结论 | 主要扣分点 | 备注 |
| --- | --- | --- | --- | --- |
| same/Google | pass | 91.2/pass | 正文里有一条写得不稳/容易被追问；技术写得太满，像堆栈炫技 | 命中 |
| same/Amazon | fail | 95.8/pass | 技术写得太满，像堆栈炫技 | 误判 |
| same/AWS | fail | 96.5/pass | 格式/强调方式影响阅读；摘要开头让 HR 第一眼误判；摘要第三句/团队贴合句没价值 | 误判 |
| same/Microsoft | fail | 91.8/fail | 岗位主技术或主能力没有被真正证明 | 命中 |
| extra/CapitalOne-AI | fail | 96.2/pass | 强调样式不稳；摘要开头让 HR 第一眼误判；结果数字多，但规模锚点不够 | 误判 |
| extra/Dataminr-Infra | fail | 98.5/pass | 格式/强调方式影响阅读；摘要第三句/团队贴合句没价值 | 误判 |
| extra/HealthEquity-DotNet | fail | 94.5/pass | 摘要开头让 HR 第一眼误判 | 误判 |
| extra/Zoox-LLM | fail | 98.6/pass | 行业/团队方向桥接不够 | 误判 |
| extra/Synechron-Backend | pass | 99.7/pass | 技能分类名不清楚 | 命中 |
| extra/Ramp-Platform | pass | 97.3/pass | 技术写得太满，像堆栈炫技 | 命中 |
| gen2/Discord-DBInfra | fail | 92.9/fail | 岗位主技术或主能力没有被真正证明 | 命中 |
| gen2/AppliedIntuition-CloudInfra | pass | 96.3/pass | 技术写得太满，像堆栈炫技 | 命中 |
| gen2/Fireblocks-SRE | pass | 96.5/pass | P1-030；格式/强调方式影响阅读；摘要开头让 HR 第一眼误判 | 命中 |
| gen2/ChildrensHospital-Azure | fail | 94.3/pass | 技术写得太满，像堆栈炫技 | 误判 |
| gen2/CapitalOne-Manager2 | fail | 89.9/fail | 年限/层级/管理范围不够 | 命中 |
| gen2/Fanduel-AnalyticsManager | fail | 89.0/fail | 摘要开头让 HR 第一眼误判；年限/层级/管理范围不够 | 命中 |
| gen2/Geico-SWE2 | pass | 96.3/pass | 技术写得太满，像堆栈炫技 | 命中 |
| gen2/Doordash-Backend | pass | 96.3/pass | 技术写得太满，像堆栈炫技 | 命中 |
| gen2/Cisco-NetworkingSenior | fail | 96.5/pass | 格式/强调方式影响阅读；摘要开头让 HR 第一眼误判；结果数字多，但规模锚点不够 | 误判 |
| gen2/Genentech-MLInfra | pass | 95.7/pass | P1-030；格式/强调方式影响阅读；跨行业迁移解释不够 | 命中 |
| conf/FlexTrade-SoftwareDeveloper | pass | 未测试 | 未测试 | 未测试 |
| conf/Whoop-SensorIntelligence | fail | 未测试 | 未测试 | 未测试 |
| conf/Hopper-CustomerPlatform | pass | 未测试 | 未测试 | 未测试 |
| conf/Nuro-OffboardInfra | pass | 未测试 | 未测试 | 未测试 |
| conf/AMH-EnterpriseDataAnalyst | pass | 未测试 | 未测试 | 未测试 |
| conf/Phantom-SDET | pass | 未测试 | 未测试 | 未测试 |
| conf/VeteransUnited-AssociateSE | pass | 未测试 | 未测试 | 未测试 |
| conf/8451-ResearchAI | fail | 未测试 | 未测试 | 未测试 |
| conf/Photon-AIEngineer | fail | 未测试 | 未测试 | 未测试 |
| conf/Clarivate-NLP | fail | 未测试 | 未测试 | 未测试 |

## v7 接入岗位原文版

| 汇总项 | 内容 |
| --- | --- |
| 本版是干嘛的 | 把岗位原文直接塞进 reviewer，让它能看到年限、职责和原始 minimum qualifications。 |
| 为什么会有这版 | 前面几版最大的问题，就是只看压缩后的岗位字段，看不到真正的一眼硬门槛。 |
| 已测试 case 数 | 20/30 |
| 主 20 case | 命中 17/20 |
| 外部确认 10 case | 未测试 |
| 平均分（已测试） | 91.1 |
| 集中扣分点 | 年限/层级/管理范围不够 x6；技术写得太满，像堆栈炫技 x6；岗位主技术或主能力没有被真正证明 x6；岗位本身要求的底层方向不对口 x4；P1-040 @ x2 |
| 这版最常漏掉的点 | 对“辅助工具”过严，死盯关键词。 |

| Case | 人工判断 | 分数/结论 | 主要扣分点 | 备注 |
| --- | --- | --- | --- | --- |
| same/Google | pass | 90.9/pass | 正文里有一条写得不稳/容易被追问；技术写得太满，像堆栈炫技 | 命中 |
| same/Amazon | fail | 90.8/fail | 年限/层级/管理范围不够 | 命中 |
| same/AWS | fail | 96.0/pass | P1-014；强调样式不稳；摘要开头让 HR 第一眼误判 | 误判 |
| same/Microsoft | fail | 78.5/fail | 岗位主技术或主能力没有被真正证明；技能区写了，但正文没证据；岗位本身要求的底层方向不对口 | 命中 |
| extra/CapitalOne-AI | fail | 90.9/fail | 年限/层级/管理范围不够 | 命中 |
| extra/Dataminr-Infra | fail | 90.7/fail | 年限/层级/管理范围不够；技术写得太满，像堆栈炫技 | 命中 |
| extra/HealthEquity-DotNet | fail | 81.5/fail | 摘要开头让 HR 第一眼误判；年限/层级/管理范围不够；特定平台深度不够 | 命中 |
| extra/Zoox-LLM | fail | 91.5/fail | 岗位主技术或主能力没有被真正证明 | 命中 |
| extra/Synechron-Backend | pass | 99.5/pass | 格式/强调方式影响阅读 | 命中 |
| extra/Ramp-Platform | pass | 98.5/pass | 强调样式不稳；结果数字多，但规模锚点不够 | 命中 |
| gen2/Discord-DBInfra | fail | 90.6/fail | 岗位本身要求的底层方向不对口 | 命中 |
| gen2/AppliedIntuition-CloudInfra | pass | 97.0/pass | 摘要开头让 HR 第一眼误判；结果数字多，但规模锚点不够 | 命中 |
| gen2/Fireblocks-SRE | pass | 91.4/fail | 岗位主技术或主能力没有被真正证明 | 误判 |
| gen2/ChildrensHospital-Azure | fail | 86.4/fail | 摘要第三句/团队贴合句没价值；岗位本身要求的底层方向不对口；技术写得太满，像堆栈炫技 | 命中 |
| gen2/CapitalOne-Manager2 | fail | 86.3/fail | 年限/层级/管理范围不够；岗位主技术或主能力没有被真正证明 | 命中 |
| gen2/Fanduel-AnalyticsManager | fail | 83.3/fail | 摘要开头让 HR 第一眼误判；岗位主技术或主能力没有被真正证明；年限/层级/管理范围不够 | 命中 |
| gen2/Geico-SWE2 | pass | 92.4/fail | 岗位主技术或主能力没有被真正证明 | 误判 |
| gen2/Doordash-Backend | pass | 95.8/pass | 技术写得太满，像堆栈炫技 | 命中 |
| gen2/Cisco-NetworkingSenior | fail | 92.4/fail | 岗位本身要求的底层方向不对口 | 命中 |
| gen2/Genentech-MLInfra | pass | 98.3/pass | 技术写得太满，像堆栈炫技 | 命中 |
| conf/FlexTrade-SoftwareDeveloper | pass | 未测试 | 未测试 | 未测试 |
| conf/Whoop-SensorIntelligence | fail | 未测试 | 未测试 | 未测试 |
| conf/Hopper-CustomerPlatform | pass | 未测试 | 未测试 | 未测试 |
| conf/Nuro-OffboardInfra | pass | 未测试 | 未测试 | 未测试 |
| conf/AMH-EnterpriseDataAnalyst | pass | 未测试 | 未测试 | 未测试 |
| conf/Phantom-SDET | pass | 未测试 | 未测试 | 未测试 |
| conf/VeteransUnited-AssociateSE | pass | 未测试 | 未测试 | 未测试 |
| conf/8451-ResearchAI | fail | 未测试 | 未测试 | 未测试 |
| conf/Photon-AIEngineer | fail | 未测试 | 未测试 | 未测试 |
| conf/Clarivate-NLP | fail | 未测试 | 未测试 | 未测试 |

## v8 辅助工具放松版

| 汇总项 | 内容 |
| --- | --- |
| 本版是干嘛的 | 把 Helm、ArgoCD、PowerShell、IaC 这类“辅助工具”从岗位主门槛里拆出来。 |
| 为什么会有这版 | 因为 v7 把不少能过的 SRE/后端简历卡死在工具词上。 |
| 已测试 case 数 | 20/30 |
| 主 20 case | 命中 16/20 |
| 外部确认 10 case | 未测试 |
| 平均分（已测试） | 92.7 |
| 集中扣分点 | 岗位主技术或主能力没有被真正证明 x5；年限/层级/管理范围不够 x4；岗位本身要求的底层方向不对口 x4；P2-001 @ x4；技术写得太满，像堆栈炫技 x3 |
| 这版最常漏掉的点 | 年限硬门槛、多云职责和候选人真实要求之间的边界。 |

| Case | 人工判断 | 分数/结论 | 主要扣分点 | 备注 |
| --- | --- | --- | --- | --- |
| same/Google | pass | 94.4/pass | 正文里有一条写得不稳/容易被追问 | 命中 |
| same/Amazon | fail | 96.9/pass | 格式/强调方式影响阅读；摘要开头让 HR 第一眼误判；主语言写得太散 | 误判 |
| same/AWS | fail | 96.0/pass | 摘要开头让 HR 第一眼误判 | 误判 |
| same/Microsoft | fail | 84.7/fail | 岗位主技术或主能力没有被真正证明；岗位本身要求的底层方向不对口 | 命中 |
| extra/CapitalOne-AI | fail | 92.4/fail | 年限/层级/管理范围不够 | 命中 |
| extra/Dataminr-Infra | fail | 95.8/pass | 技术写得太满，像堆栈炫技 | 误判 |
| extra/HealthEquity-DotNet | fail | 86.8/fail | 年限/层级/管理范围不够；特定平台深度不够 | 命中 |
| extra/Zoox-LLM | fail | 91.4/fail | 岗位主技术或主能力没有被真正证明 | 命中 |
| extra/Synechron-Backend | pass | 100.0/pass | 无主要硬扣分 | 命中 |
| extra/Ramp-Platform | pass | 99.5/pass | 格式/强调方式影响阅读 | 命中 |
| gen2/Discord-DBInfra | fail | 94.4/fail | 岗位本身要求的底层方向不对口 | 命中 |
| gen2/AppliedIntuition-CloudInfra | pass | 90.9/fail | 岗位主技术或主能力没有被真正证明 | 误判 |
| gen2/Fireblocks-SRE | pass | 92.8/pass | 摘要开头让 HR 第一眼误判；行业/团队方向桥接不够；发布/配置/辅助工具写得不够 | 命中 |
| gen2/ChildrensHospital-Azure | fail | 89.4/fail | 岗位本身要求的底层方向不对口；技术写得太满，像堆栈炫技 | 命中 |
| gen2/CapitalOne-Manager2 | fail | 85.8/fail | 年限/层级/管理范围不够；岗位主技术或主能力没有被真正证明 | 命中 |
| gen2/Fanduel-AnalyticsManager | fail | 85.8/fail | 岗位主技术或主能力没有被真正证明；年限/层级/管理范围不够 | 命中 |
| gen2/Geico-SWE2 | pass | 96.6/pass | 摘要开头让 HR 第一眼误判；最新经历第一条不够像主卖点；发布/配置/辅助工具写得不够 | 命中 |
| gen2/Doordash-Backend | pass | 97.0/pass | 摘要开头让 HR 第一眼误判；结果数字多，但规模锚点不够 | 命中 |
| gen2/Cisco-NetworkingSenior | fail | 85.8/fail | 摘要开头让 HR 第一眼误判；正文里有一条写得不稳/容易被追问；岗位本身要求的底层方向不对口 | 命中 |
| gen2/Genentech-MLInfra | pass | 96.8/pass | 技术写得太满，像堆栈炫技 | 命中 |
| conf/FlexTrade-SoftwareDeveloper | pass | 未测试 | 未测试 | 未测试 |
| conf/Whoop-SensorIntelligence | fail | 未测试 | 未测试 | 未测试 |
| conf/Hopper-CustomerPlatform | pass | 未测试 | 未测试 | 未测试 |
| conf/Nuro-OffboardInfra | pass | 未测试 | 未测试 | 未测试 |
| conf/AMH-EnterpriseDataAnalyst | pass | 未测试 | 未测试 | 未测试 |
| conf/Phantom-SDET | pass | 未测试 | 未测试 | 未测试 |
| conf/VeteransUnited-AssociateSE | pass | 未测试 | 未测试 | 未测试 |
| conf/8451-ResearchAI | fail | 未测试 | 未测试 | 未测试 |
| conf/Photon-AIEngineer | fail | 未测试 | 未测试 | 未测试 |
| conf/Clarivate-NLP | fail | 未测试 | 未测试 | 未测试 |

## v9 把硬门槛拉回来的版本

| 汇总项 | 内容 |
| --- | --- |
| 本版是干嘛的 | 重新把年限硬门槛拉严，并明确“多云职责”不等于候选人必须三云都干过。 |
| 为什么会有这版 | v8 的问题不是太严，而是把真正该硬的地方又放松了。 |
| 已测试 case 数 | 30/30 |
| 主 20 case | 命中 19/20 |
| 外部确认 10 case | 命中 8/10 |
| 平均分（已测试） | 92.2 |
| 集中扣分点 | 岗位主技术或主能力没有被真正证明 x9；年限/层级/管理范围不够 x7；P2-001 @ x6；P1-042 @ x5；摘要开头让 HR 第一眼误判 x5 |
| 这版最常漏掉的点 | 测试框架等价证据、AI coding assistant 这类示例型工具。 |

| Case | 人工判断 | 分数/结论 | 主要扣分点 | 备注 |
| --- | --- | --- | --- | --- |
| same/Google | pass | 98.0/pass | 摘要开头让 HR 第一眼误判 | 命中 |
| same/Amazon | fail | 91.2/fail | 年限/层级/管理范围不够；技术写得太满，像堆栈炫技 | 命中 |
| same/AWS | fail | 97.5/pass | 格式/强调方式影响阅读；摘要开头让 HR 第一眼误判 | 误判 |
| same/Microsoft | fail | 87.7/fail | 摘要开头让 HR 第一眼误判；岗位本身要求的底层方向不对口；技术写得太满，像堆栈炫技 | 命中 |
| extra/CapitalOne-AI | fail | 85.3/fail | 岗位主技术或主能力没有被真正证明；年限/层级/管理范围不够 | 命中 |
| extra/Dataminr-Infra | fail | 92.9/fail | 年限/层级/管理范围不够 | 命中 |
| extra/HealthEquity-DotNet | fail | 84.0/fail | 摘要开头让 HR 第一眼误判；年限/层级/管理范围不够；特定平台深度不够 | 命中 |
| extra/Zoox-LLM | fail | 93.8/fail | 岗位主技术或主能力没有被真正证明 | 命中 |
| extra/Synechron-Backend | pass | 98.5/pass | P1-030；格式/强调方式影响阅读 | 命中 |
| extra/Ramp-Platform | pass | 99.2/pass | 格式/强调方式影响阅读；细节真实性需要更稳 | 命中 |
| gen2/Discord-DBInfra | fail | 93.3/fail | 岗位本身要求的底层方向不对口 | 命中 |
| gen2/AppliedIntuition-CloudInfra | pass | 96.2/pass | 岗位主技术或主能力没有被真正证明；结果数字多，但规模锚点不够 | 命中 |
| gen2/Fireblocks-SRE | pass | 96.6/pass | 摘要开头让 HR 第一眼误判；发布/配置/辅助工具写得不够 | 命中 |
| gen2/ChildrensHospital-Azure | fail | 88.6/fail | 摘要第三句/团队贴合句没价值；岗位本身要求的底层方向不对口 | 命中 |
| gen2/CapitalOne-Manager2 | fail | 90.9/fail | 年限/层级/管理范围不够 | 命中 |
| gen2/Fanduel-AnalyticsManager | fail | 85.3/fail | 岗位主技术或主能力没有被真正证明；年限/层级/管理范围不够 | 命中 |
| gen2/Geico-SWE2 | pass | 93.9/pass | 技术写得太满，像堆栈炫技 | 命中 |
| gen2/Doordash-Backend | pass | 98.0/pass | 摘要开头让 HR 第一眼误判 | 命中 |
| gen2/Cisco-NetworkingSenior | fail | 90.7/fail | 岗位本身要求的底层方向不对口；技术写得太满，像堆栈炫技 | 命中 |
| gen2/Genentech-MLInfra | pass | 96.5/pass | 格式/强调方式影响阅读；行业/团队方向桥接不够；主语言写得太散 | 命中 |
| conf/FlexTrade-SoftwareDeveloper | pass | 94.1/pass | P1-030；格式/强调方式影响阅读；摘要开头让 HR 第一眼误判 | 命中 |
| conf/Whoop-SensorIntelligence | fail | 90.4/fail | 摘要开头让 HR 第一眼误判；岗位主技术或主能力没有被真正证明 | 命中 |
| conf/Hopper-CustomerPlatform | pass | 97.0/pass | P1-030；摘要开头让 HR 第一眼误判 | 命中 |
| conf/Nuro-OffboardInfra | pass | 97.5/pass | 强调样式不稳；摘要第三句/团队贴合句没价值；结果数字多，但规模锚点不够 | 命中 |
| conf/AMH-EnterpriseDataAnalyst | pass | 93.5/pass | 技术写得太满，像堆栈炫技 | 命中 |
| conf/Phantom-SDET | pass | 91.6/fail | 岗位主技术或主能力没有被真正证明 | 误判 |
| conf/VeteransUnited-AssociateSE | pass | 82.3/fail | 摘要开头让 HR 第一眼误判；岗位主技术或主能力没有被真正证明；技能区写了，但正文没证据 | 误判 |
| conf/8451-ResearchAI | fail | 87.3/fail | 正文里有一条写得不稳/容易被追问；岗位主技术或主能力没有被真正证明 | 命中 |
| conf/Photon-AIEngineer | fail | 89.4/fail | 摘要开头让 HR 第一眼误判；岗位主技术或主能力没有被真正证明 | 命中 |
| conf/Clarivate-NLP | fail | 85.8/fail | 岗位主技术或主能力没有被真正证明；年限/层级/管理范围不够 | 命中 |

## v10 等价证据版，也是最终推荐版

| 汇总项 | 内容 |
| --- | --- |
| 本版是干嘛的 | 明确承认等价证据：比如 .NET service layer + REST/gRPC 也算 Web APIs，reusable validation pack + pytest/Playwright + CI 也算测试框架能力。 |
| 为什么会有这版 | v9 已经很接近，但还会因为死盯关键词原文误杀 VeteransUnited 这类明显该过的简历。 |
| 已测试 case 数 | 30/30 |
| 主 20 case | 命中 20/20 |
| 外部确认 10 case | 命中 9/10 |
| 平均分（已测试） | 91.7 |
| 集中扣分点 | 岗位主技术或主能力没有被真正证明 x9；年限/层级/管理范围不够 x8；技术写得太满，像堆栈炫技 x8；P2-001 @ x5；岗位本身要求的底层方向不对口 x4 |
| 这版最常漏掉的点 | 对生产敏感测试岗里的 post-mortem 证据，仍可能偏严。 |

| Case | 人工判断 | 分数/结论 | 主要扣分点 | 备注 |
| --- | --- | --- | --- | --- |
| same/Google | pass | 94.4/pass | 正文里有一条写得不稳/容易被追问 | 命中 |
| same/Amazon | fail | 89.2/fail | 年限/层级/管理范围不够；技术写得太满，像堆栈炫技 | 命中 |
| same/AWS | fail | 90.9/fail | 年限/层级/管理范围不够 | 命中 |
| same/Microsoft | fail | 90.5/fail | 岗位本身要求的底层方向不对口 | 命中 |
| extra/CapitalOne-AI | fail | 82.5/fail | 摘要开头让 HR 第一眼误判；技能和正文主题不一致；年限/层级/管理范围不够 | 命中 |
| extra/Dataminr-Infra | fail | 91.3/fail | 年限/层级/管理范围不够 | 命中 |
| extra/HealthEquity-DotNet | fail | 84.3/fail | 摘要开头让 HR 第一眼误判；年限/层级/管理范围不够；特定平台深度不够 | 命中 |
| extra/Zoox-LLM | fail | 92.8/fail | 岗位主技术或主能力没有被真正证明 | 命中 |
| extra/Synechron-Backend | pass | 99.5/pass | 格式/强调方式影响阅读 | 命中 |
| extra/Ramp-Platform | pass | 99.0/pass | 摘要第三句/团队贴合句没价值 | 命中 |
| gen2/Discord-DBInfra | fail | 88.8/fail | 岗位主技术或主能力没有被真正证明；岗位本身要求的底层方向不对口 | 命中 |
| gen2/AppliedIntuition-CloudInfra | pass | 95.3/pass | 技术写得太满，像堆栈炫技 | 命中 |
| gen2/Fireblocks-SRE | pass | 94.7/pass | 格式/强调方式影响阅读；摘要开头让 HR 第一眼误判；跨行业迁移解释不够 | 命中 |
| gen2/ChildrensHospital-Azure | fail | 85.3/fail | 岗位主技术或主能力没有被真正证明；岗位本身要求的底层方向不对口 | 命中 |
| gen2/CapitalOne-Manager2 | fail | 91.4/fail | 年限/层级/管理范围不够 | 命中 |
| gen2/Fanduel-AnalyticsManager | fail | 86.3/fail | 岗位主技术或主能力没有被真正证明；年限/层级/管理范围不够 | 命中 |
| gen2/Geico-SWE2 | pass | 95.1/pass | 强调样式不稳；摘要开头让 HR 第一眼误判；发布/配置/辅助工具写得不够 | 命中 |
| gen2/Doordash-Backend | pass | 98.0/pass | 摘要开头让 HR 第一眼误判 | 命中 |
| gen2/Cisco-NetworkingSenior | fail | 90.4/fail | 岗位本身要求的底层方向不对口 | 命中 |
| gen2/Genentech-MLInfra | pass | 98.8/pass | 技术写得太满，像堆栈炫技 | 命中 |
| conf/FlexTrade-SoftwareDeveloper | pass | 92.2/pass | P1-030；摘要开头让 HR 第一眼误判；最新经历第一条不够像主卖点 | 命中 |
| conf/Whoop-SensorIntelligence | fail | 90.7/fail | 岗位主技术或主能力没有被真正证明；技术写得太满，像堆栈炫技 | 命中 |
| conf/Hopper-CustomerPlatform | pass | 95.5/pass | P1-030；强调样式不稳；摘要开头让 HR 第一眼误判 | 命中 |
| conf/Nuro-OffboardInfra | pass | 98.1/pass | 强调样式不稳；行业/团队方向桥接不够 | 命中 |
| conf/AMH-EnterpriseDataAnalyst | pass | 91.0/pass | 技能区写了，但正文没证据 | 命中 |
| conf/Phantom-SDET | pass | 89.6/fail | 岗位主技术或主能力没有被真正证明 | 误判 |
| conf/VeteransUnited-AssociateSE | pass | 95.1/pass | 技术写得太满，像堆栈炫技 | 命中 |
| conf/8451-ResearchAI | fail | 87.8/fail | 岗位主技术或主能力没有被真正证明；技术写得太满，像堆栈炫技 | 命中 |
| conf/Photon-AIEngineer | fail | 89.7/fail | 岗位主技术或主能力没有被真正证明；技术写得太满，像堆栈炫技 | 命中 |
| conf/Clarivate-NLP | fail | 83.2/fail | 岗位主技术或主能力没有被真正证明；年限/层级/管理范围不够；技术写得太满，像堆栈炫技 | 命中 |

