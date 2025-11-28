#!/usr/bin/env bash

# High-level test runner for the Project Puzzle repo.
#
# This script delegates to task-specific test runners under the tasks/
# directory. It simply forwards the provided task-id to the per-task script.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Require a task ID
if [ ${#} -lt 1 ]; then
  echo "Error: Task ID is required"
  echo "Usage: ./run_tests.sh <task-id>"
  exit 1
fi

TASK_ID="$1"
TASK_DIR="tasks/${TASK_ID}"

if [ ! -x "${TASK_DIR}/run-tests.sh" ]; then
  echo "No runnable test script found for task id '${TASK_ID}'. " \
    "Expected an executable ${TASK_DIR}/run-tests.sh" >&2
  exit 1
fi

echo "Running ${TASK_ID} tests..."
"${TASK_DIR}/run-tests.sh" "${TASK_ID}"