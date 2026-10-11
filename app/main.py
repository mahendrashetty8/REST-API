"""Main FastAPI application entrypoint for TaskFlow API."""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse

from app.core.config import settings
from app.core.exceptions import TaskNotFoundError
from app.database.database import Base, engine
from app.routers.health import router as health_router
from app.routers.tasks import router as tasks_router

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
INDEX_HTML = os.path.join(STATIC_DIR, "index.html")

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup and shutdown events."""
    # Create database tables if they do not exist
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "Health",
            "description": "API health and readiness checks",
        },
        {
            "name": "Tasks",
            "description": "Task management operations (CRUD and lifecycle)",
        },
    ],
)


@app.exception_handler(TaskNotFoundError)
async def task_not_found_exception_handler(
    request: Request,
    exc: TaskNotFoundError,
) -> JSONResponse:
    """Handle missing task exceptions with a consistent 404 response."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle request validation errors, transforming malformed JSON into 400 Bad Request."""
    for error in exc.errors():
        if error.get("type") == "json_invalid":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Malformed JSON request body"},
            )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(exc.errors())},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Catch-all handler to prevent Python tracebacks or database errors from leaking."""
    logger.exception("Unhandled server exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.get("/", response_class=FileResponse, include_in_schema=False)
async def serve_dashboard() -> FileResponse:
    """Serve the frontend web dashboard."""
    return FileResponse(INDEX_HTML)


# Include modular routers
app.include_router(health_router)
app.include_router(tasks_router)
