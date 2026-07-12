# aicoder

CLI tool for automatically adding PHPDoc blocks and section comments to PHP (and Twig) files using LLMs.

## Features

- **PHPDoc Generation** — Automatically generates PHPDoc blocks for PHP classes, methods, functions, and properties
- **TwigDoc Support** — Adds documentation comments to Twig templates
- **Code Analysis** — Get AI-powered feedback and improvement suggestions for your code
- **Multiple LLM Providers** — OpenAI, OpenRouter, and more
- **Patch Strategies** — Supports wholefile, udiff, and searchreplace patch formats
- **Patch Application** — Standalone patch tool (`patch` command) supporting multiple patcher versions
- **Code Validation** — Validates that generated documentation doesn't alter code functionality (PHP AST comparison)
- **Profile System** — Preset configurations combining model and strategy settings
- **Model Aliasing** — Short aliases for long model identifiers
- **Dry-Run Mode** — Preview changes without modifying files

## Installation

```bash
# Install with uv
uv pip install -e .

# Or with pip
pip install -e .
```

Requires Python 3.8+ and PHP (for code validation).

## Quick Start

```bash
# Add documentation to a PHP file
aicoder add-comments path/to/file.php

# Use a specific profile
aicoder add-comments --profile sonnet path/to/file.php

# Override model and strategy
aicoder add-comments --model openrouter/anthropic/claude-3.5-sonnet --strategy udiff file.php

# Analyze code
aicoder analyze path/to/file.php

# List available profiles
aicoder list-profiles

# Apply a patch file
patch --help
```

## Configuration

Create a `.env` file:

```ini
LLM_API_KEY=your_api_key_here
```

### Profiles

Profiles are defined in `config/profiles/` as YAML files. They combine a model and a strategy:

- `analyzer-profiles.yaml` — Profiles for the `analyze` command
- `commenter-profiles.yaml` — Profiles for the `add-comments` command

### Model Aliases

Define shortcuts in `config/model-aliases.yaml`:

```yaml
sonnet35: openrouter/anthropic/claude-3.5-sonnet
gpt4o: openai/gpt-4o-2024-05-13
```

## Usage

### `aicoder add-comments`

```bash
aicoder add-comments [OPTIONS] FILE_PATH
```

Options:
- `--profile, -p` — Profile to use (default: "default")
- `--model` — Override model from profile
- `--strategy` — Override strategy: wholefile, udiff, or searchreplace
- `--verbose, -v` — Enable verbose output

### `aicoder analyze`

```bash
aicoder analyze [OPTIONS] FILE
```

Options:
- `--profile, -p` — Analysis profile to use
- `--model` — Override model from profile
- `--verbose, -v` — Enable verbose output

### `patch`

```bash
patch SOURCE_FILE PATCH_FILE [DEST_FILE]
```

Options:
- `--verbose, -v` — Enable verbose output
- `--dry-run` — Show result without writing files

## Patch Strategies

- **wholefile** — LLM returns the complete modified file
- **udiff** — LLM returns a unified diff patch
- **searchreplace** — LLM returns search/replace pairs

## Project Structure

```
aicoder/
├── aicoder/               # Main package
│   ├── cli/               # CLI entry points and commands
│   ├── core/              # Core processing logic
│   ├── llm/               # LLM client and providers
│   ├── strategies/        # Patch strategies
│   ├── utils/             # Utilities (patchers, logger, etc.)
│   └── validation/        # AST validation
├── config/                # Configuration files
│   └── profiles/          # YAML profile definitions
├── tests/                 # Test suite
└── compare-php-files/     # PHP AST comparison scripts
```
