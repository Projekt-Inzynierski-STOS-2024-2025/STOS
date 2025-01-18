from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, override
import threading
import queue
import subprocess
import shutil
import zipfile
from manager.types import TaskData, WorkerCommands
import os
from logger.stos_logger import STOSLogger, ISTOSLogger


class IScheduler(ABC):

    # add task data to queue 
    @abstractmethod
    def register_new_task(self, task_data: TaskData) -> None:
        pass

    # initialize worker containers
    @abstractmethod
    def initialize_workers(self) -> None:
        pass

    # method that checks workers queue and tasks queue if new container can start processing task
    @abstractmethod
    def manage_workers(self) -> None:
        pass

    # start processing task inside worker docker container
    @abstractmethod
    def process_task(self, task_data: TaskData, worker_id: str) -> None:
        pass

    # register callback function that is run on task finish
    @abstractmethod
    def register_task_completion_callback(self, callback: Callable[[TaskData, Path], None]) -> None:
        pass


class Scheduler(IScheduler):

    __stos_logger: ISTOSLogger = STOSLogger("scheduler")

    __task_completion_callbacks: list[Callable[[TaskData, Path], None]]
    __tasks_queue: queue.Queue[TaskData]
    __workers_queue: queue.Queue[str]
    __workers_count: int
    __lock: threading.Lock
    __worker_cpu: str
    __worker_ram: str
    __total_cpu: str
    __total_ram: str

    def __init__(self):
        self.__task_completion_callbacks = []
        self.__tasks_queue = queue.Queue()
        self.__workers_queue = queue.Queue()
        self.__lock = threading.Lock()
        self.__worker_cpu = os.environ.get("WORKER_CPU", "1")
        self.__worker_ram = os.environ.get("WORKER_RAM", "1Gi")
        self.__total_cpu = subprocess.check_output(["nproc"]).decode().strip()
        self.__total_ram = subprocess.check_output(["free -h | awk '/^Mem:/ {print $2}'"], shell=True).decode().strip()
        self.__workers_count = self.get_initial_workers_count()
        self.initialize_workers()

    @override
    def initialize_workers(self) -> None:
        for i in range(0, self.__workers_count):
            cid = str(i)
            self.create_worker_pipes_and_directories(cid)
            self.run_worker(cid, 10)
            self.__workers_queue.put(cid)

    @override
    def register_new_task(self, task_data: TaskData) -> None:
        self.__tasks_queue.put(task_data)
        self.manage_workers()

    @override
    def manage_workers(self) -> None:
        with self.__lock:
            while not self.__workers_queue.empty() and not self.__tasks_queue.empty():
                task = self.__tasks_queue.get()
                worker_id = self.__workers_queue.get()
                thread = threading.Thread(target=self.process_task, args=(task, worker_id))
                thread.start()

    @override
    def process_task(self, task_data: TaskData, worker_id: str) -> None:
        self.__stos_logger.info(f"process_task: Worker: {worker_id} started processing task: {task_data.task_id}")
        self.zip_and_copy_task_data_files_to_worker_src(task_data, worker_id)
        self.send_command_to_worker_input_pipe(worker_id, WorkerCommands.DEBUG_AND_COMPILE.value)
        self.watch_output_pipe(task_data, worker_id)
        result_path = self.copy_result(task_data, worker_id)
        for callback in self.__task_completion_callbacks:
            callback(task_data, Path(result_path))
        self.__stos_logger.info(f"process_task: Worker: {worker_id} processed task: {task_data.task_id}")
        with self.__lock:
            self.__workers_queue.put(worker_id)
        self.manage_workers()

    @override
    def register_task_completion_callback(self, callback: Callable[[TaskData, Path], None]) -> None:
        self.__task_completion_callbacks.append(callback)

    ### HELPER METHODS ###

    # Wait for worker result and copy it to proper folder
    def watch_output_pipe(self, task_data: TaskData, worker_id: str):
        path = f'./worker_{worker_id}/io/output'
        if not os.path.exists(path):
            self.__stos_logger.error(f"watch_output_pipe: Path {path} does not exist.")
            return
        fifo = os.open(path, os.O_RDONLY)
        self.__stos_logger.info(f"watch_output_pipe: Waiting for task: {task_data.task_id} result from worker: {worker_id}")
        data = os.read(fifo, 1024 * 1024 * 1024)
        self.__stos_logger.info(f"watch_output_pipe: Result: {data} for task: {task_data.task_id} from worker: {worker_id}")
        os.close(fifo)

    # Copy task result 
    def copy_result(self, task_data: TaskData, worker_id: str) -> str:
        result_path = f'./worker_{worker_id}/io/result'
        dest_path = f"./results/{task_data.task_id}"
        os.makedirs(dest_path, exist_ok=True)
        if os.path.isdir(result_path):
            shutil.copytree(result_path, dest_path, dirs_exist_ok=True)
        else:
            shutil.copy2(result_path, dest_path)
        self.__stos_logger.info(f"copy_result: Copied task {task_data.task_id} result")
        return dest_path

    # Convert memory obtained from .env or awk to float number of gigabytes
    def convert_memory_to_gb(self, memory: str) -> float:
        if memory.lower().endswith('gi') or memory.lower().endswith("g"):
            return float(memory[:-2])
        elif memory.lower().endswith('mi') or memory.lower().endswith("m"):
            return float(memory[:-2]) / 1024
        else:
            return float(memory)

    def create_worker_pipes_and_directories(self, worker_id: str) -> None:
        self.__stos_logger.info(f'create_worker_pipes_and_directories: Started pipes and directories initialization for worker: {worker_id}')
        base_path = f"./worker_{worker_id}"
        work_dir = os.path.join(base_path, "work")
        fails_dir = os.path.join(base_path, "fails")
        io_dir = os.path.join(base_path, "io")
        src_dir = os.path.join(io_dir, "src")
        result_dir = os.path.join(io_dir, "result")
        compilers_dir = os.path.join(base_path, "compilers")
        control_dir = os.path.join(base_path, "control")
        sdks_dir = os.path.join(base_path, "sdks")
        input_pipe = os.path.join(io_dir, "input")
        output_pipe = os.path.join(io_dir, "output")
        directories = [base_path, work_dir, fails_dir, io_dir, src_dir, result_dir, compilers_dir, control_dir, sdks_dir]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        for src, dest in [("./compilers", compilers_dir), ("./sdks", sdks_dir), ("./control", control_dir)]:
            if os.path.exists(src):
                for item in os.listdir(src):
                    s = os.path.join(src, item)
                    d = os.path.join(dest, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
        for pipe in [input_pipe, output_pipe]:
            try:
                os.mkfifo(pipe)
            except FileExistsError:
                pass
        self.__stos_logger.info(f'create_worker_pipes_and_directories: Created pipes and directories for worker: {worker_id}')

    def run_worker(self, worker_id: str, timeout: int) -> None:
        base_dir =  f"./worker_{worker_id}"
        compilers_path = os.path.join(base_dir, "compilers")
        sdks_path = os.path.join(base_dir, "sdks")
        io_path = os.path.join(base_dir, "io")
        work_path = os.path.join(base_dir, "work")
        control_path = os.path.join(base_dir, "control")

        docker_command = [
            "docker", "run",
            "-d",
            "--rm",
            "--user", "root",
            "--mount", f"type=bind,readonly,src={compilers_path},target=/compiler",
            "--mount", f"type=bind,readonly,src={sdks_path},target=/sdk",
            "--mount", f"type=bind,src={io_path},target=/io",
            "--mount", f"type=bind,src={work_path},target=/work",
            "--mount", f"type=bind,src={control_path},target=/control",
            f"--memory={self.__worker_ram}g",
            f"--cpus={self.__worker_cpu}",
            "--name", f"stos.compiler.{worker_id}",
            "-e", f"CID={worker_id}",
            "-e", f"TIMEOUT={timeout}",
            "wine-vs-runner"
        ]
        result = subprocess.run(
            docker_command,
            capture_output=True,
            text=True,
            check=True
        )
        self.__stos_logger.info(f"run_worker: Worker {worker_id} started")

    # get worker count based on available resources
    def get_initial_workers_count(self) -> int:
        ram_workers = int(self.convert_memory_to_gb(self.__total_ram) / self.convert_memory_to_gb(self.__worker_ram))
        cpu_workers = int(float(self.__total_cpu) / float(self.__worker_cpu)) - 2
        return min(ram_workers, cpu_workers)

    # copies all files from task_data to
    def zip_and_copy_task_data_files_to_worker_src(self, task_data: TaskData, worker_id: str) -> None:
        worker_src_path = f'./worker_{worker_id}/io/src'
        zip_file_path = os.path.join(worker_src_path, "main.zip")
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for task_file in task_data.files:
                file_path = task_file.disk_path
                if os.path.exists(file_path):
                    zipf.write(file_path, os.path.basename(file_path))
                else:
                    self.__stos_logger.info(f"zip_and_copy_task_data_files_to_worker_src: File {task_file.file_id} does not exist {task_file.disk_path} and was skipped")

    def send_command_to_worker_input_pipe(self, worker_id: str, input_command: str):
        input_pipe_path = f'./worker_{worker_id}/io/input'
        if not os.path.exists(input_pipe_path):
            self.__stos_logger.info(f"send_command_to_worker_input_pipe: Input pipe {input_pipe_path} does not exist.")
            return
        try:
            with os.fdopen(os.open(input_pipe_path, os.O_WRONLY), 'wb') as fifo:
                _ = fifo.write(input_command.encode("UTF-8"))
                self.__stos_logger.info(f"send_command_to_worker_input_pipe: Command sent to input pipe {input_pipe_path} for worker: {worker_id}")
        except Exception as e:
            self.__stos_logger.error(f"send_command_to_worker_input_pipe: Input pipe error: {e}")
