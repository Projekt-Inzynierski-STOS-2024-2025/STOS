from abc import ABC, abstractmethod
from enum import Enum
from typing import override


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
    def run_executable(self, executable_path: str, input_data_path: str, mode: ExecutorType) -> str:
        pass

    # Fetches result file from a container
    @abstractmethod
    def read_output(self) -> str:
        pass

    # Finds available container that supports given type of executor and returns its ID
    @abstractmethod
    def find_container(self, mode: ExecutorType) -> str:
        pass


# The container is responsible for executing whole set of tests
class ContainerBulkExecutor(IExecutor):

    # When implemented, change to environment variable
    __CONTAINER_PATH: str = "/path/in/container/"

    @override
    def run_executable(self, executable_path: str, input_data_path: str, mode: ExecutorType) -> str:
        container_id: str = self.find_container(mode)
        self.__copy_to_container(container_id, executable_path, self.__CONTAINER_PATH + executable_path)
        self.__copy_to_container(container_id, input_data_path, self.__CONTAINER_PATH + input_data_path)
        self.__prepare_command_set_file(executable_path, input_data_path)
        self.__copy_to_container(container_id, "commands.bat", self.__CONTAINER_PATH + "commands.bat")
        self.__run_command_set()

        return self.read_output()

    @override
    def read_output(self) -> str:
        # To be implemented: When result of executing tests in the container of an executable file is ready, read it.
        pass

    @override
    def find_container(self, mode: ExecutorType) -> str:
        # To be implemented: When images for different execution types are created, implement this logic, that would
        # search for available container that is capable of running this type of executable.
        pass

    def __copy_to_container(self, container_id: str, source_path: str, destination_path: str) -> None:
        # To be implemented: Copy source file from host file path to the container.
        pass

    def __prepare_command_set_file(self, executable_path: str, input_data_path: str):
        commands = []
        with open(input_data_path, 'r') as f:
            for input_params in f:
                commands.append(f"{executable_path} {input_params}")
        with open("commands.bat", 'w') as f:
            for command in commands:
                f.write(command)

    def __run_command_set(self) -> None:
        # To be implemented: Run commands from previously prepared file
        pass


# Application uses executor container only for running single executable process with given set of input data
class ContainerExecutor(IExecutor):

    # When implemented, change to environment variable
    __CONTAINER_PATH: str = "/path/in/container/"

    @override
    def run_executable(self, executable_path: str, input_data_path: str, mode: ExecutorType) -> str:
        container_id: str = self.find_container(mode)
        self.__copy_to_container(container_id, executable_path, self.__CONTAINER_PATH + executable_path)
        with open(input_data_path, 'r') as f:
            self.__execute_with_param(self.__CONTAINER_PATH + executable_path, f.read())
        return self.read_output()

    @override
    def read_output(self) -> str:
        # To be implemented: When result of executing tests in the container of an executable file is ready, read it.
        pass

    @override
    def find_container(self, mode: ExecutorType) -> str:
        # To be implemented: When images for different execution types are created, implement this logic, that would
        # search for available container that is capable of running this type of executable.
        pass

    def __copy_to_container(self, container_id: str, source_path: str, destination_path: str) -> None:
        # To be implemented: Copy source file from host file path to the container.
        pass

    def __execute_with_param(self, docker_executable: str, input_params: str) -> None:
        # To be implemented: Runs executable in the container with given input parameters
        pass
