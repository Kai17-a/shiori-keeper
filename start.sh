#!/bin/sh
set -e

export API_PORT="${API_PORT:-8000}"
export DATABASE_URL="${DATABASE_URL:-/data/data.db}"

mkdir -p "$(dirname "$DATABASE_URL")"
./dbmate -u "sqlite:$DATABASE_URL" up

fastapi run api/main.py --port "$API_PORT" &
API_PID=$!

nginx -g 'daemon off;' &
FRONTEND_PID=$!

echo "0 * * * * shiori-keeper-batch" >> scheduler
supercronic ./scheduler

trap 'kill "$API_PID" "$FRONTEND_PID" 2>/dev/null || true' INT TERM
trap 'kill "$API_PID" "$FRONTEND_PID" 2>/dev/null || true' EXIT

while kill -0 "$API_PID" 2>/dev/null && kill -0 "$FRONTEND_PID" 2>/dev/null; do
  sleep 1
done

wait "$API_PID" 2>/dev/null || true
wait "$FRONTEND_PID" 2>/dev/null || true
exit 1
