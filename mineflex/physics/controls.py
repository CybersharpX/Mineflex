"""Player control states for physics simulation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ControlState:
    """Represents current movement control inputs."""

    forward: bool = False
    back: bool = False
    left: bool = False
    right: bool = False
    jump: bool = False
    sprint: bool = False
    sneak: bool = False

    def reset(self) -> None:
        """Reset all controls to inactive."""
        self.forward = False
        self.back = False
        self.left = False
        self.right = False
        self.jump = False
        self.sprint = False
        self.sneak = False

    @property
    def is_moving(self) -> bool:
        return self.forward or self.back or self.left or self.right
