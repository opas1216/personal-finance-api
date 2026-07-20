from datetime import date

import httpx
from sqlalchemy import Date
from sqlalchemy.orm import Session
from decimal import Decimal
from app.exceptions import ExternalServiceException




def get_rate(db: Session, base_currency: str, target_currency: str, as_of_date: date) -> Decimal:
    """
    取得 base_currency -> target_currency 在 as_of_date 當天的匯率。

    Cache miss 時會一次向 Frankfurter 抓取 base_currency 對所有支援貨幣的匯率，
    並整批寫入 exchange_rates 快取（不只寫入這次要的這一組），以降低同一天內
    其他貨幣對的重複 API 呼叫。呼叫端只需要關心回傳值，但要知道這個函式在
    cache miss 時會連帶寫入多筆快取資料。
    """

    if base_currency == target_currency:
        return Decimal("1.0")

    rates_response = _fetch_rates_from_frankfurter(base_currency, as_of_date)

    _cache_rates(db, base_currency, as_of_date, rates_response)




    return rate


def _fetch_rates_from_frankfurter(base_currency: str, as_of_date: date) -> list[dict]:
    """
    向 Frankfurter API 抓取 base_currency 對所有支援貨幣的匯率。
    回傳格式為 [{"date":, "base":, "quote":, "rate":, ...}]。
    """

    try:
        response = httpx.get("https://api.frankfurter.dev/v2/rates", params={"base": base_currency, "date": as_of_date.isoformat()})
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        raise ExternalServiceException(f"Frankfurter API call failed: {e}")



def _cache_rates(db: Session, base_currency: str, as_of_date: date, rates: list[dict]) -> None:
    """
    將 Frankfurter API 回傳的匯率資料整批寫入 exchange_rates 快取。
    """

    # Frankfurter return like {"date":"2026-07-01","base":"USD","quote":"JPY","rate":162.61}
    for quote_currency, rate in rates.items():
        if quote_currency == base_currency:
            continue  # 跳過 base_currency -> base_currency 的匯率

        db.add(ExchangeRate(
            base_currency=base_currency,
            target_currency=quote_currency,
            rate=Decimal(rate),
            as_of_date=as_of_date
        ))

    db.commit()

