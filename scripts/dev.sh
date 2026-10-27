#!/usr/bin/env bash
# Owner: Person 4
# Purpose: Start Miko backend (FastAPI) and frontend (Vite) simultaneously for development
# TODO(person4): Add automatic browser opening and process cleanup trap

set -e

echo "Starting Miko in development mode..."

export PROVIDER=${PROVIDER:-mock}

# Check if .env exists
if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs)
fi

echo "Active Provider: $PROVIDER"

# Trap SIGINT to kill background jobs on exit
trap 'kill $(jobs -p)' EXIT

# Start backend
echo "Launching Backend on http://127.0.0.1:8000..."
cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &

# Start frontend
echo "Launching Frontend on http://127.0.0.1:5173..."
cd apps/web && npm run dev &

wait
