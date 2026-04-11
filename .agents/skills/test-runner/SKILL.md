---
name: test-runner
description: Use when running or verifying repository tests and push/PR checks for this project, including API lint/tests, frontend unit tests, and E2E workflows.
---

# Test Runner

Use this skill when the task is about running, wiring, or verifying tests in this repository.

## Default Order

Run checks in this order unless the user asks otherwise:

1. API lint: `ruff check`
2. API tests: `pytest`
3. Frontend unit tests: `bun run test`
4. E2E tests: `bun run e2e`

## Preferred Entry Points

- Local push-prep: `./scripts/run-all-tests.sh`
- Git hook: `.githooks/pre-push`
- CI gate: `.github/workflows/pr-tests.yml`

Prefer these entry points over retyping commands.

## When To Use What

- Use `./scripts/run-all-tests.sh` for a full local verification pass.
- Use `uv run --directory api ruff check .` for API lint-only checks.
- Use `uv run --directory api pytest -q` for API-only test runs.
- Use `bun run test` for frontend unit tests.
- Use `bun run e2e` for browser-flown end-to-end verification.

## Environment Expectations

- API commands run from `api/`.
- Frontend commands run from `frontend/`.
- E2E requires both API and frontend to be reachable on `127.0.0.1:8000` and `127.0.0.1:3000`.
- If Playwright browsers are missing, install them before E2E.

## Guardrails

- Do not skip API lint when the task is to verify code quality.
- Do not treat frontend unit tests as a substitute for E2E.
- When a task affects local push behavior, keep the hook and the helper script aligned.
- If a test run fails, prefer fixing the underlying issue rather than narrowing the checks.

