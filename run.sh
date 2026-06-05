#!/usr/bin/env bash
# Run API + worker + frontend in one terminal. Ctrl+C stops everything.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

if [[ ! -f frontend/.env.local ]]; then
  echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
fi

# Backend venv
if [[ ! -x backend/.venv/bin/python ]]; then
  echo "Setting up backend venv..."
  python3 -m venv backend/.venv
  backend/.venv/bin/pip install -q -r backend/requirements-core.txt
fi

if [[ ! -d frontend/node_modules ]]; then
  echo "Installing frontend..."
  (cd frontend && npm install)
fi

PIDS=()
cleanup() {
  echo ""
  echo "Stopping Cricket Shorts AI..."
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
  wait 2>/dev/null || true
  exit 0
}
trap cleanup INT TERM EXIT

echo "Starting API on http://localhost:8000"
(cd backend && exec .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000) &
PIDS+=($!)

sleep 2

echo "Starting worker (batch inbox + job processing)"
(cd backend && exec .venv/bin/python -m app.workers.processor) &
PIDS+=($!)

echo "Starting frontend on http://localhost:3000"
(cd frontend && exec npm run dev) &
PIDS+=($!)

echo ""
echo "  App:     http://localhost:3000"
echo "  API:     http://localhost:8000/docs"
echo "  Inbox:   $ROOT/backend/storage/inbox"
echo ""
echo "Press Ctrl+C to stop all services."
echo ""

wait
