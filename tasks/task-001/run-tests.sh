#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Choose docker compose command
if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE="docker-compose"
else
  COMPOSE="docker compose"
fi

# Clean previous run
$COMPOSE down -v || true

echo "[task-001] Building and starting tester (with dependencies)..."
set +e
$COMPOSE up --build tester
EXIT_CODE=$?
set -e

# Collect logs
TESTER_LOGS="$($COMPOSE logs tester 2>/dev/null || true)"
APP_LOGS_TAIL="$($COMPOSE logs --tail=40 app 2>/dev/null || true)"

echo "\n===== TEST SUMMARY (pytest) =====\n"
if echo "$TESTER_LOGS" | grep -qiE "collected|passed|failed|ERROR|=+"; then
  echo "$TESTER_LOGS" | sed -n '/pytest/q;p' >/dev/null 2>&1 || true
  # Print only pytest-relevant lines
  echo "$TESTER_LOGS" | grep -E "collected|=+|passed|failed|errors|skipped|no tests ran" || echo "$TESTER_LOGS"
else
  echo "No pytest summary found."
fi

# If no tests ran or app likely crashed, show a short hint with app tail
if echo "$TESTER_LOGS" | grep -qi "no tests ran" || [ $EXIT_CODE -ne 0 ]; then
  echo "\n[hint] The app may have failed to start. Last 40 lines from app logs:" 
  echo "$APP_LOGS_TAIL"
fi

# Teardown
$COMPOSE down -v || true

exit $EXIT_CODE
