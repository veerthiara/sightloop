# Local Infrastructure

This directory contains local-only infrastructure used during development.

The default Compose file is intentionally minimal. Add services only when they support an active phase of work.

Current intended uses:

- local Postgres when storage work begins
- local supporting services for backend development
- isolated local dependencies that should not be installed directly on the host
