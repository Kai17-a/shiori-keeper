#!/bin/sh
set -eu

repo_root=$(cd "$(dirname "$0")/.." && pwd)

frontend_port=${FRONTEND_PORT:-3001}
api_port=${API_PORT:-8001}

cleanup() {
    if [ -n "${api_pid:-}" ]; then
        kill "$api_pid" 2>/dev/null || true
    fi
    if [ -n "${frontend_pid:-}" ]; then
        kill "$frontend_pid" 2>/dev/null || true
    fi
}

trap cleanup EXIT INT TERM

wait_for_url() {
    url=$1
    attempts=${2:-30}

    for i in $(seq 1 "$attempts"); do
        if curl -fsS "$url" >/dev/null; then
            return 0
        fi
        sleep 2
    done

    echo "Timed out waiting for $url" >&2
    return 1
}

start_api_server() {
    export API_BASE_URL="http://127.0.0.1:$api_port"
    uv run --directory "$repo_root/api" uvicorn api.main:app --app-dir "$repo_root" --host 127.0.0.1 --port "$api_port" > /tmp/bookmark-manager-api-e2e.log 2>&1 &
    api_pid=$!
}

start_frontend_server() {
    cd "$repo_root/frontend"
    export API_BASE_URL="http://127.0.0.1:$api_port"
    export NUXT_PUBLIC_API_BASE_URL="$API_BASE_URL"
    bun run build

    export HOST=0.0.0.0
    export PORT="$frontend_port"
    bun .output/server/index.mjs > /tmp/bookmark-manager-frontend-e2e.log 2>&1 &
    frontend_pid=$!
}

if [ ! -d "$HOME/.cache/ms-playwright" ] || [ -z "$(find "$HOME/.cache/ms-playwright" -mindepth 1 -maxdepth 1 2>/dev/null | head -n 1)" ]; then
    cd "$repo_root/frontend"
    bunx playwright install --with-deps chromium
fi

start_api_server
wait_for_url "http://127.0.0.1:$api_port/health"
start_frontend_server

wait_for_url "http://127.0.0.1:$api_port/health"
wait_for_url "http://127.0.0.1:$frontend_port"

PLAYWRIGHT_API_BASE_URL="http://127.0.0.1:$api_port" \
PLAYWRIGHT_FRONTEND_BASE_URL="http://127.0.0.1:$frontend_port" \
bunx playwright test "$@"
