def test_signup_success(client):
    response = client.post("/signup", json={
        "email": "user@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"
    assert "password" not in response.json()  # password must never be returned


def test_signup_duplicate_email(client):
    client.post("/signup", json={"email": "user@example.com", "password": "password123"})
    response = client.post("/signup", json={"email": "user@example.com", "password": "password123"})
    assert response.status_code == 400


def test_login_success(client):
    client.post("/signup", json={"email": "user@example.com", "password": "password123"})
    response = client.post("/login", data={"username": "user@example.com", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/signup", json={"email": "user@example.com", "password": "password123"})
    response = client.post("/login", data={"username": "user@example.com", "password": "wrongpassword"})
    assert response.status_code == 401


def test_protected_route_without_token(client):
    response = client.get("/trips")
    assert response.status_code == 401