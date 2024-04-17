import json
import logging
from abc import abstractmethod
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Iterable, Union

import boto3
from pydantic import BaseModel, Field

from scrapework.core.context import Context
from scrapework.module import Module


class Handler(Module):
    """Handler Processes and handles the structured data

    Processes and handls the structured data, such as saving it to a file or uploading it to a cloud storage service.
    """

    logger: logging.Logger

    @abstractmethod
    def process_items(
        self,
        ctx: Context,
        items: Union[Dict[str, Any], Iterable[Dict[str, Any]]],
    ):
        pass


def encode_items(items: Union[Dict[str, Any], Iterable[Dict[str, Any]]]):
    if isinstance(items, BaseModel):
        items = items.model_dump()

    elif isinstance(items, Iterable) and all(
        isinstance(item, BaseModel) for item in items
    ):
        items = [item.model_dump() for item in items]  # type: ignore
    elif is_dataclass(items):
        items = asdict(items)  # type: ignore
    elif isinstance(items, Iterable) and all(is_dataclass(item) for item in items):
        items = [asdict(item) for item in items]  # type: ignore
    # Ensure items are a list of dictionaries or a single dictionary
    if isinstance(items, Dict):
        items = [items]  # type: ignore
    elif isinstance(items, Iterable):
        items = list(items)

    return items


class JsonFileHandler(Handler):
    filename: str

    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename

    def process_items(
        self, ctx: Context, items: Union[Dict[str, Any], Iterable[Dict[str, Any]]]
    ):

        with open(self.filename, "w") as f:
            json.dump(encode_items(items), f)
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
            Body=json.dumps(encode_items(items)),
            Bucket=self.s3_bucket,
            Key=self.filename,
        )
