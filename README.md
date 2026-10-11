# TaskFlow API

[![CI Pipeline](https://github.com/mahendrashetty8/fileguard/actions/workflows/tests.yml/badge.svg)](https://github.com/mahendrashetty8/fileguard/actions/workflows/tests.yml)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](#coverage)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

TaskFlow is a reliable, production-ready task-management REST API built with FastAPI, Pydantic v2, and SQLAlchemy 2.x. It demonstrates clean architecture, strong type safety, robust validation, resilient error handling, comprehensive test coverage (with heavy prioritization of failure and edge cases), and full CI/CD automation.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the API](#running-the-api)
- [API Documentation](#api-documentation)
- [Endpoints](#endpoints)
- [Request Examples](#request-examples)
- [Response Examples](#response-examples)
- [Error Handling](#error-handling)
- [Testing](#testing)
- [Testing Philosophy](#testing-philosophy)
- [Coverage](#coverage)
- [CI/CD](#cicd)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Overview

The primary goal of TaskFlow is not to build an overly complex monolithic system, but rather to serve as an exemplary standard for modern, production-grade REST APIs. It is designed to be accessible to BCA/AI-ML students while strictly adhering to enterprise backend engineering best practices.

Key highlights:
- **Strong Typing**: 100% type-annotated code with strict Pydantic v2 schemas and SQLAlchemy 2.0 `Mapped` attributes.
- **RESTful Principles**: Proper HTTP methods (`GET`, `POST`, `PATCH`, `DELETE`), idiomatic status codes (`200`, `201`, `204`, `400`, `404`, `422`, `500`), and stateless interaction.
- **Defensive Error Handling**: Structured JSON responses for missing resources, malformed JSON, and validation errors without ever leaking Python tracebacks or database internals.
- **100% Test Coverage**: A test suite containing 65+ automated tests with an emphasis on boundary conditions, malformed input, and database isolation.

---

## Features

- **Create Tasks**: Create new tasks with title validation (3–100 chars), optional description (max 500 chars), priority enum, and optional due date.
- **List & Filter Tasks**: Retrieve tasks with offset pagination (`skip`, `limit`) and filtering by `status` (`pending`, `completed`) or `priority` (`low`, `medium`, `high`).
- **Retrieve Task by ID**: Fetch a single task by its integer identifier.
- **Partial Updates**: Safely update task fields without overwriting unsupplied fields with `null` or defaults.
- **Complete Tasks**: Mark tasks as completed idempotently without data corruption.
- **Delete Tasks**: Remove tasks returning HTTP 204 No Content.
- **Health Checks**: Fast endpoint to verify API health and availability.
- **Malformed JSON Interception**: Custom exception handling returning `400 Bad Request` instead of cryptic errors.

---

## Tech Stack

- **Python**: 3.11+ (tested on Python 3.11, 3.12, and 3.13)
- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: High-performance ASGI web server
- **Pydantic v2**: High-performance data validation and settings management
- **SQLAlchemy 2.x**: SQL toolkit and Object-Relational Mapper using modern declarative models
- **SQLite**: Zero-configuration, serverless SQL database engine
- **pytest & pytest-cov**: Automated testing framework and coverage measurement
- **HTTPX & FastAPI TestClient**: Async and sync HTTP testing tools
- **GitHub Actions**: Continuous Integration pipeline

---

## Architecture

The project adheres to a clean layered architecture, ensuring separation of concerns:

```text
HTTP Client (Browser / cURL / Frontend)
                 │
                 ▼
        [ FastAPI Application ]
                 │
        ┌────────┴────────┐
        ▼                 ▼
   [ /health ]       [ /tasks ]  <── Routers Layer (HTTP & Status codes)
                          │
                          ▼
                  [ TaskService ] <── Business Logic Layer
                          │
                          ▼
                 [ SQLAlchemy 2.x ] <── Persistence / Data Access Layer
                          │
                          ▼
                 [ SQLite Database ]
```

- **Routers**: Thin presentation layer handling routing, query/path parameters, dependency injection, and HTTP status codes.
- **Services**: Encapsulates business logic, data mutations, transactions, and domain exception raising.
- **Database / Models**: Defines SQLAlchemy declarative schemas and database connection lifecycle.
- **Schemas**: Validates input data and serializes output using Pydantic models.
- **Core**: Central configuration and domain-specific exceptions.

---

## Project Structure

```text
taskflow-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application entrypoint & exception handlers
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py               # Central settings (BaseSettings)
│   │   └── exceptions.py           # Custom domain exceptions (TaskNotFoundError)
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py             # Engine, SessionLocal, DeclarativeBase, get_db
│   │   └── models.py               # SQLAlchemy Task model
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── task.py                 # Pydantic schemas (Create, Update, Response, Enums)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py         # Business logic layer
│   │
│   └── routers/
│       ├── __init__.py
│       ├── health.py               # Health check route
│       └── tasks.py                # CRUD task routes
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures & isolated in-memory DB setup
│   ├── test_health.py              # Health check endpoint tests
│   ├── test_create_task.py         # Task creation tests (valid & invalid)
│   ├── test_get_tasks.py           # Retrieval, pagination, & filtering tests
│   ├── test_update_task.py         # Patch & complete endpoint tests
│   ├── test_delete_task.py         # Deletion & missing ID tests
│   ├── test_validation.py          # Field boundary & constraint tests
│   └── test_edge_cases.py          # Malformed JSON, types, unicode, isolation tests
│
├── .github/
│   └── workflows/
│       └── tests.yml               # GitHub Actions CI matrix workflow
│
├── reports/
│   └── .gitkeep                    # Directory for test/coverage artifacts
│
├── .gitignore                      # Python/virtualenv/coverage gitignore
├── LICENSE                         # MIT License
├── README.md                       # Comprehensive documentation
├── requirements.txt                # Runtime production dependencies
├── requirements-dev.txt            # Development & testing dependencies
├── pyproject.toml                  # PEP 517/518 build metadata & tool configs
└── pytest.ini                      # Pytest test discovery & flags
```

---

## Requirements

- Python 3.11 or newer
- `pip` and `virtualenv` / `venv`

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd taskflow-api
```

### 2. Create and activate a virtual environment

On Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Alternatively, install the package in editable development mode:
```bash
pip install -e ".[dev]"
```

---

## Configuration

TaskFlow is configured via environment variables or a `.env` file loaded through `pydantic-settings`.

Available variables:

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | string | `sqlite:///./taskflow.db` | SQLAlchemy connection string |
| `PROJECT_NAME` | string | `TaskFlow API` | Title displayed in OpenAPI docs |
| `VERSION` | string | `1.0.0` | API semver version |
| `DESCRIPTION` | string | `Reliable task management REST API` | API summary description |

To override defaults in development, create a `.env` file in the project root:
```ini
DATABASE_URL=sqlite:///./taskflow.db
```

---

## Running the API

Start the development server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The application will start at:
- **Base API**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## API Documentation

FastAPI auto-generates comprehensive interactive documentation based on Pydantic schemas and route annotations:

- **Swagger UI (`/docs`)**: Interactive sandbox to execute requests, inspect models, parameter constraints, and test validation errors directly in your browser.
- **ReDoc (`/redoc`)**: Structured, clean API reference documentation ideal for sharing and reading specifications.

---

## Endpoints

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | API health check | `200 OK` |
| `POST` | `/tasks` | Create a new task | `201 Created` |
| `GET` | `/tasks` | List tasks (pagination & filtering) | `200 OK` |
| `GET` | `/tasks/{task_id}` | Retrieve a task by ID | `200 OK` |
| `PATCH` | `/tasks/{task_id}` | Partially update a task | `200 OK` |
| `PATCH` | `/tasks/{task_id}/complete` | Mark a task as completed | `200 OK` |
| `DELETE` | `/tasks/{task_id}` | Delete a task | `204 No Content` |

---

## Request Examples

### 1. Health Check
```bash
curl -X GET http://127.0.0.1:8000/health
```

### 2. Create Task
```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn FastAPI",
    "description": "Build a REST API project",
    "priority": "high",
    "due_date": "2026-09-30"
  }'
```

### 3. List Tasks with Pagination & Filters
```bash
# Filter pending tasks with high priority
curl -X GET "http://127.0.0.1:8000/tasks?status=pending&priority=high&skip=0&limit=10"
```

### 4. Get Task by ID
```bash
curl -X GET http://127.0.0.1:8000/tasks/1
```

### 5. Update Task
```bash
curl -X PATCH http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn Advanced FastAPI",
    "priority": "high"
  }'
```

### 6. Complete Task
```bash
curl -X PATCH http://127.0.0.1:8000/tasks/1/complete
```

### 7. Delete Task
```bash
curl -X DELETE http://127.0.0.1:8000/tasks/1
```

---

## Response Examples

### Successful Task Creation (`201 Created`)
```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "description": "Build a REST API project",
  "priority": "high",
  "status": "pending",
  "due_date": "2026-09-30",
  "created_at": "2026-10-03T18:55:00.123456Z",
  "updated_at": "2026-10-03T18:55:00.123456Z"
}
```

### Health Check Response (`200 OK`)
```json
{
  "status": "ok"
}
```

### Missing Resource Error (`404 Not Found`)
```json
{
  "detail": "Task with id 999 not found"
}
```

### Malformed JSON Request (`400 Bad Request`)
```json
{
  "detail": "Malformed JSON request body"
}
```

### Validation Error (`422 Unprocessable Entity`)
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 3 characters",
      "input": "Hi",
      "ctx": {
        "min_length": 3
      }
    }
  ]
}
```

---

## Error Handling

TaskFlow implements consistent, production-safe error handling across all failure categories:

- **Validation Failures (`422`)**: Triggered when client data violates schema constraints (e.g. title too short, invalid enum value, malformed date string).
- **Malformed JSON (`400`)**: If a client sends broken JSON syntax (such as truncated braces or invalid quotes), the custom `RequestValidationError` handler intercepts `json_invalid` errors and returns a clear `400 Bad Request` instead of exposing internal parser traces.
- **Missing Resources (`404`)**: If an operation targets a non-existent task ID, domain exception `TaskNotFoundError` returns a predictable `{ "detail": "Task with id <id> not found" }`.
- **Invalid Query Parameters (`422`)**: Non-numeric or out-of-range pagination parameters (`skip < 0`, `limit < 1`, `limit > 100`) return descriptive validation errors.
- **Server Safety (`500`)**: Unhandled internal exceptions are captured by a global error handler that returns `{ "detail": "Internal server error" }` without exposing internal database or filesystem paths.

---

## Testing

The test suite is built with `pytest`, `pytest-cov`, and `httpx` (via FastAPI `TestClient`).

### Running Tests

Execute the full automated test suite:

```bash
pytest
```

Run tests with standard coverage output:

```bash
pytest --cov=app --cov-report=term-missing
```

---

## Testing Philosophy

> **The test suite prioritizes failure cases because invalid input, missing resources, malformed requests, and boundary conditions are common sources of production bugs.**
>
> **Success-path tests are also included, but the API's reliability is demonstrated primarily through its failure and edge-case tests.**

### Test Coverage Highlights
The test suite consists of **65 automated tests** organized into focused modules:

1. **`test_health.py`**: Verifies 200 OK, response structure, and JSON headers.
2. **`test_create_task.py`**: Tests valid minimal creation, full creation, default priorities, missing titles, empty titles, short titles (<3 chars), long titles (>100 chars), long descriptions (>500 chars), invalid enums, and invalid date formats.
3. **`test_get_tasks.py`**: Tests empty database state, ID lookup, 404 for missing IDs, negative task IDs, large 32-bit IDs, offset/limit pagination, status filters, priority filters, and combined filters.
4. **`test_update_task.py`**: Tests title updates, priority updates, partial updates (unspecified fields preserved), 404 on missing ID, invalid validation on updates, timestamp updating (`updated_at`), and task completion idempotency.
5. **`test_delete_task.py`**: Tests 204 No Content with empty body, verification that deleted tasks return 404, 404 on missing task deletion, and double deletion.
6. **`test_validation.py`**: Tests empty body, empty JSON object, wrong types, string lengths, enums, dates, and pagination boundaries (`skip=-1`, `limit=0`, `limit=101`).
7. **`test_edge_cases.py`**: Tests malformed JSON payloads (POST and PATCH), non-JSON content types, Unicode and emojis, duplicate titles, exact pagination bounds, session lifecycle, and 500 error interception.

### Database Isolation
All tests execute against an isolated in-memory SQLite database (`sqlite:///:memory:`) using `StaticPool`. Tables are freshly created and dropped before and after each test via pytest fixtures, guaranteeing zero state leakage and ensuring tests never modify the development database `taskflow.db`.

---

## Coverage

Generate terminal coverage report:
```bash
pytest --cov=app --cov-report=term-missing
```

Generate HTML coverage report:
```bash
pytest --cov=app --cov-report=html
```

The detailed report will be generated inside the `htmlcov/` directory. Open `htmlcov/index.html` in your web browser:
```bash
# Windows
start htmlcov/index.html

# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

TaskFlow achieves **100% test coverage** across all core application modules:

```text
Name                           Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------------
app\__init__.py                    1      0      0      0   100%
app\core\__init__.py               0      0      0      0   100%
app\core\config.py                 9      0      0      0   100%
app\core\exceptions.py             4      0      0      0   100%
app\database\__init__.py           3      0      0      0   100%
app\database\database.py          14      0      0      0   100%
app\database\models.py            18      0      0      0   100%
app\main.py                       33      0      4      0   100%
app\routers\__init__.py            3      0      0      0   100%
app\routers\health.py              6      0      0      0   100%
app\routers\tasks.py              26      0      0      0   100%
app\schemas\__init__.py            2      0      0      0   100%
app\schemas\task.py               34      0      0      0   100%
app\services\__init__.py           2      0      0      0   100%
app\services\task_service.py      48      0      8      0   100%
--------------------------------------------------------------------------
TOTAL                            203      0     12      0   100%
```

---

## CI/CD

Continuous Integration is automated via GitHub Actions in [`.github/workflows/tests.yml`](.github/workflows/tests.yml).

Every push and pull request to `main` triggers the workflow across multiple Python versions (3.11 and 3.12).

CI verifies that:
- Dependencies install cleanly without conflicts
- The test suite executes and passes 100%
- Coverage requirements (minimum 85%) are enforced
- Regressions are automatically detected before merging

---

## Future Improvements

While TaskFlow intentionally focuses on core REST reliability and clean architecture, future iterations could include:
- **Authentication & Authorization**: JWT-based OAuth2 user accounts and task ownership.
- **Search & Text Indexing**: Full-text search for task title and description.
- **Background Tasks**: Email reminders or webhooks via Celery / Redis / ARQ.
- **Database Migrations**: Alembic integration for managing evolving schema migrations.
- **PostgreSQL Support**: Connection pooling configuration for enterprise RDBMS deployments.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
