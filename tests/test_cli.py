from typer.testing import CliRunner

from ashar_cli.main import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "commute" in result.output and "trip" in result.output


def test_trip():
    result = runner.invoke(app, ["trip", "boston"])
    assert result.exit_code == 0
    assert "Boston" in result.output


def test_commute_unconfigured(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    result = runner.invoke(app, ["commute"])
    assert result.exit_code == 1


def test_commute_configured(tmp_path, monkeypatch):
    (tmp_path / "ashar").mkdir()
    (tmp_path / "ashar" / "config.toml").write_text('[commute]\nfrom = "A"\nto = "B"\n')
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    result = runner.invoke(app, ["commute"])
    assert result.exit_code == 0
    assert "A" in result.output
