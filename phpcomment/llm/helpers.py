import os
import re
import tempfile
import uuid
from pathlib import Path
from phpcomment.utils.logger import myLogger


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

    # @classmethod
    # def writeTempCodeFile(cls, content: str, suffix: str) -> Path:
    #     """
    #     Write content to temporary file
    #
    #     Args:
    #         content: The content to write to the temporary file
    #         suffix: The suffix to use for the temporary file (e.g., '.php')
    #     """
    #     tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
    #     myLogger.info(f"Writing temporary file to {tmp_file.name}")
    #     myLogger.debug(f"Content of {tmp_file.name}:\n{content}")
    #     tmp_file.write(content)
    #     tmp_file.close()
    #
    #     return Path(tmp_file.name)

    @staticmethod
    def writeTempCodeFile(content: str, suffix: str) -> Path:
        """
        Write content to temporary file

        Args:
            content: The content to write to the temporary file
            suffix: The suffix to use for the temporary file (e.g., '.php')
        """
        """Create a temporary file with given content and return its path."""
        temp_dir = "/tmp"  # or use a config value
        filename = f"temp_{uuid.uuid4()}{suffix}"
        file_path = os.path.join(temp_dir, filename)

        with open(file_path, 'w') as f:
            myLogger.info(f"Writing temporary file to {file_path}")
            myLogger.debug(f"Content of {file_path}:\n{content}")
            f.write(content)

        return Path(file_path)


    @staticmethod
    def writeTempFileV2(basename: str, content: str, suffix: str) -> Path:
        """
        Write patched code to temporary file

        Args:
            basename: The base name of the temporary file (e.g. a hash of content of original file")
            content: The patched code to write to the temporary file
            suffix: The suffix to use for the temporary file (e.g., '_patched.php' or '.diff')
        """
        """Create a temporary patched code file using the same hash."""
        code_path = os.path.join("/tmp", f"{basename}{suffix}")

        with open(code_path, 'w') as f:
            myLogger.info(f"💾 writing file {code_path}")
            f.write(content)

        return Path(code_path)

    @classmethod
    def copyToTempfile(cls, pathOrigFile: Path) -> Path:
        # detect suffix
        suffix = pathOrigFile.suffix
        # Copy original file to temporary file
        tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
        myLogger.debug(f"💾 Copying {pathOrigFile} to {tmp_file.name}")
        with open(pathOrigFile, 'r') as file:
            tmp_file.write(file.read())
        tmp_file.close()

        return Path(tmp_file.name)


    @staticmethod
    def extract_code_blocks(text):
        """
        Extracts code blocks from text and replaces them with numbered placeholders.

        Args:
            text (str): Input text containing code blocks marked with triple backticks

        Returns:
            tuple: (modified_text, list_of_blocks)
                - modified_text: Original text with code blocks replaced by [CODE_BLOCK_{n}]
                - list_of_blocks: List of extracted code blocks with their language info
        """
        # Pattern to match code blocks including language identifier
        pattern = r'```([^\n]*)\n(.*?)```'
        blocks = []

        def replace_func(match):
            language = match.group(1).strip()
            code = match.group(2).strip()
            # blocks.append({
            #     'language': language,
            #     'code': code
            # })
            blocks.append(code)
            return f'[CODE_BLOCK_{len(blocks)}]'

        # Replace code blocks with placeholders and collect blocks
        modified_text = re.sub(pattern, replace_func, text, flags=re.DOTALL)

        return modified_text, blocks
