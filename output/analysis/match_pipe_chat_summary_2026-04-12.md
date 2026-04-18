# match_pipe 多层级匹配系统评估整理

更新时间：2026-04-12

本文整理了本次关于 `match_pipe` 多层级匹配系统的讨论内容，保留业务解读、规则说明、指标说明、公式表和示例分析，省略命令行操作与中间推理过程。

---

## 一、系统结论

当前 `match_pipe` 中“正在测试的多层级匹配系统”，核心可分为两层：

1. 纯语义匹配层  
   把 JD 结构化为 `requirement_units`，基于 unit 逻辑、层级、约束类型和语义召回进行候选检索与打分。

2. 双通道 starter 选择层  
   在纯语义最优锚点之外，再单独保留“同公司连续性锚点”，供 downstream writer/planner 参考。

从当前代码和报告看，这套设计已经不是简单关键词匹配，而是一个“结构化 requirement matching + 双通道复用”的系统。

---

## 二、系统主流程

### 1. 新 JD 进入系统后的路径

```text
新 JD / 新职位
  -> loader 读入 row/raw_text
  -> units.build_structured_job
       - 文本切块
       - alias 命中 taxonomy
       - 识别 SINGLE / OR / AND / AT_LEAST_K / PARENT_ANY_CHILD
       - 生成 requirement_units / pattern_signature / recall_keys
  -> MatchEngine._candidate_pool
       - pattern_exact
       - hard_unit
       - hierarchy_expand
       - combo
       - 必要时 surface / fallback
  -> MatchEngine._score_candidate
       - 逐 unit 打分
       - 聚合 requirement_score / hard_requirement_score
       - 对 hard requirement 缺口进行惩罚
  -> StarterSelector.select
       - semantic_best_anchor
       - semantic_positive_cluster
       - company_best_anchor
       - writer_input.primary_anchor / continuity_anchor
  -> downstream writer / planner
```

### 2. 当前匹配规则的核心

- JD 会被拆成 title、summary、core skills、must-have、preferred、responsibilities、metadata 等块。
- 每个块会映射到 canonical ids。
- 系统显式识别逻辑关系：
  - `SINGLE`
  - `OR`
  - `AND`
  - `AT_LEAST_K`
  - `PARENT_ANY_CHILD`
- 每个 requirement unit 都有权重，`must_have > strong_preference > preferred > background`。
- 召回时会结合：
  - pattern exact
  - hard unit
  - hierarchy expand
  - combo
  - surface
  - same company
- 冻结后的 `teacher_b_pure_semantic` 会关闭 `surface/same_company/duplicate/metadata` 的主导作用，用来审计“纯语义能力”。

---

## 三、训练设计：它不是真正的 SGD 训练

`match_pipe` 里的“训练”不是神经网络式训练，没有 `loss/epoch/val_loss`。  
它更接近一个工程化训练流程：

1. 构造 benchmark case
2. 跑 teacher / student 检索
3. 在 holdout 上评估
4. 做小规模权重搜索 / 蒸馏
5. 做 purity audit 和 freeze 判断
6. 再做 downstream 流程验证

### 1. benchmark 分层

- `standard_cases`  
  偏“同公司、同标题、重复 JD”的旧世界命中。

- `hard_cases`  
  标题更泛化一点，但仍然大量受 duplicate/same-company 影响。

- `rebuilt_hard_cases`  
  更纯语义的难例集，强调：
  - 跨公司结构相似
  - OR / AND
  - parent-child
  - must vs preferred

- `semantic_gold`  
  小规模高置信金标，带人工 adjudication 和边界案例。

### 2. teacher / student 关系

- `teacher_b_pure_semantic`：纯语义 teacher，用来定义真正的语义上限。
- `student`：在线检索的轻量近似器，用 teacher trace 做蒸馏。

### 3. 冻结逻辑

训练的最终目标不是把单个指标刷高，而是同时满足：

- `rebuilt_hard` 和 `semantic_gold` 上的高命中
- 证明能力主要来自语义而不是 same-company/duplicate 偏置
- 能转化为下游 writer/planner 的业务收益

---

## 四、指标体系概览

### 1. benchmark 层核心指标

| 指标 | 含义 | 计算方式 | 主要用途 |
|---|---|---|---|
| `case_count` | 样本数 | `len(case_list)` | 给所有比例指标提供分母 |
| `hit_at_1` | Top1 是否命中正例 | 最佳正例排名 `<=1` 的比例 | 最核心检索指标 |
| `hit_at_3` | Top3 是否包含正例 | 最佳正例排名 `<=3` 的比例 | 看 rerank / fallback 空间 |
| `hit_at_5` | Top5 是否包含正例 | 最佳正例排名 `<=5` 的比例 | 看候选池是否包含可用解 |
| `mean_reciprocal_rank` | 平均倒数排名 | `mean(1/best_rank)`，未命中记 0 | 排名连续质量 |
| `median_positive_rank` | 正例中位排名 | 正例最佳 rank 的中位数 | 抗极端值 |
| `avg_runtime_ms` | 平均耗时 | 每条 query 平均耗时 | 部署成本 |
| `avg_candidate_pool_size` | 平均候选池大小 | 每条 query 的候选池规模均值 | 看召回宽度和噪音 |
| `misses` | 失败样本列表 | TopK 未命中的案例 | 误差分析 |

### 2. benchmark 质量审计指标

| 指标 | 含义 | 主要风险 |
|---|---|---|
| `same_company_positive_ratio` | 正例中同公司的比例 | 过高说明 benchmark 被公司偏置污染 |
| `exact_title_positive_ratio` | 正例中 exact title 的比例 | 过高说明 benchmark 只是标题重复命中 |

### 3. category 指标

这组指标不是看整体命中率，而是看“哪类规则最脆弱”。典型类别包括：

- `or_and_mixed`
- `must_vs_preferred_confusing`
- `parent_child_conflict`
- `title_same_business_different`
- `cross_company_structure_similar`

它们帮助判断下一轮要修的不是“大盘命中率”，而是哪个规则层最有风险。

---

## 五、指标的风险解读：为什么不能只看高分

### 1. 旧 benchmark 高分不代表纯语义强

从 purity audit 来看：

- `standard` 的 `same_company_positive_ratio = 1.0`
- `hard` 的 `same_company_positive_ratio = 1.0`
- `standard` 的 `exact_title_positive_ratio = 1.0`
- `hard` 的 `exact_title_positive_ratio = 1.0`

这意味着旧 benchmark 很容易被“同公司 + 同标题 + repost duplicate”刷高。

### 2. rebuilt_hard / semantic_gold 更可信，但样本偏小

- `rebuilt_hard_case_count = 33`
- `semantic_gold.case_count = 29`

它们更接近系统真正想解决的问题，但样本量偏小，方差会比较大。

### 3. `median_positive_rank=1` 很容易造成错觉

如果一半以上样本都排在第一，`median_positive_rank` 就会等于 1。  
它会掩盖长尾失败，不能单独作为“系统很好”的证据。

### 4. capability attribution 不是严格因果分解

`semantic_absolute / duplicate_absolute / same_company_absolute` 是通过 teacher variant 差分估算出来的，更像审计指标，不是严格可加的因果真值。

---

## 六、当前项目的 benchmark 层结果

### 1. benchmark 基本盘

| 指标 | 当前值 | 风险解释 |
|---|---:|---|
| `standard_case_count` | 208 | 旧基准大，但偏 duplicate/same-company |
| `hard_case_count` | 68 | 仍有很重标题与公司偏置 |
| `rebuilt_hard_case_count` | 33 | 更可信，但样本太小 |
| `semantic_gold.case_count` | 29 | 金标可信，但样本仍小 |
| `same_company_positive_ratio` | standard=1.0, hard=1.0, rebuilt_hard=0.0 | 旧 benchmark 严重污染 |
| `exact_title_positive_ratio` | standard=1.0, hard=1.0, rebuilt_hard=0.26 | rebuilt_hard 纯度明显更高 |

