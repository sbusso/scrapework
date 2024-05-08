import logging


class Logger:
    _instance = None

    def __new__(cls, name: str = "default"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.configure(name)
        return cls._instance

    def configure(self, name="default", level=logging.INFO):

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
        )

        file_handler = logging.FileHandler(f"{name}.log")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger
