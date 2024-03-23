import logging

from pydantic import BaseModel

from scrapework.config import EnvConfig


class Context(BaseModel):
    logger: logging.Logger
    config: EnvConfig

    class Config:
        arbitrary_types_allowed = True
