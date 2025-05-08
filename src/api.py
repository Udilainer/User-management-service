import logging
import logging.config
import os
from fastapi import FastAPI, Depends, HTTPException, status
from typing import List
from .user_management import (
    UserService,
    User,
    DuplicateUserError,
)
from .models import UserResponse, UserCreate

_CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'config')
_LOGGING_CONFIG_PATH = os.path.join(_CONFIG_DIR, 'logging.ini')

if os.path.exists(_LOGGING_CONFIG_PATH):
    logging.config.fileConfig(_LOGGING_CONFIG_PATH, disable_existing_loggers=False)
else:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.warning(f"Logging configuration file not found at {_LOGGING_CONFIG_PATH}. Using basicConfig.")

logger = logging.getLogger(__name__)

app = FastAPI(
    title="User Management Service API",
    description="API for managing users stored in the service.",
    version="0.1.0"
)

user_service_instance = UserService()
try:
    user_service_instance.load_users_from_json("data/users.json")
    logger.info("Preloaded users from data/users.json")
except FileNotFoundError:
    logger.warning("data/users.json not found, starting with empty user list.")
except Exception as e:
    logger.exception(f"Failed to preload users: {e}")

def get_user_service() -> UserService:
    return user_service_instance

@app.get(
    "/users",
    response_model=List[UserResponse],
    tags=["Users"],
    summary="Get all users"
)
async def get_all_users(service: UserService = Depends(get_user_service)):
    """Retrieves a list of all users currently in the service."""
    logger.info("Received request to get all users")
    return list(service.users_list.values())

@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
    summary="Create a new user"
)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """Creates a new user with the provided ID, name, and email."""
    logger.info(f"Received request to create user with ID: {user_data.id}")
    
    try:
        user = User(id=user_data.id, name=user_data.name, email=user_data.email)
        service.add_user(user)
    except DuplicateUserError as e:
        logger.warning(f"Duplicate user error for ID {user_data.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except (TypeError, ValueError) as e:
        logger.warning(f"Validation failed for creating user ID {user_data.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"User validation failed: {e}"
        )
        
    return user

@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"],
    summary="Get a specific user by ID"
)
async def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    """Retrieves the details of a specific user by their unique ID."""
    logger.info(f"Received request to get user with ID: {user_id}")
    user = service.users_list.get(user_id)
    if user is None:
        logger.warning(f"User with ID {user_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user

@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Users"],
    summary="Delete a user by ID"
)
async def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    """Deletes a user with the specified ID."""
    logger.info(f"Received request to delete user with ID: {user_id}")
    try:
        service.remove_user_by_id(user_id)
        return None
    except ValueError as e:
        logger.warning(f"Attempt to delete non-existent user ID {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )