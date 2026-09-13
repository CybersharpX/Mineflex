"""Authentication subsystem for Mineflex."""

from __future__ import annotations

from mineflex.auth.base import AuthProvider, Session
from mineflex.auth.microsoft import MicrosoftAuthProvider
from mineflex.auth.offline import OfflineAuthProvider, offline_uuid

__all__ = [
    "Session",
    "AuthProvider",
    "OfflineAuthProvider",
    "MicrosoftAuthProvider",
    "offline_uuid",
]
