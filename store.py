import json
import sys
import tempfile
from pathlib import Path
from typing import Any
from models import Store, TaskRecord

DEFAULT_PATH = Path("tasks.json")
VALID_STATUSES = ("done", "in-progress", "todo")


def load_tasks(path: Path = DEFAULT_PATH) -> Store:
    """Load the task store from JSON, creating a new store if missing."""
    if not path.exists():
        store: Store = {"nextId": 1, "order": [], "tasks": {}}
        save_tasks(store, path)
        return store

    try:
        with path.open("r", encoding="utf-8") as file:
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


def save_tasks(store: Store, path: Path = DEFAULT_PATH) -> None:
    """Atomically write the im-memory task store to JSON."""
    directory = path.parent
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", delete=False, dir=str(directory)
        ) as tmp_file:
            json.dump(store, tmp_file, indent=2, ensure_ascii=False)
            tmp_file.write("\n")
            temp_name = tmp_file.name
        Path(temp_name).replace(path)
    except OSError:
        print(f"Error: unable to write tasks file at {path}.", file=sys.stderr)
        sys.exit(2)


def _invalid_json_error(path: Path) -> None:
    print(
        f"Error: Tasks file is invalid JSON. Fix or delete {path} and try again.",
        file=sys.stderr,
    )
    sys.exit(1)


def _parse_task_record(value: Any, *, path: Path) -> TaskRecord:
    """Validate and normalize a single task record from JSON."""
    if not isinstance(value, dict):
        _invalid_json_error(path)

    description = value.get("description")
    status = value.get("status")
    createdAt = value.get("createdAt")
    updatedAt = value.get("updatedAt")

    if not (
        isinstance(description, str)
        and status in VALID_STATUSES
        and isinstance(createdAt, str)
        and isinstance(updatedAt, str)
    ):
        _invalid_json_error(path)

    task_record: TaskRecord = {
        "description": description,
        "status": status,
        "createdAt": createdAt,
        "updatedAt": updatedAt,
    }
    return task_record


def _parse_store(data: Any, *, path: Path) -> Store:
    if not isinstance(data, dict):
        _invalid_json_error(path)

    next_id = data.get("nextId")
    order = data.get("order")
    tasks = data.get("tasks")

    # Validate fields
    if not (
        isinstance(next_id, int)
        and next_id >= 1
        and isinstance(order, list)
        and all(isinstance(x, str) for x in order)
        and isinstance(tasks, dict)
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
    store: Store = {"nextId": next_id, "order": order, "tasks": parsed_tasks}
    return store
