import pytest
import json
import tempfile
import os
import subprocess
import time
import signal
import requests
import logging
from src.user_management import User, UserService

logger = logging.getLogger(__name__)

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
  
api_command = ["uvicorn", "src.api:app", "--port", "8000"]
api_base_url = "http://127.0.0.1:8000"
health_check_url = f"{api_base_url}/health"

polling_timeout = 30
polling_interval = 0.5

current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = os.path.join(current_script_dir, os.pardir)
absolute_project_root_dir = os.path.abspath(project_root_dir)

@pytest.fixture(scope="session")
def api_service():
    """Pytest fixture to start and stop the API service, polling a health check endpoint."""
    logger.info("\nStarting API service...")
    process = None
    service_started = False

    try:
        process = subprocess.Popen(
            api_command,
            cwd=absolute_project_root_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        logger.info(f"Polling health check endpoint at {health_check_url} for up to {polling_timeout} seconds...")
        start_time = time.time()

        while time.time() - start_time < polling_timeout:
            try:
                response = requests.get(health_check_url, timeout=1)

                if response.status_code == 200:
                    logger.info("API service is healthy.")
                    service_started = True
                    break

            except requests.exceptions.RequestException as e:
                logger.debug(f"Health check failed (attempting): {e}")
                pass

            time.sleep(polling_interval)

        if not service_started:
            if process.poll() is not None:
                 stdout, stderr = process.communicate()
                 logger.info(f"\nAPI service process terminated unexpectedly during startup.")
                 logger.debug(f"Stdout:\n{stdout.decode()}")
                 logger.debug(f"Stderr:\n{stderr.decode()}")
            else:
                 logger.info(f"\nAPI service did not become healthy within {polling_timeout} seconds.")

            pytest.fail("API service failed to start or become healthy.")

        logger.info("API service setup complete.")
        yield api_base_url

    finally:
        if process is not None and process.poll() is None:
            logger.info("\nStopping API service...")
            try:
                process.terminate()
                process.wait(timeout=10)
                logger.info("API service stopped.")
            except (subprocess.TimeoutExpired, ProcessLookupError):
                logger.info("API service did not terminate gracefully, killing...")
                try:
                    process.kill()
                    process.wait(timeout=5)
                    logger.info("API service killed.")
                except (subprocess.TimeoutExpired, ProcessLookupError):
                    logger.info("Failed to kill API service process.")
       
@pytest.fixture()
def clear_users_json():
    """Fixture to clear data/users.json after tests."""
    json_path = os.path.join(absolute_project_root_dir, "data", "users.json")
    yield
    logger.debug(f"Clearing {json_path}")
    try:
        with open(json_path, "w") as outfile:
            json.dump({}, outfile)
            logger.debug(f"JSON file was cleared successfully.")
    except Exception as e:
        logger.warning(f"Failed to clear JSON file '{json_path}'. An unexpected error occurred: {e}")
             
@pytest.fixture()
def add_users_json():
    """Fixture to add users to a JSON file before tests and clear it afterwards."""
    users_data_for_test = {
        "231": {
            "id": 231,
            "name": "Alice Hetun",
            "email": "alicehetun5828@example.com"
        },
        "783": {
            "id": 783,
            "name": "Bob Smith",
            "email": "bobsmith01842@example.com"
        }
    }
    
    json_path = os.path.join(absolute_project_root_dir, "data", "users.json")
    original_content = None
    if os.path.exists(json_path):
        with open(json_path, "r") as f_orig:
            try:
                original_content = json.load(f_orig)
            except json.JSONDecodeError:
                original_content = {}

    try:
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, "w") as outfile:
            json.dump(users_data_for_test, outfile, indent=4)
        logger.info(f"\n[add_users_json] Wrote test data to {json_path}")
        yield users_data_for_test
    finally:
        logger.info(f"\n[add_users_json] Restoring/clearing {json_path}")
        if original_content is not None:
            with open(json_path, "w") as outfile:
                json.dump(original_content, outfile, indent=4)
            logger.info(f"[add_users_json] Restored original content to {json_path}")
        elif os.path.exists(json_path):
            os.remove(json_path)
            logger.info(f"[add_users_json] Removed {json_path}")