import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Dict, Iterable, List, Optional, Union

from httpx import Response

from scrapework.core.collector import JobCollector, MetadataCollector
from scrapework.core.config import EnvConfig
from scrapework.core.context import Context
from scrapework.core.logger import Logger
from scrapework.handlers import Handler
from scrapework.middleware import RequestMiddleware
from scrapework.module import Module
from scrapework.parsers import HTMLBodyParser
from scrapework.reporter import LoggerReporter, Reporter
from scrapework.request import Request


# Class to handle url associated with a parser callback, using the default parser if none is provided
@dataclass
class ExtractCallback:
    url: str
    extract: Callable[
        [Context, Response], Union[Dict[str, Any], Iterable[Dict[str, Any]]]
    ]


class Scraper(ABC):
    """Scraper base class"""

    name: ClassVar[str] = "base_scraper"
    start_urls: List[str] = []
    visited_urls: List[str] = []
    urls_to_visit: List[ExtractCallback] = []
    base_url: str = ""
    filename: str = ""
    callback: Optional[
        Callable[[Context, Response], Union[Dict[str, Any], Iterable[Dict[str, Any]]]]
    ] = None

    handlers: List[Handler] = []
    middlewares: List[RequestMiddleware] = []
    reporters: List[Reporter] = []

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

    def use_modules(self) -> List[Module]:
        return [LoggerReporter()]

    def configuration(self) -> None:

        for module in self.use_modules():
            self.use(module)

    def use(self, module: Module) -> None:
        match module:
            case RequestMiddleware():
                self.middlewares.append(module)
            case Handler():
                self.handlers.append(module)
            case Reporter():
                self.reporters.append(module)

    @abstractmethod
    def extract(
        self, ctx: Context, response: Response
    ) -> Union[Dict[str, Any], Iterable[Dict[str, Any]]]:
        HTMLBodyParser().extract(response)

    def variables(self):
        return {
            "name": self.name,
        }

    def to_visit(
        self, url: str, extract: Optional[Callable] = None, force=False
    ) -> None:
        if url in self.visited_urls and not force:
            return

        if not extract:
            extract = self.extract

        self.urls_to_visit.append(ExtractCallback(url, extract))

    def run(self):
        self.logger.info("Scraping started")
        ctx = Context(
            variables=self.variables(),
            collector=MetadataCollector(),
        )

        if not self.start_urls:
            raise ValueError("No start_urls provided")

        for url in self.start_urls:
            self.to_visit(url)

        items = []

        begin_time = datetime.datetime.now()
        while self.urls_to_visit:
            iter_begin_time = datetime.datetime.now()
            url_with_callback = self.urls_to_visit.pop(0)

            response = self.make_request(ctx, url_with_callback.url)

            if not response:
                raise ValueError("Request failed")

            if response.status_code != 200:
                raise ValueError(
                    f"Request failed with status code {response.status_code}"
                )

            self.visited_urls.append(url_with_callback.url)

            new_items = list(url_with_callback.extract(ctx, response))
            items += new_items

            iter_end_time = datetime.datetime.now()
            items_count = len(items)
            ctx.collector.set("items_count", items_count)
            ctx.collector.jobs.append(
                JobCollector(
                    url=url_with_callback.url,
                    duration=iter_end_time - iter_begin_time,
                    items_count=len(new_items),
                )
            )

        for handler in self.handlers:
            handler.process_items(ctx, items)

        end_time = datetime.datetime.now()

        ctx.collector.set("duration", end_time - begin_time)
        self.logger.info("Scraping complete")

        for reporter in self.reporters:
            reporter.report(ctx)

    def make_request(self, ctx: Context, url: str) -> Optional[Response]:
        request = Request(url=url, logger=self.logger)

        self.logger.info(f"Making request to {url}")

        for middleware in self.middlewares:
            request = middleware.process_request(ctx, request)

        response = request.fetch()

        self.logger.info(f"Received response with status code {response.status_code}")

        return response
