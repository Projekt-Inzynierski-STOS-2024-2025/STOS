from abc import ABC, abstractmethod
from executor_type import ExecutorType


class IExecutor(ABC):

    # Runs executable file in a dedicated container
    @abstractmethod
    def run_executor(self, executable_path: str, input_data_path: str, mode: ExecutorType) -> None:
        pass

    # Fetches result file from a container
    @abstractmethod
    def read_output(self) -> str:
        pass
