import json
import logging
import threading
import re

"""Manages user data including loading, saving, and manipulation."""


class DuplicateUserError(ValueError):
    """Exception raised when attempting to add a user with an ID that already exists."""
    pass


class UserNotFoundError(ValueError):
    """Exception raised when a user with a specified ID is not found in the service."""
    pass


class DataFileReadError(OSError):
    """Exception raised for unexpected errors during data file reading."""
    pass


class DataFileWriteError(OSError):
    """Exception raised for unexpected errors during data file writing."""
    pass


class User:
    """Represents a user with an ID, name, and email address.

    Attributes:
        id (int): The unique identifier for the user.
        name (str): The name of the user.
        email (str): The email address of the user.
    """

    logger = logging.getLogger("user_management." + __qualname__)

    _ALLOWED_NAME_CHARS_PATTERN = re.compile(r"^[a-zA-Z .'-]+$")

    def _validate_id(self, id: int) -> None:
        """ID validation for User instance."""
        if not isinstance(id, int):
            self.logger.error(
                f"Invalid type for User ID: Expected int, got {type(id).__name__}"
            )
            raise TypeError(f"User ID must be an integer, got {type(id).__name__}")
        if id < 1:
            self.logger.error(f"Invalid value for User ID: Must be positive, got {id}")
            raise ValueError(f"User ID must be a positive integer, got {id}")

    def _validate_name(self, name: str) -> str:
        """Name validation for User instance. Returns a cleaned name."""
        if not isinstance(name, str):
            self.logger.error(
                f"Invalid type for User name: Expected str, got {type(name).__name__}"
            )
            raise TypeError(f"User name must be a string, got {type(name).__name__}")

        cleaned_name = name.strip()

        if not cleaned_name:
            self.logger.error(
                "Invalid value for User name: Cannot be empty or whitespace only"
            )
            raise ValueError("User name cannot be empty or whitespace only")
        if not self._ALLOWED_NAME_CHARS_PATTERN.fullmatch(cleaned_name):
            self.logger.error(
                f"Invalid value for User name: Contains disallowed characters, "
                f"got '{cleaned_name}'"
            )
            raise ValueError(
                "User name contains disallowed characters. Only letters, spaces, "
                "hyphens, apostrophes, and periods are allowed."
            )
        if len(cleaned_name) < 4:
            self.logger.error(
                f"Invalid value for User name: Length less than 4, "
                f"got {len(cleaned_name)}"
            )
            raise ValueError(
                f"User name length cannot be less than 4, got {len(cleaned_name)}"
            )
        if len(cleaned_name) > 70:
            self.logger.error(
                f"Invalid value for User name: Length greater than 70, "
                f"got {len(cleaned_name)}"
            )
            raise ValueError(
                f"User name length cannot be longer than 70, got {len(cleaned_name)}"
            )

        return cleaned_name

    def _validate_email(self, email: str) -> None:
        if not isinstance(email, str):
            self.logger.error(
                f"Invalid type for User email: Expected str, got {type(email).__name__}"
            )
            raise TypeError(f"User email must be a string, got {type(email).__name__}")

    def __init__(self, id: int, name: str, email: str) -> None:
        """Initializes a User instance with validation.

        Args:
            id: The user's unique integer ID.
            name: The user's non-empty string name (min 4, max 70 chars).
            email: The user's email address (expected to be a string).

        Raises:
            TypeError: If id, name, or email have incorrect types.
            ValueError: If id is not positive, or name is empty/whitespace-only,
                        violates character rules, or violates length constraints.
        """
        self._validate_id(id)
        cleaned_name = self._validate_name(name)
        self._validate_email(email)

        self.id = id
        self.name = cleaned_name
        self.email = email
        self.logger.debug(
            f"User object created successfully: "
            f"ID={self.id}, Name='{self.name}', Email='{self.email}'"
        )

    def __str__(self) -> str:
        """Returns a string representation of the User."""
        return f"{self.name} - ID: {self.id}, Email: {self.email}"


