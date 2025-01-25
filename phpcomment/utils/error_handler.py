# ---- Error Handling Utilities ----
# File: phpcomment/utils/error_handler.py

from typing import Callable, TypeVar
from functools import wraps
from rich.console import Console

T = TypeVar('T')
console = Console()

def handle_error(error: Exception, verbose: bool = False) -> None:
    """Handle exceptions with verbose output control"""
    from .output import print_error, print_warning
    import traceback
    
    error_msg = f"Error: {str(error)}"
    
    if verbose:
        print_warning("Verbose error details:")
        console.print(traceback.format_exc(), style="yellow")
        print_warning(f"Full error context:\n{error}")
    else:
        print_error(error_msg)
