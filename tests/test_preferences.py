def test_create_preference(client, test_user):
    response = client.post("/preferences", json={
        "user_id": 999,  # deliberately wrong — should be overwritten
        "preferred_climate": "tropical",
        "preferred_activities": ["hiking", "beach"],
        "max_budget": 2000.00,
        "travel_style": "adventure"
    }, headers=test_user["headers"])

    assert response.status_code == 200
    # user_id must be the authenticated user's ID, not 999
    assert response.json()["user_id"] == test_user["id"]
    # preferred_activities must come back as a list, not a string
    assert isinstance(response.json()["preferred_activities"], list)
    assert "hiking" in response.json()["preferred_activities"]