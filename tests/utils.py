import logging
import requests
import json
from typing import Any, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


def delete_user_if_exists(base_url: str, user_id: int) -> None:
    delete_url = f"{base_url}/users/{user_id}"
    response = requests.delete(delete_url, timeout=10)
    if response.status_code == 204:
        logger.debug(f"Teardown: Deleted user {user_id}")
    elif response.status_code == 404:
        logger.debug(f"Teardown: User {user_id} not found, no need to delete.")
    else:
        logger.warning(
            f"Teardown: Failed to delete user {user_id}, status: {response.status_code}"
        )
        raise Exception(
            f"Failed to delete user {user_id}, status: {response.status_code}"
        )


def load_schema(name: str) -> Dict[str, Any]:
    schema_path = Path(__file__).parent.parent / "schemas" / name
    if not schema_path.exists():
        logger.warning(f"Schema file not found: {schema_path}")
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    with open(schema_path, "r", encoding='utf-8') as f:
        logger.debug(f"Loaded {name} schema.")
        return json.load(f)
