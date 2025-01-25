# Masterplan for PHP Commenting Utility

## Overview
A CLI utility that intelligently adds PHPDoc docblocks and section comments (`// ----`) to PHP files using an LLM (e.g., OpenRouter, Deepseek, or OpenAI). The tool ensures the original code remains unchanged and provides a `--dry-run` flag to preview changes. The utility will be open-sourced on GitHub.

---

## Objectives
1. **Automate documentation**: Add PHPDoc docblocks and section comments to legacy PHP code.
2. **Preserve code integrity**: Ensure only comments are added/edited, with no modifications to the original code.
3. **Developer-friendly**: Provide a simple, verbose CLI tool with colorful output using `rich`.
4. **Open-source**: Make the tool available on GitHub for broader use.

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

## High-Level Technical Stack
### Frameworks and Libraries
- **Typer**: For building the CLI with type hints for arguments/options.
- **rich**: For colorful and user-friendly terminal output.
- **requests**: For making API calls to the LLM (e.g., OpenRouter, Deepseek).
- **nikic/PHP-Parser**: For parsing and comparing PHP files during validation.

### Python Conventions
- **Python version**: 3.10+.
- **Type hints**: Mandatory for functions.
- **Style**: Follow [PEP8](https://peps.python.org/pep-0008/) and [PEP257](https://peps.python.org/pep-0257/).
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes.
- **F-strings**: Preferred for string formatting.
- **Modularity**: Code organized into logical modules/files.
- **Section comments**: Use `# ----` to explain key parts of the code.

---

## Conceptual Data Model
Not applicable for this utility, as it does not involve persistent data storage.

---

## User Interface Design Principles
1. **CLI-first**: The tool is designed for use in the terminal.
2. **Verbose by default**: Show progress and actions taken during execution.
3. **Colorful output**: Use `rich` to enhance readability and user experience.
4. **Dry-run mode**: Allow users to preview changes without modifying files.

---

## Security Considerations
1. **API key management**: Users provide their LLM API key via environment variables.
2. **Error handling**: Ensure sensitive information (e.g., API keys) is not leaked in error messages.
3. **Code integrity**: Use `nikic/PHP-Parser` to validate that only comments are modified.

---

## Development Phases
### Phase 1: Core Functionality
- Build the CLI interface using Typer.
- Integrate the LLM API for generating PHPDoc and section comments.
- Implement file overwriting and dry-run mode.
- Add verbose output using `rich`.

### Phase 2: Validation Script
- Develop a separate CLI script using `nikic/PHP-Parser` to validate code integrity.
- Ensure the script can detect and report unintended code changes.

### Phase 3: Open-Source Setup
- Add a README with usage instructions.
- Choose an open-source license (e.g., MIT).
- Set up GitHub repository with basic CI/CD for testing.

---

## Potential Challenges and Solutions
1. **LLM prompt design**: Ensure the LLM generates accurate and consistent comments.  
   - *Solution*: Iterate on the prompt and test with various PHP files.

2. **Code integrity validation**: Accurately detect changes while ignoring whitespace.  
   - *Solution*: Use `nikic/PHP-Parser` to compare the abstract syntax tree (AST) of the original and modified files.

3. **Error handling**: Handle edge cases like invalid PHP files or LLM API failures.  
   - *Solution*: Implement robust error handling and provide clear error messages.

---

## Future Expansion Possibilities
1. **Support for other languages**: Extend the tool to support Smarty, Twig, JavaScript, etc.
2. **Configuration options**: Allow users to customize comment styles or LLM prompts.
3. **IDE integration**: Develop plugins for popular IDEs like VS Code or PHPStorm.
4. **Batch processing**: Add support for processing entire directories or projects.

---

## Next Steps
1. Review this **masterplan.md** and provide feedback.
2. Begin implementation based on the outlined phases.
3. Open-source the project on GitHub once the core functionality is complete.



