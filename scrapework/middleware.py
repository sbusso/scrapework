from abc import abstractmethod
from typing import List, Optional
from urllib.parse import urlencode

import requests
from pydantic import BaseModel


class Proxy(BaseModel):
    url: str


class Middleware(BaseModel):
    proxies: Optional[List[Proxy]] = None

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
    def process_request(self, request):
        if self.proxies:
            request.proxies = self.proxies

        return request


class MiddlewareScrapeOps(Middleware):
    api_key: str

    def process_request(self, request):

        payload = {"api_key": self.api_key, "url": request.url}
        request = requests.get(
            "https://proxy.scrapeops.io/v1/", params=urlencode(payload)
        )
        return request
