# Progress Notes

Working notes for picking up in-flight work across machines. See ROADMAP.md for
the overall plan — this file only tracks what's currently in progress.

## Status as of 2026-07-12

Week 10 (Docker) — **COMPLETE**.

### Done

- `Dockerfile` (project root): `python:3.13-slim`, `WORKDIR /app`,
  `COPY requirements.txt .` + `RUN pip install` split from `COPY . .` for
  layer-cache reuse, `EXPOSE 8000`, `CMD` runs uvicorn on `0.0.0.0:8000`.
- `.dockerignore`: excludes `.venv/`, `.git/`, `.env`(+`.env.*`, keeps
  `.env.example`), `Logs/`, `*.log`, `.pytest_cache/`, `.coverage`, `test.db`,
  `tests/` from the build context.
- `docker-compose.yml`: added an `app` service alongside the existing `db`
  service — `build: .`, `env_file: .env`, and an `environment:` override for
  `DATABASE_URL` that swaps `localhost` for the `db` service hostname (so the
  two containers can reach each other over the compose network — `.env`'s
  own `DATABASE_URL` still uses `localhost` for local non-Docker dev).
- Verified end-to-end with `docker compose up --build`: both `GET /health`
  and `GET /health/db` return 200 from inside the container, confirming the
  app container can reach the db container via the `db` hostname.
- Committed as `066e401`: "feat: Week 10 - Dockerfile and Docker Compose for
  the app", pushed to `origin/main`.

### Docker gotchas learned this session (for future reference)

- `docker build` context and `COPY` source paths are relative to the folder
  you run `docker build <path>` from (or `build:` in compose) — not relative
  to the `Dockerfile`'s own location, though in practice they're usually the
  same folder.
- Splitting `COPY requirements.txt .` + `RUN pip install` from the later
  `COPY . .` matters because of layer-cache cascading: once any layer's
  cache misses, every layer after it is automatically invalidated too (their
  cache key incorporates the previous layer's result). Copying only
  `requirements.txt` first means editing app code alone doesn't bust the
  `pip install` layer's cache.
- Inside a docker-compose network, containers reach each other by **service
  name** (e.g. `db`), not `localhost` — `localhost` inside a container refers
  to that container itself. This is why `DATABASE_URL` needs an
  `environment:` override in the `app` service (`.env`'s own value, with
  `localhost`, is only correct for running the app directly on the host).
- `EXPOSE` in the Dockerfile is documentation/metadata (also used by
  `docker run -P`) — it does not itself publish a port. The actual
  host↔container port mapping is decided at run time via `-p`/`ports:`, and
  can differ per environment without touching the Dockerfile.
- `depends_on` only controls container **start order**, not "wait until the
  dependency is actually ready to accept connections" — a possible source of
  transient connection failures right after `docker compose up` if the app
  queries the DB immediately at startup (not currently an issue here since
  nothing queries the DB eagerly at import time).
- Rebuilding an image with the same `-t` tag doesn't require deleting the
  old one first — the tag just moves to the new image; the old one becomes
  a dangling (`<none>`) image, cleanable later with `docker image prune`.
- Deploying an image to another machine goes through a registry
  (`docker push`/`docker pull`, e.g. Docker Hub) — conceptually the same
  push/pull model as git — not manual file copying. `docker save`/`load`
  to a `.tar` exists for offline transfer but isn't the common path.

### Logging gotchas learned in Week 9 (carried forward)

- Registering `@app.exception_handler(Exception)` attaches to Starlette's
  **outermost** `ServerErrorMiddleware` (wraps around user middleware) —
  unlike custom exception subclasses which are handled by the inner
  `ExceptionMiddleware`. A middleware `try/except Exception: log; raise`
  around `call_next()` would double-log unhandled crashes together with the
  catch-all handler — don't log exceptions in middleware, let the catch-all
  handler be the sole logger of unexpected crashes.
- Root-logger setup means third-party libs (httpx, asyncio) also propagate
  their own log records into the same file/console.

### Testing patterns/gotchas learned in Week 8 (carried forward)

- Query params (`?year=&month=`) vs JSON body vs path params are three
  distinct mechanisms — `client.get(url, params={...})` is the idiomatic way
  to send query params in tests, same role as `json=` for POST bodies.
- Money fields are `Decimal`, serialized to JSON as **strings**. Compare with
  `Decimal(response.json()["field"]) == Decimal("500.00")` on *both* sides —
  never mix `Decimal` against a raw string or float.
- Empty/zero results from report endpoints are a valid `200`, not `404`.
- `report_service.get_category_summary` inner-joins Transaction→Category, so
  transactions without a `category_id` are excluded from that report.

### Environment gotcha (fixed locally, check on other machines)

This machine's `.env` was missing `SECRET_KEY` (present in `.env.example`
but not `.env`), which made every JWT-issuing test fail at the
`auth_headers` fixture with `TypeError: Expected a string value` in
`jwt.encode()`. Added a locally-generated `SECRET_KEY` to `.env` (gitignored,
not pushed). If tests fail the same way on another machine, check `.env`
there too.

### Next up

Week 11 - CI/CD & Deployment (GitHub Actions, Deploy Application) per
ROADMAP.md.
