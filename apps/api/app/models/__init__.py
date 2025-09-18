"""Database models for the Audiovook domain."""

from sqlmodel import SQLModel

from .account import Account, AccountProvider
from .binding import QrBinding
from .device import Device
from .progress import ListeningProgress
from .qr import QrCode, QrStatus
from .session import PlaySession

metadata = SQLModel.metadata

__all__ = [
    "Account",
    "AccountProvider",
    "Device",
    "ListeningProgress",
    "PlaySession",
    "QrBinding",
    "QrCode",
    "QrStatus",
    "metadata",
]
