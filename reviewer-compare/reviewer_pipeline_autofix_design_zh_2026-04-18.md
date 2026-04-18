# Reviewer Pipeline 现状、判定口径与“顺手修”设计

这份文档只讨论 reviewer pipeline 本身，不讨论 writer 的改写质量。

你的新要求里最关键的变化有 4 条：

1. reviewer 不再因为某个“硬挡板”直接淘汰或拒绝，而是**必须列出全部扣分点**。
2. 年限是否低于目标 JD，不在 reviewer 里做拦截和扣分，后续由上游岗位 filter 统一处理。
3. 对 pass 简历里那些机械、细碎、不值得重新启动 writer 的问题，需要新增一个内嵌的“顺手修”角色。
4. “顺手修”修过的问题，在后续 review 轮次里**不应再次扣分**。不是屏蔽问题，而是先修，再审。

下面我先基于当前代码实现复述 reviewer 现在到底怎么跑，再把你的判断倾向抽象成通用规则，最后给出“顺手修”怎么插入 pipeline 的建议。

---

## 一、当前 reviewer 实践到底是什么

### 1. 当前不是“真分阶段串行执行”，而是“单次调用 + 阶段化规则”

从当前实现看：

- prompt 文件标题直接写的是 `Four-Pass Single-Call`
- 运行脚本 `reviewer-compare/run_iteration_codex.py` 会把整份 `Reviewer_4Stage.md` 一次性拼进 prompt
- model 一次性输出完整 JSON
- 外部 `Reviewer_Cal.py` 再按 rule id / sub_area 归口、算分、给出 `pass/fail`

也就是说：

- **设计上**：分了多个阶段
- **实践上**：不是多轮串行分开注入，而是**一次性注入全部阶段**
- 当前的“阶段”更多是**prompt 内部的逻辑分区**，不是运行时的真实中间节点

### 2. 当前 reviewer 一共有几层

如果按 prompt 的结构看，当前主 reviewer 是：

- Pass 1：结构和 ATS 红线
- Pass 2：首屏 HR 6-8 秒扫读
- Pass 3：Hiring Manager 内容审查
  - 3A 技术-叙事一致性
  - 3B JD 覆盖与桥接
  - 3C ownership / 动词强度 / 堆砌型炫技
  - 3D 量化可信度
  - 3E 生态一致性 / 合规 / 时代错位
- Pass 4：本土化翻译合规审查

代码里输出字段因为历史兼容，localization 最后会被 normalize 成 `pass_5_localization`，但语义上它就是第 4 个大阶段。

### 3. 每阶段分别在做什么

#### Pass 1

只看结构，不看岗位内容质量。

主要抓：

- 不可变字段
- Experience / project / summary 结构
- bullet 格式
- 加粗规则
- Skills 密度
- Achievements 固定格式

本质上像：

- ATS 结构校验
- 样式 lint

#### Pass 2

只看前几秒首屏抓手，不深挖正文真伪。

主要抓：

- Summary 第一句是不是“转型叙事压过岗位锚点”
- 围棋句 header 是否信息量过低
- 第一段经历第一条 bullet 是否承担最强信号
- Skills 第一行是否对齐 JD 核心
- Skills 类别命名是否模糊

本质上像：

- 真实 HR 的首屏印象扫描

#### Pass 3A

看“说了的东西有没有在正文里站住”。

主要抓：

- Skills 里写了，但正文没证据
- 正文用了，但 Skills 没列
- Summary 提了，但正文没支撑
- Summary 和正文打架

本质上像：

- 技术栈闭环
- 叙事闭环

#### Pass 3B

看和 JD 的真正匹配度。

主要抓：

- JD must-have 是否在 Skills 里覆盖
- JD must-have 是否在正文有实质性使用
- team_direction 是否有桥接
- 陌生行业是否有迁移桥接

本质上像：

- 岗位适配度主审

#### Pass 3C

看 ownership 叙事是不是虚胖、是不是在“堆技术词”。

主要抓：

- intern / junior 是否用了超 scope 动词
- 语言/框架/云平台在单段经历里堆太多
- 是否像 stack stuffing

本质上像：

