import re
import tempfile
from pathlib import Path


class MyHelpers:
    @staticmethod
    def strip_code_block_markers(content: str) -> str:
        """
        Remove code block markers like ```php or ```diff from start/end

        Args:
            content: The response content from LLM

        Returns:
            Cleaned content without markdown code blocks
        """
        content = re.sub(r'^```\w*\n', '', content)  # Remove opening markers
        content = re.sub(r'\n```$', '', content)  # Remove closing markers
        return content



    @staticmethod
    def file_put_contents(pathDestFile: str, content: str) -> None:
        """Write content to file"""
        file = open(pathDestFile, 'w')
        file.write(content)
        file.close()

    @classmethod
    def writeTempCodeFile(cls, content: str, suffix: str = '.php'):
        # Create temporary file with new content
        tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
        tmp_path = Path(tmp_file.name)
        print(f"📝 Writing temporary file to {tmp_path} with content:\n{content}")
        tmp_file.write(content)
        tmp_file.close()

        return tmp_path
