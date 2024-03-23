import json
from unittest.mock import MagicMock, patch

from scrapework.config import PipelineConfig
from scrapework.spider import Spider


# Create a concrete subclass of Spider for testing purposes
class ConcreteSpider(Spider):
    name = "concrete_spider"

    def parse(self):
        pass


def test_process_items_with_file_backend():
    items = [{"name": "item1"}, {"name": "item2"}]
    config = PipelineConfig(
        backend=BackendType.FILE,
        base_url="https://example.com",
        s3_bucket="test-bucket",
        filename="test.json",
    )
    pipeline = ItemPipeline()

    with patch("builtins.open", MagicMock()) as mock_open:
        pipeline.process_items(items, config)

        mock_open.assert_called_once_with("test.json", "w")


def test_process_items_with_s3_backend():
    items = [{"name": "item1"}, {"name": "item2"}]
    config = PipelineConfig(
        backend=BackendType.S3,
        base_url="https://example.com",
        s3_bucket="my-bucket",
        filename="example.json",
    )
    pipeline = ItemPipeline()

    with patch("boto3.client") as mock_s3_client:
        pipeline.process_items(items, config)

        mock_s3_client.assert_called_once_with("s3")
        mock_s3_client.return_value.put_object.assert_called_once_with(
            Body=json.dumps(items), Bucket="my-bucket", Key="example.json"
        )


def test_export_to_json():
    items = [{"name": "item1"}, {"name": "item2"}]
    config = PipelineConfig(
        backend=BackendType.FILE,
        base_url="https://example.com",
        s3_bucket="my-bucket",
        filename="example.json",
    )
    pipeline = ItemPipeline()

    with patch("builtins.open", MagicMock()) as mock_open:
        pipeline.export_to_json(items, config)

        mock_open.assert_called_once_with("example.json", "w")


def test_export_to_s3():
    items = [{"name": "item1"}, {"name": "item2"}]
    config = PipelineConfig(
        backend=BackendType.S3,
        base_url="https://example.com",
        s3_bucket="my-bucket",
        filename="example.json",
    )
    pipeline = ItemPipeline()

    with patch("boto3.client") as mock_s3_client:
        pipeline.export_to_s3(items, config)

        mock_s3_client.assert_called_once_with("s3")
        mock_s3_client.return_value.put_object.assert_called_once_with(
            Body=json.dumps(items), Bucket="my-bucket", Key="example.json"
        )
