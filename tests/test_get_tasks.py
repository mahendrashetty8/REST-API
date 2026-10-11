"""Tests for task retrieval and listing (GET /tasks and GET /tasks/{task_id})."""

from fastapi.testclient import TestClient


def test_get_tasks_empty_list(client: TestClient) -> None:
    """Verify GET /tasks returns an empty list when no tasks exist."""
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_get_single_task_success(client: TestClient, sample_task: dict) -> None:
    """Verify retrieving an existing task by ID returns 200 and task details."""
    task_id = sample_task["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == sample_task["title"]


def test_get_single_task_not_found(client: TestClient) -> None:
    """Verify requesting a non-existent task returns 404 with standard message."""
    response = client.get("/tasks/99999")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Task with id 99999 not found"}


def test_get_single_task_negative_id(client: TestClient) -> None:
    """Verify requesting a negative task ID returns 404 not found."""
    response = client.get("/tasks/-1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task with id -1 not found"}


def test_get_single_task_very_large_id(client: TestClient) -> None:
    """Verify requesting a very large task ID returns 404 not found."""
    response = client.get("/tasks/2147483647")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task with id 2147483647 not found"}


def test_get_tasks_pagination(client: TestClient) -> None:
    """Verify skip and limit parameters paginate tasks properly."""
    for i in range(5):
        client.post("/tasks", json={"title": f"Task Number {i}"})

    # Page 1: skip=0, limit=2
    res1 = client.get("/tasks?skip=0&limit=2")
    assert res1.status_code == 200
    data1 = res1.json()
    assert len(data1) == 2
    assert data1[0]["title"] == "Task Number 0"
    assert data1[1]["title"] == "Task Number 1"

    # Page 2: skip=2, limit=2
    res2 = client.get("/tasks?skip=2&limit=2")
    assert res2.status_code == 200
    data2 = res2.json()
    assert len(data2) == 2
    assert data2[0]["title"] == "Task Number 2"
    assert data2[1]["title"] == "Task Number 3"

    # Beyond total: skip=10, limit=10
    res3 = client.get("/tasks?skip=10&limit=10")
    assert res3.status_code == 200
    assert res3.json() == []


def test_get_tasks_filter_by_status(client: TestClient) -> None:
    """Verify filtering tasks by status."""
    t1 = client.post("/tasks", json={"title": "Pending Task"}).json()
    t2 = client.post("/tasks", json={"title": "Will Complete Task"}).json()

    # Complete the second task
    client.patch(f"/tasks/{t2['id']}/complete")

    # Filter pending
    res_pending = client.get("/tasks?status=pending")
    assert res_pending.status_code == 200
    pending_tasks = res_pending.json()
    assert all(t["status"] == "pending" for t in pending_tasks)
    assert any(t["id"] == t1["id"] for t in pending_tasks)
    assert not any(t["id"] == t2["id"] for t in pending_tasks)

    # Filter completed
    res_completed = client.get("/tasks?status=completed")
    assert res_completed.status_code == 200
    completed_tasks = res_completed.json()
    assert all(t["status"] == "completed" for t in completed_tasks)
    assert any(t["id"] == t2["id"] for t in completed_tasks)


def test_get_tasks_filter_by_priority(client: TestClient) -> None:
    """Verify filtering tasks by priority."""
    client.post("/tasks", json={"title": "Low Task", "priority": "low"})
    client.post("/tasks", json={"title": "Medium Task", "priority": "medium"})
    client.post("/tasks", json={"title": "High Task", "priority": "high"})

    res_high = client.get("/tasks?priority=high")
    assert res_high.status_code == 200
    high_tasks = res_high.json()
    assert all(t["priority"] == "high" for t in high_tasks)
    assert len(high_tasks) >= 1


def test_get_tasks_combined_filters(client: TestClient) -> None:
    """Verify combining status and priority filters."""
    client.post("/tasks", json={"title": "High Pending", "priority": "high"})
    t_to_complete = client.post("/tasks", json={"title": "High Completed", "priority": "high"}).json()
    client.patch(f"/tasks/{t_to_complete['id']}/complete")

    client.post("/tasks", json={"title": "Low Pending", "priority": "low"})

    res = client.get("/tasks?status=pending&priority=high")
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "High Pending"


def test_get_tasks_invalid_skip_fails(client: TestClient) -> None:
    """Verify negative skip parameter fails with 422."""
    response = client.get("/tasks?skip=-1")
    assert response.status_code == 422


def test_get_tasks_invalid_limit_zero_fails(client: TestClient) -> None:
    """Verify limit=0 fails with 422."""
    response = client.get("/tasks?limit=0")
    assert response.status_code == 422


def test_get_tasks_invalid_limit_too_large_fails(client: TestClient) -> None:
    """Verify limit > 100 fails with 422."""
    response = client.get("/tasks?limit=101")
    assert response.status_code == 422
