from abc import ABC

from scrapework.core.logger import Logger


class Module(ABC):
    def __init__(self) -> None:
        self.logger = Logger().get_logger()
        self.logger.info(f"Using {self.__class__.__name__}")
