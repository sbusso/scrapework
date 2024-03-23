import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, ClassVar, Dict, Iterable, List, Optional, Union

import requests
from pydantic import BaseModel

from scrapework.config import BackendType, PipelineConfig
from scrapework.extractors import Extractor
from scrapework.logger import logger
from scrapework.middleware import Middleware
from scrapework.pipelines import ItemPipeline


class Spider(BaseModel, ABC):
    name: ClassVar[str] = "base_spider"
    start_urls: List[str] = []
    pipeline: Optional[ItemPipeline] = None
    base_url: str = ""
    backend: BackendType = BackendType.FILE
    s3_bucket: str = ""
    filename: str = ""
    callback: Optional[
        Callable[[requests.Response], Union[Dict[str, Any], Iterable[Dict[str, Any]]]]
    ] = None
    middlewares: List[Middleware] = []
    logger: ClassVar[logging.Logger] = logger

    def __init__(self, **args):

        if not self.__class__.name:
            raise ValueError("Subclass must provide a name attribute")
        super().__init__(**args)
        self.callback = self.parse
        if not self.base_url and self.start_urls:
            self.base_url = self.start_urls[0]
        if not self.s3_bucket:
            self.s3_bucket = self.name
        if not self.filename:
            self.filename = f"{self.name}.json"
        if not self.pipeline:
            self.pipeline = ItemPipeline()

    class Config:
        arbitrary_types_allowed = True

    def use(self, middleware: Middleware):
        self.middlewares.append(middleware)

    @abstractmethod
    def parse(self, response) -> Union[Dict[str, Any], Iterable[Dict[str, Any]]]:
        Extractor().extract_body(response)

    @property
    def pipeline_config(self) -> PipelineConfig:
        return PipelineConfig(
            base_url=self.base_url,
            backend=self.backend,
            s3_bucket=self.s3_bucket,
            filename=self.filename,
        )

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

            if not self.pipeline:
                raise ValueError("Pipeline not defined")

            self.pipeline.process_items(items, self.pipeline_config)

    def make_request(self, url: str) -> Optional[requests.Response]:
        request = requests.Request("GET", url)

        for middleware in self.middlewares:
            request = middleware.process_request(request)

        session = requests.Session()

        prepared_request = session.prepare_request(request)
        response = session.send(prepared_request)

        return response
