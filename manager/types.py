from typing import Self
from enum import Enum
from uuid import UUID
import json


# STOS Api responses
class StosTaskResponse:
    student_id: str
    task_id: str
    files: list[str]

    def __init__(self, student_id: str, task_id: str) -> None:
        self.student_id = student_id
        self.task_id = task_id
        self.files = []

    @staticmethod
    def from_json(json_string: str) -> Self:
        data = json.loads(json_string)
        student_id = data['student_id']
        task_id = data['task_id']
        res = StosTaskResponse(student_id, task_id)
        res.files = data['file_ids']
        return res


# Intra app communication

# Enum representing type of descripted file
class TaskFileType(Enum):
    STUDENT_FILE = 1
    TASK_FILE = 2
    RESULT_FILE = 3
    ADDITIONAL_INFO_FILE = 4


# Object representing single file in context of Task
class TaskFile:
    file_id: str
    disk_path: str
    task_type: TaskFileType

    def __init__(self, file_id: str, disk_path: str, task_type: TaskFileType) -> None:
        self.file_id = file_id
        self.disk_path = disk_path
        self.task_type = task_type


# Object representing a single task, exchanged between scheduler and manager
class TaskData:
    files: list[TaskFile]
    task_id: str

    def __init__(self, task_id: str, files: list[TaskFile]) -> None:
        self.task_id = task_id
        self.files = files
        

class Worker:
    status: str
    worker_id: UUID

    def __init__(self, status: str, worker_id: UUID) -> None:
        self.status = status
        self.worker_id = worker_id
