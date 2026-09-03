from fastapi import FastAPI, Request
from sqlalchemy import text
from starlette.responses import JSONResponse

from app.database import engine
from app.routers import accounts, categories, auth, transactions, reports, transfers
from app.exceptions import NotFoundException, ForbiddenException, ConflictException, BadRequestException, ExternalServiceException
import logging
from app.logging_config import setup_logging

setup_logging()
app = FastAPI()

logger = logging.getLogger(__name__)

@app.exception_handler(NotFoundException)
async def not_found_handler(request: Request, exc: NotFoundException):
    logger.warning(f"{request.method} {request.url.path} - NotFoundException: {exc.detail}")
    return JSONResponse(status_code=404, content={"detail": exc.detail})

@app.exception_handler(ForbiddenException)
async def forbidden_handler(request: Request, exc: ForbiddenException):
    logger.warning(f"{request.method} {request.url.path} - ForbiddenException: {exc.detail}")
    return JSONResponse(status_code=403, content={"detail": exc.detail})

@app.exception_handler(ConflictException)
async def conflict_handler(request: Request, exc: ConflictException):
    logger.warning(f"{request.method} {request.url.path} - ConflictException: {exc.detail}")
    return JSONResponse(status_code=409, content={"detail": exc.detail})

@app.exception_handler(BadRequestException)
async def bad_request_handler(request: Request, exc: BadRequestException):
    logger.warning(f"{request.method} {request.url.path} - BadRequestException: {exc.detail}")
    return JSONResponse(status_code=400, content={"detail": exc.detail})

@app.exception_handler(ExternalServiceException)
async def external_service_exception(request: Request, exc: ExternalServiceException):
    logger.warning(f"{request.method} {request.url.path} - ExternalServiceException: {exc.detail}")

    # status code 用 502 Bad Gateway——語意是「我們自己沒錯,但我們依賴的上游服務掛了」
    return JSONResponse(status_code=502, content={"detail": exc.detail})

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"{request.method} {request.url.path} - Unhandled exception: {str(exc)}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"}) # 回傳Internal server error是因為不要讓外部使用者知道真正的錯誤內容避免有安全疑慮，logger會有詳細的原因紀錄

@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path}: {response.status_code}")
    return response



app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(reports.router)
app.include_router(transfers.router)


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
