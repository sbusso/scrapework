import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Union

import boto3
from pydantic import Field

from scrapework.context import Context


class Pipeline(ABC):
    @abstractmethod
    def process_items(
        self,
        items: Union[Dict[str, Any], Iterable[Dict[str, Any]]],
        ctx: Context,
    ):
        pass


class JsonFilePipeline(Pipeline):
    def process_items(
        self, items: Union[Dict[str, Any], Iterable[Dict[str, Any]]], ctx: Context
    ):

        with open(ctx.filename, "w") as f:
            json.dump(items, f)
        ctx.logger.info(f"Items written to {ctx.filename}")


class S3Pipeline(Pipeline):
    s3_bucket: str = Field(default_factory=str)

    def __init__(self, s3_bucket: str):
        self.s3_bucket = s3_bucket

    def process_items(
        self, items: Union[Dict[str, Any], Iterable[Dict[str, Any]]], ctx: Context
    ):

        s3_client = boto3.client("s3")

        s3_client.put_object(
            Body=json.dumps(items), Bucket=self.s3_bucket, Key=ctx.filename
        )


class MetadataPipeline(Pipeline):
    def process_items(
        self, items: Union[Dict[str, Any], Iterable[Dict[str, Any]]], ctx: Context
    ):
        if isinstance(items, dict):
            ctx.logger.info("Items count: 1")
            return {"items_count": 1}
        else:
            ctx.logger.info(f"Items count: {len(list(items))}")
            return {"items_count": len(list(items))}
