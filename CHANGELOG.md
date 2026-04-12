## [unreleased]

### 🚀 Features

- *(frontend)* Refine layouts and local setup
- *(frontend)* Complete dashboard screen
- *(chrome-extension)* Add autofill
- *(api)* Add health check
- *(frontend)* Add cancel button
- *(frontend)* Update bookmark UI
- *(frontend)* Temporary change
- *(frontend)* Run e2e with test ports
- *(frontend)* Add bookmark delete confirmation
- *(api)* Add descriptions to folders and tags
- *(frontend)* Support folder and tag descriptions
- *(ci)* Add tag release workflow
- *(ci)* Add on push
- Add act
- *(api)* Add bookmark favorite flag
- *(api)* Add bookmark favorite endpoint
- *(frontend)* Add favorites page
- *(frontend)* Move bookmark actions
- *(frontend)* Add favorites sidebar link
- *(frontend)* Make bookmark actions responsive
- *(api)* Add dashboard metrics endpoint
- *(frontend)* Update bookmark card layout
- *(frontend)* Use dashboard metrics api
- *(frontend)* Update dashboard metrics layout
- *(api)* Add rss feed crud
- *(frontend)* Add rss management screen
- *(frontend)* Add rss dashboard stats and e2e coverage
- *(api)* Validate rss feed urls on create
- *(frontend)* Add refresh buttons to content pages
- *(frontend)* Add theme tabs in settings
- *(frontend)* Highlight selected theme tab
- *(frontend)* Restyle rss feed cards
- *(api)* Move webhook registration to settings api
- *(frontend)* Add rss execution and webhook settings
- *(api)* Set webhook username
- *(frontend)* Change rss execute button

### 🐛 Bug Fixes

- *(chrome-extension)* Fix storage access
- *(chrome-extension)* Adjust popup size
- *(frontend)* Fix save button control
- *(api)* Add bookmark and tag conflict responses
- *(frontend)* Adjust registration message
- *(api)* Fix pyright issues
- *(api)* Use environment for API base URL
- *(api)* Make docker build use virtualenv
- *(api)* Enforce unique folder and tag names
- *(api)* Split local and docker startup commands
- *(frontend)* Remove navbar connection badges
- *(frontend)* Refine bookmark and edit modal layouts
- *(frontend)* Stabilize vitest test command
- *(frontend)* Disable module preload polyfill warning
- *(frontend)* Disable tailwind sourcemap warning
- *(frontend)* Disable tailwind sourcemap warnings
- *(frontend)* Pin bun to build-compatible version
- *(frontend)* Silence tailwind build warning
- *(frontend)* Remove invalid nuxt css source map config
- *(frontend)* Resolve zed diagnostics
- *(frontend)* Simplify connection status handling
- *(docker)* Install bash for bun build scripts
- *(docker)* Avoid copying host node_modules into builds
- *(docker)* Publish image to ghcr
- *(frontend)* Simplify build script
- *(frontend)* Import process explicitly in playwright files
- Show entity descriptions in detail views
- Show bookmark relations by detail view
- Simplify tag and folder lists
- Replace bookmark ids with actions
- Stop bookmark action clicks
- Enable bookmark actions on tag details
- *(docker)* Resolve api host from runtime request origin
- *(ci)* Pin bun version for frozen lockfile
- *(ci)* Run frontend e2e via shared script
- *(ci)* Run frontend e2e via shared script
- *(frontend)* Restore bun-compatible vitest version
- *(ci)* Skip commit message checks on pull requests
- *(frontend)* Restore bun-compatible vitest version
- Stabilize act frontend-unit defaults
- Prepare nuxt before frontend unit tests
- Relax frontend dependency install in ci
- Remove frontend env file requirement from e2e
- Skip commit message check for dependabot
- Remove duplicate docker publish workflow
- Grant ghcr permissions at workflow level
- Create release after image publish
- Publish multi arch release images
- *(frontend)* Accept api base url alias
- *(docker)* Make exposed ports configurable
- *(docker)* Make api port configurable
- *(docker)* Override compose api base from api port
- *(frontend)* Remove cookie consent banner
- *(api)* Resolve bookmark favorite route
- *(frontend)* Restore dashboard sidebar data
- *(frontend)* Show rss stats on dashboard
- *(frontend)* Constrain rss modal layout
- *(frontend)* Simplify theme toggle styling
- *(frontend-e2e)* Use local rss feed server
- *(frontend-e2e)* Stabilize rss feed test

### 🚜 Refactor

- *(frontend)* Finalize app restructure
- *(api)* Refine bookmark behavior
- *(chrome-extension)* Rework popup
- *(frontend)* Remove redundant API mirror
- *(chrome-extension)* Update popup save flow
- *(api)* Clean up main module formatting
- *(frontend)* Remove mutable api settings UI
- *(frontend)* Extract bookmark list helpers
- *(frontend)* Move e2e tests to root tests
- *(api)* Extract shared service dependencies
- *(api)* Centralize config and bookmark helpers
- *(frontend)* Rename component folders
- *(frontend)* Improve toast feedback and test stability
- *(frontend)* Remove list descriptions
- *(api)* Remove settings endpoint

### 📚 Documentation

- Add docker usage to README
- Sync requirements with pyproject
- Clarify docker runtime layout
- Reorganize project documentation
- Define feature-sized commits
- *(specs)* Add LLM reading guide and agent instructions
- Add test runner skill and workspace-local hooks
- Split and refresh repository readmes
- Require commits after code changes
- *(development)* Pin bun build runtime
- *(changelog)* Record recent changes
- Clarify tag and folder descriptions
- Mention github docker image publishing
- Rename docker publishing reference to github packages
- *(dev)* Add local GitHub Actions runner
- *(dev)* Run github actions with act
- *(readme)* Add act workflow instructions
- Add compose api env example
- Add git flow branch rule
- Separate user and development guides
- Replace absolute paths in markdown links
- *(frontend)* Note app color customization
- *(specs)* Update webhook settings design

### 🧪 Testing

- *(frontend)* Add Vitest logic tests
- Add test docs and playwright e2e

### ⚙️ Miscellaneous Tasks

- Initialize monorepo
- Commit non-extension changes
- Initial commit
- *(chrome-extension)* Initial commit
- Refactor api and frontend build setup
- *(api)* Sync api dependencies
- Add data directory to gitignore
- Update skill packaging
- Expand gitignore for local caches
- Refine gitignore entries
- Rename docker publish workflow
- *(ci)* Add dependabot configuration
- *(ci)* Publish docker image only on tag push
- *(mise)* Pin git-cliff version
- *(scripts)* Remove github actions wrapper
- *(docker)* Update compose example ports
- Stop tracking actrc
- Update local ignore rules and api lockfile
- Add zed settings
- Commit workspace changes
