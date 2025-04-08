import json
import logging
import logging.config

# logging.config.fileConfig('config/logging.conf')
logger = logging.getLogger(__name__)

class User:
    def __init__(self, id, name, email) -> None:
        self.id = id
        self.name = name
        self.email = email
        
    def __str__(self) -> str:
        return f'{self.name}; id: {self.id}, email: {self.email}.'
        
class UserService:
    def __init__(self) -> None:
        self.users_list = {}
    
    def add_user(self, user):
        if not isinstance(user, User):
            return False
        if user.id in self.users_list:
            return False
        
        self.users_list[user.id] = user
        
    def remove_user_by_id(self, user_id):
        result = self.users_list.pop(user_id, False)
        
        if result:
            return True
        else:
            return False
    
    def __str__(self) -> str:
        output_strings = ''
        for index, user in enumerate(self.users_list):
            output_strings += f'{index + 1}. {user}\n'
            
        return output_strings
    
def import_data_json(file):
    try:
        with open(file, 'r') as outfile:
            try:
                loaded_data = json.load(outfile)
                return loaded_data
            except json.JSONDecodeError:
                print(f'Error: could not decode JSON in file {file}. The file might be corrupted or empty.')
    except FileNotFoundError:
        print(f'The file {file} could not be found.')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')
        
def export_data_json(data, file='users.json'):
    try:
        with open(file, 'w') as infile:
            json.dump(data, infile)
            logger.info(f"Data successfully exported to {file}")
    except TypeError as e:
        logger.error(f'Error during JSON export to {file}: Object of type {type(e.args[0]) if e.args else "unknown"} is not JSON serializable.')
    except OverflowError as e:
        logger.error(f'Error during JSON export to {file}: Numerical value is too large for JSON representation.')
    except UnicodeEncodeError as e:
        logger.error(f'Error during JSON export to {file}: String encoding issue - {e}')
    except Exception as e:
        logger.error(f'An unexpected error occurred during JSON export to {file}: {e}')