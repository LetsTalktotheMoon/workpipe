# Reviewer Pipe 深度评估证据版（中文）

日期：2026-04-17

## 说明

这份报告是在
[reviewer_pipe_deep_eval_zh_2026-04-17.md](reviewer_pipe_deep_eval_zh_2026-04-17.md)
的基础上展开证据。

写法原则：

- 每个关键判断后面，都补一段具体简历原文。
- 同时列出旧 pipe 与新 pipe 的原始评价摘录。
- 再结合对应分数或维度落点，解释我为什么得出这个结论。

本报告使用的两轮 Codex-only 结果：

- 新 pipe：
  [reviewer-compare/runs/20260417_185315_270748](runs/20260417_185315_270748)
- 旧 pipe：
  [reviewer-compare/old-pipe-codex/runs/20260417_185315_269474](old-pipe-codex/runs/20260417_185315_269474)

## 1. 新 pipe 明显更慢

结论：

- 旧 pipe 总耗时 `521s`，新 pipe `839s`。
- 旧 pipe 平均 `52.1s/case`，新 pipe `83.9s/case`。
- 新 pipe 平均约慢 `1.67x`。

### 证据 1：`same/Microsoft`

简历原文：

```md
* **Backend Engineering Alignment:** Software engineer transitioning from data analytics to backend engineering, with hands-on delivery across **Python**, **Java**, **C#**, **C++**, **JavaScript**, and **SQL** in production-facing security, operations, and distributed backend systems.
* **Distributed Systems Focus:** Contributed to internal services using **C++**, **Microservices**, **Kafka**, **gRPC**, **Docker**, **Kubernetes**, and **Azure**, translating ambiguous requirements into maintainable backend tooling and measurable reliability gains in latency-sensitive, service-to-service workflows.
```

旧 pipe：

- 耗时 `54s`
- 综合分 `88.1`
- 主要高分歧评价：
  - `JD 必须技术 Distributed Systems 没有在 Skills 中显式出现`
  - `开头先写 transitioning from data analytics to backend engineering，弱 framing 过强`

新 pipe：

- 耗时 `121s`
- 综合分 `80.9`
- 主要高分歧评价：
  - `P3B-001`：`Distributed Systems` 没有显式列在 Skills
  - `P3C-010`：TikTok 一段同时铺开 Go/Python/Java/C++/C#/JavaScript，像 stack stuffing
  - `P3E-002`：Temu 时间锚点冲突

讲解：

- 这个 case 的原文本身就容易触发多轮检查：首句 framing、技能显式覆盖、多语言 ownership、时间锚点。
- 旧 pipe 主要停留在“首屏 + JD 对齐”这两层。
- 新 pipe 会继续往下做结构、首屏、内容、生态四层细拆，所以同一个文本会触发更多规则匹配，耗时自然拉长。

### 证据 2：`extra/HealthEquity-DotNet`

简历原文：

```md
* **Software engineer trajectory:** Software engineer transitioning from data analytics with **3+ years** of experience building internal products across **Python**, **SQL**, **ASP.NET**, **.NET**, **JavaScript**, **Angular**, and **Scala**/Spark-oriented analytics workflows for security, operations, and audit-sensitive environments.
* **Delivery fit:** Hands-on in **Git**, **Scrum**, Agile, **CI/CD**, **Html**, **Css**, and operator-facing feature delivery, with experience supporting data and application workflows that intersect with **Azure**, **Databricks**, and **MongoDB**-style enterprise stacks.
```

旧 pipe：

- 耗时 `46s`
- 综合分 `93.5 pass`
- 高严重度 finding：无

新 pipe：

- 耗时 `111s`
- 综合分 `79.5 fail`
- 高严重度评价：
  - `P2-001`：首句是“从数据分析转向软件工程”的过渡过程
  - `P3B-001`：`Agile` 没在 Skills 显式出现；`Spark` 只以 `Spark SQL` / `Spark-oriented` 出现
  - `P3E-002`：Temu 时间锚点冲突

