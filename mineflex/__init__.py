"""Mineflex: A native Python port and equivalent of Mineflayer.

Provides an asynchronous, event-driven framework for building Minecraft bots.
"""

from __future__ import annotations

from mineflex.bot import Bot, create_bot
from mineflex.errors import (
    ActionError,
    AuthenticationError,
    ConnectionError,
    CraftingError,
    DiggingError,
    InventoryError,
    MineflexError,
    PacketError,
    PhysicsError,
    ProtocolError,
    TimeoutError,
    UnsupportedVersionError,
)
from mineflex.events.emitter import AsyncEventEmitter
from mineflex.types import AABB, Angle, Position, Vec3

__version__ = "0.1.0"
__all__ = [
    "Bot",
    "create_bot",
    "Vec3",
    "AABB",
    "Position",
    "Angle",
    "AsyncEventEmitter",
    "MineflexError",
    "ConnectionError",
    "AuthenticationError",
    "ProtocolError",
    "PacketError",
    "UnsupportedVersionError",
    "TimeoutError",
    "InventoryError",
    "DiggingError",
    "CraftingError",
    "ActionError",
    "PhysicsError",
]
