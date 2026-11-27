"""`ashar commute`: your commute route, with one-tap links."""

from __future__ import annotations

import webbrowser
from urllib.parse import quote_plus

import typer
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel

from ashar_cli.config import config_path, load_section, save_section

console = Console()

TRAINTIME = "https://traintime.mta.info"


def setup_hint() -> str:
    return (
        "[yellow]No commute set up yet.[/yellow] Save it once:\n\n"
        '  [bold]ashar commute --from "Your station" --to "Penn Station" --save[/bold]\n\n'
        f"(stored privately in {config_path()})"
    )


def resolve_route(frm: str | None, to: str | None, home: bool) -> tuple[str, str] | None:
    """The route to show: explicit --from/--to, else the saved one, flipped for --home."""
    cfg = load_section("commute")
    origin, dest = frm or cfg.get("from"), to or cfg.get("to")
    if not origin or not dest:
        return None
    return (dest, origin) if home else (origin, dest)


def commute_link(origin: str, dest: str) -> str:
    return (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={quote_plus(origin)}&destination={quote_plus(dest)}&travelmode=transit"
    )


def commute(
    frm: str = typer.Option(None, "--from", "-f", help="Where you start."),
    to: str = typer.Option(None, "--to", "-t", help="Where you're going."),
    home: bool = typer.Option(False, "--home", help="Flip direction: the trip home."),
    save: bool = typer.Option(False, "--save", help="Remember --from/--to."),
    open_: bool = typer.Option(False, "--open", "-o", help="Open directions in your browser."),
) -> None:
    """Show your commute, with transit directions."""
    route = resolve_route(frm, to, home=False)
    if route is None:
        console.print(setup_hint())
        raise typer.Exit(1)
    origin, dest = route

    if save:
        save_section("commute", {"from": origin, "to": dest})
        console.print(f"[green]Saved:[/green] {escape(origin)} → {escape(dest)}")

    if home:
        origin, dest = dest, origin

    maps = commute_link(origin, dest)
    console.print(
        Panel.fit(
            f"[bold]{escape(origin)}[/bold] → [bold]{escape(dest)}[/bold]\n\n"
            f"Directions: [cyan]{maps}[/cyan]\n"
            f"LIRR times: [cyan]{TRAINTIME}[/cyan]",
            title="🚆 Commute",
        )
    )
    if open_:
        webbrowser.open(maps)
