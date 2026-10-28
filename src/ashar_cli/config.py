"""Private settings live in ~/.config/ashar/config.toml, never in the package."""

from __future__ import annotations

import os
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
        return tomllib.load(f)


def _q(v: str) -> str:
    return '"' + str(v).replace("\\", "\\\\").replace('"', '\\"') + '"'


def save_section(section: str, values: dict[str, str]) -> Path:
    """Merge string values into one [section] and rewrite the file."""
    cfg = load_config()
    cfg.setdefault(section, {}).update(values)
    lines = []
    for name, table in cfg.items():
        if isinstance(table, dict):
            lines.append(f"[{name}]")
            lines += [f"{k} = {_q(v)}" for k, v in table.items()]
            lines.append("")
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))
    return path
