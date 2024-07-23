from abc import ABC, abstractmethod
from typing import override

class IStorageDriver(ABC):
    
    # Save file with name id and return URL/PATH
    @abstractmethod
    @staticmethod
    def save_file(id: str, content: str) -> str:
        pass

    # Get contents of file under url. Returns None if file does not exist
    @abstractmethod
    @staticmethod
    def get_file(url: str) -> str | None:
        pass

class LocalStorageDriver(IStorageDriver):
    
    @staticmethod
    @override
    def save_file(id: str, content: str) -> str:
        return f"/tmp/stos/{id}"

    @staticmethod
    @override
    def get_file(url: str) -> str | None:
        return "file contents"
