import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client():
    return TestClient(app_module.app)


@pytest.fixture
def reset_activities():
    original = {
        name: {
            **details,
            "participants": list(details["participants"]),
        }
        for name, details in app_module.activities.items()
    }

    app_module.activities.clear()
    app_module.activities.update(original)
    yield
    app_module.activities.clear()
    app_module.activities.update(original)


def test_signup_adds_student_to_activity(client, reset_activities):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/Science Club/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in app_module.activities["Science Club"]["participants"]
    assert response.json()["message"] == f"Signed up {email} for Science Club"


def test_duplicate_signup_returns_400(client, reset_activities):
    # Arrange
    email = "student@mergington.edu"
    app_module.activities["Science Club"]["participants"].append(email)

    # Act
    response = client.post(f"/activities/Science Club/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unknown_activity_returns_404(client, reset_activities):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/Unknown Activity/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_full_activity_returns_400(client, reset_activities):
    # Arrange
    activity = app_module.activities["Science Club"]
    activity["participants"] = [f"student{i}@mergington.edu" for i in range(activity["max_participants"])]

    # Act
    response = client.post("/activities/Science Club/signup?email=another@mergington.edu")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_unregister_removes_student_from_activity(client, reset_activities):
    # Arrange
    email = "student@mergington.edu"
    app_module.activities["Science Club"]["participants"].append(email)

    # Act
    response = client.delete(f"/activities/Science Club/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email not in app_module.activities["Science Club"]["participants"]
    assert response.json()["message"] == f"Removed {email} from Science Club"


def test_unregister_missing_student_returns_404(client, reset_activities):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/Science Club/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
