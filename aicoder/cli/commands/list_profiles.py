from rich.console import Console
from rich.table import Table
from aicoder.profiles import profile_loader, ProfileType

console = Console()

def list_profiles_command():
    """List all available profiles with their settings"""
    
    # Create and display commenter profiles table
    console.print("\n[bold blue]Commenter Profiles[/bold blue]")
    table = Table()
    table.add_column("Profile", style="cyan")
    table.add_column("Model", style="green")
    table.add_column("Strategy", style="magenta")
    
    commenter_profiles = profile_loader.profiles[ProfileType.COMMENTER]
    for profile_name, profile_data in commenter_profiles.items():
        table.add_row(
            profile_name,
            profile_data.get("model", "N/A"),
            profile_data.get("strategy", "N/A")
        )
    
    console.print(table)
    
    # Create and display analyzer profiles table
    console.print("\n[bold blue]Analyzer Profiles[/bold blue]")
    table = Table()
    table.add_column("Profile", style="cyan")
    table.add_column("Model", style="green")
    
    analyzer_profiles = profile_loader.profiles[ProfileType.ANALYZER]
    for profile_name, profile_data in analyzer_profiles.items():
        table.add_row(
            profile_name,
            profile_data.get("model", "N/A")
        )
    
    console.print(table)