### 2. teacher / freeze 关键结果

| 数据集 | Hit@1 | Hit@3 | MRR | 备注 |
|---|---:|---:|---:|---|
| 旧 standard teacher | 0.9459 | 0.9730 | 高 | 容易被 duplicate 偏置刷高 |
| 旧 hard teacher | 0.8182 | 0.9091 | 高 | 同样受旧 benchmark 偏置影响 |
| `teacher_b` rebuilt_hard | 0.7273 | 0.8788 | 0.7980 | 更能代表纯语义能力 |
| `teacher_b` semantic_gold | 0.7586 | 0.9310 | 0.8391 | 更接近冻结判断依据 |

冻结报告结论：

- `passed = true`
- `frozen_version = teacher_b_semantic_v1`

### 3. 当前最危险的 category 风险

| 类别 | Hit@1 | Hit@3 | 风险说明 |
|---|---:|---:|---|
| `must_vs_preferred_confusing` | 0.3333 | 0.6667 | 对 must-have 与 preferred 的区分仍偏弱 |
| `parent_child_conflict` | 0.5000 | 0.8333 | parent-child 结构仍有误判空间 |
| `title_same_business_different` | 0.6667 | 0.8333 | 同业务相近 title 仍可能误判 |
| `cross_company_structure_similar` | 1.0000 | 1.0000 | 这类能力反而较强 |
| `or_and_mixed` | 1.0000 | 1.0000 | OR/AND 在样本内表现稳定 |

---

## 七、Student 蒸馏与训练目标

### 1. 旧 student

旧 student 更依赖平面 overlap 和 metadata：

- `required_overlap`
- `all_overlap`
- `domain_overlap`
- `title_overlap`
- `role_score`
- `seniority_score`

旧权重选择目标：

```text
score = hit_at_1 + 0.5 * hit_at_3 + 0.25 * MRR
```

### 2. 新 semantic student

新 student 更接近语义 teacher：

- `must_overlap`
- `preferred_overlap`
- `background_overlap`
- `canonical_overlap`
- `hierarchy_overlap`
- `logic_overlap`
- `domain_overlap`
- `role_score`
- `seniority_score`

新蒸馏目标：

```text
0.54 * hit_at_1
+ 0.24 * hit_at_3
+ 0.12 * MRR
+ 0.10 * teacher_trace_alignment
```

### 3. 当前蒸馏规模

| 指标 | 当前值 |
|---|---:|
| `train_case_count` | 50 |
| `trace_count` | 228 |
| `rebuilt_hard_train` | 27 |
| `rebuilt_hard_holdout` | 6 |
| `semantic_gold_train` | 23 |
| `semantic_gold_holdout` | 6 |

---

## 八、匹配打分公式总表

下面只整理主匹配链路里的 score 字段。

| 字段 | 公式 / 规则 | 含义 | 主要风险 |
|---|---|---|---|
| `SurfaceElement.confidence` | 无命中时 `0.12`；否则 `min(0.55 + 0.1 * len(members), 0.96)` | 文本结构化置信度 | 启发式，不是最终排序主信号 |
| `RequirementUnit.unit_weight` | `min(base_constraint + content_bonus + section_bonus + logic_bonus, 1.35)` | unit 重要性 | tech item 很多时会把分散要求堆高 |
| `RequirementUnit.member_weights` | `experience=1.08`，父节点 `0.82`，子节点 `1.04`，其他 `1.0` | unit 内成员重要性 | 会放大 child 技能 |
| `_member_match_score` | exact / descendant 命中给高分；ancestor 命中给低分；exact element 可退化命中 | 单成员匹配分 | ancestor 奖励低，parent-child 类可能保守 |
| `_best_structure_alignment` | overlap 乘以 `(0.58 + 0.22*logic_alignment + 0.2*content_alignment)` | 结构对齐度 | floor 会让错配也保留一定分数 |
| `UnitMatchDetail.score` for `SINGLE` | `max(member_scores)` | 单项命中度 | 容易被单个强命中支撑 |
| `UnitMatchDetail.score` for `OR` | `max(member_scores)`，多 exact 命中有 bonus，上限 `1.08` | 任一满足即可 | OR 容忍度较高 |
| `UnitMatchDetail.score` for `AND` | `weighted_hits / total_weight - 0.14 * missing_ratio` | 必须同时满足 | 缺一部分时仍可能保留中分 |
| `UnitMatchDetail.score` for `AT_LEAST_K` | 前 `k` 个加权命中 / 所需权重 | 至少 K 项满足 | K 小时偏宽松 |
| `UnitMatchDetail.score` for `PARENT_ANY_CHILD` | 任一 child 高命中可直接高分 | 父类命中任一子类即可 | 较宽 |
| `_semantic_specificity(unit)` | 基于 IDF 的归一化，再按 constraint type 微调 | 稀有 requirement 更值钱 | 依赖当前索引分布 |
| `weighted_requirement` | `sum(effective_weight * unit_score) / sum(effective_weight)` | 整体 requirement 命中 | 强依赖拆分质量 |
| `semantic_band_score` | `0.52*must + 0.20*strong + 0.18*preferred + 0.10*background` | 分层 requirement 质量 | 强偏 must-have |
| `requirement_score` | `0.58 * weighted_requirement + 0.42 * semantic_band_score` | 总 requirement 分 | 同时受全局与 band 影响 |
| `hard_requirement_score` | `0.76 * must_score + 0.24 * strong_score` | 硬要求覆盖度 | 是惩罚门槛核心 |
| `surface_score` | `0.45*token_overlap + 0.35*title_overlap + 0.2*title_exact` | 表层相似度 | 纯语义 teacher 中关闭 |
| `metadata_score` | `0.34*role + 0.22*seniority + 0.18*domain + 0.26*same_company` | 元数据相似度 | 纯语义 teacher 中关闭 |
| `duplicate_score` | `0.35*same_company + 0.30*title_exact + 0.20*title_overlap + 0.15*surface_overlap` | duplicate 偏置分 | 纯语义 teacher 中关闭 |
| `total_score` | `0.64*requirement + 0.14*hard + 0.08*surface + 0.06*metadata + 0.08*duplicate` | 最终排序分 | mixed teacher 容易吃 duplicate 红利 |
| `low-hard penalty` | `hard<0.45` 乘 `0.72`；`hard<0.6` 乘 `0.86` | 限制硬要求缺口 | 0.6 附近很敏感 |
| `reuse_readiness` | `0.72*requirement_score + 0.28*hard_requirement_score` | starter 可复用度 | 比 total 更偏内容可写性 |
| `starter_priority_score` | `0.48*historical_quality + 0.32*reuse_readiness + 0.20*match.total_score` | semantic cluster 里选最终 starter | 会受历史质量影响 |
| `company_consistency_score` | `0.46*semantic_reuse + 0.34*title_exact + 0.10*title_overlap + continuity` | 同公司连续性分 | 不能混入纯语义 teacher |

---

## 九、示例：Disney JD 是怎样一步步匹配到候选简历的

这里选用一条真实 JD：

- `job_id = 69da933b9f97a42dc9c2a057`
- `company = The Walt Disney Company`
- `title = Software Engineer II`

### 1. 原始输入字段

系统使用的核心输入包括：

- `job_title`
- `job_summary`
- `core_skills`
- `must_have_quals`
- `preferred_quals`
- `core_responsibilities`
- `work_model`
- `job_location`
- `job_seniority`
- `min_years_experience`
- `taxonomy_v3`

