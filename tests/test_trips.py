def test_create_trip(client, test_user):
    response = client.post("/trips", json={
        "destination": "Paris",
        "start_date": "2025-08-01",
        "end_date": "2025-08-10",
        "budget_per_person": 1500.00,
        "is_public": True
    }, headers=test_user["headers"])
    
    assert response.status_code == 200
    assert response.json()["destination"] == "Paris"
    assert response.json()["creator_id"] == test_user["id"]


def test_list_trips_only_own(client, test_user):
    # Create a trip as test_user
    client.post("/trips", json={
        "destination": "Paris",
        "start_date": "2025-08-01",
        "end_date": "2025-08-10",
        "budget_per_person": 1500.00,
        "is_public": True
    }, headers=test_user["headers"])

    # Create a second user
    client.post("/signup", json={"email": "other@example.com", "password": "password123"})
    other_login = client.post("/login", data={"username": "other@example.com", "password": "password123"})
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}

    # Second user's trip list should be empty
    response = client.get("/trips", headers=other_headers)
    assert response.json() == []


def test_private_trip_access_denied(client, test_user):
    # Create private trip
    trip = client.post("/trips", json={
        "destination": "Secret",
        "start_date": "2025-08-01",
        "end_date": "2025-08-10",
        "budget_per_person": 500.00,
        "is_public": False
    }, headers=test_user["headers"]).json()

    # Create another user and try to access it
    client.post("/signup", json={"email": "other@example.com", "password": "password123"})
    other_login = client.post("/login", data={"username": "other@example.com", "password": "password123"})
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}

    response = client.get(f"/trips/{trip['id']}", headers=other_headers)
    assert response.status_code == 403


def test_delete_trip(client, test_user):
    trip = client.post("/trips", json={
        "destination": "Paris",
        "start_date": "2025-08-01",
        "end_date": "2025-08-10",
        "budget_per_person": 1500.00,
        "is_public": True
    }, headers=test_user["headers"]).json()

    response = client.delete(f"/trips/{trip['id']}", headers=test_user["headers"])
    assert response.status_code == 200

    # Verify it's gone
    response = client.get(f"/trips/{trip['id']}", headers=test_user["headers"])
    assert response.status_code == 404