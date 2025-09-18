"""Abstract storage interface used by media delivery services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO


class StorageBackend(ABC):
    """Define the contract for media storage operations."""

    @abstractmethod
    def open(self, path: str) -> BinaryIO:
        """Return a binary file handle for the given path."""

    @abstractmethod
    def exists(self, path: str) -> bool:
        """Return whether the media asset exists."""


class LocalStorage(StorageBackend):
    """Simple local filesystem storage backend."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def open(self, path: str) -> BinaryIO:
        return (self.root / path).open("rb")

    def exists(self, path: str) -> bool:
        return (self.root / path).exists()