class UserService:
    """Manages a collection of User objects.

    Provides functionality to add, remove, load, and export user data.

    Attributes:
        users_list (dict[int, User]): A dictionary mapping user IDs to User objects.
    """

    logger = logging.getLogger("user_management." + __qualname__)

    def __init__(self) -> None:
        """Initializes the UserService with an empty user list."""
        self.logger.info("UserService initialized.")
        self.users_list = {}
        self._lock = threading.Lock()

    def add_user(self, user: User) -> None:
        """Adds a user to the service collection.

        Args:
            user: The User object to add.

        Raises:
            TypeError: If the provided object is not a User instance.
            DuplicateUserError: If a user with the same ID already exists.
        """
        self.logger.debug(f"Attempting to add user of type {type(user).__name__}.")
        if not isinstance(user, User):
            msg = f"Expected a User object, got {type(user).__name__}"
            self.logger.error(msg)
            raise TypeError(msg)

        self.logger.debug(
            f"User (ID: {user.id}) is a valid User object. Preparing to acquire lock."
        )
        with self._lock:
            self.logger.debug(f"Lock acquired for user ID {user.id}.")
            if user.id in self.users_list:
                msg = f"User with ID {user.id} already exists."
                self.logger.warning(msg)
                raise DuplicateUserError(msg)

            self.users_list[user.id] = user
            self.logger.info(f"User added: {user}")

    def remove_user_by_id(self, user_id: int) -> None:
        """Removes a user from the service by their ID.

        Args:
            user_id: The integer ID of the user to remove.

        Raises:
            UserNotFoundError: If no user with the specified ID is found.
        """
        with self._lock:
            self.logger.debug(f"Lock acquired for user ID {user_id}.")
            self.logger.debug(f"Attempting to remove user with ID: {user_id}")

            removed_user = self.users_list.pop(user_id, None)
            if removed_user:
                self.logger.info(f"User removed: {removed_user}")
            else:
                msg = f"User with ID {user_id} not found."
                self.logger.error(msg)
                raise UserNotFoundError(msg)

    def load_users_from_json(
        self, file_path: str, clear_users_list: bool = False
    ) -> None:
        """Loads user data from a JSON file into the service.

        Replaces existing users if IDs conflict during loading
        Skips entries with invalid data format or missing keys, logging errors.

        Args:
            file_path: The path to the JSON file to load.
            clear_users_list: If True, clears the existing user list before loading.
                              Defaults to False.

        Raises:
            FileNotFoundError: If the specified file_path does not exist.
            json.JSONDecodeError: If the file contains invalid JSON.
            DataFileReadError: If an operating system-level error occurs during file
                               reading (e.g., permission denied, attempting to read a
                               directory).
        """
        self.logger.info(f"Attempting to load user data from: {file_path}")

        loaded_raw_data = None
        try:
            with open(file_path, "r") as infile:
                loaded_raw_data = json.load(infile)
            self.logger.info(f"Raw data successfully loaded from {file_path}")
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}.", exc_info=True)
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON in {file_path}: {e}", exc_info=True)
            raise
        except OSError as e:
            self.logger.error(
                f"File reading OS error during import {file_path}: {e}",
                exc_info=True,
            )
            raise DataFileReadError(f"Failed to read data file {file_path}") from e

        if not isinstance(loaded_raw_data, dict):
            msg = f"Root of JSON file {file_path} is not a dictionary."
            self.logger.error(msg)
            raise TypeError(msg)

        new_users_temp_dict = {}
        users_failed_in_preparation = 0
        self.logger.debug(f"Processing {len(loaded_raw_data)} entries for preparation.")

        for user_id_str, user_data in loaded_raw_data.items():
            try:
                if not isinstance(user_data, dict):
                    raise TypeError(
                        f"User data for key '{user_id_str}' is not a dictionary."
                    )

                user_id = int(user_id_str)
                if "id" not in user_data:
                    raise KeyError(
                        f"Missing 'id' key for user with key '{user_id_str}'."
                    )
                if user_id != user_data.get("id"):
                    raise ValueError(
                        f"ID mismatch: key='{user_id_str}', "
                        f"data_id={user_data.get('id')}. Expected {user_id}"
                    )

                user = User(
                    id=user_data["id"],
                    name=user_data["name"],
                    email=user_data["email"],
                )

                new_users_temp_dict[user.id] = user

            except (KeyError, ValueError, TypeError) as e:
                users_failed_in_preparation += 1
                self.logger.error(
                    (
                        f"Skipping invalid user data entry with key '{user_id_str}' "
                        f"in {file_path} during preparation: {e}"
                    ),
                    exc_info=False,
                )

        with self._lock:
            self.logger.debug(
                f"Lock acquired for atomic update of users_list from {file_path}."
            )

            if clear_users_list:
                self.users_list.clear()
                self.logger.debug("Cleared existing user list before atomic update.")

            for user_id, new_user in new_users_temp_dict.items():
                if user_id in self.users_list:
                    self.logger.info(f"Overwriting existing user with ID {user_id}.")

            self.users_list.update(new_users_temp_dict)

            self.logger.info(
                (
                    f"Finished atomic update from {file_path}: "
                    f"{len(new_users_temp_dict)} users loaded/updated, "
                    f"{users_failed_in_preparation} entries skipped during preparation."
                )
            )

            self.logger.debug(f"Lock released after atomic update from {file_path}.")

    def export_users_json(self, file_path="data/users.json") -> None:
        """Exports the current user list to a JSON file.

        Saves user data in JSON format. Catches specific JSON serialization errors
        and raises a custom DataFileWriteError for underlying OS-level file writing
        issues.

        Args:
            file_path: The path to the JSON file where users will be saved.

        Raises:
            TypeError: If user data is not JSON serializable.
            OverflowError: If numerical data is too large for JSON.
            UnicodeEncodeError: If there's an issue encoding strings for the file.
            DataFileWriteError: If an operating system-level error occurs during file
                                writing (e.g., permission denied, disk full, directory
                                doesn't exist).
        """
        self.logger.info(f"Attempting to export users data to: {file_path}")

        with self._lock:
            self.logger.debug("Lock acquired for data snapshot for export.")
            users_to_export = {
                user_id: user.__dict__ for user_id, user in self.users_list.items()
            }
        self.logger.debug("Lock released after data snapshot for export.")

        if not users_to_export:
            self.logger.info("No users to export.")
            return

        try:
            with open(file_path, "w") as outfile:
                json.dump(users_to_export, outfile, indent=4)
            self.logger.info(f"User data successfully exported to {file_path}")
        except TypeError as e:
            self.logger.error(
                (
                    f"Error during JSON export to {file_path}: "
                    f"Object of type {type(e).__name__} is not JSON serializable. "
                    f"Details: {e}"
                ),
                exc_info=True,
            )
            raise
        except OverflowError as e:
            self.logger.error(
                (
                    f"Error during JSON export to {file_path}: "
                    f"Numerical value is too large for JSON. Details: {e}"
                ),
                exc_info=True,
            )
            raise
        except UnicodeEncodeError as e:
            self.logger.error(
                (
                    f"Error during JSON export to {file_path}: "
                    f"String encoding issue. Details: {e}"
                ),
                exc_info=True,
            )
            raise
        except OSError as e:
            self.logger.error(
                (
                    f"File writing OS error during export to {file_path}. "
                    f"Details: {e}"
                ),
                exc_info=True,
            )
            raise DataFileWriteError(
                f"Failed to write data file {file_path}. Details: {e}"
            ) from e

    def __str__(self) -> str:
        """Returns a string representation of the users currently in the service."""
        with self._lock:
            users_for_display = list(self.users_list.values())

        output_strings = []
        if not users_for_display:
            return "No users in service."

        for index, user in enumerate(users_for_display):
            output_strings.append(f"{index + 1}. {user}")

        return "\n".join(output_strings)


if __name__ == "__main__":
    # Configure basic logging for direct execution
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    user_mgmt_logger = logging.getLogger("user_management.UserService")
    user_mgmt_logger.setLevel(logging.DEBUG)

    print("--- Running user_management.py directly ---")
    user1 = User(101, "Test Alice", "test_alice@example.com")
    user2 = User(102, "Test Bob", "test_bob@example.com")
    user_service = UserService()
    user_service.add_user(user1)
    user_service.add_user(user2)
    print(f"Direct run - Current users:\n{user_service}")
    user_service.remove_user_by_id(101)
    print(f"Direct run - Users after removal:\n{user_service}")
    print("--- User management direct run finished ---")
