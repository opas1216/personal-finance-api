# Tier 1 Expansion Plan v3 — Personal Finance API

> **Project-specific overrides (decided 2026-07-15, superseding v3 where noted below):**
>
> - **Category direction ("usage_type")**: NOT adopted. `Category` stays a pure
>   label (name only) with no income/expense/both field and no compatibility
>   validation against `Transaction.transaction_type`. Direction lives solely
>   on the transaction. Reasoning: even a "both" tag still requires extra
>   state and a validation rule; the simplest model that fully covers the
>   Stock case (buy = expense, sell/dividend = income, same category) is no
>   binding at all. Concretely, skip these Phase 1 tasks below: "Replace
>   strict category type with `usage_type`", "Support `income`, `expense`,
>   `both`", "Add enum/database validation", "Add compatibility validation",
>   "Migrate existing category data". Any Stop Point / task elsewhere in this
>   document that references `usage_type` or category/transaction
>   compatibility validation does not apply to this project.
> - **Transfers**: adopted as-is, taken on as a Phase 1 warm-up before the
>   recurring-transaction work.
> - **Scheduler technology choice (Phase 4)**: intentionally not decided yet.
>   Revisit once Phase 2 (recurring transactions) and Phase 3 (idempotency)
>   exist and the need is concrete. Known constraint to weigh then: Render's
>   Free web service spins down when idle, so a naive in-process APScheduler
>   is not guaranteed to fire on schedule.
> - **Currency handling**: still an open gap not addressed anywhere in this
>   plan. Existing `accounts.currency` is a free string with no enforced
>   single-currency-per-user rule, and existing reports already sum
>   `Transaction.amount` across accounts without currency conversion. Must be
>   explicitly decided (assume single currency vs. real conversion) before
>   Phase 5 (Budget) work begins, since budget limits are compared directly
>   against summed transaction amounts.
>
> See `docs/current-architecture.md` and `PROGRESS.md` for the audit this
> plan builds on.

> Only future expansion work is included here.
>
> Existing completed capabilities are assumed:
> - User registration/login
> - JWT authentication and authorization
> - User/Account/Transaction/Category models
> - Basic CRUD
> - Monthly report
> - Category report
> - PostgreSQL / SQLite
> - Docker
> - CI/CD

---

# 1. Data Model Revision

A category may be usable for income, expense, or both.

Example:

```text
Category: Stock
Buy stock  -> expense
Sell stock -> income
Dividend   -> income
Fee        -> expense
```

Therefore:

## Transaction

The transaction owns the direction:

```text
transaction_type:
- income
- expense
- transfer
```

Optional future subtype:

```text
purchase
sale
dividend
fee
refund
adjustment
```

## Category

The category describes the purpose/domain:

```text
name:
Food
Salary
Stock
Rent
Transportation
```

Use:

```text
usage_type:
- income
- expense
- both
```

Examples:

| Category | usage_type |
|---|---|
| Salary | income |
| Food | expense |
| Stock | both |
| Refund | both |

Validation rule:

```text
Transaction.transaction_type must be allowed by Category.usage_type.
```

Tier 1 treats Stock only as a cash-flow category. It does not implement portfolio valuation, cost basis, realized profit, unrealized profit, or market price integration.

---

# 2. Tier 1 Expansion Goal

Upgrade the project into a production-like backend system with:

- Business rules
- Database consistency
- Background processing
- Idempotency
- Retry/failure recovery
- Budget evaluation
- Notifications
- Integration testing
- Observability
- Architecture documentation

Main flow:

```text
Recurring Transaction
-> Scheduled Execution
-> Idempotency Check
-> Database Transaction
-> Transaction Creation
-> Budget Evaluation
-> Alert Generation
-> Notification Record
-> Execution Log
```

---

# Phase 1 — Correct Transaction and Category Design

## Goal

Separate transaction direction from category applicability.

## Tasks

- [ ] Add/confirm `transaction_type` on transactions
- [ ] ~~Replace strict category type with `usage_type`~~ — not adopted, see override note at top
- [ ] ~~Support `income`, `expense`, `both`~~ — not adopted
- [ ] ~~Add enum/database validation~~ — not adopted
- [ ] ~~Add compatibility validation~~ — not adopted
- [ ] ~~Migrate existing category data~~ — not adopted
- [ ] Update monthly/category reports (only if `transfers` need excluding — see below)
- [ ] Add tests for valid/invalid combinations (ownership only, no direction compatibility)

## Transfer Design

A transfer is not income or expense.

Recommended dedicated model:

```text
transfers
- id
- user_id
- source_account_id
- destination_account_id
- amount
- transfer_date
- description
- created_at
```

