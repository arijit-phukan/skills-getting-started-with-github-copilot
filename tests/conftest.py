"""
Pytest configuration and fixtures for the Mergington High School API tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture providing a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Fixture to reset activities to a clean state before each test.
    This ensures tests don't interfere with each other.
    """
    original_activities = {
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
            "participants": ["emma@mergington.edu"]
        },
        "Art Society": {
            "description": "Drawing, painting, and gallery visits for budding artists",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        }
    }
    
    # Clear and repopulate activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)
