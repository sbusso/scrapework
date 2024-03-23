import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, ClassVar, Dict, Iterable, List, Optional, Union

import requests
from pydantic import BaseModel, Field

from scrapework.config import EnvConfig
from scrapework.extractors import Extractor
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
        self.callback = self.parse
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
    def parse(self, response) -> Union[Dict[str, Any], Iterable[Dict[str, Any]]]:
        Extractor().extract_body(response)

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
