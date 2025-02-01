# ---- Documentation Prompts ----
from textwrap import dedent

class DocumentationPrompts:
    """Contains prompt templates for documentation generation"""
    
    SYSTEM_PROMPT = "You are a senior PHP developer. You are tasked to add or improve comments of a large legacy php codebase."

    @classmethod
    def get_full_prompt(cls, php_code: str, diff_format: bool) -> tuple[str, str]:
        """Return complete prompt with all original rules and formatting"""
        user_prompt = dedent(f"""
            Analyze the PHP_CODE and apply following rules:
            
            - Each class should have a docblock explaining what the class does. If a docblock already exists, try to improve it.
            - Each method should have a docblock explaining what the method does, except setters and getters.
            - Do NOT add redundant PHPDoc tags to docblocks, e.g. `@return void` or `@param string $foo` without any additional information.
            - inside functions use section comments, starting with `// ----`, explaining key parts of the code, if needed.
            - in big switch-case statements, add a section comment (starting with // ----) for each case.
            - Keep ALL original code except documentation.
            - NEVER replace code with comments like "// ... rest of the code remains unchanged ..."
            """)
        
        if diff_format:
            user_prompt += "- Respond ONLY with a unified diff patch. Format the response as a unified diff patch with 3-line context."
        else:
            user_prompt += "- Response ONLY with full modified source code."

        user_prompt += dedent(f"""
        
        PHP_CODE:

        {php_code}
        """)
        
        return cls.SYSTEM_PROMPT, user_prompt
