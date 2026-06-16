import uuid
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_get_activities_returns_valid_structure():
    # Arrange
    expected_keys = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert expected_keys.issubset(set(activities["Chess Club"].keys()))


def test_signup_and_remove_participant_uses_aaa_pattern():
    # Arrange
    activity_name = "Chess Club"
    email = f"test-user-{uuid.uuid4()}@mergington.edu"
    signup_url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    remove_url = f"/activities/{quote(activity_name)}/participants?email={quote(email)}"

    # Act - sign up a new participant
    signup_response = client.post(signup_url)

    # Assert - sign up succeeded
    assert signup_response.status_code == 200
    assert signup_response.json()["message"] == f"Signed up {email} for {activity_name}"

    # Act - verify the participant appears in the activity list
    get_response = client.get("/activities")

    # Assert - participant exists in the returned activity data
    assert get_response.status_code == 200
    participants = get_response.json()[activity_name]["participants"]
    assert email in participants

    # Act - remove the participant
    remove_response = client.delete(remove_url)

    # Assert - removal succeeded
    assert remove_response.status_code == 200
    assert remove_response.json()["message"] == f"Removed {email} from {activity_name}"

    # Act - verify the participant was removed
    final_response = client.get("/activities")

    # Assert - participant no longer exists
    assert final_response.status_code == 200
    final_participants = final_response.json()[activity_name]["participants"]
    assert email not in final_participants
