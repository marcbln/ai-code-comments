from abc import ABC, abstractmethod
from typing import Optional


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
