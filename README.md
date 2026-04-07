# Bookmark Manager Monorepo

This repository is organized as a monorepo.

## Layout

- `api/` - FastAPI backend source and tests
- `frontend/` - Nuxt 4 single-page app
- `chrome-extension/` - Chrome extension quick-add popup
- `specs/` - implementation notes and task tracking

## API

The backend lives under `api/`.

The frontend lives under `frontend/` as a Nuxt 4 SPA.

Run the API from the repository root with:

```bash
api-dev
```

Run the frontend from `frontend/` with:

```bash
bun install
bun run dev
```

Or start both services from the repository root with:

```bash
./run-local.sh
```

Run the API tests with:

```bash
python -m pytest -q
```

Pytest is configured to collect tests from `api/tests`.

## Local URLs

- Frontend: `http://127.0.0.1:3001`
- API: `http://127.0.0.1:8001`

## Chrome Extension

Load `chrome-extension/` as an unpacked extension in Chrome.
The popup pre-fills the current tab's title and URL, and posts the bookmark directly to the DB via the API.
Default API Base URL is `http://localhost:8001`.
