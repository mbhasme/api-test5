import pytest
import requests

BASE_URL = "https://jsonplaceholder.typicode.com"

def test_get_todo_status_code():
    response = requests.get(f"{BASE_URL}/todos/1")
    assert response.status_code == 200

def test_get_todo_response_body():
    response = requests.get(f"{BASE_URL}/todos/1")
    response_json = response.json()
    assert response_json["userId"] == 1
    assert response_json["id"] == 1
    assert response_json["title"] == "delectus aut autem"
    assert response_json["completed"] is False
