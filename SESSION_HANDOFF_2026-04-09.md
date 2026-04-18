# Session Handoff 2026-04-09

## Current Scheduler

- The nightly cron at `23:00 America/Chicago` now runs **scraper only**.
- It calls [`scheduled_daily_pipeline.sh`](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline/scheduled_daily_pipeline.sh), which now runs:
  - `python3 pipeline.py jobs --lookback-hours 48`
- It no longer auto-triggers:
  - `resume` generation
  - `review`
  - `pdf`
  - waiting-window enqueue / retry continuation
- Newly scraped jobs still land in `scraped_jobs.json` as the local scraper cache, but the web app should now read the merged `jobs_catalog.json` first so newly synced jobs and historical jobs share one canonical pool.

## A Plan: Current Production Router / Seed System

### What It Does Today

- Job routing is deterministic, not vector-based.
- Matching features are:
  - `required_coverage`
  - `core_coverage`
  - `preferred_coverage`
  - `role_score`
  - `domain_score`
  - `seniority_score`
  - `title_score`
  - `same_company` bias
- Main code:
  - [`runtime/automation/job_router.py`](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline/runtime/automation/job_router.py)
  - [`runtime/automation/seed_registry.py`](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline/runtime/automation/seed_registry.py)

### Diagnosed Problems

- `retarget` is the main token sink.
  - Writer is constrained by a partial-edit budget and by “preserve original story”.
  - When the source seed is structurally wrong for the target JD, writer cannot create enough new support.
  - Reviewer then keeps issuing authenticity / JD-fit failures, causing low-value rewrite loops.
- `reuse` has a measurement flaw.
  - It picks the best existing artifact under a seed family.
  - It copies the **old** `review` payload instead of forcing a fresh review against the **new** JD.
  - Core code:
    - [`pipeline.py#L389`](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline/pipeline.py#L389)
    - [`pipeline.py#L681`](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline/pipeline.py#L681)

### Important Validation Result

- A spot-check of 3 `reuse + pass` samples was run through the **current reviewer against the current target JD**.
- Results stayed `pass`:
  - Google: `94.4 -> 93.9`
  - AWS: `94.4 -> 96.1`
  - Take-Two: `94.3 -> 93.2`
- File:
  - [`runs/reuse_resample_20260408.json`](/Users/jingyizhang/Documents/Playground/projects/local_job_resume_pipeline/runs/reuse_resample_20260408.json)
- Interpretation:
  - The current `reuse` accounting is still logically wrong.
  - But it is **not** yet proven that all current `reuse` outputs are bad.
  - Immediate bulk rollback was therefore deferred.

## B Plan: JD Cluster Refactor

### User Intent

- Stop treating “seed” as the primary routing abstraction.
- Cluster **job descriptions**, not full resumes.
- Remove `title_score`.
- Keep routing anchored on:
  - technology stack
  - business/domain direction
  - seniority
  - role family
- Company clusters become automatic company-level overlays:
  - if a company has at least 2 valid resumes/jobs, it has a company cluster
- A single resume can belong to multiple clusters:
  - one company cluster
  - one or more non-company JD clusters
- Example:
  - a Google backend resume lives in `Google` cluster and in general `backend` cluster
  - other companies’ backend jobs can compare against that resume too

### Intended Pipeline After Refactor

1. If target company has a valid company cluster, use that company context first.
2. Independently match the job into the best non-company JD cluster.
3. Inside the selected cluster, compare candidate resumes by structured features, not full-text similarity.
4. Pick the best base resume.
5. Give that base resume directly to reviewer.
6. Reviewer decides:
   - direct `reuse`
   - or `PLAN + WRITE` rewrite
7. Writer/reviewer stay free; cluster is retrieval structure, not a narrative constraint.

### Why This Direction Looks Right

- It reduces dependence on brittle static promoted seeds.
- It allows cross-company reuse when stack/domain/seniority align.
- It turns routing into a retrieval problem and leaves writing freedom to reviewer/writer.
- It should reduce bad `retarget` loops, because base selection becomes less company-locked.

### Why It Was Not Migrated Yet

- It is a heavier refactor than tuning thresholds.
- Current seed routing is flawed but not obviously collapsed.
- Some `reuse` samples surprisingly still score well under real re-review.
- Because of that, a shadow A/B is preferred before full migration.

## Recommended Next Step

- Build a **shadow JD-cluster-lite router** without changing production flow.
- For the shadow version:
  - drop `title_score`
  - keep only structured JD factors
  - map current seeds safely into JD clusters
  - allow company cluster + non-company cluster dual membership
- Then run A/B on the same sample set:
  - current router vs cluster-lite router
  - compare:
    - final pass rate
    - average score
    - total tokens
    - elapsed time
    - token per pass
    - rewrite loop count

## Known Special Rules Already Added

- ByteDance and TikTok target roles use a special evidence policy:
  - remove ByteDance/TikTok internship from candidate evidence
  - write only from the two full-time roles plus Georgia Tech CS coursework/projects
- Existing ByteDance artifacts in current scraper pool were deleted and forced back to `无简历`.

## Web App / Manual Ops State

- Nightly scraper-only runs should still show up in monitor as `Daily Job Scraper`.
- Newly scraped jobs should appear in the table with `无简历`.
- Manual generation / rewrite actions and the backlog modes remain separate from the cron change.
