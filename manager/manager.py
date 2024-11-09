from abc import ABC, abstractmethod
from typing import Callable, override
from time import sleep
import os
import shutil
import logging
from manager.api_driver import IApiDriver, STOSApiDriver
from manager.cache_driver import ICacheDriver, SQliteCacheDriver
from manager.storage_driver import IStorageDriver, LocalStorageDriver
from manager.types import StosTaskResponse, TaskData


class IManager(ABC):

    @abstractmethod
    def listen(self) -> None:
        pass

    # TODO - determine what data is passed
    @abstractmethod
    def task_completion_callback(self, task_data: TaskData, output_path: str) -> None:
        pass

    @abstractmethod
    def register_new_task_callback(self, callback: Callable[[TaskData], None]) -> None:
        pass


class Manager(IManager):

    logging.basicConfig(
        filename=os.environ.get("LOGS_PATH", "/home/stos/") + 'manager.log',
        filemode='a',
        encoding='utf-8',
        format="{asctime} - {levelname} - {message}"
    )

    # Configuration from env
    __request_timeout: int

    # DI stuff
    __api_driver: type[IApiDriver]
    __cache_driver: type[ICacheDriver]
    __storage_driver: type[IStorageDriver]

    # Observer
    __new_task_callbacks: list[Callable[[TaskData], None]]

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
        logging.debug("Manager initialized successfully.\n" +
                      f"\tApiDriver connected: {self.__api_driver is not None}" +
                      f"\tCacheDriver connected: {self.__cache_driver is not None}" +
                      f"\tStorageDriver connected: {self.__storage_driver is not None}" +
                      f"\tTimeouts set to {self.__request_timeout}"
                      )

    @override
    def register_new_task_callback(self, callback: Callable[[TaskData], None]) -> None:
        logging.debug("New task callback registered")
        self.__new_task_callbacks.append(callback)

    @override
    def task_completion_callback(self, task_data: TaskData, output_path: str) -> None:
        logging.info(f"Received task completion data for task {task_data.task_id}")
        self.__api_driver.upload_results(task_data.task_id)
        shutil.rmtree(output_path)

    @override
    def listen(self) -> None:
        logging.info("Starting manager process")
        while True:
            task_data = self._handle_task_download()
            self._notify_new_task(task_data)
            sleep(self.__request_timeout)

    # Helper methods
    def _handle_task_download(self) -> TaskData:
        logging.info("Fetching data from remote")
        api_tasks = self.__api_driver.fetch_tasks()
        self._handle_cache_misses(api_tasks.files)
        task_data = self._collect_task(api_tasks)
        logging.info(f"Fetched task {task_data.task_id}")
        return task_data
           
    def _handle_cache_misses(self, files: list[str]) -> None:
        missing = self.__cache_driver.check_files(files)
        for file in missing:
            logging.debug(f"Downloading missing {file} file to the cache")
            content = self.__api_driver.download_file(file)
            path = self.__storage_driver.save_file(file, content)
            self.__cache_driver.add_entry(file, path)

    def _collect_task(self, stos_task: StosTaskResponse) -> TaskData:
        # Could do some more error handling, let's say cache is infallible
        file_entries = [self.__cache_driver.get_entry(file) for file in stos_task.files]
        task_id = stos_task.task_id
        logging.debug(f"Task {stos_task.task_id} data: file entries: {file_entries}")
        return TaskData(task_id, file_entries)

    def _notify_new_task(self, task: TaskData) -> None:
        logging.debug(f"Passing task {task.task_id} to the handlers")
        for callback in self.__new_task_callbacks:
            callback(task)
