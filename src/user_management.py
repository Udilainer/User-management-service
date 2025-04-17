import json
import logging
import os
import sys
import re

"""Manages user data including loading, saving, and manipulation."""

class DuplicateUserError(ValueError):
    """Exception raised when attempting to add a user with an ID that already exists."""
    pass

class DataFileReadError(IOError):
    """Exception raised for unexpected errors during data file reading."""
    pass

class User:
    """Represents a user with an ID, name, and email address.

    Attributes:
        id (int): The unique identifier for the user.
        name (str): The name of the user.
        email (str): The email address of the user.
    """
    logger = logging.getLogger('user_management.' + __qualname__)
    
    def __init__(self, id: int, name: str, email: str) -> None:
        """Initializes a User instance with validation.

        Args:
            id: The user's unique integer ID.
            name: The user's non-empty string name.
            email: The user's non-empty string email in a valid format.

        Raises:
            TypeError: If id, name, or email have incorrect types.
            ValueError: If name or email are empty, or if email format is invalid.
        """
        if not isinstance(id, int):
            raise TypeError(f"User ID must be an integer, got {type(id).__name__}")
        if not isinstance(name, str):
            raise TypeError(f"User name must be a string, got {type(name).__name__}")
        if not name:
            raise ValueError(f"User name cannot be empty")
        if not isinstance(email, str):
            raise TypeError(f"User email must be a string, got {type(email).__name__}")
        if not email:
            raise ValueError(f"User email cannot be empty")
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.fullmatch(email_regex, email):
            raise ValueError(f"User email has an invalid format: {email}")
        
        self.id = id
        self.name = name
        self.email = email
        User.logger.debug(f"User object created: {self}")

    def __str__(self) -> str:
        """Returns a string representation of the User."""
        return f"{self.name} - ID: {self.id}, Email: {self.email}"

