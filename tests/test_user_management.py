import pytest
import json
import os
import logging
import allure
from typing import Dict, Union, Tuple, Any, cast
from pathlib import Path
from src.user_management import (
    User,
    UserService,
    DuplicateUserError,
    UserNotFoundError,
    DataFileWriteError,
)
from pytest_mock import MockerFixture

logger = logging.getLogger(__name__)


class TestUser:
    """Tests for User class"""

    _VALID_ID = 100
    _VALID_NAME = "Test User"
    _VALID_EMAIL = "test.user@example.com"

    # --- __init__() test ---

    @allure.feature("User")
    @allure.story("User Input Validation")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Verify successful user initialization with valid data")
    # fmt: off
    @allure.description("This test verifies that a user can be initialized successfully with valid data.")  # noqa: E501
    # fmt: on
    def test_user_init_successful(self) -> None:
        """Tests user initialization with valid data."""
        logger.debug("Starting user initialization test with valid data.")
        user = User(self._VALID_ID, self._VALID_NAME, self._VALID_EMAIL)

        assert isinstance(user, User), "User instance was not created successfully"
        assert user.id == self._VALID_ID, "User ID does not match the input"
        assert user.name == self._VALID_NAME, "User name does not match the input"
        assert user.email == self._VALID_EMAIL, "User email does not match the input"

    @allure.feature("User")
    @allure.story("User Input Validation")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Verify successful user initialization with valid IDs")
    # fmt: off
    @allure.description("""This parameterized test verifies that a user can be initialized with various valid IDs. It includes checking the ID starting from a single-digit minimum value up to a five-digit value.""")  # noqa: E501)
    # fmt: on
    @pytest.mark.parametrize(
        "valid_id_input",
        [
            1,  # Minimum valid ID
            2,  # Small positive ID
            100,  # Three-digit ID
            4444,  # Four-digit ID
            99999,  # Five-digit ID
            123456789,  # Larger ID
        ],
        ids=[
            "id_min_boundary_1",
            "id_small",
            "id_three_digits",
            "id_four_digits",
            "id_five_digits",
            "id_large_number",
        ],
    )
    def test_user_init_valid_ids(self, valid_id_input: int) -> None:
        """Tests user initialization with various ID inputs."""
        logger.debug(
            f"Starting user initialization test with valid ID: {valid_id_input}"
        )
        user = User(valid_id_input, self._VALID_NAME, self._VALID_EMAIL)

        assert isinstance(user, User), "User instance was not created successfully"
        assert user.id == valid_id_input, "User ID does not match the input"
        assert user.name == self._VALID_NAME, "User name does not match the input"
        assert user.email == self._VALID_EMAIL, "User email does not match the input"

    @allure.feature("User")
    @allure.story("User Input Validation")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Verify successful user initialization with valid names")
    # fmt: off
    @allure.description("""This parameterized test verifies that a user can be initialized with various valid names. It includes minimum, medium and maximum name length.""")  # noqa: E501
    # fmt: on
    @pytest.mark.parametrize(
        "valid_name_input",
        [
            "a" * 4,
            "a" * 37,
            "a" * 70,
        ],
        ids=[
            "name_min_boundary_4",
            "name_medium_length_37",
            "name_max_boundary_70",
        ],
    )
    def test_user_init_valid_names(self, valid_name_input: str) -> None:
        """Tests user initialization with various name length inputs."""
        logger.debug(
            f"Starting user initialization test with valid name: {valid_name_input}"
        )
        user = User(self._VALID_ID, valid_name_input, self._VALID_EMAIL)

        assert isinstance(user, User), "User instance was not created successfully"
        assert user.id == self._VALID_ID, "User ID does not match the input"
        assert user.name == valid_name_input, "User name does not match the input"
        assert user.email == self._VALID_EMAIL, "User email does not match the input"

    @allure.feature("User")
    @allure.story("User Input Validation")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Verify successful user initialization with valid email")
    # fmt: off
    @allure.description("""This test verifies that a user can be initialized with valid email.""")  # noqa: E501
    # fmt: on
    def test_user_init_valid_email(self) -> None:
        """Tests user initialization with a valid email string."""
        logger.debug(
            f"Starting user initialization test with valid email: {self._VALID_EMAIL}"
        )
        user = User(self._VALID_ID, self._VALID_NAME, self._VALID_EMAIL)

        assert isinstance(user, User), "User instance was not created successfully"
        assert user.id == self._VALID_ID, "User ID does not match the input"
        assert user.name == self._VALID_NAME, "User name does not match the input"
        assert user.email == self._VALID_EMAIL, "User email does not match the input"

    @allure.feature("User")
    @allure.story("User Input Validation")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify unsuccessful user initialization with invalid IDs")
    # fmt: off
    @allure.description("""This parameterized test verifies that a user cannot be initialized with various invalid IDs. It includes negative and 0 IDs.""")  # noqa: E501
    # fmt: on
    @pytest.mark.parametrize(
        "id_input, expected_exception, error_message_substring",
        [
            ("123", TypeError, "User ID must be an integer"),
            (None, TypeError, "User ID must be an integer"),
            ([], TypeError, "User ID must be an integer"),
            (-100, ValueError, "User ID must be a positive integer"),
            (-10, ValueError, "User ID must be a positive integer"),
            (-1, ValueError, "User ID must be a positive integer"),
            (0, ValueError, "User ID must be a positive integer"),
        ],
        ids=[
            "id_type_str",
            "id_type_None",
            "id_type_list",
            "id_3-digit_negative",
            "id_2-digit_negative",
            "id_1-digit_negative",
            "id_zero",
        ],
    )
    def test_user_init_invalid_ids(
        self, id_input: int, expected_exception: type, error_message_substring: str
    ) -> None:
        """
        Tests user initialization with various invalid IDs inputs raise ValueError.
        """
        logger.debug("Starting user initialization test with invalid ID.")
        logger.debug(
            f"Attempting initialize with ID='{id_input}', "
            f"name='{self._VALID_NAME}', email='{self._VALID_EMAIL}'"
        )
        with pytest.raises(expected_exception) as excinfo:
            User(id_input, self._VALID_NAME, self._VALID_EMAIL)

        assert error_message_substring in str(excinfo.value), (
            f"Expected '{error_message_substring}' not found in "
            f"exception message: '{excinfo.value}'"
        )

    @allure.feature("User")
    @allure.story("User Input Validation")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify unsuccessful user initialization with invalid names")
    # fmt: off
    @allure.description("""This parameterized test verifies that a user cannot be initialized with various invalid names. It includes boundary values, empty name, and incorrect types.""")  # noqa: E501
    # fmt: on
    @pytest.mark.parametrize(
        "name_input, expected_exception, error_message_substring",
        [
            (123, TypeError, "User name must be a string"),
            (None, TypeError, "User name must be a string"),
            ([], TypeError, "User name must be a string"),
            ("", ValueError, "User name cannot be empty or whitespace only"),
            ("   ", ValueError, "User name cannot be empty or whitespace only"),
            ("aaa", ValueError, "User name length cannot be less than 4"),
            (" aaa ", ValueError, "User name length cannot be less than 4"),
            ("a" * 71, ValueError, "User name length cannot be longer than 70"),
        ],
        ids=[
            "name_type_int",
            "name_type_None",
            "name_type_list",
            "name_empty",
            "name_whitespace_only",
            "name_too_short",
            "name_too_short_padded",
            "name_too_long",
        ],
    )
    def test_user_init_invalid_names(
        self,
        name_input: Any,
        expected_exception: type,
        error_message_substring: str,
    ) -> None:
        """
        Tests user initialization with various invalid
        names inputs raise TypeError and ValueError.
        """
        logger.debug("Starting user initialization test with invalid name.")
        logger.debug(
            f"Attempting initialize with ID='{self._VALID_ID}', "
            f"name='{name_input}', email='{self._VALID_EMAIL}'"
        )
        with pytest.raises(expected_exception) as excinfo:
            User(self._VALID_ID, name_input, self._VALID_EMAIL)

        assert error_message_substring in str(excinfo.value), (
            f"Expected '{error_message_substring}' not found in "
            f"exception message: '{excinfo.value}'"
        )

    @allure.feature("User")
    @allure.story("User Input Validation")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify unsuccessful user initialization with invalid email types")
    # fmt: off
    @allure.description("""This parameterized test verifies that a user cannot be initialized with invalid emails. It includes None, integer and list email inputs.""")  # noqa: E501
    # fmt: on
    @pytest.mark.parametrize(
        "email_input, expected_exception, error_message_substring",
        [
            (None, TypeError, "User email must be a string"),
            (123, TypeError, "User email must be a string"),
            ([], TypeError, "User email must be a string"),
        ],
        ids=["email_type_None", "email_type_int", "email_type_list"],
    )
    def test_user_init_email_invalid_type(
        self, email_input, expected_exception, error_message_substring
    ) -> None:
        """
        Tests user initialization with invalid email inputs raise TypeError.
        """
        logger.debug("Starting user initialization test with invalid email.")
        logger.debug(
            f"Attempting initialize with ID='{self._VALID_ID}', "
            f"name='{self._VALID_NAME}', email='{email_input}'"
        )
        with pytest.raises(expected_exception) as excinfo:
            User(self._VALID_ID, self._VALID_NAME, email_input)

        assert error_message_substring in str(excinfo.value), (
            f"Expected '{error_message_substring}' not found in "
            f"exception message: '{excinfo.value}'"
        )

    # --- __str__() test ---

    @allure.feature("User")
    @allure.story("User String Representation")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.title("Verify successful string representation of the user")
    # fmt: off
    @allure.description("""This test verifies that a string representation of the user is successful and correct.""")  # noqa: E501
    # fmt: on
    def test_user_string_representation(self) -> None:
        """Tests that getting User instance string representation is successful."""
        logger.debug("Starting user string representation test.")
        user_id = 4
        user_name = "Veronica Mars"
        user_email = "veronicamars@example.com"
        user = User(user_id, user_name, user_email)

        expected_string = f"{user_name} - ID: {user_id}, Email: {user_email}"

        logger.debug(
            "Attempting to get a string representation with user attributes: "
            f"ID='{user_id}', name='{user_name}', email='{user_email}'. "
            f"Expected string: '{expected_string}'"
        )
        assert str(user) == expected_string, (
            "String representation does not match expected output."
            f" Expected: '{expected_string}', got: '{str(user)}'"
        )