- 防吹牛
- 防花哨炫技

#### Pass 3D

看量化是不是高价值量化，而不是只会写百分比。

主要抓：

- tier 1 规模 / scope 信号够不够
- 是否过度依赖 tier 2 百分比改善
- 数字能不能被追问
- junior / intern 是否写了不可信的大 scope

本质上像：

- 量化质量
- scope 可信度

#### Pass 3E

看生态、时代、合规有没有穿帮。

主要抓：

- 时间线错位
- 合规边界
- 特定公司/业务事实冲突

本质上像：

- 高风险硬错误检查

#### Pass 4 / localization

看中国公司技术栈翻译成美国 ATS 语境时有没有错位。

主要抓：

- 应翻未翻
- 不该翻硬翻
- 翻译不准确
- 缺桥接语言

本质上像：

- 中美技术栈翻译审校

### 4. 当前实践中，除了 prompt 本体还注入了什么

当前单次调用除了 `Reviewer_4Stage.md` 本体，还会注入：

- 公司名
- 岗位 title
- role_type
- seniority
- `tech_required`
- `tech_preferred`
- `team_direction`
- 原始 JD 全文
- 不可变字段块 `immutable_block`
- 简历全文

此外，prompt 本体里还自带：

- 公开事实锚点
  - ChatGPT / GPT-4 / Bedrock / LangChain 发布时间
  - TikTok USDS / Project Texas 合规边界
  - DiDi LATAM 国家事实
  - Temu/PDD 口径说明
- tier 1 / tier 2 量化分级
- 中美技术栈翻译对照表
- 归口纪律
- 严重度定义
- 输出 JSON schema
- 每阶段 findings 数量上限

也就是说，当前 reviewer 已经不是“只拿 JD 和简历裸跑”，而是：

- **大 prompt**
- **内置规则手册**
- **外部打分器**

### 5. 当前这套实现是否解决了最初设计 concern

最初设计 concern 是：

- 分阶段是为了让每一层只盯一个任务
- 减少上下文过长导致的信息损耗和幻觉

我的判断是：

- **解决了一部分**
- **但没有彻底解决**

它解决的部分：

- 通过明确的阶段分工，减少了 reviewer 胡乱发散
- 通过固定 JSON schema + 外部聚合，把“怎么打分”从 LLM 手里拿出来
- 通过 rule id / sub_area，把 findings 的归口变得更可控

它没有解决的部分：

- 因为仍然是**一次性把全部阶段塞进一个 prompt**，所以模型仍然要在一个超长上下文里同时处理结构、首屏、JD、生态、翻译、合规
- 阶段之间不是运行时隔离，所以仍然会互相污染
  - 例如本应是“小格式问题”的 finding，在模型脑中可能被放大成总评下滑
  - 或者本应只在 3B 判断的事，被 2A / 3D 的语气放大
- 当前没有中间可插入的“顺手修”节点，所以很多细碎问题只能先扣分，再一路带着进入后续总评

一句话总结：

- 当前实现已经解决了“完全无结构的 reviewer”问题
- 但还没有解决“阶段虽多，执行仍是一锅炖”的问题

---

## 二、你这轮新标注，抽象出来的判断倾向是什么

你给出的几条 case 标注，其实已经形成了一套很清楚的全局规则。

### 1. 你不希望 reviewer 充当“硬挡板裁判”

你的意思不是“这些问题不重要”，而是：

- 任何问题都要继续列出
- 所有问题都要继续扣分
- 但**不能因为某一个问题是硬门槛，就停止继续看其他问题**

这意味着 reviewer 的角色要从：

- “是否淘汰”

变成：

- “匹配度全量诊断器”

### 2. 你把“JD 年限不够”从 reviewer 里拿出去了

你的口径已经很明确：

- 只要简历本身的时间点、时间线、框架一致
- “是否低于目标 JD 的经验年限要求”
- **不在 reviewer 里拦截，也不在 reviewer 里扣分**
- 后续由上游岗位 filter 统一处理

这会直接影响：

- P3B-010
- 与年限相关的部分 P3B-011 / P3B-012
- scorer 里的 structural fail 逻辑

### 3. 你已经把问题初步分成了 4 类

