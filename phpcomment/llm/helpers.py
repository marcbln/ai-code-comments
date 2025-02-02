import re

class LlmResponseHelpers:
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
