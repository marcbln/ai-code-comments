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
    def apply_patch(self, original_content: str, udiff: str) -> str:
        """
        Applies a unified diff without range information to original content.

        Args:
            original_content: The original text content to patch
            udiff: The unified diff containing changes to apply

        Returns:
            The modified content after applying the patch

        Raises:
            NoMatchError: If the diff doesn't find matching context
            MultipleMatchesError: If the diff matches multiple locations
        """
        hunks = self._parse_hunks(udiff)
        current_content = original_content
        for hunk in hunks:
            before, after = self._hunk_to_before_after(hunk)
            current_content = self._apply_single_hunk(current_content, before, after)
        return current_content

    def _parse_hunks(self, udiff: str) -> list[list[str]]:
        """Parse raw diff into list of hunks"""
        lines = udiff.splitlines(keepends=True)
        hunks = []
        current_hunk = []

        for line in lines:
            # Skip diff header lines
            if line.startswith(('---', '+++')):
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

        return hunks

    def _hunk_to_before_after(self, hunk: list[str]) -> tuple[str, str]:
        """Extract before/after texts from a hunk"""
        before = []
        after = []

        for line in hunk:
            prefix = line[0]
            content = line[1:]

            if prefix in (' ', '-'):
                before.append(content)
            if prefix in (' ', '+'):
                after.append(content)

        return ''.join(before), ''.join(after)

    def _apply_single_hunk(self, content: str, before: str, after: str) -> str:
        """Apply a single hunk to the content"""
        # Handle empty before case (appending new content)
        if not before.strip():
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
            raise NoMatchError("No matching context found for hunk")
        if len(matches) > 1:
            raise MultipleMatchesError("Multiple possible match locations for hunk")

        # Replace the first (and only) match
        start = matches[0]
        end = start + len(before)
        return content[:start] + after + content[end:]