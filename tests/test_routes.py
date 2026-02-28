"""
Tests for the FastAPI endpoints.
Uses the Arrange-Act-Assert (AAA) pattern for clarity.
"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_200_and_json(self, client, reset_activities):
        """
        Arrange: client is ready
        Act: GET /activities
        Assert: response is 200 and contains a dict of activities
        """
        # Arrange
        # (client fixture is already set up)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success_adds_participant(self, client, reset_activities):
        """
        Arrange: activity exists with available spots
        Act: POST signup with new email
        Assert: response is 200 and participant is added
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Verify precondition: email not yet signed up
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        assert email not in initial_participants

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        assert email in updated_participants

    def test_signup_duplicate_email_returns_400(self, client, reset_activities):
        """
        Arrange: student already signed up for activity
        Act: POST signup with same email
        Assert: response is 400 with appropriate error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_activity_full_returns_400(self, client, reset_activities):
        """
        Arrange: activity is at max capacity
        Act: POST signup when activity is full
        Assert: response is 400 with appropriate error
        """
        # Arrange
        # Find an activity and fill it up
        activity_name = "Basketball Team"
        new_email = "overfill@mergington.edu"
        
        # Get current state and calculate slots needed to fill
        activities_response = client.get("/activities")
        activity = activities_response.json()[activity_name]
        current_count = len(activity["participants"])
        max_count = activity["max_participants"]
        slots_remaining = max_count - current_count
        
        # Fill remaining slots
        for i in range(slots_remaining):
            fill_email = f"filler{i}@mergington.edu"
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": fill_email}
            )

        # Act: try to signup when full
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )

        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Arrange: activity name does not exist
        Act: POST signup to non-existent activity
        Assert: response is 404
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""

    def test_unregister_success_removes_participant(self, client, reset_activities):
        """
        Arrange: student is signed up for activity
        Act: DELETE participant from activity
        Assert: response is 200 and participant is removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # already a participant
        
        initial_response = client.get("/activities")
        assert email in initial_response.json()[activity_name]["participants"]

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify participant was removed
        updated_response = client.get("/activities")
        assert email not in updated_response.json()[activity_name]["participants"]

    def test_unregister_nonexistent_participant_returns_404(self, client, reset_activities):
        """
        Arrange: student is not signed up for activity
        Act: DELETE non-existent participant
        Assert: response is 404
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notasignup@mergington.edu"
        
        initial_response = client.get("/activities")
        assert email not in initial_response.json()[activity_name]["participants"]

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Arrange: activity does not exist
        Act: DELETE from non-existent activity
        Assert: response is 404
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
