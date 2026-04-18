# 30 个 Case 逐案人工判断说明

这份文件是我对当前 30 个 `简历 + JD` 样本的最终人工判断说明，使用的是**最终修订后的标签标准**，不是最早那版快速浏览标签。

最终标签文件：

- 主 20： [hr_labels_20_raw_jd_revised.json](hr_labels_20_raw_jd_revised.json)
- 外部确认 10： [hr_labels_confirmation_10_revised.json](hr_labels_confirmation_10_revised.json)

## 我是怎么判 `pass` / `fail` 的

- `pass` 不等于“这份简历完美”。它的意思是：真实世界 HR 首筛大概率愿意给下一轮，不会因为明显硬伤一眼刷掉。
- `fail` 也不等于“候选人不行”。它的意思是：以当前简历形态去投这条 JD，真实 HR 首筛很可能会卡住，或者进入下一轮的概率很不稳。
- 我主要看 5 类东西：
  - 有没有硬门槛直接不满足，例如年限、管理经验、特定研究方向、特定主技术栈。
  - 岗位主轴是不是对上了，例如是泛后端、SRE、ML infra，还是 3D vision、NLP senior、networking kernel、people manager。
  - 简历有没有把证据写出来，而不是只写几个技术词。
  - level 是否匹配，例如 Associate、Mid、Senior、Manager、specialized infra。
  - 是否只是 title 不一样但能力其实对得上。这个我不会一刀切误杀。

## 主基准 20 Case

### same/Google | Google Cloud 平台全栈 / 后端工程师

- 最终结论：`pass`
- 我为什么判过：
  - 这条 JD 真正要的是能写代码、能做系统、语言覆盖够、能进 Google 常规工程面试流程的人，不是一定要已经在简历上写出完全一样的 title。
  - 简历里已经有 `Java`、`TypeScript`、`JavaScript`、`Node.js`、`Python`、`C++`、`Go`，并且正文里有 `Kafka`、`Docker`、`Kubernetes`、`microservices`、`GitHub Actions`、测试检查这些工程证据。
  - TikTok 和 DiDi 两段都不是纯分析表格工作，已经有内部平台、后端接口、控制台、服务协作这类工程化内容，足够支持“先让他进面试看代码和系统设计”。
- 我不会因为这些点把它打成 fail：
  - 首句写了 `transitioning from data analysis`，这会让首屏变弱，但还没弱到一眼刷掉。
  - `Node.js` 不是最强主轴，但和 `Java/TypeScript/Python` 一起已经足够撑起这类泛工程岗的首筛。
- 这份简历如果要更稳：
  - 把“转行”语气降一点，把“工程交付”往第一句放。
  - 让 `Node.js` / `JavaScript` / `TypeScript` 的项目 owner 感更明显。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 79.0/fail | 92.8/pass | 94.1/pass | 86.2/fail | 94.4/pass | 91.2/pass | 90.9/pass | 94.4/pass | 98.0/pass | 94.4/pass |

**各版本分歧点**
1. `old_pipe` 把这条打成 `79.0/fail`，核心不是岗位主轴不对，而是把“技能出处一致性”和“版式强调层级”看得太重。
   对应原文翻译（old_pipe）：正文在 TikTok 项目里用了 `AWS Bedrock`，但 `Bedrock` 没出现在 Skills 中，违反了“正文里出现的技术必须在 Skills 里可追溯”的一致性要求。
   对应原文翻译（old_pipe）：`team-maintained`、`existing`、`internal` 这类限定词被错误加粗；一些关键规模数字又没有统一强调，导致版式信号不一致。

2. 后面的版本基本把它拉回到了 `pass`，因为它们看到真正还缺的只是首屏角色锚点和 Skills 闭环，不是硬门槛。
   对应原文翻译（v10）：首屏 framing 以“从 data analysis 转向 full-stack development”为中心，第一眼更像转型说明，而不是目标岗位角色锚点。
   对应原文翻译（v10）：正文用了 `AWS Bedrock`，但 Skills 里只写了 `AWS` 和 `S3`，没有把这个命名产品显式列出来，技术栈叙事不闭环。

### same/Amazon | Amazon AGI Customization MLE II

- 最终结论：`fail`
- 我为什么判不过：
  - 这条 JD 最硬的一条不是“懂不懂 LLM”，而是 `3+ years of non-internship professional software development experience`。
  - 简历自己在 summary 里写了 `2.5+ years of non-internship experience`，这等于主动把硬门槛差距亮给 HR 看。
  - 这条岗位还是 `Engineer II`，不是 entry-level；它还要 `2+ years` 的设计/架构经验。当前简历有 ML / RAG / Bedrock / evaluation 的相邻证据，但年限门槛不稳，真实 HR 很容易先卡掉。
- 为什么这不是吹毛求疵：
  - Amazon 这类岗位在首筛上经常先看写死的年限门槛，尤其是 `non-internship` 这种词都写出来了。
  - 简历如果没把这句写死，也许还能赌一把；但当前版本等于主动确认“我没满”。
- 这份简历如果要翻盘：
  - 先解决年限表达和可归类的全职软件工程经历问题。
  - 再把 “LLM customization / training / architecture” 的 owner 证据写得更硬。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 93.3/pass | 97.8/pass | 95.0/pass | 95.3/pass | 97.3/pass | 95.8/pass | 90.8/fail | 96.9/pass | 91.2/fail | 89.2/fail |

**各版本分歧点**
1. `old_pipe` 到 `v6` 大多把它当成可修的 ML/LLM 匹配问题，没有把年限当成真正的淘汰门槛，所以一直给高分。
   对应原文翻译（old_pipe）：开头先强调“从 analytics 转向 engineering”，而不是先给出最贴合目标岗的 AGI customization / MLE 信号。
   对应原文翻译（v3）：这一版看到的主要问题是：首句还是转型叙事、ML 没放在 Skills 第一行、实习段像 broad stack dumping；它并没有把年限当成硬挡板。

2. `v7` 和 `v10` 开始真正把 Amazon raw JD 里的 `3+ years non-internship` 拉成硬门槛，所以结论才稳定收敛到 `fail`。
   对应原文翻译（v7）：简历自己写明只有 `2.5+ years` 的非实习经历，而 JD 明确要求 `3+ years of non-internship professional software development experience`，这是可见的硬门槛缺口。
   对应原文翻译（v10）：简历自己写明只有 `2.5+ years` 的非实习经历，而 JD 明确要求 `3+ years of non-internship professional software development experience`，这是可见的硬门槛缺口。

### same/AWS | AWS SDE II Builder Experience / GenAI / Codex

- 最终结论：`fail`
- 我为什么判不过：
  - 这条和 Amazon 那条一样，JD 也写了 `3+ years of non-internship professional software development experience`。
  - 当前简历能看出来的软件工程 full-time 轨迹，合在一起仍然更像“约 30 个月左右”，离稳稳满足 `3+ years non-internship` 还有差距。
  - 岗位还要求 `2+ years` 设计/架构经验，以及大规模分层分布式应用经验。简历方向相邻，但年限不稳，所以首筛不该判过。
- 这条后来为什么从 `pass` 修成了 `fail`：
  - 我最早快速看时把技术方向匹配看得更重，后来回到 raw JD 才发现这条和 Amazon 一样，是写得很死的年限门槛。
- 这份简历的优点：
  - `Java/Go/C++`、分布式服务、检索工作流、系统协作都不差。
