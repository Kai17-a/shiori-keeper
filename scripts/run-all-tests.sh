#!/bin/sh
set -eu

repo_root=$(cd "$(dirname "$0")/.." && pwd)

cleanup() {
    if [ -n "${api_pid:-}" ]; then
        kill "$api_pid" 2>/dev/null || true
    fi
    if [ -n "${frontend_pid:-}" ]; then
        kill "$frontend_pid" 2>/dev/null || true
    fi
}

trap cleanup EXIT INT TERM

cd "$repo_root/api"
uv run ruff check .
uv run pytest -q

cd "$repo_root/frontend"
bun run test

if [ ! -d "$HOME/.cache/ms-playwright" ] || [ -z "$(find "$HOME/.cache/ms-playwright" -mindepth 1 -maxdepth 1 2>/dev/null | head -n 1)" ]; then
    bunx playwright install --with-deps chromium
fi

uv run --directory "$repo_root/api" uvicorn api.main:app --host 127.0.0.1 --port 8000 > /tmp/bookmark-manager-api.log 2>&1 &
api_pid=$!

bun run dev > /tmp/bookmark-manager-frontend.log 2>&1 &
frontend_pid=$!

for url in http://127.0.0.1:8000/health http://127.0.0.1:3000; do
    for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30; do
        if curl -fsS "$url" >/dev/null; then
            break
        fi
        sleep 2
    done
done

bun run e2e
