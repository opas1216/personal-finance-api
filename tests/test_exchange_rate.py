import pytest
from decimal import Decimal

@pytest.fixture
def create_twd_account(client, auth_headers):
    # create account
    account = client.post("/accounts/", json={
        "name": "測試帳戶",
        "type": "checking",
        "currency": "TWD"
    }, headers=auth_headers)

    assert account.status_code == 201, f"create_account fixture failed: {account.status_code} {account.text}"
    return account

@pytest.fixture
def create_jpy_account(client, auth_headers):
    # create account
    account = client.post("/accounts/", json={
        "name": "測試帳戶",
        "type": "checking",
        "currency": "JPY"
    }, headers=auth_headers)

    assert account.status_code == 201, f"create_account fixture failed: {account.status_code} {account.text}"
    return account

@pytest.fixture
def generate_transaction(client, auth_headers, create_account):
    account_id = create_account.json()["id"]
    # create transaction
    transaction = client.post("/transactions/", json={
        "account_id": account_id,
        "amount": "100.00",
        "transaction_type": "expense",
        "transaction_date": "2026-06-01"
    }, headers=auth_headers)
    return transaction


def test_same_currency_transaction(client, auth_headers, create_twd_account):
    # auth_headers default currency is TWD, so creating a transaction in TWD should have exchange_rate_to_base = 1.0
    # a currency of a transaction is based on the account's currency, so we need to create an account with TWD currency first

    account_id = create_twd_account.json()["id"]
    response = client.post("/transactions/", json={
        "account_id": account_id,
        "amount": "100.00",
        "transaction_type": "expense",
        "transaction_date": "2026-06-01"
    }, headers=auth_headers)

    assert response.status_code == 201
    assert Decimal(response.json()["amount"]) == Decimal("100.00")
    assert Decimal(response.json()["exchange_rate_to_base"]) == Decimal("1.00000000")
    assert Decimal(response.json()["base_currency_amount"]) == Decimal("100.00")


def test_different_currency_transaction(client, auth_headers, create_usd_account):
    # auth_headers default currency is TWD, so creating a transaction in USD should have exchange_rate_to_base != 1.0
    account_id = create_usd_account.json()["id"]
    response = client.post("/transactions/", json={
        "account_id": account_id,
        "amount": "100.00",
        "transaction_type": "expense",
        "transaction_date": "2026-06-01"
    }, headers=auth_headers)

    assert response.status_code == 201
    assert Decimal(response.json()["amount"]) == Decimal("100.00")
    assert Decimal(response.json()["exchange_rate_to_base"]) != Decimal("1.0")
    assert Decimal(response.json()["exchange_rate_to_base"]) == Decimal("30.5")
    assert Decimal(response.json()["base_currency_amount"]) == Decimal("100.00") * Decimal(response.json()["exchange_rate_to_base"])