- 但最终仍然 fail 的原因：
  - 不是技术太差，而是**硬门槛不稳**。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 94.6/pass | 94.4/fail | 97.5/pass | 97.7/pass | 96.3/pass | 96.5/pass | 96.0/pass | 96.0/pass | 97.5/pass | 90.9/fail |

**各版本分歧点**
1. 大多数中间版本都把这条当成“方向对、只差首屏和 scope”的案例，所以给了很高的 `pass` 分。
   对应原文翻译（old_pipe）：旧 pipe 只抓到两类小问题：限定词加粗，以及首句先讲“从 analytics 转向 engineering”，并没有把它当成硬门槛不满足。
   对应原文翻译（v3）：如果想更像 AWS Builder Experience，只需要再补一个 team size、event volume、SLA 或 rollout scope 这类显式 scope signal；其他结构和不可变信息已经一致。

2. 只有 `v10` 最终把 AWS 这条和 Amazon 一样，按 `3+ years non-internship` 的真实 HR 门槛收成了 `fail`。
   对应原文翻译（v10）：可见的非实习专业时间线只有大约 30 个月，不能清楚满足 JD 里“3 年以上非实习软件开发经验”的要求。
   对应原文翻译（v10）：JD 还要求 3+ 年外加更高一级的 SDE II 设计/架构可信度，但最新经历主要还是百分比改善，缺少 tier-1 规模锚点。

### same/Microsoft | Azure Storage 软件工程师

- 最终结论：`fail`
- 我为什么判不过：
  - 这条不是泛后端，而是 `Azure Storage`。JD 明写 `C/C++/C#`、`2+ years distributed systems`、`2+ years on-call experience`。
  - 当前简历虽然能写出 `C++`、`C#`、后端、分布式相邻信号，但主叙事仍然不是存储系统，也没有把 on-call、storage、底层系统 owner 经验写出来。
  - 这类岗位真实 HR 首筛看的是“你是不是已经明显在这个技术带上”，而不只是“你也会这些语言”。
- 为什么我没有因为 title 不同就直接杀：
  - 如果它是普通 Azure / backend 应用工程岗，我未必会 fail。
  - 但 `Azure Storage` 更偏基础设施和系统软件，不是普通业务后端。
- 这份简历如果要翻盘：
  - 需要更硬的 `C++/C# + distributed systems + on-call` 证据。
  - 最好能有真正存储、可靠性、性能或底层服务 owner 叙事。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 88.1/fail | 90.4/pass | 90.3/fail | 95.8/pass | 95.8/pass | 91.8/fail | 78.5/fail | 84.7/fail | 87.7/fail | 90.5/fail |

**各版本分歧点**
1. `v2`、`v4`、`v5` 会给 `pass`，说明它们更相信 `C# / C++ / Kafka / gRPC / 分布式相邻信号` 已经够像 Azure 后端。
   对应原文翻译（v2）：JD 必须项里的 `Distributed Systems` 只被简历用 `Microservices`、`Kafka`、`gRPC` 间接表达，ATS 和招聘方首扫都可能读不出硬覆盖。
   对应原文翻译（v5）：这一版主要担心的是 stack stuffing 和 scope 不够硬，并没有把 Azure Storage 当成 specialized substrate role 单独处理。

2. `v10` 改判为 `fail`，是因为它把这条岗位当成了真正的 Azure Storage specialized role，而不是普通后端。
   对应原文翻译（v10）：这是一个专门的 storage/substrate 角色，但简历只展示了相邻的 backend、安全和数据经历，没有 replication、sharding、durability、checkpointing、storage path ownership 或 HA/recovery 这类直接存储系统证据。
   对应原文翻译（v10）：首句先讲“从 data analytics 转向 backend engineering”，前 6-8 秒并没有回答“为什么我适合 Azure Storage”。

### extra/CapitalOne-AI | Capital One 数据分析经理

- 最终结论：`fail`
- 先说明一件事：
  - 这个 case 名字里带 `AI`，但这条**实际不是 AI 岗**，它是 `Manager, Data Analysis - Card Services`。
- 我为什么判不过：
  - JD 要 `4+ years professional data analysis`、`4+ years programming`，更高配还希望有 `people management`。
  - 当前简历虽然数据分析底子不错，也有 Python / SQL / Spark / ETL，但总年限只有 `3+ years` 左右，且没有真正的人管人证据。
  - 这条岗位 title 是 `Manager`，真实 HR 会先看“你有没有带人、管项目、扛正式 owner scope”，而当前简历更像强 IC。
- 为什么不是因为“技术不够炫”：
  - 这条不是缺模型、缺 AI library。
  - 真正的问题是**level 和管理要求不匹配**。
- 这份简历如果要翻盘：
  - 要么投更偏 senior analyst / analytics engineer / IC data 方向。
  - 要么把真实带人、项目 owner、跨团队决策权写出来。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 89.2/fail | 95.2/pass | 87.9/fail | 88.6/fail | 91.9/fail | 96.2/pass | 90.9/fail | 92.4/fail | 85.3/fail | 82.5/fail |

**各版本分歧点**
1. 高分版本会被 `Python / SQL / Spark / ETL` 这些分析相关词带偏，以为这是一条普通 senior analyst / IC data 岗。
   对应原文翻译（v2）：这一版抓的主要是首句 framing、R 没有正文证据、以及业务迁移逻辑不够直；它没有把 manager level 当成真正的硬挡板。
   对应原文翻译（v6）：这版也一度主要纠结首屏和写法，没有把 BS+6 / MS+4 以及带人要求收成决定性问题。

2. 更稳的版本都回到 `fail`，因为它们看见了这条实际是 Manager bar，而不是单纯的数据分析相关性。
   对应原文翻译（v10）：JD 的 Manager 线要求更长的数据分析年限，而且要有 people-management / project-management 证据；当前简历只显出 3 年左右的数据分析经历，没有明确带人证据。
   对应原文翻译（v10）：简历没有把 food/security/ops analytics 明确桥接到 Capital One 的 card-services 场景，业务迁移逻辑需要招聘方自己补全。

### extra/Dataminr-Infra | Dataminr 高级后端

- 最终结论：`fail`
- 我为什么判不过：
  - JD 明写 `4+ years of experience building back end services and applications`。
  - 当前简历里后端、Kafka、微服务、分布式、实时流处理这些方向都对，但表面年限仍然更像约 `3 年左右`，还混着 internship。
  - 对 `Senior Software Engineer, Backend` 来说，这不是“小缺口”，而是会直接影响 HR 首筛稳定性的硬门槛。
- 为什么这条容易让人误会：
  - 如果只看技术词，这份简历和 Dataminr 会很像。
  - 但 Dataminr 这类 senior backend 岗位，HR 往往先看的是“你是不是已经到 senior 的时间和 owner 程度了”。
- 这份简历的真实状态：
  - 方向对，level 还差一点。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 92.8/fail | 97.4/pass | 99.0/pass | 98.5/pass | 95.5/pass | 98.5/pass | 90.7/fail | 95.8/pass | 92.9/fail | 91.3/fail |

**各版本分歧点**
1. `v2` 到 `v6` 以及 `v8` 多次给出高分，是因为它们看到的是 backend、Kafka、微服务、实时流处理这些相邻能力，而不是 senior 年限门槛。
   对应原文翻译（v3）：这一阶段主要在改首句、header 和 stack dumping；它没有把 Dataminr 的 senior backend 年限当成必须先过的门槛。
   对应原文翻译（v8）：这一版仍主要在看 backend fit、scope 和 stack 展示，没有把 4+ 年硬门槛卡死。

