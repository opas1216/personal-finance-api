import pytest
from decimal import Decimal

@pytest.fixture
def create_transfer(client, auth_headers, create_accounts):
    accounts = create_accounts
    source_account = accounts["USD"]
    destination_account = accounts["JPY"]

    transfer = client.post("/transfers/", json={
        "source_account_id": source_account.json()["id"],
        "destination_account_id": destination_account.json()["id"],
        "source_amount": "100.00",
        "transfer_date": "2026-09-03",
        "description": "測試轉帳"
    }, headers=auth_headers)
    assert transfer.status_code == 201, f"create transfer failed: {transfer.json()}"

    return transfer


def test_create_transfer(client, auth_headers, create_transfer):
    data = create_transfer.json()

    assert create_transfer.status_code == 201
    assert "id" in data
    assert Decimal(data["source_amount"]) == Decimal("100.00")
    assert Decimal(data["destination_amount"]) == Decimal("100.00") * Decimal("110.0")
    assert data["description"] == "測試轉帳"



# def test_transfer_excluded_from_monthly_report(client, auth_headers, create_transfer):
