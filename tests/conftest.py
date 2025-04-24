import pytest
import json
import tempfile
import os
from src.user_management import User, UserService

@pytest.fixture
def basic_instances():
    user_service = UserService()
    user1 = User(1, "Walter White", "walterwhite444@example.com")
    user2 = User(2, "Xia Li", "xiali@example.com")
    user3 = User(3, "Bella Swan", "bellaswan@example.com")
    instances = {
        'user_service': user_service,
        'user1': user1,
        'user2': user2,
        'user3': user3
    }
    
    yield instances
    
    user_service.users_list.clear()
    
@pytest.fixture
def json_with_users_path(basic_instances):
    temp_dir = tempfile.TemporaryDirectory()
    json_path = os.path.join(temp_dir.name, 'test_users.json')
    user1 = basic_instances['user1']
    user2 = basic_instances['user2']
    users_to_load = {
        user1.id: user1.__dict__,
        user2.id: user2.__dict__
    }
    try:
        with open(json_path, 'w') as f:
            json.dump(users_to_load, f)
    except Exception as e:
        pytest.fail(f"Setup failed: Could not write temporary test file: {e}")
        
    yield json_path
    
    temp_dir.cleanup()
    
@pytest.fixture
def malformed_json_path():
    temp_dir = tempfile.TemporaryDirectory()
    json_path = os.path.join(temp_dir.name, "malformed_file.json")
    malformed_data = "{81 {'name': 'John Tidison}"
    with open(json_path, 'w') as f:
        f.write(malformed_data)
        
    yield json_path
    
    temp_dir.cleanup()
    
@pytest.fixture(params=[
    {'44': 'user info'},
    {'715': {'id': 'one', 'name': 'Nick Nitrig', 'email': 'nicknitrig33@example.com'}},
    {'341': {'id': 89, 'name': 'Maria Kenz', 'email': 'mariakenz53@example.com'}},
    {'122': {'id': 122, 'position': 'HR department', 'email': 'haroldziberg232@example.com'}},
], ids=[
    "user_with_data_not_dict",
    "user_with_invalid_id_type",
    "user_with_id_mismatch",
    "user_with_invalid_key"
])
def json_with_invalid_data(request):
    temp_dir = tempfile.TemporaryDirectory()
    malformed_file_path = os.path.join(temp_dir.name, 'malformed_file.json')
    with open(malformed_file_path, 'w') as f:
        json.dump(request.param, f)
    
    yield malformed_file_path, request.param
    
    temp_dir.cleanup()
    
@pytest.fixture
def json_path_to_export():
    temp_dir = tempfile.TemporaryDirectory()
    json_path = os.path.join(temp_dir.name, "test_users.json")
    
    yield json_path
    
    temp_dir.cleanup()