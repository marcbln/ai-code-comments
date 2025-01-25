# ---- CLI Entry Point ----
# File: phpcomment/cli/main.py

import typer
from rich import print
from ..core.processor import process_php_file

app = typer.Typer(help="PHP documentation automation tool")

@app.command()
def annotate(
    file_path: str = typer.Argument(..., help="PHP file to process"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without saving"),
):
    """Main command to process PHP files"""
    # TODO: Implement core processing flow
    print(f"Processing {file_path}...")
    # process_php_file(file_path, dry_run)

if __name__ == "__main__":
    app()
