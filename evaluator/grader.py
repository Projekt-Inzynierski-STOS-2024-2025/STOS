from abc import ABC, abstractmethod
from enum import Enum
from typing import override


class IGrader(ABC):

    # Grades given result based on expected result
    @abstractmethod
    def grade(self, result: str, expected_result: str, **kwargs) -> bool:
        pass


class GradingStrategy(Enum):
    DEFAULT_STRATEGY = 0
    IGNORE_TIMEOUT_STRATEGY = 1


class GraderFactory:
    @staticmethod
    def get_grader(strategy: GradingStrategy) -> IGrader:
        if strategy == GradingStrategy.DEFAULT_STRATEGY:
            return DefaultGrader()
        elif strategy == GradingStrategy.IGNORE_TIMEOUT_STRATEGY:
            return IgnoreTimeoutGrader()


class DefaultGrader(IGrader):
    @override
    def grade(self, result: str, expected_result: str, **kwargs) -> bool:
        if kwargs['execution_time'] > kwargs['max_execution_time']:
            return False
        if result != expected_result:
            return False
        return True


class IgnoreTimeoutGrader(IGrader):
    @override
    def grade(self, result: str, expected_result: str, **kwargs) -> bool:
        if result != expected_result:
            return False
        return True
