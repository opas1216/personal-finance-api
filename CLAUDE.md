# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

- Python + FastAPI + uvicorn
- PostgreSQL (database)
- SQLAlchemy ORM + Alembic (migrations)
- Pydantic v2 (schemas)
- Virtual environment at `.venv/`

## Commands

```powershell
# Run dev server
.venv\Scripts\python -m uvicorn app.main:app --reload

# Run migrations
.venv\Scripts\alembic upgrade head

# Create a new migration
.venv\Scripts\alembic revision --autogenerate -m "description"

# Run tests
.venv\Scripts\pytest
```

## Planned Directory Structure

```
app/
  main.py
  database.py        # SQLAlchemy engine & session
  models/            # SQLAlchemy ORM models
  schemas/           # Pydantic request/response schemas
  routers/           # FastAPI routers (one file per domain)
  services/          # Business logic
alembic/             # Migration files
tests/
```

## Database Schema (from PROJECT_SCOPE.md)

| Table        | Key Columns                                                                 |
|--------------|-----------------------------------------------------------------------------|
| users        | id, email, password_hash, created_at                                        |
| accounts     | id, user_id, name, type, currency                                           |
| categories   | id, user_id, name, type                                                     |
| transactions | id, user_id, account_id, category_id, amount, transaction_type, transaction_date, description |

---

## Architecture Rules

1. Use FastAPI
2. Use PostgreSQL
3. Use SQLAlchemy ORM
4. Use Alembic for migrations
5. Use Pydantic schemas

## Layer Rules

### Router

Router should:

- Receive request
- Validate request
- Call service
- Return response

Do NOT place business logic in routers.

### Service

Service should:

- Handle business logic
- Handle validations
- Coordinate database operations

### Model

Models should only define database structure.

## Development Rules

1. Follow ROADMAP.md
2. Do not implement future phases early
3. Keep changes small and focused
4. Explain important architectural decisions
5. Prefer simplicity over complexity

## Forbidden (Current Stage)

Do not introduce:

- Microservices
- DDD
- CQRS
- Event Sourcing
- Kafka
- Kubernetes

unless explicitly requested.

## Code Quality

- Add type hints
- Write readable code
- Avoid unnecessary abstractions
- Keep functions focused

## Before Creating Code

Check:

- Does it match current roadmap week?
- Is it needed now?
- Can it be explained in an interview?
- Is there a simpler solution?
