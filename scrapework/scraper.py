import datetime
from abc import ABC
from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Dict, Iterable, List, Optional, Union

from httpx import Response
from parsel import Selector

from scrapework.core.collector import JobCollector, MetadataCollector
from scrapework.core.context import Context
from scrapework.core.logger import Logger
from scrapework.handlers import Handler
from scrapework.middleware import RequestMiddleware
from scrapework.module import Module
from scrapework.parsers import Parser
from scrapework.reporter import LoggerReporter, Reporter
from scrapework.request import Request


# Class to handle url associated with a parser callback, using the default parser if none is provided
@dataclass
class ExtractCallback:
    url: str
    extract: Callable[
        [Context, Selector], Union[Dict[str, Any], Iterable[Dict[str, Any]]]
    ]


class Scraper(ABC):
    """Scraper base class"""

    name: ClassVar[str] = "base_scraper"
    # start_urls: List[str] = []
    visited_urls: List[str] = []
    urls_to_visit: List[ExtractCallback] = []
    base_url: str = ""
    filename: str = ""
    callback: Optional[
        Callable[[Context, Response], Union[Dict[str, Any], Iterable[Dict[str, Any]]]]
    ] = None

    parser: Parser = Parser()

    handlers: List[Handler] = []
    middlewares: List[RequestMiddleware] = []
    reporters: List[Reporter] = []

    modules: List[Module] = [LoggerReporter()]

    def __init__(self, **args):

        if not self.__class__.name:
            raise ValueError("Subclass must provide a name attribute")

        if not self.filename:
            self.filename = f"{self.name}.json"

        self.logger = Logger(self.name).get_logger()

        self.configuration()

    def use_modules(self) -> List[Module]:
        return []

    def configuration(self) -> None:

        for module in [*self.modules, *self.use_modules()]:
            self.use(module)

    def variables(self):
        return {
            "name": self.name,
        }

    def use(self, module: Module | List[Module]) -> None:
        if isinstance(module, list):
            for m in module:
                self.use(m)
        match module:
            case RequestMiddleware():
                self.middlewares.append(module)
            case Handler():
                self.handlers.append(module)
            case Reporter():
                self.reporters.append(module)

    def build_start_urls(self, input) -> List[str]:
        return []

    def extract(
        self, ctx: Context, selector: Selector
    ) -> Union[Dict[str, Any], Iterable[Dict[str, Any]]]:
        return self.parser.extract(ctx, selector)

    def process(
        self, ctx: Context, items: Union[Dict[str, Any], Iterable[Dict[str, Any]]]
    ):
        for handler in self.handlers:
            handler.process_items(ctx, items)

    def report(self, ctx: Context):
        for reporter in self.reporters:
            reporter.report(ctx)

    def run(self, start_urls: Optional[List[str]] = None, input: Optional[Any] = None):
        self.logger.info("Scraping started")

        if not start_urls and not input:
            raise ValueError("Either start_urls or input must be provided")

        start_urls = start_urls or []

        if input:
            start_urls += self.build_start_urls(input)

        for url in start_urls:
            self.to_visit(url)

        ctx = Context(
            variables=self.variables(),
            collector=MetadataCollector(),
        )

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

            new_items = url_with_callback.extract(ctx, Selector(response.text))

            # TODO: self.process(ctx, new_items)

            # append new_items to items, Items can be a list or a dict
            if isinstance(new_items, dict):
                items.append(new_items)
            else:
                items += new_items

            iter_end_time = datetime.datetime.now()
            items_count = len(items)
            ctx.collector.set("items_count", items_count)
            ctx.collector.jobs.append(
                JobCollector(
                    url=url_with_callback.url,
                    duration=iter_end_time - iter_begin_time,
                    items_count=len(list(new_items)),
                )
            )

        self.process(ctx, items)

        end_time = datetime.datetime.now()

        ctx.collector.set("duration", end_time - begin_time)
        self.logger.info("Scraping complete")

        self.report(ctx)

    def to_visit(
        self, url: str, extract: Optional[Callable] = None, force=False
    ) -> None:
        if url in self.visited_urls and not force:
            return

        if not extract:
            extract = self.extract

        self.urls_to_visit.append(ExtractCallback(url, extract))

    def make_request(self, ctx: Context, url: str) -> Optional[Response]:
        request = Request(url=url, logger=self.logger)

        self.logger.info(f"Making request to {url}")

        for middleware in self.middlewares:
            request = middleware.process_request(ctx, request)

        response = request.fetch()

        self.logger.info(f"Received response with status code {response.status_code}")

        ctx.response = response
        ctx.request = request

        return response
