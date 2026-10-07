"""
Centralized logging configuration for i-Downloader
"""

import logging
import sys
from pathlib import Path
from .constants import APP_DATA_DIR


def setup_logger(name: str = "i-downloader", log_level: int = logging.INFO) -> logging.Logger:
    """
    Setup and return a configured logger instance.
    Logs are written to stdout and ~/.i-downloader/logs/app.log
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(log_level)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)

    # File Handler
    try:
        log_dir = APP_DATA_DIR / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "app.log"

        file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not initialize file log handler: {e}")

    return logger


logger = setup_logger()
