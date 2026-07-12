# Progress Notes

Working notes for picking up in-flight work across machines. See ROADMAP.md for
the overall plan — this file only tracks what's currently in progress.

## Status as of 2026-07-13

Week 11 (CI/CD & Deployment) — **IN PROGRESS**: CI done, deployment not started.

### Done

- `.github/workflows/ci.yml`: runs on `push`/`pull_request` to `main`. Job
  `test` on `ubuntu-latest`: `actions/checkout@v4` → `actions/setup-python@v5`
  (3.13) → `pip install -r requirements.txt` → `pytest`.
- `env:` at job level sets fake `DATABASE_URL` (a syntactically valid but
  unreachable `postgresql://` URL) and a throwaway `SECRET_KEY` — needed
  because `.env` is gitignored and never exists in the CI checkout, and
  `app/database.py` calls `create_engine(DATABASE_URL)` at **import time**
  (top-level code, not inside a function), so a `None` value crashes pytest's
  collection phase before any test runs. The fake `DATABASE_URL` never
  actually gets connected to — tests override `get_db` with a SQLite session
  in `tests/conftest.py`, so the real `engine` object sits unused.
- Verified passing on GitHub (commit `e2b82b0`, run `29203548700`,
  conclusion `success`) via the public Actions API.
- Committed as `e2b82b0`: "feat: Week 11 - GitHub Actions CI (pytest on
  push/PR to main)", pushed to `origin/main`.
- Installed `gh` CLI locally (`winget install --id GitHub.cli`) for querying
  Actions/PRs from the terminal — not yet run `gh auth login` (interactive,
  needs to be done by hand, not automatable in a background session).

### Next up

Deploy Application (Week 11, second half) — platform not yet chosen.
Candidates discussed: Railway/Render (easiest, connect-repo-and-go),
Fly.io (CLI-driven, still simple), AWS/GCP/Azure (closer to real industry
setup, much more config). Decide platform, then wire up CD (likely a second
job in the same workflow, or a separate `deploy.yml`, gated on the `test`
job passing).

### CI/CD gotchas learned this session (for future reference)

- `git pull` (local fetch+merge) and a GitHub "Pull Request" (a review/merge
  *request* between branches on the platform) are unrelated despite the
  shared word — opening a PR does not touch the base branch; only clicking
  **Merge** does.
- A module-level statement (not inside `def`/`class`) executes immediately
  the moment the module is imported — this is why `create_engine(...)` at
  the top of `app/database.py` runs during pytest's *collection* phase
  (import chain: `conftest.py` → `app.main` → `app.database`), before any
  test function body runs.
- SQLAlchemy's `create_engine()` only parses the URL string into an object;
  it doesn't open a network connection until something actually queries
  through it. A syntactically-valid-but-fake Postgres URL is fine as long as
  nothing ever uses that engine (confirmed true here — tests fully bypass it
  via `dependency_overrides`).
- `actions/checkout@vN` / `actions/setup-python@vN` version tags are
  independent of each other (no cross-compatibility matrix to track) — check
  each action's own GitHub repo for its current recommended major version.
- `winget install` can hang non-interactively if it needs to prompt for the
  `msstore` source's terms — add `--source winget --accept-source-agreements
  --accept-package-agreements` to force the official source and skip the
  prompt.

### Docker gotchas learned in Week 10 (carried forward)

- `docker build` context and `COPY` source paths are relative to the folder
  you run `docker build <path>` from (or `build:` in compose) — not relative
  to the `Dockerfile`'s own location.
- Splitting `COPY requirements.txt .` + `RUN pip install` from the later
  `COPY . .` matters because of layer-cache cascading: once any layer's
  cache misses, every layer after it is automatically invalidated too.
- Inside a docker-compose network, containers reach each other by **service
  name** (e.g. `db`), not `localhost`.
- `EXPOSE` in the Dockerfile is documentation/metadata only — actual
  host↔container port mapping is decided at run time via `-p`/`ports:`.
- `depends_on` only controls container **start order**, not readiness.
- Deploying an image to another machine goes through a registry
  (`docker push`/`docker pull`), conceptually the same push/pull model as git.

### Logging gotchas learned in Week 9 (carried forward)

- Registering `@app.exception_handler(Exception)` attaches to Starlette's
  **outermost** `ServerErrorMiddleware` (wraps around user middleware) —
  unlike custom exception subclasses which are handled by the inner
  `ExceptionMiddleware`. Don't log exceptions in middleware — let the
  catch-all handler be the sole logger of unexpected crashes.
- Root-logger setup means third-party libs (httpx, asyncio) also propagate
  their own log records into the same file/console.

### Testing patterns/gotchas learned in Week 8 (carried forward)

- Query params (`?year=&month=`) vs JSON body vs path params are three
  distinct mechanisms — `client.get(url, params={...})` is the idiomatic way
  to send query params in tests, same role as `json=` for POST bodies.
- Money fields are `Decimal`, serialized to JSON as **strings**. Compare with
  `Decimal(response.json()["field"]) == Decimal("500.00")` on *both* sides.
- Empty/zero results from report endpoints are a valid `200`, not `404`.

### Environment gotcha (fixed locally, check on other machines)

This machine's `.env` was missing `SECRET_KEY` (present in `.env.example`
but not `.env`), which made every JWT-issuing test fail at the
`auth_headers` fixture with `TypeError: Expected a string value` in
`jwt.encode()`. Added a locally-generated `SECRET_KEY` to `.env` (gitignored,
not pushed). If tests fail the same way on another machine, check `.env`
there too.
