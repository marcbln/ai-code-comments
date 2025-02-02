from .base import ChangeStrategy
from pathlib import Path
from typing import Optional, Tuple
import tempfile
import subprocess
from textwrap import dedent

class UDiffStrategy(ChangeStrategy):
    @staticmethod
    def get_prompt_additions() -> str:
        """Return strategy-specific prompt additions for udiff format"""
        return dedent("""
            - Output MUST be a valid unified diff patch.
            - Start response with '--- original.php'
            - Second line must be '+++ modified.php'
            - Start each hunk of changes with a `@@ ... @@` line.
            - DON'T include line numbers like `diff -U0` does (The user's patch tool doesn't need them). just use literally `@@ ... @@` instead.
            - The user's patch tool needs CORRECT patches that apply cleanly against the current contents of the file!
            - Think carefully and make sure you include and mark all lines that need to be removed or changed as `-` lines.
            - Make sure you mark all new or modified lines with `+`.
            - Don't leave out any lines or the diff patch won't apply correctly.

            Indentation matters in the diffs!

            Start a new hunk for each section of the file that needs changes.

            Only output hunks that specify changes with `+` or `-` lines.
            Skip any hunks that are entirely unchanging ` ` lines.

            Output hunks in whatever order makes the most sense.
            Hunks don't need to be in any particular order.

            - Do NOT include any text outside the diff
            - Do NOT wrap in markdown blocks
            - Include proper line endings for the complete code block
            """)

    def apply_changes(self, file_path: Path, llm_response: str, verbose: bool = False) -> Tuple[bool, Optional[Path]]:
        if verbose:
            print("🔄 Applying changes via patch...")
            
        # Create patch file
        patch_file = tempfile.NamedTemporaryFile(mode='w', suffix='.diff', delete=False)
        patch_path = Path(patch_file.name)
        patch_file.write(llm_response)
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
