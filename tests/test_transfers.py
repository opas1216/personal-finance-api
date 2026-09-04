import pytest
from decimal import Decimal
from app.models import Transfer
from app.exceptions import ExternalServiceException
from app.services import transfer_service


@pytest.fixture
def create_transfer(client, auth_headers, create_accounts):
    accounts = create_accounts
    source_account = accounts["USD"]
    destination_account = accounts["JPY"]

    transfer = client.post("/transfers/", json={
        "source_account_id": source_account.json()["id"],
        "destination_account_id": destination_account.json()["id"],
        "source_amount": "100.00",
        "transfer_date": "2026-06-01",
        "description": "測試轉帳"
    }, headers=auth_headers)
    assert transfer.status_code == 201, f"create transfer failed: {transfer.json()}"

    return transfer


def test_create_transfer(client, auth_headers, create_transfer):
    data = create_transfer.json()

    assert create_transfer.status_code == 201
    assert Decimal(data["destination_amount"]) == Decimal("100.00") * Decimal("110.0")
    assert data["description"] == "測試轉帳"



def test_transfer_excluded_from_monthly_report(client, auth_headers, generate_transactions, create_transfer):
    transactions = generate_transactions
    transfer = create_transfer

    # Get monthly report for June 2026
    date = transactions["expense"].json()["transaction_date"]
    year = date[:4]
    month = date[5:7]

    report = client.get("/reports/monthly", params={"year": year, "month": month}, headers=auth_headers)

    assert report.status_code == 200
    assert Decimal(report.json()["total_income"]) == Decimal("2700.00") * Decimal("30.5")
    assert Decimal(report.json()["total_expense"]) == Decimal("500.00") * Decimal("30.5")
    assert Decimal(report.json()["net"]) == Decimal("2200.00") * Decimal("30.5")


def test_same_account_transfer(client, auth_headers, create_accounts):
    usd_account = create_accounts["USD"]
    jpy_account = create_accounts["JPY"]

    transfer = client.post("/transfers/", json={
        "source_account_id": usd_account.json()["id"],
        "destination_account_id": usd_account.json()["id"],
        "source_amount": "100.00",
        "transfer_date": "2026-06-01",
        "description": "測試轉帳"
    }, headers=auth_headers)

    assert transfer.status_code == 400


def test_transfer_rollback_on_exchange_rate_failure(client, auth_headers, db, create_accounts, monkeypatch):
    def fake_get_rate(*args, **kwargs):
        raise ExternalServiceException("模擬 Frankfurter API 掛掉")

    monkeypatch.setattr(transfer_service, "get_rate", fake_get_rate)

    usd = create_accounts["USD"]
    jpy = create_accounts["JPY"]

    response = client.post("/transfers/", json={
        "source_account_id": usd.json()["id"],
        "destination_account_id": jpy.json()["id"],
        "source_amount": "100.00",
        "transfer_date": "2026-06-01"
    }, headers=auth_headers)

    assert response.status_code == 502
    assert db.query(Transfer).count() == 0


