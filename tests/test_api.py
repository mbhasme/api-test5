import pytest
import requests

BASE_URL = "https://jsonplaceholder.typicode.com"

# Test data for status code checks
status_code_test_data = [
    (1, 200),  # todo_id, expected_status_code
    (2, 200),
    (0, 404),  # Assuming 0 is an invalid ID leading to 404
    (99999, 404) # Assuming a very large ID is not found
]

@pytest.mark.parametrize("todo_id, expected_status_code", status_code_test_data)
def test_get_todo_status_code(todo_id, expected_status_code):
    response = requests.get(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == expected_status_code

# Test data for response body checks
response_body_test_data = [
    (1, {"userId": 1, "id": 1, "title": "delectus aut autem", "completed": False}),
    (2, {"userId": 1, "id": 2, "title": "quis ut nam facilis et officia qui", "completed": False})
]

@pytest.mark.parametrize("todo_id, expected_data", response_body_test_data)
def test_get_todo_response_body(todo_id, expected_data):
    response = requests.get(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == 200  # Ensure we are checking a valid response
    response_json = response.json()
    assert response_json["userId"] == expected_data["userId"]
    assert response_json["id"] == expected_data["id"]
    assert response_json["title"] == expected_data["title"]
    assert response_json["completed"] == expected_data["completed"]

# Example of a test for a non-existent resource (can be combined or separate)
@pytest.mark.parametrize("todo_id", [0, 99999])
def test_get_non_existent_todo(todo_id):
    response = requests.get(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == 404
