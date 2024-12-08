from abc import ABC, abstractmethod
from typing import override

from evaluator.executor import IExecutor, ExecutorType
from grader import IGrader, GradingStrategy, GraderFactory
from logger.stos_logger import ISTOSLogger, STOSLogger


class IEvaluator(ABC):

    # Runs process of executable file evaluation based on expected result from given output
    @abstractmethod
    def evaluate_solution(self, executable_path: str, input_data_path: str, mode: ExecutorType,
                          expected_output_file_path: str, grading_strategy: GradingStrategy) -> list[tuple[bool, str]]:
        pass

    # Evaluates singular test and returns its grade and message
    @abstractmethod
    def evaluate_singular(self, result: str, expected_result: str, grader: IGrader) -> (bool, str):
        pass


class Evaluator(IEvaluator):

    __stos_logger: ISTOSLogger = STOSLogger("evaluator")
    __executor: IExecutor

    def __init__(self, executor: IExecutor):
        self.__executor = executor

    @override
    def evaluate_solution(self, executable_path: str, input_data_path: str, mode: ExecutorType,
                          expected_output_file_path: str, grading_strategy: GradingStrategy) -> list[tuple[bool, str]]:
        self.__executor.run_executor(executable_path, input_data_path, mode)
        output: str = self.__executor.read_output()
        parsed_output: list[str] = self.__output_parser(output)
        parsed_expected_output: list[str] = self.__expected_output_file_parser(expected_output_file_path)
        grader = GraderFactory.get_grader(grading_strategy)

        results = []
        for result, expected in zip(parsed_output, parsed_expected_output):
            results.append(self.evaluate_singular(result, expected, grader))
        return results

    @override
    def evaluate_singular(self, result: str, expected_result: str, grader: IGrader) -> (bool, str):
        split_output_values = result.split(",")
        output, execution_time = split_output_values[0], split_output_values[1]
        split_expected_output_values = expected_result.split(",")
        expected_output, expected_execution_time = split_expected_output_values[0], split_expected_output_values[1]

        return grader.grade(output, expected_output,
                            execution_time=execution_time,
                            max_execution_time=expected_execution_time)

    def __output_parser(self, result: str) -> list[str]:
        return result.split('\n')

    def __expected_output_file_parser(self, expected_result_file: str) -> list[str]:
        with open(expected_result_file, "r") as f:
            return f.read().split('\n')
