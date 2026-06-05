"""Tests for the activities API endpoints."""
import pytest


def test_root_redirect(client):
    """Test that GET / redirects to /static/index.html."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test that GET /activities returns a dict of activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert activities["Chess Club"]["description"]
    assert activities["Chess Club"]["schedule"]
    assert activities["Chess Club"]["max_participants"]
    assert isinstance(activities["Chess Club"]["participants"], list)


def test_signup_success(client):
    """Test that a student can sign up for an activity."""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    assert "newstudent@mergington.edu" in result["message"]

    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_unregister_success(client):
    """Test that a participant can be unregistered from an activity."""
    # First, sign up a student
    client.post(
        "/activities/Programming Class/signup",
        params={"email": "temp@mergington.edu"}
    )

    # Verify they're registered
    activities = client.get("/activities").json()
    assert "temp@mergington.edu" in activities["Programming Class"]["participants"]

    # Unregister the student
    response = client.delete(
        "/activities/Programming Class/unregister",
        params={"email": "temp@mergington.edu"}
    )
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]

    # Verify participant was removed
    activities = client.get("/activities").json()
    assert "temp@mergington.edu" not in activities["Programming Class"]["participants"]


def test_duplicate_signup_error(client):
    """Test that duplicate signup returns 400 error."""
    # First signup
    response1 = client.post(
        "/activities/Drama Club/signup",
        params={"email": "duplicate@mergington.edu"}
    )
    assert response1.status_code == 200

    # Attempt duplicate signup
    response2 = client.post(
        "/activities/Drama Club/signup",
        params={"email": "duplicate@mergington.edu"}
    )
    assert response2.status_code == 400
    result = response2.json()
    assert "already signed up" in result["detail"]
