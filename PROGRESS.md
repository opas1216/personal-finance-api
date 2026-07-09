# Progress Notes

Working notes for picking up in-flight work across machines. See ROADMAP.md for
the overall plan — this file only tracks what's currently in progress.

## Status as of 2026-07-09

Week 8 (Testing) is in progress.

### Done

- `accounts`: full CRUD is JWT-protected. `get_all`/`get_one`/`update`/`delete`
  all verify the resource belongs to `current_user` (403 via
  `ForbiddenException` otherwise). Verified end-to-end with two separate
  users.
- `categories`: same JWT + ownership-validation pattern applied, mirroring
  `accounts`. Also verified end-to-end with two separate users.
- `tests/test_accounts.py`: 4 tests, all passing.
- `tests/test_auth.py`, `tests/test_transactions.py`: passing.

### Next up: `tests/test_categories.py` (4 of 7 tests currently failing)

1. `test_create_category` expects 201, gets 200 — `POST /categories/` needs
   `status_code=status.HTTP_201_CREATED` on the route decorator, same as
   `accounts`.
2. `test_create_category_invalid_data` sends `name=""` and expects 422, gets
   200 — `CategoryCreate.name` has no length validation yet; needs something
   like `Field(min_length=1)` or a `field_validator`.
3. `test_get_category_missing_id` uses `category_id=""` and expects 404 — the
   test's premise is broken: an empty id collapses the URL to `/categories/`,
   which hits the list route (`get_all`), not the detail route. Rewrite using
   a real nonexistent numeric id (e.g. `99999`) to actually exercise the
   `NotFoundException` → 404 path.
4. `test_get_categories_by_user_id` calls
   `client.get("/categories/", json={...})` — `TestClient.get()` doesn't
   accept a `json` kwarg, and `user_id` isn't needed anymore now that
   `get_all` is JWT-based. Rewrite as
   `client.get("/categories/", headers=auth_headers)`.
5. `test_get_categories_missing_user_id` has no assertions yet — needs to be
   filled in.

### Reminder

Once `test_categories.py` is green, go learn how `@app.exception_handler`
works (`app/main.py:12-26`) — four handlers map `NotFoundException` → 404,
`ForbiddenException` → 403, `ConflictException` → 409, `BadRequestException`
→ 400. This was deferred earlier to focus on the ownership-validation work.
