from pydantic import BaseModel

# 定義建立時 client 要傳什麼欄位
class AccountCreate(BaseModel):
    user_id: int
    name: str
    type: str
    currency: str


# 底下的資料決定了，當Update 資料時，會有哪些資料可以被更新，
# 定義更新時可以改哪些欄位，全部 Optional
class AccountUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    currency: str | None = None


# Response model 決定了你想要回傳給User時的資料有哪些，創建table 結構時有很多種資料，
# 但在底下可以決定要背回傳給User的資料是哪幾個特定資料，沒有記載的資料就不會被回傳，定義回傳給 client 的欄位長什麼樣
class AccountResponse(BaseModel):
    id: int
    user_id: int
    name: str
    type: str
    currency: str

    model_config = {"from_attributes": True}


"""
SQLAlchemy ORM 物件（Python 物件，有屬性）
      ↓ from_attributes = True
Pydantic schema 物件（Python 物件，有欄位）
      ↓ Pydantic 序列化
JSON（純文字，可以透過網路傳送）

Schema 和 JSON 很像，但不是同一個東西：

  ┌──────────┬───────────────────────┬───────────────────────┐
  │          │  Schema（Pydantic）   │         JSON          │
  ├──────────┼───────────────────────┼───────────────────────┤
  │ 本質     │ Python 物件           │ 純文字字串            │
  ├──────────┼───────────────────────┼───────────────────────┤
  │ 有型別   │ ✅ Decimal, date, int │ ❌ 全部都是字串或數字 │
  ├──────────┼───────────────────────┼───────────────────────┤
  │ 可以傳輸 │ ❌                    │ ✅                    │
  └──────────┴───────────────────────┴───────────────────────┘

  例如：

  # Pydantic schema 物件（還在 Python 裡）
  TransactionResponse(id=1, amount=Decimal("150.00"), transaction_date=date(2026, 6, 30))

  # 序列化成 JSON（變成可傳輸的純文字）
  {"id": 1, "amount": "150.00", "transaction_date": "2026-06-30"}

  Decimal 和 date 是 Python 型別，JSON 裡沒有這些，Pydantic 負責把它們轉成 JSON 認識的格式。

"""