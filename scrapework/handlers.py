import json
import logging
from abc import abstractmethod
from typing import Any, Dict, Iterable, List, Union

import boto3
from pydantic import Field

from scrapework.core.context import Context
from scrapework.module import Module


class Handler(Module):
    logger: logging.Logger

    @abstractmethod
    def process_items(
        self,
        ctx: Context,
        items: Union[Dict[str, Any], List[Dict[str, Any]]],
    ):
        pass


class JsonFileHandler(Handler):
    filename: str

    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename

    def process_items(
        self, ctx: Context, items: Union[Dict[str, Any], Iterable[Dict[str, Any]]]
    ):

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

    def process_items(
        self, ctx: Context, items: Union[Dict[str, Any], Iterable[Dict[str, Any]]]
    ):

        s3_client = boto3.client("s3")

        s3_client.put_object(
            Body=json.dumps(items), Bucket=self.s3_bucket, Key=self.filename
        )
