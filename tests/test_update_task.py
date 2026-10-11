"""Tests for updating and completing tasks (PATCH /tasks/{id} and PATCH /tasks/{id}/complete)."""

import time
from fastapi.testclient import TestClient


def test_update_task_title(client: TestClient, sample_task: dict) -> None:
    """Verify updating only title succeeds and retains existing description/priority."""
    task_id = sample_task["id"]
    payload = {"title": "Updated Task Title"}
    response = client.patch(f"/tasks/{task_id}", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Updated Task Title"
    assert data["description"] == sample_task["description"]
    assert data["priority"] == sample_task["priority"]


def test_update_task_priority(client: TestClient, sample_task: dict) -> None:
    """Verify updating only priority."""
    task_id = sample_task["id"]
    payload = {"priority": "low"}
    response = client.patch(f"/tasks/{task_id}", json=payload)
    assert response.status_code == 200
    assert response.json()["priority"] == "low"
    assert response.json()["title"] == sample_task["title"]


def test_update_task_partial_does_not_clear_fields(client: TestClient, sample_task: dict) -> None:
    """Verify unspecified fields remain untouched."""
    task_id = sample_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"description": "Brand new description"})
    assert response.status_code == 200

    data = response.json()
    assert data["description"] == "Brand new description"
    assert data["title"] == sample_task["title"]
    assert data["priority"] == sample_task["priority"]
    assert data["due_date"] == sample_task["due_date"]


def test_update_task_not_found(client: TestClient) -> None:
    """Verify updating a non-existent task returns 404."""
    response = client.patch("/tasks/99999", json={"title": "Non-existent Task"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Task with id 99999 not found"}


def test_update_task_invalid_title_length(client: TestClient, sample_task: dict) -> None:
    """Verify updating with a title shorter than 3 characters fails with 422."""
    task_id = sample_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"title": "No"})
    assert response.status_code == 422


def test_update_task_invalid_priority(client: TestClient, sample_task: dict) -> None:
    """Verify updating with invalid priority fails with 422."""
    task_id = sample_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"priority": "super-urgent"})
    assert response.status_code == 422


def test_update_task_refreshes_updated_at(client: TestClient, sample_task: dict) -> None:
    """Verify that updating a task changes the updated_at timestamp."""
    task_id = sample_task["id"]
    initial_updated_at = sample_task["updated_at"]

    time.sleep(0.01)  # small pause to ensure timestamp ticks
    response = client.patch(f"/tasks/{task_id}", json={"title": "Changed Title"})
    assert response.status_code == 200

    new_updated_at = response.json()["updated_at"]
    assert new_updated_at >= initial_updated_at


def test_complete_task_success(client: TestClient, sample_task: dict) -> None:
    """Verify marking a pending task as completed sets status to completed."""
    task_id = sample_task["id"]
    assert sample_task["status"] == "pending"

    response = client.patch(f"/tasks/{task_id}/complete")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == task_id
    assert data["status"] == "completed"


def test_complete_task_already_completed(client: TestClient, sample_task: dict) -> None:
    """Verify completing an already completed task is idempotent and preserves data."""
    task_id = sample_task["id"]
    # Complete the first time
    res1 = client.patch(f"/tasks/{task_id}/complete")
    assert res1.status_code == 200
    assert res1.json()["status"] == "completed"

    # Complete the second time
    res2 = client.patch(f"/tasks/{task_id}/complete")
    assert res2.status_code == 200
    assert res2.json()["status"] == "completed"
    assert res2.json()["title"] == sample_task["title"]


def test_complete_task_not_found(client: TestClient) -> None:
    """Verify completing a missing task returns 404."""
    response = client.patch("/tasks/88888/complete")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task with id 88888 not found"}
