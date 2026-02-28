"""
Pytest configuration and shared fixtures for API tests.
"""
import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app
import src.app


@pytest.fixture
def client():
    """Provide a TestClient connected to the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Snapshot the initial activities state before each test,
    and restore it after to ensure test isolation.
    """
    # Arrange: save the initial state
    original_activities = copy.deepcopy(src.app.activities)
    yield
    # Cleanup: restore the original state
    src.app.activities.clear()
    src.app.activities.update(original_activities)
