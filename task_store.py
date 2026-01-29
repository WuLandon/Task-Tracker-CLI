import json
import os
import sys
import tempfile
from typing import Any, Literal, TypedDict

DEFAULT_PATH = "tasks.json"
TASK_STATUSES = ("todo", "in-progress", "done")

TaskStatus = Literal["done", "in-progress", "todo"]
TaskId = str

class TaskRecord(TypedDict):
    description: str
    status: TaskStatus
    createdAt: str
    updatedAt: str


class Store(TypedDict):
    nextId: int
    order: list[TaskId]
    tasks: dict[TaskId, TaskRecord]


def _invalid_json_error(path: str) -> None:
    print(
        f"Error: tasks file is invalid JSON. Fix or delete {path} and try again.",
        file=sys.stderr,
    )
    sys.exit(1)


def _parse_task_record(value: Any, *, path: str) -> TaskRecord:
    if not isinstance(value, dict):
        _invalid_json_error(path)

    description = value.get("description")
    status = value.get("status")
    createdAt = value.get("createdAt")
    updatedAt = value.get("updatedAt")

    if not (
        isinstance(description, str) and
        status in TASK_STATUSES and
        isinstance(createdAt, str) and
        isinstance(updatedAt, str)
    ):
        _invalid_json_error(path)

    task_record: TaskRecord = {
        "description": description,
        "status": status,
        "createdAt": createdAt,
        "updatedAt": updatedAt,
    }
    return task_record


def _parse_store(data: Any, *, path: str) -> Store:
    if not isinstance(data, dict):
        _invalid_json_error(path)

    next_id = data.get("nextId")
    order = data.get("order")
    tasks = data.get("tasks")

    # Validate fields
    if not (
        isinstance(next_id, int) and next_id >= 1 and
        isinstance(order, list) and
        all(isinstance(x, str) for x in order) and
        isinstance(tasks, dict)
    ):
        _invalid_json_error(path)

    # Validate tasks
    parsed_tasks: dict[str, TaskRecord] = {}
    for task_id, record in tasks.items():
        if not isinstance(task_id, str) or not task_id.isdigit():
            _invalid_json_error(path)
        parsed_tasks[task_id] = _parse_task_record(record, path=path)

    # Invariants: order should match tasks exactly (no missing, no extras, no duplicates)
    if len(order) != len(set(order)):
        _invalid_json_error(path)
    if set(order) != set(parsed_tasks.keys()):
        _invalid_json_error(path)

    # Create Store
    store: Store = {
        "nextId": next_id,
        "order": order,
        "tasks": parsed_tasks
    }
    return store


def load_tasks(path: str = DEFAULT_PATH) -> Store:
    if not os.path.exists(path):
        store: Store = {"nextId": 1, "order": [], "tasks": {}}
        save_tasks(store, path)
        return store
    
    try:
        with open(path, "r", encoding="utf-8") as file:
            data: Any = json.load(file)
    except json.JSONDecodeError:
        _invalid_json_error(path)
    except OSError:
        print(f"Error: unable to read tasks file at {path}.", file=sys.stderr)
        sys.exit(2)
    
    if not isinstance(data, dict):
        _invalid_json_error(path)

    store: Store = _parse_store(data, path=path)
    return store


def save_tasks(store: Store, path: str = DEFAULT_PATH) -> None:
    directory = os.path.dirname(path) or "."
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", delete=False, dir=directory
        ) as tmp_file:
            json.dump(store, tmp_file, indent=2, ensure_ascii=False)
            tmp_file.write("\n")
            temp_name = tmp_file.name
        os.replace(temp_name, path)
    except OSError:
        print(f"Error: unable to write tasks file at {path}.", file=sys.stderr)
        sys.exit(2)
