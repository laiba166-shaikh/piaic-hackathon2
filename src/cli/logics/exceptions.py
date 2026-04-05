"""Custom exceptions for the Todo application"""


class TaskNotFoundError(Exception):
    """Raised when a task with the specified ID does not exist"""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found")


class ValidationError(Exception):
    """Raised when task data validation fails"""

    pass


class InvalidIDError(Exception):
    """Raised when an invalid task ID is provided"""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"Invalid task ID: {task_id}")
