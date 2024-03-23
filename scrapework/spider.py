import logging
from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import Any, Callable, ClassVar, Dict, Iterable, List, Optional, Union

import requests
from pydantic import BaseModel, Field
from urllib3.exceptions import (
    HTTPError,
    MaxRetryError,
    TimeoutError,
)

from scrapework.config import EnvConfig
from scrapework.extractors import BodyExtractor
from scrapework.logger import logger
from scrapework.middleware import Middleware
from scrapework.pipelines import Pipeline


class Spider(BaseModel, ABC):
    name: ClassVar[str] = "base_spider"
    start_urls: List[str] = []
    pipelines: List[Pipeline] = []
    base_url: str = ""
    filename: str = ""
    callback: Optional[
        Callable[[requests.Response], Union[Dict[str, Any], Iterable[Dict[str, Any]]]]
    ] = None
    middlewares: List[Middleware] = []
    logger: ClassVar[logging.Logger] = logger
    config: EnvConfig = Field(default_factory=EnvConfig)

    def __init__(self, **args):

        if not self.__class__.name:
            raise ValueError("Subclass must provide a name attribute")
        super().__init__(**args)
        self.config = self.SpiderConfig.create_config()
        self.callback = self.extract
        if not self.base_url and self.start_urls:
            self.base_url = self.start_urls[0]

        if not self.filename:
            self.filename = f"{self.name}.json"

    class SpiderConfig(EnvConfig):
        pass

    class Config:
        arbitrary_types_allowed = True

    def use(self, middleware: Middleware):
        self.middlewares.append(middleware)

    @abstractmethod
    def extract(self, response) -> Union[Dict[str, Any], Iterable[Dict[str, Any]]]:
        BodyExtractor().extract(response)

    def run(self):
        for url in self.start_urls:
            response = self.make_request(url)

            if not response:
                raise ValueError("Request failed")

            if response.status_code != 200:
                raise ValueError(
                    f"Request failed with status code {response.status_code}"
                )

            if not self.callback:
                raise ValueError("Callback not defined")

            items = self.callback(response)

            if items is None:
                raise ValueError("Items not returned")

            for pipeline in self.pipelines:
                pipeline.process_items(items, self.filename)

    def make_request(self, url: str) -> Optional[requests.Response]:
        request = requests.Request("GET", url)

        self.logger.info(f"Making request to {url}")

        for middleware in self.middlewares:
            request = middleware.process_request(request)

        session = requests.Session()

        prepared_request = session.prepare_request(request)
        response = session.send(prepared_request)

        self.logger.info(f"Received response with status code {response.status_code}")

        return response

    def fetch(self, url):
        """
        Fetches the HTML content of a given URL.

        :param cache: The cache object used for caching the fetched HTML content.
        :param url: The URL to fetch.

        :return: The fetched HTML content as a string, or None if there was an error.
        """

        r = None

        try:
            self.logger.debug(f"fetching {url}")
            r = requests.get(str(url), timeout=10)

            if r is None:
                logger.error(f"Failed to fetch {url} returned NONE")
                return None
            if r.status_code != HTTPStatus.OK:
                logger.error(f"Failed to fetch {url} returned {r.status_code}")
                return None

            return r.text  # noqa: TRY300

        except MaxRetryError as err:
            logger.error(f"MaxRetryError fetching {url}")  # type: ignore
            raise err

        except TimeoutError as err:
            logger.error(f"TimeoutError fetching {url}: {err}")  # type: ignore
            raise err

        except HTTPError as err:
            logger.error(f"HTTPError fetching {url}: {err}")  # type: ignore
            raise err

        except Exception as err:
            logger.error(f"Exception fetching {url}: {err}")  # type: ignore
            raise err

        return None
