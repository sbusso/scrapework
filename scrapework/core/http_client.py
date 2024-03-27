from abc import ABC, abstractmethod

import httpx

from scrapework.core.logger import Logger


class HTTPClient(ABC):

    @classmethod
    @abstractmethod
    def build_client(cls, **kwargs) -> httpx.Client:
        pass


class HttpxClient(HTTPClient):
    @classmethod
    def build_client(cls, **kwargs) -> httpx.Client:
        Logger().get_logger().debug("Building httpx client")
        return httpx.Client(**kwargs)
