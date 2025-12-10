"""Shared pytest fixtures for all tests"""
from datetime import datetime, timedelta
from typing import List
import pytest
from src.core.models import Task, Priority, Recurrence


@pytest.fixture
def sample_task() -> Task:
    """Create a simple sample task for testing"""
    return Task(
        title="Buy groceries",
        description="Get milk, eggs, and bread",
        priority=Priority.MEDIUM,
        tags=["personal", "shopping"],
    )


@pytest.fixture
def sample_tasks() -> List[Task]:
    """Create a list of sample tasks for testing"""
    return [
        Task(
            title="Complete project proposal",
            description="Finish the Q4 proposal",
            priority=Priority.HIGH,
            tags=["work", "urgent"],
            due_date=datetime.now() + timedelta(days=2),
        ),
        Task(
            title="Buy groceries",
            description="Get milk, eggs, and bread",
            priority=Priority.MEDIUM,
            tags=["personal", "shopping"],
            due_date=datetime.now() + timedelta(days=1),
        ),
        Task(
            title="Read book chapter",
            description="Chapter 5 of Python book",
            priority=Priority.LOW,
            tags=["personal", "learning"],
        ),
    ]


@pytest.fixture
def completed_task() -> Task:
    """Create a completed task for testing"""
    task = Task(
        title="Completed task",
        description="This task is done",
        completed=True,
    )
    return task


@pytest.fixture
def overdue_task() -> Task:
    """Create an overdue task for testing"""
    return Task(
        title="Overdue task",
        description="This task is overdue",
        priority=Priority.HIGH,
        due_date=datetime.now() - timedelta(days=1),
    )


@pytest.fixture
def due_today_task() -> Task:
    """Create a task due today for testing"""
    return Task(
        title="Task due today",
        description="Due today",
        priority=Priority.HIGH,
        due_date=datetime.now(),
    )


@pytest.fixture
def recurring_task() -> Task:
    """Create a recurring task for testing"""
    return Task(
        title="Daily standup",
        description="Team standup meeting",
        priority=Priority.MEDIUM,
        recurrence=Recurrence.DAILY,
        due_date=datetime.now() + timedelta(days=1, hours=9),
    )
