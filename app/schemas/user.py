from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id :int
    email: str
    created_at: datetime

    model_config = {'from_attributes': True}

# JWT(Json Web Token)
# Login 成功後，server 不想每次都去查資料庫確認你是誰，所以發一張「通行證」給 client，之後每次 request帶著這張通行證，server 驗證它合法就直接信任。

# JWT 長這樣（三段用 . 分隔）：
#
#   eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxfQ.abc123xyz
#        ↑ Header           ↑ Payload          ↑ Signature
#     (演算法資訊)      (你放進去的資料)      (防偽簽名)
#
#   - Header：說明用什麼演算法簽名
#   - Payload：你放的資料，例如 {"user_id": 1, "exp": 過期時間}
#   - Signature：用 SECRET_KEY 對前兩段簽名，別人沒有 key 就無法偽造
#
#   任何人都可以解碼前兩段看內容（它只是 base64），但沒有 SECRET_KEY 就無法產生合法的 Signature，所以無法偽造。

class Token(BaseModel):
    access_token: str   # JWT(Json Web Token) 字串本身，例如 "eyJhbGci..."
    token_type: str     # 固定值 "bearer"，告訴 client 這是 Bearer token


# HTTP 規範定義了幾種 token 類型，告訴 client 要怎麼使用這個 token：
#
#   ┌────────────┬───────────────────────────────────────────────┐
#   │ token_type │                   使用方式                    │
#   ├────────────┼───────────────────────────────────────────────┤
#   │ bearer     │ 帶在 Header：Authorization: Bearer <token>    │
#   ├────────────┼───────────────────────────────────────────────┤
#   │ basic      │ 帳密用 base64 編碼後放 Header（很舊，不安全） │
#   ├────────────┼───────────────────────────────────────────────┤
#   │ mac        │ 每個 request 都重新計算簽名（複雜，少用）     │
#   └────────────┴───────────────────────────────────────────────┘
#
#   為什麼用 bearer？
#
#   因為專案是 REST API，client 拿到 JWT 後每次 request 帶在 Header 裡，這正是 bearer
#   的使用方式。它是目前最主流的方式，簡單、無狀態、適合 API。



#  OAuth2 = Open Authorization 2.0
#
#   OAuth2 是一個授權框架的規範，定義了「如何讓第三方應用安全地取得使用者的授權」。
#
#   常見到的場景：
#
#   「使用 Google 登入」
#
#   你的 app → Google：「這個用戶允許我存取他的 email 嗎？」
#   Google → 用戶：「XXX app 想存取你的 email，允許嗎？」
#   用戶同意 → Google → 你的 app：「這是 token，代表用戶授權了」