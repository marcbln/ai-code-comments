from .base import ChangeStrategy
from pathlib import Path
from typing import Optional, Tuple
import tempfile
from textwrap import dedent

class WholeFileStrategy(ChangeStrategy):
    @staticmethod
    def get_prompt_additions() -> str:
        """Return strategy-specific prompt additions for whole file replacement"""
        return "- Response ONLY with full modified source code."

    def process_llm_response_raw(self, file_path: Path, llmResponseRaw: str, verbose: bool = False) -> Tuple[bool, Optional[Path]]:
        if verbose:
            print("📝 Applying whole file replacement...")
            
        # Create temporary file with new content
        tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False)
        tmp_path = Path(tmp_file.name)
        tmp_file.write(llmResponseRaw)
        tmp_file.close()
        
        return True, tmp_path