### 2. 切块与 canonical 抽取

这条 JD 结构化后，核心 canonical ids 包括：

- `CONSTRAINT_ONSITE`
- `RESP_SOFTWARE_DEVELOPMENT`
- `CONSTRAINT_ENGINEERING_FIELD`
- `TECH_SCALA`
- `TECH_JAVA`
- `TECH_CPP`
- `TECH_C`
- `RESP_FULLSTACK_DEVELOPMENT`
- `TECH_CSHARP`
- `TECH_PYTHON`
- `TECH_SQL`
- `EXP_YOE_3_5`
- `TECH_AIRFLOW`
- `TECH_DATABRICKS`
- `TECH_SNOWFLAKE`
- `TECH_SPARK`
- `TECH_API`
- `TECH_DATABASE`
- `TECH_MYSQL`
- `TECH_MONGODB`
- `TECH_DYNAMODB`
- `CONSTRAINT_COMPUTER_SCIENCE`

### 3. recall keys

这条 JD 的典型 recall keys 包括：

- `OR(TECH_DATABRICKS,TECH_SNOWFLAKE)`
- `OR(TECH_AIRFLOW,TECH_SCALA)`
- `AND(TECH_API,TECH_SQL)`
- `AND(RESP_FULLSTACK_DEVELOPMENT,RESP_SOFTWARE_DEVELOPMENT)`
- `TECH_SCALA`
- `TECH_JAVA`

### 4. 候选召回与排序逻辑

系统先基于 hard unit / combo / hierarchy 等方式召回候选，再对每个候选做逐 unit 打分，最后得到：

- `requirement_score`
- `hard_requirement_score`
- `total_score`

若 `hard_requirement_score` 太低，会触发整体惩罚。

### 5. 结论性理解

这个流程的关键不是“哪个词重合最多”，而是：

- 这条 JD 被拆成了哪些结构化 requirement
- 每个 requirement 的逻辑关系是什么
- candidate 是否命中了这些结构化约束
- must-have 的缺口是否足够大，以至于需要整体惩罚

---

## 十、Disney JD 的全部 requirement_units 逐条表

下面这张表使用的是当前本地可直接复现的纯 benchmark 配置：

- `teacher_b_pure_semantic`
- `include_scraped=True`
- `include_portfolio=False`

在这个配置下，这条 Disney JD 的 top1 为：

- `Amazon | Data Engineer II, Amazon Payment Products`
- `total_score = 0.4940`
- `requirement_score = 0.6372`
- `hard_requirement_score = 0.6155`

说明：

- `weight(unit/effective)` 中
  - `unit` = `unit_weight`
  - `effective` = `unit_weight * semantic_specificity`
- `top1命中分` = 该 unit 对当前 top1 的 `_score_unit` 结果

### 原句：`Software Engineering, Scala, Java, C++, C`

| unit | logic | weight(unit/effective) | top1命中分 |
|---|---|---:|---:|
| `RESP_SOFTWARE_DEVELOPMENT` | `SINGLE` | `0.9400 / 1.0076` | `0.5800` |
| `CONSTRAINT_ENGINEERING_FIELD` | `SINGLE` | `0.9200 / 0.9676` | `1.0000` |
| `TECH_SCALA` | `SINGLE` | `0.9800 / 1.1172` | `1.0000` |
| `TECH_JAVA` | `SINGLE` | `0.9800 / 1.0650` | `1.0000` |
| `TECH_CPP` | `SINGLE` | `0.9800 / 1.0737` | `0.1800` |
| `TECH_C` | `SINGLE` | `0.9800 / 1.1026` | `0.1800` |

### 原句：`3+ years of hands-on software engineering experience, Designing, building, and maintaining full stack codes utilizing various technical languages e.g. Scala, Java, C++, C, C#, Python, SQL`

| unit | logic | weight(unit/effective) | top1命中分 |
|---|---|---:|---:|
| `RESP_SOFTWARE_DEVELOPMENT, RESP_FULLSTACK_DEVELOPMENT` | `AND` | `1.2200 / 1.2550` | `0.1387` |
| `CONSTRAINT_ENGINEERING_FIELD` | `SINGLE` | `1.1600 / 1.1771` | `1.0000` |
| `TECH_SCALA` | `SINGLE` | `1.2200 / 1.2688` | `1.0000` |
| `TECH_JAVA` | `SINGLE` | `1.2200 / 1.2502` | `1.0000` |
| `TECH_CPP` | `SINGLE` | `1.2200 / 1.2533` | `0.1800` |
| `TECH_C` | `SINGLE` | `1.2200 / 1.2636` | `0.1800` |
| `TECH_CSHARP` | `SINGLE` | `1.2200 / 1.2649` | `0.1800` |
| `TECH_PYTHON` | `SINGLE` | `1.2200 / 1.2402` | `1.0000` |
| `TECH_SQL` | `SINGLE` | `1.2200 / 1.2528` | `1.0000` |
| `EXP_YOE_3_5` | `SINGLE` | `1.2000 / 1.2219` | `1.0000` |

### 原句：`Troubleshooting code for bugs using various tools available in the IDE and/or logging, Write production-grade, maintainable code primarily for data pipelines leveraging Airflow, Databricks Asset Bundles, or Snowflake in Scala`

| unit | logic | weight(unit/effective) | top1命中分 |
|---|---|---:|---:|
| `TECH_DATABRICKS, TECH_SNOWFLAKE` | `OR` | `1.2600 / 1.3104` | `0.1198` |
| `TECH_AIRFLOW, TECH_SCALA` | `OR` | `1.2600 / 1.3104` | `0.9244` |

### 原句：`Implement complex data transformations using Spark Structured streaming, Spark SQL and core Spark APIs`

| unit | logic | weight(unit/effective) | top1命中分 |
|---|---|---:|---:|
| `TECH_SQL, TECH_API` | `AND` | `1.2600 / 1.2925` | `0.4078` |
| `TECH_SPARK` | `SINGLE` | `1.2200 / 1.2670` | `0.7200` |

### 原句：`Designing and implementing relational and non-relational database schemas e.g. MySql, Mongodb, Dynamodb`

| unit | logic | weight(unit/effective) | top1命中分 |
|---|---|---:|---:|
| `TECH_DATABASE` | `SINGLE` | `1.2200 / 1.2514` | `1.0000` |
| `TECH_MYSQL` | `SINGLE` | `1.2200 / 1.2688` | `0.1296` |
| `TECH_MONGODB` | `SINGLE` | `1.2200 / 1.2688` | `0.1296` |
| `TECH_DYNAMODB` | `SINGLE` | `1.2200 / 1.2688` | `0.7200` |

### 原句：`Bachelor's Degree in Computer Science or relevant technical field`

| unit | logic | weight(unit/effective) | top1命中分 |
|---|---|---:|---:|
| `CONSTRAINT_COMPUTER_SCIENCE` | `SINGLE` | `1.1600 / 1.1825` | `0.7200` |

### 原句：`Onsite`

| unit | logic | weight(unit/effective) | top1命中分 |
|---|---|---:|---:|
| `CONSTRAINT_ONSITE` | `SINGLE` | `0.3000 / 0.3040` | `1.0000` |

### 这张表怎么读

这条 Disney JD 被 top1 拉高分的部分主要是：

- `Scala`
- `Java`
- `Python`
- `SQL`
- `YOE`
- `Engineering field`
- `Database`
- `Onsite`

真正拖分的部分主要是：

- `full stack AND`
- `Databricks | Snowflake`
- `MySQL`
- `MongoDB`
- `C / C++ / C#`

