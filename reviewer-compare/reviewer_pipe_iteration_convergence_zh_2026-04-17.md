# Reviewer Pipe 迭代收敛报告（中文）

## 1. 结论

本轮从当前 `v1` 出发，完成了 `v2`、`v3`、`v4`、`v5`、`v6` 五轮改造与全量 10 case 测试。

**最终推荐版本不是最新的 `v6`，而是 [`v3_hr_stable/Reviewer_4Stage.md`](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iterations/v3_hr_stable/Reviewer_4Stage.md) + [`v3_hr_stable/Reviewer_Cal.py`](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iterations/v3_hr_stable/Reviewer_Cal.py)。**

原因很简单：

1. `v3` 是唯一一个在我基于真实 HR 视角建立的 10 case 目标标签上做到 **10/10** 命中的版本。
2. `v4`、`v5`、`v6` 虽然分别尝试修复 `HealthEquity`、`exact token`、`平台家族/年限` 等问题，但都出现了新的系统性回摆。
3. 继续迭代已经进入“修一个 case、坏另一个 case”的过拟合状态，不再是净改进。

本轮所有比较表和中间产物都在 [`reviewer-compare`](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare) 下；全量版本对照表见 [`iteration_comparison_v6.md`](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration_comparison_v6.md)。

## 2. 评估口径

### 2.1 我采用的“真实 HR 目标标签”

这不是外部官方标签，而是我基于 10 份简历原文、目标 JD、旧 pipe/new pipe 历史输出，以及你要求的“通过 reviewer 的简历也应能过真实 HR 初筛”的标准，做出的**推定 ground truth**：

| Case | 目标标签 |
| --- | --- |
| same/Microsoft | fail |
| same/Google | pass |
| same/Amazon | pass |
| same/AWS | pass |
| extra/Dataminr-Infra | pass |
| extra/Zoox-LLM | pass |
| extra/Synechron-Backend | pass |
| extra/CapitalOne-AI | fail |
| extra/Ramp-Platform | pass |
| extra/HealthEquity-DotNet | fail |

### 2.2 为什么这样判

- `same/Microsoft`：`Distributed Systems` 是 Azure Storage 的硬门槛，当前简历虽有相关证据，但命名信号和首屏可读性仍不足，真实 HR/ATS 风险高。
- `same/Google`：核心多语言 full-stack 能力是够的，`AWS Bedrock` 出现在正文但 Skills 未列属于应修问题，不应直接误杀。
- `same/Amazon`：可过。
- `same/AWS`：不应因“可能存在合规歧义”被直接 hard fail；当前表述更像应修改的 caution，不像硬违规。
- `extra/Dataminr-Infra`：旧 pipe 的失败主要是 summary 颗粒度，不是结构性不适配，真实 HR 更可能给面试。
- `extra/Zoox-LLM`：主问题是栈呈现收敛，不是结构性 fail。
- `extra/Synechron-Backend`：应过。
- `extra/CapitalOne-AI`：`Manager` scope 明显缺失，真实 HR 很难放行。
- `extra/Ramp-Platform`：应过，但要有 infra/ownership/scope 呈现；不能被 Temu 或模糊合规猜测误杀。
- `extra/HealthEquity-DotNet`：虽然技能表面覆盖不少，但对 `6+ years`、Microsoft stack depth、healthcare/regulated bridge 的门槛仍不足，真实 HR 仍偏 fail。

## 3. 各版本总体表现

| 版本 | pass/fail | 平均分 | 平均耗时 | 总耗时 | 与目标标签一致 |
| --- | --- | ---: | ---: | ---: | --- |
| old_pipe | 5 / 5 | 91.14 | 52.1s | 521.0s | 6/10 |
| v1_current | 0 / 10 | 85.16 | 83.9s | 839.0s | 3/10 |
| v2_hr_recal | 8 / 2 | 94.44 | 58.8s | 588.0s | 5/10 |
| v3_hr_stable | 7 / 3 | 94.65 | 56.8s | 568.0s | **10/10** |
| v4_hr_converged | 8 / 2 | 94.71 | 56.7s | 567.0s | 7/10 |
| v5_hr_gate | 9 / 1 | 96.47 | 58.6s | 586.0s | 8/10 |
| v6_hr_final | 9 / 1 | 96.01 | 60.6s | 606.0s | 8/10 |

**解读**

- `v1` 的问题最明显：零通过，而且大量误杀。
- `v2` 把 Temu 误杀和 AWS/Ramp 的合规误杀拉回来了一部分，但开始把结构性错配放成 pass。
- `v3` 是平衡点。
- `v4-v6` 的平均分更高，不代表更好；它们是在**放松门槛**，不是在变准。

