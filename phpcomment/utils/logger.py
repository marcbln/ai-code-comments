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

    def debug(self, message: str, **kwargs):
        """Log debug message only if verbose mode is enabled"""
        if self.verbose:
            self.console.print(f"🔍 {message}", style="info", **kwargs)

    def info(self, message: str, **kwargs):
        """Log general information"""
        self.console.print(message, style="info", **kwargs)

    def success(self, message: str, **kwargs):
        """Log success message"""
        self.console.print(f"✓ {message}", style="success", **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.console.print(f"⚠️ {message}", style="warning", **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message"""
        self.console.print(f"✗ {message}", style="error", **kwargs)

# Global logger instance
logger = Logger.get_instance()