这也解释了为什么它虽然不是完美匹配，仍然能拿到较高的 `requirement_score` 和 `hard_requirement_score`。

---

## 十一、下游业务层面的观察

当前的小样本验证里：

| flow | avg_final_score |
|---|---:|
| `no_starter` | `94.4` |
| `old_match_anchor` | `94.7` |
| `new_dual_channel_anchor` | `94.45` |

说明现阶段真正未收敛的点不是“能不能找到语义相似候选”，而是：

- `semantic_best` 是否等于最佳可写 starter
- `company continuity` 什么时候应该加，什么时候应该降级
- planner 什么时候介入才真正带来收益

---

## 十二、最终判断

### 1. 当前系统的优点

- 已经具备比关键词匹配更强的结构化语义能力
- 能区分 must / preferred / background
- 能处理 OR / AND / 层级扩展
- 有独立的 purity audit，可以防止被 same-company / duplicate 偏置误导

### 2. 当前系统最值得警惕的风险

- 旧 benchmark 过度奖励 duplicate 和 same-company
- 纯语义 hard 集与 gold 集规模仍然偏小
- must vs preferred 与 parent-child 仍然是最脆弱的规则层
- 下游 writer/planner 的收益尚未稳定转化

### 3. 一句话总结

`match_pipe` 已经从“表层相似匹配器”演化为“结构化 requirement 匹配器 + 双通道复用系统”；  
当前最关键的问题不再是“有没有匹配能力”，而是“benchmark 是否足够纯、规则是否足够稳、以及语义命中是否真的能转化为更好的可写 starter”。

---

## 十三、附录A：第九部分 canonical 抽取逐项详解

说明：
- `source block` 指 `build_structured_job()` 里切出来的文本块。
- `识别逻辑` 指当前代码中的实际机制：`alias pattern`、`experience bucket`、`metadata constraint`、以及 `split / connector grouping`。
- 这条 Disney JD 的 `canonical_elements` 一共 22 个，下面逐一覆盖。

### A1. 逐 canonical id 表

| canonical_id | 中文介绍 | 触发短语 | 识别逻辑 | source block | 备注 |
|---|---|---|---|---|---|
| `RESP_SOFTWARE_DEVELOPMENT` | 软件开发 / 软件工程职责 | `Software Engineering`；`software engineering experience` | `alias pattern`，责任类别别名命中，重复命中后去重保留 | `core_skills`；`must_have_quals#1` | 不是 title 推断 |
| `CONSTRAINT_ENGINEERING_FIELD` | 工程类背景 / 工程相关字段 | `Software Engineering`；`software engineering experience` | `alias pattern`，约束类别别名 `engineering` 命中 | `core_skills`；`must_have_quals#1` | 不是从 `relevant technical field` 直接命中 |
| `TECH_SCALA` | Scala | `Scala` | `alias pattern`，直接命中 | `core_skills`；`must_have_quals#1`；`must_have_quals#2` | 多块重复命中后去重 |
| `TECH_JAVA` | Java | `Java` | `alias pattern`，直接命中 | `core_skills`；`must_have_quals#1` | 直接语言名命中 |
| `TECH_CPP` | C++ | `C++` | `alias pattern`，`c++` / `c/c++` / `c / c++` 命中 | `core_skills`；`must_have_quals#1` | 规范化 token 命中 |
| `TECH_C` | C 语言 | `C` | `alias pattern`，单字母语言词边界命中 | `core_skills`；`must_have_quals#1` | 依赖 `_normalize_text()` |
| `RESP_FULLSTACK_DEVELOPMENT` | 全栈开发职责 | `full stack codes` | `alias pattern`，`full stack` 别名命中 | `must_have_quals#1` | 职责类 canonical |
| `TECH_CSHARP` | C# | `C#` | `alias pattern`，直接命中 | `must_have_quals#1` | 直接语言名命中 |
| `TECH_PYTHON` | Python | `Python` | `alias pattern`，直接命中 | `must_have_quals#1` | 直接语言名命中 |
| `TECH_SQL` | SQL | `SQL`；`Spark SQL` | `alias pattern`，显式 SQL 或 Spark SQL 命中 | `must_have_quals#1`；`must_have_quals#3` | 多块重复命中 canonical |
| `EXP_YOE_3_5` | 3 到 5 年经验 | `3+ years` | `experience bucket`，由 `_detect_experience_bucket()` 抽取 | `must_have_quals#1` | 唯一明显经验桶 canonical |
| `TECH_AIRFLOW` | Airflow | `Airflow` | `alias pattern`，直接命中 | `must_have_quals#2` | 数据管道要求 |
| `TECH_DATABRICKS` | Databricks | `Databricks Asset Bundles` | `alias pattern`，taxonomy 认 `databricks`，不认 `Asset Bundles` 本身 | `must_have_quals#2` | 只抽出核心产品名 |
| `TECH_SNOWFLAKE` | Snowflake | `Snowflake` | `alias pattern`，直接命中 | `must_have_quals#2` | 直接命中 |
| `TECH_SPARK` | Spark | `Spark Structured streaming`；`Spark SQL`；`core Spark APIs` | `alias pattern`，直接命中 | `must_have_quals#3` | 不把 `Structured streaming` 单独建 canonical |
| `TECH_API` | API | `core Spark APIs` | `alias pattern`，`api` / `apis` 命中 | `must_have_quals#3` | 复数规范化命中 |
| `TECH_DATABASE` | Database | `relational and non-relational database schemas` | `alias pattern`，`database` / `databases` 命中 | `must_have_quals#5` | 父类 canonical |
| `TECH_MYSQL` | MySQL | `MySql` | `alias pattern`，直接命中 | `must_have_quals#5` | 直接数据库名命中 |
| `TECH_MONGODB` | MongoDB | `Mongodb` | `alias pattern`，直接命中 | `must_have_quals#5` | 直接数据库名命中 |
| `TECH_DYNAMODB` | DynamoDB | `Dynamodb` | `alias pattern`，直接命中 | `must_have_quals#5` | 直接数据库名命中 |
| `CONSTRAINT_COMPUTER_SCIENCE` | 计算机科学学位 / CS 背景 | `Computer Science` | `alias pattern`，`computer science` 命中 | `must_have_quals#7` | 抽到了 CS，但没抽到 `Bachelor's Degree` 本身 |
| `CONSTRAINT_ONSITE` | 到岗 / onsite 约束 | `Onsite` | `metadata constraint`，由 `work_model` 识别 | `metadata(work_model)` | 元数据约束，不是语义 alias |

### A2. 为什么这些 canonical 会出现，而别的词不会

这条 JD 的 canonical 抽取是“词典 / 别名驱动 + 结构切块驱动”，不是自由语义抽取。能抽到的，基本都满足以下之一：
- 在 `taxonomy.py` 里有显式 alias。
- 命中经验桶规则，比如 `3+ years -> EXP_YOE_3_5`。
- 命中 metadata 规则，比如 `work_model = onsite -> CONSTRAINT_ONSITE`。
- 通过 `_build_units_for_block()` 把同一块里的多个 alias 按 `and / or / plus` 组合成 unit。

### A3. 未被抽取的重要短语 / 子句表

