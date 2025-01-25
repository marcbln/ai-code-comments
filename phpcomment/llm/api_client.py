# ---- LLM API Integration ----
import json
import os
import time
from typing import Optional, Dict, Type
from abc import ABC, abstractmethod
import requests
from openai import OpenAI, APIError


class LLMProvider(ABC):
    """Base class for LLM providers"""

    @abstractmethod
    def get_api_credentials(self, api_key: Optional[str]) -> tuple:
        """Get API credentials and configuration"""
        pass

    @abstractmethod
    def create_completion(self, model: str, messages: list, verbose: bool = False) -> str:
        """Create a completion using the provider's API"""
        pass


class OpenRouterApiAdapter(LLMProvider):
    def __init__(self, base_url: Optional[str] = None):
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
            "max_tokens": 4000
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


class OpenAIApiAdapter(LLMProvider):
    def __init__(self, base_url: Optional[str] = None):
        self.client = None
        self.base_url = base_url

    def get_api_credentials(self, api_key: Optional[str]):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        key_hint = "OPENAI_API_KEY"
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
                max_tokens=4000
            )
            return response.choices[0].message.content
        except APIError as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")


class LLMClient:
    """Handle LLM API communication for documentation generation"""

    PROVIDER_CLASSES: Dict[str, Type[LLMProvider]] = {
        "openrouter": OpenRouterApiAdapter,
        "openai": OpenAIApiAdapter,
    }

    PROVIDER_CONFIGS = {
        "openrouter": {
            "adapter": OpenRouterApiAdapter,
            "prefixes": ["openrouter/"],
        },
        "openai": {
            "adapter": OpenAIApiAdapter,
            "prefixes": ["openai/"],
            "base_url": "https://api.openai.com/v1"
        },
        "deepseek": {
            "adapter": OpenAIApiAdapter,
            "prefixes": ["deepseek/"],
            "base_url": "https://api.deepseek.com/v1"
        }
    }

    def __init__(self, modelWithPrefix: str, api_key: Optional[str] = None):
        self.model = modelWithPrefix
        self.provider_name = None
        self.provider = None

        # Find matching provider config
        for provider_name, config in self.PROVIDER_CONFIGS.items():
            for prefix in config["prefixes"]:
                if modelWithPrefix.startswith(prefix):
                    self.provider_name = provider_name
                    self.model = modelWithPrefix.replace(prefix, "", 1)
                    break
            if self.provider_name:
                break

        if not self.provider_name:
            valid_prefixes = [
                prefix 
                for config in self.PROVIDER_CONFIGS.values() 
                for prefix in config["prefixes"]
            ]
            raise ValueError(
                "Model must include provider prefix. Valid prefixes: " +
                ", ".join(valid_prefixes)
            )

        # Get provider configuration
        config = self.PROVIDER_CONFIGS[self.provider_name]
        adapter_class = config["adapter"]
        base_url = config.get("base_url")

        # Instantiate provider with configuration
        self.provider = adapter_class(base_url=base_url)

        # Get credentials from provider implementation
        self.api_key, key_hint, key_prefix, self.base_url = (
            self.provider.get_api_credentials(api_key)
        )

        # Validate credentials
        if not self.api_key:
            raise ValueError(
                f"{self.provider_name.capitalize()} API key required. "
                f"Set {key_hint} environment variable or pass explicitly."
            )
        if not self.api_key.startswith(key_prefix):
            raise ValueError(f"Invalid {self.provider_name} API key format. Should start with '{key_prefix}'")

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
            # Get provider-specific request configuration
            requestBody, extra_headers = self.provider.build_request(self.model, messages)

            requestHeaders = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                **extra_headers
            }

            api_start = time.time()
            if verbose:
                print(f"🚀 Sending request to {self.model}...")
                print("🔍 Full Request Details:")
                print(f"URL: {self.base_url}/chat/completions")
                print(f"Headers: {json.dumps(requestHeaders, indent=4)}")
                print(f"Body: {json.dumps(requestBody, indent=4)}")

            content = self.provider.create_completion(self.model, messages, verbose)

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
