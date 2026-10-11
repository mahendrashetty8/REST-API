"""Tests for task deletion (DELETE /tasks/{task_id})."""

from fastapi.testclient import TestClient


def test_delete_existing_task_returns_204(client: TestClient, sample_task: dict) -> None:
    """Verify deleting an existing task returns 204 No Content with empty body."""
    task_id = sample_task["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
    assert response.text == ""


def test_deleted_task_cannot_be_retrieved(client: TestClient, sample_task: dict) -> None:
    """Verify that after deletion, GET /tasks/{id} returns 404."""
    task_id = sample_task["id"]
    del_res = client.delete(f"/tasks/{task_id}")
    assert del_res.status_code == 204

    get_res = client.get(f"/tasks/{task_id}")
    assert get_res.status_code == 404
    assert get_res.json() == {"detail": f"Task with id {task_id} not found"}


def test_delete_missing_task_returns_404(client: TestClient) -> None:
    """Verify attempting to delete a non-existent task returns 404."""
    response = client.delete("/tasks/99999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task with id 99999 not found"}


def test_delete_twice_returns_404(client: TestClient, sample_task: dict) -> None:
    """Verify deleting a task a second time returns 404."""
    task_id = sample_task["id"]
    res1 = client.delete(f"/tasks/{task_id}")
    assert res1.status_code == 204

    res2 = client.delete(f"/tasks/{task_id}")
    assert res2.status_code == 404
    assert res2.json() == {"detail": f"Task with id {task_id} not found"}
