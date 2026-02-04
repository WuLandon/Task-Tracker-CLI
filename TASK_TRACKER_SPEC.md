## Overview

**Task Tracker** is a command-line interface (CLI) application used to track and manage tasks.
The goal is to build a simple CLI that allows users to:

- Track what they need to do
- Track what they are working on
- Track what they have completed

This project helps practice:

- File system operations
- Command-line argument handling
- Data persistence using JSON
- Basic CLI design patterns

---

## Requirements

The application must:

- Run from the command line
- Accept user actions via positional CLI arguments
- Store tasks in a JSON file
- Create the JSON file if it does not exist
- Use only native filesystem modules (no external libraries)
- Handle errors and edge cases gracefully

---

## Core Features

Users must be able to:

- Add tasks
- Update tasks
- Delete tasks
- Mark tasks as **in-progress**
- Mark tasks as **done**
- List all tasks
- List tasks by status:
  - `todo`
  - `in-progress`
  - `done`

---

## Task Properties

Each task must contain the following fields:

```json
{
  "id": number,
  "description": string,
  "status": "todo" | "in-progress" | "done",
  "createdAt": string,
  "updatedAt": string
}
```

### Field Descriptions

| Field         | Description                     |
| ------------- | ------------------------------- |
| `id`          | Unique identifier for the task  |
| `description` | Short task description          |
| `status`      | Current task status             |
| `createdAt`   | Timestamp when task was created |
| `updatedAt`   | Timestamp of last update        |

---

## CLI Commands

### Add a Task

```bash
tasker add "Buy groceries"
```

---

### Update a Task

```bash
tasker update 1 "Buy groceries and cook dinner"
```

---

### Delete a Task

```bash
tasker delete 1
```

---

### Mark Task Status

```bash
tasker mark-in-progress 1
tasker mark-done 1
```

---

### List Tasks

#### List all tasks

```bash
tasker list
```

#### List tasks by status

```bash
tasker list -status "done"
tasker list -status "todo"
tasker list -status "in-progress"
```

---

## Project Constraints

- Use Python for the programming language
- Use positional CLI arguments
- Use a JSON file for storage
- JSON file must be created automatically if missing
- No external libraries or frameworks allowed
- Must use native filesystem APIs
- Errors must be handled gracefully

---

## Suggested Development Steps

### 1. Project Initialization

- Create entry file (`main.py`)
- Create empty JSON storage file

---

### 2. Implementation Order

Recommended progression:

1. Parse CLI arguments
2. Implement `add` command
3. Implement `list` command
4. Implement `update`
5. Implement `mark-in-progress`
6. Implement `mark-done`
7. Implement `delete`
8. Add validation & error handling

---

### 3. Testing & Debugging

- Ensure to test thoroughly before moving to the next implementation
- Verify JSON file contents after every command
- Test invalid inputs
- Ensure timestamps update correctly
- Confirm file creation behavior

---

## Finalization Checklist

- All commands implemented
- JSON storage working correctly
- Errors handled cleanly
- Code is readable and commented
- README written with usage examples
