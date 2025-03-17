import typer
from pathlib import Path
from rich.console import Console
from rich.syntax import Syntax
from typing import Optional

from aicoder.llm.api_client import LLMClient
from aicoder.config import Config
from aicoder.profiles import profile_loader, ProfileType
from aicoder.utils.logger import myLogger

console = Console()

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
        
        # Analysis prompt
        system_prompt = """You are a senior software engineer performing code analysis. 
        Analyze the provided code and give clear, specific feedback about:
        
        1. Code Quality:
           - Structure and organization
           - Readability and maintainability
           - Adherence to best practices
        
        2. Potential Issues:
           - Bugs or error prone patterns
           - Security concerns
           - Performance considerations
        
        3. Suggested Improvements:
           - Specific recommendations for enhancement
           - Alternative approaches where relevant
           
        Be concise but thorough. Focus on the most important points.
        Format your response in clear sections with bullet points for readability."""
        
        # Send to LLM
        myLogger.debug(f"Analyzing file: {file}")
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
