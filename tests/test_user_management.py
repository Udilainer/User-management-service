import pytest
import json
import os
import logging
from src.user_management import User, DuplicateUserError

class TestUser:
    
    # --- __init__() test ---
    
    @pytest.mark.parametrize("various_valid_id, valid_name, valid_email", [
        (0, "Karl Gekot", "karlgekot435@example.com"),
        (48, "Stive Jarviz", "stivejarviz@example.com"),
        (535, "Yun Heihachi", "yunheihachi324@example.com"),
        (6244, "Nick Rijo", "nickrijo245@example.com")
    ])
    def test_user_init_valid_ids(self, various_valid_id, valid_name, valid_email):
        """Tests user initialization with various ID inputs."""
        user = User(various_valid_id, valid_name, valid_email)
        
        assert user.id == various_valid_id
        assert user.name == valid_name
        assert user.email == valid_email
        
    @pytest.mark.parametrize("valid_id, various_valid_name, valid_email", [
        (15, "John", "bobjohnson@example.com"), # Name length 4
        (25, "Elizabeth Anne Marie Rodriguez-Garc", "elizabet@example.com"), # Name length 35
        (67, "Christopher Alexander Michael Jonathan David Williams-Johnson-Smith-Br", "william@example.com") # Name length 70
    ])
    def test_user_init_valid_names(self, valid_id, various_valid_name, valid_email):
        """Tests user initialization with various name length inputs."""
        user = User(valid_id, various_valid_name, valid_email)
        
        assert user.id == valid_id
        assert user.name == various_valid_name
        assert user.email == valid_email
        
    @pytest.mark.parametrize("valid_id, valid_name, various_valid_email", [
        (33, "Short Email User", "a@b.co"), # Email length 6
        (55, "Standard Email Name", "standardusernamehere123@example.com"), # Email length 35
        (70, "Very Long Email Example", "verylongusernameexampleherenownow13452@example.com") # Email length 50
    ])
    def test_user_init_valid_emails(self, valid_id, valid_name, various_valid_email):
        """Tests user initialization with various email length inputs."""
        user = User(valid_id, valid_name, various_valid_email)
        
        assert user.id == valid_id
        assert user.name == valid_name
        assert user.email == various_valid_email
        
    @pytest.mark.parametrize("id, name, email", [
        ('invalid_id', "Fiona Gallagher", "fionagallagher@example.com"), # Invalid ID type
        (2109, ["George Costanza"], "georgecostanza123@example.com"), # Invalid name type
        (55, "Holly Golightly", {'email': "hollygolightly@example.com"}), # Invalid email type
    ])
    def test_user_init_invalid_input_types(self, id, name, email):
        """Tests user initialization with various invalid input types."""
        with pytest.raises(TypeError):
            user = User(id, name, email)
            
    @pytest.mark.parametrize("id, name, email", [
        (3, "", "jasminekhan@example.com"), # Empty name
        (1123, "Kevin McCallister", ""), # Empty email
    ])
    def test_user_init_empty_inputs(self, id, name, email):
        """Tests user initialization with various empty inputs."""
        with pytest.raises(ValueError):
            user = User(id, name, email)
            
    @pytest.mark.parametrize("valid_id, valid_name, various_invalid_email", [
        (65, "Leia Organa", "@example.com"), # Email with no local part
        (77, "Oscar Martinez", "oscarmartinezexample.com"), # Email without '@'
        (4902, "Michael Scott", "michaelscott@.com"), # Email with no domain name
        (203, "Rachel Green", "rachelgreen222@"), # Email with no domain part
        (1, "Nancy Drew", "nancydrew999@example$.com"), # Email with incorect character ($) in domain name
        (3456, "Pam Beesly", "pambeesly111@example.%com"), # Email with incorect character (%) in TLD
        (9, "Quentin Tarantino", "quentintarantino@examplecom"), # Email without dot in domain part
        (14, "Tina Belcher", "tinabelcher@example.c"), # Email with too short TLD (1 character)
        (5876, "Sheldon Cooper", "sheldoncooper@example."), # Email without TLD
    ])
    def test_user_init_invalid_emails(self, valid_id, valid_name, various_invalid_email):
        """Tests user initialization with various invalid email inputs."""
        with pytest.raises(ValueError):
            user = User(valid_id, valid_name, various_invalid_email)
            
    # --- __str__() test ---
    
    def test_user_string_representation(self):
        """Tests that getting User instance string representation is successfull."""
        user_id = 4
        user_name = "Veronica Mars"
        user_email = "veronicamars@example.com"
        user = User(user_id, user_name, user_email)
        expected_string = f"{user_name} - ID: {user_id}, Email: {user_email}"
        
        assert str(user) == expected_string
        
