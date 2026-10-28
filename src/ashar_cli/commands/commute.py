"""`ashar commute`: your commute route, with one-tap links."""

from __future__ import annotations

import webbrowser
from urllib.parse import quote_plus

import typer
from rich.console import Console
from rich.panel import Panel

from ashar_cli.config import config_path, load_config, save_section

console = Console()


def commute(
    frm: str = typer.Option(None, "--from", "-f", help="Where you start."),
    to: str = typer.Option(None, "--to", "-t", help="Where you're going."),
    home: bool = typer.Option(False, "--home", help="Flip direction: the trip home."),
    save: bool = typer.Option(False, "--save", help="Remember --from/--to."),
    open_: bool = typer.Option(False, "--open", "-o", help="Open directions in your browser."),
) -> None:
    """Show your commute, with transit directions."""
    cfg = load_config().get("commute", {})
    origin, dest = frm or cfg.get("from"), to or cfg.get("to")
    if not origin or not dest:
        console.print(
            "[yellow]No commute set up yet.[/yellow] Save it once:\n\n"
            '  [bold]ashar commute --from "Your station" --to "Penn Station" --save[/bold]\n\n'
            f"(stored privately in {config_path()})"
        )
        raise typer.Exit(1)

    if save:
        save_section("commute", {"from": origin, "to": dest})
        console.print(f"[green]Saved:[/green] {origin} → {dest}")

    if home:
        origin, dest = dest, origin

    maps = (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={quote_plus(origin)}&destination={quote_plus(dest)}&travelmode=transit"
    )
    console.print(
        Panel.fit(
            f"[bold]{origin}[/bold] → [bold]{dest}[/bold]\n\n"
            f"Directions: [cyan]{maps}[/cyan]\n"
            f"LIRR times: [cyan]https://traintime.mta.info[/cyan]",
            title="🚆 Commute",
        )
    )
    if open_:
        webbrowser.open(maps)
