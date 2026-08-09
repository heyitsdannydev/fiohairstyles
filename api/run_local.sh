#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PORT=8000

PID=$(lsof -ti:"$PORT" || true)
if [ -n "$PID" ]; then
  echo "Killing process(es) on port $PORT: $PID"
  kill $PID
fi

uv run uvicorn app.main:app --reload --port 8000 --env-file .env
