#!/bin/sh
set -eu

repo_root=$(cd "$(dirname "$0")/.." && pwd)

frontend_port=${FRONTEND_PORT:-3001}
api_port=${API_PORT:-8001}

cleanup() {
    if [ -n "${frontend_env_backup:-}" ] && [ -f "$frontend_env_backup" ]; then
        mv "$frontend_env_backup" "$repo_root/frontend/.env"
    fi
    if [ -n "${api_pid:-}" ]; then
        kill "$api_pid" 2>/dev/null || true
    fi
    if [ -n "${frontend_pid:-}" ]; then
        kill "$frontend_pid" 2>/dev/null || true
    fi
}

trap cleanup EXIT INT TERM

start_api_server() {
    export API_BASE_URL="http://127.0.0.1:$api_port"
    uv run --directory "$repo_root/api" uvicorn api.main:app --app-dir "$repo_root" --host 127.0.0.1 --port "$api_port" > /tmp/bookmark-manager-api-e2e.log 2>&1 &
    api_pid=$!
}

start_frontend_server() {
    cd "$repo_root/frontend"
    frontend_env_backup=$(mktemp)
    cp .env "$frontend_env_backup"
    cat > .env <<EOF
NUXT_PUBLIC_API_BASE_URL=http://127.0.0.1:$api_port
NUXT_PUBLIC_API_BASE=http://127.0.0.1:$api_port
EOF
    export API_BASE_URL="http://127.0.0.1:$api_port"
    export NUXT_PUBLIC_API_BASE_URL="http://127.0.0.1:$api_port"
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
for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30; do
    if curl -fsS "http://127.0.0.1:$api_port/health" >/dev/null; then
        break
    fi
    sleep 2
done
start_frontend_server

for url in "http://127.0.0.1:$api_port/health" "http://127.0.0.1:$frontend_port"; do
    for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30; do
        if curl -fsS "$url" >/dev/null; then
            break
        fi
        sleep 2
    done
done

PLAYWRIGHT_API_BASE_URL="http://127.0.0.1:$api_port" \
PLAYWRIGHT_FRONTEND_BASE_URL="http://127.0.0.1:$frontend_port" \
bunx playwright test "$@"
