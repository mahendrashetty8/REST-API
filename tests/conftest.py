"""Pytest configuration and reusable fixtures for TaskFlow API tests."""

from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base, get_db
from app.main import app

# Isolated in-memory SQLite database dedicated for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(autouse=True)
def setup_and_teardown_db() -> Generator[None, None, None]:
    """Create fresh database tables before each test and drop them after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provide a clean, isolated SQLAlchemy session for direct database tests."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Provide a FastAPI TestClient with the database dependency overridden."""
    def override_get_db() -> Generator[Session, None, None]:
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_task_payload() -> dict:
    """Provide a valid dictionary payload for creating a task."""
    return {
        "title": "Learn FastAPI Testing",
        "description": "Comprehensive automated testing for REST APIs",
        "priority": "high",
        "due_date": "2026-10-30",
    }


@pytest.fixture
def sample_task(client: TestClient, sample_task_payload: dict) -> dict:
    """Fixture that creates and returns a sample task via the API."""
    response = client.post("/tasks", json=sample_task_payload)
    assert response.status_code == 201
    return response.json()