Tasks:

- [ ] Add transfer model
- [ ] Add transfer service
- [ ] Add transfer API
- [ ] Make transfer atomic with DB transaction
- [ ] Exclude transfers from income/expense reports
- [ ] Add rollback tests

## Stop Point 1

Proceed only when:

- ~~Stock works for both income and expense~~ (already true — Stock is just a
  label, any transaction_type is allowed on it)
- ~~Strict categories reject invalid directions~~ (not applicable — no
  direction validation adopted)
- Transfers are atomic
- Transfers do not pollute reports
- Existing reports still pass

---

# Phase 2 — Recurring Transaction Domain

## New Model

```text
recurring_transactions
- id
- user_id
- account_id
- category_id
- amount
- transaction_type
- frequency
- interval
- start_date
- next_run_date
- end_date
- description
- is_active
- created_at
- updated_at
```

Suggested frequency values:

```text
daily
weekly
monthly
yearly
```

## Tasks

- [ ] Create model and migration
- [ ] Create schemas
- [ ] Implement next-run-date calculation
- [ ] Define month-end behavior
- [ ] Implement CRUD
- [ ] Add ownership validation
- [ ] ~~Add category compatibility validation~~ — not adopted, only ownership check applies
- [ ] Add unit/integration tests

Recommended month-end rule:

```text
January 31 -> February 28/29 -> March 31 -> April 30
```

## Stop Point 2

Proceed only when:

- CRUD works
- Month-end behavior is tested
- Ownership works (category compatibility check does not apply here)
- Date calculation is explainable

---

# Phase 3 — Database Transaction and Idempotency

## New Model

```text
recurring_transaction_runs
- id
- recurring_transaction_id
- scheduled_for
- status
- created_transaction_id
- error_message
- retry_count
- created_at
- updated_at
```

Required constraint:

```text
UNIQUE(recurring_transaction_id, scheduled_for)
```

Execution flow:

```text
Begin transaction
-> claim execution slot
-> create financial transaction
-> update run record
-> update next_run_date
-> commit
```

## Tasks

- [ ] Create model/migration
- [ ] Add unique constraint
- [ ] Implement idempotent execution service
- [ ] Add transaction boundary
- [ ] Add rollback handling
- [ ] Test duplicate execution
- [ ] Test partial failure
- [ ] Document concurrency assumptions

## Stop Point 3

Proceed only when:

- Duplicate runs cannot create duplicate transactions
- Partial failures leave no inconsistent data
- DB-level uniqueness exists
- Rollback is tested

---

# Phase 4 — Scheduler and Background Processing

Recommended first technology:

```text
APScheduler
```

Optional later:

```text
Celery + Redis
```

Only add Celery/Redis for a deliberate distributed-worker learning goal.

> Note: technology choice deliberately deferred — see override note at top of
> this document. Also weigh Render's Free-tier idle spin-down before
> committing to a pure in-process scheduler.

## Tasks

- [ ] Add scheduler
- [ ] Query due recurring transactions
- [ ] Reuse idempotent execution service
- [ ] Add retry policy
- [ ] Add maximum retry count
- [ ] Add failed status
- [ ] Make restart safe
- [ ] Make duplicate scheduler runs safe
- [ ] Add manual development trigger
- [ ] Add integration tests

## Stop Point 4

Proceed only when:

- Due transactions execute automatically
- Restarts do not duplicate data
- Retries do not duplicate data
- Failed runs are visible

---

# Phase 5 — Budget and Alert Integration

> Note: decide the currency-handling approach (see override note at top)
> before starting this phase — budget limits are compared directly against
> summed transaction amounts.

## Budget Rules

Only expense transactions count toward expense budgets.

A `both` category may be budgeted, but only its expense transactions count.

Suggested models:

```text
budgets
- id
- user_id
- category_id
- year
- month
- amount_limit
```

Constraint:

```text
UNIQUE(user_id, category_id, year, month)
```

```text
notifications
- id
- user_id
- type
- title
- message
- reference_type
- reference_id
- is_read
- created_at
```

```text
budget_alert_events
- id
- budget_id
- threshold
- year
- month
- created_at
```

Constraint:

```text
UNIQUE(budget_id, threshold, year, month)
```

Suggested thresholds:

```text
80%
100%
```

## Tasks

- [ ] Add/extend budget model
- [ ] Implement budget usage query
- [ ] Exclude income/transfers
- [ ] Implement threshold calculation
- [ ] Add notification model
- [ ] Add alert-event model
- [ ] Prevent duplicate alerts
- [ ] Trigger after manual expense
- [ ] Trigger after recurring expense
- [ ] Test `both` categories (categories are unrestricted here regardless — see override note)
- [ ] Test 80%/100%
- [ ] Test duplicate prevention