| 原句 | 短语 / 子句 | 未抽取原因 |
|---|---|---|
| `Software Engineer II` | `Software Engineer II` | title 只用于 `role_family` / `seniority`，当前 taxonomy 没把这个职位名做成 canonical alias |
| `The Walt Disney Company is a global leader in media and entertainment...` | 整段公司介绍 | 背景描述，不在 canonical 词表 |
| `...join their Media and Session Data Product team...` | `Media and Session Data Product team` | 没有对应 domain alias |
| `...building data pipelines and datasets...` | `data pipelines and datasets` | taxonomy 没有 `data pipeline` / `dataset` canonical |
| `...scale their streaming services` | `streaming services` | 业务语境描述，不是当前 canonical |
| `Own the end-to-end lifecycle of data products from ingestion, transformation, orchestration, to consumption by analytics, ML, and reporting teams` | 整句 | 职责性叙述，没有对应 canonical |
| `Using basic and advanced features of code management tools e.g. GitHub` | `GitHub` | taxonomy 没有 `GitHub` canonical |
| `Develops, documents, implements and test features within existing systems` | 整句 | 通用职责句，没有 alias 命中 |
| `Presents technical issues, solutions and project status...` | 整句 | 通用职责句，没有 alias 命中 |
| `Serves as escalation point for technical problems and maintenance` | 整句 | 通用职责句，没有 alias 命中 |
| `Actively contributes to architectural direction, code reviews, design documents, and planning...` | 整句 | 当前 taxonomy 没把这些动词化职责拆成 canonical |
| `Able to break down features into prioritized tasks` | 整句 | 通用能力描述，没有 alias 命中 |
| `Mentors others in areas they have experience in` | 整句 | 通用软技能描述，没有 alias 命中 |
| `Seattle, WA` | `Seattle, WA` | `job_location` 目前只被保留为 metadata 文本 |
| `Bachelor's Degree in Computer Science or relevant technical field` | `Bachelor's Degree` | `_normalize_text()` 会打散撇号，导致这类 alias 容易漏掉 |
| `Bachelor's Degree in Computer Science or relevant technical field` | `relevant technical field` | 没有直接 alias；只被更宽泛的 `CONSTRAINT_ENGINEERING_FIELD` 间接覆盖 |
| `Troubleshooting code for bugs using various tools available in the IDE and/or logging` | 整句 | 过程描述，没有具体 canonical alias |
| `...leveraging Airflow, Databricks Asset Bundles, or Snowflake in Scala` | `Asset Bundles` | taxonomy 只有 `Databricks`，没有 `Asset Bundles` |
| `Implement complex data transformations using Spark Structured streaming, Spark SQL and core Spark APIs` | `Structured streaming` | taxonomy 只有 `Spark`，没有单独建模 `Structured streaming` |
| `Implement complex data transformations using Spark Structured streaming, Spark SQL and core Spark APIs` | `core` | 形容词，不是 canonical |
| `Designing and implementing relational and non-relational database schemas e.g. MySql, Mongodb, Dynamodb` | `relational` / `non-relational` | 没把数据库范式单独建模，只抽了 `Database` 和具体数据库名 |

### A4. 完整性评估

#### 已覆盖
- 最核心、最具体的技术栈基本都被抽到了：`Scala / Java / C++ / C / C# / Python / SQL / Airflow / Databricks / Snowflake / Spark / API / Database / MySQL / MongoDB / DynamoDB`。
- 关键约束也覆盖了：`3+ years`、`Computer Science`、`Onsite`。
- `build_structured_job()` 在这条 JD 上能有效切块，并对重复 canonical 去重。

#### 部分覆盖
- `Bachelor's Degree in Computer Science or relevant technical field` 只部分覆盖：`Computer Science` 抽到了，但 `Bachelor's Degree` 和 `relevant technical field` 没单独抽出。
- `Databricks Asset Bundles`、`Spark Structured streaming`、`core Spark APIs` 只抽了核心词，没把修饰性子短语单独建模。
- `CONSTRAINT_ENGINEERING_FIELD` 对 “technical field” 的语义覆盖是间接的，不是直达的。

#### 未覆盖
- 所有“职责说明型”长句基本没进 canonical，只留在 `pending_surface_texts`。
- 公司介绍、团队介绍、地点、GitHub 工具、端到端生命周期、code review、architectural direction 等都没有专门 canonical。
- 这不是抽取失败，而是 taxonomy 没给这些表达建立可匹配 canonical。

#### 结论
- 若以“核心技术和硬约束是否被覆盖”为标准，这条 JD 的 canonical 抽取是高覆盖但不完全。
- 若以“整段 JD 语义都应 canonical 化”为标准，这条 JD 的 canonical 抽取是不完整的，缺口主要在职责描述、过程描述和部分学位措辞。
- 若要专门验证 `Bachelor's Degree` 的撇号归一化问题，最小额外案例就是任意一条显式写了 `Bachelor's Degree` 的 JD。

### A5. 关键代码依据

- `match_pipe/units.py:94-122`  
  `_text_blocks()`，决定 title / summary / core_skills / must_have_quals / preferred_quals / core_responsibilities / metadata 怎么切块。
- `match_pipe/units.py:125-160`  
  `_normalize_text()`、`_find_alias_hits()`，决定别名如何被标准化并匹配到 canonical。
- `match_pipe/units.py:163-193`  
  `_detect_experience_bucket()`、`_detect_metadata_constraints()`，决定 `3+ years`、`Onsite` 这类结构化约束如何抽取。
- `match_pipe/units.py:196-210`  
  `_infer_logic_type()`，决定一个 unit 是 `SINGLE / OR / AND / PARENT_ANY_CHILD`。
- `match_pipe/units.py:228-262`  
  `_guess_content_type()`、`_unit_weight()`，决定 unit 属于什么内容类型，以及权重如何计算。
- `match_pipe/units.py:265-281`  
  `_member_weight()`、`_surface_confidence()`，决定成员权重和 surface 置信度。
- `match_pipe/units.py:526-661`  
  `_build_units_for_block()`，决定一个 block 如何被拆成多个 requirement_units。
- `match_pipe/units.py:684-780`  
  `build_structured_job()`，决定 canonical_elements / expanded_elements / requirement_units / pending_surface_texts 如何最终汇总。
- `match_pipe/taxonomy.py:26-297`  
  canonical 定义和 alias 表，决定“什么词能被抽成什么 canonical”。

---

## 十四、附录B：第十部分 requirement_units 表逐字段释义与逐项判分说明

基于当前文档第十部分采用的纯 benchmark 配置：`teacher_b_pure_semantic + include_scraped=True + include_portfolio=False`。  
这条 Disney JD 的 top1 候选在该配置下为：

| 项目 | 值 |
|---|---:|
| top1 candidate | `Amazon | Data Engineer II, Amazon Payment Products` |
| `total_score` | `0.4940` |
| `requirement_score` | `0.6372` |
| `hard_requirement_score` | `0.6155` |

### B1. 字段/分数总表

| 字段 | 这是什么 | 计算什么 | 为什么算 | 公式 |
|---|---|---|---|---|
| `unit` | 一个结构化 requirement，通常来自一个原句或一个切块后的逻辑片段 | 把 JD 拆成可单独比较的约束单元 | 避免把整段文本当成黑盒 | 由 `build_structured_job()` 生成 |
| `logic` | 这个 unit 的逻辑类型 | 表达“必须全满足 / 满足任一 / 至少满足 K 个 / 父类任一子类”等关系 | 不同逻辑应使用不同判分法 | `SINGLE / OR / AND / AT_LEAST_K / PARENT_ANY_CHILD` |
| `weight(unit)` | unit 自身的重要性权重 | 反映这个 requirement 在 JD 中有多重要 | 让 must-have、核心技能、标题等对总分影响更大 | `min(base_constraint + content_bonus + section_bonus + logic_bonus, 1.35)` |
| `weight(effective)` | unit 的有效权重 | 在 `unit_weight` 基础上再乘语义稀缺度 | 让更稀有、更关键的 requirement 更重要 | `unit_weight * semantic_specificity(unit)` |
| `top1命中分` | 该 unit 对当前 top1 候选的命中分 | 看这个 unit 在候选上到底匹配得多好 | 这是逐项解释总分的基本粒度 | `_score_unit(unit, candidate).score` |
| `requirement_score` | requirement 层总分 | 汇总所有 unit 的 weighted 命中质量 | 比单个 unit 更稳定 | `0.58 * weighted_requirement + 0.42 * semantic_band_score` |
| `hard_requirement_score` | 硬要求层总分 | 只强调 must-have / strong_preference 的覆盖 | 防止“表面像但硬要求缺很多”的候选排太前 | `0.76 * must_score + 0.24 * strong_score` |
| `total_score` | 最终排序分 | 决定候选最终名次 | 把 requirement、hard、surface、metadata、duplicate 合在一起 | `0.64*requirement + 0.14*hard + 0.08*surface + 0.06*metadata + 0.08*duplicate` |

