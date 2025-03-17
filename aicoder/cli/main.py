import typer

from aicoder.cli.commands.add_comments import add_comments_command
from aicoder.cli.commands.list_profiles import list_profiles_command
from aicoder.config import Config
from .commands import add_comments
from .commands import list_profiles

app = typer.Typer(
    help="Automated PHP documentation tool",
    context_settings={"help_option_names": ["-h", "--help"]}
)


@app.command()
def version():
    """Print version information"""
    typer.echo(f"aicoder {Config.APP_VERSION}")

app.command(name="add-comment")(add_comments_command)
app.command(name="list-profiles")(list_profiles_command)

def main():
    app()

if __name__ == "__main__":
    main()
