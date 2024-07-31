from abc import ABC, abstractmethod
from typing import override

from manager.types import StosTaskResponse



class IApiDriver(ABC):

    @staticmethod
    @abstractmethod
    def fetch_tasks() -> StosTaskResponse:
        pass

    @staticmethod
    @abstractmethod
    def download_file(id: str) -> str:
        pass

    @staticmethod
    @abstractmethod
    def upload_results():
        pass


class STOSApiDriver(IApiDriver):

    @override
    @staticmethod
    def fetch_tasks() -> StosTaskResponse:
        # TODO - actual api communication
        res = {"student_id": "2137", "task_id": "2201", "files": ["1", "2", "54"]}
        return StosTaskResponse.from_json(res)

    @override
    @staticmethod
    def download_file(id: str) -> str:
        # TODO - actually fetch it from api
        return f"Some file contents {id}"

    @override
    @staticmethod
    def upload_results():
        pass




