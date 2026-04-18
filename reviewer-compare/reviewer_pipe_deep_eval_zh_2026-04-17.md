# Reviewer Pipe 深度评估（中文）

日期：2026-04-17

## 产物范围

本报告基于以下两轮 Codex-only 跑分结果：

- 新 pipe（`Reviewer_4Stage.md` + `Reviewer_Cal.py`）：
  [reviewer-compare/runs/20260417_185315_270748](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/runs/20260417_185315_270748)
- 旧 pipe（原 `UnifiedReviewer` prompt + system，已隔离）：
  [reviewer-compare/old-pipe-codex/runs/20260417_185315_269474](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/old-pipe-codex/runs/20260417_185315_269474)

使用的 10 组 case：

1. `same/Microsoft`
2. `same/Google`
3. `same/Amazon`
4. `same/AWS`
5. `extra/Dataminr-Infra`
6. `extra/Zoox-LLM`
7. `extra/Synechron-Backend`
8. `extra/CapitalOne-AI`
9. `extra/Ramp-Platform`
10. `extra/HealthEquity-DotNet`

说明：

- 前 4 组有历史 Claude/official 基线，可做更完整纵向参照。
- 后 6 组没有完整恢复出的历史 Claude target 基线，因此本报告主要用于“旧 pipe Codex vs 新 pipe Codex”的横向扩样本对比。

## 一页结论

先说结论：

1. 在 Codex 模式下，**新 pipe 明显更慢**，总耗时约 **13分59秒**，旧 pipe 约 **8分41秒**；新 pipe 平均每组 **83.9 秒**，旧 pipe **52.1 秒**，约慢 **1.67x**。
2. 在 10 组样本上，**旧 pipe 5 组 pass / 5 组 fail**，而 **新 pipe 10 组全部 fail**。
3. 新 pipe 的全员降分，**不全是发现了旧 pipe 没识别的真实硬伤**。它确实抓到了一批真实问题，但当前更主要的现象是：
   - 把一类“全样本共享的锚点冲突”放大成了系统性硬失败；
   - 把一类“写法层面的合理问题”重复累计成了过重扣分；
   - 导致诊断价值变强，但 gating 校准明显失衡。

我的判断：

- **旧 pipe 更适合继续做生产 gating。**
- **新 pipe 更适合先做 shadow reviewer / 诊断 reviewer。**

## 时长对比

### 总体

| 指标 | 旧 pipe Codex | 新 pipe Codex |
| --- | ---: | ---: |
| 总耗时 | 521 秒 | 839 秒 |
| 平均每组 | 52.1 秒 | 83.9 秒 |
| 中位数 | 47.5 秒 | 76.0 秒 |
| 平均耗时倍率 | 1.00x | 1.67x |

### Case 级时长与分数

| Case | 旧分 | 新分 | 分差 | 旧耗时(秒) | 新耗时(秒) |
| --- | ---: | ---: | ---: | ---: | ---: |
| same/Microsoft | 88.1 | 80.9 | -7.2 | 54 | 121 |
| same/Google | 79.0 | 83.4 | +4.4 | 49 | 57 |
| same/Amazon | 93.3 | 89.8 | -3.5 | 46 | 81 |
| same/AWS | 94.6 | 81.5 | -13.1 | 42 | 53 |
| extra/Dataminr-Infra | 92.8 | 84.5 | -8.3 | 60 | 71 |
| extra/Zoox-LLM | 94.4 | 88.8 | -5.6 | 40 | 114 |
| extra/Synechron-Backend | 89.5 | 89.5 | 0.0 | 63 | 98 |
| extra/CapitalOne-AI | 89.2 | 83.9 | -5.3 | 46 | 62 |
| extra/Ramp-Platform | 97.0 | 89.8 | -7.2 | 75 | 71 |
| extra/HealthEquity-DotNet | 93.5 | 79.5 | -14.0 | 46 | 111 |

观察：

- 新 pipe 只有 `same/Google` 一组比分旧 pipe 更高，`extra/Synechron-Backend` 持平，其余 **8/10 全部更低**。
- 新 pipe 在 `Microsoft`、`Zoox`、`HealthEquity` 上明显更慢，说明其在结构化分阶段判定上触发了更多长推理路径。

## 失分点分别是什么

### 旧 pipe 的主要失分点

旧 pipe 的失分主要集中在这几类：

