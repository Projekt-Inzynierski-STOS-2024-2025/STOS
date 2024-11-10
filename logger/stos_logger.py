import logging
from logging.handlers import RotatingFileHandler
import os

LOGS_DIR: str = os.environ.get("LOGS_PATH", "/home/stos/")
LOGGING_LEVEL: int = logging.INFO if os.environ.get("ENVIRONMENT") == "prod" else logging.DEBUG
BACKUP_LOG_FILES: int = int(os.environ.get("BACKUP_LOG_FILES", 5))
LOG_FILE_SIZE: int = int(os.environ.get("LOG_FILE_SIZE", 10 * 1024 * 1024))


def get_logger(module_name: str) -> logging.Logger:
    log_file = LOGS_DIR + module_name + '.log'

    handler = RotatingFileHandler(log_file, maxBytes=LOG_FILE_SIZE, backupCount=BACKUP_LOG_FILES)
    handler.setLevel(LOGGING_LEVEL)

    logger = logging.getLogger(module_name)
    logger.setLevel(LOGGING_LEVEL)
    logger.addHandler(handler)

    return logger
