# ---- CLI Entry Point ----
# File: phpcomment/cli/main.py

import typer
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table

from phpcomment.config import Config
from phpcomment.profiles import profile_loader
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
    profile: str = typer.Option(
        Config.DEFAULT_PROFILE, "--profile", "-p",
        help="Profile to use (predefined model and strategy combination)",
        show_default=True
    ),
    model: Optional[str] = typer.Option(
        None, "--model",
        help="Model to use for processing (overrides profile setting)",
        show_default=False
    ),
    strategy: Optional[str] = typer.Option(
        None, "--strategy",
        help="Strategy for output format: wholefile, udiff, or searchreplace (overrides profile setting)",
        show_default=False
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Enable verbose output"
    ),
    file_path: Path = typer.Argument(..., help="Path to PHP file to document", exists=True)
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
        
        # Load profile settings
        profile_settings = profile_loader.get_profile(profile)
        if not profile_settings:
            myLogger.warning(f"Profile '{profile}' not found, using default profile")
            profile_settings = profile_loader.get_profile(Config.DEFAULT_PROFILE)
            if not profile_settings:
                # Fallback to legacy defaults if no profiles are available
                profile_settings = {
                    "model": Config.DEFAULT_MODEL,
                    "strategy": "wholefile"
                }
        
        # Override profile settings with CLI arguments if provided
        selected_model = model or profile_settings["model"]
        selected_strategy = strategy or profile_settings["strategy"]
        
        myLogger.debug(f"Using profile: {profile}")
        myLogger.debug(f"Model: {selected_model}")
        myLogger.debug(f"Strategy: {selected_strategy}")
        
        # Select strategy based on strategy parameter
        if selected_strategy.lower() == "searchreplace":
            strategy_obj = SearchReplaceStrategy()
        elif selected_strategy.lower() == "udiff":
            strategy_obj = UDiffStrategy()
        elif selected_strategy.lower() == "wholefile":
            strategy_obj = WholeFileStrategy()
        else:
            raise ValueError(f"Invalid strategy: {selected_strategy}. Choose from: wholefile, udiff, searchreplace")
        
        myLogger.debug(f"Using strategy: {strategy_obj.__class__.__name__}")
        myLogger.info(f"Sending request to LLM {selected_model}...")
        
        improveDocumentationOfPhpFile(file_path, model=selected_model, strategy=strategy_obj)
        print_success(f"\n✅ Successfully updated documentation in [bold]{file_path}[/bold]")
            
    except Exception as e:
        handle_error(e)

@app.command()
def list_profiles():
    """List all available profiles with their settings"""
    profiles = profile_loader.get_available_profiles()
    
    if not profiles:
        console.print("[yellow]No profiles found.[/yellow]")
        return
    
    table = Table(title="Available Profiles")
    table.add_column("Profile", style="cyan")
    table.add_column("Model", style="green")
    table.add_column("Strategy", style="magenta")
    
    for profile_name in profiles:
        profile_data = profile_loader.get_profile(profile_name)
        if profile_data:
            table.add_row(
                profile_name,
                profile_data.get("model", "N/A"),
                profile_data.get("strategy", "N/A")
            )
    
    console.print(table)

def main():
    app()

if __name__ == "__main__":
    main()
