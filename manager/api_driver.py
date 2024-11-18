import logging
from abc import ABC, abstractmethod
from typing import override
import requests
from manager.types import StosTaskResponse
from os import environ
from logger.stos_logger import STOSLogger


class IApiDriver(ABC):

    # Downloads files of available task
    @staticmethod
    @abstractmethod
    def fetch_tasks() -> StosTaskResponse:
        pass

    # Uploads file of given id
    @staticmethod
    @abstractmethod
    def download_file(id: str) -> str:
        pass

    # Uploads score of a given task
    @staticmethod
    @abstractmethod
    def upload_results(id: str) -> None:
        pass


class STOSApiDriver(IApiDriver):

    __stos_logger: logging.Logger = STOSLogger("stos_api_driver")

    __api_port: str = environ.get('STOS_PORT', '2137')
    __api_url: str = f"http://{environ.get('STOS_HOST', '127.0.0.1')}:{__api_port}"

    @staticmethod
    @override
    def fetch_tasks() -> StosTaskResponse:
        response = requests.get(STOSApiDriver.__api_url + '/tasks')
        response.raise_for_status()  # Raise an error for bad status codes
        parsed_response: StosTaskResponse = StosTaskResponse.from_json(response.text)
        STOSApiDriver.__stos_logger.debug(f"Successfully downloaded task {parsed_response.task_id}")
        return parsed_response

    @staticmethod
    @override
    def download_file(id: str) -> str:
        response = requests.get(STOSApiDriver.__api_url + "/files/" + id)
        response.raise_for_status()
        STOSApiDriver.__stos_logger.debug(f"Successfully downloaded file {id}")
        return response.text

    @staticmethod
    @override
    def upload_results(id: str) -> None:
        response = requests.post(STOSApiDriver.__api_url + '/tasks/' + id)
        response.raise_for_status()
        STOSApiDriver.__stos_logger.debug(f"Successfully uploaded result of task {id}")