讲解：

- 这是“新 pipe 为什么慢”的最好例子。
- 旧 pipe 把这份简历看成“整体可过，只是包装稍乱”。
- 新 pipe 则会把首句 framing、must-have 显式覆盖、时间锚点三个检查全部走完，导致推理更长，而且 verdict 也翻转。

## 2. 新 pipe 的确抓到了一些旧 pipe 低估的真实问题

### 2.1 首句 framing 过弱，这不是鸡蛋里挑骨头

#### 证据 A：`same/AWS`

简历原文：

```md
* **Backend Transition Profile:** Software engineer candidate transitioning from analytics with hands-on delivery in **Java**, **Go**, **C++**, and **Embedded**-adjacent backend workflows across security, marketplace, and operations systems.
```

旧 pipe：

- 综合分 `94.6 pass`
- `r4_rationality = 8.9`
- 只有 1 条中等级别 rationality finding，整体仍然放行

新 pipe：

- 综合分 `81.5 fail`
- 高严重度评价：
  - `P2-001`：opening framing is a transition story rather than a direct role-and-domain signal

讲解：

- 这句原文的确是先让人看到 `Transition Profile` 和 `transitioning from analytics`。
- 旧 pipe 识别到了这个问题，但只把它当成可过的包装问题。
- 新 pipe 把它上升到首屏抓手问题，我认为**这个方向是对的**，因为 AWS 这种岗位的 HR 首屏确实更想先看到 `backend/security/builder`，而不是“候选人正在转型”。

#### 证据 B：`extra/CapitalOne-AI`

简历原文：

```md
* **Data Analysis Candidate:** **3+ years** applying **Python**, **SQL**, Spark, and **ETL** workflows to operational and security-focused datasets, with experience turning ambiguous business questions into repeatable analytics and decision support.
* **Analytics to Engineering Bridge:** Combines hands-on work across data pipelines, backend services, and audit-friendly internal tools to improve reporting quality, investigation speed, and partner-facing operations.
```

旧 pipe：

- 综合分 `89.2 fail`
- 高严重度评价：
  - `Data Analysis Candidate` 和 `Analytics to Engineering Bridge` 像 generic transition profile，不像直接 data-analysis profile

新 pipe：

- 综合分 `83.9 fail`
- 高严重度评价：
  - `P2-001`：首句 framing 偏“候选人/状态描述”，不是明确角色方向 + 领域信号

讲解：

- 这是一个两条 pipeline 都在同一个地方报警的例子。
- 所以这里不属于“新 pipe 硬挑毛病”，而是**旧新共识问题**。
- 区别只在于：旧 pipe 报得更像“summary 要重写”，新 pipe 报得更像“首屏抓手不合格”。

### 2.2 第一条 bullet 缺 Tier 1 scope，这个洞察有价值

#### 证据：`same/AWS`

简历原文：

```md
* Built **Go** and **Java** handlers in a team-maintained distributed **gRPC** service that normalized **Kafka** security events into **PostgreSQL**, cutting analyst lookup time from **11 minutes** to **4 minutes** for recurring incident triage.
```

旧 pipe：

- 综合分 `94.6 pass`
- 没有把这条作为高严重度问题提出

新 pipe：

- 综合分 `81.5 fail`
- 高严重度评价之一：
  - `P2-020`：第一页最相关经历的第一条 bullet 先给了时间缩短结果，没有 Tier 1 scope signal

讲解：

- 这条 bullet 并不差，技术和结果都有。
- 但对 AWS Builder/Backend 类岗位来说，它确实更像“局部效率提升”而不是“系统规模信号”。
- 所以我认同新 pipe 在这里的**方向**，但不认同它当前的**罚分力度**。

### 2.3 Tier 2 结果过多、Tier 1 规模锚点不够，这也是实打实的问题

#### 证据：`extra/Dataminr-Infra`

简历原文：

