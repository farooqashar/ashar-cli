import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

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


def test_save_section_round_trips_control_characters(cfg):
    cfg.parent.mkdir(parents=True)
    cfg.write_text('note = """line one\nline two"""\n[commute]\nfrom = "A"\n')
    tricky = "a\rb\x7fc\x00d\te\bf\fg\x1fh\n"
    save_section("commute", {"to": tricky})
    assert tomllib.loads(cfg.read_text()) == {
        "note": "line one\nline two",
        "commute": {"from": "A", "to": tricky},
    }


def test_save_section_keeps_top_level_keys(cfg):
    cfg.parent.mkdir(parents=True)
    cfg.write_text('name = "x"\n\n[commute]\nfrom = "A"\n')
    save_section("commute", {"to": "B"})
    assert load_config() == {"name": "x", "commute": {"from": "A", "to": "B"}}


def test_save_section_keeps_types_nested_tables_and_quoted_keys(cfg):
    cfg.parent.mkdir(parents=True)
    cfg.write_text(
        'theme = "dark"\n'
        "retries = 3\n"
        "debug = true\n"
        "ratio = 0.5\n"
        "tags = [1, \"two\", [false]]\n"
        "since = 2024-01-02\n"
        "[commute]\n"
        'from = "Huntington"\n'
        'to = "Penn Station"\n'
        "[trip.defaults]\n"
        'from = "Boston"\n'
        "[trip.defaults.deep]\n"
        "n = 1\n"
        "[empty]\n"
        "[aliases]\n"
        '"work office" = "Penn Station"\n'
        '"a.b" = { x = 1, "y z" = "w" }\n'
        "[[stops]]\n"
        'name = "Jamaica"\n'
    )
    before = tomllib.loads(cfg.read_text())
    save_section("commute", {"from": "Hicksville"})
    before["commute"]["from"] = "Hicksville"
    assert tomllib.loads(cfg.read_text()) == before


def test_load_config_malformed_file_exits_with_message(cfg):
    cfg.parent.mkdir(parents=True)
    cfg.write_text("work office = 1\n")
    with pytest.raises(SystemExit) as exc:
        load_config()
    assert str(cfg) in str(exc.value.code)
    assert "\n" not in str(exc.value.code)


def test_save_section_writes_utf8(cfg):
    # Fails if any write falls back to the locale encoding, whatever this host's locale is.
    script = 'from ashar_cli.config import save_section; save_section("commute", {"from": "Zürich HB", "to": "東京"})'
    flags = ["-X", "warn_default_encoding", "-W", "error::EncodingWarning"]
    subprocess.run([sys.executable, *flags, "-c", script], check=True)
    text = cfg.read_bytes().decode("utf-8")
    assert tomllib.loads(text)["commute"] == {"from": "Zürich HB", "to": "東京"}


def test_load_config_non_utf8_file_exits_with_message(cfg):
    cfg.parent.mkdir(parents=True)
    cfg.write_bytes('[commute]\nfrom = "Café"\n'.encode("cp1252"))
    with pytest.raises(SystemExit) as exc:
        load_config()
    assert str(cfg) in str(exc.value.code)
    assert "UTF-8" in str(exc.value.code)
    assert "\n" not in str(exc.value.code)


def test_save_section_rejects_non_table_section(cfg):
    cfg.parent.mkdir(parents=True)
    cfg.write_text('commute = "Penn Station"\n')
    with pytest.raises(SystemExit) as exc:
        save_section("commute", {"from": "A", "to": "B"})
    assert exc.value.code == f"Error: [commute] in {cfg} must be a table."
    assert cfg.read_text() == 'commute = "Penn Station"\n'