#### A. 必须顺手修

特点：

- 机械
- 局部
- 不改变经历事实
- 不需要新增实质证据
- 不需要重构项目

典型包括：

- `transitioning from data analysis` 放在首句
- 限定词误加粗
- Skills 里显式补一个已经在正文出现的 must-have 技术
- Skills 类别名太模糊
- 某一句只差一个更明确的 scope 锚点
- `Distributed Systems` 其实有相邻证据，但 Skills 没明写

#### B. Writer 修

特点：

- 需要新增真实证据
- 或需要重构主叙事
- 或需要补足真正缺失的核心能力证明
- 不能靠轻量重写假装解决

典型包括：

- 没有明确带人证据
- 没有 R 的正文证据
- specialized 岗位要求的核心 artifact 完全没有
- 需要更硬的 owner 证据，但当前简历里根本没有
- stack stuffing 已经不是一句话能修，而是整段要重织

#### C. 可 pass，也可顺手修

特点：

- 不是决定性问题
- 不修也不该挡住通过
- 修了更好

典型包括：

- “Node.js 不是最强主轴”
- 业务迁移逻辑不够直，但仍可读通
- 行业桥接还可更明确

#### D. 可 pass，不处理

你这轮给出的明确代表是：

- JD 年限不足

这类问题将转移到上游 filter，不进 reviewer 主扣分。

### 4. 你实际上在推动 reviewer 从“发现问题”变成“发现问题 + 自动完成小修”

这点非常关键。

因为你并不是要：

- reviewer 对小问题闭眼

而是要：

- reviewer 先发现
- 再修掉
- 修完以后，这类问题在后续 review 轮次中不再存在，也不再扣分

所以你要的不是“忽略轻微 finding”，而是：

- **把一类 finding 转化成流程中的自动处理节点**

---

## 三、我如何复述、归纳你的常见扣分类判断倾向

下面这份归纳，是把你已经明确写出来的判断倾向抽象成 reviewer 可执行规则。

### 1. 年限类

你的口径：

- 时间线自洽要审
- 虚假时间点要审
- 但“低于 JD 要求的年限”不在 reviewer 扣分

落地后应变成：

- 可保留为 `upstream_filter_note`
- 不进入 reviewer 总分
- 不触发 fail
- 不触发 structural fail

### 2. 首句 / 首屏 framing 类

你的口径：

- 基本属于“必须顺手修”

落地后应变成：

- `auto_fixable`
- 高优先级
- 先修再继续后续 review

### 3. 加粗 / 格式 / Skills 类别命名 / 行密度 类

你的口径：

- 基本都应归到“顺手修”

落地后应变成：

- Pass 0 或 Step A 自动修复
- 后续完整版 reviewer 不再重复扣这类问题

### 4. Skills 与正文不闭环

你的口径更细：

- 如果 JD 明确要求，而且正文已经有证据，只是 Skills 漏写
  - 顺手修直接补上
- 如果 JD 根本没要求
  - 不应因为“正文有、Skills 没列”就重罚
- 如果 Skills 写了，但正文完全没证据
  - 这不是顺手修能凭空补出来的，通常要 writer 或至少人工判断

这意味着 3A 其实要拆成两类：

- 3A-可顺手修
- 3A-必须 writer

### 5. scope 太弱 / tier 1 不够

你的口径是：

- 如果只是当前句子缺一个可明确补上的 scope signal
  - 顺手修
- 如果补完轻量 scope 后，仍然缺“更高一级的设计/架构可信度”
  - 升级 writer

这说明 3D 不能粗暴地一律当 writer 问题。

### 6. specialized 岗位的核心 artifact 缺失

你的口径是：

- 若 JD 显式要求，且简历没有对应证据
  - writer 修
- 若只是叙事侧重点没对准，而现有经历里已有相邻技术
  - 先顺手修改叙事侧重点
  - 仍不过，再升级 writer

这套逻辑尤其适用于：

- storage
- Azure 平台
- networking
- SDET
- ML infra
- GenAI tooling

### 7. 业务迁移 / 行业桥接

你的口径偏宽松：

