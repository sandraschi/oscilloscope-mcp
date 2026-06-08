"""Logging helpers - stderr only to protect stdio MCP transport."""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Return a module logger that writes to stderr."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
        logger.propagate = False
    return logger
