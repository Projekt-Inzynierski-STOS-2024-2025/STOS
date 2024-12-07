from abc import ABC, abstractmethod
from enum import Enum


class ExecutorType(Enum):
    C = 0
    CPP = 1
    PYTHON = 2
    SDL = 3
    CONIO = 4
    LUA = 5


class IExecutor(ABC):

    # Runs executable file in a dedicated container
    @abstractmethod
    def run_executor(self, executable_path: str, input_data_path: str, mode: ExecutorType) -> None:
        pass

    # Fetches result file from a container
    @abstractmethod
    def read_output(self) -> str:
        pass
