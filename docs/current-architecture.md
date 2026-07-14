# Current Architecture (Phase 0 Audit — Tier 1 Expansion)

Snapshot taken 2026-07-15, right after all 12 weeks of `ROADMAP.md` were
completed and the app was deployed live. This is the baseline the
`TIER1_EXPANSION_PLAN.md` phases build on top of.

## Request flow

```
Client
  -> Router (app/routers/*.py)      — parses request, calls service, returns response
  -> Service (app/services/*.py)    — business logic, validation, ownership checks, DB ops
  -> Model (app/models/*.py)        — SQLAlchemy ORM, structure only
  -> PostgreSQL (prod) / SQLite (tests, via dependency_overrides in tests/conftest.py)
```

Exceptions: custom exceptions (`app/exceptions.py`) raised in services are caught by
global handlers registered in `app/main.py`, which log and translate them to HTTP
status codes. An outer catch-all `@app.exception_handler(Exception)` logs
unexpected crashes at ERROR with traceback and returns a generic 500.

## Current API endpoints (19 total)

- `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
- `POST|GET /accounts/`, `GET|PUT|DELETE /accounts/{id}`
- `POST|GET /categories/`, `GET|PUT|DELETE /categories/{id}`
- `POST|GET /transactions/`, `GET|PUT|DELETE /transactions/{id}` (filter by
  account_id/category_id/transaction_type, paginated via skip/limit)
- `GET /reports/monthly`, `GET /reports/categories`
- `GET /health`, `GET /health/db`

## Layering check

- Routers only parse/validate/call-service/return — confirmed no direct DB
  session queries in `app/routers/*.py`.
- Business logic (ownership checks, validation) lives in `app/services/*.py`.
- Models (`app/models/*.py`) only declare table structure, no business methods.

## Schema / migrations

- 4 tables (`users`, `accounts`, `categories`, `transactions`), all created in a
  single Alembic migration (`e75c8414e614_create_initial_tables.py`) — no
  incremental schema changes have happened yet, so this is the only revision.
- All schema changes so far have gone through Alembic (no manual `Base.metadata.create_all`
  outside of tests).

## Secrets

- `DATABASE_URL` and `SECRET_KEY` are read via `os.getenv()` in `app/database.py`
  and `app/services/auth_service.py` — no hardcoded secrets in app code.
- Locally via `.env` (gitignored). In CI, fake values set in `ci.yml` job `env:`.
  In production (Render), set as real environment variables on the Web Service.

## Environments

- **Local**: `.venv`, Postgres via `docker compose up -d` (the `db` service only),
  app run directly with uvicorn `--reload`.
- **Tests**: SQLite (`tests/conftest.py`), fully isolated from the Postgres
  `engine` built in `app/database.py` (that engine is built but never queried
  during tests — see `PROGRESS.md` CI/CD gotchas for why the fake CI `DATABASE_URL`
  is safe).
- **CI**: GitHub Actions (`.github/workflows/ci.yml`), `push`/`pull_request` to
  `main`, runs the full pytest suite with fake env vars. Latest run: success.
- **Production**: Render — Postgres (Free) + Web Service (Free, Docker runtime).
  `Dockerfile` `CMD` runs `alembic upgrade head && uvicorn ...` on every
  container start. Live at https://personal-finance-api-0tcv.onrender.com —
  `/health` and `/docs` both verified 200 as of this audit.

## Baseline test result (as of this audit)

```
25 passed, 0 failed
```

## Known technical debt / open items (carried from PROGRESS.md)

1. **No PR-based CI gate yet.** Render currently auto-deploys on every push to
   `main` independently of whether `ci.yml`'s `test` job passed — CI and CD
   both just react to the same `push` event in parallel. Decided fix (not yet
   applied): branch protection requiring the `test` job to pass before merge.
2. **`/` only registers `GET`, not `HEAD`** — Render's health check hits
   `HEAD /` and gets 405. Doesn't fail the deploy today, but is inconsistent;
   candidate fix is pointing Render's Health Check Path at `/health` instead.
3. **Shell-form Dockerfile `CMD`** (`alembic upgrade head && uvicorn ...`) makes
   `/bin/sh` PID 1 instead of uvicorn — `SIGTERM` on redeploy/scale-down isn't
   guaranteed to propagate cleanly. Not yet fixed; revisit if ungraceful-shutdown
   symptoms show up in Render logs.
4. **Single Alembic migration** — fine today (schema hasn't changed since
   initial creation), but the first real test of "safe migrations under load"
   will come with Tier 1 Phase 1's new `recurring_transactions` table.

## Stop Point 0 — status

- [x] Runs locally
- [x] Test suite passes (25/25)
- [x] Deployed version works (`/health`, `/docs` both 200 live)
- [x] Request flow understood (router -> service -> model -> DB)
- [x] Validation/business logic/DB access boundaries are clear (see Layering
  check above)

Ready to proceed to Phase 1 (recurring transactions domain model).
