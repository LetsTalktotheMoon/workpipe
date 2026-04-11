#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/managed_run.py" \
  --label "audit_backlog" \
  --display-name "Audit Backlog" \
  --cwd "$SCRIPT_DIR" \
  -- \
  python3 "$SCRIPT_DIR/pipeline.py" resume --force-all --dry-run --no-state-update "$@"
