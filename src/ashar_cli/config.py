"""Private settings live in ~/.config/ashar/config.toml, never in the package."""

from __future__ import annotations

import datetime as dt
import os
import re
import tomllib
from pathlib import Path


def config_path() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base) / "ashar" / "config.toml"


def load_config() -> dict:
    path = config_path()
    if not path.exists():
        return {}
    with path.open("rb") as f:
        try:
            return tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise SystemExit(f"Error: {path} is not valid TOML ({e}). Fix or delete it.") from None
        except UnicodeDecodeError as e:
            raise SystemExit(f"Error: {path} is not UTF-8 ({e}). Fix or delete it.") from None


def load_section(section: str, cfg: dict | None = None) -> dict:
    """One [section] of the config, or {} if absent; never a non-table value."""
    value = (load_config() if cfg is None else cfg).get(section, {})
    if not isinstance(value, dict):
        raise SystemExit(f"Error: [{section}] in {config_path()} must be a table.")
    return value


# TOML basic strings forbid raw control characters, so escape them all.
_ESCAPES = {c: f"\\u{c:04X}" for c in [*range(0x20), 0x7F]}
_ESCAPES |= {ord("\\"): "\\\\", ord('"'): '\\"', ord("\b"): "\\b", ord("\t"): "\\t"}
_ESCAPES |= {ord("\n"): "\\n", ord("\f"): "\\f", ord("\r"): "\\r"}


def _q(v: str) -> str:
    return '"' + str(v).translate(_ESCAPES) + '"'


def _key(k: str) -> str:
    return k if re.fullmatch(r"[A-Za-z0-9_-]+", k) else _q(k)


def _value(v: object) -> str:
    """Write one value the way tomllib read it, so a save round-trips."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int | float):
        return repr(v)
    if isinstance(v, dt.date | dt.time):
        return v.isoformat()
    if isinstance(v, list):
        return "[" + ", ".join(_value(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{_key(k)} = {_value(x)}" for k, x in v.items()) + "}"
    return _q(v)


def _table(header: list[str], table: dict, lines: list[str]) -> None:
    # Scalars must come before any sub-table header, or TOML nests them.
    scalars = [f"{_key(k)} = {_value(v)}" for k, v in table.items() if not isinstance(v, dict)]
    subtables = {k: v for k, v in table.items() if isinstance(v, dict)}
    if scalars or (header and not subtables):
        if header:
            lines.append("[" + ".".join(_key(k) for k in header) + "]")
        lines += [*scalars, ""]
    for k, v in subtables.items():
        _table([*header, k], v, lines)


def save_section(section: str, values: dict[str, str]) -> Path:
    """Merge string values into one [section] and rewrite the file."""
    cfg = load_config()
    cfg[section] = {**load_section(section, cfg), **values}
    lines: list[str] = []
    _table([], cfg, lines)
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
