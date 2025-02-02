from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple
import tempfile
import subprocess

class ChangeStrategy(ABC):
    @abstractmethod
    def apply_changes(self, file_path: Path, new_content: str, verbose: bool = False) -> Tuple[bool, Optional[Path]]:
        """
        Apply changes and return (success, temp_file_path)
        
        Args:
            file_path: Original file path
            new_content: New content from LLM
            verbose: Enable verbose output
            
        Returns:
            Tuple of (success, temporary_file_path)
        """
        pass
