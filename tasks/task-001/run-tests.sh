#!/usr/bin/env bash

# Simple runner for Task 001 tests.
# This script assumes that:
#   - Node.js is installed on your machine.
#   - The backend server is already running on http://localhost:5000.
#   - MongoDB is reachable (either locally or via docker-compose).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

node task_tests.js
