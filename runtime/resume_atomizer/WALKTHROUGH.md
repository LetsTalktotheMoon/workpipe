# auto-cv 项目百科全书

> 最后更新：2026-03-15
> 本文档详尽记录了项目的每个文件、每个函数、每个配置项的作用和语法，供任何角色快速上手。

---

## 目录

- [一、项目总览](#一项目总览)
- [二、项目结构](#二项目结构)
- [三、环境配置](#三环境配置)
- [四、核心模块详解](#四核心模块详解)
  - [4.1 build_resumes.py — 批量简历编译器](#41-build_resumespy--批量简历编译器)
  - [4.2 md_to_tex.py — Markdown 转 LaTeX 转换器](#42-md_to_texpy--markdown-转-latex-转换器)
  - [4.3 extract_keywords.py — ATS 关键词提取](#43-extract_keywordspy--ats-关键词提取)
  - [4.4 match_resume.py — JD 匹配 & LLM 微调（CLI）](#44-match_resumepy--jd-匹配--llm-微调cli)
  - [4.5 update_contacts.py — 批量联系方式替换](#45-update_contactspy--批量联系方式替换)
  - [4.6 build_frozen_catalog.py — 冻结关键词库](#46-build_frozen_catalogpy--冻结关键词库)
  - [4.7 notion_match.py — Notion 批量 JD 匹配](#47-notion_matchpy--notion-批量-jd-匹配)
  - [4.8 transplant_resume.py — 简历移植系统](#48-transplant_resumepy--简历移植系统)
- [五、词汇表与配置](#五词汇表与配置)
- [六、数据目录结构](#六数据目录结构)
- [七、文件同步规则](#七文件同步规则)
- [八、完整调用关系图](#八完整调用关系图)
- [九、工作流程示例](#九工作流程示例)
- [十、常用运行命令](#十常用运行命令)
- [十一、迭代指南](#十一迭代指南)

---

## 一、项目总览

**auto-cv** 是一个自动化简历管理与岗位适配系统，核心功能：

1. **简历编译**：将 Markdown 格式的简历转换为 LaTeX → PDF，支持 4 级渐进压缩（自动适配 2 页以内）
2. **关键词提取**：使用 LLM 或确定性词表从简历中提取 ATS 关键词
3. **JD 匹配**：将岗位 JD 与简历库进行多维度匹配，找出最佳候选简历
4. **简历微调**：通过 LLM 对简历进行"微微调"（只调整措辞，不伪造经历）
5. **Notion 集成**：批量从 Notion 数据库获取 JD，自动匹配并回写结果
6. **简历移植**：基于人物画像兼容性矩阵和场景感知的智能关键词注入

**技术栈**：Python 3 + OpenAI SDK（兼容千问/kimi） + Notion API + XeLaTeX

---

## 二、项目结构

```
auto-cv/
├── .env                                    # 环境变量（API 密钥、Notion 令牌）
├── profiles.json                           # 联系方式配置（多个身份）
├── design_plan.md                          # 架构设计笔记
├── README.md                               # 用户文档
│
├── resumes/                                # 📄 22 份 Markdown 源简历（编号 01-22）
│   ├── 01_AI_Application_GenAI_Integration_Engineer_Resume.md
│   ├── 02_Cloud_Data_Pipeline_Engineer_Resume.md
│   ├── ...
│   └── 22_Mobile_Engineer_Resume.md
│
├── base/                                   # 基础材料文档
│
├── output/
│   ├── tex/                               # 生成的 LaTeX 文件（与 resumes/ 1:1 对应）
│   ├── pdf/                               # 生成的 PDF 文件（与 resumes/ 1:1 对应）
│   └── tuned/                             # 微调后的简历
│       ├── md/                            # 微调后的 Markdown
│       ├── tex/                           # 微调后的 LaTeX
│       ├── pdf/                           # 微调后的 PDF
│       └── metadata/                      # 微调元数据/报告
│
├── classification/                        # ATS 关键词管理
│   ├── resume_catalog.json                # LLM 提取的关键词（extract_keywords.py 输出）
│   ├── resume_keywords_frozen.json        # 冻结关键词库（build_frozen_catalog.py 输出）
│   ├── SWE_Classification_Final_V3.md     # 分类文档
│   ├── notion_match_report.md             # Notion 匹配分析报告
│   └── notion_match_report.json           # 匹配结果（JSON）
│
├── build_resumes.py                       # ⭐ 批量编译 MD → TEX → PDF
├── md_to_tex.py                           # Markdown 解析 & LaTeX 生成
├── extract_keywords.py                    # LLM 关键词提取
├── match_resume.py                        # CLI JD 匹配 & 微调
├── update_contacts.py                     # 批量联系方式替换
├── build_frozen_catalog.py                # 确定性关键词库构建
├── notion_match.py                        # Notion 批量匹配
└── transplant_resume.py                   # 简历移植系统
```

---

## 三、环境配置

### 3.1 `.env` 文件

| 变量名 | 用途 | 示例值 |
|--------|------|--------|
| `API_KEY` | LLM 服务的认证密钥 | `sk-sp-4e60a5c3...` |
| `BASE_URL` | LLM 服务的 API 端点 | `https://coding.dashscope.aliyuncs.com/v1` |
| `LLM_MODEL` | 使用的 LLM 模型名称 | `kimi-k2.5` |
| `NOTION_TOKEN` | Notion API 认证令牌 | `ntn_127178868384...` |
| `NOTION_DB_ID` | Notion 目标数据库 ID（SWE Job Applications 2026） | `31e2f60b8d76808b...` |

### 3.2 `profiles.json` 结构

```json
[
    {"id": "A", "name": "...", "email": "...", "phone": "..."},
    {"id": "B", "name": "...", "email": "...", "phone": "..."}
]
```

**用途**：`update_contacts.py` 用此文件批量替换简历中的联系方式

### 3.3 外部工具依赖

| 工具 | 用途 | 安装方式 |
|------|------|---------|
| XeLaTeX | 从 .tex 编译 PDF | `brew install basictex` 或 `brew install mactex` |
| Helvetica Neue 字体 | 简历排版字体 | macOS 系统自带 |

### 3.4 Python 依赖

| 包名 | 用途 |
|------|------|
| `openai` | LLM API 调用（兼容 DashScope） |
| `requests` | Notion API HTTP 调用 |
| `pathlib` | 路径操作 |
| `re` | 正则表达式 |
| `json` | JSON 解析 |
| `subprocess` | 调用 xelatex 编译 |

---

## 四、核心模块详解

### 4.1 `build_resumes.py` — 批量简历编译器

**作用**：编排 MD → TEX → PDF 的完整流水线，支持自动渐进压缩

#### 常量

- `MAX_PAGES = 2`：目标最大页数
- `MAX_LEVEL = 3`：最大压缩级别
- `JUNK_EXTS`：编译后需要清理的临时文件后缀（`.aux`, `.log`, `.out`, `.fls`, `.fdb_latexmk`, `.synctex.gz`）

#### 函数

---

##### `get_pdf_pages_from_log(compile_stdout: str) -> int`

- **作用**：从 xelatex 编译输出中提取页数
- **参数**：`compile_stdout` — xelatex 的标准输出文本
- **返回值**：检测到的页数（整数）
- **原理**：正则匹配 `"Output written on ... (N pages)"` 模式

---

##### `compile_tex(tex_path: str) -> tuple[str, bool, str, int]`

- **作用**：编译单个 .tex 文件为 PDF
- **参数**：`tex_path` — .tex 文件路径
- **返回值**：`(文件名, 是否成功, 消息, 页数)`
- **执行流程**：
  1. 运行 `xelatex -interaction=nonstopmode`，输出目录为 PDF_DIR
  2. 清理临时文件（.aux, .log, .out 等）
  3. 从编译输出中提取页数
  4. 60 秒超时保护

---

##### `build_one(md_path: Path, level: int = 0) -> tuple[str, bool, int, int]`

- **作用**：在指定压缩级别下构建单份简历
- **参数**：
  - `md_path` — 源 Markdown 文件路径
  - `level` — 压缩级别（0-3）
- **返回值**：`(文件名, 是否成功, 页数, 使用的压缩级别)`
- **执行流程**：
  1. 调用 `convert_file()`（md_to_tex.py）生成 .tex
  2. 调用 `compile_tex()` 编译为 PDF
  3. 返回页数和最终压缩级别

---

##### `build_progressive(md_path: Path) -> tuple[str, bool, int, int]`

- **作用**：渐进式压缩构建——自动尝试从低到高的压缩级别，直到 ≤ 2 页
- **参数**：`md_path` — 源 Markdown 文件路径
- **返回值**：`(文件名, 是否成功, 页数, 使用的压缩级别)`
- **算法**：
  ```
  Level 0（默认间距）→ 如果 > 2 页 →
  Level 1（单行头部）→ 如果 > 2 页 →
  Level 2（+ 单行工作条目）→ 如果 > 2 页 →
  Level 3（+ 紧凑间距）
  ```
- **返回**：在第一个满足 ≤ 2 页的级别停止

---

##### `main()`

- **命令行参数**：
  - `--single`：编译指定的 .md 文件
  - `--parallel`：并行编译（当前版本未实现）
  - `--tex-only`：只生成 .tex，跳过 PDF 编译
  - `--level 0|1|2|3`：强制使用指定压缩级别（跳过渐进）
- **执行流程**：
  1. 发现 resumes/ 目录下所有 .md 文件（或 `--single` 指定的文件）
  2. 创建 output/tex/ 和 output/pdf/ 目录
  3. 如果 `--tex-only`：只转换 MD → TEX
  4. 否则：对每个简历调用 `build_progressive()`
  5. 输出统计：成功数、各压缩级别分布

---

### 4.2 `md_to_tex.py` — Markdown 转 LaTeX 转换器

**作用**：解析简历 Markdown 格式，生成 XeLaTeX 源文件，支持 4 级压缩

#### 压缩级别详解

| 级别 | 头部格式 | 工作条目格式 | 间距 |
|------|---------|-------------|------|
| 0 | 两行（名字 + 联系方式分开） | 两行（职位/日期分开） | 正常 |
| 1 | 单行（名字 \| 联系方式） | 同 Level 0 | 正常 |
| 2 | 同 Level 1 | 单行（职位 \| 公司 \| 城市 \| 日期） | 正常 |
| 3 | 同 Level 2 | 同 Level 2 | 紧凑（更小边距，更紧凑的列表） |

#### 类：`ResumeParser`

**状态机解析器**，逐行解析简历 Markdown 结构

##### 构造函数：`__init__(self, md_text: str)`

- **属性**：
  - `lines`：所有行
  - `idx`：当前行索引
  - `name`, `email`, `phone`：联系信息
  - `summary_bullets`：专业摘要要点
  - `work_experience`：工作经历列表
  - `projects`：项目列表
  - `skills`：技能列表
  - `education`：教育经历列表
  - `additional`：附加信息

##### `parse()`

- **作用**：主解析入口，逐行识别章节类型
- **识别模式**：
  - `# [Candidate Name]` → 提取姓名
  - `email | phone` → 提取联系方式
  - `## Professional Summary` → 调用 `_parse_summary()`
  - `## Work Experience` → 调用 `_parse_experience()`
  - `## Projects` → 调用 `_parse_projects()`
  - `## Skills` → 调用 `_parse_skills()`
  - `## Education` → 调用 `_parse_education()`
  - `## Additional Information` → 调用 `_parse_additional()`

##### `_parse_contact_line(line: str)`

- **作用**：从联系行中提取 email 和电话
- **分隔符**：`|`
- **正则**：
  - Email：`^[\w\.\+\-]+@[\w\.\-]+\.\w+$`
  - Phone：`^\+?[\d\-\s\(\)\.]{7,}$`

##### `_parse_one_experience()`

- **作用**：解析单个工作经历
- **标题格式**：`### Title | Company · Team | Location`
- **提取**：title, company_team, location（按 `|` 分割）
- **日期行**：下一个非空行（如 `**Jun 2025 – Dec 2025**`）
- **内容**：调用 `_collect_items()` 收集要点和子项目

##### `_collect_items()`

- **作用**：收集工作经历下的条目
- **返回值**：`[(type, text)]` 元组列表
- **类型**：
  - `'bullet'`（以 `*` 或 `-` 开头的要点）
  - `'subproject'`（加粗+斜体的子项目标题）

##### `_parse_skills()`

- **格式**：`**Category:** items` 或 `* **Category:** items`
- **正则**：`^\*\*(.+?)[:\uff1a]\*\*\s*(.+)$`（支持中英文冒号）

##### `_parse_education()`

- **格式**：Markdown 三列表格
  ```
  | Degree | Institution | Date |
  |--------|-------------|------|
  ```

##### 辅助函数

| 函数 | 参数 | 返回值 | 作用 |
|------|------|--------|------|
| `_strip_bullet(line)` | 行文本 | `str \| None` | 去除 `* ` 或 `- ` 前缀 |
| `_is_subproject_heading(line)` | 行文本 | `str \| None` | 检测子项目标题 |

---

#### `escape_latex(text: str) -> str`

- **作用**：转义 LaTeX 特殊字符，同时保留 `**bold**` 格式
- **流程**：
  1. 按 `**bold**` 标记分割文本
  2. 非加粗部分用 `_escape_raw()` 转义
  3. 加粗部分包装为 `\textbf{}`
  4. 重新拼接

#### `_escape_raw(text: str) -> str`

- **字符映射**：

  | 原字符 | LaTeX 命令 |
  |--------|-----------|
  | `\` | `\textbackslash{}` |
  | `&` | `\&` |
  | `%` | `\%` |
  | `$` | `\$` |
  | `#` | `\#` |
  | `_` | `\_` |
  | `{` | `\{` |
  | `}` | `\}` |
  | `~` | `\textasciitilde{}` |
  | `^` | `\textasciicircum{}` |
  | `–` | `--` |
  | `—` | `---` |
  | `≤` | `$\leq$` |
  | `≥` | `$\geq$` |
  | `<` | `\textless{}` |
  | `>` | `\textgreater{}` |

---

#### `emit_latex(parser: ResumeParser, level: int = 0) -> str`

- **作用**：将解析后的简历转换为完整的 LaTeX 文档
- **压缩参数（按级别）**：

  | 参数 | Level 0 | Level 3 |
  |------|---------|---------|
  | `top_margin` | 0.50in | 0.48in |
  | `section_before` | 10pt | 8pt |
  | `section_after` | 4pt | 3pt |
  | `itemsep` | 2pt | 1.5pt |

- **生成的文档结构**：
  1. **Preamble**：XeLaTeX 设置 + 几何参数 + 颜色定义
  2. **Header**：姓名（16pt 加粗）+ 联系方式（9.5pt 带链接）
  3. **Professional Summary**：章节 + 项目列表
  4. **Work Experience**：每份工作的标题 + 要点 + 子项目
  5. **Projects**：章节 + 子章节 + 要点
  6. **Skills**：键值对（类别: 技能列表）
  7. **Education**：三列表格
  8. **Additional Information**：项目列表

---

#### `build_preamble(level: int = 0) -> str`

- **作用**：生成 XeLaTeX 文档序言
- **加载的 LaTeX 包**：

  | 包名 | 用途 |
  |------|------|
  | `fontspec` | XeLaTeX 字体处理 |
  | `titlesec` | 章节格式化 |
  | `xcolor` | 颜色定义 |
  | `enumitem` | 列表自定义 |
  | `hyperref` | 超链接（hidelinks） |
  | `fancyhdr` | 页眉页脚 |
  | `tabularx` | 表格支持 |
  | `geometry` | 页面边距 |
  | `needspace` | 防止标题与正文分页 |
  | `microtype` | 排版微调 |

- **颜色定义**：
  - `sectionblue`：RGB(2B, 57, 9A) — 章节标题、职位名
  - `locgray`：RGB(66, 66, 66) — 地点文字
  - `dategray`：RGB(44, 44, 44) — 日期文字

- **字体**：全文使用 Helvetica Neue

---

#### `convert_file(md_path, output_dir=None, compact=False, level=None) -> str`

- **作用**：公开 API，将单个 MD 文件转换为 TEX
- **参数**：
  - `md_path`：输入 Markdown 文件路径
  - `output_dir`：输出目录（默认与输入同目录）
  - `compact`：已废弃（请用 level=3）
  - `level`：压缩级别 0-3
- **返回值**：生成的 .tex 文件路径
- **流程**：读取 MD → 解析 → 生成 LaTeX → 写入文件

---

### 4.3 `extract_keywords.py` — ATS 关键词提取

**作用**：使用 LLM 从简历全文中提取关键词，支持重新编号和排序

#### 常量

- `EXTRACTION_PROMPT`：LLM 关键词提取的用户 prompt
- `CATALOG_PATH`：`classification/resume_catalog.json`

#### 函数

---

##### `call_llm(content: str, max_retries: int = 2) -> dict | None`

- **作用**：调用 LLM 提取关键词
- **模型**：kimi-k2.5
- **System Prompt**："你是 ATS 简历分析专家。只输出 JSON，不要任何额外文字。"
- **温度**：0.1，max_tokens: 2000
- **返回值**：
  ```json
  {
      "hard_keywords": ["Python", "React", "AWS"],
      "core_stack": ["Python", "React", "AWS"],
      "business_directions": ["AI", "FinTech"],
      "experience_domains": ["互联网", "金融"]
  }
  ```

---

##### `compute_similarity(kw1: set, kw2: set) -> float`

- **作用**：计算两个关键词集合的 Jaccard 相似度
- **公式**：`|交集| / |并集|`
- **边界**：两个空集 → 1.0

---

##### `cluster_sort(catalog: list) -> list`

- **作用**：将简历按 AI/GenAI 标签分组，组内按相似度贪心排序
- **AI 关键词集**：{ai, genai, llm, machine learning, ...}
- **算法**：
  1. 标记含 AI 关键词的简历
  2. 分为 AI 组和其他组
  3. 每组内部贪心排序（总是选与上一份最相似的简历作为下一个）
  4. 拼接：AI 组 + 其他组

---

##### `renumber_resumes(catalog: list) -> list`

- **作用**：根据排序结果重命名简历文件
- **流程**：
  1. 创建临时目录 `_temp_rename`
  2. 所有文件先复制到临时目录（避免覆盖）
  3. 按排序顺序重命名：`{编号:02d}_{描述}.md`
  4. 更新 catalog 中的 `source_file` 和 `id`
  5. 清理临时目录

---

##### `main()`

- **命令行参数**：
  - `--renumber`：同时重命名和重排文件
  - `--dry-run`：只打印结果不保存
- **流程**：
  1. 发现所有 .md 文件
  2. 对每个文件调用 LLM 提取关键词
  3. 调用 `cluster_sort()` 排序
  4. 可选调用 `renumber_resumes()` 重命名
  5. 保存到 `classification/resume_catalog.json`

---

### 4.4 `match_resume.py` — JD 匹配 & LLM 微调（CLI）

**作用**：从命令行匹配 JD 与简历库，可选自动微调最佳匹配

#### Prompt 模板

##### `JD_EXTRACTION_PROMPT`

- **System**："你是 ATS JD 分析专家。只输出 JSON，不要任何额外文字。"
- **输出 JSON**：
  ```json
  {
      "job_title": "职位名称",
      "required_stack": ["必须核心技术 3-8 项"],
      "preferred_stack": ["加分项"],
      "business_direction": "业务方向描述",
      "seniority": "junior | mid | senior"
  }
  ```

##### `TUNE_PROMPT`

- **System**："你是简历微调专家。直接输出完整的 Markdown 简历。"
- **微调规则**：
  1. 只做"微微调"——调整措辞、重排、强调现有技能
  2. **绝不伪造不存在的经历**
  3. 可以调整 Professional Summary 的业务方向描述
  4. 可以重排 Skills 顺序
  5. 可以微调 bullet point 的关键词以匹配 JD
  6. 保持 MD 格式、姓名、联系方式、教育经历、Additional Information 不变

#### 函数

---

##### `extract_jd_keywords(jd_text: str) -> dict | None`

- **作用**：调用 LLM 从 JD 文本中提取关键词
- **返回值**：包含 required_stack, preferred_stack, business_direction 等

---

##### `match_catalog(jd_info: dict, catalog: list) -> list`

- **作用**：将所有简历与 JD 进行匹配评分
- **评分算法**：
  ```
  对每份简历：
  1. required_matched = JD 必须技术 ∩ 简历关键词
  2. required_score = 匹配数 / 总要求数
  3. preferred_matched = JD 加分项 ∩ 简历关键词
  4. preferred_score = 匹配数 / 总加分项数
  5. biz_score = JD 业务方向与简历业务方向的词级重叠
  6. total = 0.6 × required + 0.15 × preferred + 0.25 × biz
  7. core_full_match 标志：required ⊆ 简历关键词
  ```
- **返回值**：按 total 降序排列的结果列表

---

##### `tune_resume(resume_path: Path, jd_info: dict) -> Path | None`

- **作用**：使用 LLM 微调简历
- **流程**：
  1. 读取原始简历 MD
  2. 格式化 TUNE_PROMPT（注入 JD 要求）
  3. 调用 LLM 获取微调后的 MD
  4. 去除 Markdown 代码块标记
  5. 确定新文件编号（现有最大编号 + 1）
  6. 从 JD 标题生成文件名（如 "Software_Engineer"）
  7. 写入 `resumes/{新编号:02d}_{描述}_Resume.md`
  8. 更新 `classification/resume_catalog.json`
  9. 返回新路径

---

##### `build_pdf(md_path: Path) -> Path | None`

- **作用**：将 MD 文件编译为 PDF
- **流程**：调用 `convert_file()` → `xelatex` 编译 → 清理临时文件

---

##### `main()`

- **命令行参数**：
  - `--jd`：JD 文件路径（必需）
  - `--auto-tune`：如果没有完美匹配，自动微调最佳候选
  - `--top`：显示前 N 个匹配（默认 3）
- **流程**：
  1. 加载 JD 文件
  2. 加载 catalog
  3. LLM 提取 JD 关键词
  4. 匹配所有简历
  5. 显示 Top N 结果（含 required %、缺失关键词、biz 分数）
  6. 如果 `--auto-tune` 且非完美匹配：调用 `tune_resume()` + `build_pdf()`

---

### 4.5 `update_contacts.py` — 批量联系方式替换

**作用**：不修改原文件，为不同身份生成替换了联系方式的简历副本

#### 函数

---

##### `extract_current_contact(md_text: str) -> dict`

- **作用**：从 MD 文本中提取当前联系方式
- **提取**：
  - Name：第一个 `# ` 标题（非 `## `）
  - Email：正则 `^[\w\.\+\-]+@[\w\.\-]+\.\w+$`
  - Phone：正则 `^\+?[\d\-\s\(\)\.]{7,}$`
- **返回值**：`{name, email, phone, name_line_idx, contact_line_idx}`

---

##### `replace_contact(md_text: str, current: dict, profile: dict) -> str`

- **作用**：替换联系方式
- **逻辑**：
  1. 替换姓名行中的名字
  2. 重建联系方式行：`email | phone`

---

##### `process_profile(profile: dict, resume_dir: Path, output_base: Path)`

- **作用**：为一个身份处理所有简历
- **对每个 .md 文件**：提取当前联系方式 → 替换 → 写入 `output/{profile_id}/resumes/`

---

##### `main()`

- **命令行参数**：
  - `--profile, -p`：处理指定身份 ID
  - `--profiles-file`：profiles.json 路径
- **流程**：加载 profiles → 对每个 profile 调用 `process_profile()`

---

### 4.6 `build_frozen_catalog.py` — 冻结关键词库

**作用**：使用标准词表（不依赖 LLM）构建确定性关键词库

#### 函数

##### `main()`

- **命令行参数**：
  - `--verbose, -v`：打印每份简历的详细关键词
- **流程**：
  1. 发现所有 `*_Resume.md` 文件
  2. 对每个文件：
     - 读取全文
     - 去除 "Go (Weiqi)" 引用（避免围棋被误识为 Go 语言）
     - 去除 Additional Information 部分
     - 用 `scan_keywords()` 扫描 TECH_VOCAB 和 BIZ_VOCAB
     - 创建条目：`{id, source_file, tech_keywords, business_directions}`
  3. 保存到 `classification/resume_keywords_frozen.json`
  4. 输出统计

**导入自 `notion_match`**：`TECH_VOCAB`, `BIZ_VOCAB`, `scan_keywords()`

**输出格式**：
```json
[
    {
        "id": 1,
        "source_file": "01_AI_Application_GenAI_Integration_Engineer_Resume.md",
        "tech_keywords": ["ai", "llm", "langchain", "python"],
        "business_directions": ["ai", "genai"]
    }
]
```

---

### 4.7 `notion_match.py` — Notion 批量 JD 匹配

**作用**：确定性（无 LLM）的 JD-简历匹配系统，与 Notion 数据库集成

这是项目中最复杂的文件，包含词汇表、OR 组检测、自适应权重评分等。

#### 词汇表

##### `TECH_VOCAB`（146 个术语）

涵盖以下领域：
- **编程语言**：python, java, go, c++, c#, typescript, javascript, rust, scala, kotlin, swift...
- **AI/ML**：llm, rag, ai, ml, nlp, bert, gpt, pytorch, tensorflow, huggingface, langchain...
- **Web 框架**：react, angular, vue, next.js, spring boot, django, fastapi, flask...
- **云服务**：aws, gcp, azure, eks, ecs, lambda, gke, bigquery, s3...
- **基础设施**：kubernetes, docker, terraform, helm, istio, ansible...
- **数据**：kafka, spark, airflow, redis, mongodb, postgresql, elasticsearch, snowflake...
- **DevOps**：ci/cd, github actions, jenkins, argocd, prometheus, grafana, datadog...
- **协议**：grpc, rest, graphql, protobuf, websocket, tcp/ip, tls, http/2...
- **安全**：security, threat detection, dlp, siem, oauth, jwt, encryption, rbac, abac...
- **系统**：distributed systems, microservices, cuda, llvm, compiler...

##### `BIZ_VOCAB`（38 个术语）

- **行业**：fintech, e-commerce, payments, blockchain, embedded, iot, robotics
- **职能**：security, fraud, compliance, privacy, ads, search, ranking, analytics, sre
- **技术方向**：ai, ml, nlp, computer vision, data engineering, data pipeline

##### `ALIASES`（标准化别名）

| 别名 | 标准形式 |
|------|---------|
| golang | go |
| hive sql | hiveql |
| spark sql | sparksql |
| apache airflow | airflow |
| protocol buffers | protobuf |
| generative ai | genai |
| restful | rest |
| pyspark | spark |

##### `COMPOUND_SLASH_KEYWORDS`

不应被 `/` 分割的复合关键词：`ci/cd`, `tcp/ip`, `http/2`, `rbac`, `abac`

#### 函数

---

##### `scan_keywords(text: str, vocab: list[str]) -> set[str]`

- **作用**：在文本中扫描词表关键词
- **算法**：
  1. 小写化文本
  2. 对每个词表术语，用词边界正则 `\b{term}\b` 搜索
  3. 通过 ALIASES 标准化
  4. 返回标准化后的关键词集合
- **处理**：支持多词短语如 "machine learning"、"smart contract"

---

##### `detect_or_groups(jd_text: str, detected_tech: set[str]) -> list[frozenset]`

- **作用**：检测 JD 中的 "X or Y" 或 "X/Y" 关系
- **算法**：
  1. 对每对检测到的关键词：
     - 检查文本中是否存在 "X or Y" 模式
     - 检查是否存在 "X/Y" 模式（跳过 COMPOUND_SLASH_KEYWORDS）
     - 处理别名变体
  2. 合并重叠的组（类似并查集）
  3. 返回 frozenset 列表

---

##### `build_requirements(detected_tech: set[str], or_groups: list[frozenset]) -> list[frozenset]`

- **作用**：构建需求列表（处理 OR 关系）
- **逻辑**：
  - OR 组中的关键词 → 单个需求（满足任一即可）
  - 其余关键词 → 每个是独立需求

---

##### `compute_match(tech_requirements, jd_biz, resume_tech, resume_biz) -> dict`

- **作用**：计算单份简历与 JD 的匹配度
- **评分**：
  ```
  tech_score = 满足的需求数 / 总需求数
  biz_score = 匹配的业务关键词数 / 总业务关键词数

  自适应权重：
  - 既有技术又有业务：total = 0.7 × tech + 0.3 × biz
  - 只有技术：total = tech_score
  - 只有业务：total = biz_score
  - 都没有：total = 0.0
  ```
- **返回值**：
  ```python
  {
      'total': 0.85,
      'tech_score': 0.90,
      'biz_score': 0.75,
      'satisfied': 9,
      'total_requirements': 10,
      'matched_tech': ['python', 'react'],
      'missing_tech': ['rust'],
      'matched_biz': ['fintech'],
      'missing_biz': ['blockchain']
  }
  ```

---

##### `match_all_resumes(jd_text: str, catalog: list) -> list[dict]`

- **作用**：将一个 JD 与所有简历匹配
- **流程**：
  1. 扫描 JD 中的 TECH_VOCAB 关键词
  2. 扫描 JD 中的 BIZ_VOCAB 关键词
  3. 检测 OR 组
  4. 构建需求列表
  5. 对每份简历调用 `compute_match()`
  6. 按 total 降序排列

---

##### Notion API 函数

| 函数 | 参数 | 返回值 | 作用 |
|------|------|--------|------|
| `query_notion_db(db_id, start_cursor=None)` | 数据库 ID | `dict` | 查询 Notion 数据库（单页） |
| `get_all_pages(db_id)` | 数据库 ID | `list[dict]` | 分页获取所有页面 |
| `extract_page_info(page)` | Notion 页面 | `dict` | 提取 Job Title, Company, Team, Cleaned JD, Resume |
| `update_notion_fields(page_id, resume_label, score, analysis)` | 参数 | `bool` | 更新 Resume、Match Score、Match Analysis 字段 |
| `format_analysis_text(info, best, top3)` | 信息 | `str` | 生成中文分析文本 |
| `generate_md_report(all_job_results, output_path)` | 结果列表 | `None` | 生成 Markdown 分析报告 |

---

##### `main()`

- **命令行参数**：
  - `--all`：重新匹配所有 JD（覆盖已有 Resume 字段）
  - `--dry-run`：只打印不写入 Notion
  - `--report`：生成 MD 报告
  - `--top`：记录前 N 个候选（默认 3）
- **流程**：
  1. 加载冻结关键词 catalog
  2. 获取 Notion 数据库所有页面
  3. 对每个有 Cleaned JD 的页面：
     - 匹配所有简历
     - 获取 Top N 候选
     - 生成分析文本
     - 写入 Notion（除非 --dry-run）
  4. 输出统计（≥75% 匹配率、平均分等）
  5. 如果 `--report`：生成 MD 报告

---

### 4.8 `transplant_resume.py` — 简历移植系统

**作用**：最复杂的模块。基于人物画像兼容性 + 场景感知的智能关键词注入

#### 聚类定义

```python
CLUSTERS = {
    'backend':  [6, 7, 9, 15, 22],     # 后端相关简历
    'cloud':    [8, 10, 11, 13, 14],    # 云/基础设施相关
    'ai':       [1, 4, 5],              # AI/ML 相关
    'data':     [2, 3],                 # 数据工程相关
    'security': [3, 5],                 # 安全相关
}
ISOLATED_IDS = {12, 16, 17, 18, 19, 20, 21}  # 不参与移植的简历
```

#### 22 个人物画像标签

| ID | 标签 | 描述 |
|----|------|------|
| 1 | ai_genai | AI/GenAI 应用工程师 |
| 2 | cloud_data | 云数据管道工程师 |
| 3 | security | 安全工程师 |
| 4 | ml_research | ML 研究工程师 |
| 5 | responsible_ai | 负责任 AI 工程师 |
| 6 | fullstack | 全栈工程师 |
| 7 | generalist_sde | 通才 SDE |
| 8 | cloud_infra | 云基础设施工程师 |
| 9 | backend | 后端工程师 |
| 10 | devops | DevOps 工程师 |
| 11 | solutions | 解决方案工程师 |
| 12 | blockchain | 区块链工程师 |
| 13 | edge_networking | 边缘网络工程师 |
| 14 | reliability | 可靠性工程师 |
| 15 | python_fintech | Python/金融科技工程师 |
| 16 | frontend | 前端工程师 |
| 17 | embedded | 嵌入式工程师 |
| 18 | hpc_compiler | HPC/编译器工程师 |
| 19 | systems | 系统工程师 |
| 20 | billing | 计费工程师 |
| 21 | qa_sdet | QA/SDET 工程师 |
| 22 | mobile | 移动端工程师 |

#### 人物画像兼容性矩阵

**相同家族**（高兼容性 0.75-0.85）：
- (ai_genai, ml_research) = 0.85
- (backend, fullstack) = 0.80

**跨家族**（低兼容性 0.15-0.45）：
- (frontend, hpc_compiler) = 0.15

**未指定的组合**：默认 0.5

#### 7 个场景-技术亲和矩阵

| 场景 | 亲和技术 |
|------|---------|
| backend_service | python, go, java, redis, kafka, docker, postgresql, graphql... |
| data_pipeline | spark, flink, airflow, hive, hadoop, snowflake, databricks... |
| ml_training | pytorch, tensorflow, cuda, huggingface, langchain, llm, rag... |
| frontend_app | react, vue, typescript, webpack, tailwind, cypress... |
| devops_infra | terraform, ansible, kubernetes, prometheus, github actions... |
| mobile | kotlin, swift, android, ios, firebase, jetpack... |
| qa_automation | selenium, cypress, playwright, pytest, postman... |

#### 函数

---

##### `detect_jd_role(jd_text: str) -> str | None`

- **作用**：扫描 JD 中的角色信号词
- **返回值**：如果 ≥ 2 个信号词匹配，返回角色标签；否则 None

##### `get_persona_compatibility(resume_id: int, jd_role: str | None) -> float`

- **作用**：查询人物画像兼容性矩阵
- **返回值**：0.0-1.0 兼容度分数

##### `classify_bullet_scene(bullet: str) -> str`

- **作用**：分析 bullet point 文本所属的场景
- **返回值**：最匹配的场景名

##### `is_injectable(keyword: str, bullet: str) -> bool`

- **作用**：判断关键词是否与 bullet 的场景逻辑兼容
- **原理**：查询 SCENE_TECH_AFFINITY

##### `get_cluster(resume_id: int) -> str | None`

- **作用**：获取简历所属聚类
- **返回值**：聚类名或 None（isolated）

##### `get_best_cluster_for_jd(resume_id: int, jd_biz: set) -> str | None`

- **作用**：对多聚类简历，选择最匹配 JD 业务方向的聚类

##### `extract_bullets(md_text: str) -> list[tuple[int, str]]`

- **作用**：从 MD 文本中提取所有 bullet point
- **返回值**：`[(行号, 原始行文本), ...]`

##### `find_best_bullet_for_keyword(bullets, keyword, already_modified) -> tuple | None`

- **作用**：为关键词找到最合适的注入位置
- **两层过滤**：
  1. 场景兼容性（SCENE_TECH_AFFINITY）
  2. 语义相关性（领域亲和关键词）
- **返回值**：`(行号, 行文本)` 或 None

##### `format_kw_display(kw: str) -> str`

- **作用**：关键词显示格式化（如 'python' → 'Python'）
- **来源**：查询 DISPLAY_KW 字典

##### `call_llm(prompt: str, system: str = "", max_retries: int = 2) -> str | None`

- **作用**：当确定性注入找不到合适位置时，使用 LLM 生成段落
- **温度**：0.1，max_tokens: 1000

---

## 五、词汇表与配置

### TECH_VOCAB 完整列表（146 项）

共涵盖编程语言、AI/ML 框架、Web 框架、云服务、基础设施工具、数据库/消息队列、DevOps 工具、网络协议、安全技术、系统技术等。详见 `notion_match.py` 文件头部。

### BIZ_VOCAB 完整列表（38 项）

共涵盖行业领域、职能方向、技术方向。详见 `notion_match.py` 文件头部。

### ALIASES 完整映射

详见 `notion_match.py` 中的 `ALIASES` 字典。关键映射：golang→go, pyspark→spark, restful→rest, generative ai→genai。

---

## 六、数据目录结构

| 目录/文件 | 用途 | 来源 |
|-----------|------|------|
| `resumes/*.md` | 22 份 Markdown 源简历 | 手动编写/LLM 微调 |
| `output/tex/*.tex` | 生成的 LaTeX 文件 | `build_resumes.py` |
| `output/pdf/*.pdf` | 生成的 PDF 文件 | `build_resumes.py` |
| `output/tuned/md/*.md` | 微调后的 Markdown | `match_resume.py` |
| `output/tuned/tex/*.tex` | 微调后的 LaTeX | 手动/脚本 |
| `output/tuned/pdf/*.pdf` | 微调后的 PDF | 手动/脚本 |
| `output/tuned/metadata/` | 微调元数据 | 脚本 |
| `classification/resume_catalog.json` | LLM 提取的关键词库 | `extract_keywords.py` |
| `classification/resume_keywords_frozen.json` | 冻结关键词库 | `build_frozen_catalog.py` |
| `classification/notion_match_report.md` | Notion 匹配报告 | `notion_match.py` |
| `classification/notion_match_report.json` | 匹配结果 JSON | `notion_match.py` |

---

## 七、文件同步规则

以下目录**严格 1:1 同步**：

```
resumes/*.md (22 个文件) ↔ output/tex/*.tex ↔ output/pdf/*.pdf
```

`classification/resume_catalog.json` 的条目数必须与 `resumes/` 中的文件数一致。

**标准重建流程**：

```bash
# 1. 重新编译所有简历
python3 build_resumes.py

# 2. 重新生成冻结关键词库
python3 build_frozen_catalog.py

# 3. 重新匹配所有 Notion JD
python3 notion_match.py --all --report
```

---

## 八、完整调用关系图

```
build_resumes.py (批量编译入口)
├── md_to_tex.convert_file()
│   ├── ResumeParser.parse()
│   │   ├── _parse_contact_line()
│   │   ├── _parse_summary()
│   │   ├── _parse_experience()
│   │   │   └── _collect_items()
│   │   ├── _parse_projects()
│   │   ├── _parse_skills()
│   │   ├── _parse_education()
│   │   └── _parse_additional()
│   ├── emit_latex()
│   │   ├── build_preamble()
│   │   └── escape_latex() → _escape_raw()
│   └── 写入 .tex 文件
├── compile_tex()
│   ├── subprocess: xelatex
│   └── get_pdf_pages_from_log()
└── build_progressive()
    └── build_one() × 最多 4 次

extract_keywords.py (LLM 关键词提取)
├── call_llm()          [LLM API]
├── cluster_sort()
│   └── compute_similarity()
├── renumber_resumes()
└── 保存 resume_catalog.json

build_frozen_catalog.py (确定性关键词库)
├── notion_match.scan_keywords()  [导入]
│   ├── TECH_VOCAB
│   └── BIZ_VOCAB
└── 保存 resume_keywords_frozen.json

match_resume.py (CLI JD 匹配)
├── extract_jd_keywords()
│   └── call_llm()      [LLM API]
├── match_catalog()
├── tune_resume()
│   └── call_llm()      [LLM API]
└── build_pdf()
    ├── md_to_tex.convert_file()
    └── subprocess: xelatex

notion_match.py (Notion 批量匹配)
├── scan_keywords()     [TECH_VOCAB + BIZ_VOCAB]
├── detect_or_groups()
├── build_requirements()
├── compute_match()
├── match_all_resumes()
├── query_notion_db()   [Notion API]
├── get_all_pages()     [Notion API]
├── extract_page_info()
├── update_notion_fields()  [Notion API]
├── format_analysis_text()
└── generate_md_report()

transplant_resume.py (简历移植)
├── detect_jd_role()
├── get_persona_compatibility()
├── classify_bullet_scene()
├── is_injectable()
├── extract_bullets()
├── find_best_bullet_for_keyword()
├── format_kw_display()
└── call_llm()          [LLM API, 兜底]

update_contacts.py (联系方式替换)
├── extract_current_contact()
├── replace_contact()
└── process_profile()
```

---

## 九、工作流程示例

### 场景 1：全量重建所有简历 PDF

```bash
python3 build_resumes.py
```

**流程**：
1. 发现 `resumes/` 下所有 .md 文件
2. 对每个文件：`build_progressive()`
3. MD → TEX（Level 0）→ PDF（xelatex）
4. 如果 > 2 页，升级到 Level 1/2/3 重试
5. 输出统计

### 场景 2：提取关键词并重排简历

```bash
python3 extract_keywords.py --renumber
```

**流程**：
1. 对每份简历调用 LLM 提取 {hard_keywords, core_stack, business_directions}
2. `cluster_sort()`：AI/GenAI 简历优先，组内按相似度贪心排序
3. `renumber_resumes()`：按排序结果重命名文件 01-22
4. 保存到 `classification/resume_catalog.json`

### 场景 3：CLI 匹配 JD

```bash
python3 match_resume.py --jd path/to/jd.md --auto-tune --top 5
```

**流程**：
1. 加载 JD 文件
2. LLM 提取 JD 关键词
3. 加载 catalog
4. 匹配所有简历（0.6 × required + 0.15 × preferred + 0.25 × biz）
5. 显示前 5 个候选
6. 如果最佳 < 75%：LLM 微调最佳候选 + 编译 PDF

### 场景 4：Notion 批量匹配

```bash
python3 notion_match.py --all --report
```

**流程**：
1. 加载冻结关键词 catalog（无 LLM）
2. 获取 Notion 数据库所有页面
3. 对每个有 Cleaned JD 的页面：
   - 扫描 TECH_VOCAB + BIZ_VOCAB
   - 检测 OR 组（"X or Y"、"X/Y"）
   - 构建需求列表
   - 匹配所有简历
   - 更新 Notion：Resume + Match Score + Match Analysis
4. 生成 MD 报告

### 场景 5：为不同身份生成简历

```bash
python3 update_contacts.py --profile A
```

**流程**：
1. 从 profiles.json 加载指定身份
2. 对 resumes/ 下每份简历：替换姓名、email、电话
3. 输出到 `output/{profile_id}/resumes/`

---

## 十、常用运行命令

```bash
# ===== 简历编译 =====

# 全量编译（渐进压缩）
python3 build_resumes.py

# 编译单份简历
python3 build_resumes.py --single resumes/01_AI_Resume.md

# 只生成 TEX（不编译 PDF）
python3 build_resumes.py --tex-only

# 指定压缩级别
python3 build_resumes.py --level 2

# ===== 关键词管理 =====

# LLM 提取关键词
python3 extract_keywords.py

# 提取并重新编号
python3 extract_keywords.py --renumber

# 干跑（只看结果不保存）
python3 extract_keywords.py --dry-run

# 构建冻结词库
python3 build_frozen_catalog.py

# 详细模式
python3 build_frozen_catalog.py -v

# ===== JD 匹配 =====

# CLI 匹配
python3 match_resume.py --jd path/to/jd.md

# 自动微调
python3 match_resume.py --jd path/to/jd.md --auto-tune

# 显示前 5 个候选
python3 match_resume.py --jd path/to/jd.md --top 5

# ===== Notion 集成 =====

# 匹配未处理的 JD
python3 notion_match.py

# 全量重新匹配
python3 notion_match.py --all

# 干跑 + 报告
python3 notion_match.py --dry-run --report

# ===== 联系方式 =====

# 为指定身份生成
python3 update_contacts.py -p A

# 为所有身份生成
python3 update_contacts.py
```

---

## 十一、迭代指南

> 想改动某个功能时，快速定位到该改哪个文件的哪个函数

| 想做的事情 | 改哪个文件 | 改哪个函数/位置 |
|-----------|-----------|---------------|
| 修改简历排版样式 | `md_to_tex.py` | `emit_latex()` + `build_preamble()` |
| 修改字体 | `md_to_tex.py` | `build_preamble()` 中的 `\setmainfont` |
| 修改颜色 | `md_to_tex.py` | `build_preamble()` 中的 `\definecolor` |
| 添加新压缩级别 | `md_to_tex.py` | `emit_latex()` 的 level 条件分支 |
| 修改页面边距 | `md_to_tex.py` | `build_preamble()` 中的 geometry 设置 |
| 修改目标页数上限 | `build_resumes.py` | `MAX_PAGES = 2` 常量 |
| 支持新的 MD 章节格式 | `md_to_tex.py` | `ResumeParser.parse()` 添加新的匹配分支 |
| 修改 LaTeX 特殊字符转义 | `md_to_tex.py` | `_escape_raw()` 中的字符映射 |
| 修改 LLM 关键词提取 prompt | `extract_keywords.py` | `EXTRACTION_PROMPT` 常量 |
| 修改 JD 分析 prompt | `match_resume.py` | `JD_EXTRACTION_PROMPT` 常量 |
| 修改简历微调规则 | `match_resume.py` | `TUNE_PROMPT` 常量 |
| 修改匹配权重 | `match_resume.py` | `match_catalog()` 中的权重 0.6/0.15/0.25 |
| 添加新技术关键词 | `notion_match.py` | `TECH_VOCAB` 列表 |
| 添加新业务方向 | `notion_match.py` | `BIZ_VOCAB` 列表 |
| 添加新别名 | `notion_match.py` | `ALIASES` 字典 |
| 修改 Notion 匹配权重 | `notion_match.py` | `compute_match()` 中的 0.7/0.3 权重 |
| 修改 Notion 字段映射 | `notion_match.py` | `update_notion_fields()` |
| 添加新 Notion 字段 | `notion_match.py` | `update_notion_fields()` 的 properties 字典 |
| 修改 OR 组检测逻辑 | `notion_match.py` | `detect_or_groups()` |
| 添加新聚类 | `transplant_resume.py` | `CLUSTERS` 字典 |
| 修改人物画像兼容性 | `transplant_resume.py` | `PERSONA_COMPATIBILITY` 矩阵 |
| 添加新场景 | `transplant_resume.py` | `SCENE_TECH_AFFINITY` 字典 |
| 修改关键词注入逻辑 | `transplant_resume.py` | `find_best_bullet_for_keyword()` |
| 添加新身份 | `profiles.json` | 新增 JSON 对象 |
| 修改联系方式替换逻辑 | `update_contacts.py` | `replace_contact()` |
| 切换 LLM 模型 | `.env` | `LLM_MODEL` 变量 |
| 切换 Notion 数据库 | `.env` | `NOTION_DB_ID` 变量 |
| 修改匹配报告格式 | `notion_match.py` | `generate_md_report()` |
| 修改分析文本格式 | `notion_match.py` | `format_analysis_text()` |
