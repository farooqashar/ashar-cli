import pytest

from ashar_cli.commands import commute as commute_mod
from ashar_cli.commands import trip as trip_mod


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
