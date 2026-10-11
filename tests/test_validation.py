"""Tests focused purely on validation constraints and error structures."""

from fastapi.testclient import TestClient


def test_validation_empty_body(client: TestClient) -> None:
    """Verify posting without body produces 422."""
    response = client.post("/tasks")
    assert response.status_code == 422
    assert "detail" in response.json()


def test_validation_empty_json_object(client: TestClient) -> None:
    """Verify posting empty JSON object produces 422 because title is required."""
    response = client.post("/tasks", json={})
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(err["loc"][-1] == "title" for err in errors)


def test_validation_title_null(client: TestClient) -> None:
    """Verify title=None produces 422."""
    response = client.post("/tasks", json={"title": None})
    assert response.status_code == 422


def test_validation_title_numeric_or_bool(client: TestClient) -> None:
    """Verify non-string title produces validation error."""
    response = client.post("/tasks", json={"title": 12345})
    # Either coerced or validated, but if list/dict:
    response_dict = client.post("/tasks", json={"title": {"nested": "obj"}})
    assert response_dict.status_code == 422


def test_validation_title_below_minimum_length(client: TestClient) -> None:
    """Verify title with 1 or 2 characters fails with 422."""
    for short_title in ["a", "ab"]:
        res = client.post("/tasks", json={"title": short_title})
        assert res.status_code == 422


def test_validation_title_above_maximum_length(client: TestClient) -> None:
    """Verify title with 101 characters fails with 422."""
    res = client.post("/tasks", json={"title": "x" * 101})
    assert res.status_code == 422


def test_validation_description_above_maximum_length(client: TestClient) -> None:
    """Verify description with 501 characters fails with 422."""
    res = client.post("/tasks", json={"title": "Valid Title", "description": "y" * 501})
    assert res.status_code == 422


def test_validation_invalid_priority_enum(client: TestClient) -> None:
    """Verify invalid priority string fails."""
    for invalid_priority in ["extreme", "urgent", "MEDIUM", 123]:
        res = client.post("/tasks", json={"title": "Valid Title", "priority": invalid_priority})
        assert res.status_code == 422


def test_validation_invalid_due_date_format(client: TestClient) -> None:
    """Verify invalid date strings fail validation."""
    for invalid_date in ["31-12-2026", "2026/12/31", "tomorrow", "invalid"]:
        res = client.post("/tasks", json={"title": "Valid Title", "due_date": invalid_date})
        assert res.status_code == 422


def test_validation_skip_negative(client: TestClient) -> None:
    """Verify GET /tasks with negative skip parameter returns 422."""
    res = client.get("/tasks?skip=-5")
    assert res.status_code == 422
    assert "detail" in res.json()


def test_validation_limit_zero(client: TestClient) -> None:
    """Verify GET /tasks with limit=0 returns 422."""
    res = client.get("/tasks?limit=0")
    assert res.status_code == 422


def test_validation_limit_exceeds_maximum(client: TestClient) -> None:
    """Verify GET /tasks with limit=101 returns 422."""
    res = client.get("/tasks?limit=101")
    assert res.status_code == 422


def test_validation_invalid_query_enum(client: TestClient) -> None:
    """Verify GET /tasks with invalid status or priority query param returns 422."""
    res1 = client.get("/tasks?status=unknown_status")
    assert res1.status_code == 422

    res2 = client.get("/tasks?priority=mega")
    assert res2.status_code == 422
