import logging
import requests
import allure
import pytest
from typing import Tuple, Dict, Any, Callable
from utils import delete_user_if_exists, load_schema

logger = logging.getLogger(__name__)


@allure.feature("API")
@allure.story("API Health Check")
@allure.severity(allure.severity_level.BLOCKER)
@allure.title("Verify API health check endpoint is responsive")
# fmt: off
@allure.description("""This test verifies that API health check endpoint is responsive and it's ready to work via a GET request to /health.""")  # noqa: E501
# fmt: on
def test_api_health_check(api_service: str) -> None:
    """Tests that the API health check endpoint is responsive."""
    health_url = f"{api_service}/health"
    logger.debug(f"Attempting health check at: {health_url}")
    response: requests.Response = requests.get(health_url, timeout=10)

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }, "Health check response should be {'status': 'ok'}"


# --- POST /users tests ---


@allure.feature("API")
@allure.story("API User Creation")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Verify successful user creation with valid payload")
# fmt: off
@allure.description("""This test verifies that a user creation via a POST request to /users with valid payload is successful.""")  # noqa: E501
# fmt: on
def test_create_user_success(
    api_service: str, validator_factory: Callable[[dict], Any]
) -> None:
    """Tests that creating a user via POST `/users` is successful."""
    users_url = f"{api_service}/users"
    user_schema: Dict[str, Any] = load_schema("user_schema.json")
    user_data = {"id": 251, "name": "Van Jordan", "email": "vanjordan912@example.com"}
    created_test_user_id = None
    try:
        logger.debug(f"Attempting POST /users check at: {users_url}")
        response: requests.Response = requests.post(
            users_url, json=user_data, timeout=20
        )
        response_json: Dict[str, Any] = response.json()

        assert response.status_code == 201
        logger.debug("Successfully asserted user creation.")

        validator_instance = validator_factory(user_schema)
        validator_instance.validate(response_json)
        logger.debug("Successfully validated response against user_schema.json.")

        assert (
            response_json["id"] == user_data["id"]
        ), f"Expected user ID {user_data['id']}, but got {response_json['id']}"
        assert (
            response_json["name"] == user_data["name"]
        ), f"Expected user name {user_data['name']}, but got {response_json['name']}"
        assert response_json["email"] == user_data["email"], (
            f"Expected user email {user_data['email']}, "
            f"but got {response_json['email']}"
        )

        created_test_user_id = response_json["id"]
    finally:
        if created_test_user_id:
            delete_user_if_exists(api_service, created_test_user_id)


@allure.feature("API")
@allure.story("API User Creation")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Verify user creation fails for an existing ID")
# fmt: off
@allure.description("""This test verifies that a user creation via a POST request to /users with existent user ID failed correctly.""")  # noqa: E501
# fmt: on
def test_create_user_duplicate_id(
    api_service: str, created_test_user: Dict[str, Any]
) -> None:
    """
    Tests that creating a user with an existing ID via POST `/users` raises HTTP 409.
    """
    users_url = f"{api_service}/users"
    created_test_user_data: Dict[str, Any] = created_test_user

    logger.debug("Attempting to add an existent user via POST /users.")
    response: requests.Response = requests.post(
        users_url, json=created_test_user_data, timeout=20
    )
    logger.debug(f"Post existent user response JSON: {response.json()}")

    assert response.status_code == 409
    logger.debug("Successfully asserted user creation failure.")

    assert (
        response.json().get("detail")
        == f"User with ID {created_test_user['id']} already exists."
    ), (
        "Expected error message for duplicate ID not found: "
        f"{response.json().get('detail')}"
    )


