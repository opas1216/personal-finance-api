# Domain Glossary — 資料表與名詞定義

> 這份文件的目的：開發時間拉長後，很容易忘記當初設計某個欄位/資料表的「確切用途」，
> 尤其是名稱相近但意義不同的東西（例如 `Category.type` 跟 `Transaction.transaction_type`）。
> 這份文件記錄「現在程式碼實際運作的樣子」，不是規劃文件——規劃中還沒做的部分見文末章節。
>
> 建立時間：2026-09-02，根據當時的 `app/models/`、`app/schemas/`、`app/services/` 實際內容整理。
> 之後每次資料表/欄位有變動，應該回來更新這份文件，避免它過時後反而造成誤導。

---

## 1. 系統總覽

```
Client
  -> Router   (app/routers/*.py)    只做：收 request -> 呼叫 service -> 回傳 response
  -> Service  (app/services/*.py)   商業邏輯、擁有權驗證、資料庫操作
  -> Model    (app/models/*.py)     純 SQLAlchemy 資料表結構，不放邏輯
  -> PostgreSQL（本機/正式環境）／SQLite（測試環境）
```

---

## 2. 資料表清單

### `users`（`app/models/user.py`）

登入身分本身。

| 欄位 | 用途 |
|---|---|
| `email` / `password_hash` | 登入憑證 |
| `base_currency` | 這個使用者的「記帳本位幣別」，預設 `TWD`。所有報表加總都換算成這個幣別。**目前沒有「修改 base_currency」的 API**——一旦決定要做，舊交易的快照金額要一起處理，故意留到之後再設計 |

### `accounts`（`app/models/account.py`）

代表使用者實際持有的一個「錢包/帳戶」，例如「國泰銀行」「現金」「美股券商」。

| 欄位 | 用途 |
|---|---|
| `name` | 使用者自己取的帳戶名稱 |
| `type` | 帳戶種類的自由文字欄位（例如 `checking`、`cash`、`credit_card`）。**目前 schema 裡是純 `str`，沒有 enum 驗證**，靠使用者自己維持一致 |
| `currency` | 這個帳戶計價用的幣別，例如 `TWD`、`USD`。透過 `is_valid_currency()` 對照 Frankfurter `v2/currencies`（165 種）驗證，不是隨便字串都能過 |

**目前可以透過 `PUT /accounts/{id}` 修改 `currency`**——這是 Phase 1c 設計討論時特別確認過的一點：因為可修改，`Transfer` 才需要在建立當下把 `source_amount`/`destination_amount` 都存下來，而不是只存一個金額 + 事後用「當時帳戶幣別」回推。

### `categories`（`app/models/category.py`）

**這是先前最容易搞混的地方，特別記錄清楚：**

| 欄位 | 目前實際用途（依 code 裡的中文註解） | 對照 |
|---|---|---|
| `name` | **小分類**，使用者自訂的具體標籤。例如「外送」「聚會」「外食」「減肥餐」 | 這些都是被某個大領域包起來的細項 |
| `type` | **大分類**，例如「食」「衣」「住」「行」 | 用來分組用的領域標籤 |

也就是說目前的實際慣例是：`type` = 食衣住行這種大分類，`name` = 大分類底下使用者自訂的細項名稱。

**重要澄清：這只是使用慣例，不是資料庫層級強制的規則。**
- `app/schemas/category.py` 裡 `type: str` 就是一個普通字串欄位，沒有 enum、沒有檢查值域。
- `category_service.py` 完全沒有針對 `type` 做任何驗證邏輯，建立/更新都是直接把使用者傳進來的值原封不動存進去。
- 所以「`type` 該填食衣住行、`name` 該填細項」目前只存在於欄位命名和註解裡，程式不會擋下使用者填反或亂填。

