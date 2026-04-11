#!/bin/sh
set -e

export NUXT_PUBLIC_API_BASE_URL="${NUXT_PUBLIC_API_BASE_URL:-http://127.0.0.1:8000}"
export API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"
export DATABASE_URL="${DATABASE_URL:-/data/bookmark.db}"

python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

cd /app/frontend
bun run start &
FRONTEND_PID=$!

trap 'kill "$API_PID" "$FRONTEND_PID" 2>/dev/null || true' INT TERM
trap 'kill "$API_PID" "$FRONTEND_PID" 2>/dev/null || true' EXIT
wait -n "$API_PID" "$FRONTEND_PID"
exit $?
