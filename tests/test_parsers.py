from parsel import Selector

from scrapework.core.context import Context
from scrapework.parsers import HTMLBodyParser, Parser


def test_extract_body() -> None:
    extractor = HTMLBodyParser()
    selector = Selector("<body>Hello, world!</body>")
    ctx = Context()
    result = extractor.extract(ctx, selector)
    assert result == {"body": "Hello, world!"}


def test_extract_not_implemented():
    extractor = Parser()
    selector = Selector("")
    # Assert that NotImplementedError is raised
    ctx = Context()
    try:
        extractor.extract(ctx, selector)
        assert False, "Expected NotImplementedError to be raised"
    except NotImplementedError:
        pass
