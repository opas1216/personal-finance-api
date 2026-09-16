def test_create_category(client, auth_headers, create_category):
    me = client.get("/auth/me", headers=auth_headers)
    my_id = me.json()["id"]
    category = create_category

    assert category.status_code == 201
    assert category.json()["user_id"] == my_id
    assert "name" in category.json()
    assert "type" in category.json()


def test_create_category_unauthenticated(client):
    test_data = {
        "name": "外送",
        "type": "餐飲"
    }

    response = client.post("/categories/", json=test_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_create_category_invalid_data(client, auth_headers):
    test_data = {
        "name": "",
        "type": "交通"
    }

    response = client.post("/categories/", json=test_data, headers=auth_headers)

    assert response.status_code == 422
    assert "name" in response.json()["detail"][0]["loc"]

def test_get_categories_by_id(client, auth_headers, create_category):
    create_response = create_category

    # 得到新建立的category id
    category_id = create_response.json()["id"]

    get_response = client.get(f"/categories/{category_id}", headers=auth_headers)


    assert get_response.status_code == 200
    assert get_response.json()["id"] == category_id


def test_get_category_missing_id(client, auth_headers, create_category):
    create_response = create_category
    category_id = "9999"

    response = client.get(f"/categories/{category_id}", headers=auth_headers)

    assert response.status_code == 404
    assert "detail" in response.json()



def test_get_categories_by_user_id(client, auth_headers, create_category):
    me = client.get("/auth/me", headers=auth_headers)
    my_id = me.json()["id"]

    create_response = create_category
    response = client.get("/categories/", headers=auth_headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["user_id"] == my_id


def test_get_categories_unauthenticated(client):
    response = client.get("/categories/")
    assert response.status_code == 401

