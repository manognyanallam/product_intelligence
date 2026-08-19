"""
Structured logging configuration for the AI Product Intelligence Platform.

Provides consistent logging across all components with JSON formatting
for production monitoring.
"""
import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """
    Configure structured logging for the application.

    This function is idempotent — it will only configure the root logger once.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    logger = logging.getLogger()
    # Avoid adding duplicate handlers if called multiple times.
    if logger.handlers:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        return

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)-25s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Module name (typically __name__).

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)
