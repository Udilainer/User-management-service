import pytest
import json
import os
import logging
import allure
from src.user_management import User, DuplicateUserError, DataFileWriteError

logger = logging.getLogger(__name__)

class TestUser:
    
    # --- __init__() test ---
    
    @allure.feature("User")
    @allure.story("User Input Validation")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Verify successful user initialization with valid IDs")
    @allure.description("""
        This parameterized test verifies that a user can be initialized with 
        various valid IDs. It includes checking the ID starting from a single-digit 
        minimum value up to a five-digit value.""")
    @pytest.mark.parametrize("various_valid_id, valid_name, valid_email", [
        (1, "Karl Gekot", "karlgekot435@example.com"),
        (48, "Stive Jarviz", "stivejarviz@example.com"),
        (535, "Yun Heihachi", "yunheihachi324@example.com"),
        (6244, "Nick Rijo", "nickrijo245@example.com"),
        (91425, "Ben Graz", "bengraz244@example.com")
    ])
    def test_user_init_valid_ids(self, various_valid_id, valid_name, valid_email):
        """Tests user initialization with various ID inputs."""
        logger.debug(f"Starting user initialization test with valid ID: {various_valid_id}")
        user = User(various_valid_id, valid_name, valid_email)
        
        assert user.id == various_valid_id
        assert user.name == valid_name
        assert user.email == valid_email
        logger.debug("User initialization with valid ID is successful.")
    
    @allure.feature("User")
    @allure.story("User Input Validation")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Verify successful user initialization with valid names")
    @allure.description("""
        This parameterized test verifies that a user can be initialized with various 
        valid names. It includes minimum, average and maximum name length.""")
    @pytest.mark.parametrize("valid_id, various_valid_name, valid_email", [
        (15, "John", "bobjohnson@example.com"), # Name length 4
        (25, "Elizabeth Anne Marie Rodriguez-Garc", "elizabet@example.com"), # Name length 35
        (67, "Christopher Alexander Michael Jonathan David Williams-Johnson-Smith-Br", "william@example.com") # Name length 70
    ])
    def test_user_init_valid_names(self, valid_id, various_valid_name, valid_email):
        """Tests user initialization with various name length inputs."""
        logger.debug(f"Starting user initialization test with valid name: {various_valid_name}")
        user = User(valid_id, various_valid_name, valid_email)
        
        assert user.id == valid_id
        assert user.name == various_valid_name
        assert user.email == valid_email
        logger.debug("User initialization with valid name is successful.")
    
    @allure.feature("User")
    @allure.story("User Input Validation")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Verify successful user initialization with valid emails")
    @allure.description("""
        This parameterized test verifies that a user can be initialized with various 
        valid emails. It includes minimum, average and maximum email length.""")
    @pytest.mark.parametrize("valid_id, valid_name, various_valid_email", [
        (33, "Short Email User", "a@b.co"), # Email length 6
        (55, "Standard Email Name", "standardusernamehere123@example.com"), # Email length 35
        (70, "Very Long Email Example", "verylongusernameexampleherenownow13452@example.com") # Email length 50
    ])
    def test_user_init_valid_emails(self, valid_id, valid_name, various_valid_email):
        """Tests user initialization with various email length inputs."""
        logger.debug(f"Starting user initialization test with valid email: {various_valid_email}")
        user = User(valid_id, valid_name, various_valid_email)
        
        assert user.id == valid_id
        assert user.name == valid_name
        assert user.email == various_valid_email
        logger.debug("User initialization with valid email is successful.")
        
    @allure.feature("User")
    @allure.story("User Input Validation")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify unsuccessful user initialization with invalid input types")
    @allure.description("""
        This parameterized test verifies that a user cannot be initialized with various 
        invalid input types. It includes invalid types of all inputs.""")
    @pytest.mark.parametrize("id, name, email", [
        ('invalid_id', "Fiona Gallagher", "fionagallagher@example.com"), # Invalid ID type
        (2109, ["George Costanza"], "georgecostanza123@example.com"), # Invalid name type
        (55, "Holly Golightly", {'email': "hollygolightly@example.com"}), # Invalid email type
    ])
    def test_user_init_invalid_input_types(self, id, name, email):
        """Tests user initialization with various invalid input types."""
        logger.debug(f"Starting user initialization test with invalid input type.")
        logger.debug(f"Attempting initialize with ID: {id} (type: {type(id).__name__}), "
                     f"name: {name} (type: {type(name).__name__}), "
                     f"email: {email} (type: {type(email).__name__})")
        with pytest.raises(TypeError):
            user = User(id, name, email)
        logger.debug(f"Initialization failed correctly with input types: ID={type(id).__name__}, "
                    f"Name={type(name).__name__}, "
                    f"Email={type(email).__name__}. "
                    f"Expected TypeError was correctly raised.")
            
    @allure.feature("User")
    @allure.story("User Input Validation")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify unsuccessful user initialization with empty inputs")
    @allure.description("""
        This parameterized test verifies that a user cannot be initialized with empty input 
        types. It includes empty name and email inputs.""")
    @pytest.mark.parametrize("id, name, email", [
        (3, "", "jasminekhan@example.com"), # Empty name
        (1123, "Kevin McCallister", ""), # Empty email
    ])
    def test_user_init_empty_inputs(self, id, name, email):
        """Tests user initialization with various empty inputs."""
        logger.debug(f"Starting user initialization test with empty input.")
        logger.debug(f"Attempting initialize with ID='{id}', name='{name}', email='{email}'")
        with pytest.raises(ValueError):
            user = User(id, name, email)
        logger.debug(f"Initialization with empty {'name' if not name else 'email'} input failed correctly.")

    @allure.feature("User")
    @allure.story("User Input Validation")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify unsuccessful user initialization with invalid emails")
    @allure.description("""
        This parameterized test verifies that a user cannot be initialized with various invalid 
        emails. It includes all possible types of invalid email inputs.""")
    @pytest.mark.parametrize("valid_id, valid_name, various_invalid_email", [
        (65, "Leia Organa", "@example.com"), # Email with no local part
        (77, "Oscar Martinez", "oscarmartinezexample.com"), # Email without '@'
        (4902, "Michael Scott", "michaelscott@.com"), # Email with no domain name
        (203, "Rachel Green", "rachelgreen222@"), # Email with no domain part
        (1, "Nancy Drew", "nancydrew999@example$.com"), # Email with incorect character ($) in domain name
        (3456, "Pam Beesly", "pambeesly111@example.%com"), # Email with incorect character (%) in TLD
        (9, "Quentin Tarantino", "quentintarantino@examplecom"), # Email without dot in domain part
        (5876, "Sheldon Cooper", "sheldoncooper@example."), # Email without TLD
    ])
    def test_user_init_invalid_emails(self, valid_id, valid_name, various_invalid_email):
        """Tests user initialization with various invalid email inputs."""
        logger.debug(f"Starting user initialization test with invalid email.")
        logger.debug(f"Attempting initialize with ID='{valid_id}', name='{valid_name}', email='{various_invalid_email}'")
        with pytest.raises(ValueError):
            user = User(valid_id, valid_name, various_invalid_email)
        logger.debug(f"Initialization with invalid email: {various_invalid_email} failed correctly.")
            
    # --- __str__() test ---

    @allure.feature("User")
    @allure.story("User String Representation")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.title("Verify successful string representation of the user")
    @allure.description("""
        This test verifies that a string representation of the user is successful and correct.""")
    def test_user_string_representation(self):
        """Tests that getting User instance string representation is successful."""
        logger.debug(f"Starting user string representation test.")
        user_id = 4
        user_name = "Veronica Mars"
        user_email = "veronicamars@example.com"
        user = User(user_id, user_name, user_email)
        expected_string = f"{user_name} - ID: {user_id}, Email: {user_email}"
        logger.debug(f"Attempting to get a string representation with user attributes: ID='{user_id}', name='{user_name}', email='{user_email}'. "
                     f"Expected string: '{expected_string}'")
        assert str(user) == expected_string
        logger.debug(f"Getting string representation with user attributes ID='{user_id}', name='{user_name}', email='{user_email}' is successful.")
        
