from __future__ import annotations

from datetime import datetime, timezone
from task_store import Store, TaskRecord
from models import TASK_STATUS, TASK_ID
from typing import (
    Annotated,
    Callable,
    Literal,
    Optional,
    TypedDict,
    Union,
    get_args,
    get_origin,
)

VALID_STATUSES = get_args(TASK_STATUS)
queries: dict[str, dict] = {}

def add_query(func: Callable) -> Callable:
    pass

def _get_date_time() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

# @add_query
def add_task(
    store: Store, 
    description: Annotated[str, "Description of the task"]
) -> None:
    """Add a new task and return its integer ID."""
    id: TASK_ID = str(store["nextId"])
    now: str = _get_date_time()
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

    print("Task added successfully")


# @add_query
def update_task(
    store: Store, 
    task_id: Annotated[str, "ID of the task to update"],
    description: Annotated[Optional[str], 
                           "Updated task description", 
                           "--description", 
                           "-d"
                           ] = None,
    status: Annotated[Optional[TASK_STATUS], 
                      "Updated task status", 
                      "--status", 
                      "-s"
                      ] = None,
) -> None:
    """Update a task's description and/or status."""
    if task_id not in store["tasks"]:
        raise KeyError(f"Task with ID {task_id} does not exist.")
    record = store["tasks"][task_id]
    if description is not None:
        record["description"] = description
    if status is not None:
        if status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. Valid statuses: {', '.join(VALID_STATUSES)}"
            )
        record["status"] = status

    record["updatedAt"] = _get_date_time()
    print("Task updated successfully")


# @add_query
def delete_task(
    store: Store, 
    task_id: Annotated[str, "ID of the task to delete"],
) -> None:
    """Delete a task by ID."""
    raise NotImplementedError


# @add_query
def mark_in_progress(
    store: Store, 
    task_id: Annotated[str, "ID of the task to mark 'in-progress'"],
) -> None:
    """Set task status to in-progress and update timestamp."""
    raise NotImplementedError


# @add_query
def mark_done(
    store: Store,
    task_id: Annotated[str, "ID of the task to mark 'done'"],
) -> None:
    """Set task status to done and update timestamp."""
    raise NotImplementedError


# @add_query
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

