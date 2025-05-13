import pytest
import logging
import allure
import requests
import json
from src.user_management import User, DuplicateUserError

logger = logging.getLogger(__name__)

def test_api_health_check(api_service):
    """Tests that the API health check endpoint is responsive."""
    health_url = f"{api_service}/health"
    logger.debug(f"Attempting health check at: {health_url}")
    response = requests.get(health_url)
    
    logger.debug(f"Health check response status: {response.status_code}")
    logger.debug(f"Health check response JSON: {response.json()}")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_user_success(api_service):
    """Tests that creating a users via POST /users is successful."""
    users_url = f"{api_service}/users"
    user = User(251, "Van Jordan", "vanjordan912@example.com")
    logger.debug(f"Attempting POST /users check at: {users_url}")
    response = requests.post(users_url, user.__dict__)
    
    logger.debug(f"Post check response status: {response.status_code}")
    logger.debug(f"Post check response JSON: {response.json()}")
    assert response.status_code == 201
    assert response.json() == user.__dict__
    
def test_create_user_duplicate_id(api_service):
    """Tests that creating an existent user via GET /users raises DuplicateUserError."""
    users_url = f"{api_service}/users"
    user = User(462, "Feng Li", "fengli0133@example.com")
    logger.debug(f"Adding user via POST /users at: {users_url}")
    requests.post(users_url, user)
    
    logger.debug(f"Attempting to add an existent user via POST /users.")
    with pytest.raises(DuplicateUserError):
        response = requests.post(users_url, user.__dict__)
    
    logger.debug(f"Post existen user response status: {response.status_code}")
    logger.debug(f"Post existen user response JSON: {response.json()}")
    assert response.status_code == 409
    assert response.json() == user.__dict__