from enum import Enum

class TaskFileType(Enum):
    STUDENT_FILE = 1
    TASK_FILE = 2
    RESULT_FILE = 3
    ADDITIONAL_INFO_FILE = 4

class TaskFile:
    file_id: str
    disk_path: str
    task_type: TaskFileType

    def __init__(self, file_id: str, disk_path: str, task_type: TaskFileType) -> None:
        self.file_id = file_id
        self.disk_path = disk_path
        self.task_type = task_type
    
class TaskData:
    files: list[TaskFile]
    task_id: str

    def __init__(self, task_id: str, files: list[TaskFile]) -> None:
        self.task_id = task_id
        self.files = files
        
class Worker:
    worker_id: str

    def __init__(self, worker_id: str ) -> None:
        self.worker_id = worker_id