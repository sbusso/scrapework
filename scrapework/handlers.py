import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Union

import boto3
from pydantic import Field

from scrapework.core.logger import Logger


class Handler(ABC):
    logger: logging.Logger

    def __init__(self) -> None:
        self.logger = Logger().get_logger()
        self.logger.info(f"Using handler: {self.__class__.__name__}")

    @abstractmethod
    def process_items(
        self,
        items: Union[Dict[str, Any], Iterable[Dict[str, Any]]],
    ):
        pass


class JsonFileHandler(Handler):
    filename: str

    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename

    def process_items(self, items: Union[Dict[str, Any], Iterable[Dict[str, Any]]]):

        with open(self.filename, "w") as f:
            json.dump(items, f)
        self.logger.info(f"Items written to {self.filename}")


class S3Handler(Handler):
    s3_bucket: str = Field(default_factory=str)
    filename: str

    def __init__(self, s3_bucket: str, filename: str):
        super().__init__()
        self.s3_bucket = s3_bucket
        self.filename = filename

    def process_items(self, items: Union[Dict[str, Any], Iterable[Dict[str, Any]]]):

        s3_client = boto3.client("s3")

        s3_client.put_object(
            Body=json.dumps(items), Bucket=self.s3_bucket, Key=self.filename
        )


class MetadataHandler(Handler):
    def process_items(self, items: Union[Dict[str, Any], Iterable[Dict[str, Any]]]):
        if isinstance(items, dict):
            self.logger.info("Items count: 1")
            return {"items_count": 1}
        else:
            self.logger.info(f"Items count: {len(list(items))}")
            return {"items_count": len(list(items))}
