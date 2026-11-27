"""`ashar tui`: commute and trip links in one small terminal UI. No network calls."""

from __future__ import annotations

import webbrowser
from typing import ClassVar

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Input, OptionList, Static, TabbedContent, TabPane
from textual.widgets.option_list import Option

from ashar_cli.commands.commute import (
    TRAINTIME,
    commute_link,
    resolve_route,
    setup_hint,
)
from ashar_cli.commands.trip import capitalize_words, trip_links


class AsharApp(App):
    TITLE = "ashar"
    BINDINGS: ClassVar = [
        Binding("h", "flip", "Flip direction"),
        Binding("o", "open_directions", "Open directions"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.home = False

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Commute", id="commute"):
                yield Static(id="route")
            with TabPane("Trip", id="trip"):
                yield Input(placeholder="City, e.g. boston", id="city")
                yield Input(value="New York", placeholder="From", id="origin")
                yield Static(id="trip-title")
                yield OptionList(id="links")
        yield Footer()

    def on_mount(self) -> None:
        self.show_route()

    def route(self) -> tuple[str, str] | None:
        return resolve_route(None, None, self.home)

    def show_route(self) -> None:
        route = self.route()
        if route is None:
            body = Text.from_markup(setup_hint())
        else:
            origin, dest = route
            body = Text.assemble(
                (origin, "bold"), " → ", (dest, "bold"),
                "\n\nDirections: ", (commute_link(origin, dest), "cyan"),
                "\nLIRR times: ", (TRAINTIME, "cyan"),
            )
        self.query_one("#route", Static).update(body)

    def action_flip(self) -> None:
        self.home = not self.home
        self.show_route()

    def action_open_directions(self) -> None:
        route = self.route()
        if route is not None:
            webbrowser.open(commute_link(*route))

    def on_input_submitted(self) -> None:
        city = self.query_one("#city", Input).value.strip()
        if not city:
            return
        origin = self.query_one("#origin", Input).value.strip() or "New York"
        dest = capitalize_words(city)
        self.query_one("#trip-title", Static).update(Text(f"✈️  {origin} → {dest}", "bold"))
        links = self.query_one("#links", OptionList)
        links.clear_options()
        links.add_options(
            Option(Text.assemble((f"{name:<13}", "bold"), (url, "cyan")), id=url)
            for name, url in trip_links(origin, dest).items()
        )
        links.highlighted = 0
        links.focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        webbrowser.open(event.option.id)
