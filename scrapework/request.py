import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

import httpx
from httpx import HTTPError, TimeoutException


class HTTPClient(ABC):

    @classmethod
    @abstractmethod
    def build_client(cls, **kwargs) -> httpx.Client:
        pass


class HttpxClient(HTTPClient):
    @classmethod
    def build_client(cls, **kwargs) -> httpx.Client:
        return httpx.Client(**kwargs)


class Request:
    url: str
    logger: logging.Logger
    headers: Dict[str, str] = {}
    timeout: int = 10
    follow_redirects: bool = False
    proxy: str | None = None
    retries: int = 0
    cls_client: type[HTTPClient] = HttpxClient
    client_kwargs: Dict[str, Any] = {}

    def __init__(self, url: str, **kwargs):
        self.url = url
        self.logger = kwargs.get("logger", logging.getLogger("request"))
        self.headers = kwargs.get("headers", {})
        self.timeout = kwargs.get("timeout", 10)
        self.follow_redirects = kwargs.get("follow_redirects", False)
        self.proxy = kwargs.get("proxy", None)
        self.retries = kwargs.get("retries", 0)
        self.cls_client = kwargs.get("cls_client", HttpxClient)
        self.client_kwargs = kwargs.get("client_kwargs", {})

    class Config:
        arbitrary_types_allowed = True

    def fetch(self) -> httpx.Response:
        """
        Fetches the HTML content of a given URL.

        :param cache: The cache object used for caching the fetched HTML content.
        :param url: The URL to fetch.

        :return: The fetched HTML content as a string, or None if there was an error.
        """
        if self.proxy:
            mounts = {
                "https://": httpx.HTTPTransport(proxy=self.proxy),
                "http://": httpx.HTTPTransport(proxy=self.proxy),
            }
        else:
            mounts = {}
        client = self.cls_client.build_client(
            headers=self.headers,
            timeout=self.timeout,
            follow_redirects=self.follow_redirects,
            mounts=mounts,
            **self.client_kwargs,
        )
        try:

            request = client.build_request(
                "GET",
                self.url,
            )

            response = client.send(
                request,
            )

            return response

        except TimeoutException as err:
            self.logger.error(f"TimeoutError fetching {self.url}: {err}")  # type: ignore
            raise err

        except HTTPError as err:
            self.logger.error(f"HTTPError fetching {self.url}: {err}")  # type: ignore
            raise err

        except Exception as err:
            self.logger.error(f"Exception fetching {self.url}: {err}")  # type: ignore
            raise err

        finally:
            client.close()
