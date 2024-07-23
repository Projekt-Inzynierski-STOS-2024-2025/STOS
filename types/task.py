from enum import Enum

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
    
# Object representing a single task, exchanged between schedulear and manager
class TaskData:
    files: list[TaskFile]
    task_id: str

    def __init__(self, task_id: str, files) -> None:
        self.task_id = task_id
        self.files = files
        


