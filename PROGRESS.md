# Progress Notes

Working notes for picking up in-flight work across machines. See ROADMAP.md for
the overall plan — this file only tracks what's currently in progress.

## Status as of 2026-07-11

Week 8 (Testing) — **COMPLETE**. Full suite: 25 passed, 0 failed.

### Done

- `accounts`, `categories`: JWT-protected CRUD with ownership validation
  (403 via `ForbiddenException` when accessing another user's resource),
  verified end-to-end with two separate users.
- `app/routers/categories.py`: `POST /` returns `status_code=201`.
- `app/schemas/category.py`: `CategoryCreate.name` has `Field(min_length=1)`.
- `tests/test_categories.py`: 7/7 passing.
- `tests/test_reports.py`: **new this session**, 6/6 passing —
  `test_monthly_summary_success`, `test_monthly_summary_no_transactions`,
  `test_monthly_summary_unauthenticated`, `test_category_summary_success`,
  `test_category_summary_empty`, `test_category_summary_unauthenticated`.
  Covers `GET /reports/monthly` and `GET /reports/categories` (both take
  required `year`/`month` query params, both JWT-protected).
- `tests/test_accounts.py`, `tests/test_auth.py`, `tests/test_transactions.py`:
  passing.

### Testing patterns/gotchas learned this session (for future reference)

- Query params (`?year=&month=`) vs JSON body vs path params are three
  distinct mechanisms — `client.get(url, params={...})` is the idiomatic way
  to send query params in tests, same role as `json=` for POST bodies.
- Money fields are `Decimal`, serialized to JSON as **strings**. Compare with
  `Decimal(response.json()["field"]) == Decimal("500.00")` on *both* sides —
  never mix `Decimal` against a raw string or float.
- Empty/zero results from report endpoints are a valid `200`, not `404` —
  a report query is always "successful", it just may have no data. This means
  test setup (creating transactions before hitting a report endpoint) needs
  its own `assert create_response.status_code == 201` guard, otherwise a
  silently-failed setup step is indistinguishable from "genuinely no data"
  and the test passes green for the wrong reason.
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

Week 9 - Logging (Application Logging, Error Logging, Exception Handling per
ROADMAP.md). Exception handler mechanism (`app/main.py:12-26`) has already
been studied this session: custom exceptions inherit from plain `Exception`,
not FastAPI's `HTTPException`, so `@app.exception_handler(...)` is required
to map them to HTTP responses — otherwise they'd surface as unhandled 500s.
