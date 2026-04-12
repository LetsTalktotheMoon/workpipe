#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${PIPELINE_ENV_FILE:-$SCRIPT_DIR/.pipeline_env.kimi}"
if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi
exec python3 "$SCRIPT_DIR/managed_run.py" \
  --label "daily_full_pipeline_kimi" \
  --display-name "Daily Full Pipeline (Kimi)" \
  --cwd "$SCRIPT_DIR" \
  --preset-id "daily_full_pipeline_kimi" \
  -- \
  python3 "$SCRIPT_DIR/pipeline.py" all --provider kimi "$@"
