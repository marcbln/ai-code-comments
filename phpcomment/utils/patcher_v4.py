from pprint import pprint
from rich.console import Console
from rich.theme import Theme
import difflib

from .logger import myLogger

class PatchError(Exception):
    """Base exception for patch application errors"""
    pass


class NoMatchError(PatchError):
    """Raised when the hunk doesn't find a match"""
    pass


class MultipleMatchesError(PatchError):
    """Raised when the hunk finds multiple possible matches"""
    pass


class PatcherV4:
    def __init__(self, continue_on_error: bool = False, fuzzy_match: bool = True):
        """
        Initialize the patcher with error handling configuration.

        Args:
            continue_on_error: If True, continue applying remaining hunks when a hunk fails.
            fuzzy_match: If True, use fuzzy matching for finding hunk locations
        """
        self.continue_on_error = continue_on_error
        self.fuzzy_match = fuzzy_match
        self.console = Console(theme=Theme({
            "info": "cyan",
            "warning": "yellow",
            "error": "red",
            "success": "green"
        }))

    def apply_patch(self, original_content: str, udiff: str) -> str:
        """
        Applies a unified diff without range information to original content.

        Args:
            original_content: The original text content to patch
            udiff: The unified diff containing changes to apply

        Returns:
            The modified content after applying the patch
        """
        self.console.print("[info]Starting patch application...[/info]")

        # Normalize line endings in both content and diff
        original_content = self._normalize_newlines(original_content)
        udiff = self._normalize_newlines(udiff)

        hunks = self._parse_hunks(udiff)
        self.console.print(f"[info]Found {len(hunks)} hunks to apply[/info]")

        current_content = original_content
        failed_hunks = []

        for i, hunk in enumerate(hunks, 1):
            self.console.print(f"[info]Processing hunk {i} of {len(hunks)}...[/info]")
            try:
                before, after = self._hunk_to_before_after(hunk)
                current_content = self._apply_single_hunk(current_content, before, after)
                self.console.print(f"[success]Successfully applied hunk {i}[/success]")
            except PatchError as e:
                error_msg = f"Failed to apply hunk {i}: {str(e)}"
                failed_hunks.append((i, error_msg))
                self.console.print(f"[error]{error_msg}[/error]")

                if not self.continue_on_error:
                    self.console.print("[error]Stopping patch application due to error[/error]")
                    raise

        if failed_hunks:
            self.console.print("[warning]Patch application completed with errors:[/warning]")
            for hunk_num, error in failed_hunks:
                self.console.print(f"[warning]Hunk {hunk_num}: {error}[/warning]")
        else:
            self.console.print("[success]Patch application completed successfully[/success]")

        return current_content

    def _normalize_newlines(self, text: str) -> str:
        """Normalize line endings to \n"""
        return text.replace('\r\n', '\n').replace('\r', '\n')

    def _parse_hunks(self, udiff: str) -> list[list[str]]:
        """Parse raw diff into list of hunks"""
        self.console.print("[info]Parsing diff hunks...[/info]")
        lines = udiff.splitlines(keepends=True)
        hunks = []
        current_hunk = []

        for line in lines:
            # Skip diff header lines
            if line.startswith(('---', '+++')):
                self.console.print("[info]Skipping diff header line[/info]")
                continue

            # Start new hunk when we hit a non-diff line
            if not line.startswith((' ', '-', '+')):
                if current_hunk:
                    hunks.append(current_hunk)
                    current_hunk = []
                continue

            current_hunk.append(line)

        if current_hunk:
            hunks.append(current_hunk)

        self.console.print(f"[info]Parsed {len(hunks)} hunks from diff[/info]")
        return hunks

    def _hunk_to_before_after(self, hunk: list[str]) -> tuple[str, str]:
        """Extract before/after texts from a hunk"""
        self.console.print("[info]Converting hunk to before/after state...[/info]")
        before = []
        after = []

        for line in hunk:
            prefix = line[0]
            content = line[1:]

            if prefix in (' ', '-'):
                before.append(content)
            if prefix in (' ', '+'):
                after.append(content)

        before_text = ''.join(before)
        after_text = ''.join(after)

        # ---- print the before/after state with line numbers
        self.console.print(f"[info]Converted hunk to before/after state[/info]")
        print(f"<<<<<<<< ORIGINAL")
        for i, line in enumerate(before, start=1):
            print(f"{i:4d} | {line}", end='')
        print("========")
        for i, line in enumerate(after, start=1):
            print(f"{i:4d} | {line}", end='')
        print(f">>>>>>>> UPDATED")

        return before_text, after_text

    def _find_best_match(self, content: str, before: str) -> int:
        """
        Find the best matching location for a code hunk using exact and fuzzy matching strategies.

        This method attempts to find where a piece of code ('before' content) best fits within
        the target content. It uses a two-stage matching process:
        1. First attempts exact string matching
        2. If exact matching fails and fuzzy matching is enabled, uses difflib for approximate matching

        Parameters
        ----------
        content : str
            The full text content to search within. This is typically the entire file
            or document where we want to find the matching location.
        before : str
            The text content to match against. This is typically a code snippet or
            text block that we want to locate within the main content.

        Returns
        -------
        int
            The character position in 'content' where the best match begins.
            For empty 'before' content, returns the length of 'content'.

        Raises
        ------
        MultipleMatchesError
            When multiple exact matches are found, making it ambiguous where to place the hunk.
        NoMatchError
            When no exact match is found and either:
            - Fuzzy matching is disabled
            - Fuzzy matching is enabled but no match meets the minimum similarity threshold

        Notes
        -----
        The fuzzy matching algorithm:
        - Splits both content and before text into lines
        - Uses difflib.SequenceMatcher to find matching blocks
        - For each matching block:
            * Calculates similarity ratio between the matched subsequence and 'before'
            * Requires a minimum similarity ratio of 0.8 (80% similar)
        - Converts the best matching line number to a character position

        The method prefers exact matches when available and only falls back to
        fuzzy matching when necessary and enabled. This helps ensure the most
        accurate placement of code hunks.

        Example
        -------
        >>> patcher = PatcherV4(fuzzy_match=True)
        >>> content = "def hello():\\n    print('hello')\\n\\ndef world():"
        >>> before = "def hello():\\n    print('hello')"
        >>> patcher._find_best_match(content, before)
        0  # Returns 0 since the match is at the start
        """

        # Handle empty before case
        if not before.strip():
            return len(content)

        # Try exact match first
        exact_matches = []
        start = 0
        while True:
            idx = content.find(before, start)
            if idx == -1:
                break
            exact_matches.append(idx)
            start = idx + 1

        if len(exact_matches) == 1:
            myLogger.success(f"💡 Found exact match at {exact_matches[0]}")
            return exact_matches[0]

        elif len(exact_matches) > 1:
            raise MultipleMatchesError("Multiple exact matches found")

        if not self.fuzzy_match:
            raise NoMatchError("No exact match found and fuzzy matching is disabled")

        # Try fuzzy matching
        before_lines = before.splitlines()
        content_lines = content.splitlines()

        matcher = difflib.SequenceMatcher(None, before_lines, content_lines)
        matches = matcher.get_matching_blocks()  # Fixed: Call get_matching_blocks() on matcher instance

        best_match = None
        best_ratio = 0.8  # Minimum similarity threshold

        for match in matches:
            i, j, n = match
            if n > 0:  # Only consider non-zero length matches
                subsequence = '\n'.join(content_lines[j:j + n])
                ratio = difflib.SequenceMatcher(None, before, subsequence).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = j

        if best_match is not None:
            # Convert line number to character position
            char_pos = sum(len(line) + 1 for line in content_lines[:best_match])
            return char_pos

        raise NoMatchError("No suitable match found even with fuzzy matching")

    def _apply_single_hunk(self, content: str, before: str, after: str) -> str:
        """Apply a single hunk to the content"""
        self.console.print("[info]Attempting to apply single hunk...[/info]")

        try:
            start = self._find_best_match(content, before)
            self.console.print(f"[info]Found match at position {start}[/info]")

            end = start + len(before)
            return content[:start] + after + content[end:]

        except NoMatchError:
            # Try with normalized whitespace
            normalized_content = ' '.join(content.split())
            normalized_before = ' '.join(before.split())

            if normalized_content.find(normalized_before) != -1:
                self.console.print("[warning]Found match with normalized whitespace[/warning]")
                # If we find a match with normalized whitespace, try to find the actual
                # location in the original content
                start = self._find_best_match(content, before.strip())
                end = start + len(before)
                return content[:start] + after + content[end:]
            else:
                raise