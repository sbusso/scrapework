from typing import Any, Dict, Iterable, Union

from parsel import Selector
from trafilatura import bare_extraction

from scrapework.core.context import Context


class Parser:
    def extract(
        self, ctx: Context, selector: Selector
    ) -> Union[Dict[str, Any], Iterable[Dict[str, Any]]]:
        raise NotImplementedError


class EmptyParser(Parser):
    def extract(self, _ctx: Context, _selector: Selector) -> Dict[str, str]:
        return {}


class HTMLBodyParser(Parser):
    def extract(self, _: Context, selector: Selector) -> Dict[str, str]:
        body = selector.xpath("//body/text()").get()

        if not body:
            raise ValueError("Body not found")

        return {"body": body}


class ArticleParser(Parser):
    def extract(self, _ctx: Context, selector: Selector) -> Dict[str, str]:
        article = bare_extraction(selector)

        if not article:
            raise ValueError("Article not found")

        return {"text": article.text}
