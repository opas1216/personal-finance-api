# Progress Notes

Working notes for picking up in-flight work across machines. See ROADMAP.md for
the overall plan — this file only tracks what's currently in progress.

## Status as of 2026-07-11

Week 9 (Logging) — **COMPLETE**. Full suite still 25 passed, 0 failed.

### Done

- `app/logging_config.py`: `setup_logging()` configures the **root logger**
  (level DEBUG) with two handlers — `StreamHandler` (console, level INFO) and
  `FileHandler` writing to `Logs/app_<YYYY-MM-DD>.log` (level DEBUG), both
  using the same formatter (`asctime - name - levelname - message`). Log path
  is built from `Path(__file__).resolve().parent.parent` so it's independent
  of the current working directory. `Logs/` is gitignored.
- `app/main.py`:
  - `setup_logging()` is called before `app = FastAPI()`.
  - `@app.middleware("http") log_requests`: logs every request's
    `method/path/status_code` at INFO after `call_next(request)` completes.
  - Each of the 4 existing exception handlers (`NotFoundException`,
    `ForbiddenException`, `ConflictException`, `BadRequestException`) now
    logs at WARNING before returning its JSONResponse — these are expected
    business errors, not system failures.
  - New catch-all `@app.exception_handler(Exception)`: logs at ERROR via
    `logger.exception(...)` (captures full traceback) and returns a generic
    `{"detail": "Internal server error"}` 500 — never leaks internal error
    details to the client.
- Committed as `b00c624`: "feat: Week 9 - application/error logging +
  exception handling", pushed to `origin/main`.

### Logging gotchas learned this session (for future reference)

- Registering `@app.exception_handler(Exception)` is special-cased by
  Starlette: it gets attached to the **outermost** `ServerErrorMiddleware`,
  which wraps *around* your own `add_middleware`/`@app.middleware` layers —
  unlike custom exception subclasses (`NotFoundException` etc.), which are
  handled by the inner `ExceptionMiddleware` sitting *inside* user middleware.
  Practical effect: if your own middleware's `call_next()` call is wrapped in
  `try/except Exception: ... raise`, an unhandled exception gets logged once
  there AND once in the catch-all handler — verified by triggering a
  deliberate `RuntimeError` in a temp route and seeing two tracebacks in the
  log. Fix: don't catch/log exceptions in the middleware at all; let them
  propagate to the single catch-all handler, which is the sole place that
  should log unexpected crashes.
- Because `setup_logging()` configures the **root** logger, third-party
  libraries that also use stdlib `logging` (e.g. `httpx`, `asyncio`)
  propagate their own log records up to it too — you'll see their INFO/DEBUG
  lines mixed into your log file. Not a bug; quiet it later with e.g.
  `logging.getLogger("httpx").setLevel(logging.WARNING)` if it gets noisy.

### Testing patterns/gotchas learned in Week 8 (carried forward)

- Query params (`?year=&month=`) vs JSON body vs path params are three
  distinct mechanisms — `client.get(url, params={...})` is the idiomatic way
  to send query params in tests, same role as `json=` for POST bodies.
- Money fields are `Decimal`, serialized to JSON as **strings**. Compare with
  `Decimal(response.json()["field"]) == Decimal("500.00")` on *both* sides —
  never mix `Decimal` against a raw string or float.
- Empty/zero results from report endpoints are a valid `200`, not `404` —
  a report query is always "successful", it just may have no data.
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

Week 10 - Docker (Dockerfile, Docker Compose) per ROADMAP.md.
