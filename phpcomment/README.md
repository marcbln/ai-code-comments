# PHP Documentation Automator

A CLI tool for automatically adding PHPDoc blocks and section comments to PHP code.

## Features

- Automatic PHPDoc generation using LLMs
- Section comment insertion for code organization
- Dry-run mode for safe previews
- Code integrity validation

## Quick Start

```bash
# Install with uv (or use pip)
uv pip install -e .

# Get help
phpcomment --help
phpcomment comment --help
```

## Configuration
Create `.env` file:
```ini
LLM_API_KEY=your_api_key_here
```
