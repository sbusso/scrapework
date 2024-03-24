from typing import Any, Dict, Iterable, Union

from parsel import Selector
from trafilatura import bare_extraction


class Extractor:
    def extract(self, response) -> Union[Dict[str, Any], Iterable[Dict[str, Any]]]:
        raise NotImplementedError


class BodyExtractor(Extractor):
    def extract(self, response) -> Dict[str, str]:
        body = Selector(response.text).xpath("//body/text()").get()

        if not body:
            raise ValueError("Body not found")

        return {"body": body}


class ArticleExtractor(Extractor):
    def extract(self, response) -> Dict[str, str]:
        article = bare_extraction(response.text)

        if not article:
            raise ValueError("Article not found")

        return {"text": article.text}
