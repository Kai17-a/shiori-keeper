#!/bin/sh
set -eu

repo_root=$(cd "$(dirname "$0")/.." && pwd)
workflow="${1:-.github/workflows/pr-tests.yml}"
event="${2:-pull_request}"
shift 2>/dev/null || true

if ! command -v mise >/dev/null 2>&1; then
    echo "mise is required but not installed." >&2
    exit 1
fi

if [ ! -f "$repo_root/$workflow" ]; then
    echo "Workflow not found: $workflow" >&2
    exit 1
fi

cd "$repo_root"

exec mise exec act -- \
    -W "$workflow" \
    -e "$event" \
    "$@"
