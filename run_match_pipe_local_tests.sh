#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 -m pytest -q \
  "$SCRIPT_DIR/tests/test_match_pipe_eval.py" \
  "$SCRIPT_DIR/tests/test_match_pipe_freeze.py" \
  "$SCRIPT_DIR/tests/test_match_pipe_selector.py" \
  "$SCRIPT_DIR/tests/test_match_pipe_units.py"
