def test_register(client):
    response = client.post("/auth/register", json={
        "email": "user@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "user@example.com"

def test_register_duplicate_email(client):
    client.post("/auth/register", json={
        "email": "user@example.com",
        "password": "password123"
    })
    response = client.post("/auth/register", json={
        "email": "user@example.com",
        "password": "password123"
    })
    assert response.status_code == 409


def test_login(client):
    client.post("/auth/register", json={
        "email": "user@example.com",
        "password": "password123"
    })
    response = client.post("/auth/login", data={
        "username": "user@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials(client):
    response = client.post("/auth/login", data={
        "username": "worng@example.com",
        "password": "wrong"
    })
    assert response.status_code == 401
