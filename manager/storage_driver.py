import os
from abc import ABC, abstractmethod
from typing import override


class IStorageDriver(ABC):
    # Save file with name id and return URL/PATH
    @staticmethod
    @abstractmethod
    def save_file(id: str, content: str) -> str:
        pass

    # Get contents of file under url. Returns None if file does not exist
    @staticmethod
    @abstractmethod
    def get_file(url: str) -> str | None:
        pass


class LocalStorageDriver(IStorageDriver):
    # __SAVE_PATH = Path("./tmp/stos/")
    __SAVE_PATH = "tmp/stos"

    @staticmethod
    @override
    def save_file(id: str, content: str) -> str:
        LocalStorageDriver.__ensure_dir_structure()
        saved_path = str(LocalStorageDriver.__SAVE_PATH) + id
        with open(saved_path, "w", encoding='utf-8') as file:
            _ = file.write(content)
        return saved_path

    @staticmethod
    @override
    def get_file(url: str) -> str | None:
        file_exists = os.path.isfile(url)
        if not file_exists:
            return None
        with open(url, 'r', encoding='utf-8') as file:
            content = file.read()
        return content

    @staticmethod
    def __ensure_dir_structure():
        if not os.path.isdir(LocalStorageDriver.__SAVE_PATH):
            # LocalStorageDriver.__SAVE_PATH.parent.mkdir(exist_ok=True)
            os.mkdir(LocalStorageDriver.__SAVE_PATH)
