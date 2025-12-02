#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <task-id>|list" >&2
  echo "Examples:" >&2
  echo "  $0 task-001" >&2
  echo "  $0 1" >&2
  echo "  $0 list" >&2
}

# Ensure we're in the repo root (script directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ ${1-} == "" ]]; then
  usage
  exit 1
fi

CMD="$1"; shift || true

if [[ "$CMD" == "list" ]]; then
  echo "Available tasks:"
  find tasks -maxdepth 1 -type d -name 'task-*' | sort | sed 's/^/ - /'
  exit 0
fi

# Normalize IDs: allow numeric like `1` => task-001
if [[ "$CMD" =~ ^[0-9]+$ ]]; then
  NUM=$(printf "%03d" "$CMD")
  TASK_ID="task-${NUM}"
else
  TASK_ID="$CMD"
fi

TASK_DIR="tasks/${TASK_ID}"
# Remap task-<n> to task-<nnn> if needed
if [[ ! -d "$TASK_DIR" && "$TASK_ID" =~ ^task-([0-9]+)$ ]]; then
  NUM=$(printf "%03d" "${BASH_REMATCH[1]}")
  ALT_ID="task-${NUM}"
  if [[ -d "tasks/${ALT_ID}" ]]; then
    TASK_ID="$ALT_ID"
    TASK_DIR="tasks/${TASK_ID}"
  fi
fi
if [[ ! -d "$TASK_DIR" ]]; then
  echo "Error: Task directory '$TASK_DIR' not found." >&2
  echo "Run '$0 list' to see available tasks." >&2
  exit 1
fi

TASK_RUNNER="$TASK_DIR/run-tests.sh"
if [[ -x "$TASK_RUNNER" ]]; then
  echo "Running task runner: $TASK_RUNNER $*"
  exec "$TASK_RUNNER" "$@"
fi

if [[ -f "$TASK_RUNNER" ]]; then
  echo "Running task runner via bash: $TASK_RUNNER $*"
  exec bash "$TASK_RUNNER" "$@"
fi

# Fallback: try docker compose inside the task directory if a compose file exists
if [[ -f "$TASK_DIR/docker-compose.yaml" || -f "$TASK_DIR/docker-compose.yml" ]]; then
  echo "No run-tests.sh found. Attempting docker compose test run in $TASK_DIR ..."
  cd "$TASK_DIR"
  if command -v docker-compose >/dev/null 2>&1; then
    docker-compose down -v || true
    docker-compose up --build --abort-on-container-exit
    EXIT_CODE=$?
    docker-compose down -v || true
    exit $EXIT_CODE
  else
    docker compose down -v || true
    docker compose up --build --abort-on-container-exit
    EXIT_CODE=$?
    docker compose down -v || true
    exit $EXIT_CODE
  fi
fi

# Final fallback: run pytest directly if a Python test file exists
if compgen -G "$TASK_DIR/*.py" > /dev/null; then
  echo "Running pytest in $TASK_DIR ..."
  cd "$TASK_DIR"
  if command -v pytest >/dev/null 2>&1; then
    exec pytest -q
  else
    echo "Error: pytest not found. Please install it or provide run-tests.sh in the task directory." >&2
    exit 1
  fi
fi

echo "Error: No runnable entrypoint found for '$TASK_ID'. Expected one of:"
echo " - $TASK_DIR/run-tests.sh (preferred)"
echo " - $TASK_DIR/docker-compose.yaml (fallback)"
echo " - Python tests (*.py) runnable via pytest (fallback)"
exit 1