@allure.feature("API")
@allure.story("API User Creation")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Verify user creation fails for invalid payloads")
# fmt: off
@allure.description("""This test verifies that a user creation via a POST request to /users with various invalid payloads fails correctly with a 422 Unprocessable Entity status.""")  # noqa: E501
# fmt: on
@pytest.mark.parametrize(
    "invalid_payload, error_loc, error_msg",
    [
        (
            {"name": "Test Name", "email": "test@example.com"},
            ("body", "id"),
            "Field required",
        ),  # missing id
        (
            {"id": 101, "email": "test@example.com"},
            ("body", "name"),
            "Field required",
        ),  # missing name
        (
            {"id": 102, "name": "Test Name"},
            ("body", "email"),
            "Field required",
        ),  # missing email
        (
            {"id": "one", "name": "Test Name", "email": "test@example.com"},
            ("body", "id"),
            "Input should be a valid integer",
        ),  # id as string
        (
            {"id": 1.5, "name": "Test Name", "email": "test@example.com"},
            ("body", "id"),
            "Input should be a valid integer",
        ),  # id as float
        (
            {"id": True, "name": "Test Name", "email": "test@example.com"},
            ("body", "id"),
            "ID cannot be a boolean value. Please provide an integer.",
        ),  # id as boolean
        (
            {"id": 104, "name": 123, "email": "test@example.com"},
            ("body", "name"),
            "Input should be a valid string",
        ),  # name as int
        (
            {"id": 105, "name": True, "email": "test@example.com"},
            ("body", "name"),
            "Input should be a valid string",
        ),  # name as boolean
        (
            {"id": 106, "name": "", "email": "test@example.com"},
            ("body", "name"),
            "String should have at least 3 character",
        ),  # Empty name
        (
            {"id": 107, "name": None, "email": "test@example.com"},
            ("body", "name"),
            "Input should be a valid string",
        ),  # Null name
        (
            {"id": 108, "name": "Test Name", "email": None},
            ("body", "email"),
            "Input should be a valid string",
        ),  # Null email
        (
            "not a json",
            ("body",),
            "Input should be a valid dictionary or object",
        ),  # Raw string
        (123, ("body",), "Input should be a valid dictionary or object"),  # Integer
        ([], ("body",), "Input should be a valid dictionary or object"),  # Empty list
    ],
    ids=[
        "missing_id",
        "missing_name",
        "missing_email",
        "id_string",
        "id_float",
        "id_boolean",
        "name_int",
        "name_boolean",
        "empty_name",
        "name_Null",
        "email_Null",
        "payload_raw_string",
        "payload_integer",
        "payload_empty_list",
    ],
)
def test_create_user_invalid_payload(
    api_service: str,
    invalid_payload: Dict[str, Any],
    error_loc: Tuple[str, str],
    error_msg: str,
) -> None:
    """
    Tests that creating a user with invalid data via POST `/users` raises HTTP 422.
    """
    users_url = f"{api_service}/users"
    logger.debug(f"Attempting to add an invalid user via POST /users at: {users_url}")
    response: requests.Response = requests.post(
        users_url, json=invalid_payload, timeout=20
    )
    logger.debug(f"Post invalid user response JSON: {response.json()}")

    assert response.status_code == 422
    logger.debug("Successfully asserted user creation failure.")

    error_details = response.json().get("detail")
    expected_error_found = any(
        err.get("loc") == list(error_loc) and error_msg in err.get("msg")
        for err in error_details
    )

    assert expected_error_found, (
        f"Expected error for {error_loc} with message '{error_msg}' not found "
        f"not found in {error_details}"
    )


