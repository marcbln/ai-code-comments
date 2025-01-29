# Masterplan for PHP Commenting Utility

## Overview
A CLI utility that intelligently adds PHPDoc docblocks and section comments (`// ----`) to PHP files using an LLM (e.g., OpenRouter, Deepseek, or OpenAI). The tool ensures the original code remains unchanged and provides a `--dry-run` flag to preview changes.

---

## Objectives
1. **Automate documentation**: Add PHPDoc docblocks and section comments to legacy PHP code.
2. **Preserve code integrity**: Ensure only comments are added/edited, with no modifications to the original code.
3. **Developer-friendly**: Provide a simple, verbose CLI tool with colorful output using `rich`.

---

## Target Audience
- Developers working with legacy PHP codebases.
- Open-source contributors looking to improve code documentation.

---

## Core Features
1. **PHPDoc generation**: Automatically add standard PHPDoc docblocks for classes and functions.
2. **Section comments**: Insert `// ----` comments to group related code blocks.
3. **Code integrity validation**: Use `nikic/PHP-Parser` to ensure no code changes were made.
4. **Dry-run mode**: Preview changes without modifying the file (`--dry-run` flag).
5. **Verbose output**: Show progress and actions taken during execution.
6. **Error handling**: Print error messages and abort on failures.

---

## User Interface Design Principles
1. **CLI-first**: The tool is designed for use in the terminal.
2. **Verbose by default**: Show progress and actions taken during execution.
3. **Colorful output**: Use `rich` to enhance readability and user experience.
4. **Dry-run mode**: Allow users to preview changes without modifying files.

---

## Security Considerations
- **API key management**: Users provide their LLM API key via environment variables.
- **Code integrity**: Use external commands to validate code integrity.

---

## Development Phases

### Phase 1: Core Functionality
- 1.1 Build the CLI interface using Typer. Use `uv` with build system `hatchling`
- 1.2 Integrate the LLM API for generating PHPDoc and section comments.
- 1.3 Implement file overwriting and dry-run mode.

### Phase 3: Open-Source Setup
- Add a README with usage instructions.
- Choose an open-source license (e.g., MIT).
- Set up GitHub repository with basic CI/CD for testing.

---

## Future Expansion Possibilities
1. **Support for other languages**: Extend the tool to support Smarty, Twig, JavaScript, etc.
2. **Configuration options**: Allow users to customize comment styles or LLM prompts.
3. **IDE integration**: Develop plugins for popular IDEs like VS Code or PHPStorm.
4. **Batch processing**: Add support for processing entire directories or projects.



