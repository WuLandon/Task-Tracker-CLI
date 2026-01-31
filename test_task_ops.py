import datetime

from task_ops import add_task


def test_add_task(capsys):
    store = {"nextId": 1, "order": [], "tasks": {}}

    add_task(store, "Write tests")
    captured = capsys.readouterr()

    assert "Task added successfully" in captured.out
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


# def test_update_task():
#     pass


# def test_delete_task():
#     pass


# def test_mark_in_progress():
#     pass


# def test_mark_done():
#     pass


# def test_list_tasks():
#     pass