@allure.feature("API")
@allure.story("API User Creation")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Verify user creation fails for various invalid emails")
# fmt: off
@allure.description("""This test verifies that a user creation via a POST request to /users with various invalid emails fails correctly with a 422 Unprocessable Entity status.""")  # noqa: E501
# fmt: on
@pytest.mark.parametrize(
    "invalid_email_input, expected_error_loc, expected_error_msg_substring",
    [
        ("", ("body", "email"), "value is not a valid email address"),
        ("test @example.com", ("body", "email"), "value is not a valid email address"),
        ("@example.com", ("body", "email"), "value is not a valid email address"),
        ("testexample.com", ("body", "email"), "value is not a valid email address"),
        ("test@.com", ("body", "email"), "value is not a valid email address"),
        ("test@", ("body", "email"), "value is not a valid email address"),
        ("test@example%.com", ("body", "email"), "value is not a valid email address"),
        ("test@example.com%", ("body", "email"), "value is not a valid email address"),
        ("test@domain..com", ("body", "email"), "value is not a valid email address"),
        ("user@domain", ("body", "email"), "value is not a valid email address"),
        ("test@examplecom", ("body", "email"), "value is not a valid email address"),
        ("test@example.", ("body", "email"), "value is not a valid email address"),
    ],
    ids=[
        "empty_email",
        "email_with_whitespace",
        "email_no_local_part",
        "email_no_at_sign",
        "email_no_domain_name",
        "email_no_domain",
        "email_incorrect_char_in_domain",
        "email_incorrect_char_in_tld",
        "email_double_dot_domain",
        "email_no_tld",
        "email_no_dot_in_domain",
        "email_no_tld_with_dot",
    ],
)
def test_create_user_with_invalid_email(
    api_service: str,
    invalid_email_input: str,
    expected_error_loc: Tuple[str, str],
    expected_error_msg_substring: str,
) -> None:
    """
    Tests that attempting to create a user with an invalid email format via the API
    returns a 422 Unprocessable Entity status code and appropriate error detail.
    """
    users_url = f"{api_service}/users"
    user_data = {"id": 1, "name": "Test User", "email": invalid_email_input}

    logger.debug(
        "Attempting to create user with invalid email: "
        f"{invalid_email_input} via POST {users_url}"
    )
    response: requests.Response = requests.post(users_url, json=user_data, timeout=20)
    logger.debug(f"Post invalid user response JSON: {response.json()}")

    assert response.status_code == 422
    logger.debug("Successfully asserted user creation failure status code.")

    response_json = response.json()
    assert "detail" in response_json, "Response JSON must contain 'detail' field"
    assert isinstance(response_json["detail"], list), "'detail' field must be a list"
    assert len(response_json["detail"]) > 0, "'detail' list must not be empty"

    expected_error_found = any(
        err.get("loc") == list(expected_error_loc)
        and expected_error_msg_substring in err.get("msg")
        for err in response_json["detail"]
    )
    assert expected_error_found, (
        f"Expected error for location {list(expected_error_loc)} "
        f"with message substring '{expected_error_msg_substring}' "
        f"not found in {response_json['detail']}"
    )


# --- GET /users/{id} tests ---


@allure.feature("API")
@allure.story("API User Retrieval")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Verify successful user getting for multiple users")
# fmt: off
@allure.description("""This test verifies that the retrieval of multiple pre-existing users via GET /users/{user_id} is successful and returns correct data for each.""")  # noqa: E501
# fmt: on
def test_get_user_by_id(
    three_test_users: Tuple[str, Dict[str, Dict[str, Any]]],
    validator_factory: Callable[[dict], Any],
) -> None:
    """
    Tests that retrieving multiple users by ID via GET `/users/{user_id}`
    returns the correct user data for each.
    """
    api_service, users_data_for_test = three_test_users
    user_schema: Dict[str, Any] = load_schema("user_schema.json")

    for user_id_str, expected_user_data in users_data_for_test.items():
        user_id = int(user_id_str)

        user_url = f"{api_service}/users/{user_id}"
        logger.debug(f"Attempting to get user by ID {user_id} at: {user_url}")
        response: requests.Response = requests.get(user_url, timeout=20)
        logger.debug(f"Get user by ID {user_id} response JSON: {response.json()}")

        assert response.status_code == 200
        logger.debug(f"Successfully asserted user {user_id} retrieval.")

        validator_instance = validator_factory(user_schema)
        validator_instance.validate(response.json())
        logger.debug("Successfully validated response against user_schema.json.")

        user = response.json()
        assert isinstance(user, dict), "Response JSON must be a dictionary"
        assert (
            user["id"] == expected_user_data["id"]
        ), f"Expected user ID {expected_user_data['id']}, but got {user['id']}"
        assert (
            user["name"] == expected_user_data["name"]
        ), f"Expected user name {expected_user_data['name']}, but got {user['name']}"
        assert (
            user["email"] == expected_user_data["email"]
        ), f"Expected user email {expected_user_data['email']}, but got {user['email']}"


