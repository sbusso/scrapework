from unittest.mock import MagicMock

from scrapework.parsers import HTMLBodyParser, Parser


def test_extract_body():
    extractor = HTMLBodyParser()
    response = MagicMock()
    response.text = "<body>Hello, world!</body>"
    result = extractor.extract(response)
    assert result == {"body": "Hello, world!"}


def test_extract_not_implemented():
    extractor = Parser()
    response = MagicMock()
    # Assert that NotImplementedError is raised
    try:
        extractor.extract(response)
        assert False, "Expected NotImplementedError to be raised"
    except NotImplementedError:
        pass
