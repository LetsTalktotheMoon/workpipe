#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${PIPELINE_ENV_FILE:-$HOME/.pipeline_env}"
LOG_FILE="${PIPELINE_LOG_FILE:-$SCRIPT_DIR/scheduled_daily_pipeline.log}"

if [ -f "$ENV_FILE" ]; then
  while IFS='=' read -r key val; do
    [[ "$key" =~ ^[[:space:]]*# ]] && continue
    [[ -z "$key" ]] && continue
    key="${key#export }"
    key="${key#export}"
    key="${key// /}"
    if [[ -n "$val" && -z "${!key:-}" ]]; then
      export "$key=$val"
    fi
  done < "$ENV_FILE"
fi

LOOKBACK_HOURS="${PIPELINE_LOOKBACK_HOURS:-48}"

CMD=(
  python3 "$SCRIPT_DIR/pipeline.py" jobs
  --lookback-hours "$LOOKBACK_HOURS"
)

{
  echo "========================================"
  echo "▶ start $(date '+%Y-%m-%d %H:%M:%S')"
  printf 'command:'
  printf ' %q' "${CMD[@]}"
  printf '\n'
  python3 "$SCRIPT_DIR/managed_run.py" \
    --label "daily_job_scraper" \
    --display-name "Daily Job Scraper" \
    --cwd "$SCRIPT_DIR" \
    --preset-id "daily_job_scraper" \
    -- \
    "${CMD[@]}"
  echo "◀ end $(date '+%Y-%m-%d %H:%M:%S')"
  echo
} | tee -a "$LOG_FILE"
