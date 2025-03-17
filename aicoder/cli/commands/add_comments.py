import typer
from pathlib import Path
from typing import Optional

from aicoder.config import Config
from aicoder.profiles import profile_loader, ProfileType
from aicoder.strategies import UDiffStrategy, WholeFileStrategy, SearchReplaceStrategy
from aicoder.core.processor import improveDocumentationOfPhpFile
from aicoder.utils.error_handler import handle_error
from aicoder.utils.output import print_success
from aicoder.utils.logger import myLogger

def add_comments_command(
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
        profile_settings = profile_loader.get_profile(ProfileType.COMMENTER, profile)
        if not profile_settings:
            # exit the script with an error
            raise ValueError(f"Profile '{profile}' not found")
        
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
