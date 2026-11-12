# ashar-cli

[![CI](https://github.com/farooqashar/ashar-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/farooqashar/ashar-cli/actions/workflows/ci.yml) [![Coverage Status](https://coveralls.io/repos/github/farooqashar/ashar-cli/badge.svg?branch=main)](https://coveralls.io/github/farooqashar/ashar-cli?branch=main)

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
uv sync
uv run ashar --help
uv run pytest            # tests + coverage table
uv run pytest --cov-report=html && open htmlcov/index.html
```

New code needs tests: CI fails if coverage drops below the 100% threshold (`fail_under` in `pyproject.toml`).

Tests must not touch the real config: use the `cfg` and `opened` fixtures in `tests/conftest.py`.

## Releasing

1. Bump `version` in `pyproject.toml`.
2. Commit, then tag and push: `git tag v0.1.1 && git push --tags`.
3. GitHub Actions runs the tests and publishes to PyPI.
