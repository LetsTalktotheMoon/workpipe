# build_skills

独立于现有项目逻辑的技能提取模块，当前同时覆盖：

- `resume` 技术栈：批量扫描 `data/deliverables` 下所有 `resume.md` 的 `## Skills`
- `jd` 技术栈：按 web app 真实岗位池口径，优先读取 `data/job_tracker/jobs_catalog.json`，并用 `data/deliverables/resume_portfolio/portfolio_index.json` 回补历史 artifact 上下文
- `combined` 视图：将 resume + jd 技术栈并集汇总到同一个 HTML 报告
- `jd` 非技术栈词频：从 `build_skills/词频分析/output/*` 读取“泛化技术称呼 / 业务 domain / 软技能”词频结果，并 append 到主 HTML 报告

## 目录

- `taxonomy.py`: skill 别名规范化和新 taxonomy。
- `descriptions.py`: 生成每个 canonical skill 的一句话介绍和一句话业务场景。
- `pipeline.py`: combined orchestrator，统一生成 resume + jd + combined 输出。
- `resume_pipeline.py`: resume 独立提取程序。
- `jd_pipeline.py`: jd 独立提取程序。
- `__main__.py`: 支持 `python3 -m build_skills` 直接运行。
- `output/`: 本模块生成的所有结果文件。
- `词频分析/output/`: JD 非技术栈 requirement phrase 的中间结果与最终词频表，主报告会直接读取这里的 CSV/JSON。

## 用法

```bash
python3 -m build_skills \
  --resume-root data/deliverables \
  --jd-scraped-path data/job_tracker/jobs_catalog.json \
  --portfolio-index-path data/deliverables/resume_portfolio/portfolio_index.json \
  --out build_skills/output
```

单独跑 resume：

```bash
python3 -m build_skills.resume_pipeline --resume-root data/deliverables --out build_skills/output
```

单独跑 jd：

```bash
python3 -m build_skills.jd_pipeline \
  --jd-scraped-path data/job_tracker/jobs_catalog.json \
  --portfolio-index-path data/deliverables/resume_portfolio/portfolio_index.json \
  --out build_skills/output
```

## 主要输出

- `output/resume/*`: resume 独立提取结果。
- `output/jd/*`: jd 独立提取结果。
- `summary.json`: combined 扫描摘要，包含 resume/jd 来源覆盖。
- `summary.json` 还会附带 `jd_non_tech_frequency_summary`，汇总非技术栈词频板的 3999 JD 口径摘要。
- `combined_canonical_skill_frequency.csv`: resume + jd 并集 canonical skill 汇总。
- `skill_source_coverage.csv`: 每个 canonical skill 在 resume/jd 中的来源覆盖情况。
- `merged_skill_narratives.json` / `merged_skill_narratives.csv`: 合并后的技术栈叙述组，允许同一技术栈在多个业务组中重复出现。
- `REPORT.html`: 可直接打开阅读的 combined HTML 报告，包含技术栈看板和非技术栈岗位要求词频分析板。