```md
* Built **Go** and **Python** service handlers within a team-maintained **Distributed Systems** environment, extending **gRPC** endpoints backed by **PostgreSQL** and **Elasticsearch** to reduce internal investigation request latency by **28%** for analyst-facing security workflows.
* Developed **Java**, **Scala**, and **Python** service-side evaluation utilities around existing **Kafka**-driven processing paths, improving rule evaluation throughput by **19%** within a team-owned event-processing workflow.
* Contributed to deployment workflows using **Docker** and **Kubernetes**, adding health checks and rollback validation that lowered failed staging releases by **31%** across the intern-owned service scope.
```

旧 pipe：

- 综合分 `92.8 fail`
- 高严重度评价只集中在第三句 header：
  - `Structured Problem Solver` 是低信号 header

新 pipe：

- 综合分 `84.5 fail`
- 高严重度评价：
  - `P2-010`：第三句 header 低信号
  - 同时在中等级别大量命中 `P3D-001`：百分比结果很多，但 scope / 规模锚点不够

讲解：

- 旧 pipe 基本只盯住了 summary。
- 新 pipe 额外看到了整段经历几乎全在讲百分比改进，而没有明确体量、QPS、事件量、服务规模。
- 这属于**旧 pipe 相对低估**、但新 pipe 抓得对的问题。

## 3. 新 pipe 也有明显“罚过头”的地方

### 3.1 `P3E-002` 不是发现了 10 个 case 的新硬伤，而是在反复惩罚同一类 corpus 冲突

#### 证据 A：`same/Amazon`

简历原文：

```md
### Data Analyst | Temu · R&D
*Jun 2021 – Feb 2022 | Shanghai*
```

旧 pipe：

- 综合分 `93.3 pass`
- 没有 critical/high

新 pipe：

- 综合分 `89.8 fail`
- 最高严重度评价只有一条：
  - `P3E-002`：Temu role sits in Jun 2021 – Feb 2022, but hard rule flags any Temu appearance before 2022-09-01 as invalid

讲解：

- 这不是“Amazon 这个 target JD 比旧 pipe 多发现了一个独有硬伤”。
- 这是所有简历共享的一条 immutable synthetic 履历被新规则统一判死。
- 也就是说，它更像**语料级冲突**，不是**case 级差异**。

#### 证据 B：`extra/Ramp-Platform`

简历原文：

```md
### Data Analyst | Temu · R&D
*Jun 2021 – Feb 2022 | Shanghai*
```

旧 pipe：

- 综合分 `97.0 pass`
- 没有高严重度 finding

新 pipe：

- 综合分 `89.8 fail`
- critical：
  - `P3E-002`：Temu appears in a period explicitly disallowed because it predates 2022-09-01

讲解：

- Ramp 这组的其他部分其实很强，旧 pipe 甚至给到了 `97.0`。
- 新 pipe 直接翻成 fail，几乎就是被这条 universal chronology rule 决定的。
- 所以我才说：**这不是新 pipe 更会评简历，而是它把 corpus 冲突拉进了 case 级总分。**

### 3.2 同一家族问题被重复累计，导致过罚

#### 证据：`extra/Dataminr-Infra`

简历原文：

```md
* Built **Go** and **Python** service handlers ... reduce internal investigation request latency by **28%**
* Developed **Java**, **Scala**, and **Python** ... improving rule evaluation throughput by **19%**
* Contributed to deployment workflows ... lowered failed staging releases by **31%**
```

旧 pipe：

- 综合分 `92.8 fail`
- 高严重度只抓了 summary 第三句 header

新 pipe：

- 综合分 `84.5 fail`
- `pass_3_substance` 除了 `P3E-002` 之外，还在多个位置重复命中 `P3D-001`

讲解：

- 这些 bullet 的确都偏 `%`、`latency`、`throughput`、`release` 结果。
- 但它们本质上是在重复揭示同一个问题：**规模锚点不够**。
- 如果把它当作 3-4 个独立问题叠加计分，就很容易把一个“中等强度的共性缺陷”放大成 fatal score drag。

