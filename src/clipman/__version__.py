"""
Created for storing version number.
"""

# Dynamically determine __version__ from package metadata

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("clipman")
except PackageNotFoundError:
    # Fallback for when running from the source directory
    __version__ = "0.0.0+unknown"

__all__ = ("__version__",)
