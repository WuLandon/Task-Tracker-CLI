## Project: Task Tracker CLI (Python)

You are an automated coding agent helping build a small Python CLI app called **tasker** for tracking tasks stored in a local JSON file.

This repo should remain **dependency-free** (standard library only) and must implement the CLI described in `TASK_TRACKER_SPEC.md`.

---

## Non-Negotiable Constraints

- **Language:** Python (standard library only)
- **Interface:** CLI with **positional arguments only** (no interactive prompts)
- **Storage:** single JSON file (create automatically if missing)
- **No external libraries/frameworks**
- **Graceful errors:** never crash with a stack trace for user-caused issues; print a clear message and exit with non-zero status

---

## Commands & Behavior (Must Match Spec)

Implement the following commands:

- `tasker add "description"`
  - Output: `Task added successfully (ID: N)`

- `tasker update ID "new description"`

- `tasker delete ID`

- `tasker mark-in-progress ID`

- `tasker mark-done ID`

- `tasker list`
  - Lists all tasks

- `tasker list STATUS`
  - STATUS in: `todo`, `in-progress`, `done`

Storage file shape (exact shape):

```json
{
  "nextId": 1,
  "order": ["1", "2"],
  "tasks": {
    "1": {
      "description": "text",
      "status": "todo" | "in-progress" | "done",
      "createdAt": "timestamp string",
      "updatedAt": "timestamp string"
    }
  }
}
````

Task record fields (exact shape):

```json
{
  "description": "text",
  "status": "todo" | "in-progress" | "done",
  "createdAt": "timestamp string",
  "updatedAt": "timestamp string"
}
````

Timestamps must update correctly:

* `createdAt` set once on creation
* `updatedAt` set on any change (update/status change)

---

## Repo Layout Expectations

Prefer a simple, maintainable structure:

* `main.py` as the entry point
* Optional: `task_store.py` for JSON read/write helpers
* Optional: `models.py` for task creation/validation
* `tasks.json` as the default storage file (auto-created)

If you add modules, keep them small and cohesive.

---

## Implementation Guidance

### CLI Parsing

* Use `sys.argv` (or `argparse` only if it remains positional and simple).
* Provide a `help`/usage message on invalid input, e.g.:

  * unknown command
  * missing args
  * non-integer IDs
  * invalid status
* Exit codes:

  * `0` on success
  * `1` on user error (bad args, missing ID, invalid status)
  * `2` on unexpected/internal error (rare; still print a friendly message)

### JSON Storage

* Store tasks in a JSON file as a single store object containing:

  * `nextId` (integer counter for generating new IDs)
  * `order` (list of task ID strings in display order)
  * `tasks` (object mapping task ID strings → task record objects)
* If file is missing: create it (empty store with `nextId: 1`, empty `order`, empty `tasks`).
* If JSON is corrupt: print an error explaining the file is invalid and how to fix (e.g., delete or repair), then exit non-zero.
* Use atomic writes to reduce corruption risk:

  * write to temp file, then `os.replace(...)`.

### ID Generation

* IDs must be unique integers in the CLI.
* Use the stored `nextId` counter to allocate IDs and then increment it after allocation.

### Sorting / Display

* Output should be human-readable and consistent.
* Prefer listing tasks in the stored `order` (stable insertion/display order).
* Keep formatting stable to reduce test brittleness.

---

## Error Handling Standards

When a task ID is not found:

* Print: `Task not found (ID: X)` and exit non-zero.

When arguments are wrong:

* Print a short error + usage summary, exit non-zero.

Never print Python tracebacks for expected user mistakes.

---

## Quality Bar

* Keep functions short and testable.
* Avoid “clever” one-liners.
* Prefer explicit validation and clear messages.
* Add small docstrings/comments where it improves clarity.
* Keep side effects localized (file IO in one place).

---

## Before You Commit

* Run manual checks:

  * add → list → update → mark → delete
  * invalid ID / missing args / invalid status
  * missing JSON file (should auto-create)
  * corrupt JSON file (should fail gracefully)

* Ensure implementation matches `TASK_TRACKER_SPEC.md` exactly.
