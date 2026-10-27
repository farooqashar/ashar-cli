"""`ashar commute`: show the trip between home and work."""

from __future__ import annotations

from urllib.parse import quote_plus

import typer
from rich.console import Console
from rich.panel import Panel

from ashar_cli.config import config_path, load_config

console = Console()


def commute(
    reverse: bool = typer.Option(False, "--home", help="Show the trip home instead."),
) -> None:
    """Show your commute (LIRR by default)."""
    cfg = load_config().get("commute", {})
    origin = cfg.get("from")
    dest = cfg.get("to")

    if not origin or not dest:
        console.print(
            f"[yellow]No commute configured.[/yellow] Add this to [bold]{config_path()}[/bold]:\n\n"
            '[commute]\nfrom = "Your home station"\nto = "Your work station"'
        )
        raise typer.Exit(1)

    if reverse:
        origin, dest = dest, origin

    maps = (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={quote_plus(origin)}&destination={quote_plus(dest)}&travelmode=transit"
    )
    # TODO: replace with live departures (e.g. MTA GTFS-realtime feed for LIRR).
    console.print(
        Panel.fit(
            f"[bold]{origin}[/bold] → [bold]{dest}[/bold]\n\n"
            f"Live times: https://traintime.mta.info\n"
            f"Directions: {maps}",
            title="🚆 Commute",
        )
    )
