from dataclasses import dataclass


@dataclass
class MetadataCollector:
    metadata: dict

    def update(self, key, value):
        self.metadata[key] = value

    def get(self, key):
        return self.metadata.get(key)

    def reset(self):
        self.metadata = {}
