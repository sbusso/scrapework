import logging
from abc import ABC, abstractmethod
from random import choice
from typing import List
from urllib.parse import urlencode

from scrapework.core.context import Context
from scrapework.core.logger import Logger
from scrapework.request import Request


class Proxy:
    url: str

    def __init__(self, url: str):
        if not url.startswith("http"):
            raise ValueError("Proxy URL must start with http")

        self.url = url


class RequestMiddleware(ABC):
    logger: logging.Logger

    def __init__(self) -> None:
        self.logger = Logger().get_logger()
        self.logger.info(f"Using middleware: {self.__class__.__name__}")

    @abstractmethod
    def process_request(self, request: Request):
        raise NotImplementedError


class AnonymousHeaderMiddleware(RequestMiddleware):
    def process_request(self, request: Request):
        request.headers.update({"User-Agent": "Anonymous"})
        return request


class DefaultHeadersMiddleware(RequestMiddleware):
    def process_request(self, request: Request):
        request.headers.update({"User-Agent": "Mozilla/5.0"})
        return request


class LoggingMiddleware(RequestMiddleware):
    def process_request(self, request: Request):
        self.logger.info(f"Making request to {request.url}")
        return request


class ProxyMiddleware(RequestMiddleware):
    proxy: Proxy

    def __init__(self, context: Context, proxy: Proxy):
        super().__init__()
        self.proxy = proxy

    def process_request(self, request: Request):
        if self.proxy:
            request.proxy = self.proxy.url

        return request


class ScrapeOpsMiddleware(RequestMiddleware):
    api_key: str

    def __init__(self, context: Context, api_key: str):
        super().__init__()
        self.api_key = api_key

    def process_request(self, request: Request):

        payload = {"api_key": self.api_key, "url": request.url}
        request.proxy = "https://proxy.scrapeops.io/v1/" + urlencode(payload)

        return request


class ProxyRotationMiddleware(RequestMiddleware):
    proxies: List[Proxy]  # "http://Username:Password@85.237.57.198:20000",

    def __init__(self, context: Context, proxies: List[Proxy]):
        super().__init__()
        self.proxies = proxies

    def process_request(self, request: Request):
        proxy = choice(self.proxies)
        request.proxy = proxy.url
        return request
