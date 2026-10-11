"""Routers package initialization."""

from app.routers.health import router as health_router
from app.routers.tasks import router as tasks_router

__all__ = ["health_router", "tasks_router"]
