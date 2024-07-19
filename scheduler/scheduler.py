from abc import ABC, abstractmethod
from typing import override
import threading
import queue
import uuid
from manager.types import TaskData, Worker

class IScheduler(ABC):

    @abstractmethod
    def init_workers(self, number_of_workers: int) -> None:
        pass
    
    @abstractmethod
    def register_new_task(self, taskData: TaskData) -> None:
        pass

    @abstractmethod
    def manage_workers(self) -> None:
        pass

    @abstractmethod
    def run_container(self, taskData: TaskData, worker: Worker) -> None:
        pass

    @abstractmethod
    def change_workers_count(self) -> None:
        pass
 

class Scheduler(IScheduler):
    def __init__(self, initial_workers: int):
        self.task_queue: queue.Queue[TaskData] = queue.Queue()
        self.workers_queue: queue.Queue[Worker] = queue.Queue()
        self.workers_delta: int = 0
        self.lock: threading.Lock = threading.Lock()

    @override
    def init_workers(self, number_of_workers: int) -> None:
        for _ in range(number_of_workers):
            self.workers_queue.put( Worker(status="awaiting", worker_id=uuid.uuid4()))

    @override
    def register_new_task(self, taskData: TaskData) -> None:
        self.task_queue.put(taskData)
        self.manage_workers()

    @override
    def manage_workers(self) -> None:
        with self.lock:
            if self.workers_delta != 0 :
                self.change_workers_count()
            while not self.workers_queue.empty() and not self.task_queue.empty():
                task = self.task_queue.get()
                thread = threading.Thread(target=self.run_container, args=(task, self.workers_queue.get()))
                thread.start()

    @override
    def run_container(self, taskData: TaskData, worker: Worker) -> None:
        print(f"Started mock container for task {taskData.task_id}")

        #put code running container there

        print(f"Mock container for task {taskData.task_id} has completed work.")

        with self.lock:
            self.workers_queue.put(worker)
        self.manage_workers()

    @override
    def change_workers_count(self) -> None:
        while self.workers_delta > 0:
            self.workers_queue.put(Worker('awaiting', uuid.uuid4()))
            self.workers_delta -= 1
        while self.workers_delta < 0 and not self.workers_queue.empty():
            _ = self.workers_queue.get()
            self.workers_delta += 1

# todo: actually run containers
# todo: handle workers statuses
# todo: containers healthcheck

