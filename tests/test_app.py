import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app, follow_redirects=False)


def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 307  # RedirectResponse
    assert "/static/index.html" in response.headers["location"]


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data
    assert "participants" in data["Basketball Team"]
    assert "max_participants" in data["Basketball Team"]


def test_signup_success():
    # Use an activity with initial empty participants
    response = client.post("/activities/Basketball%20Team/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]

    # Verify added
    response2 = client.get("/activities")
    data = response2.json()
    assert "newstudent@mergington.edu" in data["Basketball Team"]["participants"]


def test_signup_already_signed_up():
    # First signup
    client.post("/activities/Soccer%20Club/signup?email=duplicate@mergington.edu")
    # Second signup
    response = client.post("/activities/Soccer%20Club/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]


def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent%20Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_unregister_success():
    # First signup
    client.post("/activities/Art%20Club/signup?email=removeme@mergington.edu")
    # Then unregister
    response = client.delete("/activities/Art%20Club/unregister?email=removeme@mergington.edu")
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]

    # Verify removed
    response2 = client.get("/activities")
    data = response2.json()
    assert "removeme@mergington.edu" not in data["Art Club"]["participants"]


def test_unregister_not_signed_up():
    response = client.delete("/activities/Debate%20Team/unregister?email=notsigned@mergington.edu")
    assert response.status_code == 400
    result = response.json()
    assert "not signed up" in result["detail"]


def test_unregister_activity_not_found():
    response = client.delete("/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]