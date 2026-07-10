from decimal import Decimal
import pytest

@pytest.fixture
def two_transactions(client, auth_headers):
    account_data = {"name": "測試帳戶", "type": "checking", "currency": "TWD"}
    account_id = client.post("/accounts/", json=account_data, headers=auth_headers).json()["id"]

    category_data = {"name": "外送", "type": "食"}
    category_id = client.post("/categories/", json=category_data, headers=auth_headers).json()["id"]

    expense = client.post("/transactions/", json={
        "account_id": account_id, "category_id": category_id,
        "amount": 500.00, "transaction_type": "expense",
        "transaction_date": "2026-07-10", "description": "颱風天放假的早餐"
    }, headers=auth_headers)
    assert expense.status_code == 201

    income = client.post("/transactions/", json={
        "account_id": account_id, "category_id": category_id,
        "amount": 2700.00, "transaction_type": "income",
        "transaction_date": "2026-07-10", "description": "颱風天放假的薪資"
    }, headers=auth_headers)
    assert income.status_code == 201



def test_monthly_summary_success(client, auth_headers, two_transactions):
    year = 2026
    month = 7

    response = client.get("/reports/monthly", params={"year": year, "month": month}, headers=auth_headers)

    assert response.status_code == 200
    assert Decimal(response.json()["total_income"]) == Decimal("2700.00")
    assert Decimal(response.json()["total_expense"]) == Decimal("500.00")
    assert Decimal(response.json()["net"]) == Decimal("2200.00")


def test_monthly_summary_no_transactions(client, auth_headers):
    year = 2026
    month = 7

    response = client.get("/reports/monthly", params={"year": year, "month": month}, headers=auth_headers)

    assert response.status_code == 200
    assert Decimal(response.json()["total_income"]) == Decimal("0")
    assert Decimal(response.json()["total_expense"]) == Decimal("0")
    assert Decimal(response.json()["net"]) == Decimal("0")


def test_monthly_summary_unauthenticated(client):
    response = client.get("/reports/monthly")

    assert response.status_code == 401


def test_category_summary_success(client, auth_headers, two_transactions):
    year = 2026
    month = 7

    response = client.get("/reports/categories", params={"year": year, "month": month}, headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    by_type = {item["transaction_type"]: item for item in data}
    assert by_type["expense"]["category_name"] == "外送"
    assert Decimal(by_type["expense"]["total"]) == Decimal("500.00")

    assert by_type["income"]["category_name"] == "外送"
    assert Decimal(by_type["income"]["total"]) == Decimal("2700.00")

def test_category_summary_empty(client, auth_headers):
    year = 2026
    month = 7

    response = client.get("/reports/categories", params={"year": year, "month": month}, headers=auth_headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0

def test_category_summary_unauthenticated(client):
    response = client.get("/reports/categories")
    assert response.status_code == 401