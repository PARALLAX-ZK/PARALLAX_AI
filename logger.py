import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

LOG_DIR = "./logs"
os.makedirs(LOG_DIR, exist_ok=True)

DEFAULT_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"

class ParallaxLogger:
    def __init__(
        self,
        name: str,
        level: str = "INFO",
        to_file: bool = True,
        to_console: bool = True,
        max_file_size: int = 5 * 1024 * 1024,
        backup_count: int = 3
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self._parse_level(level))
        formatter = logging.Formatter(DEFAULT_FORMAT, datefmt=DEFAULT_DATEFMT)

        if to_console:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

        if to_file:
            file_path = os.path.join(LOG_DIR, f"{name}.log")
            file_handler = RotatingFileHandler(file_path, maxBytes=max_file_size, backupCount=backup_count)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def _parse_level(self, level_str: str) -> int:
        level_str = level_str.upper()
        return {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }.get(level_str, logging.INFO)

    def get(self) -> logging.Logger:
        return self.logger

# Registry for global use
_loggers = {}

def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    if name not in _loggers:
        _loggers[name] = ParallaxLogger(name, level=level or "INFO").get()
    return _loggers[name]

def set_level(name: str, level: str):
    if name in _loggers:
        _loggers[name].setLevel(level.upper())

def list_loggers() -> list:
    return list(_loggers.keys())

if __name__ == "__main__":
    # Example use
    log = get_logger("test_subsystem", "DEBUG")
    log.debug("This is a debug message")
    log.info("Startup complete")
    log.warning("This is a warning")
    log.error("This is an error")
    log.critical("Critical condition detected")

    print("Loggers available:", list_loggers())
