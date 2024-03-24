import json
import logging
from unittest.mock import patch

from scrapework.context import Context
from scrapework.pipelines import JsonFilePipeline, S3Pipeline


def test_process_items_with_s3_backend():
    items = [{"name": "item1"}, {"name": "item2"}]

    pipeline = S3Pipeline(s3_bucket="my-bucket")

    context = Context(
        logger=logging.getLogger(),
        filename="example.json",
    )

    with patch("boto3.client") as mock_s3_client:
        pipeline.process_items(items, context)

        mock_s3_client.assert_called_once_with("s3")
        mock_s3_client.return_value.put_object.assert_called_once_with(
            Body=json.dumps(items), Bucket="my-bucket", Key="example.json"
        )


def test_process_items_with_json_file_backend():
    items = [{"name": "item1"}, {"name": "item2"}]
    filename = "output.json"
    pipeline = JsonFilePipeline()

    context = Context(
        logger=logging.getLogger(),
        filename="output.json",
    )

    with patch("builtins.open") as mock_open:
        pipeline.process_items(items, context)
        assert mock_open.call_count == 1
        assert mock_open.call_args_list[0][0][0] == filename
