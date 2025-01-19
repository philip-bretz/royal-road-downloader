import logging
from logging import getLogger

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler("testing.log"),
        logging.StreamHandler(),
    ]
)


if __name__ == "__main__":
    logger = getLogger(__name__)
    logger.info("This is an info log item")
