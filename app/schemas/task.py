"""Pydantic schemas and enums for task management and health checks."""

from datetime import date, datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class Priority(str, Enum):
    """Priority levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, Enum):
    """Lifecycle status of tasks."""
    PENDING = "pending"
    COMPLETED = "completed"


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="The title of the task (3-100 characters)",
        examples=["Learn FastAPI"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional detailed description of the task (max 500 characters)",
        examples=["Build a reliable REST API with FastAPI and SQLAlchemy"],
    )
    priority: Priority = Field(
        default=Priority.MEDIUM,
        description="Priority level: low, medium, or high",
        examples=[Priority.HIGH],
    )
    due_date: Optional[date] = Field(
        default=None,
        description="Optional task deadline (YYYY-MM-DD)",
        examples=["2026-09-30"],
    )


class TaskUpdate(BaseModel):
    """Schema for partially updating an existing task."""
    title: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=100,
        description="Updated task title (3-100 characters)",
        examples=["Learn Advanced FastAPI"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Updated task description (max 500 characters)",
        examples=["Updated task description details"],
    )
    priority: Optional[Priority] = Field(
        default=None,
        description="Updated priority level: low, medium, or high",
        examples=[Priority.HIGH],
    )
    due_date: Optional[date] = Field(
        default=None,
        description="Updated deadline (YYYY-MM-DD)",
        examples=["2026-10-31"],
    )
    status: Optional[TaskStatus] = Field(
        default=None,
        description="Updated task status: pending or completed",
        examples=[TaskStatus.COMPLETED],
    )


class TaskResponse(BaseModel):
    """Public task representation schema."""
    id: int
    title: str
    description: Optional[str] = None
    priority: Priority
    status: TaskStatus
    due_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    """Schema for API health status."""
    status: str = "ok"