## 4. 全量 10 Case 分数表

| Case | old_pipe | v1_current | v2_hr_recal | v3_hr_stable | v4_hr_converged | v5_hr_gate | v6_hr_final |
| --- | --- | --- | --- | --- | --- | --- | --- |
| extra-capitalone-ai | 89.2 (fail) | 83.9 (fail) | 95.2 (pass) | 87.9 (fail) | 88.6 (fail) | 91.9 (fail) | 96.2 (pass) |
| extra-dataminr-infra | 92.8 (fail) | 84.5 (fail) | 97.4 (pass) | 99.0 (pass) | 98.5 (pass) | 95.5 (pass) | 98.5 (pass) |
| extra-healthequity-dotnet | 93.5 (pass) | 79.5 (fail) | 88.8 (pass) | 89.6 (fail) | 88.6 (pass) | 97.0 (pass) | 94.5 (pass) |
| extra-ramp-platform | 97.0 (pass) | 89.8 (fail) | 95.8 (fail) | 97.1 (pass) | 100.0 (pass) | 100.0 (pass) | 97.3 (pass) |
| extra-synechron-backend | 89.5 (fail) | 89.5 (fail) | 95.0 (pass) | 99.2 (pass) | 100.0 (pass) | 100.0 (pass) | 99.7 (pass) |
| extra-zoox-llm | 94.4 (pass) | 88.8 (fail) | 96.8 (pass) | 96.8 (pass) | 96.4 (pass) | 96.5 (pass) | 98.6 (pass) |
| same-amazon | 93.3 (pass) | 89.8 (fail) | 97.8 (pass) | 95.0 (pass) | 95.3 (pass) | 97.3 (pass) | 95.8 (pass) |
| same-aws | 94.6 (pass) | 81.5 (fail) | 94.4 (fail) | 97.5 (pass) | 97.7 (pass) | 96.3 (pass) | 96.5 (pass) |
| same-google | 79.0 (fail) | 83.4 (fail) | 92.8 (pass) | 94.1 (pass) | 86.2 (fail) | 94.4 (pass) | 91.2 (pass) |
| same-microsoft | 88.1 (fail) | 80.9 (fail) | 90.4 (pass) | 90.3 (fail) | 95.8 (pass) | 95.8 (pass) | 91.8 (fail) |

## 5. 全量 10 Case 主要扣分项表

