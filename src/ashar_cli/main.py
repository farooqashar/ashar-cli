"""Entry point for the `ashar` command."""

from __future__ import annotations

import typer

from ashar_cli import __version__
from ashar_cli.commands.commute import commute
from ashar_cli.commands.trip import trip

app = typer.Typer(
    help="Ashar Farooq's personal CLI.",
    no_args_is_help=True,
    add_completion=True,
)

app.command()(commute)
app.command()(trip)


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
