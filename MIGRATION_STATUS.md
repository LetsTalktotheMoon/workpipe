# Migration Status

## Live Project

稳定可运行的本地主链只保留在：

- `/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline`

主入口：

- `run_jobs.sh`
- `run_resume.sh`
- `run_pdf.sh`
- `run_all.sh`
- `scheduled_run.sh`

运行时来源：

- 上游抓取运行时代码复制到 `runtime/job_tracker/`
- 中游筛选/路由/生成运行时代码复制到 `runtime/`
- 下游 PDF 运行时代码保留在 `runtime/resume_atomizer/`

保留的真实资产：

- `data/deliverables/resume_portfolio` 是已迁入新项目的真实 deliverables 副本
- `data/job_tracker/scraped_jobs.json` 是本地抓取缓存
- `data/seed_sources/` 是已本地化的 promoted seed 来源

## Archived Legacy Assets

历史试验资产已移到：

- `/Users/jingyizhang/Documents/Playground/projects/archive_resume_pipeline_experiments_20260407`

其中包含：

- 旧 `auto-cv/resume_pipeline` 的历史 `output/`
- 旧样例 `jd_input/`、`resumes/`
- 旧试验入口 `auto_trigger.py`、`batch_runner.py`、`sheet_pipeline.py`
- 旧 `docs/`、`tests/`、`tmp/`
- 新项目里一并复制过来的 `runtime/resume_atomizer/output`、`docs`、`staging`
- 已从 live 工作区挪走的旧 `job-tracker`、旧 `resume_pipeline`、旧 `resume_atomizer` 备份
## Remaining External Files

仍在新项目目录之外、但只承担系统调度职责的文件：

- `/Users/jingyizhang/Library/LaunchAgents/com.autopipeline.runjobs.plist`

当前调度入口已经直接指向新项目。

已在 2026-04-07 重新注册本地 `launchd` 任务 `com.autopipeline.runjobs`，当前计划时间是每天 `02:10 / 08:10 / 14:10 / 20:10`（America/Chicago）。
当前定时任务只运行 `scraper` 分支，不自动触发 resume pipeline 或 PDF。
