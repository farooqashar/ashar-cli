"""ashar-cli: Ashar Farooq's personal command-line tool."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ashar-cli")
except PackageNotFoundError:  # running from source without install
    __version__ = "0.0.0"
