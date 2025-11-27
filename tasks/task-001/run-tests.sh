#!/bin/bash

# Check if task ID is provided
if [ -z "$1" ]; then
  echo "Error: Task ID is required"
  echo "Usage: $0 <task-id>"
  exit 1
fi

TASK_ID=$1
TASK_DIR="tasks/${TASK_ID}"

# Ensure the task directory exists
if [ ! -d "$TASK_DIR" ]; then
  echo "Error: Task directory $TASK_DIR not found"
  exit 1
fi

# Run the tests
echo "Running tests for task ${TASK_ID}..."
python3 "${TASK_DIR}/task_tests.py"
TEST_RESULT=$?

# Generate the diff file
echo "Generating diff file..."
git add .
git diff --staged -- . ":!tasks/" > "${TASK_DIR}/task_diff.txt"

# Show test results
if [ $TEST_RESULT -eq 0 ]; then
  echo "✅ All tests passed!"
  echo "✅ Task diff saved to ${TASK_DIR}/task_diff.txt"
else
  echo "❌ Some tests failed. Check the output above for details."
  echo "⚠️  Task diff still generated but may not be complete."
fi

exit $TEST_RESULT
