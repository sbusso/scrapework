from abc import ABC, abstractmethod
from random import choice
from typing import List
from urllib.parse import urlencode

from scrapework.context import Context
from scrapework.request import Request


class Proxy:
    url: str

    def __init__(self, url: str):
        if not url.startswith("http"):
            raise ValueError("Proxy URL must start with http")

        self.url = url


class Middleware(ABC):
    context: Context

    def __init__(self, context: Context) -> None:
        self.context = context
        self.context.logger.info(f"Using middleware: {self.__class__.__name__}")

    @abstractmethod
    def process_request(self, request: Request):
        raise NotImplementedError


class MiddlewareAnonymousHeader(Middleware):
    def process_request(self, request: Request):
        request.headers.update({"User-Agent": "Anonymous"})
        return request


class MiddlewareDefaultHeaders(Middleware):
    def process_request(self, request: Request):
        request.headers.update({"User-Agent": "Mozilla/5.0"})
        return request


class MiddlewareLogging(Middleware):
    def process_request(self, request: Request):
        print(f"Making request to {request.url}")
        return request


class MiddlewareProxy(Middleware):
    proxy: Proxy

    def __init__(self, proxy: Proxy):
        self.proxy = proxy

    def process_request(self, request: Request):
        if self.proxy:
            request.proxy = self.proxy.url

        return request


class MiddlewareScrapeOps(Middleware):
    api_key: str

    def __init__(self, api_key: str):
        self.api_key = api_key

    def process_request(self, request: Request):

        payload = {"api_key": self.api_key, "url": request.url}
        request.proxy = "https://proxy.scrapeops.io/v1/" + urlencode(payload)

        return request


class ProxyRotationMiddleware(Middleware):
    proxies: List[Proxy]  # "http://Username:Password@85.237.57.198:20000",

    def __init__(self, proxies: List[Proxy]):
        self.proxies = proxies

    def process_request(self, request: Request):
        proxy = choice(self.proxies)
        request.proxy = proxy.url
        return request
