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