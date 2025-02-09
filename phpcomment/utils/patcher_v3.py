from pprint import pprint
from rich.console import Console
from rich.theme import Theme


class PatchError(Exception):
    """Base exception for patch application errors"""
    pass


class NoMatchError(PatchError):
    """Raised when the hunk doesn't find a match"""
    pass


class MultipleMatchesError(PatchError):
    """Raised when the hunk finds multiple possible matches"""
    pass


class PatcherV3:
    def __init__(self, continue_on_error: bool = False):
        """
        Initialize the patcher with error handling configuration.

        Args:
            continue_on_error: If True, continue applying remaining hunks when a hunk fails.
                             If False, raise an exception on first failure.
        """
        self.continue_on_error = continue_on_error
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

        Raises:
            NoMatchError: If the diff doesn't find matching context (when continue_on_error is False)
            MultipleMatchesError: If the diff matches multiple locations (when continue_on_error is False)
        """
        self.console.print("[info]Starting patch application...[/info]")
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

        self.console.print(f"[info]Converted hunk to before/after state[/info]")
        self.console.print(f"[blue]Before[/blue]\n```\n{''.join(before)}\n```")
        self.console.print(f"[blue]After[/blue]\n```\n{''.join(after)}\n```")

        return ''.join(before), ''.join(after)

    def _apply_single_hunk(self, content: str, before: str, after: str) -> str:
        """Apply a single hunk to the content"""
        self.console.print("[info]Attempting to apply single hunk...[/info]")

        # Handle empty before case (appending new content)
        if not before.strip():
            self.console.print("[info]Empty before content - appending new content[/info]")
            return content + after

        # Find all matches of the before text
        matches = []
        start = 0
        while True:
            idx = content.find(before, start)
            if idx == -1:
                break
            matches.append(idx)
            start = idx + 1

        if not matches:
            self.console.print("[error]No matching context found for hunk[/error]")
            raise NoMatchError("No matching context found for hunk")
        if len(matches) > 1:
            self.console.print("[error]Multiple possible match locations found[/error]")
            raise MultipleMatchesError("Multiple possible match locations for hunk")

        self.console.print(f"[info]Found match at position {matches[0]}[/info]")
        # Replace the first (and only) match
        start = matches[0]
        end = start + len(before)
        return content[:start] + after + content[end:]