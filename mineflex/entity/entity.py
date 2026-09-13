"""Entity representations and models."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from mineflex.constants import PLAYER_HEIGHT, PLAYER_WIDTH
from mineflex.types import AABB, Vec3


@dataclass
class Entity:
    """A tracked Minecraft entity in the world."""

    id: int
    uuid: uuid.UUID
    type: int
    name: str = "entity"
    category: str = "unknown"
    position: Vec3 = field(default_factory=lambda: Vec3(0, 0, 0))
    velocity: Vec3 = field(default_factory=lambda: Vec3(0, 0, 0))
    yaw: float = 0.0
    pitch: float = 0.0
    head_yaw: float = 0.0
    on_ground: bool = True
    width: float = PLAYER_WIDTH
    height: float = PLAYER_HEIGHT
    metadata: Dict[int, Any] = field(default_factory=dict)
    equipment: Dict[int, Optional[dict]] = field(default_factory=dict)
    vehicle: Optional[Entity] = None

    @property
    def bounding_box(self) -> AABB:
        return AABB.from_entity(self.position, self.width, self.height)

    @property
    def eye_position(self) -> Vec3:
        eye_y = self.height * 0.85
        return self.position.offset(0, eye_y, 0)

    def distance_to(self, other: Entity | Vec3) -> float:
        other_pos = other.position if isinstance(other, Entity) else other
        return self.position.distance_to(other_pos)

    def __repr__(self) -> str:
        return f"Entity(id={self.id}, name='{self.name}', pos={self.position.floored()})"
