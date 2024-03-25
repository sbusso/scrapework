from abc import ABC, abstractmethod
from typing import Any, Callable, ClassVar, Dict, Iterable, List, Optional, Union

from httpx import Response

from scrapework.core.config import EnvConfig
from scrapework.core.logger import Logger
from scrapework.handlers import Handler
from scrapework.parsers import HTMLBodyParser
from scrapework.request import Request
from scrapework.request_middleware import RequestMiddleware


class Scraper(ABC):
    """Scraper base class"""

    name: ClassVar[str] = "base_scraper"
    start_urls: List[str] = []
    base_url: str = ""
    filename: str = ""
    callback: Optional[
        Callable[[Response], Union[Dict[str, Any], Iterable[Dict[str, Any]]]]
    ] = None

    handlers: List[Handler] = []
    middlewares: List[RequestMiddleware] = []

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

        self.logger = Logger(self.name).get_logger()

        self.configuration()

    class SpiderConfig(EnvConfig):
        pass

    class Config:
        arbitrary_types_allowed = True

    def configuration(self):
        pass

    def use(self, module: RequestMiddleware | Handler) -> None:
        if isinstance(module, RequestMiddleware):
            self.middlewares.append(module)
        elif isinstance(module, Handler):
            self.handlers.append(module)

    @abstractmethod
    def extract(self, response) -> Union[Dict[str, Any], Iterable[Dict[str, Any]]]:
        HTMLBodyParser().extract(response)

    def run(self):
        for url in self.start_urls:
            # Load
            response = self.make_request(url)

            if not response:
                raise ValueError("Request failed")

            if response.status_code != 200:
                raise ValueError(
                    f"Request failed with status code {response.status_code}"
                )
            # Extract
            items = self.extract(response)

            if items is None:
                raise ValueError("Items not returned")

            # Process
            for handler in self.handlers:
                handler.process_items(items)
        self.logger.info("Scraping complete")

    def make_request(self, url: str) -> Optional[Response]:
        request = Request(url=url, logger=self.logger)

        self.logger.info(f"Making request to {url}")

        for middleware in self.middlewares:
            request = middleware.process_request(request)

        response = request.fetch()

        self.logger.info(f"Received response with status code {response.status_code}")

        return response
