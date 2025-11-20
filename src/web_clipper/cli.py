"""Command-line interface for web clipper."""

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from . import __version__
from .clipper import NoClipboardContentError, clip
from .config import get_config

app = typer.Typer(
    name="web-clipper",
    help="Clip web content from browsers to organized markdown files",
    add_completion=False
)
console = Console()


@app.command(name="clip")
def clip_command(
    tags: Optional[str] = typer.Option(
        None,
        "--tags",
        "-t",
        help="Comma-separated tags to add to the clip"
    )
):
    """
    Clip content from the browser to markdown.

    Reads selected text from clipboard, gets the current browser URL and title,
    and saves everything to an organized markdown file.
    """
    try:
        result = clip(tags=tags)

        # Success message
        console.print()
        console.print(
            Panel.fit(
                f"[green][/green] Clipped to: [cyan]{result.file_path}[/cyan]\n"
                f"[dim]URL:[/dim] {result.url}\n"
                f"[dim]Title:[/dim] {result.title or 'N/A'}\n"
                f"[dim]Length:[/dim] {result.content_length} characters",
                title="[bold green]Clip Saved[/bold green]",
                border_style="green"
            )
        )
        console.print()

    except NoClipboardContentError as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red][/red] {str(e)}",
                title="[bold red]No Content[/bold red]",
                border_style="red"
            )
        )
        console.print()
        raise typer.Exit(code=1)

    except Exception as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red][/red] {str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red"
            )
        )
        console.print()
        raise typer.Exit(code=1)


@app.command()
def init():
    """
    Initialize web clipper configuration.

    Creates the clips directory and shows current configuration.
    """
    config = get_config()

    try:
        config.ensure_clips_directory()

        console.print()
        console.print(
            Panel.fit(
                f"[green][/green] Clips directory: [cyan]{config.clips_directory}[/cyan]\n"
                f"[dim]Create subdirs:[/dim] {config.create_subdirs}\n"
                f"[dim]Include title:[/dim] {config.include_title}\n"
                f"[dim]Include timestamp:[/dim] {config.include_timestamp}",
                title="[bold green]Web Clipper Initialized[/bold green]",
                border_style="green"
            )
        )
        console.print()
        console.print("[dim]You can override the clips directory by setting the "
                     "WEB_CLIPPER_DIR environment variable.[/dim]")
        console.print()

    except Exception as e:
        console.print()
        console.print(
            Panel.fit(
                f"[red][/red] {str(e)}",
                title="[bold red]Initialization Error[/bold red]",
                border_style="red"
            )
        )
        console.print()
        raise typer.Exit(code=1)


@app.command(name="config")
def config_command():
    """
    Show current configuration.
    """
    config = get_config()

    console.print()
    console.print(
        Panel.fit(
            f"[cyan]Clips directory:[/cyan] {config.clips_directory}\n"
            f"[cyan]Create subdirs:[/cyan] {config.create_subdirs}\n"
            f"[cyan]Include title:[/cyan] {config.include_title}\n"
            f"[cyan]Include timestamp:[/cyan] {config.include_timestamp}\n"
            f"[cyan]Timestamp format:[/cyan] {config.timestamp_format}",
            title="[bold]Web Clipper Configuration[/bold]",
            border_style="blue"
        )
    )
    console.print()


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"web-clipper version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True
    )
):
    """
    Web Clipper - Capture web content to organized markdown files.
    """
    pass


if __name__ == "__main__":
    app()
