import json
import logging
import os
import sys

class User:
    # Use the consistent module name prefix
    logger = logging.getLogger('user_management.' + __qualname__)
    def __init__(self, id, name, email) -> None:
        self.id = id
        self.name = name
        self.email = email
        User.logger.debug(f"User object created: {self}")

    def __str__(self) -> str:
        return f'{self.name}; id: {self.id}, email: {self.email}.'

class UserService:
    # Use the consistent module name prefix
    logger = logging.getLogger('user_management.' + __qualname__)
    def __init__(self) -> None:
        UserService.logger.info("UserService initialized.")
        self.users_list = {}

    def add_user(self, user):
        UserService.logger.debug(f"Attempting to add user: {user}")
        if not isinstance(user, User):
            UserService.logger.warning(f"Attempted to add non-User object: {user}")
            return False
        if user.id in self.users_list:
            UserService.logger.warning(f"User with ID {user.id} already exists.")
            return False
        self.users_list[user.id] = user
        UserService.logger.info(f"User added: {user}")
        return True

    def remove_user_by_id(self, user_id):
        UserService.logger.debug(f"Attempting to remove user with ID: {user_id}")
        removed_user = self.users_list.pop(user_id, None)
        if removed_user:
            UserService.logger.info(f"User removed: {removed_user}")
            return True
        else:
            UserService.logger.warning(f"User with ID {user_id} not found.")
            return False

    def load_users_from_json(self, file='data/users.json', clear_users_list=False):
        base_dir = os.path.join(os.path.dirname(__file__), '..')
        file_path = os.path.join(base_dir, file) # Renamed variable to avoid conflict
        UserService.logger.info(f"Attempting to load user data from: {file_path}")
        try:
            with open(file_path, 'r') as outfile:
                try:
                    loaded_data = json.load(outfile)
                    UserService.logger.info(f"Data successfully imported from {file_path}")
                except json.JSONDecodeError as e:
                    UserService.logger.error(f'Error decoding JSON in {file_path}: {e}', exc_info=True)
                    return False

            if clear_users_list:
                self.users_list.clear()
                UserService.logger.debug("Cleared existing user list before loading.")

            users_loaded_count = 0
            for user_id, user_data in loaded_data.items():
                try:
                    user = User(id=user_data['id'], name=user_data['name'], email=user_data['email'])
                    self.users_list[user.id] = user
                    users_loaded_count += 1
                except KeyError as e:
                    UserService.logger.error(f"Missing key {e} in user data for ID {user_id} in {file_path}", exc_info=True)
                    # Decide if one error should stop the whole load? Maybe continue?
                    # return False # Stops loading on first error
                except Exception as e:
                    UserService.logger.error(f"Error creating User object for ID {user_id} in {file_path}: {e}", exc_info=True)
                    # return False # Stops loading on first error

            UserService.logger.info(f"{users_loaded_count} user(s) data successfully processed from {file_path}")
            return True
        except FileNotFoundError:
            UserService.logger.error(f'File not found: {file_path}.', exc_info=True)
            return False
        except Exception as e:
            UserService.logger.error(f"Failed to load users from {file_path}: {e}", exc_info=True)
            return False

    def export_users_json(self, file='data/users.json'):
        base_dir = os.path.join(os.path.dirname(__file__), '..')
        file_path = os.path.join(base_dir, file)
        UserService.logger.info(f"Attempting to export user data to: {file_path}")
        try:
            data_to_export = {user_id: user.__dict__ for user_id, user in self.users_list.items()}
            with open(file_path, 'w') as infile:
                json.dump(data_to_export, infile, indent=4)
                UserService.logger.info(f"User data successfully exported to {file_path}")
                
        except TypeError as e:
            UserService.logger.error(f'Error during JSON export to {file_path}: Object of type {type(e).__name__} is not JSON serializable. Details: {e}', exc_info=True)
        except OverflowError as e:
            UserService.logger.error(f'Error during JSON export to {file_path}: Numerical value is too large for JSON. Details: {e}', exc_info=True)
        except UnicodeEncodeError as e:
            UserService.logger.error(f'Error during JSON export to {file_path}: String encoding issue. Details: {e}', exc_info=True)
        except Exception as e:
            UserService.logger.error(f'An unexpected error occurred during export to {file_path}: {e}', exc_info=True)

    def __str__(self) -> str:
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