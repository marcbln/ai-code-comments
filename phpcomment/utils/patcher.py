from typing import List, Tuple, Optional
from dataclasses import dataclass
from phpcomment.utils.logger import logger


@dataclass
class PatchHunk:
    """Represents a single hunk in a patch file."""
    original: List[str]  # Lines to search for (context + removals)
    modified: List[str]  # Lines to replace with (context + additions)


class MyPatcher:
    """
    FIXME: THIS DOES NOT WORK AS INTENDED, IT DOES NOT APPLY ALL HUNKS CORRECTLY, BUT SOME (THE FIRST ONE/S?) WORK

    Handles the parsing and application of patches using unified diff format.
    This implementation treats hunks as search-replace pairs.
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def log(self, message: str) -> None:
        """Print a log message if verbose mode is enabled."""
        logger.debug(message)

    def parse_patch_hunks(self, patch_content: str) -> List[PatchHunk]:
        """Parse patch file content into a list of PatchHunk objects."""
        self.log("\n=== Parsing patch file ===")
        hunks = []
        current_hunk = []
        in_hunk = False

        for line in patch_content.splitlines():
            if line.startswith('---') or line.startswith('+++'):
                self.log(f"Skipping file header: {line}")
                continue

            if line.startswith('@@ '):
                if in_hunk:
                    hunks.append(self._parse_hunk(current_hunk))
                    current_hunk = []
                in_hunk = True
                self.log(f"\nFound hunk header: {line}")
            elif in_hunk:
                current_hunk.append(line)

        if current_hunk:
            hunks.append(self._parse_hunk(current_hunk))

        logger.info(f"Created {len(hunks)} search-replace pairs from patch")
        for i, hunk in enumerate(hunks, 1):
            self.log(f"Hunk {i}: {len(hunk.original)} original lines -> {len(hunk.modified)} modified lines")
        return hunks

    def _parse_hunk(self, hunk_lines: List[str]) -> PatchHunk:
        """Parse a single hunk into a PatchHunk object."""
        self.log("\n--- Parsing hunk ---")
        original = []
        modified = []

        for line in hunk_lines:
            # Handle the line based on its prefix, preserving empty lines
            if line.startswith(' '):
                # Context line (unchanged)
                original.append(line[1:])
                modified.append(line[1:])
            elif line.startswith('-'):
                # Removal line (only in original)
                original.append(line[1:])
            elif line.startswith('+'):
                # Addition line (only in modified)
                modified.append(line[1:])
            elif not line:
                # Empty line should be treated as context
                original.append('')
                modified.append('')

        return PatchHunk(original, modified)

    def _find_hunk_position(self, content: List[str], hunk: PatchHunk) -> Optional[int]:
        """Find the position in content where the hunk should be applied."""
        self.log("\n--- Finding hunk position ---")
        original_lines = hunk.original

        if not original_lines:
            self.log("No original lines to search for, defaulting to position 0")
            return 0

        self.log(f"Searching for original lines: {original_lines}")
        for i in range(len(content)):
            matches = True
            for j, line in enumerate(original_lines):
                if i + j >= len(content) or content[i + j] != line:
                    matches = False
                    break
            if matches:
                self.log(f"Found match at position {i}")
                return i

        self.log("No matching position found!")
        return None

    def _apply_hunk(self, content: List[str], hunk: PatchHunk) -> List[str]:
        """Apply a single hunk to the content using search-replace logic."""
        position = self._find_hunk_position(content, hunk)
        if position is None:
            self.log("WARNING: Hunk could not be applied. Skipping.")
            return content

        # Replace the original lines with the modified lines
        original_len = len(hunk.original)
        modified_lines = hunk.modified

        self.log(f"Replacing {original_len} lines at position {position} with {len(modified_lines)} lines")
        new_content = content[:position] + modified_lines + content[position + original_len:]
        return new_content

    def apply_patch(self, source_content: str, patch_content: str) -> str:
        """Apply the patch to the source content and return the result."""
        logger.info(f"Starting to apply patch...")

        # Split content preserving empty lines
        content_lines = source_content.splitlines()
        hunks = self.parse_patch_hunks(patch_content)
        new_content = content_lines

        # Apply hunks in order
        for hunk_num, hunk in enumerate(hunks, 1):
            self.log(f"\n=== Processing hunk {hunk_num}/{len(hunks)} ===")
            new_content = self._apply_hunk(new_content, hunk)

        logger.info("Patch application completed")
        return '\n'.join(new_content) + '\n'