**跟 `Transaction.transaction_type` 是兩個完全不同的概念，切勿混淆：**
- `Category.type` 描述的是「這筆支出/收入屬於哪個生活領域」（食衣住行），是分類學意義上的「領域」。
- `Transaction.transaction_type` 描述的是「這筆錢的方向」，值只會是 `income` 或 `expense`，管的是現金流方向，跟領域完全無關。
- `TIER1_EXPANSION_PLAN.md` 原本 v3 版本規劃了另一個東西叫 `usage_type`（income/expense/both，掛在 Category 上，用來限制某分類只能配哪些 transaction_type）——**這個設計最終被否決、沒有採用**（見文件開頭 override 註記），原因是「股票」這種分類買是支出、賣是收入、股息是收入，同一個分類要橫跨三種方向，加 `usage_type` 只是徒增一個要維護的狀態、還要另外寫相容性驗證，最簡單的模型就是完全不綁定，方向只交給 `Transaction` 自己決定。**所以現在 `Category` 除了 `name`/`type` 這兩個純標籤欄位以外，不含任何跟收支方向有關的欄位或驗證。**

### `transactions`（`app/models/transaction.py`）

代表一筆實際發生的收入或支出。

| 欄位 | 用途 |
|---|---|
| `account_id` | 這筆錢從/進哪個帳戶 |
| `category_id` | 屬於哪個分類（可為 `null`，不強制分類） |
| `amount` | 金額，用該帳戶的 `currency` 計價（原始金額，不是換算後的） |
| `transaction_type` | `income` 或 `expense`——**這是唯一決定金流方向的欄位**，跟 `Category.type` 無關 |
| `exchange_rate_to_base` | 建立當下，該帳戶幣別換算成使用者 `base_currency` 的匯率快照 |
| `base_currency_amount` | 建立當下，換算成使用者 `base_currency` 後的金額快照（= `amount * exchange_rate_to_base`） |

**為什麼要「快照」匯率跟換算金額，而不是報表當下即時查匯率換算？** 因為如果報表即時換算，同一筆一月的交易，會因為三月的匯率變動而讓一月的報表金額跟著改變——這在財務報表上是不能接受的。快照後，报表只加總已經存好的 `base_currency_amount`，不管以後匯率怎麼變，历史報表金額永遠不變。

`report_service.py` 的 `get_monthly_summary`/`get_category_summary` 都是加總 `base_currency_amount`，**不是**加總原始 `amount`。

### `exchange_rates`（`app/models/exchange_rate.py`）

不是「快照」，是「快取」——存的是「某天、某兩種幣別之間的匯率」這個事實本身，來源是 Frankfurter API v2。

| 欄位 | 用途 |
|---|---|
| `base_currency` / `target_currency` / `as_of_date` | 三者合起來是唯一鍵（`UniqueConstraint`），代表「某天 A 幣換 B 幣的匯率」只會抓一次、存一次 |
| `rate` | 抓到的匯率值 |

`get_rate(db, base, target, as_of_date)` 的邏輯：同幣別直接回傳 `1.0`；否則先查這張表有沒有快取，沒有才呼叫 Frankfurter API 抓，抓回來後寫進這張表再回傳。**這張表本身跟「某一筆交易」沒有直接關聯**——它是全站共用的匯率快取，`Transaction`/`Transfer` 建立時去查它、把查到的值複製一份存到自己身上（快照），兩者是不同層次的東西。

### `transfers`（`app/models/transfer.py`，Phase 1c，**進行中，尚未完全完成**）

代表使用者自己兩個帳戶之間的資金移動（例如從「現金」轉一筆到「銀行」），**不是收入也不是支出**，不影響淨資產、不算進 `income`/`expense` 報表。

| 欄位 | 用途 |
|---|---|
| `source_account_id` / `destination_account_id` | 轉出/轉入帳戶，必須都屬於同一個 `user_id`，且**不可相同**（同帳戶轉帳在 service 層擋，用 `BadRequestException`，不是 DB constraint） |
| `source_amount` / `destination_amount` | 分開存兩個金額，而不是一個 `amount` + 事後推算的匯率。原因：`Account.currency` 目前是可變更的，如果只存一個 amount，之後帳戶幣別一改，這筆歷史轉帳的意義就會跟著失真。`destination_amount` 由服務層呼叫既有的 `get_rate()` 算出，**不會**出現在 `TransferCreate`（使用者不用/不能自己填這個值），只出現在 `TransferResponse` |
| （目前規劃**不加**匯率快照欄位） | 因為 `source_amount`/`destination_amount` 兩個具體金額已經隱含了當下的匯率關係，不需要額外存 `exchange_rate_to_base` |

