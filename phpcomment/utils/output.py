# ---- Rich Output Utilities ----
# File: phpcomment/utils/output.py

from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "error": "bold red",
    "success": "green",
})

console = Console(theme=custom_theme)

def print_success(message: str) -> None:
    """Display success message with rich formatting"""
    console.print(f"✓ {message}", style="success")

def print_error(message: str) -> None:
    """Display error message with rich formatting"""
    console.print(f"✗ {message}", style="error")
