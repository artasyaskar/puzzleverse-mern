#!/usr/bin/env bash

# High-level test runner for the Project Puzzle repo.
#
# This script is intentionally small. It delegates to task-specific test
# runners under the tasks/ directory. As new tasks are added, this script
# can be updated to call their individual runners.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# For now, we only have Task 001 wired up. If its test script is present,
# we invoke it directly.
if [ -x "tasks/task-001/run-tests.sh" ]; then
  echo "Running Task 001 tests..."
  (cd tasks/task-001 && ./run-tests.sh)
else
  echo "No runnable task test scripts found yet. Add tasks/*/run-tests.sh to extend this." >&2
fi
