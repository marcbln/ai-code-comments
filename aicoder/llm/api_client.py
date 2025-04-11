import json
import time
import yaml
from pathlib import Path
from typing import Optional, Dict

from .providers import OpenAIApiAdapter, OpenRouterApiAdapter
from ..utils.logger import myLogger


def _resolve_model_alias(model_input: str) -> str:
    """Resolve model alias to full identifier if configured.
    
    Args:
        model_input: The input model name which may be an alias
        
    Returns:
        The resolved model name or original input if no alias found
    """
    try:
        # Look for config file in project root/config directory
        config_path = Path(__file__).parent.parent.parent / "config" / "model-aliases.yaml"
        if not config_path.exists():
            myLogger.debug(f"No model aliases file found at {config_path}")
            return model_input
            
        with open(config_path) as f:
            aliases = yaml.safe_load(f) or {}
            
        if model_input in aliases:
            resolved = aliases[model_input]
            myLogger.info(f"Resolved model alias '{model_input}' to '{resolved}'")
            return resolved
            
    except Exception as e:
        myLogger.warning(f"Failed to load model aliases: {str(e)}")
        
    return model_input


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
        # Resolve model alias if configured
        resolved_model = _resolve_model_alias(modelWithPrefix)
        self.model = resolved_model
        self.provider_name = None
        self.provider = None

        # Find matching provider config using the resolved model name
        for provider_name, config in self.PROVIDER_CONFIGS.items():
            for prefix in config["prefixes"]:
                if resolved_model.startswith(prefix):  # Check the resolved model name
                    self.provider_name = provider_name
                    self.model = resolved_model.replace(prefix, "", 1) # Update self.model from resolved name
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
