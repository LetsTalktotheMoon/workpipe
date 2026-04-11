#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/managed_run.py" \
  --label "jobs_only" \
  --display-name "Jobs Only" \
  --cwd "$SCRIPT_DIR" \
  --preset-id "scrape_only" \
  -- \
  python3 "$SCRIPT_DIR/pipeline.py" jobs "$@"
