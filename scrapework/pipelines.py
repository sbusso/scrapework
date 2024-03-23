import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Union

import boto3
from pydantic import BaseModel, Field


class Pipeline(ABC, BaseModel):
    @abstractmethod
    def process_items(
        self,
        items: Union[Dict[str, Any], Iterable[Dict[str, Any]]],
        filename: str | None,
    ):
        pass


class JsonFilePipeline(Pipeline):
    def process_items(
        self, items: Union[Dict[str, Any], Iterable[Dict[str, Any]]], filename: str
    ):

        with open(filename, "w") as f:
            json.dump(items, f)


class S3Pipeline(Pipeline):
    s3_bucket: str = Field(default_factory=str)

    def process_items(
        self,
        items: Union[Dict[str, Any], Iterable[Dict[str, Any]]],
        filename: str,
    ):

        s3_client = boto3.client("s3")

        s3_client.put_object(
            Body=json.dumps(items), Bucket=self.s3_bucket, Key=filename
        )


class MetadataPipeline(Pipeline):
    def process_items(
        self,
        items: Union[Dict[str, Any], Iterable[Dict[str, Any]]],
    ):
        if isinstance(items, dict):
            return {"items_count": 1}
        else:
            return {"items_count": len(list(items))}
