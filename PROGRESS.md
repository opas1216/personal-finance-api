# Progress Notes

Working notes for picking up in-flight work across machines. See ROADMAP.md for
the overall plan — this file only tracks what's currently in progress.

## Status as of 2026-07-13 (evening)

Week 11 (CI/CD & Deployment) — **DONE**. Live at
https://personal-finance-api-0tcv.onrender.com

Week 12 (Portfolio Ready) — **in progress**: README + ERD + Architecture
diagram done, Interview Notes still open (see "Next up").

### Week 12 done so far

- `README.md` rewritten from a stub into a portfolio-ready doc: live demo
  link, CI badge, Features list, Tech Stack table with rationale for each
  choice (FastAPI vs Flask/Django, Postgres vs MySQL/SQLite/Mongo, etc.),
  Getting Started (both fully-containerized and hybrid
  Docker-db-only/local-app workflows), API docs pointer, Project
  Structure, Project Documents index.
- **Architecture diagram**: Mermaid `flowchart` embedded in `README.md`
  (Client -> Router -> Service -> Model -> Postgres, plus the exception ->
  global handler -> HTTP status path). Replaces the old plain-text ASCII
  version.
- **ERD**: Mermaid `erDiagram` in `README.md`, sourced from a standalone
  `erd.mmd` file (also committed, tracked in git as the raw source). User
  wrote this one themselves after a long back-and-forth learning Mermaid's
  crow's-foot cardinality syntax (`||`, `|o`/`o|`, `}o`/`o{`, `}|`/`|{` —
  learned that the left-side and right-side forms of the same cardinality
  are mirror images and NOT interchangeable, confirmed against Mermaid's
  own docs; also learned the "outermost char = max, innermost char = min"
  rule that explains why). Caught and fixed two real bugs in their own
  draft before it was committed: `ACCOUNT` vs `ACCOUNTS` entity-name
  mismatch (would have rendered as two disconnected entities), and
  `created_at` typed as `string` instead of `datetime` (mismatched the
  actual `Column(DateTime(timezone=True), ...)` in `app/models/user.py`).
