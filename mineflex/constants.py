"""Constants for Minecraft protocol, physics, and gameplay."""

from __future__ import annotations

from enum import IntEnum

# Default supported version
DEFAULT_MINECRAFT_VERSION = "1.20.1"
DEFAULT_PROTOCOL_VERSION = 763

SUPPORTED_VERSIONS: dict[str, int] = {
    "1.20.1": 763,
    "1.20.2": 764,
    "1.20.4": 765,
    "1.21": 767,
    "1.21.1": 767,
}


class ProtocolState(IntEnum):
    """Minecraft connection protocol states."""

    HANDSHAKING = 0
    STATUS = 1
    LOGIN = 2
    PLAY = 3
    CONFIGURATION = 4


class GameMode(IntEnum):
    """Player game modes."""

    SURVIVAL = 0
    CREATIVE = 1
    ADVENTURE = 2
    SPECTATOR = 3


class BlockFace(IntEnum):
    """Minecraft block face directions."""

    BOTTOM = 0  # -Y
    TOP = 1  # +Y
    NORTH = 2  # -Z
    SOUTH = 3  # +Z
    WEST = 4  # -X
    EAST = 5  # +X


class DiggingStatus(IntEnum):
    """Player digging action statuses."""

    STARTED_DIGGING = 0
    CANCELLED_DIGGING = 1
    FINISHED_DIGGING = 2
    DROP_ITEM_STACK = 3
    DROP_ITEM = 4
    SHOOT_ARROW_OR_FINISH_EATING = 5
    SWAP_ITEM_WITH_OFFHAND = 6


class InteractType(IntEnum):
    """Entity interaction types."""

    INTERACT = 0
    ATTACK = 1
    INTERACT_AT = 2


class Hand(IntEnum):
    """Player hand identifier."""

    MAIN_HAND = 0
    OFF_HAND = 1


class EquipmentSlot(IntEnum):
    """Equipment slot identifiers."""

    MAIN_HAND = 0
    OFF_HAND = 1
    FEET = 2
    LEGS = 3
    CHEST = 4
    HEAD = 5


# Physics constants
PHYSICS_TICK_INTERVAL = 0.05  # 50 ms (20 ticks/sec)
PHYSICS_GRAVITY = 0.08
PHYSICS_TERMINAL_VELOCITY = 3.92
PHYSICS_AIR_DRAG = 0.98
PHYSICS_DEFAULT_SLIPPERINESS = 0.6
PHYSICS_JUMP_VELOCITY = 0.42
PHYSICS_SPRINT_SPEED_BOOST = 1.3
PHYSICS_SNEAK_SPEED_MULT = 0.3
PHYSICS_STEP_HEIGHT = 0.6

# Player geometry
PLAYER_WIDTH = 0.6
PLAYER_HEIGHT = 1.8
PLAYER_SNEAK_HEIGHT = 1.5
PLAYER_EYE_HEIGHT = 1.62
PLAYER_SNEAK_EYE_HEIGHT = 1.27
