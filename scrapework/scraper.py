from abc import ABC, abstractmethod
from typing import Any, Callable, ClassVar, Dict, Iterable, List, Optional, Union

from httpx import Response

from scrapework.config import EnvConfig
from scrapework.context import Context
from scrapework.extractors import BodyExtractor
from scrapework.logger import new_logger
from scrapework.middleware import Middleware
from scrapework.pipelines import Pipeline
from scrapework.request import Request


class Scraper(ABC):
    name: ClassVar[str] = "base_scraper"
    start_urls: List[str] = []
    pipelines: List[Pipeline] = []
    base_url: str = ""
    filename: str = ""
    callback: Optional[
        Callable[[Response], Union[Dict[str, Any], Iterable[Dict[str, Any]]]]
    ] = None
    middlewares: List[Middleware] = []
    context: Optional[Context] = None
    config: EnvConfig

    def __init__(self, **args):

        if not self.__class__.name:
            raise ValueError("Subclass must provide a name attribute")

        self.config = self.SpiderConfig.create_config()

        if not self.base_url and self.start_urls:
            self.base_url = self.start_urls[0]

        if not self.filename:
            self.filename = f"{self.name}.json"

        # start_urls
        args_start_urls = args.get("start_urls")
        if args_start_urls and isinstance(args_start_urls, list):
            self.start_urls = args_start_urls

        self.logger = new_logger(self.name)

        self.context = Context(logger=self.logger, filename=self.filename)

    class SpiderConfig(EnvConfig):
        pass

    class Config:
        arbitrary_types_allowed = True

    def use(self, cls: type[Middleware], **kwargs) -> None:
        cls_instance = cls(context=self.context, **kwargs)  # type: ignore
        self.middlewares.append(cls_instance)

    @abstractmethod
    def extract(self, response) -> Union[Dict[str, Any], Iterable[Dict[str, Any]]]:
        BodyExtractor().extract(response)

    def run(self):
        if not self.context:
            raise ValueError("Context not defined")
        for url in self.start_urls:
            response = self.make_request(url)

            if not response:
                raise ValueError("Request failed")

            if response.status_code != 200:
                raise ValueError(
                    f"Request failed with status code {response.status_code}"
                )

            items = self.extract(response)

            if items is None:
                raise ValueError("Items not returned")

            for pipeline in self.pipelines:
                pipeline.process_items(items, self.context)
        self.logger.info("Scraping complete")

    def make_request(self, url: str) -> Optional[Response]:
        request = Request(url=url, logger=self.logger)

        self.logger.info(f"Making request to {url}")

        for middleware in self.middlewares:
            request = middleware.process_request(request)

        response = request.fetch()

        self.logger.info(f"Received response with status code {response.status_code}")

        return response
