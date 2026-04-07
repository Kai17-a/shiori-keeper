#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_PORT="${API_PORT:-8001}"
FRONTEND_PORT="${FRONTEND_PORT:-3001}"
API_PID=""
FRONTEND_PID=""

kill_port_users() {
  local port="$1"
  local pids
  pids="$(lsof -ti tcp:"${port}" || true)"
  if [[ -n "${pids}" ]]; then
    echo "Stopping existing process on port ${port}..."
    kill ${pids} 2>/dev/null || true
    sleep 1
    pids="$(lsof -ti tcp:"${port}" || true)"
    if [[ -n "${pids}" ]]; then
      kill -9 ${pids} 2>/dev/null || true
    fi
  fi
}

cleanup() {
  if [[ -n "${FRONTEND_PID}" ]] && kill -0 "${FRONTEND_PID}" 2>/dev/null; then
    kill "${FRONTEND_PID}" 2>/dev/null || true
  fi
  if [[ -n "${API_PID}" ]] && kill -0 "${API_PID}" 2>/dev/null; then
    kill "${API_PID}" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

kill_port_users "${API_PORT}"
kill_port_users "${FRONTEND_PORT}"

if [[ ! -d "${ROOT_DIR}/frontend/node_modules" ]]; then
  echo "Installing frontend dependencies..."
  (cd "${ROOT_DIR}/frontend" && bun install)
fi

echo "Starting API on http://127.0.0.1:${API_PORT} ..."
(cd "${ROOT_DIR}" && python -m uvicorn api.app.main:app --reload --host 127.0.0.1 --port "${API_PORT}") &
API_PID=$!

echo "Starting frontend on http://127.0.0.1:${FRONTEND_PORT} ..."
(cd "${ROOT_DIR}/frontend" && NUXT_PUBLIC_API_BASE="http://127.0.0.1:${API_PORT}" bun run dev --port "${FRONTEND_PORT}") &
FRONTEND_PID=$!

wait -n "${API_PID}" "${FRONTEND_PID}"
EXIT_CODE=$?

cleanup
exit "${EXIT_CODE}"
