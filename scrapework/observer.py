from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    def observe(self, logger, metadata_collector):
        pass


class ProgressObserver(Observer):
    def observe(self, data, metadata_collector, logger):
        pages_visited = data.get("pages_visited", 0)
        items_extracted = data.get("items_extracted", 0)
        metadata_collector.update("pages_visited", pages_visited)
        metadata_collector.update("items_extracted", items_extracted)
        logger.info(
            f"Progress: {pages_visited} pages visited, {items_extracted} items extracted"
        )


class ErrorObserver(Observer):
    def observe(self, data, metadata_collector, logger):
        error_count = data.get("error_count", 0)
        metadata_collector.update("error_count", error_count)
        logger.error(f"Encountered {error_count} errors")
