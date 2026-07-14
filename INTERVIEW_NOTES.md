# Interview Notes

Practice answers for questions this project is likely to invite. Written in
first person as talking points — read them, then say them in your own
words; don't recite them verbatim.

## Architecture & Design Decisions

### Walk me through your architecture.

The API is split into four layers with a strict responsibility boundary:
Router, Service, Model, and Schema.

- **Router** only does HTTP-shaped work: parse the request, resolve the
  authenticated user via `Depends(get_current_user)`, call a service,
  return the response. It has zero business logic.
- **Service** holds the business rules — validation like "amount must be
  positive," and ownership checks like "does this account belong to the
  current user." It talks to the database through SQLAlchemy.
- **Model** is purely the database table shape — SQLAlchemy classes with
  columns, nothing else.
- **Schema** is the Pydantic boundary — it defines exactly what a client
  is allowed to send in and what gets sent back out.

A request flows: `Client -> Router -> Service -> Model -> PostgreSQL`, and
errors flow back the other way as typed exceptions
(`NotFoundException`, `ForbiddenException`, etc.) that a global handler in
`main.py` turns into the right HTTP status code. Routers and services never
build an HTTP response by hand.

### Why this layering, specifically?

Two reasons. First, testability — because business logic lives in the
service layer with plain Python arguments (not `Request` objects or
FastAPI `Depends`), it's straightforward to test in isolation. Second,
it's what let me *find* a real bug: because ownership checks are supposed
to live in the service layer, I could audit every service function and
see which ones were missing that check, instead of the logic being
scattered across routers where it's easy to miss.

### Why FastAPI over Flask or Django?

This is a pure API service with no server-rendered pages and no need for
an admin panel, so Django's "batteries included" footprint (ORM, admin,
templating) would mostly go unused. Flask is minimal but gives you nothing
for free — you'd bolt on separate libraries for validation and API docs.
FastAPI's Pydantic-based request/response models double as automatically
generated OpenAPI docs (the `/docs` Swagger UI is generated from the same
type hints used for validation), which fit a project where the schemas
were already the design's center of gravity.

### Why PostgreSQL over MySQL, SQLite, or a NoSQL store like MongoDB?

The data is inherently relational — `users -> accounts -> categories ->
transactions`, all connected by foreign keys, and the reports feature
joins `transactions` to `categories` to build a summary. That rules out a
document store like MongoDB, which fits loosely-structured data, not
this. Between the relational options, SQLite (which the test suite
actually uses, for speed and zero setup) isn't built for concurrent
multi-user production access. PostgreSQL and MySQL are both reasonable;
I went with Postgres because it has stronger support for exact numeric
types (important for money — see below) and it's the more common "default
serious choice" in backend job postings.

### How do you store money, and why does it matter?

`Transaction.amount` is `Numeric(10, 2)`, not a float. Floats can't
represent most decimal fractions exactly in binary, so repeated
arithmetic on floating-point money values accumulates rounding error.
`Numeric`/`Decimal` stores the exact decimal value. On the API side,
amounts are serialized as strings (e.g. `"100.00"`), and when comparing
them in tests I compare `Decimal(a) == Decimal(b)` rather than the raw
strings, because `"100.0"` and `"100.00"` are equal as numbers but not as
strings — a naive string comparison would produce false test failures.

## Security: Authentication & Authorization

### What's the difference between authentication and authorization, and where does your project draw the line?

Authentication answers "who are you" — enforced by
`Depends(get_current_user)`, which validates a JWT and resolves it to a
user; failing that returns `401`. Authorization answers a different
question that only makes sense *after* you already know who someone is:
"are you allowed to touch *this specific* resource"; failing that returns
`403`. They're implemented in different layers on purpose — authentication
is a router-level dependency, authorization is a service-level check
(`if resource.user_id != current_user.id: raise ForbiddenException(...)`),
because "does this belong to you" is a business rule, not an HTTP
concern.

### Tell me about a bug you found and fixed in this project.

While writing tests for the accounts and categories endpoints, I noticed
`get_one`, `update`, and `delete` all had JWT authentication but nothing
checking that the resource being accessed actually belonged to the logged
in user. That meant any authenticated user could read, modify, or delete
*another* user's account or category just by guessing an ID — a real
authorization gap, not a hypothetical one. I fixed it by adding an
explicit ownership check in the service layer for both resources, backed
by a `ForbiddenException` that a global handler already knew how to turn
into a `403`. I verified the fix by scripting an end-to-end test with two
separate users: user A creates a resource, user B is correctly blocked
(`403`) from reading, updating, or deleting it, while A can still do all
three (`200`/`200`/`204`) on their own resource.

