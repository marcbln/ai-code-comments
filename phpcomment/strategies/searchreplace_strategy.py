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
            - Output MUST use the conflict marker format with `<<<<<<<` `=======`, and `>>>>>>>` markers, like:
            ```
            <<<<<<< SEARCH
            [exact content]
            =======
            [new content]
            >>>>>>> REPLACE
            ````
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
        Parse and apply search/replace blocks from the LLM response
        
        Args:
            original_content: The original file content
            response: The LLM response containing search/replace blocks
            
        Returns:
            str: The modified content with search/replace blocks applied
        """
        # Regular expression to match search/replace blocks
        block_pattern = r'<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE'
        
        # Find all search/replace blocks
        blocks = re.findall(block_pattern, response, re.DOTALL)
        
        if not blocks:
            myLogger.warning("No search/replace blocks found in response")
            return original_content
        
        modified_content = original_content
        
        # Apply each search/replace block
        for search_text, replace_text in blocks:
            try:
                # Handle PHP namespace backslashes by using raw strings
                search_text = search_text.replace('\\', r'\\')  # Escape backslashes for regex
                search_re = re.compile(search_text, re.DOTALL)
                
                # Apply the replacement (only first occurrence)
                new_content, count = search_re.subn(replace_text, modified_content, count=1)
                
                if count == 0:
                    myLogger.warning(f"Search text not found: {search_text[:50]}...")
                else:
                    modified_content = new_content
                    myLogger.debug(f"Successfully applied search/replace block")
            except re.error as e:
                myLogger.error(f"Regex error in search pattern: {str(e)}")
            except Exception as e:
                myLogger.error(f"Error applying search/replace block: {str(e)}")
        
        return modified_content
