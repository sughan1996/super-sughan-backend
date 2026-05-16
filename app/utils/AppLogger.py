import logging

from app.config import log_level
from app.utils.AppExceptions import AppBaseException

def setup_logger(name):
    try:
        logger = logging.getLogger(name)
        if logger.handlers:
            return logger
        logger.setLevel(log_level)
        logger.propagate = False
        formatter = logging.Formatter(
            "%(filename)s:%(lineno)d - %(funcName)s() | %(message)s"
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    except Exception as err:
        raise AppBaseException(f"Error setting up logger: {err}")

logger = setup_logger("super-sughan")
