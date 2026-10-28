# ashar-cli

My personal command-line tool.

```bash
pip install ashar-cli      # or: uv tool install ashar-cli / pipx install ashar-cli
ashar --help
```

## Commands

| Command | What it does |
|---|---|
| `ashar commute` | Your commute with transit directions (`--home` flips it, `--open` opens the map) |
| `ashar trip boston` | Planning links for a trip (`--from` to change origin, `--open` opens directions) |
| `ashar about` | Who made this |
| `ashar --version` | Version |

### Commute setup

Save your stations once (stored privately in `~/.config/ashar/config.toml`, never in the package):

```bash
ashar commute --from "Your station" --to "Penn Station" --save
ashar commute          # uses the saved route
ashar commute --home   # the trip back
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
