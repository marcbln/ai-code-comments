import json
import re
import time
from typing import Dict, Type, Optional
from .prompts import DocumentationPrompts
from .providers import LLMProvider, OpenAIApiAdapter, OpenRouterApiAdapter


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


    @staticmethod
    def strip_code_block_markers(content: str) -> str:
        # Remove code block markers like ```php or ```diff from start/end
        content = re.sub(r'^```\w*\n', '', content)  # Remove opening markers
        content = re.sub(r'\n```$', '', content)  # Remove closing markers
        return content

    @staticmethod
    def clean_diff(diff: str) -> str:
        """
        Removes line numbers from the @@ ... @@ headers in a unified diff.

        Args:
            diff (str): The diff content as a string.

        Returns:
            str: The cleaned diff without line numbers in @@ ... @@ headers.
        """
        # Regex to match @@ ... @@ headers with line numbers
        header_pattern = re.compile(r"@@ -\d+(,\d+)? \+\d+(,\d+)? @@")

        # Replace the header with just @@ @@
        cleaned_diff = header_pattern.sub("@@ ... @@", diff)

        return cleaned_diff




    def improveDocumentation(self, php_code: str, use_udiff_coder: bool, verbose: bool = False) -> str:
        """Send PHP code to LLM and return documented version"""

        systemPrompt, userPrompt = DocumentationPrompts.get_full_prompt(php_code, use_udiff_coder)

        print(f"LLM Prompt:\n{userPrompt}")

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
            if verbose:
                print(f"🚀 Sending request to {self.model}...")
                print("🔍 Full Request Details:")
                print(f"URL: {self.base_url}/chat/completions")
                print(f"Headers: {json.dumps(requestHeaders, indent=4)}")
                print(f"Body: {json.dumps(requestBody, indent=4)}")

            content = self.provider.create_completion(self.model, messages, verbose)

            # In the original code:
            content = LLMClient.strip_code_block_markers(content)

            if use_udiff_coder:
                content = LLMClient.clean_diff(content)

            return content

        except Exception as e:
            print(f"======= Error: {str(e)} =======")

            debug_info = f"""
            API Error Details:
            - Model: {self.model}
            - Provider: {self.provider}
            - API Key: {self.api_key[:10]}...{self.api_key[-4:]}
            - Code Length: {len(php_code)} chars
            - Prompt Length: {len(userPrompt)} chars
            """
            raise RuntimeError(f"LLM API failed: {str(e)}\n{debug_info}") from e
