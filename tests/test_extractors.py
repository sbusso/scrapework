from parsel import Selector

from scrapework.parsers import HTMLBodyParser, Parser


def test_extract_body() -> None:
    extractor = HTMLBodyParser()
    selector = Selector("<body>Hello, world!</body>")
    result = extractor.extract(selector)
    assert result == {"body": "Hello, world!"}


def test_extract_not_implemented():
    extractor = Parser()
    selector = Selector("")
    # Assert that NotImplementedError is raised
    try:
        extractor.extract(selector)
        assert False, "Expected NotImplementedError to be raised"
    except NotImplementedError:
        pass
