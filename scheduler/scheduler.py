from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, override
import threading
import queue
from uuid import uuid4
import subprocess
import shutil
from manager.types import TaskData, TaskFile, TaskFileType
import os

class IScheduler(ABC):
     
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
    def run_container(self, taskData: TaskData) -> None:
        pass

    # register callback function that is run on task finish
    @abstractmethod
    def register_task_completion_callback(self, callback: Callable[[TaskData, Path], None])-> None:
        pass
 

class Scheduler(IScheduler):

    __task_completion_callbacks: list[Callable[[TaskData, Path], None]]
    __tasks_queue: queue.Queue[TaskData]
    __available_workers: int
    __lock: threading.Lock
    __worker_cpu: str
    __worker_ram: str
    __total_cpu: str
    __total_ram: str


    def __init__(self):
        self.__task_completion_callbacks = []
        self.__tasks_queue = queue.Queue()
        self.__lock = threading.Lock()
        self.__worker_cpu = os.environ.get("WORKER_CPU", "1")
        self.__worker_ram = os.environ.get("WORKER_RAM", "1Gi")
        self.__total_cpu = subprocess.check_output(["nproc"]).decode().strip() 
        self.__total_ram = subprocess.check_output(["free -h | awk '/^Mem:/ {print $2}'"], shell=True).decode().strip()
        self.__available_workers = self.get_initial_workers_count()
    
    def get_initial_workers_count(self) -> int:
        ram_workers = int(self.convert_memory_to_gb(self.__total_ram) / self.convert_memory_to_gb(self.__worker_ram))
        cpu_workers = int(float(self.__total_cpu) / float(self.__worker_cpu))
        return min(ram_workers, cpu_workers)

    @override
    def register_new_task(self, taskData: TaskData) -> None:
        self.__tasks_queue.put(taskData)
        self.manage_workers()

    @override
    def manage_workers(self) -> None:
        with self.__lock:
            while self.__available_workers > 0 and not self.__tasks_queue.empty():
                self.__available_workers -= 1
                task = self.__tasks_queue.get()
                thread = threading.Thread(target=self.run_container, args=(task,))
                thread.start()

    @override
    def run_container(self, taskData: TaskData) -> None:
        worker_id = uuid4()
        print(f"Started mock container for task {taskData.task_id}")
        worker_dir = Path(f"./worker_files/{worker_id}")
        worker_dir.parent.mkdir(exist_ok=True)
        if worker_dir.exists():
            shutil.rmtree(worker_dir)
        worker_dir.mkdir()
        for file in taskData.files:
            shutil.copy(file.disk_path, worker_dir / "source/main.cpp")
        abs_path_to_files = str(worker_dir.resolve())
        _ =subprocess.run([
            "docker", "run", "--rm",
            "--name", f"worker_{worker_id}" ,
            "-e", f"FILES_PATH={worker_dir}",
            "-v", f"{abs_path_to_files}:/app/project", 
            "--cpus", self.__worker_cpu,        
            "--memory", self.__worker_ram+"g", 
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
            self.__available_workers += 1
        self.manage_workers()

    @override 
    def register_task_completion_callback(self, callback: Callable[[TaskData, Path], None]) -> None:
        self.__task_completion_callbacks.append(callback)

    def convert_memory_to_gb(self, memory: str) -> float:
        if memory.endswith('Gi'):
            return float(memory[:-2])
        elif memory.endswith('Mi'):
            return float(memory[:-2])
        else:
             return float(memory)

