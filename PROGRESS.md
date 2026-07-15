# Progress Notes

Working notes for picking up in-flight work across machines. See ROADMAP.md for
the overall plan — this file only tracks what's currently in progress.

## Status as of 2026-07-14

**Project complete — all 12 weeks of `ROADMAP.md` are done.** Live at
https://personal-finance-api-0tcv.onrender.com

Week 11 (CI/CD & Deployment) — DONE.
Week 12 (Portfolio Ready) — DONE: README (with live demo link, CI badge,
tech stack rationale, Architecture + ERD Mermaid diagrams, Getting
Started, expanded "What I Learned"), `erd.mmd`, and `INTERVIEW_NOTES.md`
(narrative Q&A on this project's design decisions, bugs found/fixed, and
reflection questions) are all committed and pushed
(`7959617`, `0fd364b`, `4b0251e`).

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

**All 12 weeks of `ROADMAP.md` are done — this project's build plan is
complete.** The remaining deferred CI/CD gate decision is still open (see
below). Beyond that, the project has moved on to `TIER1_EXPANSION_PLAN.md`
(see next section) — a self-authored follow-on plan to deepen this project
for backend interview prep (transfers, recurring transactions, idempotency,
scheduler, budgets/alerts, testing, observability), added 2026-07-15.

### Tier 1 Expansion — Phase 0 done, plan upgraded to v3 (2026-07-15)

- `docs/current-architecture.md` added (commit `1b532c7`). Phase 0 audit
  confirmed baseline is healthy: 25/25 tests pass locally, latest CI run
  green, layering clean (routers/services/models), secrets via
  `os.getenv()` only, live deploy's `/health` and `/docs` both 200. Known
  technical debt logged: no PR-based CI gate yet, `/` missing `HEAD`,
  shell-form Dockerfile `CMD` PID1 concern, single Alembic migration so far.
- `TIER1_EXPANSION_PLAN.md` was replaced with a v3 revision the user brought
  in (commit `efb4245`), which adds a `transfers` domain, a month-end
  next-run-date rule, `retry_count` on execution runs, and a dedicated
  `budget_alert_events` table (with its own `UNIQUE(budget_id, threshold,
  year, month)`) for alert dedup — the last two directly fix gaps flagged
  during the Phase 0 review.
- **Design decisions locked in (annotated at the top of
  `TIER1_EXPANSION_PLAN.md`, which override the v3 body text below them):**
  - **Category stays a pure label** — v3's proposal to add
    `Category.usage_type` (income/expense/both) plus a
    transaction/category compatibility validation was considered and
    **rejected**. The user independently spotted the same flaw flagged in
    the Phase 0 review: a category like "Stock" can't have one fixed
    direction (buying is an expense, selling/dividend is income). Of the
    three options discussed (fully unbound / optional-bind / strict-bind),
    fully unbound won — `Transaction.transaction_type` alone carries
    direction; `Category` never validates it. All v3 tasks referencing
    `usage_type` or category/transaction compatibility are struck out in
    the repo's plan file.
  - **Transfers adopted** as a Phase 1 warm-up (a dedicated `transfers`
    model/service/API, atomic DB transaction, excluded from income/expense
    reports) — simpler DB-transaction/rollback practice before the harder
    idempotency work in Phase 3.
  - **Scheduler technology (Phase 4) — DECIDED (2026-07-16, ahead of
    schedule): GitHub Actions scheduled workflow calling a protected API
    endpoint.** In-process APScheduler rejected (dies when Render's Free
    Web Service spins down idle — it's the same process). Render Cron Job
    rejected (verified via Render's own docs: minimum $1/mo per cron job,
    breaks the free-tier-only constraint this project has kept throughout).
    Celery+Redis out of scope at this project's scale. GitHub Actions wins:
    free, reuses `.github/workflows/` infra already in place, and — being
    entirely external to Render — its HTTP call is exactly what wakes a
    sleeping Web Service. Caveats to design around when Phase 4 is actually
    built: 5-minute minimum interval, possible delay during high GitHub
    Actions load (documented, notably near the top of each hour), and
    auto-disabled after 60 days of zero repo activity since this repo is
    public. None block daily/weekly/monthly-granularity recurring
    transactions; the delay risk is exactly what Phase 3's idempotent
    execution design needs to already tolerate. Full reasoning in
    `TIER1_EXPANSION_PLAN.md`'s override note.
  - **Currency handling — DECIDED (2026-07-15/16): full multi-currency with
    real conversion.** `users.base_currency` (home/reporting currency) +
    new `exchange_rates` table (`base_currency`, `target_currency`, `rate`,
    `as_of_date`), populated lazily from the free key-less **Frankfurter
    API** (`api.frankfurter.dev`, ECB daily rates) the first time a date's
    rate is needed, then cached. Every `Transaction`/`Transfer` **snapshots**
    the rate/base-currency amount used at creation time — reports must never
    re-price historical transactions with today's rate (a January report
    can't change value because March's rate moved). `report_service.py`
    must sum the snapshotted base-currency amount, not raw
    `Transaction.amount`. `accounts.currency` gets validated against ISO
    4217. Explicitly out of scope: scheduled daily rate-refresh jobs,
    manual rate-override UI, backfilling currency data for
    pre-existing transactions. Full detail annotated in
    `TIER1_EXPANSION_PLAN.md`'s override note.
- **Next: Phase 1a (Currency Foundation), then Phase 1c (Transfers)** —
  build the currency/exchange-rate foundation and update `report_service.py`
  to use snapshotted base-currency amounts first, since cross-currency
  transfers depend on it; then `transfers` model + service + API (now with
  `source_amount`/`destination_amount` instead of a single `amount`, to
  support cross-currency transfers), atomic DB transaction, rollback tests,
  excluded from reports.