class UserService:
    """Manages a collection of User objects.

    Provides functionality to add, remove, load, and export user data.

    Attributes:
        users_list (dict[int, User]): A dictionary mapping user IDs to User objects.
    """
    logger = logging.getLogger('user_management.' + __qualname__)
    
    def __init__(self) -> None:
        """Initializes the UserService with an empty user list."""
        UserService.logger.info("UserService initialized.")
        self.users_list = {}

    def add_user(self, user: User) -> None:
        """Adds a user to the service collection.

        Args:
            user: The User object to add.

        Raises:
            TypeError: If the provided object is not a User instance.
            DuplicateUserError: If a user with the same ID already exists.
        """
        UserService.logger.debug(f"Attempting to add user: {user}")
        
        if not isinstance(user, User):
            msg = f"Expected a User object, got {type(user).__name__}"
            UserService.logger.error(msg)
            raise TypeError(msg)
        
        if user.id in self.users_list:
            msg = f"User with ID {user.id} already exists."
            UserService.logger.warning(msg)
            raise DuplicateUserError(msg)
        
        self.users_list[user.id] = user
        UserService.logger.info(f"User added: {user}")

    def remove_user_by_id(self, user_id: int) -> None:
        """Removes a user from the service by their ID.

        Args:
            user_id: The integer ID of the user to remove.

        Raises:
            ValueError: If no user with the specified ID is found.
        """
        UserService.logger.debug(f"Attempting to remove user with ID: {user_id}")
        
        removed_user = self.users_list.pop(user_id, None)
        if removed_user:
            UserService.logger.info(f"User removed: {removed_user}")
        else:
            msg = f"User with ID {user_id} not found."
            UserService.logger.error(msg)
            raise ValueError(msg)

    def load_users_from_json(self, file_path: str, clear_users_list: bool = False) -> None:
        """Loads user data from a JSON file into the service.

        Overwrites existing users if IDs conflict during loading (assuming modification).
        Skips entries with invalid data format or missing keys, logging errors.

        Args:
            file_path: The path to the JSON file to load.
            clear_users_list: If True, clears the existing user list before loading.
                              Defaults to False.

        Raises:
            FileNotFoundError: If the specified file_path does not exist.
            json.JSONDecodeError: If the file contains invalid JSON.
            DataFileReadError: For other unexpected errors during file reading.
            # Note: Add mention if it can raise DuplicateUserError based on implementation
        """
        UserService.logger.info(f"Attempting to load user data from: {file_path}")

        try:
            with open(file_path, 'r') as outfile:
                loaded_data = json.load(outfile)
            UserService.logger.info(f"Raw data successfully loaded from {file_path}")
        except FileNotFoundError as e:
            UserService.logger.error(f'File not found: {file_path}.', exc_info=True)
            raise
        except json.JSONDecodeError as e:
            UserService.logger.error(f'Error decoding JSON in {file_path}: {e}', exc_info=True)
            raise
        except Exception as e:
            UserService.logger.error(f"Unexpected error reading file {file_path}: {e}", exc_info=True)
            raise DataFileReadError(f"Failed to read data file {file_path}") from e

        if clear_users_list:
            self.users_list.clear()
            UserService.logger.debug("Cleared existing user list before loading.")

        users_loaded_count = 0
        users_failed_count = 0
        UserService.logger.debug(f"Processing {len(loaded_data)} entries from file.")

        for user_id_str, user_data in loaded_data.items():
            try:
                if not isinstance(user_data, dict):
                    raise TypeError(f"User data for key '{user_id_str}' is not a dictionary.")

                user_id = int(user_id_str)
                if user_id != user_data.get('id'):
                    raise ValueError(f"ID mismatch: key='{user_id_str}', data_id={user_data.get('id')}")

                user = User(id=user_data['id'], name=user_data['name'], email=user_data['email'])
                
                if user.id in self.users_list:
                     UserService.logger.warning(f"Duplicate user ID {user.id} found while loading from {file_path}. Overwriting.")
                self.users_list[user.id] = user
                users_loaded_count += 1

            except (KeyError, ValueError, TypeError) as e:
                users_failed_count += 1
                UserService.logger.error(f"Skipping invalid user data entry with key '{user_id_str}' in {file_path}: {e}", exc_info=False)

        UserService.logger.info(f"Finished processing {file_path}: {users_loaded_count} users loaded, {users_failed_count} entries skipped.")

        # Optional: Raise an error if any entries failed to load
        # if users_failed_count > 0:
        #     raise ValueError(f"Encountered {users_failed_count} invalid entries in {file_path}")

    def export_users_json(self, file_path='data/users.json') -> None:
        """Exports the current user list to a JSON file.

        Args:
            file_path: The path to the JSON file where users will be saved.

        Raises:
            TypeError: If user data is not JSON serializable (shouldn't happen with User).
            OverflowError: If numerical data is too large for JSON.
            UnicodeEncodeError: If there's an issue encoding strings.
            Exception: For other unexpected errors during file writing or export.
                      (Consider wrapping this in a custom DataFileWriteError)
        """
        UserService.logger.info(f"Attempting to export users data to: {file_path}")
        
        try:
            users_to_export = {user_id: user.__dict__ for user_id, user in self.users_list.items()}
            
            if users_to_export:
                with open(file_path, 'w') as infile:
                    json.dump(users_to_export, infile, indent=4)
                    UserService.logger.info(f"User data successfully exported to {file_path}")
            else:
                UserService.logger.info(f"No users to export.")
                
        except TypeError as e:
            UserService.logger.error(f'Error during JSON export to {file_path}: Object of type {type(e).__name__} is not JSON serializable. Details: {e}', exc_info=True)
        except OverflowError as e:
            UserService.logger.error(f'Error during JSON export to {file_path}: Numerical value is too large for JSON. Details: {e}', exc_info=True)
        except UnicodeEncodeError as e:
            UserService.logger.error(f'Error during JSON export to {file_path}: String encoding issue. Details: {e}', exc_info=True)
        except Exception as e:
            UserService.logger.error(f'An unexpected error occurred during export to {file_path}: {e}', exc_info=True)

    def __str__(self) -> str:
        """Returns a string representation of the users currently in the service."""
        output_strings = ''
        for index, user in enumerate(self.users_list.values()):
            output_strings += f'{index + 1}. {user}\n'
        return output_strings

# --- Main execution block ---
# This block should ideally be for testing this module specifically,
# it shouldn't configure logging again if main.py is the entry point.
# If you run this file directly, it *won't* have logging configured unless you add it here.
if __name__ == '__main__':
    # OPTION 1: Configure logging here if running directly (duplicates config logic)
    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # OR load from file specific for testing this module?

    # OPTION 2: Assume logging is configured by whatever runs this block
    # (Requires running it via a script that already configured logging)

    print("--- Running user_management.py directly ---")
    # Example usage without relying on prior logging config:
    user1 = User(101, 'Test Alice', 'test_alice@example.com')
    user2 = User(102, 'Test Bob', 'test_bob@example.com')
    user_service = UserService()
    user_service.add_user(user1)
    user_service.add_user(user2)
    print(f"Direct run - Current users:\n{user_service}")
    user_service.remove_user_by_id(101)
    print(f"Direct run - Users after removal:\n{user_service}")
    # Note: Logging inside methods might not output if logging isn't configured when run directly.
    print("--- User management direct run finished ---")