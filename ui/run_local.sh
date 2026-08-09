#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PORT=3000

PID=$(lsof -ti:"$PORT" || true)
if [ -n "$PID" ]; then
  echo "Killing process(es) on port $PORT: $PID"
  kill $PID
fi

npm run dev