1. **首屏 framing 不够像目标岗位本人**
   - `same/Microsoft`：开头先讲转行，而不是先讲 Azure / distributed backend。
   - `extra/CapitalOne-AI`：`Data Analysis Candidate` 太像状态描述，不像直接角色定位。
   - `same/Amazon`、`extra/Dataminr-Infra` 也有类似 summary 信号排序问题。

2. **JD 关键技术或关键语义没有显式露出**
   - `same/Microsoft`：`Distributed Systems` 没有显式出现在 Skills。
   - `same/Google`：TikTok 项目里用了 `AWS Bedrock`，但 Skills 里没列，旧 pipe 直接把这视为真实性/出处一致性问题。
   - `extra/CapitalOne-AI`：数据分析/BI 业务支持信号不够前置。

3. **结构/格式有明确但局部的硬约束问题**
   - `extra/Synechron-Backend`：Summary 不是精确的 3 句 `**小标题:**` 结构。
   - `extra/Dataminr-Infra`：第三句是低信号 cognition header。

4. **少量 case 会质疑 scope 过宽**
   - `same/Microsoft`：TikTok 一段同时覆盖过多语言与栈，像“拼接”而非聚焦 ownership。

旧 pipe 的特点是：

- 它更偏“少量高价值问题”的审查。
- 它会 fail，但通常是因为 1-2 个明确的首屏或一致性问题，而不是整页所有问题一起被累计压死。

### 新 pipe 的主要失分点

新 pipe 的失分点高度集中，前四名几乎就是整轮实验的主旋律：

1. `P3E-002`：**Temu 时间锚点冲突**
   - **10/10 case 全命中**
   - 直接把 `r7_ecosystem` 平均分打到 **6.0**
   - 是本轮全员 fail 的最强共因

2. `P2-020`：**首页第一段第一条 bullet 没有 Tier 1 scope anchor**
   - **10/10 case 全命中**
   - 它抓到的是“首屏最强信号没有前置”的问题，这个洞察本身有价值

3. `P3D-001`：**整份简历过度依赖 Tier 2 百分比结果，缺 Tier 1 规模信号**
   - **9/10 case 命中**
   - TikTok、DiDi、Temu 常被同时命中，导致同一问题家族被多次累计处罚

4. `P1-040 / P1-042`：**加粗纪律/格式纪律**
   - 各自 **6/10 case 命中**
   - 多数是“有价值但不该重罚”的格式类问题

其次才是：

- `P2-001`：transition framing 过强，4/10
- `P3B-003`：JD bridge 不够显式，4/10
- `P3C-010/011`：多语言/多栈 ownership 过宽，5/10 合计

新 pipe 的特点是：

- 它把“结构化诊断”做得更系统。
- 但它的失分重心并不是均匀分布，而是被 `P3E-002 + P2-020 + P3D-001` 这三类问题强烈主导。

## 分数全员下降，是真硬伤还是“鸡蛋里挑骨头”？

答案是：**两者都有，但当前更偏“真实问题 + 过度累计惩罚”叠加。**

### 确实是旧 pipe 相对低估的真实问题

这些不是鸡蛋里挑骨头，而是新 pipe 抓到的真实简历弱点：

1. **Summary 首句的角色信号排序**
   - 很多简历首句先讲 “transition / bridge / candidate”，而不是直接讲目标岗位身份。
   - 这确实会影响 6-8 秒 recruiter 首屏判断。

2. **第一条 bullet 缺 Tier 1 scope**
   - 很多 case 的首条 bullet 先给时间缩短、提升百分比，而不是先给规模 / throughput / system scope。
   - 这确实会削弱 senior / infra / platform 角色的说服力。

3. **过度依赖 Tier 2 指标**
   - 百分比、分钟级缩短、pilot usage 增长很多，但缺少 QPS / 事件量 / 服务规模 / 团队范围。
   - 这也是实打实的问题，尤其对 backend / infra / platform / senior MLE 岗。

4. **多语言 ownership 表达过宽**
   - 在个别 case，TikTok 一段实习同时承担太多语言/基础设施主责，确实会让面试官怀疑 scope 拼接。

### 更像“鸡蛋里挑骨头”或至少“当前被罚过头”的部分

1. **`P3E-002` 全样本 universal hard fail**
   - 它在 10/10 case 上全部命中，已经不是“个别简历发现问题”，而是“整个 synthetic corpus 与规则硬冲突”。
   - 如果这条经历本身是教学数据里的不可变字段，那么它不应该再被作为每个 target case 的主要 fail 触发器反复计入。
   - 这是当前新 pipe 最大的校准问题。

