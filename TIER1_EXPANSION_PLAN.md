# Tier 1 Expansion Plan — Personal Finance API

> Goal: Deepen the existing Personal Finance API into a production-like backend project that can be explained confidently in backend interviews, especially for Japan-oriented backend roles.

---

# 1. Current Starting Point

The current project already includes:

- FastAPI
- Pydantic
- PostgreSQL
- SQLite
- JWT
- Authentication
- Authorization
- Docker
- CI
- CD

The purpose of this plan is not to repeat the same stack.

The purpose is to deepen the project through:

- Real business logic
- Database consistency
- Background processing
- Idempotency
- Testing
- Observability
- Failure handling
- Architecture documentation

---

# 2. Final Target of Tier 1

Tier 1 is considered complete when the project can demonstrate:

- A meaningful finance-related business workflow
- Reliable database transactions
- Scheduled or background execution
- Protection against duplicate execution
- Strong integration tests
- Production-like logging and error handling
- Clear architecture documentation
- Deployment and operational understanding
- Interview-ready technical explanations

The target is not to build every possible finance feature.

The target is to build one complete and reliable backend flow.

---

# 3. Recommended Core Expansion Flow

The main expansion flow will be:

```text
Recurring Transaction
→ Scheduler / Background Job
→ Transaction Creation
→ Idempotency Check
→ Budget Calculation
→ Budget Alert
→ Notification Record
→ Audit Log
```

This flow is selected because it naturally introduces important backend concepts without forcing unnecessary complexity.

---

# 4. Phase Overview

```text
Phase 0 — Project Audit and Baseline
Phase 1 — Domain Model and Business Rules
Phase 2 — Database Transaction and Idempotency
Phase 3 — Recurring Transactions and Scheduler
Phase 4 — Budget and Alert System
Phase 5 — Testing and Failure Scenarios
Phase 6 — Logging, Metrics, and Observability
Phase 7 — Deployment Hardening and Documentation
Final Stop Point — Decide whether to enter Tier 2
```

---

# Phase 0 — Project Audit and Baseline

## Goal

Understand the existing codebase before adding new features.

## Technologies

- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Pytest
- Docker
- CI/CD

## Tasks

- [ ] Review current project structure
- [ ] Review router, service, model, and schema boundaries
- [ ] Confirm all database schema changes use Alembic
- [ ] Confirm secrets are loaded from environment variables
- [ ] Confirm PostgreSQL is used in production
- [ ] Confirm SQLite is only used for tests if applicable
- [ ] Confirm current API tests run successfully
- [ ] Confirm CI pipeline passes
- [ ] Confirm deployed application health check works
- [ ] Write a short current architecture summary

## Deliverables

- `docs/current-architecture.md`
- Baseline test result
- Current API endpoint list
- Known technical debt list

## Stop Point 0

Proceed only when:

- The current system can run locally
- The test suite passes
- The deployed version works
- You understand the current request flow
- You can explain where validation, business logic, and DB access happen

If these conditions are not met, do not add new features yet.

---

# Phase 1 — Domain Model and Business Rules

## Goal

Introduce meaningful finance domain logic instead of adding more CRUD endpoints.

## Main Feature

Recurring transaction definition.

Examples:

- Monthly rent
- Monthly salary
- Insurance payment
- Childcare fee
- Subscription payment

## Technologies

- SQLAlchemy
- Alembic
- Pydantic
- PostgreSQL constraints
- Enum types
- Date and time handling

## New Table: recurring_transactions

Suggested fields:

```text
id
user_id
account_id
category_id
amount
transaction_type
frequency
start_date
next_run_date
end_date
description
is_active
created_at
updated_at
```

Suggested frequency values:

```text
daily
weekly
monthly
yearly
```

## Business Rules

- Amount must be greater than 0
- Account must belong to the current user
- Category must belong to the current user
- Category type must match transaction type
- Next run date cannot be earlier than start date
- End date cannot be earlier than start date
- Inactive recurring transactions must not execute
- User must not access another user's recurring transaction

## API Targets

```http
POST /recurring-transactions
GET /recurring-transactions
GET /recurring-transactions/{id}
PATCH /recurring-transactions/{id}
DELETE /recurring-transactions/{id}
```

## Tasks

- [ ] Design recurring transaction model
- [ ] Create Alembic migration
- [ ] Create Pydantic request and response schemas
- [ ] Create service-layer business rules
- [ ] Create authorization checks
- [ ] Implement CRUD APIs
- [ ] Write validation tests
- [ ] Write ownership tests

## Deliverables

- Recurring transaction CRUD
- Migration file
- Domain rules documented
- Tests for invalid scenarios

## Stop Point 1

Proceed only when:

