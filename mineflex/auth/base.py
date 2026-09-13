"""Authentication base abstractions and Session model."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Session:
    """Represents an authenticated Minecraft player session."""

    username: str
    player_uuid: uuid.UUID
    access_token: Optional[str] = None
    is_online: bool = False


class AuthProvider:
    """Base interface for authentication mechanisms."""

    async def authenticate(self, username: str, **kwargs) -> Session:
        raise NotImplementedError
