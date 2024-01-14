import json
import requests
from typing import List
from pydantic import BaseModel
from pydantic import ValidationError
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


class Perform:
    def __init__(self, name: str, path: str, method: str):
        self.path = path
        self.method = method
        self.name = name


class PerformResult:
    def __init__(self, response: Response):
        self.data = json.loads(response.text)
        self.http_code = response.status_code
        self.headers = response.headers


class Call:
    def __init__(self, base_url: str, **kwargs):
        if not all(key in kwargs for key in ["connection", "size", "retry"]):
            raise Exception("connection, size and retry should be inside keyword argument")
        self.__base_url = base_url
        self.__connection = kwargs["connection"]
        self.__size = kwargs["size"]
        self.__retry = kwargs["retry"]
        adapter_config = (self.__connection, self.__size, self.__retry)
        self.adapter = self.__create_http_adapter(*adapter_config)
        self.session = requests.Session()
        self.session.mount("http://", self.adapter)
        self.session.mount("https://", self.adapter)
        self.apis: List[Perform] = []

    def __create_http_adapter(self, connection: int, size: int, retry: int) -> HTTPAdapter:
        return HTTPAdapter(
            pool_connections=connection,
            pool_maxsize=size,
            max_retries=Retry(
                total=retry,
                backoff_factor=0.5,
            ))

    def add_header(self, header: dict):
        self.session.headers.update(header)

    def add_api(self, perform: Perform):
        self.apis.append(perform)

    def execute(self, name: str, request: BaseModel) -> PerformResult | str:
        try:
            selected_api = [api for api in self.apis if api.name == name][0]
            path = selected_api.path
            method = selected_api.method
            complete_url = f"{self.__base_url}{path}" if self.__base_url else path
            request_dumped = request.model_dump()
            header_data = request_dumped["headers"]
            if header_data:
                self.session.headers.update(header_data)
                del request_dumped["headers"]
            result = self.session.request(method, complete_url, json=request_dumped)
            return PerformResult(result)
        except IndexError as e:
            return f"Index error API not registered: {str(e)}"
        except TimeoutError as e:
            return f"Calling API timeout: {str(e)}"
        except json.JSONDecodeError as e:
            return f"Response malformed: {str(e)}"
        except ValidationError as e:
            return f"Response invalid: {str(e)}"
        except Exception as e:
            return f"Unknown exception occurred: {str(e)}"
