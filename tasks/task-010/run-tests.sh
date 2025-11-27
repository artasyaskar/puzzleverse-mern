#!/usr/bin/env bash

# Task 010 test runner.
#
# This script is invoked from the repository root via ./run_tests.sh and is
# responsible for bringing up the task-specific docker-compose stack and
# running the Python/pytest-based tests defined in task_tests.py.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"
cd "$SCRIPT_DIR"

# Ensure any previous stack is torn down before starting.
docker-compose down -v >/dev/null 2>&1 || true

# Build and run the test service. We use --abort-on-container-exit so that the
# compose stack stops once tests finish, and --exit-code-from tests so that the
# overall exit code reflects the pytest result.
docker-compose up --build --abort-on-container-exit --exit-code-from tests tests

# Clean up containers and networks after the run.
docker-compose down -v
