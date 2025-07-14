import pytest
import json
import tempfile
import os
import subprocess
import time
import requests
import logging
import threading
import jsonschema
from typing import Callable, Iterator, Tuple, Dict, Any, List, Union, cast
from referencing import Resource, Registry
from referencing.jsonschema import DRAFT7
from src.user_management import User, UserService
from utils import delete_user_if_exists
from pathlib import Path


logger = logging.getLogger(__name__)


@pytest.fixture
def basic_instances() -> Iterator[Dict[str, Union[UserService, User]]]:
    """Pytest fixture to create basic instances of UserService and User."""
    user_service = UserService()
    user1 = User(1, "Walter White", "walterwhite444@example.com")
    user2 = User(2, "Xia Li", "xiali@example.com")
    user3 = User(3, "Bella Swan", "bellaswan@example.com")
    instances: Dict[str, Union[UserService, User]] = {
        "user_service": user_service,
        "user1": user1,
        "user2": user2,
        "user3": user3,
    }

    yield instances

    user_service.users_list.clear()


@pytest.fixture
def json_with_users_path(
    basic_instances: Dict[str, Union[UserService, User]]
) -> Iterator[Path]:
    """Pytest fixture to create a temporary JSON file with user data."""
    temp_dir = tempfile.TemporaryDirectory()
    json_path = Path(temp_dir.name) / "test_users.json"
    user1 = cast("User", basic_instances["user1"])
    user2 = cast("User", basic_instances["user2"])
    users_to_load = {user1.id: user1.__dict__, user2.id: user2.__dict__}
    try:
        with open(json_path, "w") as f:
            json.dump(users_to_load, f)
    except Exception as e:
        pytest.fail(f"Setup failed: Could not write temporary test file: {e}")

    yield json_path

    temp_dir.cleanup()


@pytest.fixture
def malformed_json_path() -> Iterator[Path]:
    """Pytest fixture to create a temporary malformed JSON file."""
    temp_dir = tempfile.TemporaryDirectory()
    json_path = Path(temp_dir.name) / "malformed_file.json"
    malformed_data = "{81 {'name': 'John Tidison}"

    with open(json_path, "w") as f:
        f.write(malformed_data)

    yield json_path

    temp_dir.cleanup()


INVALID_USER_DATA_CASES = {
    "user_with_data_not_dict": {
        "data": {"44": "user info"},
        "reason": "User data is not a dictionary"
    },
    "user_with_invalid_id_type": {
        "data": {
            "715": {
                "id": "one",
                "name": "Nick Nitrig",
                "email": "nick@example.com"
            }
        },
        "reason": "User ID in data is not an integer"
    },
    "user_with_id_mismatch": {
        "data": {"341": {"id": 89, "name": "Maria Kenz", "email": "maria@example.com"}},
        "reason": "User ID in data mismatches the key"
    },
    "user_with_invalid_key": {
        "data": {"122": {"id": 122, "position": "HR", "email": "harold@example.com"}},
        "reason": "Missing 'name' key in user data"
    },
}


@pytest.fixture(
    params=INVALID_USER_DATA_CASES.values(),
    ids=list(INVALID_USER_DATA_CASES.keys())
)
def json_with_invalid_data(
    request: pytest.FixtureRequest
) -> Iterator[Tuple[Path, Dict[str, Any]]]:
    """
    Pytest fixture to create a temporary JSON file
    with various invalid user data entries.
    """
    temp_dir = tempfile.TemporaryDirectory()
    invalid_user_data_file = Path(temp_dir.name) / "invalid_data.json"

    invalid_payload = request.param["data"]

    with open(invalid_user_data_file, "w") as f:
        json.dump(invalid_payload, f)

    yield invalid_user_data_file, invalid_payload

    temp_dir.cleanup()


@pytest.fixture
def json_path_to_export() -> Iterator[Path]:
    """Pytest fixture to creat a temporary JSON file for export."""
    temp_dir = tempfile.TemporaryDirectory()
    json_path = Path(temp_dir.name) / "test_users.json"

    yield json_path

    temp_dir.cleanup()


api_command = ["uvicorn", "src.api:app", "--port", "8000"]
api_base_url = "http://127.0.0.1:8000"
health_check_url = f"{api_base_url}/health"

polling_timeout = 30
polling_interval = 0.5

PROJECT_ROOT_DIR = Path(__file__).parent.parent


def _pipe_reader(pipe: Any, output_list: List[str]) -> None:
    """A simple function to be run in a thread, consuming a pipe's output."""
    try:
        with pipe:
            for line in iter(pipe.readline, b''):
                output_list.append(line.decode('utf-8').strip())
    except ValueError:
        pass
    except Exception:
        pass


