from abc import ABC, abstractmethod
from typing import override


class IApiDriver(ABC):

    @staticmethod
    @abstractmethod
    def fetch_tasks():
        pass

    @staticmethod
    @abstractmethod
    def download_file():
        pass

    @staticmethod
    @abstractmethod
    def upload_results():
        pass


class STOSApiDriver(IApiDriver):

    @override
    @staticmethod
    def fetch_tasks():
        pass

    @override
    @staticmethod
    def download_file():
        pass

    @override
    @staticmethod
    def upload_results():
        pass




