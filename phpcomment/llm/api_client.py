# ---- LLM API Integration ----
# File: phpcomment/llm/api_client.py

import os
import requests
from typing import Optional

class LLMClient:
    """Handle LLM API communication for documentation generation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
    
    def generate_documentation(self, php_code: str) -> str:
        """Send PHP code to LLM and return documented version"""
        if not self.api_key:
            raise ValueError("Missing LLM API key - set OPENROUTER_API_KEY environment variable")
        
        prompt = f"""Analyze this PHP code and:
- Add missing PHPDoc blocks
- Insert section dividers with '// ----'
- Keep ALL original code except documentation
- Wrap response between ||CODE_START|| and ||CODE_END||

PHP code:
{php_code}"""

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "deepseek/deepseek-coder-33b-instruct",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                },
                timeout=30
            )
            response.raise_for_status()
            
            content = response.json()['choices'][0]['message']['content']
            if '||CODE_START||' not in content:
                return php_code  # Fallback if format incorrect
                
            return content.split('||CODE_START||')[1].split('||CODE_END||')[0].strip()
            
        except Exception as e:
            raise RuntimeError(f"LLM API failed: {str(e)}") from e
    
    @classmethod
    def for_provider(cls, provider: str):
        return cls()
