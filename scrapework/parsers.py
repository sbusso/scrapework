from typing import Any, Dict, Iterable, Union

from trafilatura import bare_extraction


class Parser:
    def extract(self, selector) -> Union[Dict[str, Any], Iterable[Dict[str, Any]]]:
        raise NotImplementedError


class HTMLBodyParser(Parser):
    def extract(self, selector) -> Dict[str, str]:
        body = selector.xpath("//body/text()").get()

        if not body:
            raise ValueError("Body not found")

        return {"body": body}


class ArticleParser(Parser):
    def extract(self, selector) -> Dict[str, str]:
        article = bare_extraction(selector)

        if not article:
            raise ValueError("Article not found")

        return {"text": article.text}
