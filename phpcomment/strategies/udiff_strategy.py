from .base import ChangeStrategy
from pathlib import Path
from typing import Optional, Tuple
import tempfile
import subprocess

class UDiffStrategy(ChangeStrategy):
    def apply_changes(self, file_path: Path, new_content: str, verbose: bool = False) -> Tuple[bool, Optional[Path]]:
        if verbose:
            print("🔄 Applying changes via patch...")
            
        # Create patch file
        patch_file = tempfile.NamedTemporaryFile(mode='w', suffix='.diff', delete=False)
        patch_path = Path(patch_file.name)
        patch_file.write(new_content)
        patch_file.close()

        # Create a temporary copy of the original file to apply patch to
        tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False)
        tmp_path = Path(tmp_file.name)
        tmp_file.write(file_path.read_text())
        tmp_file.close()
        
        try:
            # Apply patch to the temporary file
            cmd = ['patch', str(tmp_path), str(patch_path)]
            if verbose:
                print(f"🔧 Applying patch: {' '.join(cmd)}")
                
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Error applying patch: {result.stderr}")
                return False, None
                
            return True, tmp_path
            
        except Exception as e:
            print(f"Failed to apply patch: {str(e)}")
            return False, None
        finally:
            # Clean up patch file
            patch_path.unlink()
