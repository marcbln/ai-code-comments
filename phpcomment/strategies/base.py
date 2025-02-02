from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple
import tempfile
import subprocess

class ChangeStrategy(ABC):
    @abstractmethod
    def process_llm_response_raw(self, file_path: Path, llmResponseRaw: str, verbose: bool = False) -> Tuple[bool, Optional[Path]]:
        """
        Apply changes and return (success, temp_file_path)
        
        Args:
            file_path: Original file path
            llmResponseRaw: New content from LLM
            verbose: Enable verbose output
            
        Returns:
            Tuple of (success, temporary_file_path)
        """
        pass

    @staticmethod
    def process_llm_response() -> str:
        """
        Return prompt additions specific to this strategy.. used for the LLM prompt

        Returns:
            str: Prompt additions
        """
        pass



