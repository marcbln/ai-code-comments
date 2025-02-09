import hashlib

from .base import ChangeStrategy
from pathlib import Path
from textwrap import dedent

from ..llm.helpers import MyHelpers
from ..utils.patcher import MyPatcher
from ..utils.patcher_v3 import PatcherV3
from ..utils.patcher_v4 import PatcherV4
from ..utils.logger import logger


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
        print("🔄 Applying changes by patch with custom pacher...")

        # Read original content
        with open(pathOrigFile, 'r') as f:
            original_content = f.read()


        # build hash form original content (for temp file naming)
        hash = hashlib.sha256(original_content.encode('utf-8')).hexdigest()[:8]


        # write the original content to a temp file (for debugging only)
        MyHelpers.writeTempFileV2(hash, original_content, '-original.php')


        # Apply patch using out own patcher
        # patcher = MyPatcher(verbose=False)
        patcher = PatcherV4(continue_on_error=True, fuzzy_match=True)
        try:
            modifiedResponse, blocks = MyHelpers.extract_code_blocks(llmResponseRaw)
            # strip clutter (if any) from the raw llm response
            # cleanedResponse = MyHelpers.strip_code_block_markers(llmResponseRaw)

            # ---- cleanup the response
            if len(blocks) == 0:
                # we assume that the response is a single code block
                extractedCodeBlock = llmResponseRaw
                print(f"DEBUG: No code blocks found in response - assuming full response is a single code block")
            else:
                # we assume that the response is a list of code blocks
                extractedCodeBlock = blocks[0]
                if len(blocks) > 1:
                    print(f"WARNING: More than one code block found")

            # ---- write the patch to a temp file (for debugging only)
            logger.debug(f"Cleaned Response:\n>>>>>>\n{extractedCodeBlock}\n<<<<<<", highlight=False)
            MyHelpers.writeTempFileV2(hash, extractedCodeBlock, '-patch.diff')

            # ---- apply patch
            modified_content = patcher.apply_patch(original_content, extractedCodeBlock)
        except Exception as e:
            logger.error(f"Error applying patch: {str(e)}")
            return None
            
        # Write modified content to temp file
        pathTempPhpFile = MyHelpers.writeTempFileV2(hash, modified_content, '-patched.php')
        
        return pathTempPhpFile