| Case | old_pipe 主要扣分 | v1_current 主要扣分 | v2_hr_recal 主要扣分 | v3_hr_stable 主要扣分 | v4_hr_converged 主要扣分 | v5_hr_gate 主要扣分 | v6_hr_final 主要扣分 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| extra-capitalone-ai | r4_rationality:high:Professional Summary | P2-001:high:Summary 第一句<br>P3E-002:critical:Experience | Temu · R&D | Jun 2021 – Feb 2022 | none | P2-001:high:Professional Summary, sentence 1<br>P3B-010:high:Overall target-role fit | P3B-010:high:Summary / 全文经历 | P3B-010:high:Overall role scope / Experience positioning | none |
| extra-dataminr-infra | r1_writing_standard:high:Professional Summary, sentence 3 | P2-010:high:Professional Summary 第三句<br>P3E-002:critical:Temu | Data Analyst | Jun 2021 – Feb 2022 | Shanghai | none | none | none | none | none |
| extra-healthequity-dotnet | none | P2-001:high:Professional Summary 第一句<br>P3B-001:high:Skills section<br>P3E-002:critical:Temu · Data Analyst | Jun 2021 – Feb 2022 | Shanghai | P3B-001:high:Skills section | P3B-001:high:Skills section | P2-001:high:Professional Summary, sentence 1<br>P3B-002:high:Skills + DiDi Experience, `MongoDB` / `Merchant Incident Workbench` project | none | P2-001:high:## Professional Summary, sentence 1 |
| extra-ramp-platform | none | P3E-002:critical:Temu | Data Analyst | Jun 2021 – Feb 2022 | P3E-010:critical:TikTok · Security | Software Engineer Intern | Jun 2025 – Dec 2025 | Bullet 2 | none | none | none | P3C-010:high:Professional Summary, Skills, and cloud-related bullets across TikTok and DiDi |
| extra-synechron-backend | r1_writing_standard:high:Professional Summary | P3E-002:critical:Data Analyst | Temu · R&D | Jun 2021 – Feb 2022 | Shanghai | none | none | none | none | none |
| extra-zoox-llm | none | P3C-010:high:TikTok Experience bullets<br>P3E-002:critical:Temu | Jun 2021 – Feb 2022 | P3C-010:high:TikTok · Security Experience 全段 | P3C-010:high:Skills > Programming; TikTok Experience | P3C-010:high:TikTok · Security intern bullets | none | none |
| same-amazon | none | P3E-002:critical:Temu Experience, header and dates | none | P3C-010:high:TikTok experience section | P3C-010:high:Professional Summary / Skills / Experience | P3C-010:high:TikTok · Security Experience bullets 1-4 | P3C-010:high:Professional Summary sentence 1; TikTok Experience bullets 1-4 |
| same-aws | none | P1-051:high:## Skills<br>P2-001:high:## Professional Summary, bullet 1<br>P2-010:high:## Professional Summary, bullet 3<br>P3E-002:critical:Temu · R&D | Jun 2021 – Feb 2022 | Shanghai | P3E-010:critical:TikTok project: Security Investigation Retrieval Assistant, bullet 2 | none | none | P3C-010:high:Software Engineer Intern | TikTok · Security | none |
| same-google | r0_authenticity:critical:## Skills > Cloud | P2-001:high:Professional Summary, sentence 1<br>P3E-002:critical:Temu · Data Analyst | Jun 2021 – Feb 2022 | Shanghai | P3A-002:high:TikTok Experience, project bullet 1 | P3A-002:high:TikTok · Security / Project: Security Knowledge Retrieval Assistant, bullet 1 | P3A-002:high:TikTok Project: Security Knowledge Retrieval Assistant, bullet 1<br>P3A-003:critical:Professional Summary, sentence 2 | P3A-002:high:TikTok project: Security Knowledge Retrieval Assistant, bullet 1 | P3A-002:high:TikTok project: Security Knowledge Retrieval Assistant, bullet 1<br>P3C-010:high:Professional Summary + TikTok internship section |
| same-microsoft | r2_jd_fitness:high:## Skills<br>r2_jd_fitness:high:Professional Summary / TikTok experience<br>r4_rationality:high:Professional Summary 第 1 句<br>r4_rationality:high:TikTok experience | P3B-001:high:Skills<br>P3C-010:high:TikTok Experience<br>P3E-002:critical:Temu Experience | P3B-001:high:Skills; Professional Summary; TikTok Experience<br>P3C-010:high:Professional Summary; TikTok Experience | P3B-001:high:Skills / Professional Summary | P3C-010:high:Professional Summary + TikTok · Security experience | P3C-010:high:Professional Summary / Skills / TikTok Experience | P3B-001:high:Skills；Professional Summary；TikTok Experience |

## 6. 每轮迭代记录

| 版本 | 改动内容 | 改动原因 | 实测结果 | 结论 |
| --- | --- | --- | --- | --- |
| v1_current | 当前新 pipe baseline | 作为起点 | 0 pass / 10 fail，`P3E-002` 与 `P3D-001` 主导，明显过严 | 不可用 |
| v2_hr_recal | 去掉 Temu 时间误杀；弱化格式/首屏轻微问题；给 `P3D-001` 去重降权；恢复 `P3A-002` 对命名平台的高权重 | 先解决最明显的误杀与分数坍塌 | 8 pass / 2 fail，但放过了 Microsoft / CapitalOne / HealthEquity | 从“过严”修到“过松” |
| v3_hr_stable | 把模糊合规从 hard fail 改成 `P3E-013`；新增 `P3B-010` manager/6+ years gap；新增 `P3B-011` 平台深度 gap；scorer 加结构性 fail gate | 把真正的 HR 拒点重新立起来 | **7 pass / 3 fail，10/10 命中目标标签** | **最佳平衡点** |
| v4_hr_converged | 继续削弱 exact token 倾向，尝试把 HealthEquity 的 fail 原因从 ATS exact match 拉回结构性问题 | 修 `HealthEquity` 的错误失败因 | 8 pass / 2 fail，但错误地 pass `Microsoft`、pass `HealthEquity`、fail `Google` | 发生系统性回摆，拒绝 |
| v5_hr_gate | 回到 v3 主干；把 `P3B-002` 纳入结构性 fail；继续强调不要让近义 token 主导结果 | 想保住 v3 稳定性，同时修 `HealthEquity` | 9 pass / 1 fail，但错误 pass `Microsoft`、pass `HealthEquity` | 仍过松，拒绝 |
| v6_hr_final | 退回 v3 主干，仅在 3B 局部增加例外与示例，不再全局放松 | 最后一轮验证是否能保住 v3 稳定性并修正 HealthEquity | 9 pass / 1 fail，但错误 pass `CapitalOne`、pass `HealthEquity` | 没有超越 v3，停止 |

