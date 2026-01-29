from __future__ import annotations

from typing import Optional

from task_store import Store, TaskRecord, TaskStatus


def add_task(store: Store, description: str, now: str) -> int:
    """Add a new task and return its integer ID."""
    raise NotImplementedError


def update_task(store: Store, task_id: int, description: str, now: str) -> None:
    """Update a task's description and updated timestamp."""
    raise NotImplementedError


def delete_task(store: Store, task_id: int) -> None:
    """Delete a task by ID."""
    raise NotImplementedError


def mark_in_progress(store: Store, task_id: int, now: str) -> None:
    """Set task status to in-progress and update timestamp."""
    raise NotImplementedError


def mark_done(store: Store, task_id: int, now: str) -> None:
    """Set task status to done and update timestamp."""
    raise NotImplementedError


def list_tasks(
    store: Store, status: Optional[TaskStatus] = None
) -> list[tuple[int, TaskRecord]]:
    """Return tasks (optionally filtered by status) in display order."""
    raise NotImplementedError

