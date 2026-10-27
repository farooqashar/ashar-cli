# ashar-cli

My personal command-line tool.

```bash
pip install ashar-cli      # or: uv tool install ashar-cli / pipx install ashar-cli
ashar --help
```

## Commands

| Command | What it does |
|---|---|
| `ashar commute` | Commute to work (`--home` for the trip back) |
| `ashar trip boston` | Planning links for a trip (`--from` to change origin) |
| `ashar about` | Who made this |
| `ashar --version` | Version |

### Commute setup

Personal settings stay on your machine, not in the package. Create `~/.config/ashar/config.toml`:

```toml
[commute]
from = "Huntington"
to = "Penn Station"
```

## Development

```bash
uv run ashar --help
uv run pytest
```

## Releasing

1. Bump `version` in `pyproject.toml`.
2. Commit, then tag and push: `git tag v0.1.1 && git push --tags`.
3. GitHub Actions runs the tests and publishes to PyPI.
