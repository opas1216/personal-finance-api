import pytest
from decimal import Decimal


def test_create_transfer(client, auth_headers, create_accounts):
    # me = client.get("/auth/me", headers=auth_headers)
    # my_id = me.json()["id"]
    accounts = create_accounts
    source_account = accounts["TWD"]
    destination_account = accounts["JPY"]

    transfer = client.post("/transfers/", json={
        "source_account_id": source_account.json()["id"],
        "destination_account_id": destination_account.json()["id"],
        "source_amount": "100.00",
        "transfer_date": "2026-09-03",
        "description": "測試轉帳"
    }, headers=auth_headers)

    assert transfer.status_code == 201, f"create transfer failed: {transfer.json()}"
