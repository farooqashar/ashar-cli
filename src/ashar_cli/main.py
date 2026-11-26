"""Entry point for the `ashar` command."""

from __future__ import annotations

import typer

from ashar_cli import __version__
from ashar_cli.commands.commute import commute
from ashar_cli.commands.trip import trip
from ashar_cli.config import load_config

app = typer.Typer(
    help="Ashar Farooq's personal CLI.",
    no_args_is_help=True,
    add_completion=True,
)

app.command()(commute)
app.command()(trip)


@app.command()
def tui() -> None:
    """Commute and trip links in a small terminal UI."""
    load_config()
    try:
        from ashar_cli.tui import AsharApp
    except ImportError:
        typer.echo(
            'The TUI needs an extra: pip install "ashar-cli[tui]"'
            ' (or: uv tool install "ashar-cli[tui]" / pipx install "ashar-cli[tui]")',
            err=True,
        )
        raise typer.Exit(1) from None
    AsharApp().run()


@app.command()
def about() -> None:
    """Who made this."""
    typer.echo("Ashar Farooq · https://ashar.vercel.app · github.com/farooqashar")


def _version(value: bool) -> None:
    if value:
        typer.echo(f"ashar {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", callback=_version, is_eager=True, help="Show version."
    ),
) -> None:
    pass


if __name__ == "__main__":
    app()