- 这类问题很多时候可以 pass
- 不一定值得启动 writer
- 若只是缺一句桥接话，也可以顺手修

也就是说：

- 业务迁移桥接默认不应直接重罚
- 更适合作为中低权重项

### 8. owner 证据不足

你的口径是分层的：

- 完全没有提及：writer
- 有相邻覆盖，只是侧重点不对：可顺手修或 pass

这条非常重要，因为它决定 reviewer 不应把“owner 证据不足”都打成同一种 high。

---

## 四、你还没明确表态，但属于高频或关键的扣分点

下面这些是当前 reviewer 里很高频，但你还没有完全盖住的点。我先按我的理解给出建议归类，同时标出哪些地方我需要你拍板。

### 1. Summary 提了技术 / 成就，但正文没支撑

当前规则：

- P3A-003 / P3A-004 偏重

建议归类：

- 如果只是 summary 用词比正文强一点，但正文有相邻证据
  - 先顺手修，把 summary 降回真实强度
- 如果 summary 明显写了正文没有的硬技能 / owner 结论
  - writer 或直接删回真实表述

我需要你拍板的点：

- “顺手修”是否允许**弱化或删除** summary 里的过强说法？
- 还是“顺手修”只能补，不允许删？

### 2. Skills 有，正文无

当前规则：

- P3A-001 = high

建议归类：

- 如果正文其实有相邻证据，只是没显式点名
  - 顺手修可把正文显式补出来
- 如果正文完全没有
  - 不能由顺手修臆造
  - writer / 或保留扣分

我需要你拍板的点：

- 如果这项技能不是 JD 必须项，只是候选人为显得丰富列进去，但正文没有任何证据：
  - 顺手修是否允许直接从 Skills 删除？
  - 还是保留并扣分，交给 writer？

### 3. stack stuffing / breadth 过宽

当前规则：

- 3C-010 / 3C-011 经常触发

建议归类：

- 如果只是同类技术列太多，删减 / 收束即可
  - 顺手修
- 如果已经影响整段叙事可信度，需要把整个经历重织
  - writer

我需要你拍板的点：

- 顺手修是否允许在**不改变事实**前提下，删除一些次要技术词以收束主线？

### 4. 合规边界限定语缺失

当前规则：

- 现在 reviewer 很容易因为边界语没写全而出 finding

建议归类：

- 如果实际叙事已经明显是 internal / sandbox / no user data，只是没写明
  - 顺手修补限定语
- 如果真实边界不清楚
  - 不能自动补
  - writer 或人工确认

这条我建议明确归到：

- 默认顺手修优先
- 但禁止编造边界事实

### 5. 中国技术栈翻译 / localization

建议归类：

- 一级、明确二级对等
  - 顺手修
- 可疑对应
  - 先不要自动修
  - writer 或人工

### 6. 业务桥接不够直

建议归类：

- 如果只差一句“这个经验如何迁移到目标场景”的桥接
  - 顺手修
- 如果根本没有任何可迁移基础
  - 只能保留扣分，不强补

### 7. AI coding assistant / Excel / R / Tableau / LangChain 这类 JD 点名技能

这类最容易出歧义。

我的建议是拆成 3 类：

- 简历正文已有真实证据，只是没放到 Skills 或没显式点名
  - 顺手修
- 简历有相邻证据，但不是同一技能
  - 保留扣分，可 pass / 也可 writer
- 简历完全无证据
  - writer 或保留扣分

---

## 五、关于你点名的两个 case，我的明确判断

### A. same/Google 的 `AWS Bedrock`

你问的是：

- `AWS Bedrock` 是目标 JD 什么层级的技术栈要求？
- 如果目标 JD 没要求，它出现在正文、但没进 Skills，是否还能算“技术栈不闭环”？

我的结论：

- 这条 Google JD 的核心要求是：
  - Python
  - Node.js
  - Java
  - C++
  - JavaScript / TypeScript
- 它**没有任何层级明确要求 `AWS Bedrock`**

所以按你的新口径，这件事应这样处理：

- 不能作为“JD must-have 缺失”扣分
- 不能因为它没进 Skills，就把这份简历打成不通过
- 如果你希望正文与 Skills 更整洁统一，可以把它放进“顺手修”
- 但它不应再作为重扣分问题影响 Google case 的总体结论