I also found the same category of issue on `get_all`: it was reading a
client-supplied `user_id` from the query string with no authentication at
all, so anyone could pass an arbitrary `user_id` and list someone else's
data without even logging in. That one didn't need a per-row ownership
check — the fix was simpler: drop the query parameter and derive the
`user_id` from the JWT instead, since the underlying query already
filters by `user_id`.

### Why does a custom exception class only carry a message, not a status code?

Separation of concerns: `app/exceptions.py` defines business-level
exceptions (`NotFoundException`, `ForbiddenException`, `ConflictException`,
`BadRequestException`) that only know "what kind of problem happened," not
"what HTTP status that becomes." The mapping to actual status codes lives
in one place — the global exception handlers in `main.py`
(`@app.exception_handler(...)`). If a status code were duplicated onto the
exception class itself, there'd be two places that could drift out of
sync; keeping it in one place means there's exactly one thing to check
when debugging "why did this return the wrong status."

## Testing

### How did you approach testing this project?

Pytest, with fixtures in `conftest.py` providing a SQLite-backed test
database, a `TestClient`, and an authenticated-user helper (`auth_headers`)
so most tests can just declare the fixtures they need instead of
re-registering a user every time. 25 tests currently cover authentication,
CRUD for each resource (including the authorization checks above),
validation edge cases, and reports.

### What's a subtlety about pytest fixtures you learned building this?

Fixtures form a dependency graph, not a flat list — if fixture `B`
declares fixture `A` as a parameter, any test requesting `B` automatically
gets `A` resolved too, and pytest caches each fixture's result per test
call, so it's not re-run even if multiple things in the same test ask for
it.

The more interesting lesson was *where an assertion should live*. I built
a `create_account` fixture (a precondition — it exists so a transaction
test has an account to attach a transaction to) and a
`generate_transaction` fixture (the actual thing `test_create_transaction`
exists to verify). I put a defensive `assert` inside `create_account`,
because if that precondition silently failed, the failure should surface
immediately and clearly rather than as a confusing `KeyError` two fixtures
later. But I deliberately left `generate_transaction` without an internal
assert — if I'd put the "did this succeed" check there instead of in the
test, `test_create_transaction` would become an empty shell that just
re-checks what the fixture already checked, and lose its own reason to
exist. The rule I landed on: assert inside a fixture when it's a
precondition whose correctness is verified elsewhere; leave the assertion
in the test when the fixture *is* the subject the test exists to verify.

### Tell me about a testing bug that taught you something about the framework.

FastAPI resolves security dependencies before validating the request
body. I had a test sending both an invalid body *and* no auth header,
expecting a `422` (validation error) — it actually came back `401`,
because the auth check short-circuits before the body is ever parsed.
That's not a bug in the app, it's how FastAPI's dependency resolution
order works, but it meant a couple of my test scenarios needed
`auth_headers` added explicitly to isolate the thing they were actually
trying to test.

## Database / ORM

### Explain your ER diagram / schema.

Four tables: `users`, `accounts`, `categories`, `transactions`. Every
table other than `users` carries its own `user_id` foreign key directly
(not just transitively through `accounts`) — that's deliberate, because
it's exactly what makes the per-row ownership checks in the service layer
possible without extra joins. `transactions.category_id` is the only
nullable foreign key — a transaction doesn't have to be categorized —
which shows up in the ERD as a `0..1` cardinality instead of a mandatory
`1`.

### What's the difference between `Base.metadata` and the actual database, and why did that confuse you at first?

`Base.metadata` is an in-memory schema blueprint built the moment Python
imports the model files — the `class Account(Base): ...` statement itself
registers the table shape into `Base.metadata` via SQLAlchemy's
declarative metaclass. It has nothing to do with whether the *database*
is fresh; it's rebuilt from scratch every time the process starts, purely
because importing the same `.py` files produces the same result every
time. The confusion was thinking "if the process restarts, doesn't
in-memory stuff disappear?" — it does, but that's fine, because it's not
the metadata surviving a restart, it's the same source code being
re-imported and reproducing the same metadata every time.

### What's the difference between an `engine` and a `Session`?

The `engine` just knows *how* to connect to one specific database — it
holds the connection pool and dialect info. A `Session` is the actual
unit-of-work object used to run queries, track changed objects, and
manage a transaction. This project scopes one `Session` per HTTP request
(`get_db()`), which means many different operations (a query, an insert,
an update) can happen inside the same session/transaction over the
lifetime of one request — the session's boundary is "one logical piece of
work," not "one type of database operation."

