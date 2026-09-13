"""Exception hierarchy for Mineflex."""

from __future__ import annotations


class MineflexError(Exception):
    """Base class for all Mineflex exceptions."""


class ConnectionError(MineflexError):
    """Raised when a network connection fails or is abruptly terminated."""


class AuthenticationError(MineflexError):
    """Raised when authentication fails (credentials, session token, or handshake rejection)."""


class ProtocolError(MineflexError):
    """Raised when an error occurs during protocol handling or state transitions."""


class PacketError(ProtocolError):
    """Raised when packet deserialization, serialization, or framing fails."""


class UnsupportedVersionError(ProtocolError):
    """Raised when an unsupported Minecraft protocol version is requested or encountered."""


class TimeoutError(MineflexError):
    """Raised when a network operation or expected server packet times out."""


class InvalidStateError(MineflexError):
    """Raised when an operation is performed in an invalid lifecycle or bot state."""


class InventoryError(MineflexError):
    """Base class for inventory and container manipulation errors."""


class CraftingError(InventoryError):
    """Raised when a recipe cannot be crafted due to missing items or invalid state."""


class ActionError(MineflexError):
    """Base class for high-level bot action failures."""


class DiggingError(ActionError):
    """Raised when digging cannot start, fails, or is interrupted."""


class PlacementError(ActionError):
    """Raised when block placement fails or violates game rules."""


class InteractionError(ActionError):
    """Raised when entity or world interaction fails (e.g. out of reach)."""


class PhysicsError(MineflexError):
    """Raised when an error occurs during physics simulation."""
