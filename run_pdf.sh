#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/managed_run.py" \
  --label "pdf_latest" \
  --display-name "PDF Latest" \
  --cwd "$SCRIPT_DIR" \
  --preset-id "pdf_latest" \
  -- \
  python3 "$SCRIPT_DIR/pipeline.py" pdf "$@"
