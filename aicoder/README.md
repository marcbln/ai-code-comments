# AI Coder

A CLI tool for automatically adding PHPDoc blocks and section comments to PHP code. 
And more... suggesting code improvements, refactoring, etc...

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
aicoder --help
aicoder comment --help
```

## Configuration
Create `.env` file:
```ini
LLM_API_KEY=your_api_key_here
```
