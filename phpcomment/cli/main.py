# ---- CLI Entry Point ----
# File: phpcomment/cli/main.py

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console

from phpcomment.config import Config
from ..utils.logger import myLogger



from phpcomment.strategies import UDiffStrategy, WholeFileStrategy, SearchReplaceStrategy
from ..core.processor import improveDocumentationOfPhpFile
from ..utils.error_handler import handle_error
from ..utils.output import print_success
from ..utils.logger import myLogger

app = typer.Typer(
    help="Automated PHP documentation tool",
    context_settings={"help_option_names": ["-h", "--help"]}
)
console = Console()

@app.command()
def comment(
    file_path: Path = typer.Argument(..., help="Path to PHP file to document", exists=True),
    model: str = typer.Option(
        #"openrouter/qwen/qwen-2.5-coder-32b-instruct",
        Config.DEFAULT_MODEL,
        help="Model to use for processing (openrouter/... or deepseek/...)",
        show_default=True
    ),
    use_udiff_coder: bool = typer.Option(
        False, "--diff", 
        help="Output changes as unified diff patch instead of full file"
    ),
    use_searchreplace: bool = typer.Option(
        False, "--searchreplace", 
        help="Output changes as search/replace blocks"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Enable verbose output"
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
        myLogger.set_verbose(verbose)
        # Select strategy based on response type
        if use_searchreplace:
            strategy = SearchReplaceStrategy()
        elif use_udiff_coder:
            strategy = UDiffStrategy()
        else:
            strategy = WholeFileStrategy()
        myLogger.debug(f"Using strategy: {strategy.__class__.__name__}")

        myLogger.info(f"Sending request to LLM {model}...")
        improveDocumentationOfPhpFile(file_path, model=model, strategy=strategy)
        print_success(f"\n✅ Successfully updated documentation in [bold]{file_path}[/bold]")
            
    except Exception as e:
        handle_error(e)

def main():
    app()

if __name__ == "__main__":
    main()
