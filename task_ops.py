from __future__ import annotations

from typing import Optional, Callable, Annotated, Literal
from datetime import datetime, timezone

from task_store import Store, TaskRecord
from models import TASK_STATUS, TASK_ID

queries: dict[str, dict] = {}

def add_query(func: Callable) -> Callable:
    pass


# @add_query
def add_task(
    store: Store, 
    description: Annotated[str, "Description of the task"]
) -> None:
    """Add a new task and return its integer ID."""
    id: TASK_ID = str(store["nextId"])
    now: str = datetime.now(timezone.utc).isoformat(timespec="seconds")
    status: TASK_STATUS = "todo"
    record: TaskRecord = {
        "description": description,
        "status": status,
        "createdAt": now,
        "updatedAt": now,
    }
    store["tasks"][id] = record
    store["order"].append(id)
    store["nextId"] += 1

    # today = datetime.now(timezone.utc).date().isoformat()
    # list_tasks(store, date=today)

    print("Task added successfully ({description})")


@add_query
def update_task(
    store: Store, 
    task_id: Annotated[str, "ID of the task to update"],
    description: Annotated[Optional[str], 
                           "Updated task description", 
                           "--description", 
                           "-d"
                           ] = None,
    status: Annotated[Optional[str], 
                      "Updated task status", 
                      "--status", 
                      "-s"
                      ] = None,
) -> None:
    """Update a task's description and/or status."""
    raise NotImplementedError


@add_query
def delete_task(
    store: Store, 
    task_id: Annotated[str, "ID of the task to delete"],
) -> None:
    """Delete a task by ID."""
    raise NotImplementedError


@add_query
def mark_in_progress(
    store: Store, 
    task_id: Annotated[str, "ID of the task to mark 'in-progress'"],
) -> None:
    """Set task status to in-progress and update timestamp."""
    raise NotImplementedError


@add_query
def mark_done(
    store: Store,
    task_id: Annotated[str, "ID of the task to mark 'done'"],
) -> None:
    """Set task status to done and update timestamp."""
    raise NotImplementedError


@add_query
def list_tasks(
    store: Store,
    status: Annotated[Literal[TASK_STATUS, "all"], 
                      "List all the tasks or filter by status ('todo', 'in-progress', 'done').",
                      "--status",
                      "-s"
                      ] = "all",
    date: Annotated[Optional[str],
                    "Filter tasks by date (YYYY-MM-DD). Use <, >, = operators (e.g. '<2026-01-01' means on or before)",
                    "--date",
                    "-d"
                    ] = None,
) -> None:
    """Return tasks (optionally filtered by status) in display order."""
    raise NotImplementedError

