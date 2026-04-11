#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/managed_run.py" \
  --label "resume_only" \
  --display-name "Resume Only" \
  --cwd "$SCRIPT_DIR" \
  --preset-id "resume_only" \
  -- \
  python3 "$SCRIPT_DIR/pipeline.py" resume "$@"
