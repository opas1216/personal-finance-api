def test_create_account(client, auth_headers):
    me = client.get("/auth/me", headers=auth_headers)
    my_id = me.json()["id"]

    response = client.post("/accounts/", json={
        "name": "測試帳戶_1",
        "type": "checking",
        "currency": "USD"
    }, headers=auth_headers)

    # 確認成功
    assert response.status_code == 201

    # 確認此筆資料真的有被存進去
    assert "id" in response.json()

    assert "user_id" in response.json()

    # 確認此筆新增的資料是被存入的正確的User底下
    assert response.json()["user_id"] == my_id

    assert "name" in response.json()
    assert "type" in response.json()
    assert "currency" in response.json()

def test_create_account_unauthenticated(client):
    response = client.post("/accounts/", json={
        "name": "測試帳戶_2",
        "type": "checking",
        "currency": "TWD"
    })

    assert response.status_code == 401


def test_create_account_missing_fields(client, auth_headers):
    response = client.post("/accounts/", json={
        "name": "測試帳戶_3",
    }, headers=auth_headers)

    assert response.status_code == 422


def test_create_account_ignores_client_user_id(client, auth_headers):
    me = client.get("/auth/me", headers=auth_headers)
    my_id = me.json()["id"]

    response = client.post("/accounts/", json={
        "user_id": 9999,
        "name": "測試帳戶_3",
        "type": "checking",
        "currency": "JPY"
    }, headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["user_id"] == my_id
    assert response.json()["user_id"] != 9999