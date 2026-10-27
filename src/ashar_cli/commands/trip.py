"""`ashar trip <city>`: quick trip-planning links for a destination."""

from __future__ import annotations

from urllib.parse import quote_plus

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def trip(
    city: str = typer.Argument(..., help="Destination, e.g. boston"),
    origin: str = typer.Option("New York", "--from", help="Where you're leaving from."),
) -> None:
    """Show planning links for a trip to CITY."""
    dest = city.title()
    q = quote_plus(dest)

    table = Table(title=f"✈️  Trip: {origin} → {dest}", show_header=False)
    table.add_column(style="bold")
    table.add_column()
    table.add_row(
        "Directions",
        f"https://www.google.com/maps/dir/?api=1&origin={quote_plus(origin)}&destination={q}",
    )
    table.add_row("Flights", f"https://www.google.com/travel/flights?q=flights+to+{q}")
    table.add_row("Trains", "https://www.amtrak.com")
    table.add_row("Hotels", f"https://www.google.com/travel/hotels/{q}")
    table.add_row("Things to do", f"https://www.google.com/search?q=things+to+do+in+{q}")
    # TODO: add weather, saved itineraries, or your countries-visited data.
    console.print(table)
