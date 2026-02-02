import datetime
import pytest
from commands import (
    add_task,
    delete_task,
    get_date_filter,
    list_tasks,
    mark_done,
    mark_in_progress,
    queries,
    update_task,
)


# add_task stores a new task and increments IDs without breaking order.
def test_add_task():
    store = {"nextId": 1, "order": [], "tasks": {}}

    add_task(store, "Write tests")

    assert store["nextId"] == 2
    assert store["order"] == ["1"]
    assert "1" in store["tasks"]
    record_1 = store["tasks"]["1"]
    assert record_1["description"] == "Write tests"
    assert record_1["status"] == "todo"
    assert record_1["createdAt"] == record_1["updatedAt"]
    datetime.datetime.fromisoformat(record_1["createdAt"])

    add_task(store, "Meet up with friends")
    add_task(store, "Buy groceries")

    assert store["nextId"] == 4
    assert len(store["order"]) == 3
    assert len(store["tasks"]) == 3


# update_task changes description/status and refreshes updatedAt.
def test_update_task():
    store = {"nextId": 1, "order": [], "tasks": {}}
    add_task(store, "Original description")

    old_timestamp = "2000-01-01T00:00:00+00:00"
    store["tasks"]["1"]["createdAt"] = old_timestamp
    store["tasks"]["1"]["updatedAt"] = old_timestamp

    update_task(store, "1", description="Updated description")

    record = store["tasks"]["1"]
    assert record["description"] == "Updated description"
    assert record["status"] == "todo"
    assert record["createdAt"] == old_timestamp
    assert record["updatedAt"] != old_timestamp
    datetime.datetime.fromisoformat(record["updatedAt"])

    update_task(store, "1", status="done")

    record = store["tasks"]["1"]
    assert record["description"] == "Updated description"
    assert record["status"] == "done"
    datetime.datetime.fromisoformat(record["updatedAt"])


# delete_task removes the task from both tasks and order.
def test_delete_task():
    store = {"nextId": 1, "order": [], "tasks": {}}
    add_task(store, "First task")
    add_task(store, "Second task")

    delete_task(store, "1")

    assert "1" not in store["tasks"]
    assert store["order"] == ["2"]
    assert "2" in store["tasks"]


# mark_in_progress sets status and refreshes updatedAt.
def test_mark_in_progress():
    store = {"nextId": 1, "order": [], "tasks": {}}
    add_task(store, "Status change")

    old_timestamp = "2000-01-01T00:00:00+00:00"
    store["tasks"]["1"]["createdAt"] = old_timestamp
    store["tasks"]["1"]["updatedAt"] = old_timestamp

    mark_in_progress(store, "1")

    record = store["tasks"]["1"]
    assert record["status"] == "in-progress"
    assert record["createdAt"] == old_timestamp
    assert record["updatedAt"] != old_timestamp
    datetime.datetime.fromisoformat(record["updatedAt"])


# mark_done sets status to done and refreshes updatedAt.
def test_mark_done():
    store = {"nextId": 1, "order": [], "tasks": {}}
    add_task(store, "Finish it")

    old_timestamp = "2000-01-01T00:00:00+00:00"
    store["tasks"]["1"]["createdAt"] = old_timestamp
    store["tasks"]["1"]["updatedAt"] = old_timestamp

    mark_done(store, "1")

    record = store["tasks"]["1"]
    assert record["status"] == "done"
    assert record["createdAt"] == old_timestamp
    assert record["updatedAt"] != old_timestamp
    datetime.datetime.fromisoformat(record["updatedAt"])


# list_tasks prints all tasks and supports status/date filtering.
def test_list_tasks(capsys):
    store = {"nextId": 1, "order": [], "tasks": {}}

    # Empty store should print fallback message
    list_tasks(store["tasks"])
    output = capsys.readouterr().out
    assert "No Tasks Yet!" in output

    # Invalid filters should raise errors
    with pytest.raises(ValueError):
        list_tasks(store["tasks"], status="blocked")
    with pytest.raises(ValueError):
        list_tasks(store["tasks"], date="2026-13-01")

    # Add sample tasks
    add_task(store, "Alpha")
    add_task(store, "Beta")
    add_task(store, "Gamma")
    capsys.readouterr()  # Clear output from add_task

    # Manually set task metadata for deterministic filtering
    store["tasks"]["1"]["status"] = "todo"
    store["tasks"]["1"]["createdAt"] = "2026-02-01T08:00:00+00:00"
    store["tasks"]["1"]["updatedAt"] = "2026-02-01T08:00:00+00:00"
    store["tasks"]["2"]["status"] = "in-progress"
    store["tasks"]["2"]["createdAt"] = "2026-01-15T09:00:00+00:00"
    store["tasks"]["2"]["updatedAt"] = "2026-01-15T09:00:00+00:00"
    store["tasks"]["3"]["status"] = "done"
    store["tasks"]["3"]["createdAt"] = "2025-12-31T10:00:00+00:00"
    store["tasks"]["3"]["updatedAt"] = "2025-12-31T10:00:00+00:00"

    # Listing without filters should include all tasks
    list_tasks(store["tasks"])
    output = capsys.readouterr().out
    assert "Alpha" in output
    assert "Beta" in output
    assert "Gamma" in output

    # Status filter should only show matching tasks
    list_tasks(store["tasks"], status="done")
    output = capsys.readouterr().out
    assert "Gamma" in output
    assert "Alpha" not in output
    assert "Beta" not in output

    # Date filter should include tasks created on or after cutoff
    list_tasks(store["tasks"], date=">=2026-02-01")
    output = capsys.readouterr().out
    assert "Alpha" in output
    assert "Beta" not in output
    assert "Gamma" not in output

    # Combined status + date filter
    list_tasks(store["tasks"], status="in-progress", date="<=2026-01")
    output = capsys.readouterr().out
    assert "Beta" in output
    assert "Alpha" not in output
    assert "Gamma" not in output


