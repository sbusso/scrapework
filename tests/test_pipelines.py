import json
from unittest.mock import patch

from scrapework.config import PipelineConfig
from scrapework.pipelines import JsonFilePipeline, S3Pipeline


def test_process_items_with_s3_backend():
    items = [{"name": "item1"}, {"name": "item2"}]
    config = PipelineConfig(
        base_url="https://example.com",
        filename="example.json",
    )
    pipeline = S3Pipeline(s3_bucket="my-bucket")

    with patch("boto3.client") as mock_s3_client:
        pipeline.process_items(items, config.filename)

        mock_s3_client.assert_called_once_with("s3")
        mock_s3_client.return_value.put_object.assert_called_once_with(
            Body=json.dumps(items), Bucket="my-bucket", Key="example.json"
        )


def test_process_items_with_json_file_backend():
    items = [{"name": "item1"}, {"name": "item2"}]
    filename = "output.json"
    pipeline = JsonFilePipeline()

    pipeline.process_items(items, filename)

    with open(filename, "r") as f:
        data = json.load(f)

    assert data == items
