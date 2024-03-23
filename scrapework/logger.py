import logging

# Configure the logger
# Configure the logger for the entire module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
)

# Configure file handler
file_handler = logging.FileHandler("spidy.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Optionally, configure console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