- Recurring transaction CRUD works
- All ownership checks work
- Validation rules are tested
- Business logic is not placed directly in routers
- You can explain why recurring transactions require their own table

If these are not met, stay in Phase 1.

---

# Phase 2 — Database Transaction and Idempotency

## Goal

Guarantee that scheduled transaction creation is consistent and not duplicated.

## Core Concepts

- Atomic database transaction
- Rollback
- Unique constraint
- Idempotency
- Race condition awareness

## Technologies

- PostgreSQL transactions
- SQLAlchemy session transaction
- Unique indexes
- Database constraints

## New Table: recurring_transaction_runs

Suggested fields:

```text
id
recurring_transaction_id
scheduled_for
status
created_transaction_id
error_message
created_at
updated_at
```

Suggested status values:

```text
pending
processing
completed
failed
```

## Idempotency Rule

A recurring transaction must only generate one transaction for the same scheduled date.

Recommended unique constraint:

```text
(recurring_transaction_id, scheduled_for)
```

## Target Flow

```text
Start DB transaction
→ Create execution record
→ Create financial transaction
→ Update execution record
→ Update next_run_date
→ Commit
```

If any step fails:

```text
Rollback
→ Mark execution failed when appropriate
→ Log error
```

## Tasks

- [ ] Design recurring transaction run model
- [ ] Add unique constraint
- [ ] Implement transaction generation service
- [ ] Wrap write operations in a DB transaction
- [ ] Handle duplicate execution safely
- [ ] Handle rollback
- [ ] Test duplicate execution
- [ ] Test partial failure
- [ ] Test concurrent execution assumptions

## Deliverables

- Idempotent recurring transaction execution
- DB transaction handling
- Failure tests
- Technical note explaining the chosen strategy

## Stop Point 2

Proceed only when:

- Duplicate execution does not create duplicate transactions
- Failed execution does not leave partial data
- Rollback behavior is tested
- Unique constraint is enforced at DB level
- You can explain why application-only checks are insufficient

This is a major Tier 1 checkpoint.

---

# Phase 3 — Scheduler and Background Job

## Goal

Run recurring transaction creation outside normal request-response flow.

## Recommended Technology

Start with one of:

- APScheduler
- Celery

Recommended learning path:

```text
APScheduler first
→ Celery only if a distributed worker is actually needed
```

Do not add Kafka or Kubernetes.

## Suggested Architecture

```text
Scheduler
→ Find due recurring transactions
→ Execute one job per recurring transaction
→ Reuse idempotent service from Phase 2
```

## Tasks

- [ ] Add scheduler component
- [ ] Add periodic due-transaction query
- [ ] Reuse transaction generation service
- [ ] Add safe job locking or duplicate protection
- [ ] Record execution result
- [ ] Add retry policy
- [ ] Add maximum retry limit
- [ ] Add failed job handling
- [ ] Add tests for scheduled execution
- [ ] Add manual trigger endpoint for development only

## Optional Technology

Use Redis only if using Celery.

Do not add Redis merely to say Redis is used.

## Deliverables

- Background recurring transaction execution
- Retry behavior
- Failure record
- Scheduler documentation

## Stop Point 3

Proceed only when:

- Scheduler creates due transactions automatically
- Duplicate scheduler runs are safe
- Retry does not create duplicates
- Failed jobs are visible
- You can explain scheduler vs worker responsibility
- You can explain why the job is outside the HTTP request lifecycle

At this point, the project is already stronger than a normal junior CRUD portfolio.

---

# Phase 4 — Budget and Alert System

## Goal

Add a second business domain that consumes transaction data.

## Main Features

- Monthly budget
- Category budget
- Budget usage calculation
- Overspending alert

## Technologies

- PostgreSQL aggregation
- SQLAlchemy query building
- Date range handling
- Domain service
- Notification table

## New Table: budgets

Suggested fields:

```text
id
user_id
category_id
year
month
amount_limit
created_at
updated_at
```

Recommended unique constraint:

```text
(user_id, category_id, year, month)
```

## New Table: notifications

Suggested fields:

```text
id
user_id
type
title
message
is_read
created_at
```

## Business Rules

- One monthly budget per user, category, year, and month
- Budget amount must be greater than 0
- Only expense transactions count toward expense budgets
- Alert should not be created repeatedly for the same threshold event
- Budget data must only include current user's transactions

## Suggested Alert Thresholds

```text
80%
100%
```

## Target Flow

```text
Transaction created
→ Calculate current monthly usage
→ Compare against budget
→ Create alert if threshold crossed
```

## Tasks