2. `v7`、`v9`、`v10` 才把 `4+ years building backend services` 当成真的硬门槛，所以最后稳定收成 `fail`。
   对应原文翻译（v10）：简历自述 `3+ years`，而 JD 要 `4+ years` 的 backend 服务构建经验；可见时间线大约只有 37 个月，没过硬门槛。
   对应原文翻译（v10）：最新相关段落几乎都由百分比提升主导，缺少一个明确的 tier-1 规模锚点，所以 senior 感也不够硬。

### extra/HealthEquity-DotNet | HealthEquity 软件工程师 II

- 最终结论：`fail`
- 我为什么判不过：
  - 这条 JD 不是普通 “会一点 .NET 就行”，而是写得很重：`Minimum 6 years experience`、`specific experience in the Microsoft technology stack`、`Azure App Service / API Management / Service Bus / Key Vault / Azure SQL`、`.NET / C# / SQL Server / Angular / Swagger`。
  - 当前简历虽然刻意补了 `.NET`、`ASP.NET`、`C#`、`Angular`、`Azure`、`MongoDB` 等词，也确实有一些相邻项目描述，但整体更像“做过相邻交付”，不是“长期深耕 Microsoft stack 的 6 年工程师”。
  - 年限差距太大，Azure 专项也不够实。
- 为什么不能因为它写了很多关键词就 pass：
  - 真实 HR 很容易看出“词是齐了，但主体经历不是这个栈长出来的”。
  - 这正是我后面一直在防的“看上去很唬人就放过”。
- 这份简历如果要翻盘：
  - 需要真正的微软栈主线，而不是把相邻技术拼出来。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 93.5/pass | 88.8/pass | 89.6/fail | 88.6/pass | 97.0/pass | 94.5/pass | 81.5/fail | 86.8/fail | 84.0/fail | 84.3/fail |

**各版本分歧点**
1. 早期高分版本更像是被 `.NET / ASP.NET / C# / Angular / Azure` 这些词拼出来的表面匹配带偏了。
   对应原文翻译（v2）：这一版只把“岗位主技术或主能力没有被真正证明”作为一般性提醒，但仍然给了 `90.4/pass` 这一类高分思路。
   对应原文翻译（v5）：这一版也没有把 Microsoft stack 深度和 6 年门槛压成足够重的 fail。

2. `v7` 以后稳定转成 `fail`，因为后期版本终于把“6 年微软栈 + 命名 Azure 服务深度”当成了岗位定义级要求。
   对应原文翻译（v10）：JD 要至少 6 年软件开发经验，但简历可见时间线只有大约 4.5 年，而且 summary 自己也只写 `3+ years`，这对 Software Engineer II 是明显的级别错配。
   对应原文翻译（v10）：JD 反复点名 `Azure App Service`、`API Management`、`Service Bus`、`Application Insights`、`Gateway`、`Event Grid`、`Key Vault`、`Azure SQL`、`Azure DevOps Services`，但简历只有泛化的 `Azure` 提法，没有这些服务的直接 owner 证据。

### extra/Zoox-LLM | Zoox 3D Simulation 机器学习工程师

- 最终结论：`fail`
- 我为什么判不过：
  - 这条岗位最核心的词不是 `ML`，而是 `3D simulation`、`radiance field`、`human-centric 3D vision`、`3D reconstruction`、`style transfer`。
  - 当前简历虽然有 `Python`、`C++`、ML evaluation、feature extraction、RAG、Bedrock 等内容，但这是一条**通用 ML/后端**轨迹，不是 3D vision / 3D simulation 轨迹。
  - 真实 HR 首筛看见这种 specialized 研究/工程方向，通常不会因为你泛 ML 不错就放过。
- 这不是“太严格”：
  - 3D 方向不是可有可无的加分项，而是岗位定义本身。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 94.4/pass | 96.8/pass | 96.8/pass | 96.4/pass | 96.5/pass | 98.6/pass | 91.5/fail | 91.4/fail | 93.8/fail | 92.8/fail |

**各版本分歧点**
1. 旧 pipe 到 `v6` 都把它当成泛 ML / backend 工程岗，所以只要看到 `Python`、`C++`、ML evaluation、feature extraction 就给高分。
   对应原文翻译（old_pipe）：旧 pipe 对这条基本没有提出岗位主轴层面的质疑，说明它把 Zoox 读成了普通 ML 工程岗。
   对应原文翻译（v3）：这一阶段主要还是在看 stack breadth、summary 和写法，没有把 3D simulation / radiance field 当成硬门槛。

2. `v7` 以后稳定转成 `fail`，因为后期版本把 3D 方向看成了岗位定义本身，而不是可有可无的加分项。
   对应原文翻译（v10）：JD 要的是 radiance-field、human-centric 3D vision、3D reconstruction、style transfer；而简历只有 backend/data/security ML 系统经历，没有 3D simulation / reconstruction / radiance-field 的桥接证据。
   对应原文翻译（v10）：这段实习经历把 Go、Python、C++、Java 都写成了日常主栈，对一个实习段来说 breadth 过宽，也削弱了 3D 主线的可信度。

### extra/Synechron-Backend | Python Fullstack

- 最终结论：`pass`
- 我为什么判过：
  - JD 要 `Python backend`、`Java SpringBoot`、`React.js`、关系型/NoSQL 数据库、`microservices`。
  - 这份简历里虽然 SpringBoot 不是最强直给词，但 `Python`、`Java`、内部平台、控制台、`React`、SQL/NoSQL、微服务这些能力都能从 summary、skills 和经历里拼成完整证据链。
  - 这是典型的泛业务全栈 / 后端岗，真实 HR 更看“能不能做”，不会像研究岗或底层 infra 岗那样卡得那么死。
- 这份简历为什么不是完美但仍该 pass：
  - 首屏仍然有一点“从 analytics 转过来”的味道。
  - 但只要能力轴对上、没有明显硬伤，就应该先给面试机会。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 89.5/fail | 95.0/pass | 99.2/pass | 100.0/pass | 100.0/pass | 99.7/pass | 99.5/pass | 100.0/pass | 98.5/pass | 99.5/pass |

**各版本分歧点**
1. 这条的主分歧几乎都来自 `old_pipe`。旧 pipe 把 summary 结构、Skills 分类和版式统一看得过重，所以把本来应过的通用 fullstack/backend 样本打成了 `fail`。
   对应原文翻译（old_pipe）：旧 pipe 主要抓的是 summary 结构、Skills 分类和版式统一，而不是岗位主轴本身。
   对应原文翻译（old_pipe）：它给的优先修改项是“把 Summary 改成严格的 3 句 labeled format，并清理 Skills 分类与加粗方式”，而不是说岗位主轴不匹配。

2. 从 `v2` 开始，各版本几乎一直给 `pass`，说明后续 reviewer 更能识别这是一条技术对口的泛业务全栈/后端样本。
   对应原文翻译（v10）：后期版本仍会抓首句转型叙事和 stack 主线清晰度，但没有把这条当成岗位硬错配。
   对应原文翻译（v10）：这类岗位最常见的问题被收敛成“首屏锚点不够强”而不是“技术方向不对”。

### extra/Ramp-Platform | Ramp Infrastructure

- 最终结论：`pass`
- 我为什么判过：
  - JD 要 `2+ years`、云上生产经验、`Infrastructure-as-Code`、解决 customer requirement 的能力。
  - 当前简历已经有 `Go/Python` 服务、`Kafka/Redis/PostgreSQL/MySQL/Docker/Kubernetes/Terraform`、平台交付和运维流程经验，这些对基础设施岗是有效信号。
  - 这类岗位不一定要求你过去 title 就叫 infrastructure engineer，只要生产平台和交付能力够硬，HR 会给机会。
