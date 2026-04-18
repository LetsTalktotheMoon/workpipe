# reviewer pipe 新样本泛化迭代报告（中文）

## 结论先行

本轮在原 10 case 之外新增了 10 个主基准 case，并额外抽取了 10 个外部确认 case。按 raw JD 复核并修正标签后，当前最佳版本是：

- Prompt: `iterations/v10_equiv_evidence/Reviewer_4Stage.md`
- Scorer: `iterations/v10_equiv_evidence/Reviewer_Cal.py`

最终成绩：

- revised 主基准 20 case：`20/20`
- revised 外部确认集 10 case：`9/10`

我停止在 `v10`，不继续做 `v11`。原因不是到 5 轮上限，而是当前只剩 1 个边界型 miss：`conf/Phantom-SDET`。这条 miss 的核心是 reviewer 仍把 `incident post-mortem / prevention` 当成 SDET 首筛硬门槛；如果继续放松，很可能会削弱对生产敏感测试岗的真实 hard bar。换句话说，`v10` 已经到达“主基准全对、外部确认集只剩 1 个高争议边界 case”的稳定点，再继续追这个点，过拟合风险高于收益。

## 方法与标签修订

这轮不是只看已有 20 个 case 的数字，而是做了两层验证：

- 主基准：原 10 + 新增 10，共 20 case。
- 外部确认集：额外新抽 10 case，只用于验证是否对当前 20 个 case 过拟合。

在跑 `v7` 到 `v10` 过程中，我对标签做了两次必要修订，原因都一样：最初标签是我在快速浏览下给出的，后面按 raw JD 逐条复核后，发现有几条“我自己先前定得太松”。为避免把标签误差错算成 reviewer 回退，我保留了旧标签文件，同时新增 revised 标签文件。

修订点：

- 主基准 revised：`same/AWS` 从 `pass` 改为 `fail`。
  - 原因：raw JD 明写 `3+ years of non-internship professional software development experience`，而简历可见非实习全职时间约 30 个月。
- 外部确认集 revised：`conf/Clarivate-NLP`、`conf/Photon-AIEngineer` 从 `pass` 改为 `fail`。
  - Clarivate 原因：raw JD 明写 `5+ years` NLP/Python 经验，并且要求 LangChain/LangGraph，带 senior/technical leadership 责任。
  - Photon 原因：raw JD 要求 production GenAI、LangChain/LlamaIndex、vector search、advanced retrieval、local LLM 能力，当前简历只有泛 RAG/LLM/Bedrock 证据。

相关文件：

- 主基准 revised 标签：`hr_labels_20_raw_jd_revised.json`
- 确认集 revised 标签：`hr_labels_confirmation_10_revised.json`

## 历史版本与新迭代对照

主基准（20 case, revised labels）版本总表见：

- `iteration_comparison_v10_revised.md`
- `main20_scores_v10_revised.md`
- `deduction_comparison_v10_revised.md`

外部确认集（10 case, revised labels）分数表见：

- `confirmation10_scores_v10_revised.md`

关键摘要：

- `old_pipe` 在 revised 主基准是 `12/20`。
- `v3_hr_stable` 在 revised 主基准是 `13/20`，在 revised 外部确认集是 `5/10`。
- `v7_gen2_jd_richer` 在 revised 主基准是 `17/20`。
- `v8_tooling_bridge` 在 revised 主基准是 `16/20`。
- `v9_gate_restore` 在 revised 主基准是 `19/20`，在 revised 外部确认集是 `8/10`。
- `v10_equiv_evidence` 在 revised 主基准是 `20/20`，在 revised 外部确认集是 `9/10`。

这说明：

- `v3/v5/v6` 的问题不是偶然，而是结构性的。它们在新样本和 revised 标准下都会把一类 specialized fail 放过，也会把一类强相关 pass 误杀。
- `v7` 开始真正进入“raw JD + 真实 gate”轨道。
- `v8` 修掉了工具族误杀，但把年限门槛和多云职责误读搞坏了。
- `v9` 恢复了年限门槛和多云职责边界。
- `v10` 进一步修了“等价证据识别不足”，把 `VeteransUnited` 从误杀里拉回，同时保住 revised 主基准全对。

## 4 轮迭代记录

### 第 1 轮：`v7_gen2_jd_richer`

问题来源：

- `v3/v5/v6` 只看压缩 JD 字段，不看 raw `job.md`。
- 结果是对年限、specialized platform、raw responsibilities 的判断偏松。
- 典型漏判：`Discord DB Infra`、`Childrens Azure`、`Cisco Networking`、`Amazon/Dataminr` 这类 raw JD 明示门槛。

修改内容：

- 把 raw JD 注入 prompt。
- 强化 `P3B-010/011/012`，让 year gate、platform depth、specialized substrate role 真正生效。

效果：

- revised 主基准 `17/20`。
- 把 `Discord/Childrens/Cisco` 这类 specialized-role 错配抓对了。
- 但把 `Fireblocks`、`Geico` 这类“主能力闭环成立，只缺支持性交付工具 token”的 case 误杀。

### 第 2 轮：`v8_tooling_bridge`

问题来源：

- `v7` 把 `Helm/ArgoCD/Ansible/PowerShell/IaC` 这类支持性交付工具缺口，当成了岗位定义级硬门槛。

修改内容：

- 新增 `P3B-013` 思路，把 supporting delivery tooling 与 role-defining stack 拆开。
- 对主能力闭环已成立、仅缺 supporting tooling token 的场景降级处理。

效果：

