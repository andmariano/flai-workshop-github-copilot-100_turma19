"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {
        "Soccer Team": {
            "description": "Join the school soccer team for training and matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice basketball skills and compete in games",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in plays and learn acting techniques",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Workshop": {
            "description": "Explore painting, drawing, and sculpture",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["amelia@mergington.edu", "elijah@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Prepare for math competitions and solve challenging problems",
            "schedule": "Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["ethan@mergington.edu", "charlotte@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific topics",
            "schedule": "Wednesdays, 4:00 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["benjamin@mergington.edu", "grace@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    yield


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Soccer Team" in data
        assert "Basketball Club" in data
        assert "Drama Club" in data
        assert "Art Workshop" in data
        assert "Math Olympiad" in data
        assert "Science Club" in data
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_includes_participants(self, client):
        """Test that activities include participant information"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Soccer Team" in data
        assert "participants" in data["Soccer Team"]
        assert "lucas@mergington.edu" in data["Soccer Team"]["participants"]
        assert "mia@mergington.edu" in data["Soccer Team"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_existing_activity(self, client):
        """Test successful signup for an existing activity"""
        response = client.post(
            "/activities/Soccer Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed up test@mergington.edu for Soccer Team"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test@mergington.edu" in activities_data["Soccer Team"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_already_registered(self, client):
        """Test signing up for an activity already registered for"""
        email = "lucas@mergington.edu"
        response = client.post(
            f"/activities/Soccer Team/signup?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, client):
        """Test successfully unregistering an existing participant"""
        email = "lucas@mergington.edu"
        response = client.post(
            f"/activities/Soccer Team/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Unregistered {email} from Soccer Team"
        assert email not in data["participants"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Soccer Team"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistering from an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_nonexistent_participant(self, client):
        """Test unregistering a participant not in the activity"""
        response = client.post(
            "/activities/Soccer Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Participant not found in this activity"


class TestIntegrationScenarios:
    """Integration tests for complete user workflows"""
    
    def test_complete_signup_and_unregister_workflow(self, client):
        """Test a complete workflow of signing up and unregistering"""
        email = "newstudent@mergington.edu"
        activity = "Drama Club"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
        
        # Unregister
        unregister_response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        final_activities_response = client.get("/activities")
        final_activities_data = final_activities_response.json()
        assert email not in final_activities_data[activity]["participants"]
    
    def test_signup_for_multiple_activities(self, client):
        """Test signing up for multiple different activities"""
        email = "multisport@mergington.edu"
        activities_list = ["Soccer Team", "Basketball Club", "Chess Club"]
        
        for activity in activities_list:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all signups
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        for activity in activities_list:
            assert email in activities_data[activity]["participants"]