2. **同一问题家族被重复累计**
   - `P3D-001` 经常在 TikTok、项目、Temu 三个位置分别报一遍。
   - 这有诊断价值，但不应该在分数上近似当作三个独立大问题来打。

3. **格式纪律被放大到 pass/fail 边界**
   - `P1-040`、`P1-042`、`P1-051` 这些结构/格式问题，有用，但通常不该和真实性或 chronology 冲突处于同一个 fail 量级。

4. **新 pipe 也漏掉了旧 pipe 识别到的一些真问题**
   - 最典型的是 `same/Google`：
     - 旧 pipe 抓到了 `AWS Bedrock` 在正文里出现但 Skills 没列，这属于很真实的“技术出处一致性”问题。
     - 新 pipe 这轮没把它作为主要问题抓出来，反而因为没命中这条，分数还比旧 pipe 更高。

这说明：

- 新 pipe 并不是单向更强。
- 它在某些真实性/技能出处一致性细节上，反而比旧 pipe 更弱。

## 我如何评估新 reviewer pipe

结论先行：

- **诊断能力：强于旧 pipe**
- **生产 gating 能力：弱于旧 pipe**
- **当前状态：适合 shadow，不适合直接替代**

### 1. Prompt 结构设计

优点：

- 四阶段分工清楚，模型更容易按“结构、首屏、内容、生态/锚点”拆开思考。
- rule id 稳定，后续便于统计、比对、调权重。

问题：

- 当前 prompt 把一部分“教学语料不可变字段的系统冲突”直接混进 case 级评分。
- 导致模型虽然遵守规则，但结果偏离“是否适合作为教学发布材料”的真实业务目标。

判断：

- Prompt 的可审计性明显提升。
- 但业务目标和规则目标还没有完全对齐。

### 2. Pass 1 Structural Layer

表现：

- 10 组里 9 组有 Pass 1 finding，平均 **1.7 条/组**。
- 主要抓到加粗纪律、Skills 密度、个别 verb/format 规则。

优点：

- 适合做 hygiene gate。
- 能把“排版不规范、格式不一致、skills 过密”这类问题规范化。

问题：

- 多数命中是 medium 格式问题，业务影响相对有限。
- AWS 上 `P1-051` 触发明显拉分，但这类问题是否应强推到 fail 仍值得商榷。

评价：

- **有价值，但应该更轻量、更像 lint，而不是大分值惩罚器。**

### 3. Pass 2 Attention Layer

表现：

- 10/10 case 都有 Pass 2 finding，平均 **1.9 条/组**。
- `P2-020` 10/10 全命中；`P2-001` 4/10；`P2-010` 2/10。

优点：

- 这是新 pipe 最有产品价值的部分之一。
- 它把 recruiter 首屏感知问题讲得比旧 pipe 更清楚、更稳定。

问题：

- `P2-020` 几乎 universal，说明当前判据可能过于理想化。
- 如果所有简历第一条 bullet 都被要求是 Tier 1 scope，那么这个规则更像“写法偏好”，不完全是“失分点”。

评价：

- **洞察对，但罚分偏重。**
- 建议保留为强诊断信号，降低其对总分的直接杀伤。

### 4. Pass 3A Authenticity

表现：

- 只在极少数 case 起作用，本轮只有 1 次命中。

优点：

- 如果它命中，通常应当很重要。

问题：

- 它没有补上旧 pipe 在 `same/Google` 那种“正文技术在 Skills 缺失”的一致性检查能力。
- 这说明新 pipe 的 authenticity 桶目前**不够完整**。

评价：

- **目前是薄弱环节。**
- 建议把旧 pipe 的双向技术出处一致性检查补回来。

### 5. Pass 3B JD Fitness

表现：

- 命中不算高频，但在 `Microsoft`、`HealthEquity`、`Zoox` 这类 case 上能抓到“bridge 不够显式”的问题。

优点：

- 比旧 pipe 更擅长把“为什么这个 JD bridge 不够直给”说清楚。
- 对 `Distributed Systems`、`Agile`、`Spark` 这类 must-have 暴露度比较敏感。

问题：

- 有时会向“ATS exactness”滑得太近。
- 例如 `Spark` 只以 `Spark SQL` 形式出现就被判覆盖偏弱，这在真实筛选中未必该算 high。

评价：

- **可用，但要防止 token-level 过拟合。**

### 6. Pass 3C Overqualification / Scope Plausibility

表现：

