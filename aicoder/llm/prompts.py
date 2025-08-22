from textwrap import dedent
from typing import Any

from aicoder.strategies import ChangeStrategy


class DocumentationPrompts:
    """Contains prompt templates for documentation generation"""

    SYSTEM_PROMPT = "You are a senior PHP developer. You are tasked to improve the quality of a legacy php codebase by adding or improving comments (docblocks and section comments)."

    @classmethod
    def get_full_prompt(cls, php_code: str, strategy: ChangeStrategy) -> tuple[str, str]:
        """Return complete prompt with all original rules and formatting"""
        user_prompt = dedent(f"""
            Improve the PHP_CODE by adding or improving comments (docblocks and section comments). Apply the following rules:

            - Each class should have a docblock explaining what the class does. If a docblock already exists, try to improve it.
            - Each method should have a docblock explaining what the method does, except setters and getters.
            - Do NOT add redundant PHPDoc tags to docblocks, e.g. `@return void` or `@param string $foo` without any additional information.
            - inside functions use section comments, starting with `// ----`, explaining key parts of the code, if needed.
            - in big switch-case statements, add a section comment (starting with // ----) for each case.
            - Keep ALL original code except documentation, do NOT add or remove any code. only comments.
            - NEVER replace code with comments like "// ... rest of the code remains unchanged ..."
            - do NOT change or remove timestamp comments like "07/2024 created"
            - do NOT remove comments that mark the main entry point, usually "==== MAIN ===="
            - do NOT remove TODO and FIXME comments
            - do NOT add comments to getters and setters"
            """)

        # Add strategy-specific prompt additions
        user_prompt += strategy.get_prompt_additions()
        
        user_prompt += f"\n\nPHP_CODE:\n{php_code}\n"

        return cls.SYSTEM_PROMPT, user_prompt


class TwigDocumentationPrompts:
    """Contains prompt templates for Twig template documentation generation"""

    SYSTEM_PROMPT = "You are a senior web developer specializing in Twig templates. You are tasked to improve the quality of legacy Twig templates by adding or improving comments and documentation."

    @classmethod
    def get_full_prompt(cls, twig_code: str, strategy: ChangeStrategy) -> tuple[str, str]:
        """Return complete prompt with all original rules and formatting"""
        user_prompt = dedent("""
            Improve the TWIG_CODE by adding or improving comments and documentation. Apply the following rules:

            - Add clear, concise comments explaining complex logic, variable assignments, and template structures
            - Document block names and their purposes: {# Block: header - Contains site navigation and branding #}
            - Document macro definitions and their parameters: {# Macro: renderButton(label, url, type) - Renders a styled button #}
            - Document complex conditionals and loops: {# Loop: products - Iterates over product collection #}
            - Document template inheritance: {# Extends: base.html.twig - Main layout template #}
            - Document included templates: {# Include: partials/sidebar.html.twig - Sidebar navigation #}
            - Document custom filters and functions when used
            - Keep ALL original code except documentation, do NOT add or remove any code. only comments.
            - NEVER replace code with comments like "{# ... rest of the code remains unchanged ... #}"
            - do NOT change or remove timestamp comments like "07/2024 created"
            - do NOT remove TODO and FIXME comments
            - Use Twig comment syntax: {# This is a comment #}
            - Place comments on their own line before the code they describe
            - For short inline comments, use: {{ variable }} {# explanation #}
            """)
        
        # Add strategy-specific prompt additions
        user_prompt += strategy.get_prompt_additions()
        
        user_prompt += f"\n\nTWIG_CODE:\n{twig_code}\n"

        return cls.SYSTEM_PROMPT, user_prompt