也就是说，这条在你新的体系里更像：

- `optional_auto_fix`

而不是：

- `core_deduction`

### B. same/Amazon 的 `LLM customization / training / architecture owner 证据`

我的判断是：

- 它**不是完全没有提及**
- 但也**远没有强到可以自称 training / architecture owner**

当前简历里已经有的，是这些相邻证据：

- retrieval evaluation
- Bedrock inference integration
- PyTorch reranking experiment
- RAG workflow adaptation
- sandbox / evaluation pipeline

缺的则是这些更强的 owner 证据：

- novel training techniques
- model training ownership
- architecture-level design ownership
- leading model customization system design

所以这条我会这样归类：

- 如果只是要把现有的 `LLM customization / evaluation / inference integration` 放到更对的位置、减少“analytics transition”抢镜
  - 顺手修可以做
- 如果要补成“training / architecture owner”
  - 顺手修不能编
  - 只能 writer，前提还得是真有这类经历

一句话：

- 这是**部分覆盖但强度不够**
- 不是“完全没有”
- 也不是“轻轻改一句就能变成 owner”

---

## 六、我对“顺手修”方案的总体评价

### 结论

我建议设置“顺手修”环节。

而且我认为：

- 这不是可选优化
- 这是你当前 reviewer 体系继续往真实生产靠近的关键一步

因为现在最大的流程问题不是“reviewer 看不出问题”。
最大的问题是：

- reviewer 看出了太多不值得启动 writer 的小问题
- 但当前流程里没有人负责把这些小问题闭环
- 结果就是：
  - pass 简历也带着呆板小问题离开
  - 小问题继续拖分
  - 还容易误导我们以为“这份简历本身不行”

### 主要好处

#### 1. pass 简历最终质量会明显更高

你点名的这些问题：

- 首句 framing
- 限定词加粗
- Skills 不闭环
- Skills category 模糊
- 某句缺一个明确 scope signal

本来都不值得重启 writer。

如果没有顺手修：

- 它们会一直留在最终简历里

如果有顺手修：

- 它们会在 pass 前被自动抹平

#### 2. reviewer 分数会更干净

现在很多分数被这些机械小问题拉低。

有顺手修之后：

- 后续完整 review 看到的是“已经洗过机械问题”的版本
- 分数会更集中反映真正的大问题：
  - 叙事主线
  - 岗位核心能力
  - specialized artifact
  - owner 证据

#### 3. writer 的带宽会被释放

没有顺手修时，writer 很容易被迫处理：

- 去掉某个 bold
- 改个 Skills 名字
- 把一句 `transitioning from` 往后挪

这些其实是浪费 writer 轮次。

#### 4. pipeline 会更接近真实团队协作

真实招聘文案 / 简历 polish 里，本来就有一层：

- copy cleanup
- recruiter polish
- surface alignment

你现在要的“顺手修”，本质上就是把这一层补上。

### 主要风险

#### 1. 顺手修容易越权

如果权限不清，顺手修会偷偷做这些事：

- 编造新证据
- 擅自放大 owner 语气
- 用 JD 词反向替换成候选人没做过的技能

这会直接污染真实性。

所以顺手修必须是：

- **低权限角色**
- 只能做有限动作

#### 2. 顺手修如果放得太早，可能把真正的大问题“抹平得像小问题”

例如：

- `Distributed Systems` 只是没写进 Skills
  - 顺手修可补
- 但如果实际上没有分布式系统证据
  - 就不能靠顺手修把词塞进 Skills 假装解决

所以顺手修必须区分：

- “显式化已有证据”
- “创造不存在的证据”

#### 3. 如果顺手修后不重审，就会造成假闭环

因此顺手修后必须：

- 再跑完整版 reviewer
- 而不是假设它一定修对了

---

## 七、我建议怎么设置“顺手修”环节

我建议采用你提到的“两步走”，而不是在现有单次 4-stage 里硬塞。

### 推荐方案：两步式

#### Step A：顺手修扫描

输入：

- 阉割版 reviewer prompt
- 只扫描“顺手修候选问题”

