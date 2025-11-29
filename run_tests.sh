#!/usr/bin/env bash
set -euo pipefail

TASK_ID="${1-}"
if [ -z "$TASK_ID" ]; then
  TASK_ID="${TASK_ID:-}"
fi
if [ -z "$TASK_ID" ]; then
  echo "Usage: ./run_tests.sh <task-id> or set TASK_ID env var"
  exit 2
fi

# Ensure Node dependencies are installed locally (for non-Docker runs)
NEED_NPM_INSTALL=false
if [ ! -d "node_modules" ] || [ ! -d "server/node_modules" ] || [ ! -d "client/node_modules" ]; then
  NEED_NPM_INSTALL=true
fi
# Also trigger install if server auth deps are missing
if ! node -e "require.resolve('jsonwebtoken',{paths:['server']})" >/dev/null 2>&1; then
  NEED_NPM_INSTALL=true
fi
if ! node -e "require.resolve('bcryptjs',{paths:['server']})" >/dev/null 2>&1; then
  NEED_NPM_INSTALL=true
fi
if [ "$NEED_NPM_INSTALL" = true ]; then
  echo "Installing workspace dependencies..."
  npm install --ignore-scripts --workspaces --include-workspace-root >/dev/null 2>&1
fi

# Ensure pytest is available locally when using non-Docker runs
if [ -f "tasks/${TASK_ID}/task_tests.py" ]; then
  if ! python3 -c "import pytest" >/dev/null 2>&1; then
    echo "Installing local Python test deps (pytest, requests)..."
    if ! python3 -m pip --version >/dev/null 2>&1; then
      python3 -m ensurepip --upgrade >/dev/null 2>&1 || true
    fi
    python3 -m pip install --user -q pytest requests || true
  fi
fi

# Build client once to ensure static is present
npm run build -w client >/dev/null 2>&1 || true

# Determine test framework
JEST_GLOB=("tasks/${TASK_ID}/task_tests.js" "tasks/${TASK_ID}/task_tests.cjs" "tasks/${TASK_ID}/task_tests.mjs" "tasks/${TASK_ID}/task_tests.test.js")
HAS_JEST=false
for f in "${JEST_GLOB[@]}"; do
  if [ -f "$f" ]; then HAS_JEST=true; break; fi
done

PYTEST_FILE="tasks/${TASK_ID}/task_tests.py"

if [ "$HAS_JEST" = false ] && [ ! -f "$PYTEST_FILE" ]; then
  echo "No test file found for task '${TASK_ID}'. Expected tasks/${TASK_ID}/task_tests.(py|js)"
  exit 3
fi

# Start server in background
node server/src/index.js &
SERVER_PID=$!

# Wait for health endpoint (max ~15s)
ATTEMPTS=30
until { command -v wget >/dev/null 2>&1 && wget -qO- http://localhost:3000/api/health >/dev/null 2>&1; } || { command -v curl >/dev/null 2>&1 && curl -fsS http://localhost:3000/api/health >/dev/null 2>&1; }; do
  ATTEMPTS=$((ATTEMPTS-1))
  if [ $ATTEMPTS -le 0 ]; then
    echo "Server did not become healthy in time"
    kill $SERVER_PID || true
    exit 4
  fi
  sleep 0.5
done

set +e
RESULT=0
if [ -f "$PYTEST_FILE" ]; then
  echo "Running pytest suite for $TASK_ID"
  python3 -m pytest -q "$PYTEST_FILE"
  RESULT=$?
elif [ "$HAS_JEST" = true ]; then
  export CI=1
  npx --yes jest --runInBand tasks/${TASK_ID}/task_tests.*
  RESULT=$?
fi
set -e

kill $SERVER_PID >/dev/null 2>&1 || true
wait $SERVER_PID 2>/dev/null || true

exit $RESULT
