from abc import ABC, abstractmethod
from typing import override

from types.task import TaskFile, TaskFileType


class ICacheDriver(ABC):

    # Checks cache for existance of files and returns missing files
    @abstractmethod
    @staticmethod
    def check_files(files: list[str]) -> list[str]:
        pass

    # Adds entry regarding a single file to cache
    @abstractmethod
    @staticmethod
    def add_entry(file: str, path: str):
        pass

    # Deletes a record representing file
    @abstractmethod
    @staticmethod
    def delete_entry(file: str):
        pass

    # Get file entry, returns None if file does not exist
    @abstractmethod
    @staticmethod
    def get_entry(file: str) -> TaskFile | None:
        pass



class SQliteCacheDriver(ICacheDriver):

    @override
    @staticmethod
    def check_files(files: list[str]) -> list[str]:
        # TODO -actually implement cache. Return first element for now
        return [files[0]]

    @staticmethod
    @override
    def add_entry(file: str, path: str):
        return

    @staticmethod
    @override
    def delete_entry(file: str):
        return

    @staticmethod
    @override
    def get_entry(file: str) -> TaskFile | None:
        return TaskFile(file, "/tmp/mockpath", TaskFileType.STUDENT_FILE)
    