### Phase 1a — in progress (2026-07-17)

- **Frankfurter API version corrected to `v2`** (not `v1`) — verified
  empirically that `v1` only covers ~30 ECB currencies and does not include
  TWD at all; `v2` covers 165 currently-active currencies and does include
  TWD. Confirmed request/response shapes for `v2/rates` (param is `quotes`,
  not `v1`'s `symbols`) and `v2/currencies`. `accounts.currency` validation
  will check against Frankfurter's own `v2/currencies` list (cached), not a
  generic ISO 4217 list, since ISO 4217 doesn't guarantee Frankfurter has
  rate data for every code. Full detail in `TIER1_EXPANSION_PLAN.md`'s
  override note.
- **Scheduler technology decided ahead of schedule**: GitHub Actions
  scheduled workflow calling a protected endpoint (see override note in
  `TIER1_EXPANSION_PLAN.md` for the full comparison against in-process
  APScheduler and Render Cron Job, the latter ruled out at a verified
  minimum $1/mo).
- **`users.base_currency` added** (`app/models/user.py`): user chose
  **`server_default="TWD"`** as the default (not `USD` — TWD fits the
  user's own real-world usage better; this project's test data has used
  TWD accounts throughout, and TWD is confirmed supported by Frankfurter
  `v2`). Correctly used `server_default` (database-level, applies to
  existing rows at `ALTER TABLE` time) rather than `default` (Python-side
  only, would not backfill existing users since they aren't re-inserted
  through the ORM) — this distinction was worked through explicitly since
  the `users` table already has real rows.
- **Docker gotcha hit and fixed while working on this**: running
  `docker compose up -d` (no service name) starts *all* services, not just
  `db` — built and started an `app` container the user didn't intend to
  run alongside local `uvicorn --reload`. That `app` container then crashed
  on its own (`Exited (1)`) because `depends_on: - db` only guarantees
  start *order*, not that Postgres inside `db` is actually ready to accept
  connections yet (`FATAL: the database system is starting up`) — this is
  the exact `depends_on` limitation already logged in the Week 10 Docker
  gotchas below, now actually encountered in practice. Fix identified (not
  yet applied to `docker-compose.yml`): add a `healthcheck` (`pg_isready`)
  to the `db` service and change `app`'s `depends_on` to
  `db: condition: service_healthy` so `app` waits for Postgres to be truly
  ready, not just for the container to have started.
- **Done since**: `app/schemas/user.py` (`UserCreate`/`UserResponse` now
  have `base_currency`, default `TWD` — matches the model's
  `server_default`, not `USD`; wired into `auth_service.register()`,
  commit `f79220a`). `ExchangeRate` model + migration added (commit
  `4b8bc80`) — `base_currency`/`target_currency`/`rate`
  (`Numeric(18, 8)`, higher precision than money fields since rates need
  more decimal places)/`as_of_date`/`created_at`, with a
  `UniqueConstraint(base_currency, target_currency, as_of_date)` as the
  cache key. Hit and fixed a real bug along the way: `__table_args__ = (
  UniqueConstraint(...) )` without a trailing comma isn't a tuple in
  Python (it's just the `UniqueConstraint` object itself, parens alone
  don't make a tuple — only a comma does), which SQLAlchemy rejects at
  class-definition time (`ArgumentError: __table_args__ value must be a
  tuple, dict, or None`) — reproduced and confirmed via direct import
  before the fix, and again after.
- **Design refinement (not yet implemented)**: on a cache miss, the
  exchange-rate service should fetch **all** target currencies for that
  `base_currency` + date in one Frankfurter call (omit `quotes`) and bulk
  -insert the whole batch, not just the one target actually needed — the
  marginal cost of a wider fetch is ~zero (Frankfurter returns everything
  for a base in one response regardless), and it means any other
  transaction that needs a *different* target for the same base+date
  later that day is already a cache hit. This gets most of the benefit of
  a proactive daily refresh without needing a scheduled job — user's own
  idea, arrived at through a discussion of doing this at real scale
  (thousands of users). Concurrency note for the same design: two
  requests can race on the same cache-miss and both attempt to insert the
  same batch — handle by catching the `IntegrityError` from the
  `UniqueConstraint`, rolling back, and re-querying the cache (whichever
  request "won" the insert), not `ON CONFLICT DO NOTHING` (Postgres-only
  syntax that wouldn't work against the SQLite test database) — not yet
  implemented, next up when the exchange-rate service itself is written.
- **`as_of_date` clarification (important, already correctly reasoned
  through)**: must always be the transaction's own `transaction_date`,
  never "today's system date" at query time — using "today" would break
  report stability for backdated/backfilled transactions. Confirmed
  Frankfurter `v2` supports querying any specific historical date via
  `date=YYYY-MM-DD` (tested directly), so backfilled transactions are not
  a gap — the historical rate for that exact date is always fetchable on
  first use, regardless of how long ago it was.
- **Still not done**: the exchange-rate service itself (get_rate function
  with caching + Frankfurter v2 call + the batch-fetch-on-miss + race
  handling above), currency validation against Frankfurter's
  `v2/currencies` list, `Transaction` snapshot columns + migration,
  `report_service.py` update to sum snapshotted amounts, tests, and the
  `docker-compose.yml` healthcheck fix (see above) which is still only
  designed, not applied.

**Personal note (not project-scoped)**: the user also keeps a personal
interview-prep Q&A collection at `C:\Projects\INTERVIEW_Q&A.md` (outside
this repo, not git-tracked) — that file, not this one, is where
new general engineering Q&A from conversations gets appended going
forward.

**Deferred — CI/CD gate decision (already decided, just not applied yet)**:
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
