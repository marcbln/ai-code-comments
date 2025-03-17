import difflib

# this one was build by qwen2.5

class UnifiedDiffPatcher:
    """
    A class to apply unified diffs without range information to a given content.
    """

    def __init__(self):
        pass

    def apply_patch(self, original_content: str, unified_diff: str) -> str:
        """
        Applies a unified diff (without range information) to the original content.

        Args:
            original_content (str): The original content to which the patch will be applied.
            unified_diff (str): The unified diff (without range information).

        Returns:
            str: The modified content after applying the patch.

        Raises:
            ValueError: If the diff cannot be applied cleanly.
        """
        # Parse the unified diff into before and after sections
        before_text, after_text = self._hunk_to_before_after(unified_diff)

        # Apply the hunk to the original content
        try:
            new_content = self._apply_hunk(original_content, before_text, after_text)
        except ValueError as e:
            raise ValueError(f"Failed to apply patch: {e}")

        return new_content

    def _hunk_to_before_after(self, hunk: str) -> tuple:
        """
        Extracts the 'before' and 'after' sections from a unified diff.

        Args:
            hunk (str): The unified diff content.

        Returns:
            tuple: A tuple containing the 'before' and 'after' text as strings.
        """
        before = []
        after = []

        for line in hunk.splitlines(keepends=True):
            if line.startswith(" "):
                before.append(line[1:])
                after.append(line[1:])
            elif line.startswith("-"):
                before.append(line[1:])
            elif line.startswith("+"):
                after.append(line[1:])

        return "".join(before), "".join(after)

    def _apply_hunk(self, content: str, before_text: str, after_text: str) -> str:
        """
        Applies a single hunk by searching for the 'before' text in the content
        and replacing it with the 'after' text.

        Args:
            content (str): The original content.
            before_text (str): The text to search for in the content.
            after_text (str): The text to replace the 'before' text with.

        Returns:
            str: The updated content after applying the hunk.

        Raises:
            ValueError: If the 'before' text is not found or matches multiple times.
        """
        # Check if the 'before' text exists in the content
        start = content.find(before_text)
        if start == -1:
            raise ValueError(f"'before' text not found in content:\n{before_text}")

        # Ensure the match is unique
        if content.count(before_text) > 1:
            raise ValueError(f"Multiple matches found for 'before' text:\n{before_text}")

        # Replace the 'before' text with the 'after' text
        end = start + len(before_text)
        new_content = content[:start] + after_text + content[end:]

        return new_content


# Example Usage
if __name__ == "__main__":
    # Original content
    original_content = """\
def greet(name):
    print("Hello, " + name)

def farewell(name):
    print("Goodbye, " + name)
"""

    # Unified diff without range information
    unified_diff = """\
 def greet(name):
-    print("Hello, " + name)
+    print("Hi, " + name)

 def farewell(name):
"""

    # Create the patcher instance
    patcher = UnifiedDiffPatcher()

    # Apply the patch
    try:
        modified_content = patcher.apply_patch(original_content, unified_diff)
        print("Modified Content:")
        print(modified_content)
    except ValueError as e:
        print(f"Error: {e}")