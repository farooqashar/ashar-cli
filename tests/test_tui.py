import asyncio
import sys

from typer.testing import CliRunner

from ashar_cli.commands.commute import commute_link
from ashar_cli.config import save_section
from ashar_cli.main import app
from ashar_cli.tui import AsharApp

runner = CliRunner()


def drive(*keys, trip=None):
    """Run the app headlessly, press keys, and return what it showed."""
    tui = AsharApp()

    async def go():
        async with tui.run_test() as pilot:
            if trip is not None:
                await pilot.click("#--content-tab-trip")
                tui.query_one("#city").focus()
                await pilot.press(*trip, "enter")
            await pilot.press(*keys)
            await pilot.pause()
            return {
                "route": str(tui.query_one("#route").render()),
                "trip": str(tui.query_one("#trip-title").render()),
                "links": tui.query_one("#links").option_count,
                "running": tui.is_running,
            }

    return asyncio.run(go())


def test_shows_saved_route(cfg):
    save_section("commute", {"from": "Hicksville", "to": "Penn Station"})
    route = drive()["route"]
    assert "Hicksville → Penn Station" in route
    assert "origin=Hicksville&destination=Penn+Station&travelmode=transit" in route
    assert "https://traintime.mta.info" in route


def test_h_flips_direction(cfg):
    save_section("commute", {"from": "Hicksville", "to": "Penn Station"})
    assert "Penn Station → Hicksville" in drive("h")["route"]
    assert "Hicksville → Penn Station" in drive("h", "h")["route"]


def test_o_opens_directions(cfg, opened):
    save_section("commute", {"from": "Hicksville", "to": "Penn Station"})
    drive("h", "o")
    assert opened == [commute_link("Penn Station", "Hicksville")]
    assert "origin=Penn+Station&destination=Hicksville" in opened[0]


def test_no_commute_shows_setup_hint(cfg, opened):
    route = drive("o")["route"]
    assert "No commute set up yet" in route
    assert 'ashar commute --from "Your station" --to "Penn Station" --save' in route
    assert opened == []


def test_trip_shows_all_links(cfg):
    shown = drive(trip="boston")
    assert shown["trip"] == "✈️  New York → Boston"
    assert shown["links"] == 6


def test_trip_typing_keys_is_not_a_binding(cfg, opened):
    shown = drive(trip="hoq")
    assert shown["running"] and shown["trip"] == "✈️  New York → Hoq"
    assert opened == []


def test_trip_needs_a_city(cfg):
    assert drive(trip="")["links"] == 0


def test_enter_opens_highlighted_link(cfg, opened):
    drive("down", "enter", trip="boston")
    assert opened == ["https://www.google.com/travel/flights?q=flights+from+New+York+to+Boston"]


def test_q_quits(cfg):
    assert not drive("q")["running"]


def test_tui_command_runs_app(cfg, monkeypatch):
    ran = []
    monkeypatch.setattr(AsharApp, "run", lambda self: ran.append(self))
    assert runner.invoke(app, ["tui"]).exit_code == 0
    assert len(ran) == 1


def test_tui_command_malformed_config_is_one_line_error(cfg, monkeypatch):
    monkeypatch.setattr(AsharApp, "run", lambda self: None)
    cfg.parent.mkdir(parents=True)
    cfg.write_text("work office = 1\n")
    result = runner.invoke(app, ["tui"])
    assert result.exit_code == 1
    assert str(cfg) in result.output
    assert "Traceback" not in result.output


def test_tui_command_without_extra(cfg, monkeypatch):
    # Block textual and its already-imported submodules, as if it were not installed.
    for name in [m for m in sys.modules if m == "textual" or m.startswith("textual.")]:
        monkeypatch.setitem(sys.modules, name, None)
    monkeypatch.delitem(sys.modules, "ashar_cli.tui")
    result = runner.invoke(app, ["tui"])
    assert result.exit_code == 1
    assert 'pip install "ashar-cli[tui]"' in result.output
    assert "Traceback" not in result.output
