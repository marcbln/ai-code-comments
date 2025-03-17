# ---- Output Utilities ----
# File: aicoder/utils/output.py

from .logger import myLogger

def print_success(message: str) -> None:
    """Display success message with rich formatting"""
    myLogger.success(message)

def print_error(message: str) -> None:
    """Display error message with rich formatting"""
    myLogger.error(message)

def print_warning(message: str) -> None:
    """Display warning message with rich formatting"""
    myLogger.warning(message)