- 风险点：
  - `Terraform` 和 IaC 的 owner 叙事如果再强一点，会更稳。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 97.0/pass | 95.8/fail | 97.1/pass | 100.0/pass | 100.0/pass | 97.3/pass | 98.5/pass | 99.5/pass | 99.2/pass | 99.0/pass |

**各版本分歧点**
1. 从表里看，除了 `v2` 一次误杀，这条从中后期开始几乎一直是 `pass`。也就是说，各版本对它的主分歧很小。
   对应原文翻译（v2）：v2 一度把它打成 fail，更像是早期聚合规则偏保守，而不是发现了新的岗位硬伤。
   对应原文翻译（v10）：这条从中后期开始几乎一直被当作 pass，剩下的只是首句转型叙事和 scope 强弱，而不是岗位错配。

2. 后期版本留下来的主要只是首句转型叙事和 scope 强弱问题，而不是平台/基础设施岗位错配。
   对应原文翻译（v10）：这类 case 到后面没有出现“必须项缺失”或“specialized domain 错配”的 finding，说明 reviewer 也把它当成基础设施方向的可过样本。

### gen2/Discord-DBInfra | Discord 数据库基础设施

- 最终结论：`fail`
- 我为什么判不过：
  - 这条岗位不是“会 Go / Rust / 分布式”就行，它要的是 `database infrastructure`、`complex systems in production`、`concurrency control fundamentals`、底层服务 owner 感。
  - 当前简历虽然有后端和分布式系统相邻信号，但缺少数据库内核、存储系统、高可用数据面、并发控制这类核心叙事。
  - 所以这条 fail 的原因不是“没写 Rust”这么简单，而是**专业方向差了一层**。
- 这类 case 是我一直特别注意的：
  - 不能把“泛 infra 工程师”误判成“数据库基础设施工程师”。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 82.7/fail | 未测试 | 92.9/fail | 未测试 | 93.9/fail | 92.9/fail | 90.6/fail | 94.4/fail | 93.3/fail | 88.8/fail |

**各版本分歧点**
1. 这条从旧 pipe 到 `v10` 基本都判 `fail`，真正的分歧不在结论，而在“为什么 fail”。
   对应原文翻译（old_pipe）：旧 pipe 的修改建议一度会把问题说成“先补一个真实的 Rust 证据”，这会把主问题缩窄成单一技术词缺失。
   对应原文翻译（v10）：JD 明确点了 Rust，但简历既没有 Rust，也没有任何 database infrastructure 的直接 artifact。

2. 后期版本对失败原因的解释更接近真实 HR：不是只缺一个词，而是缺数据库基础设施这条主线。
   对应原文翻译（v10）：Database Infrastructure 是 specialized substrate role，但简历只有相邻的 backend/data/platform 经验，没有 HA、replication、query path、storage path 或生产数据库 owner 证据。

### gen2/AppliedIntuition-CloudInfra | Applied 云基础设施

- 最终结论：`pass`
- 我为什么判过：
  - JD 要 `3+ years` infra / monitoring / large-scale product 经验，以及 shell 脚本到高阶语言的工程能力。
  - 当前简历有 `Go/Java/Python` 服务、release tooling、云平台、容器、部署、平台运维流程，和 cloud infra 的主轴是对上的。
  - 这类岗位需要“能上手基础设施和发布运营”，而不是必须已有某家云厂 infra title。
- 风险点：
  - monitoring / observability 的证据如果再多一点，会更稳。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 93.8/pass | 未测试 | 96.5/pass | 未测试 | 100.0/pass | 96.3/pass | 97.0/pass | 90.9/fail | 96.2/pass | 95.3/pass |

**各版本分歧点**
1. 从表里看，这条在大多数版本里都是 `pass`，说明 cloud infra 主轴本身并没有争议；唯一大的回退是 `v8`。
   对应原文翻译（v10）：后期版本只是在提醒首句转型叙事和 stack 主线清晰度，而没有把岗位本身判成错配。
   对应原文翻译（v8）：v8 一度因为把多套技术并列和 tier-1 scope 不足读得过重，误把 cloud infra 方向样本打成 fail。

2. `v8` 的误杀说明那一版把“多套技术并列”和“tier-1 scope 不足”读得太重，压过了真正的 cloud infra 对口性。
   对应原文翻译（v8）：同一份简历里把多套编程语言和开发栈都写成了使用级证据，读起来更像堆栈堆砌，而不是一条云基础设施主线。
   对应原文翻译（v8）：最新相关经历几乎都由百分比改进组成，缺少更能支撑可信度的 tier-1 规模/边界信号。

### gen2/Fireblocks-SRE | Fireblocks SRE

- 最终结论：`pass`
- 我为什么判过：
  - JD 很看重 `Python/JavaScript/Bash`、monitoring/alerting、Linux、cloud、Docker/Kubernetes、生产意识。
  - 当前简历明确写了 `Linux`、`Bash`、`Shell`、`Prometheus`、`AWS`、`Azure`、`Docker`、`Kubernetes`、`Git`，正文还有告警、发布、回滚、指标、稳定性这类内容。
  - 它不是标准传统 SRE 履历，但已经足够像“偏后端、偏可靠性、能和生产系统打交道的人”，真实 HR 应该会给下一轮。
- 为什么我没有因为 `3+ years as SRE` 这句直接 fail：
  - 因为这类 JD 常把相邻 infra/backend/reliability 经验也算进去。
  - 当前简历已经给出了足够多 production-aware 证据，不属于明显错投。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 96.1/pass | 未测试 | 98.0/pass | 未测试 | 95.6/pass | 96.5/pass | 91.4/fail | 92.8/pass | 96.6/pass | 94.7/pass |

**各版本分歧点**
1. 绝大多数版本都把这条当成 `pass`，说明 reviewer 普遍认可它具备 reliability / monitoring / release / cloud 这条可迁移主线。
   对应原文翻译（v10）：后期版本只剩“首句转型叙事”和“业务场景桥接不够圆”这类问题，没有把它判成 SRE 硬错配。
   对应原文翻译（old_pipe）：旧 pipe 也把它当成通过样本，说明基础的 SRE / infra 方向信号是被识别出来的。

2. 唯一显著回退是 `v7`，它把 raw JD 收得太死，低估了相邻 backend/reliability 证据对 SRE 首筛的可迁移性。
   对应原文翻译（v7）：这一阶段更容易把 `3+ years as SRE` 读成必须逐字满足，而不是把相邻 infra/backend/reliability 经验折算进去。
   对应原文翻译（v10）：简历展示了稳定性、监控、发布和运营工具能力，但没有把这些经历明确桥接到 Fireblocks 的 secure digital-asset / blockchain 业务场景。

### gen2/ChildrensHospital-Azure | Azure Software Engineer Professional

- 最终结论：`fail`
- 我为什么判不过：
  - 这条岗位名字就写得很直：`Azure Software Engineer`。
  - 当前简历的主体仍是泛后端、内部工具、数据和服务协作，只是有一些 Azure 相邻词，缺少真正以 Azure 为主平台的交付主线。
  - 真实 HR 很容易觉得“你可以做很多工程事，但不是我现在要的 Azure 主力工程师”。
