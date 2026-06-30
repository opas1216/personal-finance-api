from fastapi import FastAPI, Request
from sqlalchemy import text
from starlette.responses import JSONResponse

from app.database import engine
from app.routers import accounts, categories, auth, transactions
from app.exceptions import NotFoundException, ForbiddenException, ConflictException, BadRequestException


app = FastAPI()

@app.exception_handler(NotFoundException)
async def not_found_handler(request: Request, exc: NotFoundException):
    return JSONResponse(status_code=404, content={"detail": exc.detail})

@app.exception_handler(ForbiddenException)
async def forbidden_handler(request: Request, exc: ForbiddenException):
    return JSONResponse(status_code=403, content={"detail": exc.detail})

@app.exception_handler(ConflictException)
async def conflict_handler(request: Request, exc: ConflictException):
    return JSONResponse(status_code=409, content={"detail": exc.detail})

@app.exception_handler(BadRequestException)
async def bad_request_handler(request: Request, exc: BadRequestException):
    return JSONResponse(status_code=400, content={"detail": exc.detail})



app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(auth.router)
app.include_router(transactions.router)


@app.get("/")
def root():
    return {"message": "Hello Personal Finance API"}


@app.get("/health/db")
def health_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
