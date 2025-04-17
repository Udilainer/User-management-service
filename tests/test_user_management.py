import unittest
import json
import os
import tempfile
import io
import logging
from src.user_management import User, UserService, DuplicateUserError

class TestUser(unittest.TestCase):
        
    # --- __init__() test ---
    
    def test_user_initialization(self):
        """Tests that initialization is successfull."""
        user = User(156, 'Alice Bertival', 'alice191@example.com')
        self.assertEqual(user.id, 156)
        self.assertEqual(user.name, 'Alice Bertival')
        self.assertEqual(user.email, 'alice191@example.com')
    
    def test_user_init_with_invalid_id(self):
        """Tests that initialization of user with invalid ID raises TypeError."""
        with self.assertRaises(TypeError):
            user = User('232', 'Karl Tigirog', 'karlrigirog920@example.com')
    
    def test_user_init_with_invalid_name(self):
        """Tests that initialization of user with invalid name raises TypeError."""
        with self.assertRaises(TypeError):
            user = User(240, 9232, 'elenaurog112@example.com')
    
    def test_user_init_with_empty_name(self):
        """Tests that initialization of user with empty name raises ValueError."""
        with self.assertRaises(ValueError):
            user = User(240, '', 'elenaurog112@example.com')
    
    def test_user_init_with_invalid_email(self):
        """Tests that initialization of user with invalid email raises TypeError."""
        with self.assertRaises(TypeError):
            user = User(722, 'Andrew Lit', ['andrewlit332@example.com'])
    
    def test_user_init_with_empty_email(self):
        """Tests that initialization of user with empty email raises ValueError."""
        with self.assertRaises(ValueError):
            user = User(45, 'Michel Rodrigez', '')
    
    def test_user_init_with_ivalid_email_format(self):
        """Tests that initialization of user with invalid email format raises ValueError."""
        with self.assertRaises(ValueError):
            user = User(67, 'Ilya Malkolm', 'ilya2@invalidexample')
    
    # --- __str__() test ---
    
    def test_user_string_representation(self):
        """Tests that getting User instance string representation is successfull."""
        user = User(632, 'Richard Wildburg', 'richard32@example.com')
        expected_string = f'{user.name} - ID: {user.id}, Email: {user.email}'
        self.assertEqual(str(user), expected_string)

