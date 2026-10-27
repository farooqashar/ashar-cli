"""Local, private settings live in ~/.config/ashar/config.toml, never in the package.

Example config.toml:

    [commute]
    from = "Huntington"
    to = "Penn Station"
"""

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
