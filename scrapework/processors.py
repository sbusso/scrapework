from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Union

from scrapework.core.logger import Logger


class Processor(ABC):
    """Processor _summary_

    _extended_summary_

    Args:
        ABC (_type_): _description_
    """

    def __init__(self) -> None:
        self.logger = Logger().get_logger()
        self.logger.info(f"Using processor: {self.__class__.__name__}")

    @abstractmethod
    def process_items(
        self,
        items: Union[Dict[str, Any], Iterable[Dict[str, Any]]],
    ):
        pass
