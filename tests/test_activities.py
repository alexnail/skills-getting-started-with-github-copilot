"""
Integration tests for activity endpoints.
Tests GET /activities, POST signup, and DELETE unregister operations.
"""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary of activities"""
        response = client.get("/activities")
        data = response.json()
        
        assert isinstance(data, dict)
        assert len(data) > 0
    
    def test_get_activities_contains_all_activities(self, client):
        """Test that all expected activities are returned"""
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball",
            "Swimming Club", "Drama Club", "Visual Arts", "Debate Team", "Science Club"
        ]
        
        response = client.get("/activities")
        data = response.json()
        
        for activity in expected_activities:
            assert activity in data
    
    def test_get_activities_structure(self, client):
        """Test that each activity has the required fields"""
        response = client.get("/activities")
        data = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, f"Activity {activity_name} missing field {field}"
    
    def test_get_activities_field_types(self, client):
        """Test that activity fields have the correct data types"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_participants_are_strings(self, client):
        """Test that all participants in the list are email strings"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        response = client.post("/activities/Basketball/signup", params={"email": "newstudent@mergington.edu"})
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Basketball" in data["message"]
    
    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant to the activity"""
        email = "testuser@mergington.edu"
        client.post("/activities/Basketball/signup", params={"email": email})
        
        response = client.get("/activities")
        data = response.json()
        
        assert email in data["Basketball"]["participants"]
    
    def test_signup_nonexistent_activity_404(self, client):
        """Test that signing up for non-existent activity returns 404"""
        response = client.post("/activities/NonExistentClub/signup", params={"email": "student@mergington.edu"})
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_signup_duplicate_email_400(self, client):
        """Test that duplicate signup (same email) returns 400 error"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post("/activities/Chess Club/signup", params={"email": email})
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already" in data["detail"].lower()
    
    def test_signup_missing_email_parameter_422(self, client):
        """Test that missing email query parameter returns 422 validation error"""
        response = client.post("/activities/Basketball/signup")
        
        assert response.status_code == 422
    
    def test_signup_multiple_students_same_activity(self, client):
        """Test that multiple different students can sign up for the same activity"""
        activity = "Swimming Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        response1 = client.post(f"/activities/{activity}/signup", params={"email": email1})
        response2 = client.post(f"/activities/{activity}/signup", params={"email": email2})
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        response = client.get("/activities")
        data = response.json()
        
        assert email1 in data[activity]["participants"]
        assert email2 in data[activity]["participants"]
    
    def test_signup_response_message_format(self, client):
        """Test that signup response message has the expected format"""
        email = "newuser@mergington.edu"
        response = client.post("/activities/Drama Club/signup", params={"email": email})
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Drama Club" in data["message"]
        assert "Signed up" in data["message"] or "signed up" in data["message"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client):
        """Test successful unregister from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.delete("/activities/Chess Club/unregister", params={"email": email})
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        email = "daniel@mergington.edu"  # Already in Chess Club
        client.delete("/activities/Chess Club/unregister", params={"email": email})
        
        response = client.get("/activities")
        data = response.json()
        
        assert email not in data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity_404(self, client):
        """Test that unregistering from non-existent activity returns 404"""
        response = client.delete("/activities/NonExistentClub/unregister", params={"email": "student@mergington.edu"})
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_unregister_student_not_registered_400(self, client):
        """Test that unregistering a student not in the activity returns 400"""
        email = "notregistered@mergington.edu"
        response = client.delete("/activities/Chess Club/unregister", params={"email": email})
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_missing_email_parameter_422(self, client):
        """Test that missing email query parameter returns 422 validation error"""
        response = client.delete("/activities/Chess Club/unregister")
        
        assert response.status_code == 422
    
    def test_unregister_multiple_participants(self, client):
        """Test that unregistering one participant doesn't affect others"""
        activity = "Programming Class"
        remaining_email = "emma@mergington.edu"
        removed_email = "sophia@mergington.edu"
        
        response = client.delete(f"/activities/{activity}/unregister", params={"email": removed_email})
        assert response.status_code == 200
        
        response = client.get("/activities")
        data = response.json()
        
        assert removed_email not in data[activity]["participants"]
        assert remaining_email in data[activity]["participants"]
    
    def test_unregister_response_message_format(self, client):
        """Test that unregister response message has the expected format"""
        email = "michael@mergington.edu"
        response = client.delete("/activities/Chess Club/unregister", params={"email": email})
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]
        assert "Unregistered" in data["message"] or "unregistered" in data["message"]
    
    def test_signup_then_unregister_flow(self, client):
        """Test complete signup and unregister flow"""
        activity = "Debate Team"
        email = "flowtest@mergington.edu"
        
        # Verify not registered initially
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert signup_response.status_code == 200
        
        # Verify signed up
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
        assert unregister_response.status_code == 200
        
        # Verify unregistered
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
