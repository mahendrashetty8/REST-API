"""SQLAlchemy models for TaskFlow API."""

from datetime import date, datetime, timezone
from typing import Optional
from sqlalchemy import Date, DateTime, Enum as SQLEnum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.schemas.task import Priority, TaskStatus


def get_utc_now() -> datetime:
    """Helper to return current UTC datetime."""
    return datetime.now(timezone.utc)


class Task(Base):
    """SQLAlchemy model representing a task."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default=None,
    )
    priority: Mapped[Priority] = mapped_column(
        SQLEnum(Priority, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=Priority.MEDIUM,
    )
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=TaskStatus.PENDING,
    )
    due_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        default=None,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=get_utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=get_utc_now,
        onupdate=get_utc_now,
    )