class TestUserService:
    
    # --- add_user() test ---
    
    @allure.feature("User Service")
    @allure.story("User Addition Scenarios")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Verify successful user addition with valid inputs")
    @allure.description("""
        This test verifies that a user addition to user service is successful.""")
    def test_add_user(self, basic_instances):
        """Tests that adding a user is successful."""
        logger.debug(f"Starting user addition test.")
        user_service = basic_instances['user_service']
        user1 = basic_instances['user1']
        logger.debug(f"Attempting to add user {user1}")
        user_service.add_user(basic_instances['user1'])
        
        assert user1.id in user_service.users_list
        logger.debug(f"User addition with user {user1} is successful.")
        
    @allure.feature("User Service")
    @allure.story("User Addition Scenarios")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify unsuccessful non-user object addition")
    @allure.description("""
        This test verifies that a non-user object addition to user service failed correctly.""")
    def test_add_non_user_object(self, basic_instances):
        """Tests that adding a non-user object raises TypeError."""
        logger.debug(f"Starting non-user object addition test.")
        user_service = basic_instances['user_service']
        non_user_instance = 'user1'
        
        logger.debug(f"Attempting to add non-user object with {type(non_user_instance).__name__} type.")
        with pytest.raises(TypeError):
            user_service.add_user(non_user_instance)
            
        assert len(user_service.users_list) == 0
        logger.debug(f"Addition of non-user object with {type(non_user_instance).__name__} type failed correctly.")

    @allure.feature("User Service")
    @allure.story("User Addition Scenarios")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify unsuccessful existent user addition")
    @allure.description("""
        This test verifies that a existent user addition to user service failed correctly.""")
    def test_add_exist_user(self, basic_instances):
        """Tests that adding a user with an ID that already exists raises DuplicateUserError."""
        logger.debug(f"Starting existing user addition test.")
        user_service = basic_instances['user_service']
        user1 = basic_instances['user1']
        user_service.add_user(user1)
        
        logger.debug(f"Attempting to add existing user {user1}")
        with pytest.raises(DuplicateUserError):
            user_service.add_user(user1)
        assert len(user_service.users_list) == 1
        logger.debug(f"Addition of existing user {user1} failed correctly.")
        
    # --- remove_user_by_id() test ---

    @allure.feature("User Service")
    @allure.story("User Removal Scenarios")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify successful user removal")
    @allure.description("""
        This test verifies that a user removal from user service is successful.""")
    def test_remove_user_by_id(self, basic_instances):
        """Tests that removing user by ID is successful."""
        logger.debug(f"Starting user removal by ID test.")
        user_service, user1, user2, user3 = basic_instances.values()
        user_service.add_user(user1)
        user_service.add_user(user2)
        user_service.add_user(user3)
        logger.debug(f"Attempting to remove user with ID {user1.id}")
        user_service.remove_user_by_id(user1.id)
        
        assert len(user_service.users_list) == 2
        assert not user1.id in user_service.users_list
        logger.debug(f"User removal for ID {user1.id} is successful.")

    @allure.feature("User Service")
    @allure.story("User Removal Scenarios")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Verify unsuccessful non-existent user removal")
    @allure.description("""
        This test verifies that a non-existent user removal from user service failed correctly.""")
    def test_remove_non_exist_user_by_id(self, basic_instances):
        """Tests that removing a non-existing user fails."""
        logger.debug(f"Starting non-existent user removal by ID test.")
        user_service = basic_instances['user_service']
        non_exist_id = 10
        
        logger.debug(f"Attempting to remove non-existent user by ID {non_exist_id}")
        with pytest.raises(ValueError):
            user_service.remove_user_by_id(non_exist_id)
        logger.debug(f"Removal of non-existent user by ID {non_exist_id} failed correctly.")
    
    # --- load_users_from_json() test ---
    
    @allure.feature("User Service")
    @allure.story("JSON Loading Scenarios")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Verify successful loading users from JSON file")
    @allure.description("""
        This test verifies that loading users from a JSON file to user service is successful.""")
    def test_load_users_from_json(self, basic_instances, json_with_users_path):
        """Tests that loading users from a JSON file is successful."""
        logger.debug(f"Starting the test: Loading users from a JSON file.")
        user_service, user1, user2, _ = basic_instances.values()
        
        logger.debug(f"Attempting to load users '{user1}', '{user2}'"
                     f"from JSON file: '{json_with_users_path}'")
        user_service.load_users_from_json(file_path=json_with_users_path)
        
        assert len(user_service.users_list) == 2
        assert user1.id in user_service.users_list
        assert user2.id in user_service.users_list
        logger.debug(f"Loading users with JSON file '{json_with_users_path}' is successful.")

    @allure.feature("User Service")
    @allure.story("JSON Loading Scenarios")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify successful loading users from JSON file with mocked I/O")
    @allure.description("""
        This test verifies that loading users from a JSON file with mocked I/O to user service 
        is successful.""")
    def test_load_users_logic_mocked_io(self, basic_instances, mocker):
        """Tests user processing logic in load_users_from_json using mocked I/O."""
        logger.debug(f"Starting the test: Loading users from a JSON file with mocked logic of input/output.")
        user_service = basic_instances['user_service']
        user1_data = {'id': 10, 'name': 'Mocked User 1', 'email': 'mock1@example.com'}
        user2_data = {'id': 20, 'name': 'Mocked User 2', 'email': 'mock2@example.com'}
        mock_json_content = { str(user1_data['id']): user1_data, str(user2_data['id']): user2_data }
        mock_file_path = "fake/users.json"
        
        mock_load = mocker.patch('json.load', return_value=mock_json_content)
        mock_file_open = mocker.patch('builtins.open', mocker.mock_open())
        
        logger.debug(f"Attempting to load users from mocked file path '{mock_file_path}' with mocked content: {mock_json_content}")
        user_service.load_users_from_json(mock_file_path)

        assert len(user_service.users_list) == 2
        assert user1_data['id'] in user_service.users_list
        assert user2_data['id'] in user_service.users_list
        assert user_service.users_list[user1_data['id']].name == "Mocked User 1"
        assert user_service.users_list[user2_data['id']].email == "mock2@example.com"
        
        mock_file_open.assert_called_once_with(mock_file_path, 'r')
        mock_load.assert_called_once_with(mock_file_open())
        logger.debug(f"Loading users with mocked logic and file path '{mock_file_path}' is successful.")

    @allure.feature("User Service")
    @allure.story("JSON Loading Scenarios")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Verify successful loading users from JSON file with non-empty users list")
    @allure.description("""
        This test verifies that loading users from a JSON file with non-empty users in user service
        list is successful.""")
    def test_load_users_from_json_to_non_empty_users_list(self, basic_instances, json_with_users_path):
        """Tests that loading users from a JSON file with non-empty users list is successful."""
        logger.debug(f"Starting the test: Loading users from a JSON file with non-empty users list.")
        user_service, user1, user2, user3 = basic_instances.values()
        user_service.add_user(user3)
        
        logger.debug(f"Attempting to load users to non-empty users list from JSON file: '{json_with_users_path}'")
        user_service.load_users_from_json(file_path=json_with_users_path)
        
        assert len(user_service.users_list) == 3
        assert user3.id in user_service.users_list
        assert user1.id in user_service.users_list
        assert user2.id in user_service.users_list
        logger.debug(f"Loading users to non-empty users list with JSON file '{json_with_users_path}' is successful.")

    @allure.feature("User Service")
    @allure.story("JSON Loading Scenarios")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify successful loading users from JSON file with list cleanup")
    @allure.description("""
        This test verifies that loading users from a JSON file with users list cleanup in user
        service is successful.""")
    def test_load_users_from_json_clear_users_list_true(self, basic_instances, json_with_users_path):
        """Tests that loading users from JSON file with list cleanup is successful."""
        logger.debug(f"Starting the test: Loading users from a JSON file with clearing users list.")
        user_service, user1, user2, user3 = basic_instances.values()
        user_service.add_user(user3)
        
        logger.debug(f"Attempting to load users to non-empty users list with clearing from json file: '{json_with_users_path}'")
        user_service.load_users_from_json(file_path=json_with_users_path, clear_users_list=True)
        
        assert len(user_service.users_list) == 2
        assert not user3.id in user_service.users_list
        assert user1.id in user_service.users_list
        assert user2.id in user_service.users_list
        logger.debug(f"Loading users to non-empty users list with clearing with json file '{json_with_users_path}' is successful.")

    @allure.feature("User Service")
    @allure.story("JSON Loading Scenarios")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify successful loading users from JSON file with overwriting an existing user")
    @allure.description("""
        This test verifies that loading users from a JSON file with overwriting an existing user in 
        user service's users list is successful.""")
    def test_load_users_from_json_with_overwriting(self, basic_instances, json_with_users_path):
        """Tests that loading users from JSON file with overwriting an existing user is successful."""
        logger.debug(f"Starting the test: Loading users from a JSON file with overwriting.")
        user_service, user1, user2, _ = basic_instances.values()
        incorrect_user1 = User(user1.id, user2.name, user2.email)
        user_service.add_user(incorrect_user1)
        
        logger.debug(f"Attempting to load users to non-empty users list with overwriting from json file: '{json_with_users_path}'")
        user_service.load_users_from_json(file_path=json_with_users_path)
        
        assert len(user_service.users_list) == 2
        assert user1.id in user_service.users_list
        assert user1.name == user_service.users_list[user1.id].name 
        assert user1.email == user_service.users_list[user1.id].email
        logger.debug(f"Loading users with overwriting from JSON file '{json_with_users_path}' is successful.")

    @allure.feature("User Service")
    @allure.story("JSON Loading Scenarios")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Verify unsuccessful loading users from non-existing JSON file")
    @allure.description("""
        This test verifies that loading users from a non-existing JSON file to user service 
        failed correctly.""")
    def test_load_users_from_non_exist_json(self, basic_instances):
        """Tests that loading usesrs from non-existing JSON file raises FileNotFoundError exception."""
        logger.debug(f"Starting the test: Loading users from a non-existent JSON file.")
        user_service = basic_instances['user_service']
        
        logger.debug(f"Attempting to load users from non-exist JSON file.")
        with pytest.raises(FileNotFoundError):
            user_service.load_users_from_json(file_path='non_exist_file.json')
        logger.debug(f"Loading users from non-exist JSON file failed correctly.")

    @allure.feature("User Service")
    @allure.story("JSON Loading Scenarios")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Verify unsuccessful loading users from malformed JSON file")
    @allure.description("""
        This test verifies that loading users from a malformed JSON file to users service 
        failed correctly.""")
    def test_load_users_from_json_decode_error(self, basic_instances, malformed_json_path):
        """Tests that loading users from malformed JSON file raises JSONDecodeError exception."""
        logger.debug(f"Starting the test: Loading users from malformed JSON file.")
        user_service = basic_instances['user_service']
        
        logger.debug(f"Attempting to load users from malformed JSON file: '{malformed_json_path}'")
        with pytest.raises(json.JSONDecodeError):
            user_service.load_users_from_json(malformed_json_path)
        logger.debug(f"Loading users from malformed JSON file '{malformed_json_path}' failed correctly.")

    @allure.feature("User Service")
    @allure.story("JSON Loading Scenarios")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Verify unsuccessful loading users from malformed JSON file")
    @allure.description("""
        This test verifies that loading users from a malformed JSON file to user service failed 
        correctly. The 'json_with_invalid_data' fixture provides users with invalid data like 
        non-dictionary data, invalid ID type, ID mismatch and invalid user's key. The test ensures 
        that loading invalid data errors for each input.""")
    def test_load_users_from_json_with_invalid_data(self, basic_instances, json_with_invalid_data, caplog):
        """Tests that loading users with invalid data fails."""
        logger.debug(f"Starting the test: Loading JSON file with invalid data.")
        user_service = basic_instances['user_service']
        invalid_file_path, invalid_data = json_with_invalid_data
        current_invalid_data_key = next(iter(invalid_data.keys())) if invalid_data else None
        
        logger.debug(f"Attempting to load users from JSON file '{invalid_file_path}' with invalid data. Invalid data items: '{current_invalid_data_key}: {invalid_data[current_invalid_data_key]}'")
        with caplog.at_level(logging.ERROR):
            user_service.load_users_from_json(invalid_file_path)
        
        expected_substring = f"Skipping invalid user data entry with key '{current_invalid_data_key}' in {invalid_file_path}"
        
        assert any(expected_substring in message for message in caplog.messages), \
            f"Expected log message not found. Looking for: '{expected_substring}' in {caplog.messages}"
        assert len(user_service.users_list) == 0
        logger.debug(f"Loading users from JSON file '{invalid_file_path}' with invalid data logged expected messages.")
    
    # --- export_users_json() test ---

    @allure.feature("User Service")
    @allure.story("JSON Exporting Scenarios")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Verify successful exporting users to JSON file")
    @allure.description("""
        This test verifies that exporting users to JSON file from user service is successful.""")
    def test_export_users_json(self, basic_instances, json_path_to_export):
        """Tests that exporting users to JSON file is successful."""
        logger.debug(f"Starting the test: Export users in JSON file.")
        user_service, user1, user2, user3 = basic_instances.values()
        user_service.add_user(user1)
        user_service.add_user(user2)
        user_service.add_user(user3)
        
        logger.debug(f"Attempting to export {len(user_service.users_list)} users to JSON file path '{json_path_to_export}'")
        user_service.export_users_json(json_path_to_export)
        
        expected_data = {
            str(user1.id): user1.__dict__,
            str(user2.id): user2.__dict__,
            str(user3.id): user3.__dict__
        }
        
        assert os.path.exists(json_path_to_export)
        
        with open(json_path_to_export, 'r') as f:
            loaded_data = json.load(f)
            
        assert loaded_data == expected_data
        logger.debug(f"Exporting users to JSON file '{json_path_to_export}' is successful.")

    @allure.feature("User Service")
    @allure.story("JSON Exporting Scenarios")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify successful exporting users to JSON file with mocked I/O")
    @allure.description("""
        This test verifies that exporting users to JSON file with mocked I/O from user service
        is successful. The test ensures that exporting users is successful in isolated conditions.""")
    def test_export_users_mocked_io(self, basic_instances, mocker):
        """Tests export logic without writing to disk."""
        logger.debug(f"Starting the test: Export users to JSON file with mocked input and output.")
        user_service, user1, user2, _ = basic_instances.values()
        user_service.add_user(user1)
        user_service.add_user(user2)
        mock_file_path = "fake/export.json"

        expected_data_to_dump = {
            user1.id: user1.__dict__,
            user2.id: user2.__dict__
        }

        mock_file_open = mocker.patch('builtins.open', mocker.mock_open())
        mock_dump = mocker.patch('json.dump')

        logger.debug(f"Attempting to export {len(user_service.users_list)} users to mocked JSON file path: '{mock_file_path}'")
        user_service.export_users_json(mock_file_path)

        mock_file_open.assert_called_once_with(mock_file_path, 'w')
        mock_dump.assert_called_once_with(
            expected_data_to_dump,
            mock_file_open(),
            indent=4
        )
        logger.debug(f"Export users to mocked JSON file path '{mock_file_path}' is successful.")

    @allure.feature("User Service")
    @allure.story("JSON Exporting Scenarios")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Verify unsuccessful exporting users to non-existent directory")
    @allure.description("""
        This test verifies that exporting users to non-existent directory from user service 
        failed correctly.""")
    def test_export_users_non_existent_dir(self, basic_instances):
        """Test that exporting users to non-existent directory fails."""
        logger.debug(f"Staring the test: Export users to non-existent directory.")
        user_service, user1, user2, _ = basic_instances.values()
        user_service.add_user(user1)
        user_service.add_user(user2)
        non_existent_dir = "non_exist_dir/users.json"
        
        logger.debug(f"Attempting to export users: \n{user_service}In non-existent directory: '{non_existent_dir}'")
        with pytest.raises(DataFileWriteError):
            user_service.export_users_json(non_existent_dir)
        logger.debug(f"Exporting users to non-existent directory '{non_existent_dir}' failed correctly.")
        
    # --- __str__() test ---

    @allure.feature("User Service")
    @allure.story("User Service String Representation")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.title("Verify successful string representation of the user service")
    @allure.description("""
        This test verifies that string representation of the user service is successful.""")
    def test_user_service_string_representation(self, basic_instances):
        """Tests that getting UserService instance string representation is successful."""
        logger.debug(f"Starting user service string representation test.")
        user_service, user1, user2, user3 = basic_instances.values()
        user_service.add_user(user1)
        user_service.add_user(user2)
        user_service.add_user(user3)
        expected_string = f'1. {user1.name} - ID: {user1.id}, Email: {user1.email}\n2. {user2.name} - ID: {user2.id}, Email: {user2.email}\n3. {user3.name} - ID: {user3.id}, Email: {user3.email}\n'
        
        logger.debug(f"Attempting to verify whether user service string representation is equal to expected string: {expected_string}")
        assert str(user_service) == expected_string
        logger.debug(f"Getting string representation of user service successfuly equal to expected string: {expected_string}")