"""Tests for edge cases, unusual payloads, malformed requests, and boundaries."""

from fastapi.testclient import TestClient


def test_malformed_json_on_create(client: TestClient) -> None:
    """Verify malformed JSON on POST /tasks returns 400 Bad Request."""
    malformed_body = '{"title": "Test",'
    response = client.post(
        "/tasks",
        content=malformed_body,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Malformed JSON request body"}


def test_malformed_json_on_update(client: TestClient, sample_task: dict) -> None:
    """Verify malformed JSON on PATCH /tasks/{id} returns 400 Bad Request."""
    task_id = sample_task["id"]
    malformed_body = '{"title": "Updated", '
    response = client.patch(
        f"/tasks/{task_id}",
        content=malformed_body,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Malformed JSON request body"}


def test_wrong_content_type_handling(client: TestClient) -> None:
    """Verify sending non-JSON content-type to /tasks results in 422 Unprocessable Entity."""
    response = client.post(
        "/tasks",
        content="plain text content",
        headers={"Content-Type": "text/plain"},
    )
    assert response.status_code == 422


def test_special_characters_and_unicode_in_task(client: TestClient) -> None:
    """Verify tasks support emojis, accents, and punctuation safely."""
    payload = {
        "title": "Fix 🐞 in Système d'exploitation! 🚀",
        "description": "Unicode test: 日本語, العربية, and symbols: <>&'\"@#$%",
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]


def test_empty_description_allowed(client: TestClient) -> None:
    """Verify an empty string description is accepted (or None)."""
    payload = {"title": "Task with empty description", "description": ""}
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    assert response.json()["description"] == ""


def test_duplicate_task_titles_allowed(client: TestClient) -> None:
    """Verify creating multiple tasks with identical titles creates distinct entries with unique IDs."""
    res1 = client.post("/tasks", json={"title": "Duplicate Title"})
    res2 = client.post("/tasks", json={"title": "Duplicate Title"})

    assert res1.status_code == 201
    assert res2.status_code == 201
    assert res1.json()["id"] != res2.json()["id"]


def test_boundary_pagination_exact_limits(client: TestClient) -> None:
    """Verify minimum valid pagination values (skip=0, limit=1 and limit=100) are accepted."""
    client.post("/tasks", json={"title": "Boundary Task 1"})

    res_min = client.get("/tasks?skip=0&limit=1")
    assert res_min.status_code == 200
    assert len(res_min.json()) == 1

    res_max = client.get("/tasks?skip=0&limit=100")
    assert res_max.status_code == 200
    assert len(res_max.json()) == 1


def test_database_isolation(client: TestClient) -> None:
    """Verify database is isolated: previous test tasks do not leak into this test."""
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_get_db_session_dependency() -> None:
    """Verify real get_db generator yields a session and closes cleanly."""
    from app.database.database import get_db
    from sqlalchemy.orm import Session

    gen = get_db()
    db = next(gen)
    assert isinstance(db, Session)
    try:
        next(gen)
    except StopIteration:
        pass


def test_unhandled_exception_handler(client: TestClient) -> None:
    """Verify unhandled generic exceptions return 500 without leaking stack traces."""
    from unittest.mock import patch
    with patch("app.services.task_service.task_service.get_tasks", side_effect=RuntimeError("Simulated crash")):
        response = client.get("/tasks")
        assert response.status_code == 500
        assert response.json() == {"detail": "Internal server error"}