## 7. 为什么 `v3` 是最佳版本

### 7.1 它是唯一的全局最优点

- `v3`：10/10 命中目标标签。
- `v4`：7/10。
- `v5`：8/10。
- `v6`：8/10。

这里最关键的不是“平均分更高”，而是**该过的过、该挂的挂**。

### 7.2 它同时解决了两个方向的错误

`v3` 是唯一同时做到以下两点的版本：

1. 不再误杀 `AWS`、`Ramp` 这类因为 Temu 或模糊合规而被打挂的 case。
2. 仍然保留对 `Microsoft`、`CapitalOne`、`HealthEquity` 这三类真实结构性问题的 fail 能力。

这就是我判断它最像真实 HR 初筛器的原因。

### 7.3 后续版本都在“局部修复，整体退步”

- `v4` 修了部分 exact-token 倾向，但开始错误放行 `Microsoft` 和 `HealthEquity`，还把 `Google` 打挂。
- `v5` 更明显地变成“高分宽松版 reviewer”，误把 `Microsoft`、`HealthEquity` 放过。
- `v6` 试图回收，但又把 `CapitalOne Manager` 放过。

这说明：**在当前 LLM 单次 reviewer + 外部打分器结构下，继续往“少看 token、多看语义”方向拉，会导致结构性门槛也一起被放松。**

## 8. 停止原因

我停止在 `v6`，不是因为“最多 5 轮到了”，而是因为已经出现清晰的收敛信号：

1. `v3` 之后连续三轮都没有产生净改进。
2. 错误开始在不同 case 间振荡：`Microsoft`、`Google`、`CapitalOne`、`HealthEquity` 来回摇摆。
3. 这说明继续修改 prompt 本身，收益已经低于风险；再改下去是在为单个 case 过拟合。

换句话说，**当前这条 reviewer pipe 的最优停点已经出现，但不在最新版本，而在 `v3`**。

## 9. 对新 reviewer pipe 的最终评估

### 9.1 我认可的部分

- 四阶段结构比旧 pipe 更可审计。
- `P3A` 命名平台/框架一致性检查，比旧 pipe 更容易抓出像 `AWS Bedrock` 这种正文/Skills 不一致问题。
- `P3E` 从“品牌/年份考据”收敛到“真实合规边界”后，方向是对的。
- 外部 `Reviewer_Cal.py` 的规则化聚合是有价值的，至少它让“为什么 fail”可被稳定追踪。

### 9.2 目前的根本限制

目前这套 pipe 仍然有一个核心问题：**很多最难的真实 HR 判断，实际上不是 prompt wording 能稳定解决的，而需要更显式的 deterministic gate。**

最典型的三类：

1. `manager / 6+ years` 这类 seniority 门槛。
2. `Azure App Service / API Management / Event Grid` 这类平台深度门槛。
3. “正文有无真正使用证据”这类 body-proof 门槛。

只靠 prompt 提醒，LLM 会摇摆。`v3` 只是目前最稳的局部最优，不是理论上的终点。

### 9.3 如果继续演进，我建议下一步不要再纯改 prompt

若要超越 `v3`，我建议下一步改的是架构，而不是继续堆 prompt：

1. 把 `JD hard-gap deterministic checker` 从 LLM 审阅里拆出来。
2. 用结构化规则单独检查：
   - `manager/lead` scope
   - `6+ years` 明显年限不足
   - 命名平台子服务缺失
   - Skills 有但正文无 body evidence
3. LLM 继续负责：
   - framing
   - bridge
   - ownership 语言
   - 合规表述边界
   - narrative quality

这样才有机会在不破坏 `v3` 稳定性的前提下，真正修好 `HealthEquity` 这类 case。

## 10. 推荐采用方案

**当前就地可用的推荐方案：**

- 生产/影子评测推荐版本：[`v3_hr_stable/Reviewer_4Stage.md`](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iterations/v3_hr_stable/Reviewer_4Stage.md)
- 对应 scorer：[`v3_hr_stable/Reviewer_Cal.py`](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iterations/v3_hr_stable/Reviewer_Cal.py)
- 全量 run：[`v3-hr-stable_20260417_195326_805428`](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline_prompt_worktree/reviewer-compare/iteration-runs/v3-hr-stable_20260417_195326_805428)

**不推荐采用的版本：**

- `v4_hr_converged`
- `v5_hr_gate`
- `v6_hr_final`

不是因为它们“最新所以不稳”，而是因为它们在 10 case 全量对照上已经证明确实不如 `v3`。
