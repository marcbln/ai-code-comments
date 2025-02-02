from .base import ChangeStrategy
from pathlib import Path
from typing import Optional, Tuple
import tempfile

class WholeFileStrategy(ChangeStrategy):
    def apply_changes(self, file_path: Path, new_content: str, verbose: bool = False) -> Tuple[bool, Optional[Path]]:
        if verbose:
            print("📝 Applying whole file replacement...")
            
        # Create temporary file with new content
        tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False)
        tmp_path = Path(tmp_file.name)
        tmp_file.write(new_content)
        tmp_file.close()
        
        return True, tmp_path
