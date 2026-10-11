"""Task management router."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.task import Priority, TaskCreate, TaskResponse, TaskStatus, TaskUpdate
from app.services.task_service import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task with title, optional description, priority, and optional due date.",
)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
) -> TaskResponse:
    """Create a task in the database."""
    return task_service.create_task(db=db, task_in=task_in)


@router.get(
    "",
    response_model=List[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List all tasks",
    description="Retrieve a paginated list of tasks with optional filtering by status and priority.",
)
def get_tasks(
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip for pagination (skip >= 0)",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of records to return (1 <= limit <= 100)",
    ),
    status_filter: Optional[TaskStatus] = Query(
        default=None,
        alias="status",
        description="Filter tasks by status (pending or completed)",
    ),
    priority_filter: Optional[Priority] = Query(
        default=None,
        alias="priority",
        description="Filter tasks by priority (low, medium, high)",
    ),
    db: Session = Depends(get_db),
) -> List[TaskResponse]:
    """Retrieve all tasks matching query parameters."""
    return task_service.get_tasks(
        db=db,
        skip=skip,
        limit=limit,
        status=status_filter,
        priority=priority_filter,
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a task by ID",
    description="Retrieve full details for a single task given its unique integer ID.",
)
def get_task(
    task_id: int = Path(..., description="Unique integer ID of the task"),
    db: Session = Depends(get_db),
) -> TaskResponse:
    """Retrieve a single task or return 404 if not found."""
    return task_service.get_task_by_id(db=db, task_id=task_id)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a task",
    description="Partially update an existing task. Only supplied fields will be modified.",
)
def update_task(
    task_in: TaskUpdate,
    task_id: int = Path(..., description="Unique integer ID of the task to update"),
    db: Session = Depends(get_db),
) -> TaskResponse:
    """Partially update task fields."""
    return task_service.update_task(db=db, task_id=task_id, task_in=task_in)


@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark task as completed",
    description="Mark a task's status as completed. Safe and idempotent on already completed tasks.",
)
def complete_task(
    task_id: int = Path(..., description="Unique integer ID of the task to mark as completed"),
    db: Session = Depends(get_db),
) -> TaskResponse:
    """Mark a task as completed."""
    return task_service.complete_task(db=db, task_id=task_id)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Delete a task by ID. Returns 204 No Content on success or 404 if not found.",
)
def delete_task(
    task_id: int = Path(..., description="Unique integer ID of the task to delete"),
    db: Session = Depends(get_db),
) -> Response:
    """Delete a task from the database."""
    task_service.delete_task(db=db, task_id=task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
