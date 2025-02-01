import os
import requests
from .base import LLMProvider
from typing import Optional


class OpenRouterApiAdapter(LLMProvider):
    def __init__(self, base_url: Optional[str] = None):
        self.max_tokens = 1000000
        self.base_url = base_url or "https://openrouter.ai/api/v1"

    def get_api_credentials(self, api_key: Optional[str]):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        key_hint = "OPENROUTER_API_KEY"
        key_prefix = "sk-"
        return self.api_key, key_hint, key_prefix, self.base_url

    def build_request(self, model: str, messages: list):
        headers = {
            "Content-Type": "application/json",
            "Referer": "https://yourdomain.com",
            "X-Title": "PHPComment/1.0"
        }

        data = {
            "model": model,
            "messages": messages,
            "temperature": 0.2,
        }

        return data, headers

    def create_completion(self, model: str, messages: list, verbose: bool = False) -> str:
        try:
            data, headers = self.build_request(model, messages)
            headers.update({
                "Authorization": f"Bearer {self.api_key}"
            })

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']

        except Exception as e:
            raise RuntimeError(f"OpenRouter API error: {str(e)}")
