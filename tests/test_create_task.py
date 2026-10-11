"""Tests for task creation (POST /tasks)."""

import pytest
from fastapi.testclient import TestClient


def test_create_task_minimal_valid(client: TestClient) -> None:
    """Verify creating a task with only required fields succeeds."""
    payload = {"title": "Minimal Task"}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "Minimal Task"
    assert data["description"] is None
    assert data["priority"] == "medium"  # default
    assert data["status"] == "pending"   # default
    assert data["due_date"] is None
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_full_valid(client: TestClient) -> None:
    """Verify creating a task with all fields supplied succeeds."""
    payload = {
        "title": "Comprehensive Task",
        "description": "Thoroughly test all fields and persistence",
        "priority": "high",
        "due_date": "2026-11-20",
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["priority"] == "high"
    assert data["status"] == "pending"
    assert data["due_date"] == "2026-11-20"


def test_create_task_low_priority(client: TestClient) -> None:
    """Verify task creation with low priority succeeds."""
    response = client.post("/tasks", json={"title": "Low Priority Task", "priority": "low"})
    assert response.status_code == 201
    assert response.json()["priority"] == "low"


def test_create_task_missing_title_fails(client: TestClient) -> None:
    """Verify creating a task without title fails with 422."""
    payload = {"description": "A task with no title"}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()


def test_create_task_empty_title_fails(client: TestClient) -> None:
    """Verify creating a task with empty string title fails with 422."""
    payload = {"title": ""}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 422


def test_create_task_short_title_fails(client: TestClient) -> None:
    """Verify title with less than 3 characters fails with 422."""
    payload = {"title": "Hi"}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 422


def test_create_task_exact_minimum_title_length(client: TestClient) -> None:
    """Verify title with exactly 3 characters succeeds."""
    payload = {"title": "Abc"}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    assert response.json()["title"] == "Abc"


def test_create_task_long_title_fails(client: TestClient) -> None:
    """Verify title with more than 100 characters fails with 422."""
    payload = {"title": "A" * 101}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 422


def test_create_task_exact_maximum_title_length(client: TestClient) -> None:
    """Verify title with exactly 100 characters succeeds."""
    payload = {"title": "A" * 100}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    assert len(response.json()["title"]) == 100


def test_create_task_long_description_fails(client: TestClient) -> None:
    """Verify description exceeding 500 characters fails with 422."""
    payload = {"title": "Valid Title", "description": "D" * 501}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 422


def test_create_task_exact_maximum_description_length(client: TestClient) -> None:
    """Verify description of exactly 500 characters succeeds."""
    payload = {"title": "Valid Title", "description": "D" * 500}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    assert len(response.json()["description"]) == 500


def test_create_task_invalid_priority_fails(client: TestClient) -> None:
    """Verify invalid priority string fails with 422."""
    payload = {"title": "Valid Title", "priority": "critical"}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 422


def test_create_task_invalid_date_fails(client: TestClient) -> None:
    """Verify non-date string for due_date fails with 422."""
    payload = {"title": "Valid Title", "due_date": "not-a-valid-date"}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 422
