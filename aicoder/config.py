# config.py
class Config:
    # Default profile to use if none specified
    APP_VERSION = "1.0.0"
    DEFAULT_PROFILE = "default"

    # Default temperature setting for LLM requests
    DEFAULT_TEMPERATURE = 0.0

    # Retry configuration for LLM requests
    LLM_RETRY_COUNT = 5
    LLM_RETRY_MIN_DELAY = 2
    LLM_RETRY_MAX_DELAY = 30

    # Legacy model setting - kept for backward compatibility
    # Will be used if no profile is specified and no model is provided via CLI
    # see https://aider.chat/docs/leaderboards/
    # DEFAULT_MODEL = "openrouter/deepseek/deepseek-r1-distill-qwen-32b"
    # DEFAULT_MODEL = "openrouter/allenai/llama-3.1-tulu-3-405b"
    # DEFAULT_MODEL = "openrouter/qwen/qwen2.5-vl-72b-instruct:free"
    # DEFAULT_MODEL = "openrouter/qwen/qwen-2.5-coder-32b-instruct"
    # DEFAULT_MODEL = "openrouter/qwen/qwen-max"
    # DEFAULT_MODEL = "openrouter/anthropic/claude-3.5-sonnet"
    # DEFAULT_MODEL = "openrouter/google/gemini-2.0-flash-exp:free"
