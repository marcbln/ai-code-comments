# ---- CLI Entry Point ----
# File: phpcomment/cli/main.py

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from ..core.processor import process_php_file
from ..utils.error_handler import handle_errors
from ..utils.output import print_success

app = typer.Typer(
    help="Automated PHP documentation tool",
    context_settings={"help_option_names": ["-h", "--help"]}
)
console = Console()

@app.command()
def comment(
    file_path: Path = typer.Argument(..., help="Path to PHP file to document", exists=True),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without modifying files"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed processing information")
):
    """
    Add PHPDoc comments and section markers to a PHP file
    
    Features:
    - Generates PHPDoc blocks for classes and functions
    - Adds // ---- section separators
    - Preserves original code structure
    """
    try:
        result = process_php_file(file_path, dry_run=dry_run)
        
        if dry_run:
            console.print("\n[DRY RUN MODE] Proposed changes:\n")
            console.print(result)
        else:
            print_success(f"\nSuccessfully updated documentation in [bold]{file_path}[/bold]")
            
            if verbose:
                console.print("\nModified content:", markup=False)
                console.print(result)
                
    except Exception as e:
        handle_error(e, verbose=verbose)

def main():
    app()

if __name__ == "__main__":
    main()
