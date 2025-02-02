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

    def apply_changes(self, file_path: Path, new_content: str, verbose: bool = False) -> Tuple[bool, Optional[Path]]:
        if verbose:
            print("📝 Applying whole file replacement...")
            
        # Create temporary file with new content
        tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False)
        tmp_path = Path(tmp_file.name)
        tmp_file.write(new_content)
        tmp_file.close()
        
        return True, tmp_path
