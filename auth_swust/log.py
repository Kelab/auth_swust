import sys
import logging
from logging import DEBUG
from logging import ERROR
from logging import FATAL
from logging import INFO
from logging import WARN
from loguru import logger

AuthLogger = logging.getLogger("AuthLogger")
logger.error("deprecated: 请使用 loguru 设置 log 等级.")
