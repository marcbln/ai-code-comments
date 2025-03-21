import json
import time
from typing import Optional

from .providers import OpenAIApiAdapter, OpenRouterApiAdapter
from ..utils.logger import myLogger


class LLMClient:
    """Handle LLM API communication for documentation generation"""


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





    def sendRequest(self, systemPrompt: str, userPrompt: str, verbose: bool = True) -> str:
        """Send PHP code to LLM and return documented version"""



        myLogger.debug(f"LLM Prompt:\n{userPrompt}", highlight=False)

        try:
            # if len(prompt) > 12000:  # Add size validation
            #     raise ValueError("Code too large for LLM processing (max 12k characters)")

            messages = [
                {
                    "role": "system",
                    "content": systemPrompt
                },
                {
                    "role": "user",
                    "content": userPrompt
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
            myLogger.debug(f"Sending request to {self.model}...")
            myLogger.debug("Full Request Details:")
            myLogger.debug(f"URL: {self.base_url}/chat/completions")
            myLogger.debug(f"Headers: {json.dumps(requestHeaders, indent=4)}")
            myLogger.debug(f"Body: {json.dumps(requestBody, indent=4)}")

            content = self.provider.create_completion(self.model, messages, verbose)

            return content

        except Exception as e:
            print(f"======= Error: {str(e)} =======")

            debug_info = (
                "\nAPI Error Details:\n"
                f"- Model: {self.model}\n"
                f"- Provider: {self.provider_name}\n"
                f"- API Key: {self.api_key[:10]}...{self.api_key[-4:]}\n"
                f"- Prompt Length: {len(userPrompt)} chars\n"
            )
            raise RuntimeError(f"LLM API failed: {str(e)}\n{debug_info}") from e
