from typing import Literal, TypedDict

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