import hashlib

from .base import ChangeStrategy
from pathlib import Path
from textwrap import dedent

from ..llm.helpers import MyHelpers
from ..utils.patcher import MyPatcher
from ..utils.patcher_v3 import PatcherV3


class UDiffStrategy(ChangeStrategy):
    @staticmethod
    def get_prompt_additions() -> str:
        """Return strategy-specific prompt additions for udiff format"""
        return dedent("""
            - Output MUST be a valid unified diff patch.
            - Start response with '--- original.php'
            - Second line must be '+++ modified.php'
            - Start each hunk of changes with a `@@ ... @@` line.
            - DON'T include line numbers like `diff -U0` does, The user's patch tool doesn't need them. Just use literally `@@ ... @@` instead.
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

    def process_llm_response(self, llmResponseRaw: str, pathOrigFile) -> Path|None:
        print("🔄 Applying changes via patch...")
        
        # Read original content
        with open(pathOrigFile, 'r') as f:
            original_content = f.read()

        # build hash form original content (for temp file naming)
        hash = hashlib.sha256(original_content.encode('utf-8')).hexdigest()


        # Apply patch using MyPatcher
        # patcher = MyPatcher(verbose=False)
        patcher = PatcherV3()
        try:
            # strip clutter (if any) from the raw llm response
            cleanedResponse = MyHelpers.strip_code_block_markers(llmResponseRaw)
            # write the patch to a temp file for debugging
            MyHelpers.writeTempFileV2(hash, cleanedResponse, '.diff')
            # apply patch
            modified_content = patcher.apply_patch(original_content, cleanedResponse)
        except Exception as e:
            print(f"Error applying patch: {str(e)}")
            return None
            
        # Write modified content to temp file
        pathTempPhpFile = MyHelpers.writeTempFileV2(hash, modified_content, '.php')
        
        return pathTempPhpFile

