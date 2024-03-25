from dataclasses import dataclass, field


@dataclass
class MetadataCollector:
    metadata: dict = field(default_factory=dict)

    def set(self, key, value):
        self.metadata[key] = value

    def get(self, key):
        return self.metadata.get(key)

    def reset(self):
        self.metadata = {}
