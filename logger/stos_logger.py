import logging
from logging.handlers import RotatingFileHandler
from abc import ABC, abstractmethod
from typing import override
import os


class ISTOSLogger(ABC):

    @abstractmethod
    def info(self, message: str):
        pass

    @abstractmethod
    def debug(self, message: str):
        pass

    @abstractmethod
    def warning(self, message: str):
        pass

    @abstractmethod
    def error(self, message: str):
        pass


class STOSLogger(ISTOSLogger):

    __logger: logging.Logger
    __LOGS_DIR: str = os.environ.get("LOGS_PATH", "/home/stos/")
    __LOGGING_LEVEL: int = logging.INFO if os.environ.get("ENVIRONMENT") == "prod" else logging.DEBUG
    __BACKUP_LOG_FILES: int = int(os.environ.get("BACKUP_LOG_FILES", 5))
    __LOG_FILE_SIZE: int = int(os.environ.get("LOG_FILE_SIZE", 10 * 1024 * 1024))

    def __init__(self, module_name: str):
        log_file = f"{self.__LOGS_DIR}{module_name}.log"
        handler = RotatingFileHandler(log_file, maxBytes=self.__LOG_FILE_SIZE, backupCount=self.__BACKUP_LOG_FILES)
        handler.setLevel(self.__LOGGING_LEVEL)
        self.__logger = logging.getLogger(module_name)
        self.__logger.setLevel(self.__LOGGING_LEVEL)
        self.__logger.addHandler(handler)

    @override
    def debug(self, message: str) -> None:
        self.__logger.debug(message)

    @override
    def info(self, message: str) -> None:
        self.__logger.info(message)

    @override
    def warning(self, message: str) -> None:
        self.__logger.warning(message)

    @override
    def error(self, message: str) -> None:
        self.__logger.error(message)
