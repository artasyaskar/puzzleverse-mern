#!/usr/bin/env bash

# High-level test runner for the Project Puzzle repo.
#
# This script delegates to task-specific test runners under the tasks/
# directory in local/dev environments that have docker-compose installed.
# In environments without docker-compose (like the oracle runner), it falls
# back to running the Python tests directly.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Determine which task to run. If no argument is provided, default to task-001
# to preserve the original behaviour.
TASK_ID="${1:-task-001}"
TASK_DIR="tasks/${TASK_ID}"

# If docker-compose is available, keep the original behaviour:
# call the per-task docker-based runner.
if command -v docker-compose >/dev/null 2>&1; then
  if [ -x "${TASK_DIR}/run-tests.sh" ]; then
    echo "Running ${TASK_ID} tests via docker-compose..."
    (cd "${TASK_DIR}" && ./run-tests.sh)
    exit 0
  else
    echo "No runnable test script found for task id '${TASK_ID}'. " \
      "Expected an executable ${TASK_DIR}/run-tests.sh" >&2
    exit 1
  fi
fi

# Fallback for environments without docker-compose (e.g. oracle runner):
# run pytest directly against the task's test file.
echo "docker-compose not available; running ${TASK_ID} tests directly with pytest..."

cd "${TASK_DIR}"

# Ensure pytest and requests are available; ignore error if already installed.
python -m pip install --quiet pytest requests || true

pytest -q task_tests.py