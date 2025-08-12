import json
import time
import yaml
from pathlib import Path
from typing import Optional, Dict

# ---- Add necessary imports ----
from openai import RateLimitError as OpenAiRateLimitError
from requests.exceptions import HTTPError as RequestsHTTPError
from .providers import OpenAIApiAdapter, OpenRouterApiAdapter
from ..utils.logger import myLogger
from ..config import Config  # Import the Config class

# Cache for model aliases
_model_aliases_cache: Optional[Dict[str, str]] = None


def _resolve_model_alias(model_with_prefix: str) -> str:
    """Resolve model aliases from YAML configuration."""
    global _model_aliases_cache

    if _model_aliases_cache is None:
        aliases_path = Path(__file__).parent.parent.parent / "config" / "model-aliases.yaml"
        if aliases_path.exists():
            with open(aliases_path, 'r') as f:
                _model_aliases_cache = yaml.safe_load(f) or {}
        else:
            _model_aliases_cache = {}

    return _model_aliases_cache.get(model_with_prefix, model_with_prefix)


class LLMClient:
    """Client for interacting with LLM providers."""

    def __init__(self, modelWithPrefix: str):
        """Initialize the LLM client with a specific model."""
        self.modelWithPrefix = modelWithPrefix
        self.model = _resolve_model_alias(modelWithPrefix)

        # Determine provider based on model prefix
        if self.model.startswith("openai/"):
            self.provider = OpenAIApiAdapter()
            self.provider_name = "openai"
            self.model = self.model.replace("openai/", "", 1)
        elif self.model.startswith("openrouter/"):
            self.provider = OpenRouterApiAdapter()
            self.provider_name = "openrouter"
            self.model = self.model.replace("openrouter/", "", 1)
        else:
            # Default to openrouter if no prefix
            self.provider = OpenRouterApiAdapter()
            self.provider_name = "openrouter"

    def sendRequest(self, systemPrompt: str, userPrompt: str, verbose: bool = True) -> str:
        """Send PHP code to LLM and return documented version, with retry logic."""
        myLogger.debug(f"LLM Prompt:\n{userPrompt}", highlight=False)

        messages = [
            {"role": "system", "content": systemPrompt},
            {"role": "user", "content": userPrompt}
        ]

        # Calculate the linear step for the delay increase
        # Avoid division by zero if retry count is 1
        if Config.LLM_RETRY_COUNT > 1:
            delay_step = (Config.LLM_RETRY_MAX_DELAY - Config.LLM_RETRY_MIN_DELAY) / (Config.LLM_RETRY_COUNT - 1)
        else:
            delay_step = 0

        last_exception = None

        for attempt in range(Config.LLM_RETRY_COUNT + 1):  # +1 to include the initial attempt
            if attempt > 0:
                # This is a retry attempt
                sleep_duration = Config.LLM_RETRY_MIN_DELAY + (attempt - 1) * delay_step
                sleep_duration = min(sleep_duration, Config.LLM_RETRY_MAX_DELAY)  # Cap the delay

                myLogger.warning(
                    f"Rate limit exceeded. Retrying in {sleep_duration:.1f} seconds... "
                    f"(Attempt {attempt}/{Config.LLM_RETRY_COUNT})"
                )
                time.sleep(sleep_duration)

            try:
                content = self.provider.create_completion(self.model, messages, verbose)
                return content

            except (OpenAiRateLimitError, RequestsHTTPError) as e:
                last_exception = e
                # For requests, we need to check the status code explicitly
                if isinstance(e, RequestsHTTPError):
                    if e.response.status_code != 429:
                        # Not a rate limit error, re-raise immediately
                        raise e
                # For OpenAiRateLimitError, the type itself is enough.
                # Continue to the next attempt in the loop.
                continue

            except Exception as e:
                # Handle other unexpected errors
                debug_info = (
                    f"\nAPI Error Details:\n"
                    f"- Model: {self.model}\n"
                    f"- Provider: {self.provider_name}\n"
                    f"- Prompt Length: {len(userPrompt):,} chars\n"
                )
                raise RuntimeError(f"LLM API failed with a non-retryable error: {str(e)}\n{debug_info}") from e

        # If the loop completes without returning, all retries have failed
        raise RuntimeError(
            f"LLM API request failed after {Config.LLM_RETRY_COUNT} retries. "
            f"Last error: {str(last_exception)}"
        ) from last_exception
