"""Local filesystem storage backend implementation."""

from pathlib import Path
from typing import BinaryIO

from .base import LocalStorage


def create_local_storage(root: str | Path) -> LocalStorage:
    """Return a configured LocalStorage instance."""

    return LocalStorage(root)
