import re
from pathlib import Path
from typing import Optional
from textwrap import dedent

from .base import ChangeStrategy
from phpcomment.utils.logger import myLogger
from phpcomment.llm.helpers import MyHelpers


class SearchReplaceStrategy(ChangeStrategy):
    """
    Strategy for handling search/replace style changes.
    
    This strategy processes LLM responses formatted as search/replace blocks
    and applies them to the original file.
    """
    
    @staticmethod
    def get_prompt_additions() -> str:
        """Return strategy-specific prompt additions for search/replace format"""
        return dedent("""
            - Output MUST use the conflict marker format with `<<<<<<<`, `=======`, and `>>>>>>>` markers, but ONLY for meaningful changes
            - Include at most 3 lines of unchanged context before and after each code change
            - For each change, format as:
            ```            
            <<<<<<< SEARCH
            [exact content - include 3 lines before and after the modified content for context]
            =======
            [new content]
            >>>>>>> REPLACE
            ```
            - For multiple changes in the same file, show each change as a separate conflict block
            - DO NOT return search replace blocks if there are no changes
        """)
    
    def process_llm_response(self, llmResponseRaw: str, pathOrigFile: Path) -> Optional[Path]:
        """
        Process LLM response containing search/replace conflict markers
        
        Args:
            llmResponseRaw: The raw response from the LLM containing search/replace blocks
            pathOrigFile: Path to the original PHP file
            
        Returns:
            Optional[Path]: Path to the modified file or None if processing failed
        """
        myLogger.debug(f"Processing response with SearchReplaceStrategy")
        
        # Clean up the response to extract just the code blocks
        cleaned_response = MyHelpers.strip_code_block_markers(llmResponseRaw)
        
        # Read the original file content
        with open(pathOrigFile, 'r') as f:
            original_content = f.read()
        
        # Apply the search/replace blocks
        modified_content = self._apply_search_replace_blocks(original_content, cleaned_response)
        
        # Write the modified content to a temporary file
        temp_file = MyHelpers.writeTempCodeFile(modified_content, "-searchreplace.php")
        return temp_file


    def _apply_search_replace_blocks(self, original_content: str, response: str) -> str:
        """
        Parse and apply search/replace blocks from the LLM response using line-by-line processing

        Args:
            original_content: The original file content
            response: The LLM response containing search/replace blocks

        Returns:
            str: The modified content with search/replace blocks applied
        """
        # Split response into lines for processing
        response_lines = response.split('\n')

        modified_content = original_content
        search_text = []
        replace_text = []
        current_block = None

        # Parse the response line by line to extract search/replace blocks
        for line in response_lines:
            if line.startswith('<<<<<<< SEARCH'):
                current_block = 'search'
                search_text = []
            elif line.startswith('======='):
                current_block = 'replace'
                replace_text = []
            elif line.startswith('>>>>>>> REPLACE'):
                if search_text and replace_text:
                    # Convert lists to strings
                    search_str = '\n'.join(search_text)
                    replace_str = '\n'.join(replace_text)

                    # Find and replace the first occurrence
                    try:
                        search_pos = modified_content.find(search_str)
                        if search_pos != -1:
                            before = modified_content[:search_pos]
                            after = modified_content[search_pos + len(search_str):]
                            modified_content = before + replace_str + after
                            myLogger.debug(f"Successfully applied search/replace block")
                        else:
                            myLogger.warning(f"Search text not found: {search_str[:50]}...")
                    except Exception as e:
                        myLogger.error(f"Error applying search/replace block: {str(e)}")

                current_block = None
                search_text = []
                replace_text = []
            elif current_block == 'search':
                search_text.append(line)
            elif current_block == 'replace':
                replace_text.append(line)

        return modified_content