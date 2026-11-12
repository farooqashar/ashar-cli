import tomllib
from pathlib import Path

from ashar_cli.config import config_path, load_config, save_section


def test_config_path_honours_xdg(cfg):
    assert config_path() == cfg


def test_config_path_falls_back_to_home(tmp_path, monkeypatch):
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    assert config_path() == tmp_path / ".config" / "ashar" / "config.toml"


def test_load_config_missing_file(cfg):
    assert not cfg.exists()
    assert load_config() == {}


def test_save_section_merges_and_keeps_other_sections(cfg):
    save_section("commute", {"from": "A", "to": "B"})
    save_section("other", {"key": "value"})
    save_section("commute", {"to": "C"})
    assert load_config() == {"commute": {"from": "A", "to": "C"}, "other": {"key": "value"}}


def test_save_section_round_trips_quotes_and_backslashes(cfg):
    tricky = 'say "hi" C:\\path\\to\\'
    save_section("commute", {"from": tricky})
    assert tomllib.loads(cfg.read_text())["commute"]["from"] == tricky


def test_save_section_keeps_top_level_keys(cfg):
    cfg.parent.mkdir(parents=True)
    cfg.write_text('name = "x"\n\n[commute]\nfrom = "A"\n')
    save_section("commute", {"to": "B"})
    assert load_config() == {"name": "x", "commute": {"from": "A", "to": "B"}}
