"""Database models for the Audiovook domain."""

from sqlmodel import SQLModel

from .account import Account, AccountProvider
from .binding import QrBinding
from .device import Device
from .magic_link import MagicLinkToken
from .progress import ListeningProgress
from .qr import QrCode, QrStatus
from .session import PlaySession
from .user import User

metadata = SQLModel.metadata

__all__ = [
    "Account",
    "AccountProvider",
    "Device",
    "ListeningProgress",
    "MagicLinkToken",
    "PlaySession",
    "QrBinding",
    "QrCode",
    "QrStatus",
    "User",
    "metadata",
]