### B2. 这些分数为什么要这样算

`unit_weight` 是“这条 requirement 值不值得重视”；`effective_weight` 是“这条 requirement 在整个 corpus 里是不是稀缺、是不是更该被放大”。  
`top1命中分` 则是“候选在这一条 requirement 上到底命中几分”。

`requirement_score` 和 `hard_requirement_score` 是不同层面的聚合：
- `requirement_score` 看整体语义覆盖，适合衡量“像不像这份 JD”。
- `hard_requirement_score` 专门盯硬条件，避免只靠标题、职责、泛化词把分刷高。
- `total_score` 是最终排序分；在当前纯语义配置里，`surface_score / metadata_score / duplicate_score` 被关闭，所以这条 Disney 的 `total_score` 数值上主要来自 `requirement_score` 和 `hard_requirement_score`。

### B3. 单项判分的核心公式

| 组件 | 公式 | 含义 |
|---|---|---|
| `semantic_specificity(unit)` | `1 + bump(normalized_idf)` | 稀有 requirement 更值钱 |
| `normalized_idf` | `clamp(avg_idf / 3.5, 0, 1)` | 把稀有度压到 0 到 1 |
| `avg_idf` | `mean(log((corpus_size + 1) / (df + 1)) + 1)` | 统计这个 member 在语料中有多稀有 |
| `SINGLE` | `max(member_scores)` | 任一成员命中即可 |
| `OR` | `max(member_scores)`，多个 exact 命中再加 bonus | 满足任一成员即可 |
| `AND` | `weighted_hits / total_weight - 0.14 * missing_weight / total_weight` | 必须尽量同时满足 |
| `AT_LEAST_K` | 前 `k` 个加权命中 / 所需权重 | 至少满足 K 个 |
| `PARENT_ANY_CHILD` | 任一 child 高命中则直接高分 | 父类命中任一子类即可 |

`member_match_score` 决定单个 member 的命中分，核心是：

| 情况 | 结果 |
|---|---|
| query member 在 candidate unit 中精确出现 | `1.0 * constraint_alignment` |
| query member 的 descendant 在 candidate unit 中出现 | `1.0 * constraint_alignment` |
| query member 的 ancestor 在 candidate unit 中出现 | `0.18 * constraint_alignment` |
| 以上都没有，但 query member 在 candidate exact elements 中 | `background` 档或 `0.12` |
| 都没有 | `0.0` |

`constraint_alignment` 则把“强约束对强约束”与“强约束对背景”区分开。例如：`must_have -> must_have = 1.0`，`must_have -> preferred = 0.72`，`must_have -> background = 0.44`，`strong_preference -> background = 0.58`。

### B4. 逐项判分说明

#### 原句：`Software Engineering, Scala, Java, C++, C`

| unit | logic | weight(unit/effective) | top1命中分 | 为什么是这个分 |
|---|---|---:|---:|---|
| `RESP_SOFTWARE_DEVELOPMENT` | `SINGLE` | `0.9400 / 1.0076` | `0.5800` | 候选有软件开发职责的弱对齐，但不是强精确命中，所以只拿到中等分。 |
| `CONSTRAINT_ENGINEERING_FIELD` | `SINGLE` | `0.9200 / 0.9676` | `1.0000` | 工程背景约束精确/等价命中，因此满分。 |
| `TECH_SCALA` | `SINGLE` | `0.9800 / 1.1172` | `1.0000` | Scala 是强精确命中。 |
| `TECH_JAVA` | `SINGLE` | `0.9800 / 1.0650` | `1.0000` | Java 同样是精确命中。 |
| `TECH_CPP` | `SINGLE` | `0.9800 / 1.0737` | `0.1800` | 没有精确 C++，只剩上位编程语言信号，所以弱分。 |
| `TECH_C` | `SINGLE` | `0.9800 / 1.1026` | `0.1800` | 和 C++ 类似，只拿到泛化语言层级的弱命中。 |

#### 原句：`3+ years of hands-on software engineering experience, Designing, building, and maintaining full stack codes utilizing various technical languages e.g. Scala, Java, C++, C, C#, Python, SQL`

| unit | logic | weight(unit/effective) | top1命中分 | 为什么是这个分 |
|---|---|---:|---:|---|
| `RESP_SOFTWARE_DEVELOPMENT, RESP_FULLSTACK_DEVELOPMENT` | `AND` | `1.2200 / 1.2550` | `0.1387` | AND 要同时满足两个 member，但候选只对其中一部分有弱支持，另一部分缺失，missing_weight 拉低分数。 |
| `CONSTRAINT_ENGINEERING_FIELD` | `SINGLE` | `1.1600 / 1.1771` | `1.0000` | 工程背景是硬命中。 |
| `TECH_SCALA` | `SINGLE` | `1.2200 / 1.2688` | `1.0000` | 精确命中。 |
| `TECH_JAVA` | `SINGLE` | `1.2200 / 1.2502` | `1.0000` | 精确命中。 |
| `TECH_CPP` | `SINGLE` | `1.2200 / 1.2533` | `0.1800` | 仍然只有祖先级别弱命中。 |
| `TECH_C` | `SINGLE` | `1.2200 / 1.2636` | `0.1800` | 同上。 |
| `TECH_CSHARP` | `SINGLE` | `1.2200 / 1.2649` | `0.1800` | 同上。 |
| `TECH_PYTHON` | `SINGLE` | `1.2200 / 1.2402` | `1.0000` | 精确命中。 |
| `TECH_SQL` | `SINGLE` | `1.2200 / 1.2528` | `1.0000` | 精确命中。 |
| `EXP_YOE_3_5` | `SINGLE` | `1.2000 / 1.2219` | `1.0000` | 经验桶正好命中 3 到 5 年。 |

#### 原句：`Troubleshooting code for bugs using various tools available in the IDE and/or logging, Write production-grade, maintainable code primarily for data pipelines leveraging Airflow, Databricks Asset Bundles, or Snowflake in Scala`

| unit | logic | weight(unit/effective) | top1命中分 | 为什么是这个分 |
|---|---|---:|---:|---|
| `TECH_DATABRICKS, TECH_SNOWFLAKE` | `OR` | `1.2600 / 1.3104` | `0.1198` | 两个成员都没有形成强精确命中，只剩很弱的数据平台相关信号。 |
| `TECH_AIRFLOW, TECH_SCALA` | `OR` | `1.2600 / 1.3104` | `0.9244` | Scala 是强命中，OR 只要有一个成员满足即可，所以这个 unit 被显著抬高。 |

#### 原句：`Implement complex data transformations using Spark Structured streaming, Spark SQL and core Spark APIs`

| unit | logic | weight(unit/effective) | top1命中分 | 为什么是这个分 |
|---|---|---:|---:|---|
| `TECH_SQL, TECH_API` | `AND` | `1.2600 / 1.2925` | `0.4078` | SQL 命中强，但 API 不完整，AND 会把缺失成员的权重扣掉。 |
| `TECH_SPARK` | `SINGLE` | `1.2200 / 1.2670` | `0.7200` | 不是完整 Spark API 精确覆盖，但有较强的数据处理邻近信号。 |

