# Plan: Implement Model Aliasing System

This document outlines the plan to implement a model aliasing system within the `aicoder` project.

## 1. Create Alias Configuration File

*   **File:** `config/model-aliases.yaml`
*   **Format:** YAML dictionary (key: alias, value: full model identifier)
*   **Example Content:**
    ```yaml
    # config/model-aliases.yaml
    gpt4o: openai/gpt-4o-2024-05-13
    claude35: openrouter/anthropic/claude-3.5-sonnet
    geminiflash: openrouter/google/gemini-2.0-flash-exp:free
    deepseekcoder: openrouter/deepseek/deepseek-coder
    ```

## 2. Modify `aicoder/llm/api_client.py`

*   **Imports:** Add `yaml`, `os`, `pathlib` at the top.
*   **Helper Function:** Define a *module-level* helper function (outside the `LLMClient` class) named `_resolve_model_alias(model_input: str) -> str`.
    *   This function will contain the complete logic for:
        *   Finding the `config/model-aliases.yaml` file relative to the project structure.
        *   Loading the YAML file with robust error handling (file not found, parse errors -> log warning/error, return empty dict).
        *   Checking if `model_input` is a key in the loaded aliases.
        *   If found, log the resolution (e.g., using `myLogger`) and return the resolved full model identifier.
        *   If not found or if loading failed, return the original `model_input` unchanged.
*   **Modify `LLMClient.__init__`:**
    *   Call the helper function at the very beginning: `resolved_model_name = _resolve_model_alias(modelWithPrefix)`
    *   Use `resolved_model_name` instead of `modelWithPrefix` in the subsequent logic for determining the provider and setting `self.model`.

## 3. Add Dependency

*   Add `PyYAML` to `pyproject.toml`.
*   Ensure it's installed (e.g., `uv pip install PyYAML`).

## 4. Testing

*   Run CLI commands (e.g., `aicoder analyze`, `aicoder add-comments`) using aliases and full names.
*   Verify correct resolution via logs/output.
*   Test edge cases: missing alias, missing/invalid config file.

## Conceptual Flow Diagram

```mermaid
graph TD
    A[Start __init__ with modelWithPrefix] --> B[Call _resolve_model_alias(modelWithPrefix)];
    subgraph Helper Function _resolve_model_alias
        direction LR
        B_Start[Input: model_input] --> B_Load{Load model-aliases.yaml};
        B_Load -- Success --> B_Check{Is model_input in Aliases?};
        B_Load -- Failure --> B_EmptyMap[Use Empty Map];
        B_EmptyMap --> B_ReturnOriginal;
        B_Check -- Yes --> B_GetValue[Get Alias Value];
        B_Check -- No --> B_ReturnOriginal[Return Original model_input];
        B_GetValue --> B_ReturnResolved[Return Resolved Value];
    end
    B -- Returns resolved_model_name --> C[Store resolved_model_name in self.model];
    C --> D{Check Provider Prefix using resolved_model_name};
    D --> E[Update self.model (remove prefix)];
    E --> F[Initialize Provider];
    F --> G[End __init__];

    style B_Load fill:#f9f,stroke:#333,stroke-width:2px
    style B_Check fill:#ccf,stroke:#333,stroke-width:2px