import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# 使用 SQLite 作為測試資料庫，避免汙染正式的 PostgreSQL
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

# 建立測試用的 SQLite engine
# check_same_thread=False 是 SQLite 的必要設定，允許多執行緒存取
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 建立指向測試 DB 的 session 工廠（不使用正式的 SessionLocal）
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)   # 測試前：根據 ORM model 建立所有 table
    session = TestingSessionLocal()          # 建立一個測試用的 DB session 實例
    try:
        yield session                        # 將 session 提供給測試使用
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine) # 測試後：刪除所有 table，確保每次測試都是乾淨的


@pytest.fixture
def client(db):
    def override_get_db():
        yield db                            # 將測試 session 注入，取代正式 DB session

    # 替換 FastAPI 的 get_db dependency，讓 API 在測試時連到測試 DB
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c                             # 提供模擬 HTTP 請求的 TestClient
    app.dependency_overrides.clear()        # 測試結束後清除 dependency 替換


@pytest.fixture
def auth_headers(client):
    # 建立測試用的 user
    client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "password123"
    })
    # 登入取得 JWT token
    # respones是一個Token物件
    response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "password123"
    })
    token = response.json()["access_token"]
    # 回傳帶有 token 的 Authorization header，供需要驗證的測試使用
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def mock_frankfurter(monkeypatch):
    # 模擬 Frankfurter API 回傳的匯率資料
    def fake_get(url, params=None, **kwargs):
        request = httpx.Request("GET", url, params=params)

        if "v2/currencies" in url:
            return httpx.Response(200, request=request, json=[
                {"iso_code": "TWD"},
                {"iso_code": "USD"},
                {"iso_code": "JPY"},
            ])

        if "v2/rates" in url:
            return httpx.Response(200, request=request, json=[
                {"quote": "TWD", "rate": 30.5},
                {"quote": "USD", "rate": 1.0},
                {"quote": "JPY", "rate": 110.0},
            ])

    monkeypatch.setattr(httpx, "get", fake_get)