这一步只允许发现这些问题：

- 首句 / 首屏轻量 framing
- 加粗 / 格式 / Skills 类别名
- 正文已有证据但 Skills 漏列
- Skills 已列但正文已有相邻句子可显式化
- 可在当前句补上的 scope signal
- 合规边界限定语缺失，但已有安全语境
- 行业迁移桥接只差一句过渡
- localization 的确定性低风险翻译

输出不应是最终评分，而应是：

- `auto_fix_patch_plan`
- 每条包含：
  - 问题
  - fix 类型
  - 允许修改的 section
  - 禁止越权说明

#### Step B：顺手修执行

执行者：

- 一个专门的低权限 fixer

允许动作：

- 改写 summary 首句 / 第二句顺序
- 去掉错误加粗
- 重命名 Skills 类别
- 把正文已有技术补到 Skills
- 把已有上下文里的 scope 信号前置
- 增加 1 句 bridge sentence
- 补 `internal / sandbox / no user data` 这类限定语，但前提是上下文已支持

禁止动作：

- 新增未出现过的硬技能
- 新增没证据的 owner 表述
- 新增人管理经历
- 新增 specialized artifact
- 改动不可变字段
- 改写项目主线

#### Step C：完整版 reviewer

这一步才喂完整版 `Reviewer_4Stage.md`。

作用：

- 检查顺手修有没有修对
- 继续找 writer 级问题
- 最终给出总分

### 为什么我不建议直接在当前 4-stage 单次 prompt 里内嵌顺手修

因为当前执行是单次调用。

如果你在一个 prompt 里要求：

- 先发现
- 再修
- 再继续后续 review

那模型实际上还是在一次上下文里脑内模拟这些步骤。

问题是：

- 你拿不到中间产物
- 也没法验证它真的修了什么
- 更没法保证“修过的问题在后续轮次里不再扣分”

所以如果你真要稳，顺手修必须成为**显式的流程节点**。

---

## 八、我建议如何修改 prompt 与 scorer

### 1. prompt 侧要新增“问题处理归类”

我建议每条 finding 不再只有：

- severity
- field
- issue
- fix

还要新增：

- `handler`
  - `auto_fix`
  - `writer`
  - `upstream_filter`
  - `pass_note`
- `auto_fix_scope`
  - `summary_rephrase`
  - `skills_explicitization`
  - `format_cleanup`
  - `scope_frontload`
  - `bridge_sentence`
  - `safe_boundary_qualifier`
- `evidence_level`
  - `already_explicit`
  - `latent_in_resume`
  - `missing_real_evidence`

这样后面的 fixer 才知道：

- 哪些能改
- 哪些不能碰

### 2. prompt 侧要把“年限不足”从 reviewer 主扣分中剥离

我建议：

- reviewer 仍可记录
- 但输出到单独字段，比如：
  - `upstream_filter_notes`

不要再进入：

- `pass_3_substance.findings`

否则 scorer 还会把它扣进总分。

### 3. scorer 侧必须去掉 structural fail

当前 `v10` scorer 里有：

- `STRUCTURAL_FAIL_RULE_IDS`
- `structural_fail`
- `overall_verdict = fail` if structural_fail

这和你的新目标直接冲突。

你新的体系里应该变成：

- 任何问题都只是扣分
- 不再有“某条 rule 命中就直接 fail”

### 4. scorer 侧要支持“顺手修后不重复扣分”

建议方式：

- Step A 产出 `auto_fix_actions.json`
- Step B 产出修后的简历
- Step C reviewer 只对修后简历出 findings

也就是说，不要靠 scorer 去“豁免旧问题”，而是：

- 让它们在修后版本里自然消失

这样最稳。

### 5. prompt 侧要把“轻微问题的发现”与“最终是否需要 writer”分开

建议新增两个字段：

- `small_fix_only`
- `writer_required`

这样你后面能更方便做路由：

- 只有 `small_fix_only`
  - 走顺手修后直接通过
- 出现 `writer_required`
  - 走 writer

---

## 九、token 与时间消耗会增大还是减小

### 我的判断