- `Fireblocks`、`Geico` 被修回。
- 但副作用很大：`Amazon`、`Dataminr` 年限 fail 被放掉，`AppliedIntuition` 又把多云职责误读成三云硬门槛。
- revised 主基准反而降到 `16/20`。

### 第 3 轮：`v9_gate_restore`

问题来源：

- `v8` 过度放松，把真正的 year gate 又抹平了。
- 同时对 “deploys across AWS/GCP/Azure” 产生了错误外推。

修改内容：

- 强化 `P3B-010`：显式年限不足必须 `high`，non-internship 不能拿 internship 补。
- 加明确约束：多云职责默认描述团队运行环境，不等于候选人必须三云都做过。

效果：

- revised 主基准提升到 `19/20`。
- revised 确认集是 `8/10`。
- 修回了 `Amazon/Dataminr/AppliedIntuition/Fireblocks/Geico`。
- 但外部确认集仍误杀 `Phantom-SDET` 和 `VeteransUnited-AssociateSE`。

### 第 4 轮：`v10_equiv_evidence`

问题来源：

- `v9` 仍然过度依赖 exact token，对等价证据识别不足。
- 典型问题：
  - `Phantom-SDET` 已有 reusable validation pack、fixtures/mocks、pytest/Playwright、CI、flake control，但 reviewer 仍读成“不算 framework ownership”。
  - `VeteransUnited-AssociateSE` 已有 `.NET/C#/ASP.NET/service layer/gRPC/Angular/CI-CD`，但 reviewer 仍把 `AI coding assistant such as ...` 和 `Web APIs` 当 exact token gate。

修改内容：

- 明确等价证据规则：
  - `ASP.NET/.NET service layer + REST/gRPC` 可以满足 `Web APIs / microservice architecture` baseline。
  - `reusable validation pack / harness / fixtures+mocks / pytest+Playwright / CI / flake tracking` 可以满足 test framework ownership baseline。
  - `AI coding assistant such as Windsurf / ChatGPT / Copilot / Cursor` 按 example-family developer tooling 处理；associate/junior 岗未写具体产品名不得 structural fail。
  - 同时明确：这些 developer assistant tools 不能和 `LangChain/LlamaIndex/LangGraph/vector search` 这类岗位定义型 AI framework 混为一谈。

效果：

- revised 主基准达到 `20/20`。
- revised 确认集提升到 `9/10`。
- `VeteransUnited` 修回，`Photon/Clarivate/84.51/WHOOP` 这类 specialized fail 没被误放。
- 仅剩 `Phantom-SDET` 一条仍然 fail，且失败理由已经收缩到一个很窄的点：`incident post-mortem / prevention` 被当成首筛硬门槛。

## 为什么停在 `v10`

我没有继续做 `v11`，原因是当前剩余 miss 已经是高争议边界：

- `Phantom` raw JD 确实把 `incident post-mortem with concrete prevention steps` 放在 minimum qualifications 里。
- 我个人在 revised label 里仍把它判成 `pass`，因为我认为这对首筛来说偏“加分型 production maturity”，不该压过已有的 reusable test framework/CI/flakiness/API harness 组合证据。
- 但如果继续为了修这 1 条而把 post-mortem / prevention 再整体降级，很可能会损伤 reviewer 对生产敏感测试岗、SRE/QA automation 岗的真实 hard bar。

所以这里的决策是：

- 不为 1 个高争议边界 case 再继续松 prompt。
- 接受 `v10` 作为当前最优稳定点。
- 在后续真实使用中，对 `SDET / QA automation / platform validation` 这类岗位保留人工复核观察项。

这符合你要的“不要为了商业 case 过拟合成玩具 reviewer”。

## 我对当前新 reviewer pipe 的最终评价

推荐版本：`v10_equiv_evidence`。

我对它的评价是：

- 它已经比 `v3/v5/v6` 更接近真实 HR 首筛，不再只是商业 case lint 工具。
- 它能比较稳定地识别真正的结构性问题：
  - non-internship 年限不足
  - manager / people-management 缺口
  - specialized platform / substrate role mismatch
  - AI/NLP/GenAI 岗位里的真实 framework / retrieval architecture gap
- 它也开始具备“不过度 exact token 化”的能力：
  - 不再把 supporting tooling 当 role-defining must-have
  - 能识别 associate/junior 岗位里的等价 developer tooling 证据
  - 能承认 `.NET/C#/ASP.NET/service layer` 对 `Web APIs` 的等价覆盖

但它仍有一个明确残余风险：

- 对 production-sensitive testing / validation roles，仍可能把 `incident post-mortem / prevention` 读得偏硬。

如果你现在就要落地，我建议：

- 生产默认 reviewer：用 `v10`。
- 在 `SDET / QA automation / validation / platform test` 这一小类岗位上，加一个人工复核提醒，而不是继续在 prompt 上无限放松。

## 产物索引

推荐采用：

- `iterations/v10_equiv_evidence/Reviewer_4Stage.md`
- `iterations/v10_equiv_evidence/Reviewer_Cal.py`

核心报告与表格：

- `reviewer_pipe_generalization_iteration_zh_2026-04-17.md`
- `iteration_comparison_v10_revised.md`
- `main20_scores_v10_revised.md`
- `confirmation10_scores_v10_revised.md`
- `deduction_comparison_v10_revised.md`

中间评估与 revised 标签：

- `hr_labels_20_raw_jd_revised.json`
- `hr_labels_confirmation_10_revised.json`
- `v9_main_revised.md`
- `v10_main_revised.md`
- `v9_conf_revised.md`
- `v10_conf_full.md`
