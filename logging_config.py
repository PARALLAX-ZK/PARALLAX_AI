import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Log directory and file
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "parallax.log"

# Log level can be configured via environment
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Standard log format
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def configure_logger(name: str) -> logging.Logger:
    """
    Configures and returns a named logger with both stream and file handlers.
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    # Avoid adding multiple handlers if already configured
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    # File handler (rotating)
    file_handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# Example usage
if __name__ == "__main__":
    test_logger = configure_logger("PARALLAX_LOGGER_TEST")
    test_logger.info("Logger initialized successfully")
    test_logger.warning("This is a test warning")
    test_logger.error("This is a test error")
