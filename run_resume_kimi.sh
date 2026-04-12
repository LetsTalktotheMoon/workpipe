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
  --label "resume_only_kimi" \
  --display-name "Resume Only (Kimi)" \
  --cwd "$SCRIPT_DIR" \
  --preset-id "resume_only_kimi" \
  -- \
  python3 "$SCRIPT_DIR/pipeline.py" resume --provider kimi "$@"
