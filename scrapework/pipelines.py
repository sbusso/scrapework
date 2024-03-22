from typing import Dict, Iterable, Union

from scrapework.config import BackendType, SpiderConfig
import boto3
import json


class ItemPipeline:
    def process_items(self, items: Union[Dict, Iterable], config: SpiderConfig):
        if config.backend == BackendType.FILE:
            self.export_to_json(items, config)
        self.export_to_s3(items, config)

    def export_to_json(self, items: Union[Dict, Iterable], config: SpiderConfig):
        file_name = f"{config.base_url.split('//')[-1]}.json"
        with open(file_name, "w") as f:
            json.dump(items, f)

    def export_to_s3(self, items: Union[Dict, Iterable], config: SpiderConfig):
        if not config.s3_bucket:
            raise ValueError("S3 bucket name not provided in the configuration.")

        s3_client = boto3.client("s3")
        file_name = f"{config.base_url.split('//')[-1]}.json"
        s3_client.put_object(
            Body=json.dumps(items), Bucket=config.s3_bucket, Key=file_name
        )