# add_query registers decorated functions with parsed metadata.
def test_add_query():
    assert "update" in queries
    update_entry = queries["update"]
    assert update_entry["command"] is update_task
    assert update_entry["help"] == update_task.__doc__
    assert len(update_entry["args"]) == 3

    update_id = update_entry["args"][0]
    assert update_id["name"] == ["task_id"]
    assert update_id["help"] == "ID of the task to update"
    assert update_id["choices"] is None
    assert update_id["default"] is None

    update_description = update_entry["args"][1]
    assert update_description["name"] == ["--description", "-d"]
    assert update_description["help"] == "Updated task description"
    assert update_description["choices"] is None
    assert update_description["default"] is None

    update_status = update_entry["args"][2]
    assert update_status["name"] == ["--status", "-s"]
    assert update_status["help"] == "Updated task status"
    assert set(update_status["choices"]) == {"todo", "in-progress", "done"}
    assert update_status["default"] is None


# get_date_filter applies operators across YYYY, YYYY-MM, YYYY-MM-DD formats.
def test_get_date_filter():
    # YYYY-MM-DD with >= operator (inclusive lower bound).
    predicate = get_date_filter(">=2026-02-01")
    assert predicate("2026-02-01T00:00:00+00:00") is True
    assert predicate("2026-01-31T23:59:59+00:00") is False

    # YYYY-MM-DD with <= operator (inclusive upper bound).
    predicate = get_date_filter("<=2026-02-01")
    assert predicate("2026-02-01T23:59:59+00:00") is True
    assert predicate("2026-02-02T00:00:00+00:00") is False

    # YYYY-MM-DD with = operator (exact date match).
    predicate = get_date_filter("=2026-02-01")
    assert predicate("2026-02-01T12:00:00+00:00") is True
    assert predicate("2026-02-02T00:00:00+00:00") is False

    # YYYY-MM-DD with < operator (exclusive upper bound).
    predicate = get_date_filter("<2026-02-01")
    assert predicate("2026-01-31T23:59:59+00:00") is True
    assert predicate("2026-02-01T00:00:00+00:00") is False

    # YYYY-MM-DD with > operator (exclusive lower bound).
    predicate = get_date_filter(">2026-02-01")
    assert predicate("2026-02-02T00:00:00+00:00") is True
    assert predicate("2026-02-01T23:59:59+00:00") is False

    # YYYY-MM with default '=' operator (matches the month).
    predicate = get_date_filter("2026-02")
    assert predicate("2026-02-15T12:00:00+00:00") is True
    assert predicate("2026-03-01T00:00:00+00:00") is False
    assert predicate("2026-01-31T23:59:59+00:00") is False

    # YYYY-MM with >= operator (month-level inclusive lower bound).
    predicate = get_date_filter(">=2026-02")
    assert predicate("2026-02-01T00:00:00+00:00") is True
    assert predicate("2026-01-31T23:59:59+00:00") is False

    # YYYY with default '=' operator (matches the year).
    predicate = get_date_filter("2026")
    assert predicate("2026-12-31T23:59:59+00:00") is True
    assert predicate("2025-12-31T23:59:59+00:00") is False

    # YYYY with < operator (exclusive upper bound on year).
    predicate = get_date_filter("<2026")
    assert predicate("2025-12-31T23:59:59+00:00") is True
    assert predicate("2026-01-01T00:00:00+00:00") is False

    # YYYY with > operator (exclusive lower bound on year).
    predicate = get_date_filter(">2026")
    assert predicate("2027-01-01T00:00:00+00:00") is True
    assert predicate("2026-12-31T23:59:59+00:00") is False

    # Invalid operator should raise ValueError.
    with pytest.raises(ValueError):
        get_date_filter("=>2026-01-01")
