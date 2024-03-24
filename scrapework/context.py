import logging

from pydantic import BaseModel


class Context(BaseModel):
    logger: logging.Logger

    filename: str

    class Config:
        arbitrary_types_allowed = True
