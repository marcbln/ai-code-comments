# ---- CLI Entry Point ----
# File: phpcomment/cli/main.py

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from ..core.processor import process_php_file
from ..utils.error_handler import handle_error
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
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed processing information"),
    model: str = typer.Option(
        "openrouter/qwen/qwen-2.5-coder-32b-instruct",
        help="Model to use for processing (openrouter/... or deepseek/...)",
        show_default=True
    ),
    diff_format: bool = typer.Option(
        False, "--diff", 
        help="Output changes as unified diff patch instead of full file"
    )
):
    """
    Add PHPDoc comments and section markers to a PHP file
    
    Features:
    - Generates PHPDoc blocks for classes and functions
    - Adds // ---- section separators
    - Preserves original code structure
    """
    try:
        with console.status("[bold green]Processing PHP file...", spinner="dots"):
            result = process_php_file(file_path, dry_run=dry_run, diff_format=diff_format, verbose=verbose, model=model)
            console.print(f"✅ [green]Processed {file_path.name} in", end="")
        
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
