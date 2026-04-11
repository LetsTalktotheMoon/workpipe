#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROVIDER="${PIPELINE_PROVIDER:-codex}"
exec python3 "$SCRIPT_DIR/managed_run.py" \
  --label "write_backlog_batch" \
  --display-name "Write Backlog Batch" \
  --cwd "$SCRIPT_DIR" \
  --preset-id "resume_only" \
  -- \
  python3 "$SCRIPT_DIR/pipeline.py" resume --force-all --enable-llm --provider "$PROVIDER" "$@"
