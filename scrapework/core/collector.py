import datetime
from dataclasses import dataclass, field
from typing import List


@dataclass
class JobCollector:
    url: str
    duration: datetime.timedelta
    items_count: int


@dataclass
class MetadataCollector:
    metadata: dict = field(default_factory=dict)
    jobs: List[JobCollector] = field(default_factory=list)

    def set(self, key, value):
        self.metadata[key] = value

    def get(self, key):
        return self.metadata.get(key)

    def reset(self):
        self.metadata = {}
