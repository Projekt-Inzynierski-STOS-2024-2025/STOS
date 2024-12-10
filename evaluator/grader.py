from abc import ABC, abstractmethod
from enum import Enum
from typing import override


class IGrader(ABC):

    # Grades given result based on expected result
    @abstractmethod
    def grade(self, result: str, expected_result: str, **kwargs) -> (bool, str):
        pass


class GradingStrategy(Enum):
    DEFAULT_STRATEGY = 0
    IGNORE_TIMEOUT_STRATEGY = 1
    DELTA_ERROR_STRATEGY = 2


class GraderFactory:

    @staticmethod
    def get_grader(strategy: GradingStrategy) -> IGrader:
        if strategy == GradingStrategy.DEFAULT_STRATEGY:
            return DefaultGrader()
        elif strategy == GradingStrategy.IGNORE_TIMEOUT_STRATEGY:
            return IgnoreTimeoutGrader()
        elif strategy == GradingStrategy.DELTA_ERROR_STRATEGY:
            return DeltaErrorGrader()


class DefaultGrader(IGrader):

    @override
    def grade(self, result: str, expected_result: str, **kwargs) -> (bool, str):
        max_execution_time = kwargs.get('max_execution_time', 1)
        if kwargs.get('execution_time', 0) > max_execution_time:
            return False, f"timeout, max={max_execution_time}"
        if result != expected_result:
            return False, f"incorrect output. got {result}, expected {expected_result}"
        return True, "success"


class IgnoreTimeoutGrader(IGrader):

    @override
    def grade(self, result: str, expected_result: str, **kwargs) -> (bool, str):
        if result != expected_result:
            return False, f"incorrect output. got {result}, expected {expected_result}"
        return True, "success"


class DeltaErrorGrader(IGrader):

    @override
    def grade(self, result: str, expected_result: str, **kwargs) -> (bool, str):
        delta_error: float = kwargs.get('delta_error', 1.0)
        try:
            float(result)
            float(expected_result)
        except ValueError:
            return False, f"cannot cast {result} or {expected_result} to float"
        min_allowed_value: float = float(expected_result) * (1.0 - delta_error)
        max_allowed_value: float = float(expected_result) * (1.0 + delta_error)

        if not min_allowed_value < float(result) < max_allowed_value:
            return False, f"result {result} not in range ({min_allowed_value}, {max_allowed_value})"
        return True, "success"
