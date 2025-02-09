# ---- CLI Entry Point ----
# File: phpcomment/cli/main.py

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console

from phpcomment.strategies import UDiffStrategy, WholeFileStrategy
from ..core.processor import improveDocumentationOfPhpFile
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
    model: str = typer.Option(
        #"openrouter/qwen/qwen-2.5-coder-32b-instruct",
        "openrouter/deepseek/deepseek-r1-distill-qwen-32b",
        help="Model to use for processing (openrouter/... or deepseek/...)",
        show_default=True
    ),
    use_udiff_coder: bool = typer.Option(
        False, "--diff", 
        help="Output changes as unified diff patch instead of full file"
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
        from ..utils.logger import logger
        logger.set_verbose(verbose)
        
        with console.status("[bold green]Processing PHP file...", spinner="dots"):
            # Select strategy based on response type
            strategy = UDiffStrategy() if use_udiff_coder else WholeFileStrategy()
            logger.debug(f"Using strategy: {strategy.__class__.__name__}")

            result = improveDocumentationOfPhpFile(file_path, strategy=strategy, model=model)
            console.print(f"✅ [green]Processed {file_path.name} in", end="")
            print_success(f"\nSuccessfully updated documentation in [bold]{file_path}[/bold]")
            
            console.print("\nModified content:", markup=False)
            console.print(result)
                
    except Exception as e:
        handle_error(e)

def main():
    app()

if __name__ == "__main__":
    main()