- **"What I Learned" section**: substantially expanded beyond the original
  3 bullets — now covers Authentication vs Authorization (with the real
  ownership-bug story), Testing & Pytest Fixtures (dependency graph
  resolution, where assertions belong in a fixture vs a test, `assert`
  message semantics, `Response` not being subscriptable, Decimal
  comparison), SQLAlchemy/ORM internals (`Base.metadata` vs database
  freshness, `engine` vs `Session`), API/HTTP design (how FastAPI infers
  param source, auto-generated `/docs`), and CI/CD & Deployment (Docker
  CMD exec vs shell form, module-level `create_engine`, what a webhook is,
  why CI and CD aren't auto-chained without a PR gate). This mostly also
  covers the ROADMAP's "Interview Notes" task — see below.
- Also refactored `tests/test_transactions.py` while working through
  fixture concepts for the README: extracted `create_account` /
  `generate_transaction` fixtures (with assert-placement following the
  precondition-vs-subject-under-test distinction learned this session),
  strengthened `test_get_transactions` to actually verify the created
  transaction appears in the response instead of just checking response
  shape. Committed as `7959617` along with the README/ERD work.
- Deployed a small custom HTML/SVG artifact (not part of the repo) as a
  one-off visual ERD reference plus a guide to real ERD tools (Mermaid Live
  Editor, dbdiagram.io, pgAdmin's ERD tool, draw.io) — recommended Mermaid
  Live Editor (mermaid.live) as the companion preview tool since there's no
  way to render Mermaid inside this dev environment itself
  (`npx @mermaid-js/mermaid-cli` timed out trying to fetch a headless
  browser).

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
- **Deployed to Render**: PostgreSQL (Free) + Web Service (Free, Docker
  runtime, auto-detected `Dockerfile`) in the same region. Env vars set on
  the Web Service: `DATABASE_URL` (Render Internal Database URL for the
  Postgres instance) and `SECRET_KEY` (freshly generated via
  `python -c "import secrets; print(secrets.token_hex(32))"`, not reused
  from any local `.env`).
- `Dockerfile` `CMD` fixed to run `alembic upgrade head && uvicorn ...` on
  container start (commit `242f606`) — without this, a freshly provisioned
  database would have no tables. First attempt used exec-form
  `CMD ["alembic", ..., "&&", "uvicorn", ...]`, which does not invoke a shell
  — `&&` was passed to `alembic` as a literal (invalid) argument and
  `uvicorn` never ran. Fixed by switching to shell form
  (`CMD alembic upgrade head && uvicorn ...`, no brackets). Verified locally
  with a real Postgres container before deploying, and confirmed again via
  the live Render deploy logs (migration ran, then uvicorn started).
- Verified against the live URL from outside: `/health` → 200, `/` → 200,
  `/docs` → 200, `/openapi.json` served, and a full
  register → login → create-account (JWT-protected) flow succeeded against
  the real production database.

### Next up

Week 12 (Portfolio Ready): README, ERD, and Architecture Diagram are done
(see "Week 12 done so far" above). Only **Interview Notes** is still open —
though the README's "What I Learned" section already covers most of the
substance (concrete bugs found/fixed, concepts learned, with the "why").
Next session: decide whether Interview Notes should be a separate document
(e.g. `INTERVIEW_NOTES.md`) or whether "What I Learned" in the README is
sufficient on its own — if a separate doc, it'd likely go deeper into
question-and-answer format (anticipating "walk me through a design
decision" style interview questions) rather than the README's narrative
style.

**Deferred until after Week 12 — CI/CD gate decision (already made, just not applied yet)**:
Right now Render auto-deploys on every push to `main` regardless of whether
the `test` job in `ci.yml` passed — the two are currently independent,
because this project pushes straight to `main` with no PR step, so CI and
CD both just react to the same `push` event in parallel instead of CD
waiting on CI.

Decided approach: switch this repo to a PR-based workflow going forward
(feature branch → PR → require the `ci.yml` `test` job to pass via GitHub
branch protection → merge → merge is what lands on `main` → Render deploys
only what already passed CI). This is a config change only (GitHub branch
protection rules + habit of using PRs), not an app-code change — deliberately
postponed until Week 12 is done since the core project is otherwise
finished and this only matters for *future* changes to the repo.

### Deployment gotchas learned this session (for future reference)

- Render Web Service creation flow prompts for a credit card if a
  non-Free instance type is selected (even accidentally/by default) —
  re-selecting the Free plan avoids it. Not a general "Render always
  requires a card" thing.
- Render health check hit `HEAD /` and got a `405 Method Not Allowed`,
  because the app `/` route is only registered for `GET`, not `HEAD`.
  This did **not** fail the deploy — Render still marked it "Live". Worth
  double-checking if this ever needs to be tightened (e.g. explicitly
  registering `HEAD` on `/` or pointing the Render Health Check Path
  setting at the existing `/health` route instead of the default `/`).
- Shell-form `CMD` (used for the `&&` migration-then-serve chain) makes
  `/bin/sh` PID 1 instead of `uvicorn`; `SIGTERM` on redeploy/scale-down
  is not guaranteed to propagate cleanly to the child process. Not fixed —
  revisit if ungraceful-shutdown symptoms show up in Render logs later
  (candidate fix: `exec` the final command, or go back to exec-form CMD
  wrapped in `sh -c`).

### CI/CD gotchas learned in Week 11 CI phase (carried forward)

- `git pull` (local fetch+merge) and a GitHub "Pull Request" (a review/merge
  *request* between branches on the platform) are unrelated despite the
  shared word — opening a PR does not touch the base branch; only clicking
  **Merge** does.
- A module-level statement (not inside `def`/`class`) executes immediately
  the moment the module is imported — this is why `create_engine(...)` at
  the top of `app/database.py` runs during pytest collection phase
  (import chain: `conftest.py` → `app.main` → `app.database`), before any
  test function body runs.
- SQLAlchemy `create_engine()` only parses the URL string into an object;
  it does not open a network connection until something actually queries
  through it. A syntactically-valid-but-fake Postgres URL is fine as long as
  nothing ever uses that engine (confirmed true here — tests fully bypass it
  via `dependency_overrides`).
- `actions/checkout@vN` / `actions/setup-python@vN` version tags are
  independent of each other (no cross-compatibility matrix to track) — check
  each action own GitHub repo for its current recommended major version.
- `winget install` can hang non-interactively if it needs to prompt for the
  `msstore` source terms — add `--source winget --accept-source-agreements
  --accept-package-agreements` to force the official source and skip the
  prompt.

### Docker gotchas learned in Week 10 (carried forward)

- `docker build` context and `COPY` source paths are relative to the folder
  you run `docker build <path>` from (or `build:` in compose) — not relative
  to the Dockerfile own location.
- Splitting `COPY requirements.txt .` + `RUN pip install` from the later
  `COPY . .` matters because of layer-cache cascading: once any layer cache
  misses, every layer after it is automatically invalidated too.
- Inside a docker-compose network, containers reach each other by **service
  name** (e.g. `db`), not `localhost`.
- `EXPOSE` in the Dockerfile is documentation/metadata only — actual
  host-to-container port mapping is decided at run time via `-p`/`ports:`.
- `depends_on` only controls container **start order**, not readiness.
- Deploying an image to another machine goes through a registry
  (`docker push`/`docker pull`), conceptually the same push/pull model as git.

### Logging gotchas learned in Week 9 (carried forward)

- Registering `@app.exception_handler(Exception)` attaches to Starlette
  **outermost** `ServerErrorMiddleware` (wraps around user middleware) —
  unlike custom exception subclasses which are handled by the inner
  `ExceptionMiddleware`. Do not log exceptions in middleware — let the
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

This machine `.env` was missing `SECRET_KEY` (present in `.env.example`
but not `.env`), which made every JWT-issuing test fail at the
`auth_headers` fixture with `TypeError: Expected a string value` in
`jwt.encode()`. Added a locally-generated `SECRET_KEY` to `.env` (gitignored,
not pushed). If tests fail the same way on another machine, check `.env`
there too.
