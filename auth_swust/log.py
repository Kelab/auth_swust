import sys
import logging
from logging import DEBUG
from logging import ERROR
from logging import FATAL
from logging import INFO
from logging import WARN

AuthLogger = logging.getLogger("AuthLogger")

AuthLogger.setLevel(INFO)
StreamHandler = logging.StreamHandler(sys.stdout)

StreamHandler.setFormatter(
    logging.Formatter(
        fmt=
        "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] [%(funcName)s] > %(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]",
    ))

AuthLogger.addHandler(StreamHandler)
