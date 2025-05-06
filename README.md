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
3.  **Install the project in editable mode with test dependencies:**
    ```bash
    # This installs runtime deps (if any), the project package,
    # pytest, pytest-mock, and allure-pytest
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

This project uses `pytest` and generates detailed report data using Allure.

1.  Ensure test dependencies are installed (see Installation section).
2.  Run tests from the project root directory, generating Allure results:
    ```bash
    pytest --alluredir=allure-results
    ```
    *(Test options like `-v` and `-s` are configured in `pytest.ini` and applied automatically)*

## Viewing Test Reports

Test results can be viewed using the Allure Framework's reporting UI.

1.  **Prerequisite: Allure Commandline**
    You must have the Allure Commandline tool installed to generate the report. Please follow the official installation guide for your operating system:
    [https://allurereport.org/docs/gettingstarted-installation/](https://allurereport.org/docs/gettingstarted-installation/)

2.  **Generate and View Report**
    After running the tests using the command above (which creates the `allure-results` directory), execute the following command from your project root:
    ```bash
    allure serve allure-results
    ```
    This command will generate the HTML report and open it in your default web browser.

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
* pytest - Testing framework
* pytest-mock - Mocking library
* allure-pytest - For generating Allure report data
* email-validator - For robust email validation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.