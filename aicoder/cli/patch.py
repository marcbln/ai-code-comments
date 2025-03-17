from pathlib import Path
from typing import Optional
import typer
from rich import print
from aicoder.utils.patcher import MyPatcher
from aicoder.utils.patcher_v3 import PatcherV3
from aicoder.utils.patcher_v4 import PatcherV4


def patch_files(
        source_file: Path = typer.Argument(..., help="Original file to patch"),
        patch_file: Path = typer.Argument(..., help="Patch file to apply"),
        dest_file: Optional[Path] = typer.Argument(None,
                                                   help="Optional destination file (if not provided, source file will be modified)"),
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Print result without modifying files")
) -> None:
    """
    Apply a patch file to a source file.
    If dest_file is provided, the source file remains unchanged and the result is written to dest_file.
    """
    try:
        # patcher = MyPatcher(verbose=verbose)
        patcher = PatcherV4(continue_on_error=True)
        # Read input files
        with open(source_file) as f:
            source_content = f.read()
        with open(patch_file) as f:
            patch_content = f.read()

        # Apply patch
        result = patcher.apply_patch(source_content, patch_content)

        if dry_run:
            print("[yellow]Dry run - showing result without writing files:[/yellow]\n")
            print(result)
        else:
            # Write result
            output_file = dest_file or source_file
            with open(output_file, 'w') as f:
                f.write(result)

            if dest_file:
                print(f"[green]Successfully created patched file: {dest_file}[/green]")
                print(f"[blue]Original file {source_file} remains unchanged[/blue]")
            else:
                print(f"[green]Successfully patched {source_file}[/green]")

    except Exception as e:
        print(f"[red]Error applying patch: {e}[/red]")
        raise typer.Exit(1)


def main():
    typer.run(patch_files)

if __name__ == "__main__":
    main()