- **单次完整 review 的 token 会下降一点**
- **整条 pipeline 的总调用次数会增加**
- **总耗时大概率小幅增加或基本持平**
- **writer + reviewer 的返工次数会下降**

### 更细一点的估计

假设现在是：

- 1 次完整版 reviewer

改成：

- 1 次顺手修扫描
- 1 次顺手修执行
- 1 次完整版 reviewer

表面看是多了 2 次调用。

但这两次的上下文都可以比完整版短很多：

- 顺手修扫描 prompt 只保留 auto-fix 范围规则
- 顺手修执行 prompt 只保留 patch 规则和简历

我对成本的粗估是：

#### token

- 单次完整版 reviewer token：不变
- 额外增加：
  - 顺手修扫描：约完整版的 `20% - 30%`
  - 顺手修执行：约完整版的 `10% - 20%`

整条 pass case 的总 token：

- 约增加 `30% - 50%`

#### 时间

如果不考虑 writer 返工：

- pass case 的 reviewer 纯耗时
  - 约增加 `25% - 45%`

但是如果考虑减少 writer+reviewer 往返：

- 全链路平均耗时未必增加
- 甚至有机会下降

因为你现在最浪费时间的部分之一就是：

- 本可顺手修的小问题
- 被迫触发 writer 再来一轮

如果顺手修把这些拦下来：

- 整体返工成本会下降很多

一句话总结：

- **局部 reviewer 成本会上升**
- **全链路返工成本大概率会下降**

---

## 十、我建议的最终落地方案

### 我建议你采纳“顺手修”环节

而且建议是：

- **显式节点**
- **低权限**
- **先修再审**

### 我建议的具体流程

1. 上游岗位 filter
   - 处理年限、地点、签证、工作制等硬筛选

2. Reviewer Step A：顺手修扫描
   - 只找 `auto_fix` 类问题

3. Auto-fix executor：顺手修执行
   - 只允许低扰动改动

4. Reviewer Step B：完整版 reviewer
   - 对修后简历做真正评分
   - 继续识别 writer 级问题

5. 路由
   - 只有 `auto_fix` 问题：直接出最终版
   - 有 `writer_required`：退回 writer

### 我建议优先改的 4 个点

1. 去掉 reviewer scorer 里的年限 fail / structural fail 逻辑
2. 给 findings 增加 `handler` / `evidence_level` / `auto_fix_scope`
3. 新增一个顺手修专用 prompt
4. 把 pass case 也强制走“修后复审”

---

## 十一、还需要你拍板的几个歧义点

为了后续真正执行，我还需要你明确这几条。

### 1. 顺手修是否允许删除 / 弱化不实或过强表述

例如：

- summary 里说得太满
- Skills 列了正文完全无证据的技术

顺手修是否可以：

- 直接删掉
- 或降级措辞

### 2. 顺手修是否允许重排 bullet 顺序

例如：

- 把第一条弱 bullet 和第二条强 bullet 对调

这很常见，而且对首屏影响很大。

### 3. 顺手修是否允许删除次要技术词，来缓解 stack stuffing

如果不允许删，很多 stack stuffing 问题只能交给 writer。

### 4. 对“行业桥接不够直”这类问题，你希望默认：

- pass 不处理
- pass 但顺手修
- 还是看严重程度分流

### 5. 对“Skills 有、正文无”的非 must-have 技能

你希望默认：

- 顺手修从 Skills 删除
- 保留扣分，交给 writer
- 还是保留但不扣分

---

## 十二、我的总体结论

你的方案方向是对的，而且比当前 reviewer 更接近真实生产。

当前 reviewer 最大的问题不是“不会发现问题”，而是：

- 把很多本该自动闭环的小问题和真正需要 writer 的大问题混在一起
- 又因为没有“顺手修”节点，只能让它们一起拖分、一起返工

所以我建议：

- 保留现有四阶段审查思路
- 但把执行从“单次四阶段一锅炖”
- 改成“顺手修预处理 + 完整复审”

同时：

- reviewer 不再做年限淘汰
- 不再做 structural fail 一票否决
- 所有问题都继续列出、继续加总扣分
- 只是把一部分问题先修掉，再进入终审

这是最符合你这轮全局预期的方向。  
