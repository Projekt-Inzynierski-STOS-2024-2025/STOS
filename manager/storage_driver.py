import logging
from abc import ABC, abstractmethod
import os
from typing_extensions import override
from logger.stos_logger import get_logger


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

    __stos_logger: logging.Logger = get_logger("local_storage_driver")

    # __SAVE_PATH = Path("./tmp/stos/")
    __SAVE_PATH = "D:\\STOS\\tmp\\"

    @staticmethod
    @override
    def save_file(id: str, content: str) -> str:
        LocalStorageDriver.__ensure_dir_structure()
        saved_path = str(LocalStorageDriver.__SAVE_PATH) + id
        with open(saved_path, "w") as file:
            _ = file.write(content)
        return saved_path

    @staticmethod
    @override
    def get_file(url: str) -> str | None:
        file_exists = os.path.isfile(url)
        if not file_exists:
            LocalStorageDriver.__stos_logger.debug(f"File {url} does not exist")
            return None
        with open(url, 'r') as file:
            content = file.read()
        LocalStorageDriver.__stos_logger.debug(f"File has been read successfully")
        return content

    @staticmethod
    def __ensure_dir_structure() -> None:
        if not os.path.isdir(LocalStorageDriver.__SAVE_PATH):
            # LocalStorageDriver.__SAVE_PATH.parent.mkdir(exist_ok=True)
            LocalStorageDriver.__stos_logger.debug(f"Creating directory {LocalStorageDriver.__SAVE_PATH}")
            os.mkdir(LocalStorageDriver.__SAVE_PATH)
