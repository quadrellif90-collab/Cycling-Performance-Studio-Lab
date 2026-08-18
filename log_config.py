"""Logging configuration for Cycling Performance Studio Lab."""

import logging
import sys


def setup_logging() -> None:
    """Configure the root logger for the application."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if called multiple times
    if logger.handlers:
        return

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)