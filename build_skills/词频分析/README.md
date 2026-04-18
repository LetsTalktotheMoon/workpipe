# 词频分析

这个目录只放“非技术栈词频分析”的规则层，不负责最终抽取、聚合或 HTML 渲染。
后续流水线会先从 JD 中抽出要求相关文本，再调用这里的规则函数做清洗、排除、同义合并和 bucket 归类。

## 输入

- 已经抽取出来的 JD 候选短语，或者从 `must_have_quals`、`preferred_quals`、`core_responsibilities`、`job.md` 里拆出来的片段
- 候选短语应尽量保持短语级别，不要先切成单词

## 输出

规则层输出的是可复用的分类结果，而不是最终统计表：

- `PhraseDecision`
- `canonicalize_phrase()`
- `canonicalize_variants()`
- `classify_phrase()`
- `group_phrases()`

后续聚合器可以把 `PhraseDecision.title` 作为表格第一列，把原始变体列表作为第二列，把频数作为第三列。

## 三类 bucket

- `generalized_tech`：泛化技术概念，例如 `Software Engineering`、`Full-Stack Development`、`Relational Databases`
- `business_domain`：业务 domain，例如 `Healthcare`、`Finance / FinTech`、`Logistics / Supply Chain`
- `soft_skill`：软技能，例如 `Communication`、`Problem Solving`、`Cross-Functional Collaboration`

## 已做的规则

- 去掉无意义单词和噪声短语：`the` / `an` / `and` / `or`、`related field`、`equivalent experience`、`benefits`、`salary`、`equal opportunity employer` 等
- 识别并忽略公司介绍、团队介绍、福利、薪资、学历、法律声明、location/visa 等噪声
- 同义短语合并到统一标题，例如：
  - `Software Development` / `Software Engineer` / `Software Engineering` / `Software Developer` -> `Software Engineering`
  - `Full Stack` / `Full-Stack` / `Fullstack` -> `Full-Stack Development`
  - `Cross-functional collaboration` / `cross functional teamwork` -> `Cross-Functional Collaboration`
  - `Relational databases` / `rdbms` / `database systems` -> `Database Systems`
- 短语边界保护：
  - `C` / `Go` / `R` 只在独立 token 时识别
  - `Full Stack` 不会被拆成单词级误判
- 技术栈排除：
  - 直接引用 `build_skills.taxonomy` 中的 canonical skills 和 aliases 作为黑名单
  - 但会对白名单中的泛化技术概念放行，避免把 `Relational Databases`、`Version Control` 这类泛化词误删

## 规则边界

- 这里只负责“候选短语 -> 标准标题/ bucket”
- 不负责：
  - JD 段落切分
  - 候选短语挖掘
  - 频率统计
  - 输出 HTML

## 已知局限

- 规则是保守型的，宁可漏掉少量模糊短语，也尽量不把具体技术栈混进非技术词频板
- 业务 domain 的同义词覆盖还可以继续补充，尤其是长尾行业词
- 软技能和泛化技术的边界在少数表达上仍有交叉，需要后续根据 3999 份 JD 的真实分布继续迭代
- 当前只处理英文 JD 常见表达，遇到大量中文 JD 时仍需要补充词表