### Your models don't use SQLAlchemy's `relationship()` — was that a deliberate choice?

Yes. `relationship()` lets you navigate related rows as Python attributes
(e.g. `user.accounts` instead of manually querying), but every service
function in this project queries explicitly instead —
`db.query(Account).filter(Account.user_id == user_id).all()` rather than
object-graph navigation. I kept it that way for a few reasons: every query
that actually hits the database is visible right where it's written, with
no risk of an attribute access silently firing an extra query (the classic
ORM N+1 problem); it avoids an entire extra category of bugs around
SQLAlchemy's lazy-loading strategies and `DetachedInstanceError` when a
relationship is accessed outside its session; and it matches this
project's own rule that models are "DB structure only" — no
navigation/convenience logic mixed into the table definition.

That said, it's a tradeoff, not a rule I'd apply everywhere. I'd reach for
`relationship()` once a specific pain point actually shows up — the same
filter-by-foreign-key query duplicated across many call sites, code that
needs to walk several relationship hops at once, or needing declarative
cascade-delete behavior (e.g. deleting a user should also delete their
accounts/categories/transactions, which right now would just hit a
foreign-key constraint error since nothing cascades). I'd add it to that
specific pair of tables when the need is concrete, not retrofit it across
the whole schema preemptively.

## DevOps: CI/CD & Deployment

### Walk me through your CI/CD pipeline.

GitHub Actions (`ci.yml`) runs pytest on every push and PR to `main`. The
app is containerized with Docker (multi-stage-free single Dockerfile,
plus a docker-compose for local Postgres), and Render is connected
directly to the GitHub repo, auto-deploying on every push via a webhook
GitHub calls when it detects a new commit. Render provisions the Postgres
instance and the web service on its free tier.

### Tell me about a deployment bug you hit.

The container's `CMD` originally only started `uvicorn`; a freshly
provisioned database would have no tables. I changed it to
`alembic upgrade head && uvicorn ...` so migrations run automatically on
startup — except my first attempt wrote it as exec-form JSON,
`CMD ["alembic", "upgrade", "head", "&&", "uvicorn", ...]`. Exec-form
`CMD` never invokes a shell, so `&&` isn't interpreted as a logical
operator — it gets passed to `alembic` as a literal, invalid CLI
argument, `alembic` errors out, and `uvicorn` never runs at all. Switching
to shell form (`CMD alembic upgrade head && uvicorn ...`, no brackets)
fixed it. I verified it locally against a real Postgres container before
trusting it in production, and confirmed it again by reading the actual
Render deploy logs after shipping.

### What's a known gap in your CI/CD setup right now, and how would you fix it?

CI and CD aren't actually chained. Because this repo pushes straight to
`main` with no pull-request step, GitHub Actions' test job and Render's
deploy webhook both react independently to the same `push` event — a
broken test suite doesn't currently block a broken deploy. The fix I've
scoped but not yet applied: move to a PR-based workflow with branch
protection requiring the CI job to pass before a merge to `main` is
allowed, so by the time Render ever sees a new commit on `main`, it's
already passed CI. I deliberately deferred this until after finishing the
portfolio-readiness work, since it only affects how *future* changes to
the repo get shipped, not anything currently running.

### What would you do differently if you started this project over?

Two things. First, I'd set up the PR + branch-protection workflow from
day one instead of retrofitting it at the end — it's a small amount of
GitHub configuration that would have made CI meaningfully load-bearing
the whole time, not just informative. Second, I'd write the ownership
(authorization) checks alongside the very first CRUD endpoint instead of
adding JWT authentication first and coming back to authorization later —
having done it the second way once, I now recognize "authenticated but
not authorized" as a distinct checklist item to verify immediately for
every new resource, rather than something that surfaces later while
writing tests.

## Reflection

### What are you most proud of in this project?

Finding and fixing the authorization gap without being told to look for
it — it came out of methodically reviewing what each service function
actually checked versus what its router required, not from a bug report.
That process (audit what each layer is actually responsible for) is
something I'd apply to any codebase, not just this one.

### What was the hardest concept to really understand, not just use?

The authentication-vs-authorization distinction sounds obvious once you
say it, but it took hitting the actual bug to internalize it — before
that, "the endpoint requires login" and "the endpoint is secure" felt
like the same statement. They aren't, and the gap between them is exactly
where this vulnerability lived.
