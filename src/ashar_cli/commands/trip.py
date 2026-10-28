"""`ashar trip <city>`: quick planning links for a destination."""

from __future__ import annotations

import webbrowser
from urllib.parse import quote_plus

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def trip_links(origin: str, dest: str) -> dict[str, str]:
    o, d = quote_plus(origin), quote_plus(dest)
    return {
        "Directions": f"https://www.google.com/maps/dir/?api=1&origin={o}&destination={d}",
        "Flights": f"https://www.google.com/travel/flights?q=flights+from+{o}+to+{d}",
        "Trains": "https://www.amtrak.com",
        "Hotels": f"https://www.google.com/travel/hotels/{d}",
        "Things to do": f"https://www.google.com/search?q=things+to+do+in+{d}",
        "Food": f"https://www.google.com/maps/search/best+restaurants+in+{d}",
    }


def trip(
    city: str = typer.Argument(..., help="Destination, e.g. boston"),
    origin: str = typer.Option("New York", "--from", help="Where you're leaving from."),
    open_: bool = typer.Option(False, "--open", "-o", help="Open directions in your browser."),
) -> None:
    """Planning links for a trip to CITY."""
    dest = city.title()
    links = trip_links(origin, dest)

    table = Table(title=f"✈️  {origin} → {dest}", show_header=False)
    table.add_column(style="bold")
    table.add_column(style="cyan", overflow="fold")
    for name, url in links.items():
        table.add_row(name, url)
    console.print(table)
    if open_:
        webbrowser.open(links["Directions"])