class TestUserService:

    # --- add_user() test ---

    @allure.feature("User Service")
    @allure.story("User Addition Scenarios")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Verify successful user addition with valid inputs")
    # fmt: off
    @allure.description("""This test verifies that a user addition to user service is successful.""")  # noqa: E501
    # fmt: on
    def test_add_user(
        self, basic_instances: Dict[str, Union["UserService", "User"]]
    ) -> None:
        """Tests that adding a user is successful."""
        logger.debug("Starting user addition test.")
        user_service = cast("UserService", basic_instances["user_service"])
        user1 = cast("User", basic_instances["user1"])

        logger.debug(f"Attempting to add user {user1}")
        user_service.add_user(user1)

        assert user_service.users_list[user1.id] is user1, (
            "User was not added to the user service's users list. "
            f"Expected user ID: {user1.id}, "
            f"got: {user_service.users_list.get(user1.id)}"
        )

    @allure.feature("User Service")
    @allure.story("User Addition Scenarios")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify unsuccessful non-user object addition")
    # fmt: off
    @allure.description("""This test verifies that a non-user object addition to user service failed correctly.""")  # noqa: E501
    # fmt: on
    def test_add_non_user_object(
        self, basic_instances: Dict[str, Union["UserService", "User"]]
    ) -> None:
        """Tests that adding a non-user object raises TypeError."""
        logger.debug("Starting non-user object addition test.")
        user_service = cast("UserService", basic_instances["user_service"])
        non_user_instance = "user1"

        logger.debug(
            "Attempting to add non-user object with "
            f"{type(non_user_instance).__name__} type."
        )
        with pytest.raises(TypeError):
            user_service.add_user(cast("User", non_user_instance))

        assert (
            len(user_service.users_list) == 0
        ), "Users list should remain empty after trying to add a non-user object."

    @allure.feature("User Service")
    @allure.story("User Addition Scenarios")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify unsuccessful existent user addition")
    # fmt: off
    @allure.description("""This test verifies that a existent user addition to user service failed correctly.""")  # noqa: E501
    # fmt: on
    def test_add_exist_user(
        self, basic_instances: Dict[str, Union["UserService", "User"]]
    ) -> None:
        """
        Tests that adding a user with an ID that already exists raises
        DuplicateUserError.
        """
        logger.debug("Starting existing user addition test.")
        user_service = cast("UserService", basic_instances["user_service"])
        user1 = cast("User", basic_instances["user1"])

        user_service.add_user(user1)

        logger.debug(f"Attempting to add existing user {user1}")
        with pytest.raises(DuplicateUserError):
            user_service.add_user(user1)

        assert len(user_service.users_list) == 1, (
            "Users list should contain only one user "
            "after trying to add an existing user."
        )

    # --- remove_user_by_id() test ---

    @allure.feature("User Service")
    @allure.story("User Removal Scenarios")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify successful user removal")
    # fmt: off
    @allure.description("""This test verifies that a user removal from user service is successful.""")  # noqa: E501
    # fmt: on
    def test_remove_user_by_id(
        self, basic_instances: Dict[str, Union["UserService", "User"]]
    ) -> None:
        """Tests that removing user by ID is successful."""
        logger.debug("Starting user removal by ID test.")
        user_service = cast("UserService", basic_instances["user_service"])
        user1 = cast("User", basic_instances["user1"])
        user2 = cast("User", basic_instances["user2"])
        user3 = cast("User", basic_instances["user3"])
        user_service.add_user(user1)
        user_service.add_user(user2)
        user_service.add_user(user3)

        logger.debug(f"Attempting to remove user with ID {user1.id}")
        user_service.remove_user_by_id(user1.id)

        assert (
            len(user_service.users_list) == 2
        ), "Users list should contain two users after removal."
        assert (
            user1.id not in user_service.users_list
        ), f"User with ID {user1.id} should be removed from the users list."

    @allure.feature("User Service")
    @allure.story("User Removal Scenarios")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Verify unsuccessful non-existent user removal")
    # fmt: off
    @allure.description("""This test verifies that a non-existent user removal from user service failed correctly.""")  # noqa: E501
    # fmt: on
    def test_remove_non_exist_user_by_id(
        self, basic_instances: Dict[str, Union["UserService", "User"]]
    ) -> None:
        """Tests that removing a non-existing user fails."""
        logger.debug("Starting non-existent user removal by ID test.")
        user_service = cast("UserService", basic_instances["user_service"])
        non_exist_id = 10

        logger.debug(f"Attempting to remove non-existent user by ID {non_exist_id}")
        with pytest.raises(UserNotFoundError):
            user_service.remove_user_by_id(non_exist_id)

        assert len(user_service.users_list) == 0, (
            "Users list should remain empty after "
            "trying to remove a non-existent user."
        )

    # --- load_users_from_json() test ---

    @allure.feature("User Service")
    @allure.story("JSON Loading Scenarios")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Verify successful loading users from JSON file")
    # fmt: off
    @allure.description("""This test verifies that loading users from a JSON file to user service is successful.""")  # noqa: E501
    # fmt: on
    def test_load_users_from_json(
        self,
        basic_instances: Dict[str, Union["UserService", "User"]],
        json_with_users_path: Path,
    ) -> None:
        """Tests that loading users from a JSON file is successful."""
        logger.debug("Starting the test: Loading users from a JSON file.")
        user_service = cast("UserService", basic_instances["user_service"])
        user1 = cast("User", basic_instances["user1"])
        user2 = cast("User", basic_instances["user2"])

        logger.debug(
            f"Attempting to load users '{user1}', '{user2}'"
            f"from JSON file: '{json_with_users_path}'"
        )
        user_service.load_users_from_json(file_path=str(json_with_users_path))

        assert (
            len(user_service.users_list) == 2
        ), "Users list should contain two users after loading from JSON file."
        assert user1.id in user_service.users_list, "User1 should be in the users list."
        assert user2.id in user_service.users_list, "User2 should be in the users list."
        assert (
            user_service.users_list[user1.id].name == user1.name
        ), "User1 name does not match after loading from JSON file."
        assert (
            user_service.users_list[user1.id].email == user1.email
        ), "User1 email does not match after loading from JSON file."
        assert (
            user_service.users_list[user2.id].name == user2.name
        ), "User2 name does not match after loading from JSON file."
        assert (
            user_service.users_list[user2.id].email == user2.email
        ), "User2 email does not match after loading from JSON file."

    @allure.feature("User Service")
    @allure.story("JSON Loading Scenarios")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify successful loading users from JSON file with mocked I/O")
    # fmt: off
    @allure.description("""This test verifies that loading users from a JSON file with mocked I/O to user service is successful.""")  # noqa: E501
    # fmt: on
    def test_load_users_logic_mocked_io(
        self,
        basic_instances: Dict[str, Union["UserService", "User"]],
        mocker: MockerFixture,
    ) -> None:
        """Tests user processing logic in load_users_from_json using mocked I/O."""
        logger.debug(
            "Starting the test: Loading users from a JSON file with mocked logic of "
            "input/output."
        )
        user_service = cast("UserService", basic_instances["user_service"])
        user1_data = {"id": 10, "name": "Mocked UserOne", "email": "mock1@example.com"}
        user2_data = {"id": 20, "name": "Mocked UserTwo", "email": "mock2@example.com"}
        mock_json_content = {
            str(user1_data["id"]): user1_data,
            str(user2_data["id"]): user2_data,
        }
        mock_file_path = "fake/users.json"

        mock_load = mocker.patch("json.load", return_value=mock_json_content)
        mock_file_open = mocker.patch("builtins.open", mocker.mock_open())

        logger.debug(
            f"Attempting to load users from mocked file path '{mock_file_path}' "
            f"with mocked content: {mock_json_content}"
        )
        user_service.load_users_from_json(mock_file_path)

        assert (
            len(user_service.users_list) == 2
        ), "Users list should contain two users after loading from mocked JSON file."
        assert (
            user1_data["id"] in user_service.users_list
        ), "User1 should be in the users list after loading from mocked JSON file."
        assert (
            user2_data["id"] in user_service.users_list
        ), "User2 should be in the users list after loading from mocked JSON file."
        assert (
            user_service.users_list[user1_data["id"]].name == user1_data["name"]
        ), "User1 name does not match after loading from mocked JSON file."
        assert (
            user_service.users_list[user2_data["id"]].email == user2_data["email"]
        ), "User2 email does not match after loading from mocked JSON file."

        mock_file_open.assert_called_once_with(mock_file_path, "r")
        mock_load.assert_called_once_with(mock_file_open())

    @allure.feature("User Service")
    @allure.story("JSON Loading Scenarios")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title(
        "Verify successful loading users from JSON file with non-empty users list"
    )
    # fmt: off
    @allure.description("""This test verifies that loading users from a JSON file with non-empty users in user service list is successful.""")  # noqa: E501
    # fmt: on
    def test_load_users_from_json_to_non_empty_users_list(
        self,
        basic_instances: Dict[str, Union["UserService", "User"]],
        json_with_users_path: Path,
    ) -> None:
        """
        Tests that loading users from a JSON file with non-empty users list is
        successful.
        """
        logger.debug(
            "Starting the test: Loading users from a JSON file with non-empty "
            "users list."
        )
        user_service = cast("UserService", basic_instances["user_service"])
        user1 = cast("User", basic_instances["user1"])
        user2 = cast("User", basic_instances["user2"])
        user3 = cast("User", basic_instances["user3"])

        user_service.add_user(user3)

        logger.debug(
            "Attempting to load users to non-empty users list from JSON file: "
            f"'{json_with_users_path}'"
        )
        user_service.load_users_from_json(file_path=str(json_with_users_path))

        assert (
            len(user_service.users_list) == 3
        ), "Users list should contain three users after loading from JSON file."
        assert user3.id in user_service.users_list, "User3 should be in the users list."
        assert user1.id in user_service.users_list, "User1 should be in the users list."
        assert user2.id in user_service.users_list, "User2 should be in the users list."
        assert (
            user_service.users_list[user1.id].name == user1.name
        ), "User1 name does not match after loading from JSON file."
        assert (
            user_service.users_list[user1.id].email == user1.email
        ), "User1 email does not match after loading from JSON file."
        assert (
            user_service.users_list[user2.id].name == user2.name
        ), "User2 name does not match after loading from JSON file."
        assert (
            user_service.users_list[user2.id].email == user2.email
        ), "User2 email does not match after loading from JSON file."

    @allure.feature("User Service")
    @allure.story("JSON Loading Scenarios")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify successful loading users from JSON file with list cleanup")
    # fmt: off
    @allure.description("""This test verifies that loading users from a JSON file with users list cleanup in user service is successful.""")  # noqa: E501
    # fmt: on
    def test_load_users_from_json_clear_users_list_true(
        self,
        basic_instances: Dict[str, Union["UserService", "User"]],
        json_with_users_path: Path,
    ) -> None:
        """Tests that loading users from JSON file with list cleanup is successful."""
        logger.debug(
            "Starting the test: Loading users from a JSON file with "
            "clearing users list."
        )
        user_service = cast("UserService", basic_instances["user_service"])
        user1 = cast("User", basic_instances["user1"])
        user2 = cast("User", basic_instances["user2"])
        user3 = cast("User", basic_instances["user3"])

        user_service.add_user(user3)

        logger.debug(
            "Attempting to load users to non-empty users list with clearing "
            f"from json file: '{json_with_users_path}'"
        )
        user_service.load_users_from_json(
            file_path=str(json_with_users_path), clear_users_list=True
        )

        assert len(user_service.users_list) == 2, (
            "Users list should contain two users after loading from JSON file with "
            "clearing."
        )
        assert user3.id not in user_service.users_list, (
            "User3 should not be in the users list after loading from JSON file with "
            "clearing."
        )
        assert user1.id in user_service.users_list, "User1 should be in the users list."
        assert user2.id in user_service.users_list, "User2 should be in the users list."
        assert (
            user_service.users_list[user1.id].name == user1.name
        ), "User1 name does not match after loading from JSON file with clearing."
        assert (
            user_service.users_list[user1.id].email == user1.email
        ), "User1 email does not match after loading from JSON file with clearing."
        assert (
            user_service.users_list[user2.id].name == user2.name
        ), "User2 name does not match after loading from JSON file with clearing."
        assert (
            user_service.users_list[user2.id].email == user2.email
        ), "User2 email does not match after loading from JSON file with clearing."

    @allure.feature("User Service")
    @allure.story("JSON Loading Scenarios")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title(
        "Verify successful loading users from JSON file with overwriting "
        "an existing user"
    )
    # fmt: off
    @allure.description("""This test verifies that loading users from a JSON file with overwriting an existing user in user service's users list is successful.""")  # noqa: E501
    # fmt: on
    def test_load_users_from_json_with_overwriting(
        self,
        basic_instances: Dict[str, Union["UserService", "User"]],
        json_with_users_path: Path,
    ) -> None:
        """
        Tests that loading users from JSON file with overwriting an existing user
        is successful.
        """
        logger.debug(
            "Starting the test: Loading users from a JSON file with overwriting."
        )
        user_service = cast("UserService", basic_instances["user_service"])
        user1 = cast("User", basic_instances["user1"])
        user2 = cast("User", basic_instances["user2"])
        incorrect_user1 = User(user1.id, user2.name, user2.email)

        user_service.add_user(incorrect_user1)

        logger.debug(
            "Attempting to load users to non-empty users list with overwriting "
            f"from json file: '{json_with_users_path}'"
        )
        user_service.load_users_from_json(file_path=str(json_with_users_path))

        assert len(user_service.users_list) == 2, (
            "Users list should contain two users after loading from JSON file with "
            "overwriting."
        )
        assert user1.id in user_service.users_list, "User1 should be in the users list."
        assert user2.id in user_service.users_list, "User2 should be in the users list."
        assert (
            user_service.users_list[user1.id].name == user1.name
        ), "User1 name does not match after loading from JSON file with overwriting."
        assert (
            user_service.users_list[user1.id].email == user1.email
        ), "User1 email does not match after loading from JSON file with overwriting."
        assert (
            user_service.users_list[user2.id].name == user2.name
        ), "User2 name does not match after loading from JSON file with overwriting."
        assert (
            user_service.users_list[user2.id].email == user2.email
        ), "User2 email does not match after loading from JSON file with overwriting."

    @allure.feature("User Service")
    @allure.story("JSON Loading Scenarios")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Verify unsuccessful loading users from non-existing JSON file")
    # fmt: off
    @allure.description("""This test verifies that loading users from a non-existing JSON file to user service failed correctly.""")  # noqa: E501
    # fmt: on
    def test_load_users_from_non_exist_json(
        self, basic_instances: Dict[str, Union["UserService", "User"]]
    ) -> None:
        """
        Tests that loading usesrs from non-existing JSON file raises
        FileNotFoundError exception.
        """
        logger.debug("Starting the test: Loading users from a non-existent JSON file.")
        user_service = cast("UserService", basic_instances["user_service"])

        logger.debug("Attempting to load users from non-exist JSON file.")
        with pytest.raises(FileNotFoundError):
            user_service.load_users_from_json(file_path="non_exist_file.json")

        assert len(user_service.users_list) == 0, (
            "Users list should remain empty after trying to load from a non-existing "
            "JSON file."
        )

    @allure.feature("User Service")
    @allure.story("JSON Loading Scenarios")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Verify unsuccessful loading users from malformed JSON file")
    # fmt: off
    @allure.description("""This test verifies that loading users from a malformed JSON file to users service failed correctly.""")  # noqa: E501
    # fmt: on
    def test_load_users_from_json_decode_error(
        self,
        basic_instances: Dict[str, Union["UserService", "User"]],
        malformed_json_path: Path,
    ) -> None:
        """
        Tests that loading users from malformed JSON file raises JSONDecodeError
        exception.
        """
        logger.debug("Starting the test: Loading users from malformed JSON file.")
        user_service = cast("UserService", basic_instances["user_service"])

        logger.debug(
            "Attempting to load users from malformed JSON file: "
            f"'{malformed_json_path}'"
        )
        with pytest.raises(json.JSONDecodeError):
            user_service.load_users_from_json(str(malformed_json_path))

        assert len(user_service.users_list) == 0, (
            "Users list should remain empty after trying to load from a malformed "
            "JSON file."
        )

    @allure.feature("User Service")
    @allure.story("JSON Loading Scenarios")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Verify unsuccessful loading users from malformed JSON file")
    # fmt: off
    @allure.description("""This test verifies that loading users from a malformed JSON file to user service failed correctly. The 'json_with_invalid_data' fixture provides users with invalid data like non-dictionary data, invalid ID type, ID mismatch and invalid user's key. The test ensures that loading invalid data errors for each input.""")  # noqa: E501
    # fmt: on
    def test_load_users_from_json_with_invalid_data(
        self,
        basic_instances: Dict[str, Union["UserService", "User"]],
        json_with_invalid_data: Tuple[Path, Dict[str, Any]],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Tests that loading users with invalid data fails."""
        logger.debug("Starting the test: Loading JSON file with invalid data.")
        user_service = cast("UserService", basic_instances["user_service"])
        invalid_file_path, invalid_data = json_with_invalid_data
        current_invalid_data_key = (
            next(iter(invalid_data.keys())) if invalid_data else None
        )

        if current_invalid_data_key is not None:
            invalid_data_str = (
                "Invalid data items: "
                f"'{current_invalid_data_key}: "
                f"{invalid_data[current_invalid_data_key]}'"
            )
        else:
            invalid_data_str = "No invalid data items provided."

        logger.debug(
            "Attempting to load users from JSON file "
            f"'{invalid_file_path}' with invalid data: "
            f"{invalid_data_str}"
        )
        user_service_logger = logging.getLogger("user_management.UserService")
        user_service_logger.addHandler(caplog.handler)
        caplog.clear()
        try:
            with caplog.at_level(logging.ERROR):
                user_service.load_users_from_json(str(invalid_file_path))
        finally:
            user_service_logger.removeHandler(caplog.handler)

        expected_substring = (
            "Skipping invalid user data entry with key "
            f"'{current_invalid_data_key}' in {invalid_file_path}"
        )
        relevant_log_messages = [
            record.message
            for record in caplog.records
            if record.levelno == logging.ERROR
            and record.name == "user_management.UserService"
        ]

        assert any(
            expected_substring in message for message in relevant_log_messages
        ), (
            f"Expected log message not found. Looking for: '{expected_substring}' in "
            f"{relevant_log_messages}"
        )
        assert len(user_service.users_list) == 0, (
            "Users list should remain empty after trying to load from a JSON file "
            "with invalid data."
        )

    # --- export_users_json() test ---

    @allure.feature("User Service")
    @allure.story("JSON Exporting Scenarios")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Verify successful exporting users to JSON file")
    # fmt: off
    @allure.description("""This test verifies that exporting users to JSON file from user service is successful.""")  # noqa: E501
    # fmt: on
    def test_export_users_json(
        self,
        basic_instances: Dict[str, Union["UserService", "User"]],
        json_path_to_export: Path,
    ) -> None:
        """Tests that exporting users to JSON file is successful."""
        logger.debug("Starting the test: Export users in JSON file.")
        user_service = cast("UserService", basic_instances["user_service"])
        user1 = cast("User", basic_instances["user1"])
        user2 = cast("User", basic_instances["user2"])
        user3 = cast("User", basic_instances["user3"])
        user_service.add_user(user1)
        user_service.add_user(user2)
        user_service.add_user(user3)

        logger.debug(
            f"Attempting to export {len(user_service.users_list)} users to JSON file "
            f"path '{json_path_to_export}'"
        )
        user_service.export_users_json(str(json_path_to_export))

        expected_data = {
            str(user1.id): user1.__dict__,
            str(user2.id): user2.__dict__,
            str(user3.id): user3.__dict__,
        }

        assert os.path.exists(json_path_to_export), "JSON file was not created."

        with open(json_path_to_export, "r") as f:
            loaded_data = json.load(f)
        assert loaded_data == expected_data, (
            "Exported data does not match expected data. "
            f"Expected: {expected_data}, got: {loaded_data}"
        )

    @allure.feature("User Service")
    @allure.story("JSON Exporting Scenarios")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify successful exporting users to JSON file with mocked I/O")
    # fmt: off
    @allure.description("""This test verifies that exporting users to JSON file with mocked I/O from user service is successful. The test ensures that exporting users is successful in isolated conditions.""")  # noqa: E501
    # fmt: on
    def test_export_users_mocked_io(
        self,
        basic_instances: Dict[str, Union["UserService", "User"]],
        mocker: MockerFixture,
    ) -> None:
        """Tests export logic without writing to disk."""
        logger.debug(
            "Starting the test: Export users to JSON file with mocked input and output."
        )
        user_service = cast("UserService", basic_instances["user_service"])
        user1 = cast("User", basic_instances["user1"])
        user2 = cast("User", basic_instances["user2"])
        user_service.add_user(user1)
        user_service.add_user(user2)
        mock_file_path = "fake/export.json"

        expected_data_to_dump = {user1.id: user1.__dict__, user2.id: user2.__dict__}

        mock_file_open = mocker.patch("builtins.open", mocker.mock_open())
        mock_dump = mocker.patch("json.dump")

        logger.debug(
            f"Attempting to export {len(user_service.users_list)} users to mocked "
            f"JSON file path: '{mock_file_path}'"
        )
        user_service.export_users_json(mock_file_path)

        mock_file_open.assert_called_once_with(mock_file_path, "w")
        mock_dump.assert_called_once_with(
            expected_data_to_dump, mock_file_open(), indent=4
        )

    @allure.feature("User Service")
    @allure.story("JSON Exporting Scenarios")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Verify unsuccessful exporting users to non-existent directory")
    # fmt: off
    @allure.description("""This test verifies that exporting users to non-existent directory from user service failed correctly.""")  # noqa: E501
    # fmt: on
    def test_export_users_non_existent_dir(
        self, basic_instances: Dict[str, Union["UserService", "User"]]
    ) -> None:
        """Test that exporting users to non-existent directory fails."""
        logger.debug("Staring the test: Export users to non-existent directory.")
        user_service = cast("UserService", basic_instances["user_service"])
        user1 = cast("User", basic_instances["user1"])
        user2 = cast("User", basic_instances["user2"])
        user_service.add_user(user1)
        user_service.add_user(user2)
        non_existent_dir = "non_exist_dir/users.json"

        logger.debug(
            f"Attempting to export users: \n{user_service}In non-existent directory: "
            f"'{non_existent_dir}'"
        )
        with pytest.raises(DataFileWriteError):
            user_service.export_users_json(non_existent_dir)
        assert len(user_service.users_list) == 2, (
            "Users list should remain unchanged after "
            "trying to export to a non-existent directory."
        )

    # --- __str__() test ---

    @allure.feature("User Service")
    @allure.story("User Service String Representation")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.title("Verify successful string representation of the user service")
    # fmt: off
    @allure.description("""This test verifies that string representation of the user service is successful.""")  # noqa: E501
    # fmt: on
    def test_user_service_string_representation(
        self, basic_instances: Dict[str, Union["UserService", "User"]]
    ) -> None:
        """
        Tests that getting UserService instance string representation is successful.
        """
        logger.debug("Starting user service string representation test.")
        user_service = cast("UserService", basic_instances["user_service"])
        user1 = cast("User", basic_instances["user1"])
        user2 = cast("User", basic_instances["user2"])
        user3 = cast("User", basic_instances["user3"])
        user_service.add_user(user1)
        user_service.add_user(user2)
        user_service.add_user(user3)

        expected_strings = [
            f"1. {user1.name} - ID: {user1.id}, Email: {user1.email}",
            f"2. {user2.name} - ID: {user2.id}, Email: {user2.email}",
            f"3. {user3.name} - ID: {user3.id}, Email: {user3.email}",
        ]
        expected_output = "\n".join(expected_strings)

        logger.debug(
            "Attempting to verify whether user service string representation is equal "
            f"to expected output: {expected_output}"
        )
        assert str(user_service) == expected_output, (
            "String representation of the user service does not match expected output. "
            f"Expected: '{expected_output}', got: '{str(user_service)}'"
        )
