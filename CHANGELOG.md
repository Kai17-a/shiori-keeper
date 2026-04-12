## [unreleased]

### 🚀 Features

- _(frontend)_ Refine layouts and local setup
- _(frontend)_ Complete dashboard screen
- _(chrome-extension)_ Add autofill
- _(api)_ Add health check
- _(frontend)_ Add cancel button
- _(frontend)_ Update bookmark UI
- _(frontend)_ Temporary change
- _(frontend)_ Run e2e with test ports

### 🐛 Bug Fixes

- _(chrome-extension)_ Fix storage access
- _(chrome-extension)_ Adjust popup size
- _(frontend)_ Fix save button control
- _(api)_ Add bookmark and tag conflict responses
- _(frontend)_ Adjust registration message
- _(api)_ Fix pyright issues
- _(api)_ Use environment for API base URL
- _(api)_ Make docker build use virtualenv
- _(api)_ Enforce unique folder and tag names
- _(api)_ Split local and docker startup commands
- _(frontend)_ Remove navbar connection badges
- _(frontend)_ Refine bookmark and edit modal layouts
- _(frontend)_ Stabilize vitest test command
- _(frontend)_ Disable module preload polyfill warning
- _(frontend)_ Disable tailwind sourcemap warning
- _(frontend)_ Disable tailwind sourcemap warnings
- _(frontend)_ Pin bun to build-compatible version
- _(frontend)_ Silence tailwind build warning
- _(frontend)_ Remove invalid nuxt css source map config
- _(frontend)_ Resolve zed diagnostics
- _(frontend)_ Simplify connection status handling
- _(docker)_ Install bash for bun build scripts
- _(docker)_ Avoid copying host node_modules into builds
- _(docker)_ Publish image to ghcr
- _(frontend)_ Simplify build script

### 🚜 Refactor

- _(frontend)_ Finalize app restructure
- _(api)_ Refine bookmark behavior
- _(chrome-extension)_ Rework popup
- _(frontend)_ Remove redundant API mirror
- _(chrome-extension)_ Update popup save flow
- _(api)_ Clean up main module formatting
- _(frontend)_ Remove mutable api settings UI
- _(frontend)_ Extract bookmark list helpers
- _(frontend)_ Move e2e tests to root tests
- _(api)_ Extract shared service dependencies
- _(api)_ Centralize config and bookmark helpers

### 📚 Documentation

- Add docker usage to README
- Sync requirements with pyproject
- Clarify docker runtime layout
- Reorganize project documentation
- Define feature-sized commits
- _(specs)_ Add LLM reading guide and agent instructions
- Add test runner skill and workspace-local hooks
- Split and refresh repository readmes
- Require commits after code changes
- _(development)_ Pin bun build runtime

### 🧪 Testing

- _(frontend)_ Add Vitest logic tests
- Add test docs and playwright e2e

### ⚙️ Miscellaneous Tasks

- Initialize monorepo
- Commit non-extension changes
- Initial commit
- _(chrome-extension)_ Initial commit
- Refactor api and frontend build setup
- _(api)_ Sync api dependencies
- Add data directory to gitignore
- Update skill packaging
- Expand gitignore for local caches
- Refine gitignore entries
