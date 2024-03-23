from abc import abstractmethod
from random import choice
from typing import List
from urllib.parse import urlencode

import requests
from pydantic import BaseModel


class Proxy(BaseModel):
    url: str

    def validate(self, value):
        if not value.startswith("http"):
            raise ValueError("Proxy url must start with http")
        return value


class Middleware(BaseModel):
    @abstractmethod
    def process_request(self, request):
        raise NotImplementedError


class MiddlewareAnonymousHeader(Middleware):
    def process_request(self, request):
        request.headers.update({"User-Agent": "Anonymous"})
        return request


class MiddlewareDefaultHeaders(Middleware):
    def process_request(self, request):
        request.headers.update({"User-Agent": "Mozilla/5.0"})
        return request


class MiddlewareLogging(Middleware):
    def process_request(self, request):
        print(f"Making request to {request.url}")
        return request


class MiddlewareProxy(Middleware):
    proxy: Proxy

    def process_request(self, request):
        if self.proxy:
            request.proxies = self.proxy.url

        return request


class MiddlewareScrapeOps(Middleware):
    api_key: str

    def process_request(self, request):

        payload = {"api_key": self.api_key, "url": request.url}
        request = requests.get(
            "https://proxy.scrapeops.io/v1/", params=urlencode(payload)
        )
        return request


class ProxyRotationMiddleware(Middleware):
    proxies: List[Proxy]  # "http://Username:Password@85.237.57.198:20000",

    def process_request(self, request):
        proxy = choice(self.proxies)
        request.proxies = {
            "http": proxy.url,
            "https": proxy.url,
        }
        return request
