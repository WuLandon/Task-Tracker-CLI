import datetime

from task_ops import add_task, update_task


# Validates add_task stores a new task and increments IDs without breaking order.
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


# Verifies update_task changes description/status and refreshes updatedAt.
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


# def test_delete_task():
#     pass


# def test_mark_in_progress():
#     pass


# def test_mark_done():
#     pass


# def test_list_tasks():
#     pass
