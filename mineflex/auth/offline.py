"""Offline authentication mode with vanilla-compatible UUID generation."""

from __future__ import annotations

import hashlib
import uuid

from mineflex.auth.base import AuthProvider, Session


def offline_uuid(username: str) -> uuid.UUID:
    """Generate vanilla Java Edition offline player UUID from username (UUID.nameUUIDFromBytes)."""
    raw = f"OfflinePlayer:{username}".encode("utf-8")
    md5_bytes = bytearray(hashlib.md5(raw).digest())

    # Set version to 3 (MD5-based UUID)
    md5_bytes[6] = (md5_bytes[6] & 0x0F) | 0x30
    # Set variant to IETF (RFC 4122)
    md5_bytes[8] = (md5_bytes[8] & 0x3F) | 0x80

    return uuid.UUID(bytes=bytes(md5_bytes))


class OfflineAuthProvider(AuthProvider):
    """Generates an offline session with deterministic UUID without network calls."""

    async def authenticate(self, username: str, **kwargs) -> Session:
        player_uuid = offline_uuid(username)
        return Session(
            username=username,
            player_uuid=player_uuid,
            access_token=None,
            is_online=False,
        )
