def test_create_transaction(client, auth_headers):
    # create account
    account = client.post("/accounts/", json={
        "user_id": 1,
        "name": "測試帳戶",
        "type": "checking",
        "currency": "TWD"
    }, headers=auth_headers)
    account_id = account.json()["id"]

    response = client.post("/transactions/", json={
        "account_id": account_id,
        "amount": "100.00",
        "transaction_type": "expense",
        "transaction_date": "2026-06-01"
    }, headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["amount"] == "100.00"

def test_get_transactions(client, auth_headers):
    response = client.get("/transactions/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_transaction_invalid_amount(client, auth_headers):
    account = client.post("/accounts/", json={
        "user_id": 1,
        "name": "測試帳戶",
        "type": "checking",
        "currency": "TWD"
    }, headers=auth_headers)
    account_id = account.json()["id"]

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