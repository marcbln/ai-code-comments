import typer

from aicoder.cli.commands.add_comments import add_comments_command
from aicoder.cli.commands.list_profiles import list_profiles_command
from aicoder.cli.commands.analyze import analyze_command
from aicoder.config import Config

app = typer.Typer(
    help="Automated PHP documentation tool",
    context_settings={"help_option_names": ["-h", "--help"]}
)


@app.command()
def version():
    """Print version information"""
    typer.echo(f"aicoder {Config.APP_VERSION}")

app.command(name="add-comments")(add_comments_command)
app.command(name="list-profiles")(list_profiles_command)
app.command(name="analyze")(analyze_command)

def main():
    app()

if __name__ == "__main__":
    main()
