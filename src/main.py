import logging
import logging.config
import os
import user_management

script_dir = os.path.dirname(__file__)
config_file_path = os.path.join(script_dir, '..', 'config', 'logging.ini')
log_dir = os.path.join(script_dir, '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.config.fileConfig(config_file_path, disable_existing_loggers=False)

logger = logging.getLogger('main_app')

def main():
    logger.info("Main application starting.")
    user1 = user_management.User(1, 'Alice Hetun', 'alice@example.com')
    user2 = user_management.User(2, 'Bob Smith', 'bob@example.com')

    user_service = user_management.UserService()
    user_service.add_user(user1)
    user_service.add_user(user2)

    logger.info("Exporting users...")
    user_service.export_users_json()

    logger.info("Loading users from JSON...")
    user_service.load_users_from_json(file_path='data/users.json', clear_users_list=True)

    if user_service.users_list:
        logger.info("User data loaded successfully.")
        logger.info(f"Users after loading:\n{user_service}")
    else:
        logger.warning("Failed to load user data from JSON.")

    logger.info("Main application finished.")

if __name__ == '__main__':
    main()