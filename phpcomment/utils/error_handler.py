# ---- Error Handling Utilities ----
# File: phpcomment/utils/error_handler.py

from typing import Callable, TypeVar
from functools import wraps

T = TypeVar('T')

def handle_errors(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator for consistent error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            from .output import print_error  # Add circular import guard
            print_error(f"Operation failed: {str(e)}")
            raise
    return wrapper
