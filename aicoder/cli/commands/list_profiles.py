from rich.console import Console
from rich.table import Table
from aicoder.profiles import profile_loader

console = Console()

def list_profiles_command():
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
