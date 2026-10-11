"""Tests for the /health endpoint."""

from fastapi.testclient import TestClient


def test_health_returns_200(client: TestClient) -> None:
    """Verify that GET /health returns HTTP 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_structure(client: TestClient) -> None:
    """Verify that GET /health returns the exact expected payload."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "ok"}
    assert isinstance(data["status"], str)


def test_health_response_content_type(client: TestClient) -> None:
    """Verify that GET /health returns application/json content type."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")


def test_root_dashboard_returns_html(client: TestClient) -> None:
    """Verify that GET / serves the HTML web dashboard."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "TaskFlow" in response.text

