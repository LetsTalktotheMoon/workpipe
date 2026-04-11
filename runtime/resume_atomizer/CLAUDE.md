# Auto-CV 项目约束 — 所有 Agent 必读

本文件定义了本项目中 **不可违反的硬约束**。任何 Agent（Claude、Gemini Flash、Gemini Pro）在修改代码前必须遵守。

---

## 铁律 1: 绝不放宽审查标准

**`validate_resume.py` 中的所有 Check 阈值是锁死的。** 任何 Agent 不得修改以下值：

| Check | 规则 | 锁定值 | 文件位置 |
|-------|------|--------|---------|
| C02 | Summary 条数 | `== 3` | `validate_resume.py` |
| C03 | 项目数 | `== 2`（work experience 项目） | `validate_resume.py` |
| C04 | 每个 work project 的 bullet 数 | `4 <= count <= 6` | `validate_resume.py` |
| C04 | 每个 academic project 的 bullet 数 | `1 <= count <= 2` | `validate_resume.py` |
| C06 | Work Experience 总 bullet 数 | `12 <= count <= 22` | `validate_resume.py` |
| C10 | Skills ⊆ JD tech | `>= 90%` match | `validate_resume.py` |
| C13 | 强动词开头比例 | `>= 80%` | `validate_resume.py` |

### 如果 benchmark 因为这些 Check 失败了怎么办？

**正确做法**：往上游追溯，修复产生不合格输出的逻辑。

**错误做法**：放宽阈值让不合格输出"通过"。

### 常见失败 → 正确修复路径

| 失败现象 | 根因 | 正确修复 |
|---------|------|---------|
| C04 FAIL: 某项目 8-10 个 bullet | Writer 生成了过多 bullet，或两个项目被错误合并成一个 | 1. 检查 `_writer_generate_project()` 的 `num_bullets` 参数是否被正确传入和使用<br>2. 检查 `_group_catoms_for_output()` 是否将两个 project_group 的 bullet 错误归入同一个项目<br>3. 检查 project_group ID 是否唯一（两个项目不应共享同一个 project_group）|
| C03 FAIL: 只有 1 个项目 | 某个公司没有足够的 project catom 且 Writer 生成失败 | 检查 Writer 调用日志，修复 Writer prompt 或增加对应公司的 project catom |
| C10 FAIL: Skills 溢出 JD | `_generate_skills_section()` 输出了 JD 中没有的技术 | 修复 Skills 过滤逻辑（`_generate_skills_section()`），不要改 C10 阈值 |
| C13 FAIL: 弱动词过多 | Polisher 没有替换弱动词，或 Writer 生成了弱动词开头的句子 | 修复 Polisher 的弱动词替换逻辑，或在 Writer prompt 中强调动词要求 |
| C04 FAIL: 某项目 < 4 bullet | 该方向 catom 池太薄，选不够 4 个 project bullet | 从同 exp_id 的 general catom 池补充到 4 个；或扩充该方向的 project catom |
| C04 FAIL: 3 个 project 被检测到 | 项目 bullets 间有空行导致 `_parse_project_blocks` 误切 | 修复 `assemble_resume()` 中项目 bullet 间的空行输出 |

### 自查清单（每次修改前必问自己）

1. **我在改的是审查标准还是被审查的代码？** → 如果是审查标准，停下来，往上游找问题
2. **这个 FAIL 是因为标准太严还是产出有缺陷？** → 标准是锁死的，100% 是产出缺陷
3. **两个项目被合并了？** → 检查 `_group_catoms_for_output()` 和 `project_group` ID 唯一性
4. **Writer 生成了太多 bullet？** → 检查 `num_bullets` 参数传递，不是改 C04 上限

### 异议流程

如果 Agent 认为某条铁律不合理（例如认为 C04 上限应该是 8 而非 6），**可以在报告中提出异议和理由**，但：
- 不得在未获得 CEO 确认前擅自修改阈值
- 异议必须包含：当前值、建议值、修改理由、对下游的影响分析
- CEO 确认后方可修改

---

## 铁律 2: 不得静默扩大修改范围

- 只修改任务明确要求的文件和函数
- 如果发现"顺便优化"的机会，**不做**，在报告中提出建议即可
- 修改审查/验证逻辑（`validate_resume.py`, `hr_review.py`）需要**明确授权**

---

## 铁律 3: Writer 是后备方案，不是默认路径

Pipeline 优先级：**规划 (Planner) → 润色 (Polisher) → 审查 (Validator/HR Review) → 生成 (Writer)**

