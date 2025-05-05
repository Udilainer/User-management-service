# User Management Service

A simple Python project demonstrating user management functionalities, including adding, removing, loading from JSON, and exporting to JSON, with comprehensive testing using pytest.

## Features

* Add new users with validation (ID, Name, Email).
* Remove users by ID.
* Load user data from a JSON file, skipping invalid entries.
* Overwrite existing users when loading conflicting IDs from JSON.
* Export current user list to a JSON file.
* Configurable logging.
* Comprehensive unit and integration tests using pytest.

## Prerequisites

* Python 3.9+
* pip (Python package installer)

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Genidit/User-management-service.git
    cd User_Management_Service
    ```
2.  **Create a virtual environment (Recommended):**
    ```bash
    python -m venv venv
    # Activate the environment
    # Windows:
    # .\venv\Scripts\activate
    # macOS/Linux:
    # source venv/bin/activate
    ```
3.  **Install the project in editable mode (includes runtime dependencies):**
    ```bash
    pip install -e .
    ```
4.  **Install test dependencies (if needed separately):**
    ```bash
    pip install -e .[test]
    ```

## Configuration

* **Logging:** Logging behavior is configured in `config/logging.ini`. Modify this file to change log levels, output destinations (file/console), and formats.
* **Default Data File:** The default user data file used by `main.py` (if applicable) or default methods is typically `data/users.json`.

## Usage

```bash
python src/main.py
```

## Running Tests

This project uses `pytest`. Configuration options (`-v`, `-s`) are set in `pytest.ini`.

1.  Ensure test dependencies are installed (e.g., `pip install -e .[test]`).
2.  Run tests from the project root directory:
    ```bash
    pytest
    ```

## Project Structure

```
├─── config/
├─── data/
├─── logs/
├─── src/
│    └─── user_management.py
│    └─── main.py
├─── tests/
│    └─── conftest.py
│    └─── test_user_management.py
├─── .gitignore
├─── pyproject.toml
├─── pytest.ini
├─── requirements.txt
└─── README.md
```

## Built With

* Python
* email_validator - For robust email address validation
* pytest - Testing framework
* pytest-mock - Mocking library for pytest

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.