#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${OUTPUT_DIR:-$SCRIPT_DIR/output/analysis}"

python3 -m match_pipe.downstream_validation_runner \
  --output-dir "$OUTPUT_DIR" \
  --llm-transport kimi \
  --write-model kimi-for-coding \
  --review-model kimi-for-coding

python3 -m match_pipe.planner_validation_runner \
  --output-dir "$OUTPUT_DIR" \
  --llm-transport kimi \
  --write-model kimi-for-coding \
  --review-model kimi-for-coding \
  --planner-model kimi-for-coding
