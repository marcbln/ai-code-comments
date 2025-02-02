from textwrap import dedent


class DocumentationPrompts:
    """Contains prompt templates for documentation generation"""

    SYSTEM_PROMPT = "You are a senior PHP developer. You are tasked to add or improve comments of a large legacy php codebase."

    @classmethod
    def get_full_prompt(cls, php_code: str, use_udiff_coder: bool) -> tuple[str, str]:
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

        if use_udiff_coder:
            user_prompt += dedent("""
                - Output MUST be a valid unified diff patch.
                - Start response with '--- original.php'
                - Second line must be '+++ modified.php'
                - Start each hunk of changes with a `@@ ... @@` line.
                - DON'T include line numbers like `diff -U0` does (The user's patch tool doesn't need them). just use literally `@@ ... @@` instead.
                - The user's patch tool needs CORRECT patches that apply cleanly against the current contents of the file!
                - Think carefully and make sure you include and mark all lines that need to be removed or changed as `-` lines.
                - Make sure you mark all new or modified lines with `+`.
                - Don't leave out any lines or the diff patch won't apply correctly.

                Indentation matters in the diffs!

                Start a new hunk for each section of the file that needs changes.

                Only output hunks that specify changes with `+` or `-` lines.
                Skip any hunks that are entirely unchanging ` ` lines.

                Output hunks in whatever order makes the most sense.
                Hunks don't need to be in any particular order.

                - Do NOT include any text outside the diff
                - Do NOT wrap in markdown blocks
                - Include proper line endings for the complete code block
            """)

            # user_prompt += dedent("""
            #     - Output MUST be a valid unified diff patch.
            #     - Follow these rules exactly:
            #     
            #     1. OUTPUT FORMAT
            #     - Start with "--- original.php" followed by "+++ modified.php" on the next line
            #     - Do not include any explanations or text outside the diff
            #     - Do not wrap the output in code blocks or quotes
            #     - End the diff with a newline
            #     
            #     2. HUNK HEADERS
            #     - Each hunk must start with @@ and include both line ranges
            #     - Format: @@ -originalStart,originalCount +newStart,newCount @@ contextLine
            #     - The contextLine must be the first line after the numbers (copy it from original)
            #     - Line numbers must account for any previous hunks' additions/deletions
            #     
            #     3. HUNK CONTENT
            #     - Include 3 lines of unchanged context before and after changes
            #     - Prefix unchanged lines with a space
            #     - Prefix added lines with +
            #     - Prefix removed lines with -
            #     - Keep indentation exactly as in original
            #     - Include closing braces and complete code blocks
            #     
            #     4. MULTIPLE HUNKS
            #     - If changes are far apart, create separate hunks
            #     - Start each new hunk with @@ line ranges @@
            #     - Account for line number shifts from previous hunks
            #     - Maintain 3 lines of context between hunks
            #     
            #     5. LINE COUNTING
            #     - Count all lines including empty lines
            #     - Include newlines in the count
            #     - Update line numbers in subsequent hunks based on lines added/removed
            #     
            #     Do not explain your changes. Output only the raw diff patch.
            #     """)
            # user_prompt += dedent("""
            #     - Output MUST be a valid unified diff patch
            #     - Start response with '--- original.php'
            #     - Second line must be '+++ modified.php'
            #     - Each hunk MUST include complete context and show all affected lines
            #     - DON'T include line numbers like `diff -U0` does. The user's patch tool doesn't need them.
            #     - Do NOT include any text outside the diff
            #     - Do NOT wrap in markdown blocks
            #     - Include proper line endings for the complete code block
            #     """)
        else:
            user_prompt += "- Response ONLY with full modified source code."

        user_prompt += f"\n\nPHP_CODE:\n{php_code}\n"

        return cls.SYSTEM_PROMPT, user_prompt