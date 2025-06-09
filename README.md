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

### Parameterized Testing (Data-Driven Tests)

For testing multiple scenarios with the same test logic but different data, you can use `pytest.mark.parametrize`. This allows you to define a set of input data and expected outcomes, and `pytest` will generate a test case for each combination.

**Example:**

To test different todo IDs and their expected status codes:

```python
import pytest
import requests

BASE_URL = "https://jsonplaceholder.typicode.com" # Or your API's base URL

# Define test data: list of tuples (input_value, expected_output)
status_code_test_data = [
    (1, 200),  # (todo_id, expected_status_code)
    (2, 200),
    (0, 404),  # Example: an invalid ID
    (99999, 404) # Example: a non-existent ID
]

@pytest.mark.parametrize("todo_id, expected_status_code", status_code_test_data)
def test_get_todo_status_code(todo_id, expected_status_code):
    response = requests.get(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == expected_status_code
```

In this example:
- `status_code_test_data` holds the different sets of `todo_id` and `expected_status_code`.
- The `@pytest.mark.parametrize("todo_id, expected_status_code", status_code_test_data)` decorator tells pytest to run `test_get_todo_status_code` multiple times, once for each tuple in `status_code_test_data`.
- In each run, `todo_id` and `expected_status_code` will be assigned the values from the current tuple.

You can use a similar approach to parameterize other aspects of your tests, such as request payloads or parts of the expected response body.
