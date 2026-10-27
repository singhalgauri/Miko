#!/usr/bin/env bash
# Owner: Person 4
# Purpose: Helper script to trigger sample data reset via backend API
# TODO(person4): Add command-line arguments to specify dataset variant

set -e

BACKEND_URL=${BACKEND_URL:-http://127.0.0.1:8000}

echo "Resetting Miko sample data via $BACKEND_URL/api/seed/reset..."

curl -s -X POST "$BACKEND_URL/api/seed/reset" \
  -H "Content-Type: application/json" | grep -o '"status":"[^"]*"'

echo "Done."