- 这不是因为 title 不同就卡：
  - 如果只是一般 backend role，不一定 fail。
  - 但这条要的是 Azure 主体经验。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 87.7/fail | 未测试 | 93.3/pass | 未测试 | 93.0/pass | 94.3/pass | 86.4/fail | 89.4/fail | 88.6/fail | 85.3/fail |

**各版本分歧点**
1. `v3`、`v5`、`v6` 会给 `pass`，说明它们更相信 Azure 相邻词和通用后端/fullstack 经历已经足以桥接。
   对应原文翻译（v3）：中期版本更常把这类 case 看成“首句、scope、stack 主线还有优化空间”，而不是 Azure 平台错配。
   对应原文翻译（v5）：这一阶段并没有把 Azure 平台 artifact 当成必须出现的硬证据。

2. `v10` 回到 `fail`，因为它把这条岗位理解成真正的 Azure 平台工程岗，而不是一般的应用开发岗。
   对应原文翻译（v10）：JD 核心技能明确包含 C# 和 Azure，但简历正文和 Skills 都没有 C# / Azure 的实质使用证据；现在能看到的更多是 Node.js、React、Angular 和通用云/容器栈。
   对应原文翻译（v10）：岗位是专门的 Azure Software Engineer Professional，但正文呈现的是通用全栈/后台交付和 GCP 经验，没有 Azure 平台 artifact、service ownership 或平台深度证据。

### gen2/CapitalOne-Manager2 | Capital One 数据分析经理

- 最终结论：`fail`
- 我为什么判不过：
  - 和前面的 Capital One 一样，这条核心不是“会不会分析”，而是 manager level。
  - JD 要求的是更长的数据分析年限和正式 people management / owner scope。
  - 当前简历主要体现的是强执行、强跨职能、强交付，但不是“明确带团队的 manager”。
- 这条 fail 的本质：
  - **级别不匹配**，不是能力一无是处。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 92.6/fail | 未测试 | 90.2/fail | 未测试 | 90.9/fail | 89.9/fail | 86.3/fail | 85.8/fail | 90.9/fail | 91.4/fail |

**各版本分歧点**
1. 高分版本会被 `Python / SQL / Spark / ETL` 这些分析相关词带偏，以为这是一条普通 senior analyst / IC data 岗。
   对应原文翻译（v2）：这一版抓的主要是首句 framing、R 没有正文证据、以及业务迁移逻辑不够直；它没有把 manager level 当成真正的硬挡板。
   对应原文翻译（v6）：这版也一度主要纠结首屏和写法，没有把 BS+6 / MS+4 以及带人要求收成决定性问题。

2. 更稳的版本都回到 `fail`，因为它们看见了这条实际是 Manager bar，而不是单纯的数据分析相关性。
   对应原文翻译（v10）：JD 的 Manager 线要求更长的数据分析年限，而且要有 people-management / project-management 证据；当前简历只显出 3 年左右的数据分析经历，没有明确带人证据。
   对应原文翻译（v10）：简历没有把 food/security/ops analytics 明确桥接到 Capital One 的 card-services 场景，业务迁移逻辑需要招聘方自己补全。

### gen2/Fanduel-AnalyticsManager | FanDuel Analytics Manager

- 最终结论：`fail`
- 我为什么判不过：
  - JD 明写 `1+ years managing and coaching analysts, data scientists and/or data engineers`。
  - 当前简历没有直接的人管理证据，也没有清楚写出“带人、绩效、培养、分工、招聘”这类 manager 证据。
  - 即便分析能力本身不错，真实 HR 仍然很可能在首筛先卡掉。
- 为什么我不会因为“有 data lead 字样”就放过：
  - `data lead within a 13-person squad` 更像项目中的分析负责人，不等于正式 people manager。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 93.8/pass | 未测试 | 94.7/pass | 未测试 | 89.0/fail | 89.0/fail | 83.3/fail | 85.8/fail | 85.3/fail | 86.3/fail |

**各版本分歧点**
1. `old_pipe` 和 `v3` 会给 `pass`，说明它们把 `data lead`、跨团队协作和 analytics 主线误读成了管理经验。
   对应原文翻译（old_pipe）：旧 pipe 并没有抓住“1+ years managing and coaching analysts”这条 manager 硬门槛，所以给了 `93.8/pass`。
   对应原文翻译（v3）：v3 也没有把 people-management 当成结构性缺口，而是更关注写法、首屏和 stack 展示。

2. `v5` 以后结论稳定回到 `fail`，因为后面的版本终于把 people-management 当成了首筛必须先过的条件。
   对应原文翻译（v10）：JD 要 5+ 年相关经验，还要至少 1 年管理/辅导分析师、数据科学家或数据工程师；当前简历可见时间线更接近 3 年加一段实习，而且没有 people-management 证据。
   对应原文翻译（v10）：即便分析能力本身不错，没有“带人、绩效、培养、分工、招聘”这类 manager 证据，真实 HR 也很难先放过去。

### gen2/Geico-SWE2 | GEICO Software Engineer II

- 最终结论：`pass`
- 我为什么判过：
  - JD 要至少两门现代语言、面向对象设计、微服务、REST API。
  - 当前简历有 `Golang/Java/C++/Python/C#` 中多门语言，且有 `micro-services`、`REST APIs`、code review、云和服务发布经验。
  - 这是比较典型的泛软件工程 II 岗位，只要工程基础够、没有明显硬伤，就应该过首筛。
- 风险点：
  - 首屏依然可以更工程化一点，少一点“转型说明”。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 91.7/fail | 未测试 | 97.0/pass | 未测试 | 96.5/pass | 96.3/pass | 92.4/fail | 96.6/pass | 93.9/pass | 95.1/pass |

**各版本分歧点**
1. 从表里看，这条在大多数版本里都应该是 `pass`；真正的异常是 `old_pipe` 和 `v7`。
   对应原文翻译（old_pipe）：旧 pipe 当时更容易被 Skills 分类和格式问题拖低，所以把本来应过的 SWE II 样本误伤成了 fail。
   对应原文翻译（v7）：v7 一度把 raw JD 收得过紧，连这类泛 SWE II 也因为首屏转型叙事和 scope 不够硬而误杀。

2. 稳定版本之所以把它判过，是因为语言、REST API、分布式、code review 和云发布这条泛 SWE II 证据链是成立的。
   对应原文翻译（v10）：后期版本对这条更多是提醒首屏别先讲转型，而不是说岗位主轴不对。

### gen2/Doordash-Backend | DoorDash 泛后端

- 最终结论：`pass`
- 我为什么判过：
  - JD 要 `2+ years backend`、service-oriented architecture、`REST API`、unit testing、架构设计。
  - 当前简历的后端、微服务、`REST`、`SQL/NoSQL`、服务发布、内部工具、测试和发布流程都比较完整。
  - 这类岗位的关键不是某个单独框架，而是有没有真实后端交付证据。当前简历有。
- 风险点：
  - 如果能再多一点“性能/稳定性/服务 owner”叙事，会更像更强的 backend profile。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 94.4/pass | 未测试 | 96.0/pass | 未测试 | 97.0/pass | 96.3/pass | 95.8/pass | 97.0/pass | 98.0/pass | 98.0/pass |

**各版本分歧点**
1. 从表里看，这条几乎从头到尾都是 `pass`，说明各版本对它的岗位主轴判断基本一致。
   对应原文翻译（v10）：这条到后期只剩首句仍然先讲“从 analytics 转过来”，削弱 backend 角色锚点。

