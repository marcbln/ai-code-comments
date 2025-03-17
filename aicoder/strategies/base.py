from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple
import tempfile
import subprocess

class ChangeStrategy(ABC):

    @staticmethod
    @abstractmethod
    def get_prompt_additions() -> str:
        """Return strategy-specific prompt additions for whole file replacement"""
        return "- Response ONLY with full modified source code."

    @abstractmethod
    def process_llm_response(self, llmResponseRaw: str, pathOrigFile) -> Path|None:
        """
        Apply changes and return (success, temp_file_path)
        
        Args:
            file_path: Original file path
            llmResponseRaw: New content from LLM
            verbose: Enable verbose output
            
        Returns:
            str temporary_file_path
        """
        pass