- 主要命中 `same/Microsoft`、`extra/Zoox-LLM` 一类多语言/多栈过宽的 case。

优点：

- 比旧 pipe 更会拆“stack stuffing”和“ownership 不聚焦”的问题。
- 对 hiring manager 视角是有价值的。

问题：

- 有些简历本来就是跨语言协作型经历，新 pipe 容易把“接触过多栈”读成“claim 过度”。

评价：

- **方向是对的，但应加强‘主责 vs 支撑’的判定弹性。**

### 7. Pass 3D Rationality / Signal Quality

表现：

- 10 组里 9 组命中，且经常在同一 case 里命中多次。
- 新 pipe 的 `r4_rationality` 平均分只有 **6.6**，是全局最低维度。

优点：

- 它真正抓到了这批简历的共同短板：Tier 2 指标很多，Tier 1 规模锚点不够。
- 这是这轮里最有参考价值的“新洞察”之一。

问题：

- 同一家族问题重复扣分太狠。
- 它已经不只是“指出问题”，而是在数学上把大量 case 压到了 fail。

评价：

- **这是新 pipe 最值得保留的核心能力之一，但必须重做聚合策略。**

### 8. Pass 3E Ecosystem / Public Anchor

表现：

- `P3E-002` 10/10 全命中。
- 新 pipe 的 `r7_ecosystem` 平均分被打到 **6.0**。

优点：

- 对真实世界投递，时间线/public anchor 检查当然重要。

问题：

- 这是本轮最大失真来源。
- 当一条 synthetic 不可变字段与规则锚点先天冲突时，把它反复当作每个 target case 的 critical 主因，不是在评估 target resume，而是在反复惩罚 corpus 本身。

评价：

- **当前版本不适合直接进入总分。**
- 更合理的做法是：
  - 先做 corpus-level precheck；
  - 或者改成单独阻断标签，不进入 case 级 weighted score；
  - 或者对已知 immutable synthetic 冲突做白名单/降级。

### 9. Pass 5 Localization

表现：

- 本轮 10 组完全没有 finding。

评价：

- **当前等于空桶。**
- 如果短期内没有实际信号来源，可以先不进主评分，避免结构复杂度高于真实价值。

### 10. `Reviewer_Cal.py` 的聚合/阈值

这是新 pipe 当前最需要重做的部分。

证据：

- 新 pipe 10/10 全 fail。
- 旧 pipe 还能分出 5 pass / 5 fail。
- 新 pipe 平均维度分里，`r4_rationality = 6.6`，`r7_ecosystem = 6.0`，几乎决定了全局结论。

问题不在“外部数学聚合”这个思路，而在当前的参数化方式：

1. `critical` 的权重过强，且 `P3E-002` 被 universal 触发。
2. 同类 `P3D-001` 会在多个 section 重复扣。
3. `FAIL_THRESHOLD=85`、`REVISION_THRESHOLD=93` 是从旧密度规则迁移过来的，但新规则密度明显更高，阈值没有同步重标定。

评价：

- **外部 deterministic scorer 方向是对的。**
- **当前权重和阈值没有完成校准。**

## 最终判断

### 旧 pipe

- 优点：更接近当前项目的真实发布门槛，误杀更少。
- 缺点：对首屏 framing、Tier 1 scope、Tier 2 过载这类问题提醒得不够系统。

### 新 pipe

- 优点：更可审计，更可统计，问题 taxonomy 更稳定，诊断深度更高。
- 缺点：当前被 `P3E-002` 和重复 `P3D-001` 绑架，导致分数和 verdict 明显失真。

### 建议

1. 继续保留旧 pipe 作为生产 gating。
2. 新 pipe 先作为 shadow reviewer 挂一段时间。
3. 新 pipe 在上线前至少要做四件事：
   - 把 `P3E-002` 从 case-level weighted score 中拆出去，或做 immutable synthetic 白名单。
   - 给 `P3D-001` 做去重/上限，不要在同一家族问题上无限叠罚。
   - 把旧 pipe 的“正文技术 <-> Skills 双向一致性检查”补回新 pipe。
   - 重新标定阈值，不要继续沿用旧 reviewer 的 `85/93` 边界。

## 结论句

如果问我现在是否建议用新 pipe 替代旧 pipe：

- **不建议。**

如果问我新 pipe 值不值得继续做：

- **值得，而且值得继续。**

因为它已经证明了自己在“诊断能力”上比旧 pipe 更强；只是它还没有完成从“好诊断器”到“好裁判”的最后一段校准。
