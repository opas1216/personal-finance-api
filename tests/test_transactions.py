import pytest
from decimal import Decimal

@pytest.fixture
def two_transactions(client, auth_headers):
    account_data = {"name": "測試帳戶", "type": "checking", "currency": "USD"}
    account_id = client.post("/accounts/", json=account_data, headers=auth_headers).json()["id"]

    category_data = {"name": "外送", "type": "食"}
    category_id = client.post("/categories/", json=category_data, headers=auth_headers).json()["id"]

    expense = client.post("/transactions/", json={
        "account_id": account_id,
        "category_id": category_id,
        "amount": 500.00,
        "transaction_type": "expense",
        "transaction_date": "2026-07-10",
        "description": "颱風天放假的早餐"
    }, headers=auth_headers)
    assert expense.status_code == 201

    income = client.post("/transactions/", json={
        "account_id": account_id, "category_id": category_id,
        "amount": 2700.00, "transaction_type": "income",
        "transaction_date": "2026-07-10", "description": "颱風天放假的薪資"
    }, headers=auth_headers)
    assert income.status_code == 201


def test_create_transaction(generate_expense_transaction):
    assert generate_expense_transaction.status_code == 201
    assert generate_expense_transaction.json()["amount"] == "500.00"

def test_get_transactions(client, auth_headers, generate_expense_transaction):
    account_id = generate_expense_transaction.json()["account_id"]
    response = client.get("/transactions/", headers=auth_headers)
    assert response.status_code == 200

    transactions = response.json()
    assert isinstance(transactions, list)
    assert len(transactions) >= 1
    assert any(Decimal(t["amount"]) == Decimal("500.00") and t["account_id"] == account_id for t in transactions)

def test_create_transaction_invalid_amount(client, auth_headers, create_usd_account):
    account_id = create_usd_account.json()["id"]

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