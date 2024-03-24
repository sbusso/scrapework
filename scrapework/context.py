import logging


class Context:
    logger: logging.Logger

    filename: str

    def __init__(self, logger: logging.Logger, filename: str):
        if not isinstance(logger, logging.Logger):
            raise TypeError("logger must be an instance of logging.Logger")
        if not isinstance(filename, str):
            raise TypeError("filename must be a string")
        self.logger = logger
        self.filename = filename

    class Config:
        arbitrary_types_allowed = True
