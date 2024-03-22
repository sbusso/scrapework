from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Iterator, List, Optional, Union

import requests

from scrapework.config import SpiderConfig
from scrapework.pipelines import ItemPipeline


class Spider(ABC):
    name: str = "base_spider"
    start_urls: List[str] = []

    def __init__(self, config: SpiderConfig):
        self.config = config
        self.pipeline = ItemPipeline()

    def start_requests(self) -> Iterator[requests.Response]:
        for url in self.start_urls:
            yield requests.get(url)

    def _generate_urls(self) -> Iterator[str]:
        for url in self.start_urls:
            yield url

    @abstractmethod
    def parse(self, response) -> Union[Dict[str, Any], Iterable[Dict[str, Any]]]:
        raise NotImplementedError

    def run(self):
        for url in self.start_urls:
            response = self.make_request(url)

            if not response:
                raise ValueError("Request failed")

            if response.status_code != 200:
                raise ValueError(
                    f"Request failed with status code {response.status_code}"
                )

            items = self.parse(response)

            self.pipeline.process_items(items, self.config)

    @staticmethod
    def make_request(url: str) -> Optional[requests.Response]:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0"})
        response = session.get(url)

        return response
