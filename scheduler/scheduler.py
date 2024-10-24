from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, override
import threading
import queue
from uuid import uuid4
import subprocess
import shutil
from .scheduler_types import Worker
from manager.types import TaskData, TaskFile, TaskFileType
import os

class IScheduler(ABC):

    # initialize queue with workers
    @abstractmethod
    def init_workers(self, number_of_workers: int) -> None:
        pass
     
    # add task data to queue 
    @abstractmethod
    def register_new_task(self, taskData: TaskData) -> None:
        pass

    # method that handles:
    #   - changes in amount of workers
    #   - checks workers queue and tasks queue if new container can start processing task
    @abstractmethod
    def manage_workers(self) -> None:
        pass

    # run container that process the task
    @abstractmethod
    def run_container(self, taskData: TaskData, worker: Worker) -> None:
        pass

    # change amount of workers in queue
    @abstractmethod
    def change_workers_count(self) -> None:
        pass

    # register callback function that is run on task finish
    @abstractmethod
    def register_task_completion_callback(self, callback: Callable[[TaskData, str], None])-> None:
        pass
 

class Scheduler(IScheduler):

    __task_completion_callbacks: list[Callable[[TaskData, str], None]]
    __tasks_queue: queue.Queue[TaskData]
    __workers_queue: queue.Queue[Worker]
    __workers_delta: int
    __lock: threading.Lock


    def __init__(self):
        self.__task_completion_callbacks = []
        self.__tasks_queue = queue.Queue()
        self.__workers_queue = queue.Queue()
        self.__workers_delta = 0
        self.__lock = threading.Lock()
        self.init_workers(int(os.environ.get("NUMBER_OF_WORKERS", "3")))
        

    @override
    def init_workers(self, number_of_workers: int) -> None:
        for _ in range(number_of_workers):
            self.__workers_queue.put( Worker(worker_id=str(uuid4())))

    @override
    def register_new_task(self, taskData: TaskData) -> None:
        self.__tasks_queue.put(taskData)
        self.manage_workers()

    @override
    def manage_workers(self) -> None:
        with self.__lock:
            if self.__workers_delta != 0 :
                self.change_workers_count()
            while not self.__workers_queue.empty() and not self.__tasks_queue.empty():
                task = self.__tasks_queue.get()
                thread = threading.Thread(target=self.run_container, args=(task, self.__workers_queue.get()))
                thread.start()

    @override
    def run_container(self, taskData: TaskData, worker: Worker) -> None:
        print(f"Started mock container for task {taskData.task_id}")
        worker_dir = Path(f"./worker_files/{worker.worker_id}")
        worker_dir.parent.mkdir(exist_ok=True)
        if worker_dir.exists():
            shutil.rmtree(worker_dir)
        worker_dir.mkdir()
        for file in taskData.files:
            shutil.copy(file.disk_path, worker_dir / Path(file.disk_path).name)
        abs_path_to_files = str(worker_dir.resolve())
        _ =subprocess.run([
            "docker", "run", "--rm",
            "--name", f"worker_{worker.worker_id}" ,
            "-e", f"FILES_PATH={worker_dir}",
            "-v", f"{abs_path_to_files}:/app/{worker_dir}", 
            "worker"
        ], 
        check=True)
        print(f"Mock container for task {taskData.task_id} has completed work.")
        resultData: TaskData = TaskData(taskData.task_id, [])
        output_dir = Path(f"./output/{taskData.task_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        for file_path in worker_dir.iterdir():
            if file_path.is_file():
                shutil.copy(file_path, output_dir / file_path.name)
                resultData.files.append(TaskFile(str(uuid4()), str(worker_dir / file_path.name), TaskFileType.RESULT_FILE))
        print(f"Files copied to output folder.")
        for callback in self.__task_completion_callbacks:
            callback(resultData, output_dir)
        with self.__lock:
            self.__workers_queue.put(worker)
        self.manage_workers()

    @override
    def change_workers_count(self) -> None:
        while self.__workers_delta > 0:
            self.__workers_queue.put(Worker(str(uuid4())))
            self.__workers_delta -= 1
        while self.__workers_delta < 0 and not self.__workers_queue.empty():
            _ = self.__workers_queue.get()
            self.__workers_delta += 1

    @override 
    def register_task_completion_callback(self, callback: Callable[[TaskData, str], None]) -> None:
        self.__task_completion_callbacks.append(callback)
