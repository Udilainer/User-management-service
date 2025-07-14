# User Management Service

A simple Python project demonstrating user management functionalities via a REST API (built with FastAPI), including adding, removing, loading from JSON, and exporting to JSON. Features robust validation and comprehensive testing using pytest with Allure reporting.

## Features

* REST API endpoints (`GET`, `POST`, `DELETE`) for user management via FastAPI.
* Add new users with validation (ID, Name, Email format and constraints) using Pydantic.
* Remove users by ID.
* Load user data from a JSON file, skipping invalid entries and overwriting duplicates.
* Export current user list to a JSON file.
* Configurable logging via `config/logging.ini`.
* Comprehensive unit and integration tests using pytest.
* API response validation using custom JSON schemas (for User and User List).
* Detailed test reporting using Allure.

## Prerequisites

* Python 3.9+
* pip and venv (standard with Python)
* Allure Commandline Tool (for viewing reports, see "Viewing Test Reports" section)

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd User_Management_Service
    ```
2.  **Create and activate a virtual environment (Recommended):**
    ```bash
    python -m venv venv
    # Windows: .\venv\Scripts\activate
    # macOS/Linux: source venv/bin/activate
    ```
3.  **Install the project in editable mode with test dependencies:**
    ```bash
    # This installs runtime dependencies (fastapi, pydantic, email-validator),
    # the project package itself, and test dependencies
    # (pytest, pytest-mock, allure-pytest, uvicorn) defined in pyproject.toml
    pip install -e .[test]
    ```

## Configuration

* **Logging:** Logging behavior is configured in `config/logging.ini`. Modify this file to change log levels, output destinations (file/console), and formats. The API service loads this configuration on startup.
* **Default Data File:** The service attempts to preload user data from `data/users.json` on startup by default (if the file exists).

## Running the API Service

1.  Ensure your virtual environment is activated and dependencies are installed.
2.  Run the FastAPI application using Uvicorn from the project root directory:
    ```bash
    uvicorn src.api:app --reload
    ```
    * `--reload` enables auto-reloading for development. Remove for production deployments.
3.  The API will typically be available at `http://127.0.0.1:8000`.
4.  Interactive API documentation (Swagger UI) is available at `http://127.0.0.1:8000/docs`.
5.  Alternative API documentation (ReDoc) is available at `http://127.0.0.1:8000/redoc`.

## Running Tests

This project uses `pytest` and generates detailed report data using Allure.

1.  Ensure test dependencies are installed (see Installation section).
2.  Run tests from the project root directory, generating Allure results:
    ```bash
    python -m pytest --alluredir=allure-results
    ```
    *(Test options like `-v` and `-s` are configured in `pytest.ini` and applied automatically)*
3.  With the clearing of old Allure Reports (powershell):
    ```bash
    Remove-Item -Recurse -Force allure-results; python -m pytest --alluredir=allure-results
    ```

## Viewing Test Reports

Test execution generates detailed reports using Allure.

1.  **Generate Allure Results:** Run pytest with the `--alluredir` option:
    ```bash
    python -m pytest --alluredir=allure-results
    ```
2.  **Prerequisite: Allure Commandline Tool**
    You must have the Allure Commandline tool installed to generate the report. Please follow the official installation guide for your operating system:
    [https://allurereport.org/docs/gettingstarted-installation/](https://allurereport.org/docs/gettingstarted-installation/)
3.  **Generate and View Report**
    After generating the results, execute the following command from your project root:
    ```bash
    allure serve allure-results
    ```
    This command will generate the HTML report and open it in your default web browser.

## Project Structure

```
User_Management_Service/
├── config/               # Configuration files (logging.ini)
├── data/                 # Default data files (users.json)
├── logs/                 # Log output files (ignored by git)
├── schemas/              # JSON schemas (meta and custom)
│   ├── user_schema.json  # Schema for a single User object
│   ├── user_list_schema.json # Schema for a list of User objects
│   └── meta/             # Meta schema for local validation (draft-07.json)
├── src/                  # Source code
│   ├── api.py            # FastAPI application and endpoints
│   ├── models.py         # Pydantic models
│   ├── user_management.py # Core logic (User class, UserService)
│   └── init.py
├── tests/                # Automated tests
│   ├── conftest.py       # Pytest fixtures
│   ├── utils.py          # Helper functions
│   ├── test_user_management.py # Test implementation
│   └── test_api.py       # Test implementation
├── .gitignore            # Git ignore rules
├── LICENSE               # Project license file
├── pyproject.toml        # Project metadata and dependencies (PEP 621)
├── pytest.ini            # Pytest configuration
└── README.md             # This file
```

## Built With

* Python
* FastAPI - Web framework for APIs
* Pydantic - Data validation and serialization
* Uvicorn - ASGI server
* email-validator - Email validation library (for Pydantic)
* pytest - Testing framework
* pytest-mock - Mocking library
* Allure Pytest - Reporting integration

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.