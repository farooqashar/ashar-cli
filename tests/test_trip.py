from typer.testing import CliRunner

from ashar_cli.commands.trip import trip_links
from ashar_cli.main import app

runner = CliRunner()


def test_trip_links_has_every_link():
    links = trip_links("New York", "Boston")
    assert set(links) == {"Directions", "Flights", "Trains", "Hotels", "Things to do", "Food"}
    assert all(url.startswith("https://") for url in links.values())


def test_trip_open(opened):
    result = runner.invoke(app, ["trip", "boston", "--open"], terminal_width=200)
    assert result.exit_code == 0, result.output
    assert "New York → Boston" in result.output
    assert "Flights" in result.output
    assert opened and "destination=Boston" in opened[0]


def test_trip_without_open_does_not_open_browser(opened):
    result = runner.invoke(app, ["trip", "boston"], terminal_width=200)
    assert result.exit_code == 0, result.output
    assert opened == []


def test_trip_from_overrides_origin(opened):
    result = runner.invoke(app, ["trip", "boston", "--from", "Chicago", "--open"], terminal_width=200)
    assert result.exit_code == 0, result.output
    assert "Chicago → Boston" in result.output
    assert "origin=Chicago" in opened[0]


def test_trip_multi_word_city_is_title_cased_and_encoded(opened):
    result = runner.invoke(app, ["trip", "san juan", "--open"], terminal_width=200)
    assert result.exit_code == 0, result.output
    assert "New York → San Juan" in result.output
    assert "San+Juan" in result.output
    assert "destination=San+Juan" in opened[0]
