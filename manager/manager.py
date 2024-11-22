import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, override
from time import sleep
import os
import shutil
from manager.api_driver import IApiDriver, STOSApiDriver
from manager.cache_driver import ICacheDriver, SQliteCacheDriver
from manager.storage_driver import IStorageDriver, LocalStorageDriver
from manager.types import StosTaskResponse, TaskData
from logger.stos_logger import STOSLogger


class IManager(ABC):

    @abstractmethod
    def listen(self) -> None:
        pass

    @abstractmethod
    def task_completion_callback(self, task_data: TaskData, output_path: Path) -> None:
        pass

    @abstractmethod
    def register_new_task_callback(self, callback: Callable[[TaskData], None]) -> None:
        pass


class Manager(IManager):
    __stos_logger: logging.Logger = STOSLogger("manager")

    # Configuration from env
    __request_timeout: int

    # DI stuff
    __api_driver: type[IApiDriver]
    __cache_driver: type[ICacheDriver]
    __storage_driver: type[IStorageDriver]

    # Observer
    __new_task_callbacks: list[Callable[[TaskData], None]]

    __remote_tag: str = ''

    def __init__(self, 
                 api: type[IApiDriver] = STOSApiDriver,
                 cache: type[ICacheDriver] = SQliteCacheDriver,
                 storage: type[IStorageDriver] = LocalStorageDriver
                 ) -> None:
        self.__new_task_callbacks = []
        # Load configuration from env variables
        self.__request_timeout = int(os.environ.get("MANAGER_REQUEST_TIMEOUT", "1"))
        # DI
        self.__api_driver = api
        self.__cache_driver = cache
        self.__storage_driver = storage
        self.__stos_logger.debug("Manager initialized successfully.\n" +
                                 f"\tApiDriver connected: {self.__api_driver is not None}" +
                                 f"\tCacheDriver connected: {self.__cache_driver is not None}" +
                                 f"\tStorageDriver connected: {self.__storage_driver is not None}" +
                                 f"\tTimeouts set to {self.__request_timeout}"
                                 )

    @override
    def register_new_task_callback(self, callback: Callable[[TaskData], None]) -> None:
        self.__stos_logger.debug("New task callback registered")
        self.__new_task_callbacks.append(callback)

    @override
    def task_completion_callback(self, task_data: TaskData, output_path: Path) -> None:
        self.__stos_logger.info(f"Received task completion data for task {task_data.task_id}")
        self.__api_driver.upload_results(task_data.task_id)
        try:
            shutil.rmtree(output_path)
        except:
            self.__stos_logger.error(f"Error while deleting task {task_data.task_id} result directory")

    @override
    def listen(self) -> None:
        self.__stos_logger.info("Starting manager process")
        while True:
            self.synchronize_filesdb()
            task_data = self._handle_task_download()
            self._notify_new_task(task_data)
            sleep(self.__request_timeout)

    # Helper methods
    def _handle_task_download(self) -> TaskData:
        self.__stos_logger.info("Fetching data from remote")
        api_tasks = self.__api_driver.fetch_tasks()
        self._handle_cache_misses(api_tasks.files)
        task_data = self._collect_task(api_tasks)
        self.__stos_logger.info(f"Fetched task {task_data.task_id}")
        return task_data

    def _handle_cache_misses(self, files: list[str]) -> None:
        missing = self.__cache_driver.check_files(files)
        for file in missing:
            self.__stos_logger.debug(f"Downloading missing {file} file to the cache")
            content, extension = self.__api_driver.download_file(file)
            path = self.__storage_driver.save_file(file, content, extension)
            self.__cache_driver.add_entry(file, path)

    def _collect_task(self, stos_task: StosTaskResponse) -> TaskData:
        # Could do some more error handling, let's say cache is infallible
        file_entries = [self.__cache_driver.get_entry(file) for file in stos_task.files]
        task_id = stos_task.task_id
        self.__stos_logger.debug(f"Task's {stos_task.task_id} file entries: " +
                                "\n".join([file.disk_path if file is not None else "<UNKNOWN FILE>" for file in file_entries]))
        return TaskData(task_id, file_entries)

    def _notify_new_task(self, task: TaskData) -> None:
        self.__stos_logger.debug(f"Passing task {task.task_id} to the handlers")
        for callback in self.__new_task_callbacks:
            callback(task)

    def synchronize_filesdb(self) -> None:
        remote_tag = self.__api_driver.fetch_remote_tag()
        if(not self.__remote_tag or remote_tag.remote_tag != self.__remote_tag):
            self.__stos_logger.info(f"Remote tag not equal Local:{self.__remote_tag} - Remote:{remote_tag.remote_tag}, fetching files.db...")
            self.__api_driver.fetch_filesdb_zip()
            self.__stos_logger.info("Files db fetched")
            self.__remote_tag = remote_tag.remote_tag