### 3.3 格式纪律被放大到了不成比例的程度

#### 证据：`same/AWS`

简历原文：

```md
## Skills
* **Programming:** Java, C++, Go, Python, React, Linux, Embedded, gRPC, REST, Flask
* **Data:** SQL, ETL, Airflow, Hive, Pandas, Spark SQL, A/B Testing, AWS Bedrock, RAG
* **Cloud:** Kafka, PostgreSQL, Docker, Kubernetes, AWS, CI/CD, GitHub Actions
```

旧 pipe：

- 综合分 `94.6 pass`
- 整体认为只是轻微写法问题

新 pipe：

- 综合分 `81.5 fail`
- 高严重度评价：
  - `P1-051`：三条 skills line 全都超过 14-word cap

讲解：

- Skills line 太密，确实不优。
- 但如果把它放到和 chronology mismatch 同一个 verdict 层级去影响整体，力度就偏过了。
- 这类问题更适合成为 lint / cleanup signal，而不是核心 fail 原因。

## 4. 新 pipe 并不是单向更强，它也漏掉了旧 pipe 能抓到的问题

### 4.1 `same/Google`：旧 pipe 抓到了技能出处一致性，新 pipe 这一轮反而没抓到

简历原文：

```md
* Built feature components in a retrieval workflow leveraging **AWS**, Bedrock, and **S3**, contributing to answer retrieval coverage for **12K+** indexed documents within a team-maintained knowledge base.
```

对应 Skills：

```md
* **Cloud:** Microservices, Docker, Kubernetes, GitHub Actions, PostgreSQL, Kafka, MySQL, Redis, AWS, S3
```

旧 pipe：

- 综合分 `79.0 fail`
- 关键 critical：
  - `正文在 TikTok 项目里使用了 AWS Bedrock，但 Bedrock 没有出现在 Skills 中`

新 pipe：

- 综合分 `83.4 fail`
- 主要高严重度只抓了：
  - `P2-001` transition framing
  - `P3E-002` Temu chronology

讲解：

- 这里旧 pipe 的判断是对的，而且是很实在的 ATS/一致性问题。
- 新 pipe 这轮没把这条作为主要问题抓出来，反而因此比分更高。
- 所以不能说“新 pipe 全面强于旧 pipe”。在 authenticity / skill provenance 这条线上，旧 pipe 当前更强。

## 5. 逐环节评估，也给出对应文本证据

### 5.1 Pass 1 结构检查：方向对，但更适合做 lint

证据样本：`same/AWS`

原文：

```md
* **Programming:** Java, C++, Go, Python, React, Linux, Embedded, gRPC, REST, Flask
* **Data:** SQL, ETL, Airflow, Hive, Pandas, Spark SQL, A/B Testing, AWS Bedrock, RAG
* **Cloud:** Kafka, PostgreSQL, Docker, Kubernetes, AWS, CI/CD, GitHub Actions
```

旧 pipe：

- `94.6 pass`
- 不认为这是高严重度结构问题

新 pipe：

- `81.5 fail`
- `P1-051` high：三条 skills line 全都超过 14-word cap

我的评价：

- 这条规则适合保留。
- 但更适合做“必须整理”的 lint，而不是直接大幅拉低总分。

### 5.2 Pass 2 首屏检查：这是新 pipe 最有产品价值的一层

证据样本：`extra/CapitalOne-AI`

原文：

```md
* **Data Analysis Candidate:** **3+ years** applying **Python**, **SQL**, Spark, and **ETL** workflows...
* **Analytics to Engineering Bridge:** Combines hands-on work across data pipelines, backend services...
```

旧 pipe：

- `89.2 fail`
- 高严重度：summary 开头像 generic transition profile

新 pipe：

- `83.9 fail`
- `P2-001` high：首句 framing 偏 candidate / state，不是直接角色方向

我的评价：

- 这层是新 pipe 最稳定、最值得保留的能力。
- 它把“首屏不像目标岗位本人”说得更清楚。

