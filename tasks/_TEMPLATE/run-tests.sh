#!/usr/bin/env bash
set -euo pipefail

TASK_ID="${1-}"
if [ -z "$TASK_ID" ]; then
  echo "Usage: ./tasks/_TEMPLATE/run-tests.sh <task-id>"
  exit 2
fi

exec ./run_tests.sh "$TASK_ID"
