from dataclasses import dataclass, field
from typing import Dict

from httpx import Response

from scrapework.core.collector import MetadataCollector
from scrapework.request import Request


@dataclass
class Context:
    collector: MetadataCollector = field(default_factory=MetadataCollector)
    variables: Dict = field(default_factory=dict)
    response: Response | None = None
    request: Request | None = None

    def urljoin(self, url: str) -> str:
        if not self.request:
            return url
        else:
            return self.request.urljoin(url)
