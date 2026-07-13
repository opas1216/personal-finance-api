import pytest
from decimal import Decimal

@pytest.fixture
def create_account(client, auth_headers):
    # create account
    account = client.post("/accounts/", json={
        "name": "測試帳戶",
        "type": "checking",
        "currency": "TWD"
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


def test_create_transaction(generate_transaction):
    assert generate_transaction.status_code == 201
    assert generate_transaction.json()["amount"] == "100.00"

def test_get_transactions(client, auth_headers, generate_transaction):
    account_id = generate_transaction.json()["account_id"]
    response = client.get("/transactions/", headers=auth_headers)
    assert response.status_code == 200

    transactions = response.json()
    assert isinstance(transactions, list)
    assert len(transactions) >= 1
    assert any(Decimal(t["amount"]) == Decimal("100.00") and t["account_id"] == account_id for t in transactions)

def test_create_transaction_invalid_amount(client, auth_headers, create_account):
    account_id = create_account.json()["id"]

    response = client.post("/transactions/", json={
        "account_id": account_id,
        "amount": "-50.00",
        "transaction_type": "expense",
        "transaction_date": "2026-06-01"
    }, headers=auth_headers)
    assert response.status_code == 422


def test_create_transaction_unauthenticated(client):
    response = client.post("/transactions/", json={
        "account_id": 1,
        "amount": "100.00",
        "transaction_type": "expense",
        "transaction_date": "2026-06-01"
    })
    assert response.status_code == 401