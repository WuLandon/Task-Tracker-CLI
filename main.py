from __future__ import annotations

import sys
from datetime import datetime, timezone

import task_ops
from task_store import TASK_STATUSES, load_tasks, save_tasks


def now_iso_utc() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def print_usage() -> None:
    print("Usage:")
    print('tasker add "description"')
    print('tasker update ID "new description"')
    print("tasker delete ID")
    print("tasker mark-in-progress ID")
    print("tasker mark-done ID")
    print(f"tasker list [{'|'.join(TASK_STATUSES)}]")


def parse_task_id(value: str) -> int:
    try:
        task_id = int(value)
    except ValueError:
        raise ValueError("Task ID must be an integer.") from None
    if task_id < 1:
        raise ValueError("Task ID must be a positive integer.")
    return task_id


def main() -> None:
    args = sys.argv[1:]

    if not args:
        print("Error: missing command.", file=sys.stderr)
        print_usage()
        sys.exit(1)

    cmd = args[0]
    known_commands = {
        "add",
        "update",
        "delete",
        "mark-in-progress",
        "mark-done",
        "list",
    }

    if cmd not in known_commands:
        print(f"Error: unknown command '{cmd}'.", file=sys.stderr)
        print_usage()
        sys.exit(1)

    try:
        store = load_tasks()

        if cmd == "add":
            if len(args) != 2:
                raise ValueError("add requires exactly 1 argument (description).")
            task_id = task_ops.add_task(store, args[1], now_iso_utc())
            save_tasks(store)
            print(f"Task added successfully (ID: {task_id})")
            return

        if cmd == "update":
            if len(args) != 3:
                raise ValueError("update requires exactly 2 arguments (ID and description).")
            task_id = parse_task_id(args[1])
            task_ops.update_task(store, task_id, args[2], now_iso_utc())
            save_tasks(store)
            return

        if cmd == "delete":
            if len(args) != 2:
                raise ValueError("delete requires exactly 1 argument (ID).")
            task_id = parse_task_id(args[1])
            task_ops.delete_task(store, task_id)
            save_tasks(store)
            return

        if cmd == "mark-in-progress":
            if len(args) != 2:
                raise ValueError("mark-in-progress requires exactly 1 argument (ID).")
            task_id = parse_task_id(args[1])
            task_ops.mark_in_progress(store, task_id, now_iso_utc())
            save_tasks(store)
            return

        if cmd == "mark-done":
            if len(args) != 2:
                raise ValueError("mark-done requires exactly 1 argument (ID).")
            task_id = parse_task_id(args[1])
            task_ops.mark_done(store, task_id, now_iso_utc())
            save_tasks(store)
            return

        if cmd == "list":
            if len(args) > 2:
                raise ValueError("list takes at most 1 argument (status).")

            status_filter = None
            if len(args) == 2:
                status_filter = args[1]
                if status_filter not in TASK_STATUSES:
                    raise ValueError(f"invalid status '{status_filter}'.")

            tasks = task_ops.list_tasks(store, status_filter)  # type: ignore[arg-type]
            for task_id, record in tasks:
                print(f"[{task_id}] {record['description']} ({record['status']})")
            return

        print("Error: command not implemented yet.", file=sys.stderr)
        print_usage()
        sys.exit(2)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        print_usage()
        sys.exit(1)
    except NotImplementedError:
        print("Error: not implemented yet.", file=sys.stderr)
        sys.exit(2)
    except SystemExit:
        raise
    except Exception:
        print("Error: unexpected internal error.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
