#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${PIPELINE_ENV_FILE:-$SCRIPT_DIR/.pipeline_env.kimi}"

if [ -f "$ENV_FILE" ]; then
  set -a
  source "$ENV_FILE"
  set +a
fi

exec python3 "$SCRIPT_DIR/managed_run.py" \
  --label "write_backlog_batch_kimi" \
  --display-name "Write Backlog Batch Kimi" \
  --cwd "$SCRIPT_DIR" \
  --preset-id "resume_only" \
  -- \
  python3 "$SCRIPT_DIR/pipeline.py" resume --force-all --enable-llm --provider kimi "$@"
