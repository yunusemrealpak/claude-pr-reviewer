"""Logging configuration for the PR review automation system."""

import logging
import sys
from logging.handlers import RotatingFileHandler
import os


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure application-wide logging with console and file handlers.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured root logger instance
    """
    # Create logs directory if not exists
    os.makedirs("logs", exist_ok=True)

    # Log format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Main file handler with rotation
    file_handler = RotatingFileHandler(
        "logs/pr_review.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # Error-only file handler
    error_handler = RotatingFileHandler(
        "logs/pr_review_errors.log",
        maxBytes=5_000_000,  # 5MB
        backupCount=3,
        encoding="utf-8"
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
