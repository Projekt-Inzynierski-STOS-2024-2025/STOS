from abc import ABC, abstractmethod
from typing import override
import requests
from manager.types import StosTaskResponse
from os import environ 

class IApiDriver(ABC):

    @staticmethod
    @abstractmethod
    def fetch_tasks() -> StosTaskResponse:
        pass

    @staticmethod
    @abstractmethod
    def download_file(id: str) -> str:
        pass

    @staticmethod
    @abstractmethod
    def upload_results(id: str) -> None:
        pass


class STOSApiDriver(IApiDriver):

    __api_port: str = environ.get('STOS_PORT', '2137')
    __api_url: str = f"http://{environ.get('STOS_HOST', '127.0.0.1')}:{__api_port}"

    @override
    @staticmethod
    def fetch_tasks() -> StosTaskResponse:
        response = requests.get(STOSApiDriver.__api_url + '/tasks' )
        response.raise_for_status()  # Raise an error for bad status codes
        return StosTaskResponse.from_json(response.text)

    @override
    @staticmethod
    def download_file(id: str) -> str:
        response = requests.get(STOSApiDriver.__api_url + "/files/" + id)
        response.raise_for_status()
        return response.text

    @override
    @staticmethod
    def upload_results(id: str) -> None:
        response = requests.post(STOSApiDriver.__api_url +  '/tasks/' + id)
        response.raise_for_status()       
        return
