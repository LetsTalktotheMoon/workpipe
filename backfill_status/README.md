# backfill_status

`backfill_status` is the batch status classifier for the local jobs pipeline.
It classifies each known job into:

- `open`
- `closed`
- `unknown` (intentionally conservative)

The system is designed to scale across large pools without browser automation,
while avoiding unsafe guesses on anti-bot or ambiguous pages.

## Canonical Pool Source

The canonical input pool is loaded from the local job app aggregation layer:

- `backfill_status.pool.load_full_job_pool()`
- canonical current-source file: `data/job_tracker/jobs_catalog.json`
- aggregation entrypoint: `runtime.job_webapp.main.JobAppStore.build_jobs_payload()`

This means the backfill operates on the same merged universe used by the web app
(current scraped jobs + portfolio history), not just one scrape snapshot.

Important reporting note:

- current reports distinguish the current canonical pool from the run scope
- historical reports may still reflect an older subset-style口径 (for example the old `1258` pool snapshot) and should not be read as the current canonical full pool
- prefer `canonical_total_jobs`, `canonical_total_jobs_with_apply_url`, `requested_scope_total_jobs`, and `run_scope_total_jobs`
- `pool_total_jobs` remains only as a deprecated compatibility alias

## Persistence Targets

The backfill writes to three places:

- `state/job_status_backfill.json`
  - per-job evidence cache (`status`, detector, confidence, reason, markers, host, timestamps)
- `state/job_app_status.json`
  - webapp-compatible flags (`closed`, plus preserved `applied` / `abandoned`)
- `output/backfill_status/`
  - run reports (`latest_backfill_status.json` or timestamped reports)

## Detector Layers

Detection is layered in `backfill_status/detectors.py`:

1. Request and extraction layer
   - HTTP fetch with retry for transient responses
   - text extraction from visible HTML
   - structured extraction from scripts/JSON-LD and OG/Twitter meta tags

2. Fast decisive signals
   - hard HTTP unavailable codes (for example `404` / `410`) -> `closed`
   - final URL closed hints (`job-not-found`, `.../404`, etc.) -> `closed`

3. Host-aware scoring
   - host family detection (`rules.py`)
   - host markers + generic markers + structured markers
   - title/token overlap as a supporting signal

4. Conservative fallback
   - if evidence is weak or conflicting, keep `unknown`
   - anti-bot/challenge pages are intentionally not forced to `open`/`closed`

## Host-Specific Logic

Rules live in `backfill_status/rules.py` and are applied by family.

- LinkedIn
  - direct `/jobs/view/...` pages can return `429`
  - detector attempts guest endpoint first: `jobs-guest/jobs/api/jobPosting/<id>`
  - if guest payload has live posting content, classify `open`

- Greenhouse (`boards.greenhouse.io`, `grnh.se`)
  - form/posting payload markers -> `open`
  - inactive/archived/removed markers -> `closed`

- Ashby (`jobs.ashbyhq.com`)
  - posting/form definition markers -> `open`
  - explicit null app payload patterns (organization/posting/jobBoard null) -> `closed`

- Amazon Jobs (`www.amazon.jobs`)
  - qualifications/job-details markers -> `open`
  - filled/unavailable/expired markers -> `closed`

- Workday (`*.myworkdayjobs.com`)
  - requisition/posting payload markers -> `open`
  - `postingAvailable:false` and explicit closed markers -> `closed`

- Oracle Candidate Experience (`*.oraclecloud.com`, contacthr frontends)
  - candidate-experience job payload markers -> `open`
  - explicit not-found/expired markers -> `closed`

- Phenom-like career sites
  - includes hosts such as Adobe/Qualcomm/Mastercard career pages
  - strong OG/meta + structured posting content -> `open`
  - explicit filled/removed markers -> `closed`

- Jobvite
  - posting/details markers -> `open`
  - `"the job listing no longer exists"` and related signals -> `closed`

## Unknown and Anti-Bot Policy

`unknown` is a valid and expected output.

The detector keeps `unknown` when:

- response is a challenge wall (Cloudflare/anti-bot/security check)
- page is a generic shell with no reliable job payload
- open/closed signals conflict
- transport or parsing fails without decisive evidence

This is deliberate: forcing a label in these cases increases false status output.

## Monotonic Cache Semantics

Cache writes are monotonic by default (`backfill_status/persistence.py`):

- existing terminal status (`open`/`closed`) is preserved
- a new `unknown` result does **not** overwrite existing terminal status
- `unknown` only replaces terminal status when explicitly enabled:
  - CLI flag: `--allow-unknown-overwrite-terminal`

This prevents coverage regressions from temporary rate limits or anti-bot spikes.

## Run Recipes

### 1) 历史 unknown (recheck historical unknown only)

```bash
python3 - <<'PY' | sh
import json
from pathlib import Path
payload = json.loads(Path("state/job_status_backfill.json").read_text(encoding="utf-8"))
ids = [job_id for job_id, item in payload.items() if str(item.get("status", "")).lower() == "unknown"]
if not ids:
    print("echo 'No unknown jobs in cache.'")
else:
    args = " ".join(f"--job-id {job_id}" for job_id in ids)
    print(f"python3 -m backfill_status.cli --force --concurrency 8 {args}")
PY
```

This runs only the job ids currently marked `unknown`, and refreshes them with `--force` while keeping monotonic cache protection (new `unknown` will not erase existing `open`/`closed`).

### 2) 新增岗位 (incremental for newly seen jobs)

```bash
python3 -m backfill_status.cli --concurrency 12
```

This is the default incremental mode: cached terminal jobs (`open`/`closed`) are skipped, so it mainly processes newly added jobs plus any non-terminal leftovers.

The generated report now makes this explicit:

- `canonical_total_jobs`: current canonical pool size from the aggregated job payload
- `canonical_total_jobs_with_apply_url`: canonical jobs eligible for backfill HTTP checks
- `requested_scope_total_jobs`: jobs matched by the current `--job-id` / `--host` selection before cache skipping
- `run_scope_total_jobs`: jobs actually scheduled for this invocation after cache skipping and `--limit`

### 3) 历史全量 (full historical sweep)

```bash
python3 -m backfill_status.cli --force --concurrency 12 --request-timeout 20
```

This forces a full-pool recheck for all jobs, but still uses monotonic semantics so a transient `unknown` result does not downgrade an already terminal cached status.

## LinkedIn Timeout Path

Runner mode with the default `--request-timeout 20` still preserves LinkedIn host-specific detection:

- LinkedIn jobs still attempt the guest endpoint first: `jobs-guest/jobs/api/jobPosting/<id>`
- only if that path is unavailable or remains `unknown` does the runner fall back to the normal page fetch

This avoids the timeout-enabled runner path accidentally bypassing LinkedIn-specific logic.
