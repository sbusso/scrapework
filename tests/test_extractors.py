from unittest.mock import MagicMock

from scrapework.extractors import Extractor


def test_extract_body():
    extractor = Extractor()
    response = MagicMock()
    response.text = "<body>Hello, world!</body>"
    result = extractor.extract_body(response)
    assert result == {"body": "Hello, world!"}


def test_extract_not_implemented():
    extractor = Extractor()
    response = MagicMock()
    # Assert that NotImplementedError is raised
    try:
        extractor.extract(response)
        assert False, "Expected NotImplementedError to be raised"
    except NotImplementedError:
        pass
