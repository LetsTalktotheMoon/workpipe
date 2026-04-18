# Local Job Resume Pipeline

统一本地入口，围绕当前已经稳定的三段程序工作：

- 上游：`job-tracker/main.py --scrape-only`
- 中游：`auto-cv/resume_pipeline` 的筛选、路由、`retarget` / `free-write`
- 下游：`automation/artifacts.compile_markdown_to_pdf`

这个新项目不搬迁现有 deliverables，也不改写上游程序。它只做四个稳定命令的编排：

```bash
./run_jobs.sh
./run_resume.sh
./run_pdf.sh
./run_all.sh
./audit_backlog.sh
./write_backlog_batch.sh
./resume_state.sh
./run_job_app.sh
./backfill_job_app_yoe.sh
./scheduled_daily_pipeline.sh
```

迁移与归档说明见：

- `MIGRATION_STATUS.md`

## 推荐用法

当前仓库新增了 `scheduled_daily_pipeline.sh`，用于 `crontab` 触发的 daily full pipeline。
它会默认执行 `jobs -> resume -> PDF` 全链路，默认只处理大厂岗位，
默认看最近 `48` 小时岗位，不设运行时长上限；如需手动限时，可显式传 `--max-runtime-minutes`。

旧 `launchd` 定时任务仍只运行 `scraper` 分支，不会自动触发 resume 或 PDF。

如果你完全不想要自动 `scraper`，可以删掉系统调度文件
`/Users/jingyizhang/Library/LaunchAgents/com.autopipeline.runjobs.plist`。
删掉后就不会再有每天四次的自动抓取。

先做无 LLM 的小范围验证：

```bash
cd <repo-root>

./run_all.sh \
  --skip-scrape \
  --dry-run \
  --no-state-update
```

只跑中游本地筛选和路由：

```bash
./run_resume.sh \
  --dry-run \
  --no-state-update
```

清点历史岗位池，不写 state、不触发 LLM：

```bash
./audit_backlog.sh --max-jobs 200
```

不传 `--max-jobs` 时默认不设上限；只有你显式传这个参数时才会截断。

手动清历史库存，默认只跑 resume 生成，不自动 PDF：

```bash
./write_backlog_batch.sh \
  --max-jobs 20 \
  --publish-portfolio
```

默认 `resume` / `all` / `write_backlog_batch.sh` / `rereview_resume_portfolio.py`
都只处理大厂岗位。中厂和小厂只有显式传 `--company-tier` 时才会进入链路。

例如放开到中厂：

```bash
./run_resume.sh \
  --enable-llm \
  --publish-portfolio \
  --company-tier mid_large \
  --company-tier mid_small
```

只处理指定日期：

```bash
./run_all.sh \
  --enable-llm \
  --publish-portfolio \
  --publish-date 2026-04-08
```

只处理指定日期范围：

```bash
./run_all.sh \
  --enable-llm \
  --publish-portfolio \
  --publish-date-from 2026-04-07 \
  --publish-date-to 2026-04-08
```

查看或重置 backlog state：

```bash
./resume_state.sh show
./resume_state.sh clear
./resume_state.sh remove --job-id 69cefaa354f00230c6d05841
```

启用真实生成，默认走 Codex CLI：

```bash
./run_resume.sh \
  --enable-llm \
  --provider codex \
  --publish-portfolio
```

切到 Claude Code CLI：

```bash
./run_resume.sh \
  --enable-llm \
  --provider claude \
  --publish-portfolio
```

对最近一次中游产物补 PDF：

```bash
./run_pdf.sh
```

对单个 markdown 验证 PDF：

```bash
./run_pdf.sh \
  --resume-md /abs/path/to/resume.md \
  --output-dir /abs/path/to/output
```

打开本地下游岗位处理网页：

```bash
./run_job_app.sh
```

默认会自动打开 `http://127.0.0.1:8765/`，表格优先展示 `data/job_tracker/jobs_catalog.json`
中的全量岗位，并与历史 `resume_portfolio` 产物合并补齐简历状态。
`data/job_tracker/scraped_jobs.json` 只保留“本地 scraper 缓存”语义，不再代表全体岗位。
页面默认每 60 秒自动刷新一次；checkbox 状态持久化到 `state/job_app_status.json`；
筛选器已移除 seed filter。

对 `YOE = Unknown` 的岗位做轻量回填：

```bash
./backfill_job_app_yoe.sh
```

回填结果写到 `state/job_app_yoe_cache.json`，网页会自动读取这个缓存。
如需尝试对部分站点抓取在线职位页再增强判断，可手动运行：

```bash
./backfill_job_app_yoe.sh --fetch-html
```

## 输出约定

- 所有新入口运行记录都写到 `runs/`
- 增量处理状态写到 `state/resume_state.json`
- 只有显式传 `--publish-portfolio` 时，才会把新生成简历发布进现有 portfolio
- PDF 阶段只更新目标目录及其 `manifest.json`；如果目标在现有 portfolio 下，会重建索引
- `audit_backlog.sh` 默认只做历史库存审计
- `write_backlog_batch.sh` 默认不触发 PDF，需要时单独跑 `run_pdf.sh`
- `resume` / `all` / `rereview` 默认只跑大厂；中厂、小厂必须手动加 `--company-tier`

## 当前安全边界

- dry-run 不触发真实 LLM
- `--no-state-update` 不会写增量状态
- 没有任何命令会删除现有 deliverables
- 历史试验资产已移到 `/Users/jingyizhang/Documents/Playground/projects/archive_resume_pipeline_experiments_20260407`
- `scheduled_daily_pipeline.sh` 默认不设运行时长上限；如需限时可手动传 `--max-runtime-minutes`
