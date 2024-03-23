from typing import Any, Dict, Iterable, Union

from parsel import Selector


class Extractor:
    def extract(self, response) -> Union[Dict[str, Any], Iterable[Dict[str, Any]]]:
        raise NotImplementedError

    def extract_body(self, response) -> Dict[str, str]:
        body = Selector(response.text).xpath("//body/text()").get()

        if not body:
            raise ValueError("Body not found")

        return {"body": body}