- [ ] Create budget model
- [ ] Create notification model
- [ ] Add migrations
- [ ] Implement budget CRUD
- [ ] Implement budget usage API
- [ ] Implement threshold evaluation
- [ ] Prevent duplicate alerts
- [ ] Trigger alert after transaction creation
- [ ] Trigger alert after recurring transaction execution
- [ ] Add tests for 80% and 100% thresholds

## Deliverables

- Budget management
- Budget usage report
- Alert generation
- Duplicate alert prevention

## Stop Point 4

Proceed only when:

- Budget usage is calculated correctly
- Alerts are generated at correct thresholds
- Duplicate alerts are prevented
- Recurring and manual transactions share the same logic
- Aggregation queries are tested
- You can explain where budget calculation belongs in the architecture

---

# Phase 5 — Testing and Failure Scenarios

## Goal

Upgrade the project from "working" to "reliable".

## Technologies

- Pytest
- Test database
- Integration tests
- Fixtures
- Mocking only where necessary
- Coverage reporting

## Required Test Categories

### Unit Tests

- Date calculation
- Next run date calculation
- Budget threshold calculation
- Validation logic

### Integration Tests

- User registration and login
- Authorization
- Recurring transaction CRUD
- Scheduled transaction execution
- Idempotency
- DB rollback
- Budget alert creation
- Report queries

### Failure Tests

- Invalid ownership
- Duplicate job execution
- DB failure
- Invalid date
- Scheduler retry
- Expired JWT
- Missing authorization
- Invalid category type
- Duplicate budget definition

## Recommended Coverage Target

Do not chase 100%.

Recommended target:

```text
70%–85% meaningful coverage
```

## Tasks

- [ ] Create reliable test fixtures
- [ ] Separate test database
- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Add failure-path tests
- [ ] Add coverage output to CI
- [ ] Make CI fail below minimum threshold

## Deliverables

- Stable test suite
- CI coverage report
- Failure scenario documentation

## Stop Point 5

Proceed only when:

- Core business flows are integration tested
- Failure paths are tested
- CI runs tests automatically
- Tests are deterministic
- You can explain the difference between unit and integration tests
- You can change a core business rule with confidence

If tests are flaky, do not continue.

---

# Phase 6 — Logging, Metrics, and Observability

## Goal

Make the system diagnosable after deployment.

## Technologies

- Python logging
- Structured JSON logging
- Request ID / Correlation ID
- Health check
- Readiness check
- Metrics library
- Optional Sentry

## Required Logs

- Request start and end
- Authentication failure
- Recurring job start and completion
- Recurring job failure
- Duplicate execution prevention
- Budget alert creation
- Unexpected exception

## Logging Rules

Do not log:

- Passwords
- JWT tokens
- Full sensitive financial data
- Secrets

## Suggested Metrics

- Request count
- Request latency
- Error count
- Scheduled job success count
- Scheduled job failure count
- Duplicate job prevention count

## Tasks

- [ ] Add structured logging
- [ ] Add request ID
- [ ] Add global exception logging
- [ ] Add health endpoint
- [ ] Add readiness endpoint
- [ ] Add basic metrics
- [ ] Add optional error monitoring
- [ ] Document operational troubleshooting

## Deliverables

- Structured logs
- Metrics endpoint or monitoring integration
- Troubleshooting guide

## Stop Point 6

Proceed only when:

- A failed job can be diagnosed from logs
- Request and job executions can be traced
- Sensitive information is not logged
- Health and readiness checks are meaningful
- You can explain how you would investigate a production failure

---

# Phase 7 — Deployment Hardening and Documentation

## Goal

Make the project portfolio-ready and interview-ready.

## Technologies

- Docker
- Docker Compose
- GitHub Actions
- Deployment platform
- Environment-based configuration
- Alembic migrations
- Architecture diagrams

## Deployment Tasks

- [ ] Confirm production uses PostgreSQL
- [ ] Confirm migrations run safely
- [ ] Confirm secrets are configured securely
- [ ] Confirm rollback procedure
- [ ] Confirm health checks
- [ ] Confirm scheduler runs in correct process
- [ ] Confirm application restart behavior
- [ ] Confirm logs are accessible
- [ ] Confirm CI/CD pipeline stages

## Documentation Files

Recommended:

```text
README.md
PROJECT_SCOPE.md
ROADMAP.md
CLAUDE.md
docs/architecture.md
docs/data-model.md
docs/recurring-transaction-flow.md
docs/idempotency.md
docs/deployment.md
docs/interview-notes.md
```

## Architecture Diagram Should Include

```text
Client
→ FastAPI API
→ Service Layer
→ PostgreSQL

Scheduler
→ Background Job
→ Recurring Transaction Service
→ PostgreSQL

Transaction Service
→ Budget Service
→ Notification Service
```