class TestUserService:
    
    # --- add_user() test ---
    
    def test_add_user(self, basic_instances):
        """Tests that adding a user is successfull."""
        user_service = basic_instances['user_service']
        user1 = basic_instances['user1']
        user_service.add_user(basic_instances['user1'])
        
        assert user1.id in user_service.users_list
        
    def test_add_non_user_object(self, basic_instances):
        """Tests that adding a non-user object raises TypeError."""
        user_service = basic_instances['user_service']
        non_user_instance = 'user1'
        
        with pytest.raises(TypeError):
            user_service.add_user(non_user_instance)
            
        assert len(user_service.users_list) == 0
    
    def test_add_exist_user(self, basic_instances):
        """Tests that adding a user with an ID that already exists raises DuplicateUserError."""
        user_service = basic_instances['user_service']
        user1 = basic_instances['user1']
        user_service.add_user(user1)
        
        with pytest.raises(DuplicateUserError):
            user_service.add_user(user1)
        assert len(user_service.users_list) == 1
        
    # --- remove_user_by_id() test ---
    
    def test_remove_user_by_id(self, basic_instances):
        """Tests that removing user by id is successfull."""
        user_service, user1, user2, user3 = basic_instances.values()
        user_service.add_user(user1)
        user_service.add_user(user2)
        user_service.add_user(user3)
        user_service.remove_user_by_id(user1.id)
        
        assert len(user_service.users_list) == 2
        assert not user1.id in user_service.users_list 
        
    def test_remove_non_exist_user_by_id(self, basic_instances):
        """Tests that removing a non-existing user fails."""
        user_service = basic_instances['user_service']
        
        with pytest.raises(ValueError):
            user_service.remove_user_by_id(10)
    
    # --- load_users_from_json() test ---
    
    def test_load_users_from_json(self, basic_instances, json_with_users_path):
        """Tests that loading users from a json file is successfull."""
        user_service, user1, user2, _ = basic_instances.values()
        
        user_service.load_users_from_json(file_path=json_with_users_path)
        
        assert len(user_service.users_list) == 2
        assert user1.id in user_service.users_list
        assert user2.id in user_service.users_list
        
    def test_load_users_logic_mocked_io(self, basic_instances, mocker):
        """Tests user processing logic in load_users_from_json using mocked I/O."""
        user_service = basic_instances['user_service']
        user1_data = {'id': 10, 'name': 'Mocked User 1', 'email': 'mock1@example.com'}
        user2_data = {'id': 20, 'name': 'Mocked User 2', 'email': 'mock2@example.com'}
        mock_json_content = { str(user1_data['id']): user1_data, str(user2_data['id']): user2_data }
        mock_file_path = "fake/users.json"
        
        mock_load = mocker.patch('json.load', return_value=mock_json_content)
        mock_file_open = mocker.patch('builtins.open', mocker.mock_open())
        
        user_service.load_users_from_json(mock_file_path)

        assert len(user_service.users_list) == 2
        assert user1_data['id'] in user_service.users_list
        assert user2_data['id'] in user_service.users_list
        assert user_service.users_list[user1_data['id']].name == "Mocked User 1"
        assert user_service.users_list[user2_data['id']].email == "mock2@example.com"
        
        mock_file_open.assert_called_once_with(mock_file_path, 'r')
        mock_load.assert_called_once_with(mock_file_open())
        
    def test_load_users_from_json_to_non_empty_users_list(self, basic_instances, json_with_users_path):
        """Tests that loading users from a json file with non-empty users list is successfull."""
        user_service, user1, user2, user3 = basic_instances.values()
        user_service.add_user(user3)
        
        user_service.load_users_from_json(file_path=json_with_users_path)
        
        assert len(user_service.users_list) == 3
        assert user3.id in user_service.users_list
        assert user1.id in user_service.users_list
        assert user2.id in user_service.users_list
        
    def test_load_users_from_json_clear_users_list_true(self, basic_instances, json_with_users_path):
        """Tests that loading users from json file with list cleanup is successful."""
        user_service, user1, user2, user3 = basic_instances.values()
        user_service.add_user(user3)
        
        user_service.load_users_from_json(file_path=json_with_users_path, clear_users_list=True)
        
        assert len(user_service.users_list) == 2
        assert not user3.id in user_service.users_list
        assert user1.id in user_service.users_list
        assert user2.id in user_service.users_list
        
    def test_load_users_from_json_with_overwriting(self, basic_instances, json_with_users_path):
        """Tests that loading users from json file with overwriting an existing user is successfull."""
        user_service, user1, user2, _ = basic_instances.values()
        incorrect_user1 = User(user1.id, user2.name, user2.email)
        user_service.add_user(incorrect_user1)
        
        user_service.load_users_from_json(file_path=json_with_users_path)
        
        assert len(user_service.users_list) == 2
        assert user1.id in user_service.users_list
        assert user1.name == user_service.users_list[user1.id].name 
        assert user1.email == user_service.users_list[user1.id].email
        
    def test_load_users_from_non_exist_json(self, basic_instances):
        """Tests that loading usesrs from non-existing json file raises FileNotFoundError exception."""
        user_service = basic_instances['user_service']
        
        with pytest.raises(FileNotFoundError):
            user_service.load_users_from_json(file_path='non_exist_file.json')
            
    def test_load_users_from_json_decode_error(self, basic_instances, malformed_json_path):
        """Tests that loading users from malformed file raises JSONDecodeError exception."""
        user_service = basic_instances['user_service']
            
        with pytest.raises(json.JSONDecodeError):
            user_service.load_users_from_json(malformed_json_path)
        
    def test_load_users_from_json_with_invalid_data(self, basic_instances, json_with_invalid_data, caplog):
        """Tests that loading users with invalid data fails."""
        user_service = basic_instances['user_service']
        invalid_file_path, invalid_data = json_with_invalid_data
        
        with caplog.at_level(logging.ERROR):
            user_service.load_users_from_json(invalid_file_path)
            
        assert f"Skipping invalid user data entry with key '{[k for k in invalid_data.keys()][0]}' in {invalid_file_path}" in caplog.messages[0]
    
    # --- export_users_json() test ---
        
    def test_export_users_json(self, basic_instances, json_path_to_export):
        """Tests that exporting users from json file is successfull."""
        user_service, user1, user2, user3 = basic_instances.values()
        user_service.add_user(user1)
        user_service.add_user(user2)
        user_service.add_user(user3)
        
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
        
    def test_export_users_mocked_io(self, basic_instances, mocker):
        """Tests export logic without writing to disk."""
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

        user_service.export_users_json(mock_file_path)

        mock_file_open.assert_called_once_with(mock_file_path, 'w')
        mock_dump.assert_called_once_with(
            expected_data_to_dump,
            mock_file_open(),
            indent=4
        )
        
    # --- __str__() test ---
    
    def test_user_service_string_representation(self, basic_instances):
        """Tests that getting UserService instance string representation is successfull."""
        user_service, user1, user2, user3 = basic_instances.values()
        user_service.add_user(user1)
        user_service.add_user(user2)
        user_service.add_user(user3)
        expected_string = f'1. {user1.name} - ID: {user1.id}, Email: {user1.email}\n2. {user2.name} - ID: {user2.id}, Email: {user2.email}\n3. {user3.name} - ID: {user3.id}, Email: {user3.email}\n'
        
        assert str(user_service) == expected_string