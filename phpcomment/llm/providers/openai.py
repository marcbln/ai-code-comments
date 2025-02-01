import os
from openai import OpenAI, APIError
from typing import Optional
from .base import LLMProvider


class OpenAIApiAdapter(LLMProvider):
    def __init__(self, base_url: Optional[str] = None):
        self.max_tokens = 8000
        self.client = None
        self.base_url = base_url

    def get_api_credentials(self, api_key: Optional[str]):
        """Get API credentials based on configuration"""
        credentials_config = {
            "deepseek": {
                "env_key": "DEEPSEEK_API_KEY",
                "domain": "deepseek.com"
            },
            "openai": {
                "env_key": "OPENAI_API_KEY",
                "domain": "api.openai.com"
            }
        }

        # Determine provider based on base_url
        provider = next(
            (k for k, v in credentials_config.items() 
             if self.base_url and v["domain"] in self.base_url),
            "openai"  # Default to OpenAI if no match
        )
        
        config = credentials_config[provider]
        api_key = api_key or os.getenv(config["env_key"])
        key_hint = config["env_key"]
        key_prefix = "sk-"
        self.client = OpenAI(
            api_key=api_key,
            base_url=self.base_url if self.base_url else "https://api.openai.com/v1"
        )
        return api_key, key_hint, key_prefix, self.base_url or "https://api.openai.com/v1"

    def build_request(self, model: str, messages: list):
        # Return empty dicts since we'll use the client directly
        return {}, {}

    def create_completion(self, model: str, messages: list, verbose: bool = False):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except APIError as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
