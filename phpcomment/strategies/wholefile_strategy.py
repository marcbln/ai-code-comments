from .base import ChangeStrategy
from pathlib import Path
from typing import Optional, Tuple
import tempfile
from textwrap import dedent

from ..llm.helpers import MyHelpers


class WholeFileStrategy(ChangeStrategy):
    @staticmethod
    def get_prompt_additions() -> str:
        """Return strategy-specific prompt additions for whole file replacement"""
        return "- Response ONLY with full modified source code."

    def process_llm_response(self, llmResponseRaw: str, pathOrigFile) -> str|Path:

        print("📝 Applying whole file replacement...")

        cleanedResponse = MyHelpers.strip_code_block_markers(llmResponseRaw)

        # Write cleaned response to a temporary file
        pathTempFile = MyHelpers.writeTempCodeFile(cleanedResponse, '.php')

        return pathTempFile