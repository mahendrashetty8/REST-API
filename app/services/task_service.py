"""Business logic service layer for task operations."""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import TaskNotFoundError
from app.database.models import Task
from app.schemas.task import Priority, TaskCreate, TaskStatus, TaskUpdate


class TaskService:
    """Service encapsulating all task business and database operations."""

    def create_task(self, db: Session, task_in: TaskCreate) -> Task:
        """Create and persist a new task."""
        task = Task(
            title=task_in.title,
            description=task_in.description,
            priority=task_in.priority,
            due_date=task_in.due_date,
            status=TaskStatus.PENDING,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def get_task_by_id(self, db: Session, task_id: int) -> Task:
        """Retrieve a task by ID, or raise TaskNotFoundError if missing."""
        task = db.get(Task, task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def get_tasks(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 10,
        status: Optional[TaskStatus] = None,
        priority: Optional[Priority] = None,
    ) -> List[Task]:
        """Retrieve a paginated and filtered list of tasks."""
        stmt = select(Task)
        if status is not None:
            stmt = stmt.where(Task.status == status)
        if priority is not None:
            stmt = stmt.where(Task.priority == priority)
        stmt = stmt.order_by(Task.id.asc()).offset(skip).limit(limit)
        return list(db.scalars(stmt).all())

    def update_task(self, db: Session, task_id: int, task_in: TaskUpdate) -> Task:
        """Partially update an existing task."""
        task = self.get_task_by_id(db, task_id)
        update_data = task_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(task, field, value)

        task.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(task)
        return task

    def complete_task(self, db: Session, task_id: int) -> Task:
        """Mark a task as completed. Idempotent on already completed tasks."""
        task = self.get_task_by_id(db, task_id)
        task.status = TaskStatus.COMPLETED
        task.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(task)
        return task

    def delete_task(self, db: Session, task_id: int) -> None:
        """Delete an existing task by ID, or raise TaskNotFoundError if missing."""
        task = self.get_task_by_id(db, task_id)
        db.delete(task)
        db.commit()


task_service = TaskService()
