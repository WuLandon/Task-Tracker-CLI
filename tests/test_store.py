import json
import pytest
from pathlib import Path
from store import load_tasks, save_tasks


# load_tasks tests
def test_load_tasks_creates_store_when_missing(tmp_path: Path):
    path = tmp_path / "tasks.json"

    store = load_tasks(path)

    assert store == {"nextId": 1, "order": [], "tasks": {}}
    assert path.exists()


def test_load_tasks_rejects_invalid_json(tmp_path: Path):
    path = tmp_path / "tasks.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(SystemExit) as excinfo:
        load_tasks(path)
    assert excinfo.value.code == 1


def test_load_tasks_rejects_invalid_shape(tmp_path: Path):
    path = tmp_path / "tasks.json"
    path.write_text(
        json.dumps({"nextId": 0, "order": [], "tasks": {}}), encoding="utf-8"
    )

    with pytest.raises(SystemExit) as excinfo:
        load_tasks(path)
    assert excinfo.value.code == 1


# save_tasks tests
def test_save_tasks_writes_json(tmp_path: Path):
    path = tmp_path / "tasks.json"
    store = {
        "nextId": 2,
        "order": ["1"],
        "tasks": {
            "1": {
                "description": "Write tests",
                "status": "todo",
                "createdAt": "2026-02-01T08:00:00+00:00",
                "updatedAt": "2026-02-01T08:00:00+00:00",
            }
        },
    }

    save_tasks(store, path)

    data = json.loads(path.read_text(encoding="utf-8"))
    assert data == store
