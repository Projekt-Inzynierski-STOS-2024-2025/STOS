from typing import Any, Self


class StosTaskResponse:
    student_id: str
    task_id: str
    files: list[str]

    def __init__(self, student_id: str, task_id: str) -> None:
        self.student_id = student_id
        self.task_id = task_id
        self.files = []

    @staticmethod
    def from_json(json_object: dict[str, Any]) -> Self:
        student_id = json_object['student_id']
        task_id = json_object['task_id']
        res = StosTaskResponse(student_id, task_id)
        res.files = json_object['files']
        return res


