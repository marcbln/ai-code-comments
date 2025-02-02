# ---- Error Handling Utilities ----
# File: phpcomment/utils/error_handler.py

from typing import Callable, TypeVar
from functools import wraps
from .output import print_error, print_warning
import traceback
from rich.console import Console

T = TypeVar('T')
console = Console()

def handle_error(error: Exception) -> None:
    """Handle exceptions with verbose output control"""

    console.print(traceback.format_exc(), style="yellow")
    print_warning(f"Full error context:\n{error}")
