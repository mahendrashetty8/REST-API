"""Custom application exceptions."""


class TaskNotFoundError(Exception):
    """Exception raised when a requested task does not exist."""

    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with id {task_id} not found")
