#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/managed_run.py" \
  --label "daily_full_pipeline" \
  --display-name "Daily Full Pipeline" \
  --cwd "$SCRIPT_DIR" \
  --preset-id "daily_full_pipeline" \
  -- \
  python3 "$SCRIPT_DIR/pipeline.py" all "$@"
