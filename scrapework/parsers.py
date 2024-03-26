from typing import Any, Dict, Iterable, Union

from trafilatura import bare_extraction


class Parser:
    def extract(self, body) -> Union[Dict[str, Any], Iterable[Dict[str, Any]]]:
        raise NotImplementedError


class HTMLBodyParser(Parser):
    def extract(self, body) -> Dict[str, str]:
        body = body.xpath("//body/text()").get()

        if not body:
            raise ValueError("Body not found")

        return {"body": body}


class ArticleParser(Parser):
    def extract(self, body) -> Dict[str, str]:
        article = bare_extraction(body)

        if not article:
            raise ValueError("Article not found")

        return {"text": article.text}
