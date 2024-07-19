# Types shared throughout STOS, especially ones used in communication between scheduler and manager

from enum import Enum

# Enum representing type of descripted file
class TaskFileType(Enum):
    STUDENT_FILE = 1
    TASK_FILE = 2
    RESULT_FILE = 3
    ADDITIONAL_INFO_FILE = 4

# Object representing single file in context of Task
class TaskFile:
    file_id: int
    disk_path: str
    type: TaskFileType
    
# Object representing a single task, exchanged between schedulear and manager
class TaskData:
    files: list[TaskFile]
    task_id: str