## Stop Point 5

Proceed only when:

- Only expenses count
- Transfers do not count
- Alerts are emitted once per threshold
- Manual/recurring flows reuse the same service

---

# Phase 6 — Testing and Failure Recovery

Required tests:

## Unit

- ~~Category compatibility~~ — not applicable, see override note
- Next-run calculation
- Month-end calculation
- Budget usage
- Threshold crossing
- Retry decisions

## Integration

- Transfer creation/rollback
- Recurring transaction creation
- Scheduled execution
- Idempotency
- DB rollback
- Budget alert
- Notification
- Authorization

## Failure Paths

- Invalid ownership
- ~~Invalid direction~~ — not applicable, no direction validation adopted
- Duplicate execution
- DB failure
- Scheduler retry
- Invalid recurring date
- Duplicate alert
- Transfer to same account

Recommended meaningful coverage:

```text
70%–85%
```

## Stop Point 6

Proceed only when:

- Core flows have integration tests
- Failure paths are tested
- CI runs the suite
- Tests are deterministic

---

# Phase 7 — Observability and Operations

Technologies:

- Structured logging
- Request/correlation ID
- Health check
- Readiness check
- Basic metrics
- Optional Sentry

Required logs:

- Transfer success/failure
- Recurring run start/success/failure
- Duplicate execution prevented
- Budget alert created
- Unexpected errors

Do not log passwords, JWTs, secrets, or full sensitive financial payloads.

Suggested metrics:

- Request count/latency
- Error count
- Recurring success/failure count
- Duplicate prevention count
- Budget alert count
- Transfer failure count

## Stop Point 7

Proceed only when:

- Failed jobs can be traced
- Transfer failures can be diagnosed
- Sensitive data is protected
- Health/readiness checks are meaningful

---

# Phase 8 — Documentation and Tier 1 Freeze

Required documentation:

```text
docs/architecture.md
docs/data-model.md
docs/category-and-transaction-design.md
docs/transfer-flow.md
docs/recurring-transaction-flow.md
docs/idempotency.md
docs/budget-alert-flow.md
docs/deployment.md
docs/interview-notes.md
```

Prepare to explain:

- Why direction belongs to transaction
- ~~Why category supports income/expense/both~~ — replace with: why this
  project deliberately chose no category/transaction direction binding at all
- Why transfers are separate
- Why Stock is bidirectional
- Idempotency
- DB transactions/rollback
- Unique constraints
- Scheduler restart/retry behavior
- Duplicate-alert prevention
- CI/CD
- Production debugging
- Scalability limits

## Final Stop Point

Freeze Tier 1 when:

- ~~Categories support income/expense/both~~ — replaced by: categories are
  unrestricted labels; direction lives on transactions only
- Transfers are atomic and excluded from reports
- Recurring transactions run automatically
- Duplicate execution is prevented
- Rollback is tested
- Budget alerts work without duplicates
- Core flows have integration tests
- CI/CD passes
- Logs diagnose failures
- Deployment is stable
- Architecture is documented
- You can explain the system without reading code

Then:

```text
Freeze Tier 1
-> Fix only bugs/docs
-> Begin Tier 2
```

---

# Exact Implementation Order

```text
1. (skipped — no category usage_type adopted)
2. (skipped — no category usage_type adopted)
3. (skipped — no category data migration needed)
4. Update reports only as needed to exclude transfers
5. Add dedicated transfer model/service
6. Add transfer tests
7. Add recurring transaction model
8. Add next-run calculation
9. Add recurring CRUD
10. Add recurring execution record
11. Add DB unique constraint
12. Add idempotent execution service
13. Add rollback tests
14. Add scheduler (technology TBD — see override note)
15. Add retry/restart safety
16. Decide currency-handling approach (see override note)
17. Add budget usage calculation
18. Add notification/alert-event models
19. Add duplicate-alert prevention
20. Connect manual/recurring expenses
21. Add integration/failure tests
22. Add structured logging
23. Add health/readiness/metrics
24. Harden deployment
25. Complete documentation
26. Run final review
27. Freeze Tier 1
28. Begin Tier 2
```

---

# Scope Boundary

Do not turn Tier 1 into an investment portfolio system.

Do not add yet:

- Stock price APIs
- Cost-basis calculation
- FIFO/LIFO lots
- Realized/unrealized profit
- Portfolio valuation
- Brokerage integration
- Kafka
- Kubernetes
- Microservices
- CQRS
- Event sourcing

Stock remains a cash-flow category in Tier 1.

Estimated total:

```text
8–12 weeks
```
