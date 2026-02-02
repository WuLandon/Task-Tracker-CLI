from typing import Literal, TypedDict

TASK_STATUS_TYPES = Literal["done", "in-progress", "todo"]
TASK_ID = str


class TaskRecord(TypedDict):
    description: str
    status: TASK_STATUS_TYPES
    createdAt: str
    updatedAt: str


class Store(TypedDict):
    nextId: int
    order: list[TASK_ID]
    tasks: dict[TASK_ID, TaskRecord]
