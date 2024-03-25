from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Union

from scrapework.core.context import Context


class Processor(ABC):
    """Processor _summary_

    _extended_summary_

    Args:
        ABC (_type_): _description_
    """

    def __init__(self, context: Context) -> None:
        self.context = context
        self.context.logger.info(f"Using processor: {self.__class__.__name__}")

    @abstractmethod
    def process_items(
        self,
        items: Union[Dict[str, Any], Iterable[Dict[str, Any]]],
    ):
        pass
