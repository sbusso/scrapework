from dataclasses import dataclass, field
from typing import Dict

from httpx import Response

from scrapework.core.collector import MetadataCollector


@dataclass
class Context:
    collector: MetadataCollector = field(default_factory=MetadataCollector)
    variables: Dict = field(default_factory=dict)
    response: Response | None = None
