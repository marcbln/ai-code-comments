import os
import requests
from .base import LLMProvider
from typing import Optional

from ...config import Config


class OpenRouterApiAdapter(LLMProvider):
    def __init__(self, base_url: Optional[str] = None):
        self.max_tokens = 1000000
        self.base_url = base_url or "https://openrouter.ai/api/v1"
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")

    def get_api_credentials(self, api_key: Optional[str]):
        # Use provided api_key or fall back to instance api_key
        api_key_to_use = api_key or self.api_key
        if not api_key_to_use:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")
        key_hint = "OPENROUTER_API_KEY"
        key_prefix = "sk-"
        return api_key_to_use, key_hint, key_prefix, self.base_url

    def build_request(self, model: str, messages: list):
        headers = {
            "Content-Type": "application/json",
            "Referer": "https://yourdomain.com",
            "X-Title": "PHPComment/1.0"
        }

        data = {
            "model": model,
            "messages": messages,
            "temperature": Config.DEFAULT_TEMPERATURE,
        }

        return data, headers

    def create_completion(self, model: str, messages: list, verbose: bool = False) -> str:
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")
        
        try:
            data, headers = self.build_request(model, messages)
            headers.update({
                "Authorization": f"Bearer {self.api_key}"
            })

            if verbose:
                print(f"Making request to OpenRouter API with model: {model}")

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            response_json = response.json()
            if 'choices' not in response_json:
                raise RuntimeError(f"OpenRouter API error: 'choices' key missing in response. Full response: {response_json}")
            return response_json['choices'][0]['message']['content']

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"OpenRouter API request failed: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"OpenRouter API error: {str(e)}")
