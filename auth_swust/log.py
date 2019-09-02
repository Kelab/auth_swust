import sys
import logging
from logging.config import dictConfig

LOGGING_CONFIG_DEFAULTS = dict(
    version=1,
    disable_existing_loggers=False,
    loggers={
        "AUTH_LOGGER": {"level": "INFO", "handlers": ["console"]},
    },
    handlers={
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": sys.stdout,
        }
    },
    formatters={
        "generic": {
            "format": "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] [%(funcName)s] > %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S]",
            "class": "logging.Formatter",
        },
    }
)
dictConfig(LOGGING_CONFIG_DEFAULTS)

AUTH_LOGGER = logging.getLogger("AUTH_LOGGER")