**API 範圍刻意縮小，只有 `POST`（建立）+ `GET`（查詢/列表），沒有 `PUT`、沒有 `DELETE`。** 理由：比照真實金融機構的轉帳紀錄不可竄改/不可刪除的原則——要「修正」一筆轉帳，應該是再建立一筆反向轉帳去抵銷,而不是竄改或刪除歷史紀錄。這是刻意跟 `Transaction`（有支援 PUT/DELETE）不一致的設計決定。

**目前狀態**：`Transfer` model + migration 已經寫完、commit、push（`b5835d0`）。`app/schemas/transfer.py` 已建立檔案但內容還是空殼（`TransferCreate`/`TransferResponse` 兩個 class 都還沒填欄位）。`app/services/transfer_service.py`、`app/routers/transfers.py` 都還沒開始寫。

---

## 3. 容易混淆的名詞對照表

| 名詞 A | 名詞 B | 差異 |
|---|---|---|
| `Category.type`（食衣住行大分類） | `Category.name`（使用者自訂細項） | `type` 是領域分組，`name` 是這個領域底下的具體標籤。兩者都只是自由文字，程式不驗證值域 |
| `Category.type` | `Transaction.transaction_type` | 前者是「花費屬於哪個生活領域」，後者是「錢的方向（`income`/`expense`）」。完全不同維度，故意不互相綁定 |
| `Account.currency` | `User.base_currency` | 前者是某一個帳戶自己計價用的幣別（可能好幾個帳戶各自不同），後者是整個使用者唯一的「報表/記帳本位幣」，兩者不同時才需要換算 |
| `ExchangeRate`（快取表） | `Transaction.exchange_rate_to_base` / `Transfer` 的金額欄位（快照） | 前者是「某天兩幣別間匯率」這個事實的全站共用快取，會員/交易/轉帳建立時去查它；後者是查到之後複製一份存在該筆紀錄自己身上，之後永遠不變，不受快取表未來變化影響 |
| `Transaction` | `Transfer` | 前者是收入或支出，會改變淨資產，可掛 `category_id`；後者是資金在自己帳戶間移動，不影響淨資產，沒有分類，報表不計入 |

---

## 4. 目前完成度（對照 `TIER1_EXPANSION_PLAN.md`）

**已完成：**
- Phase 0（架構稽核）
- Phase 1a（貨幣基礎建設：`base_currency`、`exchange_rates`、匯率服務、幣別驗證、`Transaction` 快照欄位、報表改加總快照值）
- Phase 1（Category/Transaction 設計釐清，決定不採用 `usage_type`）

**進行中：**
- Phase 1c（Transfer）— model/migration 完成，schema/service/router 未完成

**尚未開始：**
- Phase 2 — Recurring Transaction（定期交易）model 與邏輯
- Phase 3 — 資料庫交易與冪等性（`recurring_transaction_runs`、唯一約束、rollback）
- Phase 4 — 排程（已決定技術方案：GitHub Actions scheduled workflow，尚未實作）
- Phase 5 — Budget/Alert（`budgets`、`notifications`、`budget_alert_events` 三張新表，目前完全不存在）
- Phase 6 — 完整測試與失敗路徑覆蓋
- Phase 7 — Observability（結構化 log、correlation id、metrics）
- Phase 8 — 文件（`docs/data-model.md`、`docs/transfer-flow.md` 等正式文件，這份 glossary 可以作為之後寫這些文件時的素材，但不是同一份東西）

**刻意排除、目前不做的範圍**（`TIER1_EXPANSION_PLAN.md` 結尾 Scope Boundary）：
股票價格 API、成本基礎計算、FIFO/LIFO、已實現/未實現損益、投資組合估值、券商串接、Kafka、Kubernetes、微服務、CQRS、事件溯源、即時/排程匯率更新、手動匯率覆寫介面。
