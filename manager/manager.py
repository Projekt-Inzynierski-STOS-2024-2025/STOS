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


class IManager(ABC):

    @abstractmethod
    def listen(self):
        pass

    # TODO - determine what data is passed
    @abstractmethod
    def task_completion_callback(self, task_data: TaskData, output_path: Path):
        pass

    @abstractmethod
    def register_new_task_callback(self, callback: Callable[[TaskData], None]):
        pass


class Manager(IManager):

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

    @override
    def register_new_task_callback(self, callback: Callable[[TaskData], None]):
        self.__new_task_callbacks.append(callback)

    @override
    def task_completion_callback(self, task_data: TaskData, output_path: Path):
        print('Received task completion data')
        self.__api_driver.upload_results(task_data.task_id)
        try:
            shutil.rmtree(output_path)
        except:
            print("Error handled successfully")

    @override
    def listen(self):
        # TODO - log
        print("Starting manager process")
        while(True):
            task_data = self._handle_task_download()
            self._notify_new_task(task_data)
            sleep(self.__request_timeout)

    # Helper methods
    def _handle_task_download(self) -> TaskData:
            print("manager: fetching data from remote")
            api_tasks = self.__api_driver.fetch_tasks()
            self._handle_cache_misses(api_tasks.files)
            task_data = self._collect_task(api_tasks)
            return task_data
           
    def _handle_cache_misses(self, files: list[str]) -> None:
            missing = self.__cache_driver.check_files(files)
            for file in missing:
                content = self.__api_driver.download_file(file)
                path = self.__storage_driver.save_file(file, content)
                self.__cache_driver.add_entry(file, path)

    def _collect_task(self, stos_task: StosTaskResponse) -> TaskData:
        # Could do some more error handling, let's say cache is infallible
        file_entries = [self.__cache_driver.get_entry(file) for file in stos_task.files]
        task_id = stos_task.task_id
        return TaskData(task_id, file_entries)

    def _notify_new_task(self, task: TaskData):
        for callback in self.__new_task_callbacks:
            callback(task)


        



