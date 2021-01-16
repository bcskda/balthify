import logging
from balthify.config import Config

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(Config.loglevel)
    return logger
