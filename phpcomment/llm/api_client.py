# ---- LLM API Integration ----
# File: phpcomment/llm/api_client.py

import os
import requests
from typing import Optional

class LLMClient:
    """Handle LLM API communication for documentation generation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key required. "
                "Set OPENROUTER_API_KEY environment variable or visit "
                "https://openrouter.ai/keys to get one."
            )
        if not self.api_key.startswith("sk-"):
            raise ValueError("Invalid API key format. Keys should start with 'sk-'")
    
    def generate_documentation(self, php_code: str) -> str:
        """Send PHP code to LLM and return documented version"""
        
        prompt = f"""Analyze this PHP code and:
- Add missing PHPDoc blocks
- Insert section dividers with '// ----'
- Keep ALL original code except documentation
- Wrap response between ||CODE_START|| and ||CODE_END||

PHP code:
{php_code}"""

        try:
            if len(prompt) > 12000:  # Add size validation
                raise ValueError("Code too large for LLM processing (max 12k characters)")
                
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Referer": "https://yourdomain.com",  # Required by OpenRouter
                    "X-Title": "PHPComment/1.0"  # Identify your app with version
                },
                json={
                    "model": "deepseek-ai/deepseek-coder-33b-instruct",  # Corrected model name
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a PHP documentation assistant. Only add PHPDoc comments and section markers."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 4000
                },
                timeout=30
            )
            response.raise_for_status()
            
            content = response.json()['choices'][0]['message']['content']
            if '||CODE_START||' not in content:
                return php_code  # Fallback if format incorrect
                
            return content.split('||CODE_START||')[1].split('||CODE_END||')[0].strip()
            
        except Exception as e:
            debug_info = f"""
            API Error Details:
            - Api Key: {self.api_key[:10]}...
            - Code Length: {len(php_code)} chars
            - Prompt Length: {len(prompt)} chars
            """
            raise RuntimeError(f"LLM API failed: {str(e)}\n{debug_info}") from e
    
    @classmethod
    def for_provider(cls, provider: str):
        return cls()