#### 原句：`Designing and implementing relational and non-relational database schemas e.g. MySql, Mongodb, Dynamodb`

| unit | logic | weight(unit/effective) | top1命中分 | 为什么是这个分 |
|---|---|---:|---:|---|
| `TECH_DATABASE` | `SINGLE` | `1.2200 / 1.2514` | `1.0000` | 候选在数据库/schema 层面有直接命中。 |
| `TECH_MYSQL` | `SINGLE` | `1.2200 / 1.2688` | `0.1296` | 没有 MySQL 精确命中，只剩祖先或弱相关数据库信号。 |
| `TECH_MONGODB` | `SINGLE` | `1.2200 / 1.2688` | `0.1296` | 和 MySQL 一样，只有弱相关信号。 |
| `TECH_DYNAMODB` | `SINGLE` | `1.2200 / 1.2688` | `0.7200` | 比 MySQL/MongoDB 强一些，有更接近的 NoSQL / datastore 信号。 |

#### 原句：`Bachelor's Degree in Computer Science or relevant technical field`

| unit | logic | weight(unit/effective) | top1命中分 | 为什么是这个分 |
|---|---|---:|---:|---|
| `CONSTRAINT_COMPUTER_SCIENCE` | `SINGLE` | `1.1600 / 1.1825` | `0.7200` | 不是绝对精确覆盖，但有技术学位/相关学科的较强对齐。 |

#### 原句：`Onsite`

| unit | logic | weight(unit/effective) | top1命中分 | 为什么是这个分 |
|---|---|---:|---:|---|
| `CONSTRAINT_ONSITE` | `SINGLE` | `0.3000 / 0.3040` | `1.0000` | work model 完全对上，但这个 unit 权重很低，所以满分但影响小。 |

### B5. 这张表怎么读

这张表不是在看“哪个词出现最多”，而是在看“哪个结构化 requirement 对最终排序贡献最大”。

先看 `weight(effective)`，它告诉你这条 requirement 是不是高价值、稀缺、应该放大。  
再看 `top1命中分`，它告诉你候选在这一条 requirement 上到底是精确命中、弱命中还是缺失。

在这条 Disney JD 里，拉高分的部分主要是：
- `TECH_SCALA`
- `TECH_JAVA`
- `TECH_PYTHON`
- `TECH_SQL`
- `EXP_YOE_3_5`
- `CONSTRAINT_ENGINEERING_FIELD`
- `TECH_DATABASE`
- `CONSTRAINT_ONSITE`

原因是它们要么是精确 member 命中，要么是非常强的约束对齐，而且很多都属于 `must_have`，所以同时具备高 `unit_weight` 和高 `effective_weight`。  
例如 `TECH_SQL` 和 `TECH_PYTHON` 的 effective weight 都在 `1.24` 到 `1.25` 左右，命中分又是 `1.0`，它们对 `weighted_requirement` 和 `must_score` 的抬升非常明显。  
`CONSTRAINT_ONSITE` 虽然也是 `1.0`，但它的权重只有 `0.3000 / 0.3040`，所以“满分但不太改变总盘”。

拖分的部分主要是：
- `RESP_SOFTWARE_DEVELOPMENT, RESP_FULLSTACK_DEVELOPMENT` 这个 `AND`
- `TECH_DATABRICKS, TECH_SNOWFLAKE` 这个 `OR`
- `TECH_MYSQL`
- `TECH_MONGODB`
- `TECH_CPP`
- `TECH_C`
- `TECH_CSHARP`

原因有三类：
1. `AND` 逻辑更严格，`RESP_FULLSTACK_DEVELOPMENT` 没被完整覆盖，所以整个 AND unit 被压低。
2. `OR` 逻辑虽然宽松，但前提是要有一个成员真的强，`TECH_DATABRICKS, TECH_SNOWFLAKE` 两个都不够强，所以低。
3. C / C++ / C#、MySQL、MongoDB 这类 unit 都是高权重 must-have，但 candidate 只给了祖先级别或弱对齐，一旦 `member_match_score` 只剩 `0.18` 或 `0.1296`，而 unit 权重又高，这些项就会明显拖低总分。

最重要的一点是，**总分不是所有 unit 的简单平均**。高 `effective_weight` 的 unit，特别是 `must_have` 里的精确命中或高质量弱命中，会比低权重背景项更能决定排名。`Onsite` 即使满分，也不会像 `Scala / Java / SQL / YOE` 那样显著改变候选位置。

### B6. 关键代码依据

| 位置 | 作用 |
|---|---|
| [match_pipe/units.py:94](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/match_pipe/units.py:94) | `_text_blocks()`，把 JD 拆成 title / summary / core_skills / must_have / preferred / responsibilities / metadata |
| [match_pipe/units.py:196](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/match_pipe/units.py:196) | `_infer_logic_type()`，识别 `SINGLE / OR / AND / AT_LEAST_K / PARENT_ANY_CHILD` |
| [match_pipe/units.py:239](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/match_pipe/units.py:239) | `_unit_weight()`，计算 `unit_weight` |
| [match_pipe/units.py:265](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/match_pipe/units.py:265) | `_member_weight()`，计算 unit 内成员权重 |
| [match_pipe/matcher.py:402](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/match_pipe/matcher.py:402) | `_score_candidate()`，把各 unit 分合成最终候选分 |
| [match_pipe/matcher.py:508](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/match_pipe/matcher.py:508) | `_semantic_specificity()`，用 IDF 估计稀缺度并放大有效权重 |
| [match_pipe/matcher.py:526](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/match_pipe/matcher.py:526) | `_score_unit()`，计算单个 requirement unit 的命中分 |
| [match_pipe/matcher.py:588](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/match_pipe/matcher.py:588) | `_member_match_score()`，计算单个 member 的 exact / ancestor / background 命中分 |
| [match_pipe/matcher.py:619](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/match_pipe/matcher.py:619) | `_best_structure_alignment()`，计算结构对齐度并影响 OR / AND / AT_LEAST_K / PARENT_ANY_CHILD |

---

## 十五、附录C：第十二部分三类风险的细化解释与案例映射

### 1. 旧 benchmark 过度奖励 `duplicate` 和 `same-company`

这句话的意思不是“系统只能看公司名”，而是 benchmark 的正例构造太偏旧世界的重复样本，所以只要 matcher 会吃到同公司、同标题、近重复的红利，就能拿到很高分。

| 当前字段 | 当前数值 | 真实含义 |
|---|---:|---|
| `benchmark_audit.standard.case_count` | `208` | 旧标准集样本多，但构造偏重复 |
| `benchmark_audit.standard.same_company_positive_ratio` | `1.0` | 正例全部同公司 |
| `benchmark_audit.standard.exact_title_positive_ratio` | `1.0` | 正例全部同标题重复 |
| `benchmark_audit.hard.case_count` | `68` | 旧 hard 集仍然不纯 |
| `benchmark_audit.hard.same_company_positive_ratio` | `1.0` | 仍然完全吃 same-company 偏置 |
| `benchmark_audit.hard.exact_title_positive_ratio` | `1.0` | 仍然完全吃 exact-title 偏置 |
| `benchmark_audit.rebuilt_hard.case_count` | `33` | 开始接近纯语义 |
| `benchmark_audit.rebuilt_hard.same_company_positive_ratio` | `0.0` | 去掉 same-company 主导 |
| `benchmark_audit.rebuilt_hard.exact_title_positive_ratio` | `0.26` | 只剩少量标题重复 |

