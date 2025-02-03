from rich.console import Console
from rich.theme import Theme
from typing import Optional

class Logger:
    """Global logger with verbosity support"""
    
    _instance: Optional['Logger'] = None
    
    def __init__(self):
        self.verbose = False
        self.console = Console(theme=Theme({
            "info": "dim cyan",
            "warning": "magenta",
            "error": "bold red",
            "success": "green",
        }))

    @classmethod
    def get_instance(cls) -> 'Logger':
        if cls._instance is None:
            cls._instance = Logger()
        return cls._instance

    def set_verbose(self, verbose: bool):
        self.verbose = verbose

    def debug(self, message: str):
        """Log debug message only if verbose mode is enabled"""
        if self.verbose:
            self.console.print(f"🔍 {message}", style="info")

    def info(self, message: str):
        """Log general information"""
        self.console.print(message)

    def success(self, message: str):
        """Log success message"""
        self.console.print(f"✓ {message}", style="success")

    def warning(self, message: str):
        """Log warning message"""
        self.console.print(f"⚠️ {message}", style="warning")

    def error(self, message: str):
        """Log error message"""
        self.console.print(f"✗ {message}", style="error")

# Global logger instance
logger = Logger.get_instance()