@allure.feature("API")
@allure.story("API User Retrieval")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Verify getting a non-existent user fails with 404")
# fmt: off
@allure.description("""This test verifies that the retrieval of a non-existent user via a GET request to /users/{user_id} fails correctly.""")  # noqa: E501
# fmt: on
def test_get_non_existent_user(api_service: str) -> None:
    """
    Tests that attempting to get a non-existent user via GET `/users/{user_id}`
    raises HTTP 404.
    """
    non_existent_user_id = 9999
    get_url = f"{api_service}/users/{non_existent_user_id}"
    logger.debug(
        f"Attempting to get non-existent user with ID {non_existent_user_id} at: "
        f"{get_url}"
    )
    response: requests.Response = requests.get(get_url, timeout=20)
    logger.debug(f"Get non-existent user response JSON: {response.json()}")

    assert response.status_code == 404
    logger.debug("Successfully asserted non-existent user retrieval failure.")

    expected_detail_msg = f"User with ID {non_existent_user_id} not found"

    assert response.json().get("detail") == expected_detail_msg, (
        f"Expected detail message '{expected_detail_msg}' "
        f"not found in response: {response.json()}"
    )


# --- DELETE /users/{id} tests ---


@allure.feature("API")
@allure.story("API User Removal")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Verify successful user removal")
# fmt: off
@allure.description("""This test verifies that a user removal via a DELETE request to /users/{user_id} is successful.""")  # noqa: E501
# fmt: on
def test_delete_user_success(
    api_service: str, created_test_user: Dict[str, Any]
) -> None:
    """Tests that deleting a user via DELETE `/users/{user_id}` is successful."""
    user_id_to_delete: int = created_test_user["id"]
    delete_url = f"{api_service}/users/{user_id_to_delete}"

    logger.debug(
        f"Attempting to delete a user via DELETE /users/{user_id_to_delete} "
        f"at: {delete_url}"
    )
    response: requests.Response = requests.delete(delete_url, timeout=20)

    assert response.status_code == 204
    logger.debug("Successfully asserted user deletion.")

    logger.debug(f"Verifying user {user_id_to_delete} is deleted via GET.")
    verify_response: requests.Response = requests.get(delete_url, timeout=20)
    assert verify_response.status_code == 404, "User should not be found after deletion"


@allure.feature("API")
@allure.story("API User Removal")
@allure.severity(allure.severity_level.MINOR)
@allure.title("Verify unsuccessful non-existent user removal")
# fmt: off
@allure.description("""This test verifies that a non-existent user removal via a DELETE request to /users/{user_id} failed correctly.""")  # noqa: E501
# fmt: on
def test_delete_non_existent_user(api_service: str) -> None:
    """
    Tests that attempting to delete a non-existent user via DELETE `/users/{user_id}`
    raises HTTP 404.
    """
    non_existent_user_id = 9999
    delete_url = f"{api_service}/users/{non_existent_user_id}"
    logger.debug(
        f"Attempting to delete non-existent user with ID {non_existent_user_id} "
        f"at: {delete_url}"
    )
    response: requests.Response = requests.delete(delete_url, timeout=20)
    logger.debug(f"Delete non-existent user response JSON: {response.json()}")

    assert response.status_code == 404
    logger.debug("Successfully asserted non-existent user deletion failure.")

    expected_message = f"User with ID {non_existent_user_id} not found."

    assert response.json().get("detail") == expected_message, (
        f"Expected detail message '{expected_message}' "
        f"not found in response: {response.json()}"
    )


# --- GET and DELETE /users/{id} invalid ID path test ---


