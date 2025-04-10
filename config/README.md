# Configuration Files

This directory contains configuration files for the `aicoder` application.

## Model Aliasing (`model-aliases.yaml`)

The `model-aliases.yaml` file allows you to define short, memorable aliases for longer LLM model identifiers. This simplifies configuration in profiles and potentially command-line usage.

**Format:**

The file uses a simple YAML dictionary format:

```yaml
# alias: full_model_identifier
gpt4o: openai/gpt-4o-2024-05-13
claude35: openrouter/anthropic/claude-3.5-sonnet
# ... add more aliases as needed
```

**Usage:**

When the application needs a model identifier (e.g., from a profile in `config/profiles/` or a `--model` CLI argument), it first checks if the provided string matches an alias key in `model-aliases.yaml`.

*   If a match is found, the application automatically replaces the alias with its corresponding full model identifier value before proceeding.
*   If no match is found, the application uses the provided string as is.

This resolution happens automatically within the `LLMClient`.

**Example:**

If `model-aliases.yaml` contains `claude35: openrouter/anthropic/claude-3.5-sonnet`, you can use `claude35` in your profile files (like `analyzer-profiles.yaml` or `commenter-profiles.yaml`) instead of the full identifier:

```yaml
# In config/profiles/analyzer-profiles.yaml
profiles:
  sonnet:
    model: claude35 # Alias will be resolved automatically
    prompt: full-analysis
```

## Profiles (`profiles/`)

The `profiles/` subdirectory contains YAML files defining different operational profiles for tasks like analysis (`analyzer-profiles.yaml`) and commenting (`commenter-profiles.yaml`). These profiles specify the model (potentially using an alias), prompts, and strategies to use for specific tasks.