## Interview Preparation

Prepare answers for:

- Why FastAPI?
- Why PostgreSQL?
- Why SQLite exists in the project?
- How JWT works?
- Authentication vs authorization?
- How idempotency is implemented?
- How database rollback works?
- How recurring transaction execution works?
- How duplicate alerts are prevented?
- How CI/CD works?
- How production failures are diagnosed?
- What would change at 1 million users?

## Deliverables

- Updated README
- Architecture diagram
- ERD
- Deployment guide
- Technical decision notes
- Interview notes

## Stop Point 7

Tier 1 is complete when:

- The system is deployed
- Core business flow works end-to-end
- Tests pass in CI
- Scheduler works
- Idempotency works
- Budget alert works
- Logs support debugging
- Architecture is documented
- You can explain the project without reading code
- You can discuss tradeoffs and limitations

---

# 5. Final Tier 1 Completion Checklist

## Core Backend

- [ ] Authentication
- [ ] Authorization
- [ ] PostgreSQL
- [ ] Alembic
- [ ] Service layer
- [ ] Business validation
- [ ] Database transaction
- [ ] Idempotency
- [ ] Background job
- [ ] Scheduler
- [ ] Retry handling
- [ ] Failure handling

## Business Features

- [ ] Recurring transaction
- [ ] Budget management
- [ ] Budget usage report
- [ ] Budget alert
- [ ] Notification record
- [ ] Audit or execution record

## Quality

- [ ] Unit tests
- [ ] Integration tests
- [ ] Failure-path tests
- [ ] CI test execution
- [ ] Coverage report
- [ ] Structured logging
- [ ] Health check
- [ ] Readiness check

## Portfolio

- [ ] Deployment
- [ ] README
- [ ] Architecture diagram
- [ ] ERD
- [ ] Technical decision notes
- [ ] Interview notes

---

# 6. Hard Stop Rules

Do not continue adding features forever.

Tier 1 must stop when all of the following are true:

1. Recurring transaction works automatically
2. Duplicate execution is prevented
3. Budget alert works
4. Database transaction and rollback are tested
5. Core flow has integration tests
6. CI/CD passes
7. Logs can diagnose failures
8. The project is deployed
9. Architecture is documented
10. You can explain the system confidently

Once these conditions are met:

```text
Stop expanding Tier 1
→ Freeze new feature development
→ Fix only bugs and documentation
→ Begin Tier 2 project
```

---

# 7. What Not to Add Before Tier 2

Do not add these unless there is a clear technical reason:

- Kafka
- Kubernetes
- Microservices
- GraphQL
- Event sourcing
- CQRS
- Multi-region deployment
- Complex recommendation engine
- Machine learning
- Blockchain
- Full frontend application

These may create complexity without improving backend fundamentals.

---

# 8. Tier 2 Entry Criteria

Begin Tier 2 only when:

- [ ] Tier 1 hard stop rules are satisfied
- [ ] You can explain the full request flow
- [ ] You can explain the scheduled job flow
- [ ] You can explain idempotency
- [ ] You can explain DB transaction behavior
- [ ] You can explain CI/CD pipeline
- [ ] You can diagnose a failed deployed job
- [ ] You can write a new integration test without AI doing everything
- [ ] You can modify one business rule safely
- [ ] You can discuss current architecture limitations

---

# 9. Suggested Work Order

Recommended exact order:

```text
1. Audit current project
2. Add recurring transaction model and CRUD
3. Add recurring execution record
4. Add database transaction
5. Add idempotency
6. Add scheduler
7. Add retry and failure handling
8. Add budget model
9. Add budget usage calculation
10. Add alert generation
11. Add duplicate alert prevention
12. Add integration tests
13. Add failure tests
14. Add structured logging
15. Add health and readiness checks
16. Add metrics
17. Harden deployment
18. Complete documentation
19. Run final review
20. Stop Tier 1 and enter Tier 2
```

---

# 10. Recommended Pace

A realistic pace:

```text
Phase 0: 1 week
Phase 1: 1–2 weeks
Phase 2: 1–2 weeks
Phase 3: 2 weeks
Phase 4: 1–2 weeks
Phase 5: 2 weeks
Phase 6: 1 week
Phase 7: 1 week
```

Estimated total:

```text
10–13 weeks
```

Do not rush.

The quality of explanation and understanding matters more than the number of features.

---

# 11. Final Reminder

The goal of Tier 1 is not:

> Use as many technologies as possible.

The goal is:

> Build one backend project that demonstrates reliable business logic, data consistency, background processing, testing, deployment, and operational understanding.

When this plan is complete, Personal Finance API should be strong enough to serve as the primary technical project in a backend job interview.