class TestUserService(unittest.TestCase):
    
    def setUp(self) -> None:
        self.user_service = UserService()
        self.user1 = User(82, 'John Melat', 'johnmelat43@example.com')
        self.user2 = User(102, 'Nick Hiphon', 'nichhepon912@example.com')
        self.user3 = User(215, 'William King', 'williamking192@example.com')
        
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file_path = os.path.join(self.temp_dir.name, 'test_users.json')
        
        users_to_load = {
            self.user1.id: self.user1.__dict__,
            self.user2.id: self.user2.__dict__
        }
        try:
            with open(self.test_file_path, 'w') as infile:
                json.dump(users_to_load, infile, indent=4)
        except Exception as e:
            self.fail(f"Setup failed: Could not write temporary test file: {e}")

        return super().setUp()
    
    def tearDown(self) -> None:
        self.user_service.users_list.clear()
        self.temp_dir.cleanup()
        
        return super().tearDown()
        
    # --- add_user() test ---
    
    def test_add_user(self):
        """Tests that adding a user is successfull."""
        self.user_service.add_user(self.user1)
        self.assertEqual(len(self.user_service.users_list), 1)
        expected_string = f'{self.user1.name} - ID: {self.user1.id}, Email: {self.user1.email}'
        self.assertEqual(str(self.user_service.users_list[self.user1.id]), expected_string)
    
    def test_add_non_user_object(self):
        """Tests that adding a non-user object raises TypeError."""
        fake_user = 'Karl Libeht'
        with self.assertRaises(TypeError):
            self.user_service.add_user(fake_user)
        self.assertEqual(len(self.user_service.users_list), 0)
    
    def test_add_exist_user(self):
        """Tests that adding a user with an ID that already exists raises DuplicateUserError."""
        self.user_service.add_user(self.user1)
        with self.assertRaises(DuplicateUserError):
            self.user_service.add_user(self.user1)
        self.assertEqual(len(self.user_service.users_list), 1)
        
    # --- remove_user_by_id() test ---
    
    def test_remove_user_by_id(self):
        """Tests that removing user by id is successfull."""
        self.user_service.add_user(self.user1)
        self.user_service.remove_user_by_id(self.user1.id)
        self.assertEqual(len(self.user_service.users_list), 0)
    
    def test_remove_non_exist_user_by_id(self):
        """Tests that removing a non-existing user fails."""
        self.user_service.add_user(self.user1)
        with self.assertRaises(ValueError):
            self.user_service.remove_user_by_id(340)
        self.assertEqual(len(self.user_service.users_list), 1)
        
    # --- load_users_from_json() test ---
    
    def test_load_users_from_json(self):
        """Tests that loading users from a json file is successfull."""
        self.user_service.load_users_from_json(file_path=self.test_file_path)
        self.assertIn(self.user1.id, self.user_service.users_list)
        self.assertIn(self.user2.id, self.user_service.users_list)
        self.assertEqual(len(self.user_service.users_list), 2)
    
    def test_load_users_from_json_to_non_empty_users_list(self):
        """Tests that loading users from a json file with non-empty users list is successfull."""
        self.user_service.add_user(self.user3)
        self.user_service.load_users_from_json(file_path=self.test_file_path)
        self.assertIn(self.user3.id, self.user_service.users_list)
        self.assertIn(self.user1.id, self.user_service.users_list)
        self.assertIn(self.user2.id, self.user_service.users_list)
        self.assertEqual(len(self.user_service.users_list), 3)
    
    def test_load_users_from_json_clear_users_list_true(self):
        """Tests that loading users from json file with list cleanup is successful."""
        self.user_service.add_user(self.user3)
        self.user_service.load_users_from_json(file_path=self.test_file_path, clear_users_list=True)
        self.assertNotIn(self.user3.id, self.user_service.users_list)
        self.assertIn(self.user1.id, self.user_service.users_list)
        self.assertIn(self.user2.id, self.user_service.users_list)
        self.assertEqual(len(self.user_service.users_list), 2)
        
    def test_load_users_from_json_with_overwriting(self):
        """Tests that loading users from json file with overwriting an existing user is successfull."""
        user3 = User(self.user1.id, 'Nico Wong', 'nicowong243@example.com')
        self.user_service.add_user(user3)
        self.user_service.load_users_from_json(file_path=self.test_file_path)
        self.assertIn(self.user1.id, self.user_service.users_list)
        self.assertEqual(self.user_service.users_list[self.user1.id].name, self.user1.name)
        self.assertEqual(self.user_service.users_list[self.user1.id].email, self.user1.email)
            
    def test_load_users_from_non_exist_json(self):
        """Tests that loading usesrs from non-existing json file raises FileNotFoundError exception."""
        with self.assertRaises(FileNotFoundError):
            self.user_service.load_users_from_json(file_path='non_exist_file.json')
        
    def test_load_users_from_json_decode_error(self):
        """Tests that loading users from malformed file raises JSONDecodeError exception."""
        malformed_file_path = os.path.join(self.temp_dir.name, 'test_malformed_users.json')
        malformed_string = '{"82": {"id": 82 "name": "John Mela"}'
        
        with open(malformed_file_path, 'w') as infile:
            infile.write(malformed_string)
            
        with self.assertRaises(json.JSONDecodeError):
            self.user_service.load_users_from_json(file_path=malformed_file_path)
    
    def test_load_users_from_json_with_invalid_data(self):
        """Tests that loading users with invalid data fails."""
        test_file_with_mixed_data = os.path.join(self.temp_dir.name, 'test_load_invalid_data.json')
        users_to_load = {
            '44': 'user info',
            '715': {'id': 'one', 'name': 'Nick Nitrig', 'email': 'nicknitrig33@example.com'},
            '341': {'id': 89, 'name': 'Maria Kenz', 'email': 'mariakenz53@example.com'},
            '122': {'id': 122, 'position': 'HR department', 'email': 'haroldziberg232@example.com'},
            '872': {'id': 872, 'name': 'Henri Nightingale', 'email': 'henrinightingale01@example.com'}
            }

        with open(test_file_with_mixed_data, 'w') as infile:
            json.dump(users_to_load, infile, indent=4)
        
        with self.assertLogs('user_management.UserService', level='ERROR') as cm:
            self.user_service.load_users_from_json(file_path=test_file_with_mixed_data)
        
        users_keys = []
        for key in users_to_load.keys():
            users_keys.append(int(key))
            
        self.assertIn(users_keys[4], self.user_service.users_list)
        self.assertNotIn(users_keys[0], self.user_service.users_list)
        self.assertNotIn(users_keys[1], self.user_service.users_list)
        self.assertNotIn(users_keys[2], self.user_service.users_list)
        self.assertNotIn(users_keys[3], self.user_service.users_list)
        self.assertEqual(len(cm.output), 4)
        self.assertIn(f"Skipping invalid user data entry with key '{users_keys[0]}' in {test_file_with_mixed_data}", cm.output[0])
        self.assertIn(f"Skipping invalid user data entry with key '{users_keys[1]}' in {test_file_with_mixed_data}", cm.output[1])
        self.assertIn(f"Skipping invalid user data entry with key '{users_keys[2]}' in {test_file_with_mixed_data}", cm.output[2])
        self.assertIn(f"Skipping invalid user data entry with key '{users_keys[3]}' in {test_file_with_mixed_data}", cm.output[3])
    
    # --- export_users_json() test ---
    
    def test_export_users_json(self):
        """Tests that exporting users from json file is successfull."""
        self.user_service.add_user(self.user1)
        self.user_service.add_user(self.user2)
        
        export_file_path = os.path.join(self.temp_dir.name, 'export_test.json')
        self.user_service.export_users_json(export_file_path)
        
        self.assertTrue(os.path.exists(export_file_path))

        with open(export_file_path, 'r') as outfile:
            loaded_data = json.load(outfile)
            
        expected_content = {
            str(self.user1.id): {'id': self.user1.id, 'name': self.user1.name, 'email': self.user1.email},
            str(self.user2.id): {'id': self.user2.id, 'name': self.user2.name, 'email': self.user2.email}
        }
        self.assertEqual(loaded_data, expected_content)
        
    # --- __str__() test ---
    
    def test_user_service_string_representation(self):
        """Tests that getting UserService instance string representation is successfull."""
        self.user_service.add_user(self.user1)
        self.user_service.add_user(self.user2)
        expected_string = f'1. {self.user1.name} - ID: {self.user1.id}, Email: {self.user1.email}\n2. {self.user2.name} - ID: {self.user2.id}, Email: {self.user2.email}\n'
        self.assertEqual(str(self.user_service), expected_string)

if __name__ == '__main__':
    unittest.main()