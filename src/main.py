import logging
import logging.config
import os
import user_management

# --- Configure Logging ---
# BEST PRACTICE: Configure logging ONCE at the application entry point.
script_dir = os.path.dirname(__file__)
config_file_path = os.path.join(script_dir, '..', 'config', 'logging.conf')
log_dir = os.path.join(script_dir, '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.config.fileConfig(config_file_path, disable_existing_loggers=False)

# Get the logger for this module
logger = logging.getLogger('main_app')

def main():
    logger.info("Main application starting.")
    user1 = user_management.User(1, 'Alice', 'alice@example.com')
    user2 = user_management.User(2, 'Bob', 'bob@example.com')

    user_service = user_management.UserService()
    user_service.add_user(user1)
    user_service.add_user(user2)

    logger.info("Exporting users...")
    user_service.export_users_json()

    logger.info("Loading users from JSON...")
    success = user_service.load_users_from_json('data/users.json', clear_users_list=True)

    if success:
        logger.info("User data loaded successfully.")
        logger.info(f"Users after loading:\n{user_service}")
    else:
        logger.warning("Failed to load user data from JSON.")

    logger.info("Main application finished.")

if __name__ == '__main__':
    main()