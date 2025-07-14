import logging
import logging.config
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Dict, Union
from .user_management import (
    UserService,
    User,
    DuplicateUserError,
    UserNotFoundError,
)
from .models import HealthStatus, UserResponse, UserCreate, UserSetupPayload
from pathlib import Path

_CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", "config")
_LOGGING_CONFIG_PATH = os.path.join(_CONFIG_DIR, "logging.ini")

if os.path.exists(_LOGGING_CONFIG_PATH):
    logging.config.fileConfig(_LOGGING_CONFIG_PATH, disable_existing_loggers=False)
else:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.warning(
        f"Logging configuration file not found at {_LOGGING_CONFIG_PATH}. "
        "Using basicConfig."
    )

logger = logging.getLogger(__name__)

app = FastAPI(
    title="User Management Service API",
    description="API for managing users stored in the service.",
    version="0.1.0",
)


@app.exception_handler(DuplicateUserError)
async def duplicate_user_exception_handler(request, exc: DuplicateUserError):
    logger.warning(f"Duplicate user error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


@app.exception_handler(UserNotFoundError)
async def user_not_found_exception_handler(request, exc: UserNotFoundError):
    logger.warning(f"User not found error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(ValueError)
async def value_error_exception_handler(request, exc: ValueError):
    logger.warning(f"Validation failed: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": f"User validation failed: {exc}"},
    )

user_service_instance = UserService()
try:
    users_data_path = Path("data/users.json")
    if users_data_path.exists() and users_data_path.stat().st_size > 0:
        user_service_instance.load_users_from_json(str(users_data_path))
        logger.info("Preloaded users from data/users.json")
    else:
        logger.warning(
            "data/users.json is missing or empty, starting with empty user list."
        )
except FileNotFoundError:
    logger.warning("data/users.json not found, starting with empty user list.")
except Exception:
    logger.exception("Failed to preload users from data/users.json")


def get_user_service() -> UserService:
    return user_service_instance


if os.environ.get("TESTING") == "1":

    @app.post("/test/setup-users")
    def setup_users_endpoint(
        payload: UserSetupPayload, service: UserService = Depends(get_user_service)
    ) -> Dict[str, Union[str, int]]:
        logger.info("API_SETUP_USERS: Received request to batch set up users.")
        with service._lock:
            logger.debug("API_SETUP_USERS: Lock acquired. Clearing existing users.")
            loaded_count = 0
            skipped_count = 0
            for user_data in payload.users:
                try:
                    user = User(
                        id=user_data.id, name=user_data.name, email=user_data.email
                    )
                    service.users_list[user.id] = user
                    loaded_count += 1
                except (TypeError, ValueError) as e:
                    logger.warning(
                        "API_SETUP_USERS: Skipping invalid user data "
                        "during batch setup: %s - %s",
                        user_data.model_dump_json(), e,
                    )
                    skipped_count += 1
            logger.info(
                f"API_SETUP_USERS: Batch setup complete. Users loaded: {loaded_count}, "
                f"Skipped: {skipped_count}. Lock will be released."
            )
        return {"status": "users_set", "loaded": loaded_count, "skipped": skipped_count}

    @app.post("/test/clear-users")
    def clear_users(service: UserService = Depends(get_user_service)) -> Dict[str, str]:
        logger.info("API_CLEAR_USERS: Received request.")
        with service._lock:
            logger.debug("API_CLEAR_USERS: Lock acquired.")
            service.users_list.clear()
        logger.debug("API_CLEAR_USERS: Lock released.")
        logger.info("API_CLEAR_USERS: Request finished.")
        return {"status": "cleared"}


@app.get(
    "/health",
    response_model=HealthStatus,
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Ensure that service is running",
)
async def service_health_check() -> Dict[str, str]:
    """Returns HTTP_200_OK to ensure that service is successfuly running."""
    logger.info("Confirming that the service is running.")
    return {"status": "ok"}


@app.get(
    "/users", response_model=List[UserResponse], tags=["Users"], summary="Get all users"
)
async def get_all_users(service: UserService = Depends(get_user_service)) -> List[User]:
    """Retrieves a list of all users currently in the service."""
    logger.info("Received request to get all users.")
    with service._lock:
        users = list(service.users_list.values())
    return users


@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
    summary="Create a new user",
)
async def create_user(
    user_data: UserCreate, service: UserService = Depends(get_user_service)
) -> User:
    """Creates a new user with the provided ID, name, and email."""
    logger.info(f"Received request to create user with ID: {user_data.id}")
    user = User(id=user_data.id, name=user_data.name, email=user_data.email)
    logger.debug(
        f"User object created for ID {user_data.id}. "
        "About to call service.add_user."
    )
    service.add_user(user)
    logger.debug(f"service.add_user for ID {user_data.id} completed.")
    return user


@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"],
    summary="Get a specific user by ID",
)
async def get_user(
    user_id: int, service: UserService = Depends(get_user_service)
) -> User:
    """Retrieves the details of a specific user by their unique ID."""
    logger.info(f"Received request to get user with ID: {user_id}")
    with service._lock:
        user = service.users_list.get(user_id)
    logger.debug(f"User lookup result for ID {user_id}: {user}")
    if user is None:
        logger.warning(f"User with ID {user_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    logger.info(f"Returning user: {user}")
    return user


@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Users"],
    summary="Delete a user by ID",
)
async def delete_user(
    user_id: int, service: UserService = Depends(get_user_service)
) -> None:
    """Deletes a user with the specified ID."""
    logger.info(f"Received request to delete user with ID: {user_id}")
    service.remove_user_by_id(user_id)
    return None