@allure.feature("API")
@allure.story("API Input Validation")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Verify API fails for invalid ID type in path for GET/DELETE")
# fmt: off
@allure.description("""This test verifies that attempting to get or delete a user via GET/DELETE /users/{user_id} where {user_id} is of an invalid type (e.g., string, float) results in a 422 Unprocessable Entity error.""")  # noqa: E501
# fmt: on
@pytest.mark.parametrize("http_method", ["GET", "DELETE"])
@pytest.mark.parametrize(
    "invalid_user_id_path, expected_error_msg_substring",
    [
        ("abc", "Input should be a valid integer"),  # Non-numeric string
        ("1.5", "Input should be a valid integer"),  # Float as string
        ("true", "Input should be a valid integer"),  # Boolean as string
        ("null", "Input should be a valid integer"),  # Null as string
        ("!@#", "Input should be a valid integer"),  # Special characters
    ],
    ids=[
        "non_numeric_string",
        "float_string",
        "boolean_string",
        "null_string",
        "special_chars",
    ],
)
def test_request_with_invalid_id_type_in_path(
    api_service: str,
    http_method: str,
    invalid_user_id_path: str,
    expected_error_msg_substring: str,
) -> None:
    """
    Tests that GET and DELETE requests with an invalid type for user_id in the path
    return HTTP 422.
    """
    url = f"{api_service}/users/{invalid_user_id_path}"
    logger.debug(
        f"Attempting {http_method} request with invalid "
        f"ID type '{invalid_user_id_path}' at: {url}"
    )

    response: requests.Response = requests.request(http_method, url, timeout=20)
    logger.debug(f"{http_method} user invalid ID type response JSON: {response.json()}")

    assert response.status_code == 422
    logger.debug(
        f"Successfully asserted user {http_method} request failure for invalid ID type."
    )

    response_json = response.json()
    assert (
        "detail" in response_json
    ), "Response JSON must contain 'detail' field for 422 errors"
    assert isinstance(response_json["detail"], list), "'detail' field must be a list"
    assert len(response_json["detail"]) > 0, "'detail' list must not be empty"
    logger.debug("Successfully validated 'detail' field in response JSON.")

    expected_error_loc = ("path", "user_id")
    expected_error_found = any(
        err.get("loc") == list(expected_error_loc)
        and expected_error_msg_substring in err.get("msg")
        for err in response_json["detail"]
    )

    assert expected_error_found, (
        f"Expected error for location {list(expected_error_loc)} "
        f"with message substring '{expected_error_msg_substring}' "
        f"not found in {response_json['detail']}"
    )


# --- GET /users test ---


@allure.feature("API")
@allure.story("API Users Retrieval")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Verify successful retrieval of all users")
# fmt: off
@allure.description("""This test verifies that the retrieval of all users via a GET request to /users is successful.""")  # noqa: E501
# fmt: on
def test_get_all_users(
    three_test_users: Tuple[str, Dict[str, Dict[str, Any]]],
    validator_factory: Callable[[dict], Any],
) -> None:
    """Tests that retrieving all users via GET `/users` returns a list of users."""
    api_service, users_data_for_test = three_test_users
    user_list_schema: Dict[str, Any] = load_schema("user_list_schema.json")
    users_url = f"{api_service}/users"
    logger.debug(f"Attempting to get all users at: {users_url}")
    response: requests.Response = requests.get(users_url, timeout=20)

    assert response.status_code == 200
    logger.debug("Successfully asserted user retrieval.")

    validator_instance = validator_factory(user_list_schema)
    validator_instance.validate(response.json())
    logger.debug("Successfully validated response against user_list_schema.json.")

    assert len(response.json()) == len(
        users_data_for_test
    ), f"Expected {len(users_data_for_test)} users, but got {len(response.json())}"
    logger.debug(
        f"Successfully asserted the count of returned users ({len(response.json())})."
    )

    for user_dict in response.json():
        assert isinstance(user_dict, dict)
        assert (
            str(user_dict["id"]) in users_data_for_test
        ), f"Returned user ID {user_dict['id']} not found in expected test data."

        expected_user = users_data_for_test[str(user_dict["id"])]
        assert (
            user_dict["id"] == expected_user["id"]
        ), f"Expected user ID {expected_user['id']}, but got {user_dict['id']}"
        assert (
            user_dict["name"] == expected_user["name"]
        ), f"Expected user name {expected_user['name']}, but got {user_dict['name']}"
        assert (
            user_dict["email"] == expected_user["email"]
        ), f"Expected user email {expected_user['email']}, but got {user_dict['email']}"
        logger.debug(f"Successfully validated data for user ID {user_dict['id']}.")


@allure.feature("API")
@allure.story("API Users Retrieval")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Verify successful status code when in-memory store is empty")
# fmt: off
@allure.description("""This test verifies that the retrieval of all users attempt via a GET request to /users returns 200 OK with empty list.""")  # noqa: E501
# fmt: on
def test_get_all_users_with_empty_in_memory_store(api_service: str) -> None:
    users_url = f"{api_service}/users"
    logger.debug(f"Attempting to get all users at: {users_url}")
    response: requests.Response = requests.get(users_url, timeout=20)

    assert response.status_code == 200
    logger.debug("Successfully asserted user retrieval.")
    assert len(response.json()) == 0, "Expected an empty list of users"