2. 版本间分数波动主要反映的是谁对首屏 framing 更严格，而不是谁认为它不适合 backend。
   对应原文翻译（v10）：首句把“transitioning from analytics”放在前台，首屏更像转型说明而不是 backend 定位。

### gen2/Cisco-NetworkingSenior | Cisco Networking Technologies 高级工程师

- 最终结论：`fail`
- 我为什么判不过：
  - JD 明写 `C/C++`、`Python automated test suites for kernel module validation`、`Linux` debugging、`TCP/IP`、routers、switches、NPUs。
  - 当前简历虽然有 `C++`、Linux、验证、自动化等相邻信号，但没有真正网络系统、协议、内核模块验证、交换路由设备这条主线。
  - 这不是普通 backend，而是明显更偏 networking systems 的 specialized 岗。
- 这条不能宽松：
  - 如果泛后端也能过这条，那 reviewer 就已经偏离真实 HR 视角了。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 91.8/fail | 未测试 | 96.8/pass | 未测试 | 95.8/pass | 96.5/pass | 92.4/fail | 85.8/fail | 90.7/fail | 90.4/fail |

**各版本分歧点**
1. `v3`、`v5`、`v6` 一度会给 `pass`，说明这些版本把 `C++ / Linux / 自动化验证` 这种相邻信号看得太重。
   对应原文翻译（v3）：中期版本更容易把这条看成“技术相邻、首屏和 stack 主线还能再收”的 case，而不是 specialized networking role。
   对应原文翻译（v5）：这阶段主要担心 stack stuffing 和 scope，不足以把 networking 主轴缺口打成 fail。

2. `v10` 回到 `fail`，是因为后期版本把 Cisco 这条读成了真正的 networking technologies specialized role。
   对应原文翻译（v10）：Cisco 这条是 specialized networking role，但简历只有相邻的 backend/security/data 工作和泛化的验证语言，没有 IOS-XR、router/switch、TCP/IP、NPU 或 kernel-module ownership 证据。
   对应原文翻译（v10）：最新经历几乎全是时间缩短、误报下降、回滚率下降这类 tier-2 结果，没有 tier-1 scope marker 来支撑 senior networking credibility。

### gen2/Genentech-MLInfra | Genentech ML Infrastructure

- 最终结论：`pass`
- 我为什么判过：
  - JD 要 `2-3 years industry experience`、`AWS` infra、`Python` 加编译型语言、Git、跨团队合作。
  - 当前简历在年限上是够的，而且明显给出了 `AWS/S3`、`Python/Go/C++/Rust/Java/Scala`、ML evaluation、RAG workflow、deployment、Git、replay / regression / infrastructure 相关证据。
  - 这条更像“ML infra 工程能力 + 云上交付能力”的组合，不要求纯研究背景。当前简历形成了可接受闭环。
- 风险点：
  - 如果投 senior 档，会稍微悬；但作为这个范围内的首筛，应该 pass。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 95.9/pass | 未测试 | 96.4/pass | 未测试 | 96.5/pass | 95.7/pass | 98.3/pass | 96.8/pass | 96.5/pass | 98.8/pass |

**各版本分歧点**
1. 从表里看，这条几乎全程都是 `pass`，后期版本只是在同一个结论上越打越稳。
   对应原文翻译（old_pipe）：旧 pipe 就已经把它判成 pass，说明基础的 ML infra / AWS / 编程语言闭环是被看见的。
   对应原文翻译（v10）：后期版本越来越能识别出 `AWS + Python/Go/C++/Rust + ML infra/replay/evaluation` 这一整条闭环证据，所以分数更稳、更高。

2. 后期分数更高，不是标准变松了，而是 reviewer 更能识别这条简历里 `AWS + Python/Go/C++/Rust + replay/evaluation` 的成套证据。
   对应原文翻译（v10）：后期版本越来越能识别出 `AWS + Python/Go/C++/Rust + ML infra/replay/evaluation` 这一整条闭环证据，所以分数更稳、更高。

## 外部确认 10 Case

### conf/FlexTrade-SoftwareDeveloper | FlexTrade 后端开发

- 最终结论：`pass`
- 我为什么判过：
  - JD 要 `2-4 years backend`、`Golang`、`Docker`、`AWS`、`Linux`、shell scripting。
  - 当前简历对 `Go`、`AWS`、容器、后端、Linux/Bash/Shell 这些点覆盖很直接。
  - 这是非常典型的“技术对口、级别也对口”的 pass 样本。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 未测试 | 未测试 | 90.6/fail | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 94.1/pass | 92.2/pass |

**各版本分歧点**
1. `v3` 把它误判成 `fail`，本质上是把“必须显式写出 Distributed Systems”和“行业桥接必须特别直白”读得太死了。
   对应原文翻译（v3）：JD 必须项 `Distributed Systems` 只被间接暗示为 `distributed service environment`，没有被明确写进 Skills。
   对应原文翻译（v3）：简历没有把经历桥接到 FlexTrade 的 `high performance execution / order management` 方向，读起来像通用后端而不是交易系统候选人。

2. `v9` 和 `v10` 把它拉回 `pass`，说明后期版本更愿意承认这类通用后端能力对 FlexTrade 是真实可迁移的。
   对应原文翻译（v10）：简历是通用 backend + 数据分析迁移叙事，但没有明确把经历桥接到 FlexTrade 的高性能 OMS / execution-management 方向，所以行业迁移逻辑还没讲圆。
   对应原文翻译（v10）：这一版仍提醒首句偏“analytics-to-engineering”桥接叙事、首条 bullet 缺少 tier-1 scope，但没有再把这些问题升级成 fail。

### conf/Whoop-SensorIntelligence | WHOOP 传感器智能 / 信号处理

- 最终结论：`fail`
- 我为什么判不过：
  - JD 真正要的是 `signal processing`、`time-series data`、`filters / FFT / peak detection / windowing`、wearable biosignals。
  - 当前简历主线是软件工程、数据分析、验证、服务和 ML 相邻能力，不是生理信号处理或可穿戴设备算法。
  - 即便候选人聪明、泛能力强，这条岗位在真实 HR 首筛里也太偏专业，不该放过。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 未测试 | 未测试 | 94.0/pass | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 90.4/fail | 90.7/fail |

**各版本分歧点**
1. `v3` 会给 `pass`，说明它只看到了“转型叙事偏重”和“业务场景桥接不够直”，没有把 WHOOP 的 signal-processing / wearable 门槛读成硬要求。
   对应原文翻译（v3）：v3 当时只看到了“迁移叙事偏重”和“没有把 marketplace/security/mobility 经验桥接到 WHOOP 场景”这类泛问题，没有把 signal processing / wearable domain 当成硬门槛。
   对应原文翻译（v3）：它还把 TensorFlow、Keras、PyTorch、scikit-learn 同时写在一条里，当成 stack stuffing 风险，而不是领域门槛缺失。

2. `v9`、`v10` 稳定改成 `fail`，因为后期版本终于把 WHOOP 这条真正的 domain baseline 抓住了。
   对应原文翻译（v10）：简历没有 WHOOP 这条最核心的 sensor-intelligence baseline：signal processing、time-series、wearable biosignals、C 或 statistical inference；读起来更像 backend/data/ML 和 retrieval tooling。
   对应原文翻译（v10）：一条 bullet 同时堆 TensorFlow、Keras、PyTorch、scikit-learn，会更像框架点名，而不是具体的 signal-processing 工作流。

### conf/Hopper-CustomerPlatform | Hopper 客户体验平台高级工程师

