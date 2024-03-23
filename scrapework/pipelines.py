import json
from typing import Dict, Iterable, List, Union

import boto3
from pydantic import BaseModel

from scrapework.config import BackendType, PipelineConfig


class ItemPipeline(BaseModel):
    def process_items(self, items: Union[Dict, Iterable], config: PipelineConfig):
        if config.backend == BackendType.FILE:
            self.export_to_json(list(items), config)
        elif config.backend == BackendType.S3:
            self.export_to_s3(items, config)

    def export_to_json(self, items: Union[Dict, List], config: PipelineConfig):
        file_name = config.filename
        with open(file_name, "w") as f:
            json.dump(items, f)

    def export_to_s3(self, items: Union[Dict, Iterable], config: PipelineConfig):
        if not config.s3_bucket:
            raise ValueError("S3 bucket name not provided in the configuration.")

        s3_client = boto3.client("s3")
        file_name = config.filename
        s3_client.put_object(
            Body=json.dumps(items), Bucket=config.s3_bucket, Key=file_name
        )
