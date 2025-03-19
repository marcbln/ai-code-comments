import typer
from pathlib import Path
from rich.console import Console
from rich.syntax import Syntax
from typing import Optional
import yaml

from aicoder.llm.api_client import LLMClient
from aicoder.config import Config
from aicoder.profiles import profile_loader, ProfileType
from aicoder.utils.logger import myLogger

console = Console()

def load_prompts():
    """Load prompts from analyzer-prompts.yaml"""
    prompts_path = Path(__file__).resolve().parent.parent.parent.parent / "config" / "profiles" / "analyzer-prompts.yaml"
    try:
        with open(prompts_path) as f:
            prompts = yaml.safe_load(f)["prompts"]
            if "default" not in prompts:
                raise ValueError("Default prompt not found in analyzer-prompts.yaml")
            return prompts
    except Exception as e:
        console.print(f"[red]Error:[/red] Could not load prompts: {str(e)}")
        raise typer.Exit(1)

def analyze_command(
    file: Path = typer.Argument(..., help="File to analyze"),
    profile: str = typer.Option(
        Config.DEFAULT_PROFILE, "--profile", "-p",
        help="Analysis profile to use (predefined model combination)",
        show_default=True
    ),
    model: Optional[str] = typer.Option(
        None, "--model",
        help="Model to use for analysis (overrides profile setting)",
        show_default=False
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Enable verbose output",
        show_default=True
    ),
):
    """Get AI feedback about the code in a file"""
    
    if not file.exists():
        console.print(f"[red]Error:[/red] File {file} does not exist")
        raise typer.Exit(1)

    # Get model from profile or override
    selected_profile = profile_loader.get_profile(ProfileType.ANALYZER, profile)
    if not selected_profile:
        console.print(f"[red]Error:[/red] Analysis profile '{profile}' not found")
        raise typer.Exit(1)
    
    model_to_use = model or selected_profile.get("model")
    if not model_to_use:
        console.print("[red]Error:[/red] No model specified in profile or command line")
        raise typer.Exit(1)

    try:
        # Read the file content
        content = file.read_text()
        
        # Create LLM client
        llm = LLMClient(model_to_use)
        
        # Load prompts
        prompts = load_prompts()
        
        # Get system prompt from profile or use default
        prompt_name = selected_profile.get("prompt", "default")
        system_prompt = prompts[prompt_name]
        
        # Send to LLM
        myLogger.debug(f"Analyzing file: {file}")
        
        if verbose:
            console.print("\n[bold yellow]AI Prompt[/bold yellow]")
            console.print("=" * 40)
            console.print("[bold]System Prompt:[/bold]")
            console.print(system_prompt)
            console.print(f"\n[bold]Code Content Size:[/bold] {len(content.encode('utf-8'))} bytes")
            console.print("=" * 40)
            console.print("\n")
            
        response = llm.sendRequest(system_prompt, content, verbose)
        
        # Output the original code with syntax highlighting
        console.print("\n[bold blue]Original PHP Code[/bold blue]")
        console.print("=" * 40)
        syntax = Syntax(content, "php", theme="monokai", line_numbers=True)
        console.print(syntax)
        console.print("\n")

        # Output the analysis
        console.print("[bold blue]Code Analysis Results[/bold blue]")
        console.print("=" * 40)
        console.print(response)
        console.print("=" * 40)

    except Exception as e:
        console.print(f"[red]Error during analysis:[/red] {str(e)}")
        raise typer.Exit(1)
