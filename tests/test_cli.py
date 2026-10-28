import tomllib

import pytest
from typer.testing import CliRunner

from ashar_cli.commands import commute as commute_mod
from ashar_cli.commands import trip as trip_mod
from ashar_cli.main import app

runner = CliRunner()


@pytest.fixture
def cfg(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    return tmp_path / "ashar" / "config.toml"


@pytest.fixture
def opened(monkeypatch):
    urls = []
    monkeypatch.setattr(commute_mod.webbrowser, "open", urls.append)
    monkeypatch.setattr(trip_mod.webbrowser, "open", urls.append)
    return urls


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "commute" in result.output and "trip" in result.output


def test_version():
    assert runner.invoke(app, ["--version"]).output.startswith("ashar ")


def test_commute_needs_setup(cfg):
    result = runner.invoke(app, ["commute"])
    assert result.exit_code == 1
    assert "--save" in result.output


def test_commute_save_reuse_and_flip(cfg):
    result = runner.invoke(app, ["commute", "--from", "Hicksville", "--to", "Penn Station", "--save"])
    assert result.exit_code == 0, result.output
    assert tomllib.loads(cfg.read_text())["commute"] == {"from": "Hicksville", "to": "Penn Station"}

    again = runner.invoke(app, ["commute"], terminal_width=200)
    assert "Hicksville → Penn Station" in again.output

    back = runner.invoke(app, ["commute", "--home"], terminal_width=200)
    assert "Penn Station → Hicksville" in back.output


def test_commute_open(cfg, opened):
    runner.invoke(app, ["commute", "-f", "A", "-t", "B", "--open"])
    assert opened and "travelmode=transit" in opened[0]


def test_trip(opened):
    result = runner.invoke(app, ["trip", "boston", "--open"], terminal_width=200)
    assert result.exit_code == 0, result.output
    assert "New York → Boston" in result.output
    assert "Flights" in result.output
    assert opened and "destination=Boston" in opened[0]
