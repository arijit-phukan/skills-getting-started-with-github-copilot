"""
Test suite for Mergington High School Activities API.
Uses AAA (Arrange-Act-Assert) pattern for clear test structure.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        # Arrange - no setup needed, activities are pre-populated by fixture
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Art Society" in data
        assert len(data) == 3

    def test_get_activities_includes_activity_details(self, client, reset_activities):
        # Arrange
        
        # Act
        response = client.get("/activities")
        
        # Assert
        data = response.json()
        chess_club = data["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_includes_participants(self, client, reset_activities):
        # Arrange
        
        # Act
        response = client.get("/activities")
        
        # Assert
        data = response.json()
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
        assert "emma@mergington.edu" in data["Programming Class"]["participants"]
        assert data["Art Society"]["participants"] == []


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client, reset_activities):
        # Arrange
        activity_name = "Art Society"
        email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_adds_participant_to_existing_list(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "newplayer@mergington.edu"
        existing_participants = activities[activity_name]["participants"].copy()
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        updated_participants = activities[activity_name]["participants"]
        assert email in updated_participants
        assert all(p in updated_participants for p in existing_participants)

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_signup_returns_400(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_prevents_duplicate_participant(self, client, reset_activities):
        # Arrange
        activity_name = "Art Society"
        email = "student@mergington.edu"
        
        # Act - Sign up once successfully
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Try to sign up again
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response2.status_code == 400
        assert activities[activity_name]["participants"].count(email) == 1


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_successful(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_removes_only_specified_participant(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        other_email = "daniel@mergington.edu"
        
        # Act
        client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )
        
        # Assert
        assert email_to_remove not in activities[activity_name]["participants"]
        assert other_email in activities[activity_name]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_nonparticipant_returns_400(self, client, reset_activities):
        # Arrange
        activity_name = "Art Society"
        email = "notregistered@mergington.edu"  # Not signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_unregister_prevents_duplicate_removal(self, client, reset_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act - Remove once successfully
        response1 = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Try to remove again
        response2 = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response2.status_code == 400


class TestSignupUnregisterFlow:
    """Integration tests for signup and unregister workflows."""

    def test_signup_then_unregister_flow(self, client, reset_activities):
        # Arrange
        activity_name = "Art Society"
        email = "newstudent@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert signup
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]
        
        # Act - Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert unregister
        assert unregister_response.status_code == 200
        assert email not in activities[activity_name]["participants"]

    def test_multiple_signups_and_unregisters(self, client, reset_activities):
        # Arrange
        activity_name = "Art Society"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        # Act - Sign up all students
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert all signed up
        assert all(email in activities[activity_name]["participants"] for email in emails)
        assert len(activities[activity_name]["participants"]) == 3
        
        # Act - Unregister middle student
        client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": emails[1]}
        )
        
        # Assert middle student removed, others remain
        assert emails[0] in activities[activity_name]["participants"]
        assert emails[1] not in activities[activity_name]["participants"]
        assert emails[2] in activities[activity_name]["participants"]
