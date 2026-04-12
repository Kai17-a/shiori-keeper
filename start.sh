#!/bin/sh
set -e

export API_PORT="${API_PORT:-8000}"
if [ -z "${API_BASE_URL:-}" ] || [ "$API_BASE_URL" = "http://127.0.0.1:8000" ]; then
  export API_BASE_URL="http://127.0.0.1:${API_PORT}"
fi
export NUXT_PUBLIC_API_BASE_URL="${NUXT_PUBLIC_API_BASE_URL:-$API_BASE_URL}"
export NUXT_PUBLIC_API_PORT="${NUXT_PUBLIC_API_PORT:-$API_PORT}"
export DATABASE_URL="${DATABASE_URL:-/data/bookmark.db}"

fastapi run api/main.py --host 0.0.0.0 --port "$API_PORT" &
API_PID=$!

nginx -g 'daemon off;' &
FRONTEND_PID=$!

trap 'kill "$API_PID" "$FRONTEND_PID" 2>/dev/null || true' INT TERM
trap 'kill "$API_PID" "$FRONTEND_PID" 2>/dev/null || true' EXIT

while kill -0 "$API_PID" 2>/dev/null && kill -0 "$FRONTEND_PID" 2>/dev/null; do
  sleep 1
done

wait "$API_PID" 2>/dev/null || true
wait "$FRONTEND_PID" 2>/dev/null || true
exit 1
