#!/usr/bin/env bash

# High-level test runner for the Project Puzzle repo.
#
# This script is intentionally small. It delegates to task-specific test
# runners under the tasks/ directory. As new tasks are added, this script
# can be updated to call their individual runners.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Determine which task to run. If no argument is provided, default to task-001
# to preserve the original behaviour.
TASK_ID="${1:-task-001}"
TASK_DIR="tasks/${TASK_ID}"

if [ -x """${TASK_DIR}/run-tests.sh""" ]; then
  echo "Running ${TASK_ID} tests..."
  (cd "${TASK_DIR}" && ./run-tests.sh)
else
  echo "No runnable test script found for task id '${TASK_ID}'. " \
    "Expected an executable ${TASK_DIR}/run-tests.sh" >&2
  exit 1
fi