- 最终结论：`pass`
- 我为什么判过：
  - JD 要 `3+ years`、大规模分布式系统或 customer-facing applications、前后端、API、云基础设施。
  - 当前简历有 `TypeScript/Node.js/Python/React`，也有内部平台、服务工作流、API、控制台、运维和协作证据。
  - 这类 customer platform 岗位更重全链路交付能力。当前简历虽然 senior 表达还可以更强，但到首筛应当能过。
- 风险点：
  - 如果面试再往上走，可能会问更重的 customer-facing scale ownership。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 未测试 | 未测试 | 97.5/pass | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 97.0/pass | 95.5/pass |

**各版本分歧点**
1. 从表里看，这条在已测试版本里一直是 `pass`，说明各版本对它的岗位主轴判断基本一致。
   对应原文翻译（v3）：v3 虽然会提醒 senior 感和写法，但并没有把 customer platform 方向判成错配。
   对应原文翻译（v10）：v10 只抓 summary 是 noun-phrase 标签、首句先讲转型、以及 senior 量化锚点还不够强。

2. 版本分歧主要只剩“能不能更像 senior”，而不是“适不适合 customer platform”。
   对应原文翻译（v10）：最新经历大多是战术性的百分比改进和 turnaround 缩短，规模信号有但不算特别强，所以更像“能过首筛但 senior 感还可以更强”。

### conf/Nuro-OffboardInfra | Nuro Offboard Infrastructure

- 最终结论：`pass`
- 我为什么判过：
  - JD 要 `2+ years` 相关工业经验，再加 `Python/C++/Go`、distributed systems、data/infrastructure。
  - 当前简历在语言和 infra 方向上非常对口，且有后端、分布式、数据/系统协作的交集。
  - 这不是“机器人算法岗”，而是 offboard infrastructure，所以当前简历足够构成 pass。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 未测试 | 未测试 | 94.6/pass | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 97.5/pass | 98.1/pass |

**各版本分歧点**
1. 从表里看，这条在已测试版本里一直都是 `pass`，说明 Python/C++/Go + 分布式 + 基础设施这条主线是被 reviewer 稳定识别出来的。
   对应原文翻译（v10）：后期版本只提醒量化信号没有统一高亮，以及从 backend + security/data + infrastructure 到 Nuro offboard/autonomy 的桥接还可以更直。

2. 后期版本之所以还能给很高分，是因为它们把这些问题都当成“迁移逻辑可加强”，而不是岗位主轴错配。
   对应原文翻译（v10）：简历主线更像 backend + security/data + infrastructure，但没有把这条线明确桥接到 Nuro 的 offboard infrastructure / simulation / autonomy 方向。

### conf/AMH-EnterpriseDataAnalyst | AMH 企业数据分析师

- 最终结论：`pass`
- 我为什么判过：
  - JD 要 `3 years` Business Intelligence / Analytics / Financial Reporting / Data Warehousing。
  - 当前简历的数据分析主轴、SQL、ETL、运营指标、报表质量、跨团队决策支持都非常贴这类岗位。
  - 这是 30 个 case 里非常标准的一条 pass，不存在什么需要硬拗的地方。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 未测试 | 未测试 | 98.0/pass | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 93.5/pass | 91.0/pass |

**各版本分歧点**
1. 从表里看，这条在已测试版本里一直都是 `pass`，说明 reviewer 整体认可它的数据分析主轴。
   对应原文翻译（v3）：v3 就已经给了高分 pass，说明 enterprise data analyst 的主方向没有争议。
   对应原文翻译（v10）：v10 仍然给 pass，虽然它开始更严格地追 Excel/BI 和 financial reporting 桥接。

2. 后期版本更保守的地方在于：它开始追问 Excel/BI 工具和财务报表桥接，但还没有严重到直接 fail。
   对应原文翻译（v10）：JD 明确要求 intermediate Excel，并偏好 Power BI / Tableau，但简历正文没有任何可核验的 Excel、报表、仪表盘或 BI 工具使用证据。
   对应原文翻译（v10）：AMH 这条岗位核心是 BI、financial reporting、requirements gathering 和 stakeholder reporting，但简历首屏和前两段经历更像后端/安全/数据管道叙事，分析岗桥接不够直。

### conf/Phantom-SDET | Phantom 钱包平台 SDET

- 最终结论：`pass`
- 我为什么判过：
  - JD 最关键的词是：`Python / TS / JS / Go`、`build test frameworks from scratch`、API testing、SQL test data、CI、flakiness、cloud、incident prevention。
  - 当前简历虽然不是传统 QA/SDET title，但正文给出了 `pytest`、`Playwright`、`GitHub Actions`、`GitLab CI`、`REST/gRPC`、`SQL validation`、`reusable validation pack`、`flaky rate`、API harness、分布式系统验证这些非常接近的证据。
  - 对真实 HR 来说，这种“强质量工程 + 自动化 + API + CI + 测试框架相邻 owner”是可以进下一轮验证的，不该一眼刷掉。
- 为什么它不是 `fail`：
  - 我承认它在 “从零搭框架” 和 “incident post-mortem ownership” 上还不算完美。
  - 但它已经明显超出“只是给现成测试套件补几条 case”那种弱证据了，所以首筛应过。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 未测试 | 未测试 | 95.5/pass | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 91.6/fail | 89.6/fail |

**各版本分歧点**
1. `v3` 给出 `95.5/pass`，说明那一版认为“可复用验证包 + pytest/Playwright + CI/API testing”已经足够构成 SDET 首筛的相邻证据。
   对应原文翻译（v3）：v3 看到的是 `reusable validation pack`、`pytest`、`Playwright`、`GitHub Actions`、`GitLab CI`、`REST/gRPC` 和 API 验证这条线，所以把它当成可以进下一轮核验的 SDET 相邻证据。
   对应原文翻译（v3）：它真正抓的主要是：summary 小标题偏 trait-led、首句还是转型叙事、以及业务场景还没显式桥到 wallet / financial correctness。

2. `v9` 和 `v10` 改成 `fail`，因为后期版本把“从零搭测试框架”和 incident prevention / post-mortem ownership 读得更硬。
   对应原文翻译（v10）：JD 明确要求参与或拥有 incident post-mortem 并给出具体预防措施，但简历没有任何可见证据。
   对应原文翻译（v10）：最新且最相关经历的开头仍偏百分比改善叙事，tier-1 规模/边界信号不够靠前，首屏可信度主要靠 tier-2 指标支撑。

### conf/VeteransUnited-AssociateSE | Veterans United Associate SE

- 最终结论：`pass`
- 我为什么判过：
  - JD 要 `CI/CD`、`Web APIs`、`microservice architecture`、`C#/.NET`、`TypeScript/Angular`、数据库、Agile。
  - 当前简历已经给出 `.NET / ASP.NET / C# / Angular / TypeScript / SQL / MongoDB / CI/CD / Git / Unit Testing`，并且在 DiDi 项目里有实际服务层和前端控制台描述。
  - 这条还是 `Associate` 级别，不是 senior。对这类 entry / associate 岗位来说，当前证据已经足够。
- 为什么我没有因为没写具体 AI coding assistant 就 fail：
  - 那条更像偏好项或工作方式偏好，不应该压过主体工程匹配。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 未测试 | 未测试 | 95.8/pass | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 82.3/fail | 95.1/pass |