实现上，这不是隐式偏差：`purity_audit_runner.py` 把 `same_company` 和 `duplicate` 单独列成特征，`benchmark.py:351-373` 直接统计 `same_company_positive_ratio` 和 `exact_title_positive_ratio`，而 `matcher.py:652-669` 的 `_metadata_score()` / `_duplicate_score()` 又把 `same_company`、`title_exact`、`title_overlap` 真正放进最终打分里，所以这类 bias 会真实抬分。

对 Disney 这个例子来说，它**不能直接证明** same-company bias，因为当前 top1 是跨公司候选 `Amazon | Data Engineer II, Amazon Payment Products`，不是同公司结果。Disney 这个单例能说明的是：在 `teacher_b_pure_semantic` 下，系统可以依靠结构化语义把跨公司候选推到第一；但“旧 benchmark 过度奖励 duplicate/same-company”这件事，要靠上面的 audit 字段来证明，而不是靠 Disney 单例本身。

最小额外证据可以直接引用 `output/analysis/match_pipe_purity_audit.json` 里的 audit 字段，以及 `match_pipe/matcher.py:146-160` 里 `teacher_b_pure_semantic` 关闭 `same_company` / `duplicate` 相关能力的配置。

### 2. 纯语义 `hard` 集与 `gold` 集规模仍偏小

这句话的意思是：现在 benchmark 终于更纯了，但样本量还不足以稳定刻画尾部错误，尤其是分类边界、parent-child、must/preferred 这类细粒度问题。一个样本的得失会明显改变比例。

| 当前字段 | 当前数值 | 含义 |
|---|---:|---|
| `benchmark_suite.rebuilt_hard_case_count` | `33` | 纯语义 hard 集只有 33 条 |
| `semantic_freeze_report.semantic_gold.case_count` | `29` | 人工/半人工 gold 也只有 29 条 |
| `semantic_freeze_runner._build_gold_set().category_limits` | `6/4/5/5/5/5` | 每个类别都被强行限额，说明不是大规模金标 |
| `semantic_freeze_report.boundary_policy.active_boundary_case_count` | `1` | 当前只有 1 条 active boundary case |
| `semantic_freeze_runner._freeze_decision().criteria.rebuilt_hard_hit_at_1_min` | `0.55` | 冻结门槛建立在小集合上 |
| `semantic_freeze_runner._freeze_decision().criteria.gold_hit_at_1_min` | `0.68` | gold 门槛同样基于小样本 |

这不是抽象担忧，而是直接的统计稳定性问题。`33` 条样本里，单条样本就会让 `hit@1` 变化约 `3.03%`；`29` 条 gold 里单条样本会让 `hit@1` 变化约 `3.45%`。而类别级别只有 `6` 条时，单条样本就会让类别 `hit@1` 变化 `16.67%`。这就是为什么当前报告里 `critical_category_hit_at_3_min = 0.5` 这种阈值能过，但你仍然不能把它当成“大样本已收敛”。

Disney 单例在这里也**不足以直接证明**这个风险，因为它只展示了一条 query 的局部行为，不能说明 benchmark 的方差是否足够小。真正说明问题的是 `semantic_freeze_runner.py:118-190` 里的 `_build_gold_set()` 和 `category_limits`，以及 `semantic_freeze_runner.py:462-476` 里的 freeze criteria。换句话说，Disney 只能当案例，不能当统计结论。

如果要补一个最小额外案例，`output/analysis/match_pipe_semantic_freeze_report.json` 里这条最合适：`69d83774869c7e25d859479c::must_vs_preferred_confusing`，它的 rationale 已经说明 generic-title query 可能对应多个 acceptable positives，所以 gold 集必须允许 boundary / multi-positive，而不能硬压成单解。

### 3. `must vs preferred` 与 `parent-child` 仍是最脆弱的规则层

这句话的意思是两类问题最容易把“语义上差一点”的候选排到“应该更优”的候选前面。

| 当前字段 | 当前数值 | 含义 |
|---|---:|---|
| `semantic_freeze_report.category_metrics.must_vs_preferred_confusing.case_count` | `6` | 这类样本只有 6 条 |
| `semantic_freeze_report.category_metrics.must_vs_preferred_confusing.hit_at_1` | `0.3333` | Top1 只有 1/3 正确 |
| `semantic_freeze_report.category_metrics.must_vs_preferred_confusing.hit_at_3` | `0.6667` | Top3 也只是中等 |
| `semantic_freeze_report.category_metrics.parent_child_conflict.case_count` | `6` | parent-child 冲突同样只有 6 条 |
| `semantic_freeze_report.category_metrics.parent_child_conflict.hit_at_1` | `0.5` | Top1 只有一半正确 |
| `semantic_freeze_report.category_metrics.parent_child_conflict.hit_at_3` | `0.8333` | Top3 仍有漏失 |
| `semantic_freeze_runner._freeze_decision().criteria.critical_category_hit_at_3_min` | `0.5` | 这些类别正是 freeze 的硬门槛之一 |

`must vs preferred` 的真实含义是：系统把“应该是必须项”的信号，误让位给了“只是偏好项”的表层重合。`parent-child` 的真实含义是：taxonomy 里的父节点、兄弟节点、或更泛化的祖先节点，抢走了真正 child 节点的排名。

代码上，`match_pipe/matcher.py:588-642` 的 `_member_match_score()` 和 `_best_structure_alignment()` 已经把这个问题写进去了：exact / descendant 命中给满分，ancestor 只给 `0.18` 倍；同时还要乘上 `logic_alignment` 和 `content_alignment`。这意味着一旦 taxonomy 粗、候选又有父级泛化覆盖，分数就可能看起来“还不错”，但其实漏掉了真正该命中的 child。

Disney 这个例子里，`parent-child` 风险是可以**部分体现**的：`TECH_DATABASE = 1.0000`，但 `TECH_MYSQL = 0.1296`、`TECH_MONGODB = 0.1296`、`TECH_DYNAMODB = 0.7200`。这说明候选对“数据库父类概念”命中很强，但对具体 child 节点并不均匀，正是 parent-child 结构容易出问题的典型形态。  
但 Disney **不能直接体现** `must vs preferred`，因为这个 JD 里没有显式的 `preferred_quals` 主导冲突；它更像是 `must_have` 和 `strong_preference` 混合的结构化 JD。要看 `must vs preferred` 的直接样本，应该引用 `69d83774869c7e25d859479c::must_vs_preferred_confusing`，其 rationale 明确写着 “Must-have alignment should outrank preferred-only overlap.”  
要看 `parent-child` 的直接样本，可以引用 `69d83b10f4ea471a51fe4be1::parent_child_conflict`，其 rationale 明确写着更具体的 child units 应该压过更宽的兄弟/父级角色。

### 代码与报告依据

| 依据 | 位置 |
|---|---|
| `benchmark.py` 旧 benchmark 审计 | `match_pipe/benchmark.py:351-373` |
| `purity_audit_runner.py` 特征归因 | `match_pipe/purity_audit_runner.py:107-165` |
| `semantic_freeze_runner.py` gold 构造 | `match_pipe/semantic_freeze_runner.py:118-190` |
| `semantic_freeze_runner.py` freeze 门槛 | `match_pipe/semantic_freeze_runner.py:462-476` |
| `semantic_freeze_runner.py` boundary policy | `match_pipe/semantic_freeze_runner.py:690-694` |
| `units.py` 切块 / 逻辑识别 / 权重 | `match_pipe/units.py:94-120, 196-210, 239-275, 383-444` |
| `matcher.py` 语义 specificity / unit score / hierarchy | `match_pipe/matcher.py:508-642, 652-669` |
