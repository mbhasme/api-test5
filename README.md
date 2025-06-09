# API Testing Framework

This project contains an API testing framework using pytest.

## Recommended Python Version

It is recommended to use Python 3.8 or higher for this project.

## Setup

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```
2.  **Activate the virtual environment:**
    *   On Windows:
        ```bash
        venv\Scripts\activate
        ```
    *   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running Tests

To run the API tests, use the following command:
```bash
pytest
```

## Adding New Tests

1.  Open the `tests/test_api.py` file.
2.  Add new test functions using the `pytest` conventions.
3.  You can use the `requests` library to make API calls and assert the responses.
