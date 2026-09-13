"""Player tracking and player list information."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional

from mineflex.entity.entity import Entity


@dataclass
class Player:
    """Represents a player in the server's tablist / game."""

    uuid: uuid.UUID
    username: str
    ping: int = 0
    gamemode: int = 0
    display_name: Optional[str] = None
    entity: Optional[Entity] = None

    def __repr__(self) -> str:
        return f"Player(username='{self.username}', ping={self.ping}, gm={self.gamemode})"
