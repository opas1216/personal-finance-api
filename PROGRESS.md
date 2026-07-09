# Progress Notes

Working notes for picking up in-flight work across machines. See ROADMAP.md for
the overall plan — this file only tracks what's currently in progress.

## Status as of 2026-07-10

Week 8 (Testing) — `tests/test_categories.py` is now fully green (7/7).

### Done

- `accounts`: full CRUD is JWT-protected. `get_all`/`get_one`/`update`/`delete`
  all verify the resource belongs to `current_user` (403 via
  `ForbiddenException` otherwise). Verified end-to-end with two separate
  users.
- `categories`: same JWT + ownership-validation pattern applied, mirroring
  `accounts`. Also verified end-to-end with two separate users.
- `app/routers/categories.py`: `POST /` now returns `status_code=201`
  (matches `accounts`' convention — FastAPI defaults to 200, so only POST
  needs an explicit override; GET/PUT already default correctly and DELETE
  is already 204).
- `app/schemas/category.py`: `CategoryCreate.name` now has
  `Field(min_length=1)` so an empty name is rejected with 422.
- `tests/test_categories.py`: all 7 tests passing —
  `test_create_category`, `test_create_category_unauthenticated`,
  `test_create_category_invalid_data`, `test_get_categories_by_id`,
  `test_get_category_missing_id` (rewritten to use a real nonexistent id
  `9999` instead of `""`, since an empty path segment collapses the URL to
  `/categories/` and hits `get_all`, not `get_one`), `test_get_categories_by_user_id`
  (rewritten to drop the invalid `json=` kwarg on `.get()` and to assert on
  `user_id` — comparing against a category's own `id` is a different PK and
  only coincidentally matches in a fresh per-test SQLite db), and the new
  `test_get_categories_unauthenticated`.
- `tests/test_accounts.py`, `tests/test_auth.py`, `tests/test_transactions.py`:
  passing.
- Full suite: 17 passed, 0 failed.

### Environment gotcha (fixed locally, check on other machines)

This machine's `.env` was missing `SECRET_KEY` (present in `.env.example`
but not `.env`), which made every JWT-issuing test fail at the
`auth_headers` fixture with `TypeError: Expected a string value` in
`jwt.encode()`. Added a locally-generated `SECRET_KEY` to `.env` (gitignored,
not pushed). If tests fail the same way on another machine, check `.env`
there too.

### Next up

Go learn how `@app.exception_handler` works (`app/main.py:12-26`) — four
handlers map `NotFoundException` → 404, `ForbiddenException` → 403,
`ConflictException` → 409, `BadRequestException` → 400. This was deferred
earlier to focus on the ownership-validation work.

After that: Week 9 - Logging.
