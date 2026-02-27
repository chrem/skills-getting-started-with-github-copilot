import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module

# TestClient expects the FastAPI app instance
client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Arrange: preserve and restore the global activities dict between tests"""
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = original


def test_root_redirect():
    # Act
    response = client.get("/")
    # Assert
    assert response.status_code == 200
    # The redirect returns the index page content; ensure path ends with index.html when followed
    assert "/static/index.html" in str(response.url)


def test_get_activities_contains_known():
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_successful_signup():
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert email in app_module.activities[activity]["participants"]


def test_duplicate_signup_fails():
    # Arrange
    email = "michael@mergington.edu"  # already signed up
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 400


def test_signup_unknown_activity():
    # Arrange
    email = "someone@mergington.edu"
    activity = "Nonexistent"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 404


def test_remove_participant_success():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.delete(f"/activities/{activity}/participants?email={email}")
    # Assert
    assert response.status_code == 200
    assert email not in app_module.activities[activity]["participants"]


def test_remove_nonexistent_participant():
    # Arrange
    email = "nobody@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.delete(f"/activities/{activity}/participants?email={email}")
    # Assert
    assert response.status_code == 404
