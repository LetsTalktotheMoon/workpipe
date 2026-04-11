# Auto-CV 指令手册

所有命令都在 `resume_atomizer/` 目录下运行。

## profiles.json — 个人信息配置

位于上级目录 `auto-cv/profiles.json`（不在本目录内，不会被共享给其他 agent）。

```json
[
  {"id": "A", "name": "...", "email": "...", "phone": "..."},
  {"id": "B", "name": "...", "email": "...", "phone": "..."}
]
```

> **安全提示**：`profiles.json` 和 `.env` 在上级目录 `auto-cv/` 中，本目录不含任何 PII 和密钥。

---

## 核心指令

### 从 JD 生成简历（主 pipeline）

```bash
# 从 JD 文件生成，用 profile A 的身份信息
python3 generate_resume.py --jd jd.txt --profile A

# 直接传 JD 文本
python3 generate_resume.py --jd-text "Requirements: Python, K8s..." -p B

# 只看选中了哪些 catom，不输出文件
python3 generate_resume.py --jd jd.txt --dry-run

# 指定输出文件名
python3 generate_resume.py --jd jd.txt -p A --output my_resume.md
```

输出到 `output/`。

### 静态简历替换联系方式 + 编译 PDF

```bash
# Step 1: 替换 resumes/ 下所有 MD 的联系方式 → output/{profile_id}/resumes/
python3 update_contacts.py --profile A

# Step 2: 编译 PDF
python3 build_resumes.py --single output/A/resumes/01_*.md    # 单份
python3 build_resumes.py --single "output/A/resumes/*.md"     # 全部
```

### 全量编译（默认简历集）

```bash
python3 build_resumes.py                    # 全部 MD → TEX → PDF
python3 build_resumes.py --level 2          # 指定压缩级别
python3 build_resumes.py --tex-only         # 只生成 TEX
```

压缩级别：0=默认 | 1=单行header | 2=+单行job | 3=+紧凑间距。超2页自动递进。

### JD 匹配推荐

```bash
python3 transplant_resume.py --jd jd.txt                    # 推荐 Top-5 简历
python3 transplant_resume.py --jd jd.txt --threshold 0.80   # 调达标阈值
```

### 三层简历优化（Notion 批处理）

```bash
python3 transplant_resume.py --all                # 优化所有 <75% 的 JD
python3 transplant_resume.py --all --no-llm       # 仅移植+Skills，不调 LLM
python3 transplant_resume.py --all --update-notion # 优化并回写 Notion
```

### ATS 关键词 + 编号

```bash
python3 extract_keywords.py              # 提取关键词
python3 extract_keywords.py --renumber   # 提取 + 按 ATS 相似度重新编号
```

### Notion 批量匹配

```bash
python3 notion_match.py              # 匹配无 Resume 的 JD
python3 notion_match.py --all        # 重匹配所有
python3 notion_match.py --dry-run    # 只打印，不写入
```

---

## 配置文件速查

| 要改什么 | 去哪个文件 |
|---------|-----------|
| 个人身份信息（姓名/邮箱/电话） | `../profiles.json`（上级目录，不在本目录内） |
| LLM API key / Notion token | `../.env`（上级目录） |
| 验证阈值（C04/C10/C13 等） | `validate_resume.py` (**锁死，不改**) |
| HR 审核维度 | `hr_review.py` |
| 公司背景/Seniority 规则 | `generate_resume.py` 中 `COMPANY_CONTEXT` |
| catom 数据库 | `consolidated_atom_store.json`（通过 `consolidate_atoms.py` 修改） |
| 项目铁律和约束 | `CLAUDE.md` |

## 环境依赖

- Python 3.11+, XeLaTeX (`brew install --cask mactex`), `pip install openai requests`
