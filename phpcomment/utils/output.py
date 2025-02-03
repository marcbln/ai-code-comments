# ---- Output Utilities ----
# File: phpcomment/utils/output.py

from .logger import logger

def print_success(message: str) -> None:
    """Display success message with rich formatting"""
    logger.success(message)

def print_error(message: str) -> None:
    """Display error message with rich formatting"""
    logger.error(message)

def print_warning(message: str) -> None:
    """Display warning message with rich formatting"""
    logger.warning(message)