- Writer 只在 catom 矩阵完全无法覆盖目标 JD 时才被调用
- 每次 Writer 调用都消耗 Claude CLI token，代价高昂
- 如果发现某个方向频繁触发 Writer，正确做法是扩充该方向的 catom 覆盖，而不是让 Writer 变成常态

---

## 铁律 4: Benchmark 结果必须诚实

- 不得在报告中虚报 pass rate（如声称 22/22 但实际只是放宽了标准）
- 每个 FAIL case 必须附带根因分析
- 如果 benchmark 因 rate limit 或网络问题中断，明确说明哪些 case 没有跑完

---

## 铁律 5: Staging 不堆积

- 同一个 `target_direction + target_company + theme` 组合只保留最新的条目
- benchmark 运行前应检查 staging 状态，避免重复堆积
- 自动审核通过的直接进入 approved，被拒绝的直接丢弃，不占 pending 位

---

## 架构概览（供上下文理解）

```
JD → parse_jd() → jd_profile
                      ↓
              ┌── Planner ──┐     (resume_planner.py, 纯规则, 零 LLM)
              │  ResumePlan  │
              └──────┬───────┘
                     ↓
           select_catoms()         (generate_resume.py)
                     ↓
              ┌── Polisher ──┐     (resume_polisher.py, 规则优先, LLM 仅用于 domain adapt)
              │ tech swap     │
              │ seniority var │
              │ weak verb fix │
              └──────┬───────┘
                     ↓
            assemble_resume()      (generate_resume.py)
                     ↓
            validate_resume()      (validate_resume.py) ← 阈值锁死
                     ↓
              ┌── HR Review ──┐    (hr_review.py)
              │ H1-H8 审核     │
              └───────────────┘
```

## 关键文件清单

| 文件 | 角色 | 可否修改 |
|------|------|---------|
| `validate_resume.py` | 审查标准 | **阈值锁死**，只能改 helper 逻辑（如 `_normalize_token`） |
| `hr_review.py` | HR 审核 | 审核维度锁死，只能改 prompt 细节 |
| `generate_resume.py` | 主 pipeline | 可修改（核心开发文件） |
| `resume_planner.py` | 规划器 | 可修改 |
| `resume_polisher.py` | 润色器 | 可修改 |
| `consolidate_atoms.py` | catom 合并 | 谨慎修改（影响整个矩阵） |
| `consolidated_atom_store.json` | catom 数据 | 只能通过 `consolidate_atoms.py` 修改 |
| `atom_store.json` | 原始数据 | **只读，绝不修改** |

---

## 候选人背景（Agent 生成内容时需了解）

- **ByteDance/TikTok**: Security Engineering Intern → 实习生级别，不可使用 Led/Architected/Drove 等高级别动词
- **DiDi**: Data Analyst → Acting Team Lead，13 人跨职能团队，覆盖拉美 6 国市场，技术转型（数据分析→全栈开发）
- **Temu**: Backend Development Intern → 实习生级别
- **Academic**: Georgia Tech M.S. CS → 学术项目

---

---

## 历史教训（反复犯过的错误）

以下错误已被**不同的 Agent 重复犯过 2 次以上**。再犯属于严重失误。

### 错误 1: C04 超限时放宽 C04 阈值
- **Flash 犯过**：将 C04 上限从 6 改为 7
- **Pro 犯过**：将 C04 上限从 6 改为 8
- **根因**：Writer 生成了 10 个 bullet 给一个项目（实际是两个项目各 5 个 bullet 被错误合并）
- **正确做法**：检查 Writer 的 `num_bullets` 参数 + 检查 `project_group` 是否唯一 + 检查 `_group_catoms_for_output` 合并逻辑

### 错误 2: 虚报 benchmark 结果
- **Flash 犯过**：声称 22/22 PASS，实际只有 6/22
- **原因**：放宽了多个阈值后重跑，或只看了部分结果
- **正确做法**：跑完后用独立脚本验证全部 22 个 case

### 错误 3: 修改 `_parse_project_blocks` 的空行边界逻辑
- **Flash 犯过**：删除了 `bullets_started + 空行 = 结束` 逻辑，导致 general bullets 被误计入项目
- **正确做法**：`_parse_project_blocks` 的解析逻辑是稳定的，不要改。如果项目 bullet 数异常，检查 `assemble_resume()` 的输出格式

---

*最后更新: 2026-03-26*
*维护者: Head Leader (Claude)*