@pytest.fixture(scope="session")
def api_service(request: pytest.FixtureRequest) -> Iterator[str]:
    """
    Pytest fixture to start and stop the API service, polling a health check endpoint.
    """
    logger.info("\nStarting API service...")
    process = None
    service_started = False

    env = os.environ.copy()
    env["TESTING"] = "1"

    stdout_output: List[str] = []
    stderr_output: List[str] = []

    try:
        process = subprocess.Popen(
            api_command,
            cwd=PROJECT_ROOT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )

        stdout_thread = threading.Thread(
            target=_pipe_reader,
            args=[process.stdout, stdout_output],
            daemon=True
        )
        stderr_thread = threading.Thread(
            target=_pipe_reader,
            args=[process.stderr, stderr_output],
            daemon=True
        )
        stdout_thread.start()
        stderr_thread.start()

        logger.info(
            f"Polling health check endpoint at {health_check_url} "
            f"for up to {polling_timeout} seconds..."
        )
        start_time: float = time.time()

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
            logger.error("\n--- API Service Startup Stdout: ---")
            for line in stdout_output:
                logger.error(line)
            logger.error("--- API Service Startup Stderr: ---")
            for line in stderr_output:
                logger.error(line)

            if process.poll() is not None:
                logger.error(
                    f"\nAPI service process terminated unexpectedly with exit code "
                    f"{process.returncode} during startup."
                )
            else:
                logger.error(
                    f"\nAPI service did not become healthy within "
                    f"{polling_timeout} seconds."
                )
            pytest.fail("API service failed to start or become healthy.")

        logger.info("API service setup complete.")
        yield api_base_url

    finally:
        if process is not None and process.poll() is None:
            logger.info("\nStopping API service...")
            if request.session.testsfailed > 0:
                logger.info(
                    "--- Captured API Stdout during test run (if failures): ---"
                )
                for line in stdout_output:
                    print(line)
                logger.info(
                    "--- Captured API Stderr during test run (if failures): ---"
                )
                for line in stderr_output:
                    print(line)
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


@pytest.fixture(scope="session")
def local_schema_registry() -> Registry:
    """
    Creates a schema registry and populates it with a local copy of the Draft-07
    metaschema.
    """
    schema_path: Path = PROJECT_ROOT_DIR / "schemas" / "meta" / "draft-07.json"
    with schema_path.open() as f:
        local_draft7_meta_schema: Dict[str, Any] = json.load(f)
    local_draft7_resource: Resource = Resource.from_contents(
        local_draft7_meta_schema,
        default_specification=DRAFT7,
    )
    registry: Registry = Registry().with_resources(
        [("http://json-schema.org/draft-07/schema#", local_draft7_resource)]
    )
    return registry


@pytest.fixture(scope="session")
def validator_factory(
    local_schema_registry: Registry
) -> Callable[[dict], jsonschema.Draft7Validator]:
    """
    Provides a factory function to create validator instances.
    Each instance is correctly configured with the local schema registry.
    """
    def _validator_factory(schema: dict) -> jsonschema.Draft7Validator:
        return jsonschema.Draft7Validator(schema, registry=local_schema_registry)

    return _validator_factory


@pytest.fixture(autouse=True)
def api_auto_cleanup(request: pytest.FixtureRequest) -> None:
    """
    An autouse fixture to ensure a clean state for every API test.

    This fixture runs each test function. It checks if the test is using
    the `api_service` fixture. If it is, it calls the `/test/clear-users`
    endpoint to guarantee the test starts with no pre-existing user data.
    """
    if "api_service" in request.fixturenames:
        api_base_url: str = request.getfixturevalue('api_service')
        logger.info("AUTOUSE CLEANUP: Clearing all users before test starts.")
        try:
            response = requests.post(f"{api_base_url}/test/clear-users", timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Failed to clear users during pre-test cleanup: {e}")


@pytest.fixture()
def created_test_user(api_service: str) -> Iterator[Dict[str, Any]]:
    """
    Pytest fixture to create a single user and guarantee its deletion after the test.
    It yields the data of the created user to the test function.
    """
    logger.debug("Fixture 'created_user': Setting up user.")
    users_url: str = f"{api_service}/users"
    user_data: Dict[str, Any] = {
        "id": 888,
        "name": "TestUser Name",
        "email": "testuser.name@example.com"
    }
    user_id_to_delete: int | None = None

    try:
        response = requests.post(users_url, json=user_data, timeout=10)
        response.raise_for_status()
        created_user_data: Dict[str, Any] = response.json()
        user_id_to_delete = created_user_data["id"]

        logger.debug(
            f"Fixture 'created_user': successfully created user {user_id_to_delete}"
        )

        yield created_user_data
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Fixture 'created_user' failed during setup: {e}")
    finally:
        if user_id_to_delete:
            logger.debug(
                f"Fixture 'created_user': cleaning up user {user_id_to_delete}"
            )
            delete_user_if_exists(api_service, user_id_to_delete)


@pytest.fixture()
def three_test_users(
    api_service: str
) -> Iterator[Tuple[str, Dict[str, Dict[str, Any]]]]:
    """
    Sets up three users via a test endpoint and yields the API service URL
    and a dictionary of the created users, keyed by their ID.
    """
    logger.debug("Fixture 'post_users_json': Setting up users.")
    users_to_create_list: List[Dict[str, Any]] = [
        {"id": 231, "name": "Alice Hetun", "email": "alicehetun5828@example.com"},
        {"id": 783, "name": "Bob Smith", "email": "bobsmith01842@example.com"},
        {"id": 325, "name": "Charlie Brown", "email": "charliebrown6632@example.com"},
    ]
    setup_payload: Dict[str, List[Dict[str, Any]]] = {"users": users_to_create_list}

    try:
        response = requests.post(
            f"{api_service}/test/setup-users", json=setup_payload, timeout=10
        )
        response.raise_for_status()
        logger.debug(
            "Fixture 'post_users_json': Users set up via /test/setup-users. "
            f"Response: {response.json()}"
        )
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Fixture 'post_users_json' failed during setup: {e}")

    users_data_for_test_assertion: Dict[str, Dict[str, Any]] = {
        str(u["id"]): u for u in users_to_create_list
    }

    yield api_service, users_data_for_test_assertion