### 5.3 Pass 3A 真伪/出处一致性：当前反而不如旧 pipe 完整

证据样本：`same/Google`

原文：

```md
* Built feature components in a retrieval workflow leveraging **AWS**, Bedrock, and **S3**
```

旧 pipe：

- `r0_authenticity` 直接被打到 `5.0`
- critical：正文里用了 `AWS Bedrock`，Skills 没列

新 pipe：

- 没把这条作为主要 finding 抓出来

我的评价：

- 新 pipe 在这条线上要补旧 pipe 的“双向技术出处一致性检查”。

### 5.4 Pass 3D 信号质量：新 pipe 最值得保留的核心能力之一

证据样本：`extra/Dataminr-Infra`

原文：

```md
* ... reduce internal investigation request latency by **28%**
* ... improving rule evaluation throughput by **19%**
* ... lowered failed staging releases by **31%**
```

旧 pipe：

- 只抓 summary 第三句 header

新 pipe：

- 在 `P3D-001` 上多次命中，认为整页过度依赖 Tier 2 百分比指标

我的评价：

- 这个洞察是对的。
- 但需要做“同家族去重”，否则太容易过罚。

### 5.5 Pass 3E 生态/公开锚点：当前是最大失真来源

证据样本：`same/Amazon` 与 `extra/Ramp-Platform`

原文：

```md
### Data Analyst | Temu · R&D
*Jun 2021 – Feb 2022 | Shanghai*
```

旧 pipe：

- `same/Amazon = 93.3 pass`
- `extra/Ramp-Platform = 97.0 pass`

新 pipe：

- `same/Amazon = 89.8 fail`
- `extra/Ramp-Platform = 89.8 fail`
- 两者最高严重度主因都是 `P3E-002`

我的评价：

- 这层不能继续按现在的方式直接进总分。
- 它更应该先做 corpus-level precheck，或拆成单独阻断标签。

## 6. 为什么我说“新 pipe 是更好的诊断器，但不是更好的裁判”

用两组最典型的对照来解释。

### 对照 A：`extra/Dataminr-Infra`

简历原文：

```md
* **Backend Engineer with Data Systems Depth:** ...
* **Microservices and Event-Driven Builder:** ...
* **Structured Problem Solver:** ...
```

旧 pipe：

- 综合分 `92.8 fail`
- 实际高严重度只抓到：
  - `Structured Problem Solver` 这个第三句 header 太弱

新 pipe：

- 综合分 `84.5 fail`
- 除了同样抓到第三句 header 太弱，还进一步指出：
  - Tier 1 scope 不足
  - Tier 2 指标过多
  - Temu chronology 冲突

解释：

- 从“解释为什么这份简历还不够强”来说，新 pipe 明显更会讲。
- 这就是它作为诊断器的优势。

### 对照 B：`extra/Ramp-Platform`

简历原文：

```md
* **Infrastructure-focused backend engineer:** Building **Go** and **Python** services with **Kafka**, **Redis**, **PostgreSQL**, **MySQL**, **Docker**, **Kubernetes**, and **Terraform**
```

旧 pipe：

- 综合分 `97.0 pass`
- 说明旧 pipe 认为这份简历对 Ramp 的 target 几乎已经是高质量成品

新 pipe：

- 综合分 `89.8 fail`
- 主因几乎就是 `P3E-002`

解释：

- 这里新 pipe 给出的不是“更好的 target fit 判断”。
- 它给出的是“更严格的 rule compliance 判断”。
- 所以它更像一个规则审计器，而不是一个校准好的发布裁判。

## 最后一句

如果你问我，这份证据展开之后，结论有没有变化：

- **没有本质变化，只是证据更充分了。**

更具体地说：

- 新 pipe 真的比旧 pipe 更会“指出哪里不对”。
- 但它目前还不会稳定地区分：
  - 哪些是会影响最终 gating 的硬问题；
  - 哪些只是应当在 rewrite 阶段修掉、但不该直接把整份简历打成 fail 的问题。
