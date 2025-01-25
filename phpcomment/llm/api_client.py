# ---- LLM API Integration ----
# File: phpcomment/llm/api_client.py
import json
import os
import time
import requests
from typing import Optional

class LLMClient:
    """Handle LLM API communication for documentation generation"""
    
    def __init__(self, modelWithPrefix: str, api_key: Optional[str] = None):

        PROVIDER_PREFIXES = {
            "openrouter/": "openrouter",
            "deepseek/": "deepseek",
            # ...
            # "anthropic/": "anthropic",
            # "azure/": "azure",
        }

        self.provider = None
        self.model = None

        for prefix, provider_name in PROVIDER_PREFIXES.items():
            if modelWithPrefix.startswith(prefix):
                self.model = modelWithPrefix.replace(prefix, "")
                self.provider = provider_name
                break

        if self.provider == "openrouter":
            self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
            self.base_url = "https://openrouter.ai/api/v1"
            key_hint = "OPENROUTER_API_KEY"
            key_prefix = "sk-"
        else:
            self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
            self.base_url = "https://api.deepseek.com/v1"
            key_hint = "DEEPSEEK_API_KEY"
            key_prefix = "sk-"

        if not self.api_key:
            raise ValueError(
                f"{self.provider.capitalize()} API key required. "
                f"Set {key_hint} environment variable."
            )
        if not self.api_key.startswith(key_prefix):
            raise ValueError(f"Invalid {self.provider} API key format. Keys should start with '{key_prefix}'")
    
    def improveDocumentation(self, php_code: str, verbose: bool = False) -> str:
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

            messages = [
                {
                    "role": "system",
                    "content": "You are a PHP documentation expert. Add complete PHPDoc blocks and section comments."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            requestBody = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 4000
            }
            requestHeaders = {
                "Authorization": f"Bearer {self.api_key}",
                "Referer": "https://yourdomain.com" if self.provider == "openrouter" else "",
                "X-Title": "PHPComment/1.0",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }



            api_start = time.time()
            if verbose:
                print(f"🚀 Sending request to {self.model}...")
                print("🔍 Full Request Details:")
                print(f"URL: {self.base_url}/chat/completions")
                print(f"Headers: {json.dumps(requestHeaders, indent=4)}")
                print(f"Body: {json.dumps(requestBody, indent=4)}")

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=requestHeaders,
                json=requestBody,
                timeout=30
            )
            response.raise_for_status()
            
            response_time = time.time() - api_start
            if verbose:
                print(f"📥 Received response in {response_time:.1f}s")
                print("🔍 Full Response Details:")
                print(f"Status Code: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
                print(f"Content: {response.text[:1000]}...")  # Truncate long responses
            
            content = response.json()['choices'][0]['message']['content']

            print(f'Response: {json.dumps(response.json(), indent=4)}')

            if '||CODE_START||' not in content and '<?php' in content:
                return content
                
            return content.split('||CODE_START||')[-1].split('||CODE_END||')[0].strip()
            
        except Exception as e:
            print(f"======= Error: {str(e)} =======")

            debug_info = f"""
            API Error Details:
            - Model: {self.model}
            - Provider: {self.provider}
            - API Key: {self.api_key[:10]}...{self.api_key[-4:]}
            - Code Length: {len(php_code)} chars
            - Prompt Length: {len(prompt)} chars
            """
            raise RuntimeError(f"LLM API failed: {str(e)}\n{debug_info}") from e

    @classmethod
    def for_provider(cls, provider: str):
        return cls()
