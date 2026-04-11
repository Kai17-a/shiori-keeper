# Frontend E2E Test Observations

| Flow | What it covers | Main checks |
|---|---|---|
| Bookmark lifecycle | Integrated bookmark flow | Create, search, edit, delete |
| Folder lifecycle | Integrated folder flow | Create, rename, detail view, delete |
| Tag lifecycle | Integrated tag flow | Create, rename, detail view, delete |
| API integration | Frontend + API together | Requests reach live API and reflect in UI |
| Routing | Browser navigation | Page transitions stay functional |
| Delete behavior | Cleanup after actions | Items disappear and backend returns 404 |
| Search/filter | Query-driven UI | Search box updates the displayed list |
| Resilience | DOM structure changes | Use stable roles and visible text |
| Test runtime | External server setup | Requires API/frontend processes and explicit base URLs |

## Test Types

| Type | Purpose |
|---|---|
| E2E | Validate real browser behavior against live services |
| Smoke | Quick high-value flow checks |
| Regression | Protect against UI/API integration breakage |

## Notes

- Use dedicated test database files and explicit frontend/API base URLs.
- Keep browser selectors stable and user-facing.
- Separate run commands from result-viewing commands when possible.
