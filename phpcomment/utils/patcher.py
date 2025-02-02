from typing import List, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass
from rich.console import Console

console = Console()


@dataclass
class PatchHunk:
    """Represents a single hunk in a patch file."""
    context_before: List[str]
    changes: List[Tuple[str, str]]  # List of (operation, line) tuples
    context_after: List[str]


class MyPatcher:
    """
    Handles the parsing and application of patches.

    The hunks in the patch file have some "special format" which are missing the range information. For example instead of
    ```
    @@ -1,6 +1,10 @@
    ```
    the hunks look like
    ```
    @@ ... @@
    ```
    or just
    ```
    @@ @@
    ```
    This patcher ignores any range information in the hunks. It just searches in the source code for the correct locations.
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def log(self, message: str) -> None:
        """Print a log message if verbose mode is enabled."""
        if self.verbose:
            console.log(message)

    def parse_patch_hunks(self, patch_content: str) -> List[PatchHunk]:
        """Parse patch file content into a list of PatchHunk objects."""
        self.log("\n=== Parsing patch file ===")
        hunks = []
        current_hunk = []
        in_hunk = False

        for line_num, line in enumerate(patch_content.splitlines(), 1):
            if line.startswith('---') or line.startswith('+++'):
                self.log(f"Skipping file header at line {line_num}: {line}")
                continue

            if line.startswith('@@ '):
                self.log(f"\nFound hunk header at line {line_num}: {line}")
                if in_hunk:
                    hunks.append(self._parse_hunk(current_hunk))
                    current_hunk = []
                in_hunk = True
                current_hunk = []
            elif in_hunk:
                current_hunk.append(line)

        if current_hunk:
            hunks.append(self._parse_hunk(current_hunk))

        self.log(f"\nTotal hunks found: {len(hunks)}")
        return hunks

    def _parse_hunk(self, hunk_lines: List[str]) -> PatchHunk:
        """Parse a single hunk into a PatchHunk object."""
        self.log("\n--- Parsing hunk ---")
        context_before = []
        changes = []
        context_after = []

        # Skip empty lines at the start
        start_idx = 0
        while start_idx < len(hunk_lines) and not hunk_lines[start_idx].strip():
            start_idx += 1

        current_section = context_before

        for line_num, line in enumerate(hunk_lines[start_idx:], 1):
            if line.startswith(' '):
                if changes and current_section is context_before:
                    self.log("Switching to context_after section")
                    current_section = context_after
                current_section.append(line[1:])
                section_name = "before" if current_section is context_before else "after"
                self.log(f"Adding context line ({section_name}): {line[1:]!r}")
            elif line.startswith('-'):
                if current_section is context_before and context_before:
                    removed = context_before.pop()
                    self.log(f"Removing line from context_before: {removed!r}")
                changes.append(('-', line[1:]))
                self.log(f"Recording removal: {line[1:]!r}")
            elif line.startswith('+'):
                changes.append(('+', line[1:]))
                self.log(f"Recording addition: {line[1:]!r}")

        return PatchHunk(context_before, changes, context_after)

    def _find_hunk_position(self, content: List[str], hunk: PatchHunk) -> Optional[int]:
        """Find the position in content where the hunk should be applied."""
        self.log("\n--- Finding hunk position ---")

        if not hunk.context_before and not hunk.context_after:
            self.log("No context lines available, defaulting to position 0")
            return 0

        # Try to find position using context_before
        if hunk.context_before:
            self.log("\nSearching using context_before:")
            self.log(f"Context lines: {[line.rstrip() for line in hunk.context_before]}")
            for i in range(len(content)):
                matches = True
                for j, ctx_line in enumerate(hunk.context_before):
                    if i + j >= len(content) or content[i + j].rstrip() != ctx_line.rstrip():
                        matches = False
                        break
                if matches:
                    position = i + len(hunk.context_before)
                    self.log(f"Found match at position {position}")
                    return position

        # If no match found with context_before, try context_after
        if hunk.context_after:
            self.log("\nSearching using context_after:")
            self.log(f"Context lines: {[line.rstrip() for line in hunk.context_after]}")
            for i in range(len(content)):
                matches = True
                for j, ctx_line in enumerate(hunk.context_after):
                    if i + j >= len(content) or content[i + j].rstrip() != ctx_line.rstrip():
                        matches = False
                        break
                if matches:
                    self.log(f"Found match at position {i}")
                    return i

        self.log("No matching position found!")
        return None

    def _apply_changes(self, content: List[str], position: int, changes: List[Tuple[str, str]]) -> List[str]:
        """Apply changes at the specified position."""
        self.log(f"\n--- Applying changes at position {position} ---")
        result = content[:position]
        i = position
        
        # Group changes by type for easier processing
        additions = []
        removals = []
        for op, line in changes:
            if op == '+':
                additions.append(line)
            else:
                removals.append(line)
                
        # Process removals first to find their positions
        lines_to_remove = set()
        for line in removals:
            search_pos = i
            while search_pos < len(content):
                if content[search_pos].rstrip() == line.rstrip():
                    self.log(f"Marking line for removal at position {search_pos}: {content[search_pos]!r}")
                    lines_to_remove.add(search_pos)
                    break
                search_pos += 1
                
        # Now process the content, adding new lines at the start of the change position
        # Add all additions first
        for line in additions:
            self.log(f"Adding line: {line!r}")
            result.append(line)
            
        # Then add remaining content, skipping removed lines
        while i < len(content):
            if i not in lines_to_remove:
                result.append(content[i])
            i += 1
                
        return result

    def apply_patch(self, source_content: str, patch_content: str) -> str:
        """Apply the patch to the source content and return the result."""
        self.log(f"\n=== Starting patch application ===")

        content_lines = source_content.splitlines()
        hunks = self.parse_patch_hunks(patch_content)
        new_content = content_lines

        # Apply hunks in order
        for hunk_num, hunk in enumerate(hunks, 1):
            self.log(f"\n=== Processing hunk {hunk_num}/{len(hunks)} ===")
            position = self._find_hunk_position(new_content, hunk)

            if position is None:
                self.log(f"WARNING: Could not find match for hunk {hunk_num}")
                self.log(f"Context before: {hunk.context_before}")
                self.log(f"Context after: {hunk.context_after}")
                continue

            self.log(f"Applying changes for hunk {hunk_num} at position {position}")
            new_content = self._apply_changes(new_content, position, hunk.changes)

        self.log("\n=== Patch application completed ===")
        return '\n'.join(new_content) + '\n'
