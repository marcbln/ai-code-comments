#!/usr/bin/env python3
import sys
import re
from typing import List, Tuple

def parse_patch_hunks(patch_content: str) -> List[Tuple[List[str], List[str], List[str]]]:
    """Parse patch file into hunks. Each hunk contains (context_before, changes, context_after)."""
    hunks = []
    current_hunk = []
    in_hunk = False
    
    for line in patch_content.splitlines():
        if line.startswith('@@ '):
            if in_hunk:
                hunks.append(parse_hunk(current_hunk))
                current_hunk = []
            in_hunk = True
        if in_hunk:
            current_hunk.append(line)
            
    if current_hunk:
        hunks.append(parse_hunk(current_hunk))
        
    return hunks

def parse_hunk(hunk_lines: List[str]) -> Tuple[List[str], List[str], List[str]]:
    """Parse a single hunk into context_before, changes, and context_after."""
    context_before = []
    changes = []
    context_after = []
    
    # Skip the @@ line
    current_section = context_before
    
    for line in hunk_lines[1:]:
        if line.startswith(' '):
            if changes and current_section is context_before:
                current_section = context_after
            current_section.append(line[1:])
        elif line.startswith('-'):
            if current_section is context_before:
                context_before.pop()
            changes.append(('-', line[1:]))
        elif line.startswith('+'):
            changes.append(('+', line[1:]))
            
    return context_before, changes, context_after

def find_hunk_position(content: List[str], context_before: List[str], context_after: List[str]) -> int:
    """Find the position in content where the hunk should be applied."""
    if not context_before and not context_after:
        return -1
        
    content_str = '\n'.join(content)
    search_str = '\n'.join(context_before + context_after)
    
    # Handle empty context cases
    if not search_str:
        return 0
        
    # Find all possible matches
    matches = []
    start = 0
    while True:
        pos = content_str.find(search_str, start)
        if pos == -1:
            break
        matches.append(pos)
        start = pos + 1
        
    if len(matches) == 1:
        # Count newlines to get line number
        return content_str.count('\n', 0, matches[0]) + len(context_before)
    
    return -1

def apply_patch(source_file: str, patch_file: str) -> str:
    """Apply the patch to the source file."""
    with open(source_file, 'r') as f:
        content = f.read().splitlines()
        
    with open(patch_file, 'r') as f:
        patch_content = f.read()
        
    hunks = parse_patch_hunks(patch_content)
    new_content = content.copy()
    
    # Apply hunks in reverse order to keep line numbers valid
    for context_before, changes, context_after in reversed(hunks):
        position = find_hunk_position(content, context_before, context_after)
        
        if position == -1:
            print(f"Warning: Could not find match for hunk:\n{context_before}\n{changes}\n{context_after}")
            continue
            
        # Apply changes
        for op, line in reversed(changes):
            if op == '+':
                new_content.insert(position, line)
            elif op == '-':
                if position < len(new_content) and new_content[position] == line:
                    del new_content[position]
                else:
                    print(f"Warning: Line to remove not found: {line}")
                    
    return '\n'.join(new_content)

def main():
    if len(sys.argv) != 3:
        print("Usage: python my-patch.py <source-file> <patch-file>")
        sys.exit(1)
        
    source_file = sys.argv[1]
    patch_file = sys.argv[2]
    
    try:
        patched_content = apply_patch(source_file, patch_file)
        with open(source_file, 'w') as f:
            f.write(patched_content)
    except Exception as e:
        print(f"Error applying patch: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