**各版本分歧点**
1. `v9` 的 `82.3/fail` 是一次明显误杀：它把 AI coding assistant 和 Web APIs / microservice 的显式点名看得过硬。
   对应原文翻译（v9）：JD minimum qualification 明确要求 AI coding assistant 经验，例如 Windsurf、ChatGPT、Copilot 或 Cursor，但 v9 看到简历里没有点名任何一个，也没有使用场景描述。
   对应原文翻译（v9）：JD core skills 反复指向 `Web APIs` 和 `microservice architecture`，但 v9 认为简历只给了 `.NET service`、`gRPC`、内部控制台这些相邻信号，没有直接把 API / 微服务工作讲明白。

2. `v10` 把它拉回 `95.1/pass`，说明后期版本开始承认 `.NET / ASP.NET / C# / Angular / TypeScript / service-layer` 可以构成这条 Associate 岗位的等价证据。
   对应原文翻译（v10）：v10 仍提醒：这份简历没有把 security、ops、support workflow 经验显式桥接到 Veterans United 的 home-loan / customer-operations 方向，行业迁移逻辑需要 HR 自己补。
   对应原文翻译（v10）：这条到 v10 仍会提醒首句先讲“trajectory / transitioning from data analytics”，以及 `APIs` 作为分类标题过于笼统，但这些都没有再压过岗位主体匹配。

### conf/8451-ResearchAI | 8451 Research AI / Agentic Systems

- 最终结论：`fail`
- 我为什么判不过：
  - JD 明写 `agentic systems`、`multi-step reasoning systems`、`research agents`、`RLHF`、agent design patterns。
  - 当前简历虽然有 LLM / ML engineering / evaluation / RAG，但更偏工程实现和应用层，不是 research-agent 或 RLHF 路线。
  - 对这种研究味道很重的 AI 岗位，真实 HR 首筛不会因为“也做过 LLM 应用”就判过。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 未测试 | 未测试 | 95.8/pass | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 87.3/fail | 87.8/fail |

**各版本分歧点**
1. `v3` 给到 `95.8/pass`，说明当时它把通用的 LLM / RAG / 评估经验误读成了 research AI 足够证据。
   对应原文翻译（v3）：v3 主要抓的是“首句先讲转型”和“同一段里 AWS、GCP、Azure、Kubernetes、Docker、Bedrock 同时出现像 stack stuffing”，并没有把 research-agent / RLHF 当成硬门槛。

2. `v9`、`v10` 稳定改成 `fail`，因为后期版本终于把 8451 这条真正的研究型 AI 能力家族单独拎出来了。
   对应原文翻译（v10）：JD 的核心能力家族是 agentic systems、multi-step reasoning、research agents、RLHF / reward modeling / PPO / DPO、world modeling、causal reasoning、pretraining 和 distributed training；简历只覆盖了泛化的 LLM / RAG / PyTorch / deep learning，没有这些研究型能力的实质证据。
   对应原文翻译（v10）：当前叙事主轴更偏 security、mobility 和通用分析，和 retail / commerce decisioning 的桥接也不够直接。

### conf/Photon-AIEngineer | Photon AI Engineer

- 最终结论：`fail`
- 我为什么判不过：
  - JD 要 `production GenAI`、`LangChain / LlamaIndex`、vector search、advanced retrieval、fine-tuning、local LLM quantization / hosting。
  - 当前简历有 `RAG / LLM / Bedrock`，说明方向相邻，但没有把 `LangChain/LlamaIndex`、高级检索架构、local LLM 这类关键能力写成足够硬的证据。
  - 这条不是普通“AI 感兴趣即可”的岗位，而是要求已经有比较明确的 production GenAI 工程实践。
- 这条是我后来修订成 fail 的典型案例：
  - 早期我把“做过 RAG/LLM”看得太重了。
  - 回到 raw JD 后，发现它要得更深、更具体。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 未测试 | 未测试 | 93.3/pass | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 89.4/fail | 89.7/fail |

**各版本分歧点**
1. `v3` 给 `93.3/pass`，说明它当时主要看到的是“首句先讲转型”和“多套技术并列太多”，而不是 production GenAI 的真正硬要求。
   对应原文翻译（v3）：v3 主要抓的是“首句先讲转型”和“多套技术并列太多、像 stack 展示”，并没有把 LangChain/LlamaIndex/vector search/local LLM 当成必须出现的硬证据。
   对应原文翻译（v3）：它把 breadth 过宽和 tier-1 scope 不足当成主要问题，没有把 LangChain/LlamaIndex/vector search/local LLM 当成必须出现的证据。

2. `v9`、`v10` 之所以稳定回到 `fail`，是因为后期版本把 Photon 这条岗位真正点名的框架和检索架构要求拉出来了。
   对应原文翻译（v10）：JD 反复强调 LangChain、LlamaIndex、vector search、embedding 和本地 LLM 运行，但简历只证明了泛化的 RAG、Bedrock 和 retrieval，没有把这些核心 GenAI 框架与检索架构讲出来。
   对应原文翻译（v10）：同一段实习里同时出现多套语言、平台和 AI 栈，会被读成 stack 拼贴，而不是清晰的 production GenAI ownership。

### conf/Clarivate-NLP | Clarivate NLP 高级数据科学家

- 最终结论：`fail`
- 我为什么判不过：
  - JD 明写 `5+ years` NLP / Python，且点名 `LangChain`，还带 `senior / technical leadership` 的意味。
  - 当前简历最多只能构成 `3+ years transferable NLP/ML`，并没有足够长的 NLP 主线，也没有 senior technical leadership 的明确证据。
  - 这条不是“你会一点 NLP 就行”，而是 senior NLP data scientist。
- 这条也是后来修订成 fail 的原因：
  - 早期我把“相关性”看得太高，低估了 senior NLP 年限和领导责任的硬度。

## 最后总结

- 这 30 个 case 里，`pass` 的共同特点是：
  - 岗位主轴和简历主轴基本对上。
  - 没有明显硬门槛冲突。
  - 即使 title 不完全一样，也有足够正文证据支撑 HR 给下一轮。
- `fail` 的共同特点是：
  - 年限硬门槛不够。
  - specialized 方向差得太远，例如 3D、signal processing、networking、research AI。
  - 或者 level 不对，例如 manager / senior specialist。
  - 或者技术词写得像，但真实主线不是那个岗位要的人。

如果你下一步要，我可以继续补一版“30 个 case 逐条摘原文证据”的文件，把每一条判定后面直接附上 `job.md` 和 `resume.md` 里的关键句。

**各版本打分**
| old_pipe | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 | v10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 未测试 | 未测试 | 99.7/pass | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 85.8/fail | 83.2/fail |

**各版本分歧点**
1. `v3` 给出 `99.7/pass`，非常能说明那一版几乎完全漏掉了 senior NLP 的硬门槛。
   对应原文翻译（v3）：v3 对 Clarivate 只抓到安全语境里的 Bedrock 数据边界表述，没有把 `5+ years NLP + LangChain/LangGraph + senior leadership` 当成硬门槛。

2. `v9`、`v10` 回到 `fail`，因为后期版本终于把 `5+ years NLP + 5+ years Python + LangChain/LangGraph + senior leadership` 这些硬条件当成了首筛门槛。
   对应原文翻译（v10）：JD 要 5+ 年 NLP 和 5+ 年 Python 经验，但简历可见时间线只有大约 3+ 年；而且 `LangChain / LangGraph` 这类核心 toolkit 也没有直接证据。
   对应原文翻译（v10）：最新相关经历仍然主要靠百分比提升和时延改进，没有能支撑 senior NLP 的 tier-1 scope 锚点。

