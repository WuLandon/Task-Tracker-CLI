import operator
from datetime import datetime, timezone, date as date_type
from tabulate import tabulate
from inspect import signature
from task_store import Store, TaskRecord, VALID_STATUSES
from models import TASK_STATUS_TYPES, TASK_ID
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

# Used in list_tasks()
TASK_STATUS_FILTER = Literal["done", "in-progress", "todo", "all"]

queries: dict[str, dict] = {}


def add_query(func: Callable) -> Callable:
    """Decorator to add valid queries to the queries dictionary."""
    name = func.__name__.removesuffix("_task").replace("_", "-")
    queries[name] = {"command": func, "help": func.__doc__, "args": []}
    for p in signature(func).parameters.values():
        if p.name in ("store", "store_tasks"):
            continue
        t, *metadata = get_args(p.annotation)
        if get_origin(t) is Union:
            t = get_args(t)[0]
        queries[name]["args"].append(
            {
                "name": metadata[1:] if len(metadata) > 1 else [p.name],
                "help": metadata[0],
                "choices": get_args(t) if get_origin(t) is Literal else None,
                "default": p.default if p.default is not p.empty else None,
            }
        )
    return func


@add_query
def add_task(
    store: Store, description: Annotated[str, "Description of the task"]
) -> None:
    """Add a new task."""
    id: TASK_ID = str(store["nextId"])
    now: str = _get_date_time()
    status: TASK_STATUS_TYPES = "todo"
    record: TaskRecord = {
        "description": description,
        "status": status,
        "createdAt": now,
        "updatedAt": now,
    }
    store["tasks"][id] = record
    store["order"].append(id)
    store["nextId"] += 1

    list_tasks({id: store["tasks"][id]})


@add_query
def update_task(
    store: Store,
    task_id: Annotated[str, "ID of the task to update"],
    description: Annotated[
        Optional[str], "Updated task description", "--description", "-d"
    ] = None,
    status: Annotated[
        Optional[TASK_STATUS_TYPES], "Updated task status", "--status", "-s"
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

    list_tasks({task_id: store["tasks"][task_id]})


# @add_query
def delete_task(
    store: Store,
    task_id: Annotated[str, "ID of the task to delete"],
) -> None:
    """Delete a task."""
    if task_id not in store["tasks"]:
        raise KeyError(f"Task with ID {task_id} does not exist.")
    if task_id in store["order"]:
        store["order"].remove(task_id)
    del store["tasks"][task_id]

    print("Task deleted successfully")


# @add_query
def mark_in_progress(
    store: Store,
    task_id: Annotated[str, "ID of the task to mark 'in-progress'"],
) -> None:
    """Set task status to 'in-progress'."""
    update_task(store, task_id, status="in-progress")


# @add_query
def mark_done(
    store: Store,
    task_id: Annotated[str, "ID of the task to mark 'done'"],
) -> None:
    """Set task status to 'done'."""
    update_task(store, task_id, status="done")


# @add_query
def list_tasks(
    store_tasks: dict[TASK_ID, TaskRecord],
    status: Annotated[
        TASK_STATUS_FILTER,
        "List all the tasks or filter by status ('todo', 'in-progress', 'done').",
        "--status",
        "-s",
    ] = "all",
    date: Annotated[
        Optional[str],
        "Filter tasks by date. Supports YYYY, YYYY-MM, or YYYY-MM-DD, "
        "optionally prefixed with <, <=, =, >=, or > (e.g. '2026', '>=2026-06').",
        "--date",
        "-d",
    ] = None,
) -> None:
    """List tasks filtered by status and/or date."""
    if status not in {*VALID_STATUSES, "all"}:
        raise ValueError(
            f"Invalid status '{status}'. Valid statuses: {', '.join(VALID_STATUSES)}."
        )
    filter_date = get_date_filter(date)
    data_table = (
        {
            "ID": id,
            "Description": task["description"],
            "Created At": datetime.fromisoformat(task["createdAt"]).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "Updated At": datetime.fromisoformat(task["updatedAt"]).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }
        for id, task in store_tasks.items()
        if (status == "all" or task["status"] == status)
        and filter_date(task["createdAt"])
    )

    print(
        tabulate(data_table, tablefmt="rounded_grid", headers="keys") or "No Tasks Yet!"
    )


def _get_date_time() -> str:
    # (e.g. "2026-01-31T14:30:45+00:00")
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_date_filter(date_filter: Optional[str] = None) -> Callable[[str], bool]:
    """
    Build a predicate that checks whether an ISO datetime string (e.g. '2026-01-31T12:00:00')
    satisfies a date filter.

    Supported filters:
      - Operators: <=, >=, =, <, > (default '=')
      - Date formats: YYYY, YYYY-MM, YYYY-MM-DD

    Raises ValueError if the filter is invalid.
    """
    # No filter → accept all dates
    if date_filter is None or date_filter.strip() == "":
        return lambda _: True

    # Extract optional comparison operator from the filter string
    s = date_filter.strip()
    op_tokens = ("<=", ">=", "=", "<", ">")
    op = next((tok for tok in op_tokens if s.startswith(tok)), None)

    # Split operator and date (default to "=" if no operator provided)
    if op is None:
        op = "="
        date_part = s
    else:
        date_part = s[len(op) :].strip()
    if not date_part:
        raise ValueError(f"Invalid date filter: {date_filter!r}")

    # Parse date with increasing coarseness (day → month → year)
    parsed_date: Optional[date_type] = None
    chosen_fmt: Optional[str] = None
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            parsed_date = datetime.strptime(date_part, fmt).date()
            chosen_fmt = fmt
            break
        except ValueError:
            continue
    if parsed_date is None or chosen_fmt is None:
        raise ValueError(
            f"Invalid date format: {date_part!r}. Expected YYYY-MM-DD, YYYY-MM, or YYYY."
        )

    # Predicate: compare stored ISO date against parsed filter date
    comparators = {
        "<": operator.lt,
        "<=": operator.le,
        ">": operator.gt,
        ">=": operator.ge,
        "=": operator.eq,
    }
    cmp = comparators[op]

    def predicate(stored_date_iso: str) -> bool:
        date_prefix = stored_date_iso[: len(date_part)]
        try:
            candidate_date = datetime.strptime(date_prefix, chosen_fmt).date()
        except ValueError:
            raise ValueError(f"Invalid stored date value: {stored_date_iso!r}")
        return cmp(candidate_date, parsed_date)

    return predicate
