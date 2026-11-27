import importlib
import importlib.metadata
import tomllib

import pytest
from typer.testing import CliRunner

import ashar_cli
from ashar_cli.main import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "commute" in result.output and "trip" in result.output


def test_version():
    assert runner.invoke(app, ["--version"]).output.startswith("ashar ")


def test_about():
    result = runner.invoke(app, ["about"])
    assert result.exit_code == 0
    assert "https://ashar.vercel.app" in result.output


@pytest.fixture
def uninstalled(monkeypatch):
    def missing(name):
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", missing)
    yield
    monkeypatch.undo()
    importlib.reload(ashar_cli)


def test_version_fallback_when_not_installed(uninstalled):
    importlib.reload(ashar_cli)
    assert ashar_cli.__version__ == "0.0.0"


def test_commute_needs_setup(cfg):
    result = runner.invoke(app, ["commute"])
    assert result.exit_code == 1
    assert "--save" in result.output


def test_commute_home_needs_setup(cfg):
    result = runner.invoke(app, ["commute", "--home"])
    assert result.exit_code == 1
    assert "--save" in result.output


def test_commute_save_reuse_and_flip(cfg):
    result = runner.invoke(
        app, ["commute", "--from", "Hicksville", "--to", "Penn Station", "--save"], terminal_width=200
    )
    assert result.exit_code == 0, result.output
    assert "Saved: Hicksville → Penn Station" in result.output
    assert tomllib.loads(cfg.read_text())["commute"] == {"from": "Hicksville", "to": "Penn Station"}

    again = runner.invoke(app, ["commute"], terminal_width=200)
    assert "Hicksville → Penn Station" in again.output

    back = runner.invoke(app, ["commute", "--home"], terminal_width=200)
    assert "Penn Station → Hicksville" in back.output


def test_commute_malformed_config_is_one_line_error(cfg):
    cfg.parent.mkdir(parents=True)
    cfg.write_text("work office = 1\n")
    result = runner.invoke(app, ["commute"])
    assert result.exit_code == 1
    assert str(cfg) in result.output
    assert "Traceback" not in result.output


def test_commute_non_utf8_config_is_one_line_error(cfg):
    cfg.parent.mkdir(parents=True)
    cfg.write_bytes('[commute]\nfrom = "Café"\n'.encode("cp1252"))
    result = runner.invoke(app, ["commute"])
    assert result.exit_code == 1
    assert str(cfg) in result.output
    assert "Traceback" not in result.output


@pytest.mark.parametrize("args", [[], ["--from", "A", "--to", "B", "--save"]])
def test_commute_non_table_config_is_one_line_error(cfg, args):
    cfg.parent.mkdir(parents=True)
    cfg.write_text('commute = "x"\n')
    result = runner.invoke(app, ["commute", *args])
    assert result.exit_code == 1
    assert f"[commute] in {cfg} must be a table." in result.output
    assert "Traceback" not in result.output
    assert cfg.read_text() == 'commute = "x"\n'


def test_commute_open(cfg, opened):
    runner.invoke(app, ["commute", "-f", "A", "-t", "B", "--open"])
    assert opened and "travelmode=transit" in opened[0]


def test_commute_names_are_shown_literally_not_as_markup(cfg):
    result = runner.invoke(
        app, ["commute", "--from", "Penn Station [lirr]", "--to", "B", "--save"], terminal_width=200
    )
    assert result.exit_code == 0, result.output
    assert "Saved: Penn Station [lirr] → B" in result.output
    assert "│ Penn Station [lirr] → B" in result.output

    result = runner.invoke(app, ["commute", "--from", "A [/b]", "--to", "B"], terminal_width=200)
    assert result.exit_code == 0, result.output
    assert "A [/b] → B" in result.output
